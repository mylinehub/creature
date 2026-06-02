"""
Leg rig for mathlab-mylinehub-creature.

This file controls already-built leg systems.

Architecture rule:
- leg_rig.py does not create disconnected duplicate joints
- leg_rig.py can build fallback legs if needed
- leg_rig.py controls leg state, foot state, knee angle, ankle angle
- leg_rig.py does not animate directly
- walk_action.py and step_action.py will call this rig later
- audio is not handled here

Connection chain:

    Action
        |
        LegRig
            |
            Left Leg
                |
                KneeJoint
                AnkleJoint
                Foot
            |
            Right Leg
                |
                KneeJoint
                AnkleJoint
                Foot
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
from mathlab_creature.core.kinematics import solve_body_bounce
from mathlab_creature.core.kinematics import solve_body_sway
from mathlab_creature.core.kinematics import solve_step_arc
from mathlab_creature.core.kinematics import smooth_rotate_towards
from mathlab_creature.core.logger import get_logger
from mathlab_creature.core.transforms import TransformNode
from mathlab_creature.core.transforms import create_transform_node

from mathlab_creature.creature.parts.legs import ArticulatedLeg
from mathlab_creature.creature.parts.legs import LegConfig
from mathlab_creature.creature.parts.legs import build_left_leg
from mathlab_creature.creature.parts.legs import build_right_leg
from mathlab_creature.creature.parts.legs import build_legs


logger = get_logger(__name__)


_LEFT_LEG_INDEX = 0
_RIGHT_LEG_INDEX = 1
_LEG_RIG_MIN_COUNT = 2


@dataclass
class LegRigConfig:
    """
    Tunable locomotion settings.
    """

    stride_length: float = 0.70
    step_height: float = 0.28
    walk_cycle_speed: float = 1.50

    hip_bounce_amplitude: float = 0.08
    hip_sway_amplitude: float = 0.05

    foot_lift_threshold: float = 0.55

    upper_leg_length: float = 1.10
    lower_leg_length: float = 1.00

    max_foot_rotation: float = 0.35
    turn_speed: float = 5.0
    movement_smoothing: float = 8.0


def _validate_numeric(
    name: str,
    value: float | int,
) -> float:
    if not isinstance(value, (int, float)):
        raise TypeError(
            f"{name} must be numeric, got {type(value).__name__}"
        )

    return float(value)


def _validate_positive(
    name: str,
    value: float | int,
) -> float:
    value = _validate_numeric(
        name,
        value,
    )

    if value <= 0:
        raise ValueError(
            f"{name} must be > 0, got {value}"
        )

    return value


def _validate_non_negative(
    name: str,
    value: float | int,
) -> float:
    value = _validate_numeric(
        name,
        value,
    )

    if value < 0:
        raise ValueError(
            f"{name} must be >= 0, got {value}"
        )

    return value


def _validate_side(
    side: str,
) -> str:
    if not isinstance(side, str):
        raise TypeError(
            f"side must be str, got {type(side).__name__}"
        )

    side = side.strip().lower()

    if side not in {"left", "right"}:
        raise ValueError(
            "side must be 'left' or 'right'"
        )

    return side


def _validated_config(
    config: Optional[LegRigConfig],
) -> LegRigConfig:
    config = config or LegRigConfig()

    config.stride_length = _validate_non_negative(
        "config.stride_length",
        config.stride_length,
    )
    config.step_height = _validate_non_negative(
        "config.step_height",
        config.step_height,
    )
    config.walk_cycle_speed = _validate_non_negative(
        "config.walk_cycle_speed",
        config.walk_cycle_speed,
    )
    config.hip_bounce_amplitude = _validate_non_negative(
        "config.hip_bounce_amplitude",
        config.hip_bounce_amplitude,
    )
    config.hip_sway_amplitude = _validate_non_negative(
        "config.hip_sway_amplitude",
        config.hip_sway_amplitude,
    )
    config.foot_lift_threshold = clamp(
        config.foot_lift_threshold,
        0.0,
        1.0,
    )
    config.upper_leg_length = _validate_positive(
        "config.upper_leg_length",
        config.upper_leg_length,
    )
    config.lower_leg_length = _validate_positive(
        "config.lower_leg_length",
        config.lower_leg_length,
    )
    config.max_foot_rotation = _validate_non_negative(
        "config.max_foot_rotation",
        config.max_foot_rotation,
    )
    config.turn_speed = _validate_non_negative(
        "config.turn_speed",
        config.turn_speed,
    )
    config.movement_smoothing = _validate_non_negative(
        "config.movement_smoothing",
        config.movement_smoothing,
    )

    return config


def _validate_leg(
    leg: ArticulatedLeg,
) -> None:
    if not isinstance(leg, ArticulatedLeg):
        raise TypeError(
            f"leg must be ArticulatedLeg, got {type(leg).__name__}"
        )


def _validate_leg_group(
    group: VGroup,
) -> None:
    if not isinstance(group, VGroup):
        raise TypeError(
            f"leg group must be VGroup, got {type(group).__name__}"
        )

    if len(group) < _LEG_RIG_MIN_COUNT:
        raise ValueError(
            "leg group must contain left and right legs"
        )


def _leg_config_from_rig_config(
    config: LegRigConfig,
) -> LegConfig:
    return LegConfig(
        upper_leg_length=config.upper_leg_length,
        lower_leg_length=config.lower_leg_length,
    )


def _attach_leg_metadata(
    leg: ArticulatedLeg,
    *,
    side: str,
) -> ArticulatedLeg:
    _validate_leg(
        leg,
    )

    leg.side = _validate_side(
        side,
    )

    if not hasattr(
        leg,
        "transform_node",
    ):
        leg.transform_node = create_transform_node(
            name=f"{side}_leg",
            mobject=leg,
        )

    leg.is_creature_leg = True

    return leg


def _refresh_leg_group_metadata(
    group: VGroup,
) -> VGroup:
    _validate_leg_group(
        group,
    )

    left_leg = group[_LEFT_LEG_INDEX]
    right_leg = group[_RIGHT_LEG_INDEX]

    _attach_leg_metadata(
        left_leg,
        side="left",
    )
    _attach_leg_metadata(
        right_leg,
        side="right",
    )

    group.left_leg = left_leg
    group.right_leg = right_leg

    group.left_foot = left_leg.get_foot()
    group.right_foot = right_leg.get_foot()

    if not hasattr(
        group,
        "transform_node",
    ):
        group.transform_node = create_transform_node(
            name="creature_leg_rig",
            mobject=group,
        )
        group.get_transform_node = lambda: group.transform_node

    group.name = "creature_leg_rig"
    group.is_creature_leg_rig_group = True

    return group


class LegRig:
    """
    Controller wrapper for leg systems.

    Controls:
    - left/right leg access
    - walk-cycle state
    - knee/ankle angle state
    - planted/lifted foot state
    - procedural step metadata
    """

    def __init__(
        self,
        leg_group: Optional[VGroup] = None,
        *,
        left_leg: Optional[ArticulatedLeg] = None,
        right_leg: Optional[ArticulatedLeg] = None,
        body_center=None,
        config: Optional[LegRigConfig] = None,
        debug_enabled: Optional[bool] = None,
    ) -> None:
        self.config = _validated_config(
            config,
        )
        self.body_center = body_center
        self.debug_enabled = DEBUG_MODE if debug_enabled is None else bool(debug_enabled)

        if leg_group is None:
            if left_leg is None or right_leg is None:
                leg_config = _leg_config_from_rig_config(
                    self.config,
                )

                if left_leg is None:
                    left_leg = build_left_leg(
                        body_center=body_center,
                        config=leg_config,
                        include_foot=True,
                        debug_enabled=self.debug_enabled,
                    )

                if right_leg is None:
                    right_leg = build_right_leg(
                        body_center=body_center,
                        config=leg_config,
                        include_foot=True,
                        debug_enabled=self.debug_enabled,
                    )

            leg_group = VGroup(
                left_leg,
                right_leg,
            )

        _refresh_leg_group_metadata(
            leg_group,
        )

        self.group = leg_group
        self.left_leg = leg_group.left_leg
        self.right_leg = leg_group.right_leg
        self.left_foot = leg_group.left_foot
        self.right_foot = leg_group.right_foot

        self.transform_node = leg_group.transform_node

        self.walk_cycle = 0.0
        self.walk_speed = 1.0
        self.current_velocity = zero_vector()
        self.current_rotation = 0.0
        self.is_walking = False

        self.left_foot_planted = True
        self.right_foot_planted = True

        self.current_pose = "idle"

    def _sync_from_group(self) -> None:
        _refresh_leg_group_metadata(
            self.group,
        )

        self.left_leg = self.group.left_leg
        self.right_leg = self.group.right_leg
        self.left_foot = self.group.left_foot
        self.right_foot = self.group.right_foot
        self.transform_node = self.group.transform_node

    def get_group(self) -> VGroup:
        return self.group

    def get_transform_node(self) -> TransformNode:
        return self.transform_node

    def get_left_leg(self) -> ArticulatedLeg:
        return self.left_leg

    def get_right_leg(self) -> ArticulatedLeg:
        return self.right_leg

    def get_left_foot(self):
        return self.left_foot

    def get_right_foot(self):
        return self.right_foot

    def update_walk_cycle(
        self,
        delta_time: float,
        movement_speed: float = 1.0,
    ) -> None:
        """
        Advance procedural gait cycle.
        """
        delta_time = _validate_non_negative(
            "delta_time",
            delta_time,
        )
        movement_speed = _validate_non_negative(
            "movement_speed",
            movement_speed,
        )

        self.walk_cycle += (
            delta_time
            * self.config.walk_cycle_speed
            * movement_speed
        )

    def get_walk_cycle(self) -> float:
        return float(
            self.walk_cycle,
        )

    def _cycle_value(
        self,
        phase_offset: float = 0.0,
    ) -> float:
        """
        Return normalized walk cycle value [0, 1].
        """
        return float(
            np.sin(
                (self.walk_cycle + phase_offset)
                * np.pi,
            )
            * 0.5
            + 0.5
        )

    def _update_single_leg_step_state(
        self,
        leg: ArticulatedLeg,
        *,
        cycle_value: float,
    ) -> None:
        """
        Update one leg's knee/ankle/foot metadata.
        """
        knee_angle = cycle_value * 0.45
        ankle_angle = clamp(
            -knee_angle * 0.35,
            -self.config.max_foot_rotation,
            self.config.max_foot_rotation,
        )

        leg.set_knee_angle(
            knee_angle,
        )
        leg.set_ankle_angle(
            ankle_angle,
        )

        if cycle_value > self.config.foot_lift_threshold:
            leg.set_foot_lifted()
        else:
            leg.set_foot_planted()

    def update_step_pose(
        self,
        *,
        left_phase: float = 0.0,
        right_phase: float = 1.0,
    ) -> None:
        """
        Update both leg states for current walk cycle.

        This stores procedural state and updates debug visuals.
        Segment animation will be handled later by actions/controllers.
        """
        left_cycle = self._cycle_value(
            left_phase,
        )
        right_cycle = self._cycle_value(
            right_phase,
        )

        self._update_single_leg_step_state(
            self.left_leg,
            cycle_value=left_cycle,
        )
        self._update_single_leg_step_state(
            self.right_leg,
            cycle_value=right_cycle,
        )

        self.left_foot_planted = left_cycle <= self.config.foot_lift_threshold
        self.right_foot_planted = right_cycle <= self.config.foot_lift_threshold

    def solve_step_target(
        self,
        start,
        end,
        t: float,
    ):
        """
        Return step arc point for use by step_action.py.
        """
        return solve_step_arc(
            start=start,
            end=end,
            step_height=self.config.step_height,
            t=t,
        )

    def get_body_motion_offset(
        self,
    ):
        """
        Return body bounce/sway offset for current cycle.

        body_rig.py may use this later.
        """
        cycle_value = self._cycle_value()

        bounce = solve_body_bounce(
            cycle_value,
            self.config.hip_bounce_amplitude,
        )

        sway = solve_body_sway(
            cycle_value,
            self.config.hip_sway_amplitude,
        )

        return point(
            sway,
            bounce,
            0.0,
        )

    def move_in_direction(
        self,
        movement_direction,
        speed: float,
        delta_time: float,
    ) -> None:
        """
        High-level procedural movement state update.

        This does not directly move body root.
        movement_controller.py / body_rig.py should move CreatureRoot later.
        """
        direction_vec = as_vec3(
            movement_direction,
            name="movement_direction",
        )

        direction_norm = normalize(
            direction_vec,
        )

        speed = _validate_non_negative(
            "speed",
            speed,
        )
        delta_time = _validate_non_negative(
            "delta_time",
            delta_time,
        )

        if np.linalg.norm(direction_norm) <= 1e-8 or speed <= 0.0:
            self.is_walking = False
            self.current_velocity = zero_vector()
            self.current_pose = "idle"
            return

        self.is_walking = True
        self.current_pose = "walk"
        self.walk_speed = speed
        self.current_velocity = direction_norm * speed

        self.update_walk_cycle(
            delta_time,
            movement_speed=speed,
        )
        self.update_step_pose()

    def rotate_towards(
        self,
        target_angle: float,
        delta_time: float,
    ) -> None:
        """
        Store smooth rig rotation value.

        Actual root rotation should be applied by body_rig.py/controller.
        """
        self.current_rotation = smooth_rotate_towards(
            self.current_rotation,
            target_angle,
            self.config.turn_speed,
            delta_time,
        )

    def get_velocity(self):
        return np.array(
            self.current_velocity,
            dtype=float,
        )

    def foot_is_planted(
        self,
        side: str = "left",
    ) -> bool:
        side = _validate_side(
            side,
        )

        return (
            self.left_foot_planted
            if side == "left"
            else self.right_foot_planted
        )

    def set_feet_planted(self) -> None:
        self.left_leg.set_foot_planted()
        self.right_leg.set_foot_planted()
        self.left_foot_planted = True
        self.right_foot_planted = True

    def set_feet_lifted(self) -> None:
        self.left_leg.set_foot_lifted()
        self.right_leg.set_foot_lifted()
        self.left_foot_planted = False
        self.right_foot_planted = False

    def reset_pose(self) -> None:
        """
        Reset rig state.
        """
        self.walk_cycle = 0.0
        self.walk_speed = 1.0
        self.current_velocity = zero_vector()
        self.current_rotation = 0.0
        self.is_walking = False
        self.current_pose = "idle"

        self.left_leg.reset_leg_state()
        self.right_leg.reset_leg_state()

        self.left_foot_planted = True
        self.right_foot_planted = True

    def enable_debug(self) -> None:
        for leg in (self.left_leg, self.right_leg):
            knee = leg.get_knee_joint()
            ankle = leg.get_ankle_joint()
            foot = leg.get_foot()

            if hasattr(knee, "enable_debug"):
                knee.enable_debug()

            if hasattr(ankle, "enable_debug"):
                ankle.enable_debug()

            if foot is not None and hasattr(foot, "enable_debug"):
                foot.enable_debug()

    def disable_debug(self) -> None:
        for leg in (self.left_leg, self.right_leg):
            knee = leg.get_knee_joint()
            ankle = leg.get_ankle_joint()
            foot = leg.get_foot()

            if hasattr(knee, "disable_debug"):
                knee.disable_debug()

            if hasattr(ankle, "disable_debug"):
                ankle.disable_debug()

            if foot is not None and hasattr(foot, "disable_debug"):
                foot.disable_debug()

    def debug_print(self) -> None:
        print("========== LEG RIG DEBUG ==========")
        print("Body Center:", self.body_center)
        print("Pose:", self.current_pose)
        print("Walk Cycle:", self.walk_cycle)
        print("Velocity:", self.current_velocity)
        print("Left Foot Planted:", self.left_foot_planted)
        print("Right Foot Planted:", self.right_foot_planted)
        print("Left Leg:", getattr(self.left_leg, "name", "left_leg"))
        print("Right Leg:", getattr(self.right_leg, "name", "right_leg"))
        print("===================================")

    def __repr__(self) -> str:
        return (
            "LegRig("
            f"pose={self.current_pose!r}, "
            f"walking={self.is_walking}"
            ")"
        )


def build_leg_rig(
    body_center=None,
    *,
    config: Optional[LegRigConfig] = None,
    debug_enabled: Optional[bool] = None,
) -> LegRig:
    """
    Build full left/right LegRig wrapper.
    """
    if LOG_CREATURE_BUILD:
        logger.info("Building leg rig")

    rig = LegRig(
        body_center=body_center,
        config=config,
        debug_enabled=debug_enabled,
    )

    if LOG_CREATURE_BUILD:
        logger.info("Leg rig created successfully")

    return rig


def build_leg_rig_group(
    body_center=None,
    *,
    config: Optional[LegRigConfig] = None,
    debug_enabled: Optional[bool] = None,
) -> VGroup:
    """
    Compatibility helper returning only VGroup.
    """
    return build_leg_rig(
        body_center=body_center,
        config=config,
        debug_enabled=debug_enabled,
    ).get_group()


def build_left_leg_rig(
    config: Optional[LegRigConfig] = None,
) -> LegRig:
    """
    Compatibility helper.

    Builds a full LegRig and exposes both legs.
    Prefer build_leg_rig().
    """
    return build_leg_rig(
        config=config,
    )


def build_right_leg_rig(
    config: Optional[LegRigConfig] = None,
) -> LegRig:
    """
    Compatibility helper.

    Builds a full LegRig and exposes both legs.
    Prefer build_leg_rig().
    """
    return build_leg_rig(
        config=config,
    )


def build_leg_rig_map(
    body_center=None,
) -> dict[str, object]:
    rig = build_leg_rig(
        body_center=body_center,
    )

    group = rig.get_group()

    return {
        "rig": rig,
        "left_leg": rig.get_left_leg(),
        "right_leg": rig.get_right_leg(),
        "left_foot": rig.get_left_foot(),
        "right_foot": rig.get_right_foot(),
        "group": group,
        "body_center": body_center,
    }


__all__ = [
    "LegRigConfig",
    "LegRig",
    "build_leg_rig",
    "build_leg_rig_group",
    "build_left_leg_rig",
    "build_right_leg_rig",
    "build_leg_rig_map",
]