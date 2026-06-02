"""
Body rig for mathlab-mylinehub-creature.

This is the master control rig.

Architecture rule:
- body_rig.py controls the complete connected creature
- body_rig.py does not rebuild duplicate face/arm/leg parts
- BodyM owns the visible creature parts
- FaceRig controls BodyM face parts
- ArmRig controls BodyM arm parts
- LegRig controls BodyM leg parts
- movement_controller.py / actions will call BodyRig later
- audio is not handled here

Connection chain:

    Action / Controller
        |
        BodyRig
            |
            BodyM
                |
                Face parts
                Arm systems
                Leg systems
            |
            FaceRig
            ArmRig
            LegRig
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

from manimlib import VGroup

from mathlab_creature.config.defaults import DEBUG_MODE
from mathlab_creature.config.defaults import LOG_CREATURE_BUILD

from mathlab_creature.core.geometry import as_vec3
from mathlab_creature.core.geometry import clamp
from mathlab_creature.core.geometry import normalize
from mathlab_creature.core.geometry import point
from mathlab_creature.core.geometry import zero_vector
from mathlab_creature.core.kinematics import damp
from mathlab_creature.core.kinematics import damp_vector
from mathlab_creature.core.kinematics import solve_body_bounce
from mathlab_creature.core.kinematics import solve_body_sway
from mathlab_creature.core.kinematics import solve_body_tilt
from mathlab_creature.core.logger import get_logger
from mathlab_creature.core.transforms import RootTransformNode
from mathlab_creature.core.transforms import create_root_transform

from mathlab_creature.creature.parts.body_m import BodyM
from mathlab_creature.creature.parts.body_m import build_body_m
from mathlab_creature.creature.rigs.arm_rig import ArmRig
from mathlab_creature.creature.rigs.arm_rig import build_arm_rig
from mathlab_creature.creature.rigs.face_rig import FaceRig
from mathlab_creature.creature.rigs.face_rig import build_face_rig
from mathlab_creature.creature.rigs.leg_rig import LegRig
from mathlab_creature.creature.rigs.leg_rig import build_leg_rig


logger = get_logger(__name__)


@dataclass
class BodyRigConfig:
    """
    Tunable master body rig settings.
    """

    movement_smoothing: float = 8.0
    rotation_smoothing: float = 7.0

    body_tilt_strength: float = 0.18
    body_bounce_strength: float = 0.08
    body_sway_strength: float = 0.05

    walk_speed: float = 1.0
    run_multiplier: float = 2.0
    precision_multiplier: float = 0.4

    min_scale: float = 0.05
    max_scale: float = 100.0


def _validate_numeric(name: str, value: float | int) -> float:
    if not isinstance(value, (int, float)):
        raise TypeError(
            f"{name} must be numeric, got {type(value).__name__}"
        )

    return float(value)


def _validate_non_negative(name: str, value: float | int) -> float:
    value = _validate_numeric(name, value)

    if value < 0:
        raise ValueError(
            f"{name} must be >= 0, got {value}"
        )

    return value


def _validated_config(
    config: Optional[BodyRigConfig],
) -> BodyRigConfig:
    config = config or BodyRigConfig()

    config.movement_smoothing = _validate_non_negative(
        "config.movement_smoothing",
        config.movement_smoothing,
    )
    config.rotation_smoothing = _validate_non_negative(
        "config.rotation_smoothing",
        config.rotation_smoothing,
    )
    config.body_tilt_strength = _validate_non_negative(
        "config.body_tilt_strength",
        config.body_tilt_strength,
    )
    config.body_bounce_strength = _validate_non_negative(
        "config.body_bounce_strength",
        config.body_bounce_strength,
    )
    config.body_sway_strength = _validate_non_negative(
        "config.body_sway_strength",
        config.body_sway_strength,
    )
    config.walk_speed = _validate_non_negative(
        "config.walk_speed",
        config.walk_speed,
    )
    config.run_multiplier = _validate_non_negative(
        "config.run_multiplier",
        config.run_multiplier,
    )
    config.precision_multiplier = _validate_non_negative(
        "config.precision_multiplier",
        config.precision_multiplier,
    )

    config.min_scale = max(
        0.001,
        _validate_non_negative(
            "config.min_scale",
            config.min_scale,
        ),
    )
    config.max_scale = max(
        config.min_scale,
        _validate_non_negative(
            "config.max_scale",
            config.max_scale,
        ),
    )

    return config


class BodyRig(VGroup):
    """
    Master creature control rig.

    Owns:
    - BodyM visible creature
    - FaceRig controller
    - ArmRig controller
    - LegRig controller
    - root transform state
    - movement state
    - balance state
    """

    def __init__(
        self,
        body: Optional[BodyM] = None,
        *,
        config: Optional[BodyRigConfig] = None,
        name: str = "body_rig",
        position=None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.config = _validated_config(
            config,
        )
        self.rig_name = str(name)

        self.body = body or build_body_m()

        self.root_transform: RootTransformNode = create_root_transform(
            name=f"{self.rig_name}_root",
            mobject=self,
        )

        self.current_position = zero_vector()
        self.target_position = zero_vector()
        self.current_velocity = zero_vector()

        self.current_rotation = 0.0
        self.target_rotation = 0.0

        self.current_scale = 1.0
        self.walk_cycle = 0.0

        self.is_hidden = False
        self.is_moving = False
        self.is_grounded = True

        self.center_of_mass = zero_vector()
        self.balance_offset = zero_vector()

        self.body_tilt = 0.0
        self.body_bounce = 0.0
        self.body_sway = 0.0

        self._build_rigs_from_body()
        self._assemble()
        self._register_metadata()

        if position is not None:
            self.teleport(position)

        self.name = "creature_body_rig"
        self.is_creature_body_rig = True

    def _build_rigs_from_body(self) -> None:
        """
        Build controller rigs from existing BodyM parts.

        Important:
        This does not rebuild duplicate visual parts.
        It wraps already-created body parts.
        """

        self.face_rig: Optional[FaceRig] = None
        self.arm_rig: Optional[ArmRig] = None
        self.leg_rig: Optional[LegRig] = None

        if getattr(self.body, "eyes", None) is not None:
            self.face_rig = build_face_rig(
                eyes=self.body.eyes,
                nose=self.body.nose,
                mouth=self.body.mouth,
                body_center=self.body.body_center,
            )

        if getattr(self.body, "arms", None) is not None:
            self.arm_rig = ArmRig(
                arm_group=self.body.arms,
                body_center=self.body.body_center,
            )

        if getattr(self.body, "legs", None) is not None:
            self.leg_rig = LegRig(
                leg_group=self.body.legs,
                body_center=self.body.body_center,
            )

    def _assemble(self) -> None:
        """
        Add only the full body object.

        Rigs are controllers/wrappers around parts already inside BodyM,
        so they are not added again.
        """

        self.add(
            self.body,
        )

    def _register_metadata(self) -> None:
        """
        Register root metadata and convenience references.
        """

        self.root_anchor = zero_vector()
        self.center_anchor = as_vec3(
            self.body.body_center,
            name="body.body_center",
        )

        self.root_transform.set_root_pivot(
            self.root_anchor,
        )
        self.root_transform.set_center_point(
            self.center_anchor,
        )

        self.root_transform.add_child(
            self.body.get_transform_node(),
        )

        self.parts = {
            "body": self.body,
            "face_rig": self.face_rig,
            "arm_rig": self.arm_rig,
            "leg_rig": self.leg_rig,
        }

    def move(
        self,
        direction,
        speed: float,
        delta_time: float,
    ) -> None:
        """
        High-level movement state update.

        This moves the root group only.
        Child parts remain connected because they are inside BodyM.
        """

        direction_vec = as_vec3(
            direction,
            name="direction",
        )
        speed = _validate_non_negative(
            "speed",
            speed,
        )
        delta_time = _validate_non_negative(
            "delta_time",
            delta_time,
        )

        direction_norm = normalize(
            direction_vec,
        )

        if np.linalg.norm(direction_norm) <= 1e-8 or speed <= 0.0:
            self.is_moving = False
            self.current_velocity = zero_vector()
            return

        self.is_moving = True
        self.current_velocity = direction_norm * speed

        movement = self.current_velocity * delta_time
        self.current_position = self.current_position + movement

        self.move_to(
            self.current_position,
        )

        self.root_transform.move_root_to(
            self.current_position,
        )
        self.root_transform.set_velocity(
            self.current_velocity,
        )
        self.root_transform.set_facing_direction(
            direction_norm,
        )

        self.walk_cycle += delta_time * speed

        if self.leg_rig is not None:
            self.leg_rig.move_in_direction(
                direction_norm,
                speed,
                delta_time,
            )

        self._update_balance()

    def move_towards(
        self,
        target_position,
        delta_time: float,
    ) -> None:
        """
        Smoothly move root toward target position.
        """

        target = as_vec3(
            target_position,
            name="target_position",
        )
        delta_time = _validate_non_negative(
            "delta_time",
            delta_time,
        )

        self.target_position = target

        next_position = damp_vector(
            self.current_position,
            self.target_position,
            self.config.movement_smoothing,
            delta_time,
        )

        self.current_velocity = (
            next_position
            - self.current_position
        )

        self.current_position = next_position

        self.move_to(
            self.current_position,
        )

        self.root_transform.move_root_to(
            self.current_position,
        )

    def _update_balance(self) -> None:
        """
        Solve body balance metadata.

        This stores values for actions/controllers.
        It avoids accumulating direct shift/rotate on body each frame.
        """

        cycle = (
            np.sin(self.walk_cycle)
            * 0.5
            + 0.5
        )

        self.body_bounce = solve_body_bounce(
            cycle,
            self.config.body_bounce_strength,
        )

        self.body_sway = solve_body_sway(
            cycle,
            self.config.body_sway_strength,
        )

        self.body_tilt = solve_body_tilt(
            self.current_velocity,
            self.config.body_tilt_strength,
        )

        self.center_of_mass = point(
            self.body_sway,
            self.body_bounce,
            0.0,
        )

        self.balance_offset = self.center_of_mass

    def rotate_towards(
        self,
        target_angle: float,
        delta_time: float,
    ) -> None:
        """
        Smooth procedural turning.
        """

        self.target_rotation = _validate_numeric(
            "target_angle",
            target_angle,
        )

        delta_time = _validate_non_negative(
            "delta_time",
            delta_time,
        )

        self.current_rotation = damp(
            self.current_rotation,
            self.target_rotation,
            self.config.rotation_smoothing,
            delta_time,
        )

        self.rotate(
            self.current_rotation,
            about_point=self.root_anchor,
        )

        self.root_transform.set_local_rotation(
            self.current_rotation,
        )

    def rotate_to(
        self,
        target_angle: float,
        delta_time: float = 0.016,
    ) -> None:
        """
        Compatibility alias.
        """

        self.rotate_towards(
            target_angle,
            delta_time,
        )

    def set_rotation(
        self,
        angle: float,
    ) -> None:
        """
        Directly set body rig rotation state.
        """

        self.current_rotation = _validate_numeric(
            "angle",
            angle,
        )

        self.rotate(
            self.current_rotation,
            about_point=self.root_anchor,
        )

        self.root_transform.set_local_rotation(
            self.current_rotation,
        )

    def get_rotation(self) -> float:
        """
        Return current rotation.
        """

        return float(
            self.current_rotation,
        )

    def teleport(
        self,
        position,
    ) -> None:
        """
        Instant reposition.
        """

        position_vec = as_vec3(
            position,
            name="position",
        )

        self.current_position = position_vec
        self.target_position = position_vec

        self.move_to(
            position_vec,
        )

        self.root_transform.move_root_to(
            position_vec,
        )

    def set_creature_scale(
        self,
        scale_value: float,
    ) -> None:
        """
        Global creature scaling.
        """

        scale_value = clamp(
            _validate_numeric(
                "scale_value",
                scale_value,
            ),
            self.config.min_scale,
            self.config.max_scale,
        )

        ratio = scale_value / self.current_scale

        self.scale(
            ratio,
        )

        self.current_scale = scale_value

    def hide_creature(self) -> None:
        """
        Hide without destroying state.
        """

        self.is_hidden = True
        self.set_opacity(0.0)
        self.root_transform.set_visible(False)

    def show_creature(self) -> None:
        """
        Restore creature visibility.
        """

        self.is_hidden = False
        self.set_opacity(1.0)
        self.root_transform.set_visible(True)

    def toggle_visibility(self) -> None:
        if self.is_hidden:
            self.show_creature()
        else:
            self.hide_creature()

    def get_root_transform(self) -> RootTransformNode:
        return self.root_transform

    def get_transform_node(self) -> RootTransformNode:
        return self.root_transform

    def get_body(self) -> BodyM:
        return self.body

    def get_face_rig(self) -> Optional[FaceRig]:
        return self.face_rig

    def get_arm_rig(self) -> Optional[ArmRig]:
        return self.arm_rig

    def get_leg_rig(self) -> Optional[LegRig]:
        return self.leg_rig

    def get_center_of_mass(self):
        return np.array(
            self.center_of_mass,
            dtype=float,
        )

    def get_velocity(self):
        return np.array(
            self.current_velocity,
            dtype=float,
        )

    def get_facing_direction(self):
        return np.array(
            self.root_transform.get_facing_direction(),
            dtype=float,
        )

    def get_part(
        self,
        name: str,
    ):
        return self.parts.get(
            name,
        )

    def creature_is_hidden(self) -> bool:
        return bool(
            self.is_hidden,
        )

    def creature_is_moving(self) -> bool:
        return bool(
            self.is_moving,
        )

    def reset_pose(self) -> None:
        """
        Reset full creature procedural state.
        """

        self.current_velocity = zero_vector()
        self.current_rotation = 0.0
        self.target_rotation = 0.0
        self.walk_cycle = 0.0

        self.center_of_mass = zero_vector()
        self.balance_offset = zero_vector()

        self.body_tilt = 0.0
        self.body_bounce = 0.0
        self.body_sway = 0.0

        if self.face_rig is not None:
            self.face_rig.reset_look()

        if self.arm_rig is not None:
            self.arm_rig.reset_pose()

        if self.leg_rig is not None:
            self.leg_rig.reset_pose()

    def enable_debug(self) -> None:
        if self.leg_rig is not None:
            self.leg_rig.enable_debug()

    def disable_debug(self) -> None:
        if self.leg_rig is not None:
            self.leg_rig.disable_debug()

    def debug_print(self) -> None:
        print("========== BODY RIG DEBUG ==========")
        print("Name:", self.rig_name)
        print("Position:", self.current_position)
        print("Rotation:", self.current_rotation)
        print("Velocity:", self.current_velocity)
        print("Moving:", self.is_moving)
        print("Hidden:", self.is_hidden)
        print("Has FaceRig:", self.face_rig is not None)
        print("Has ArmRig:", self.arm_rig is not None)
        print("Has LegRig:", self.leg_rig is not None)
        print("====================================")

    def __repr__(self) -> str:
        return (
            "BodyRig("
            f"name={self.rig_name!r}"
            ")"
        )


def build_body_rig(
    position=None,
    config: Optional[BodyRigConfig] = None,
    body: Optional[BodyM] = None,
) -> BodyRig:
    """
    Create master creature body rig.
    """

    if LOG_CREATURE_BUILD:
        logger.info("Building body rig")

    rig = BodyRig(
        body=body,
        config=config,
    )

    if position is not None:
        rig.teleport(
            position,
        )

    if DEBUG_MODE:
        logger.debug(
            "Body rig built | position=%s",
            position,
        )

    if LOG_CREATURE_BUILD:
        logger.info("Body rig created successfully")

    return rig


__all__ = [
    "BodyRigConfig",
    "BodyRig",
    "build_body_rig",
]