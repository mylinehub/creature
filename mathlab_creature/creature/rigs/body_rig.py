"""
mathlab_creature/creature/rigs/body_rig.py

MASTER CONTROL RIG
Production-grade creature body rig system.

Core Responsibilities
---------------------
- center-of-mass
- balance
- leaning
- root movement
- facing direction
- hide/show state
- full creature coordination
- movement orchestration
- gait synchronization

IMPORTANT
---------
This is the MASTER CONTROL RIG.

Everything attaches here:
- body
- face
- arms
- legs
- controllers
- movement systems

Design Goals
------------
- production-ready
- hierarchy-safe
- procedural-animation-ready
- cinematic-motion-ready
- future AI-ready
- future 3D-ready
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from manimlib import (
    VGroup,
)

from mathlab_creature.core.transforms import (
    RootTransformNode,
    create_root_transform,
    vec3,
)

from mathlab_creature.core.kinematics import (
    damp_vector,
    damp,
    solve_body_tilt,
    solve_body_bounce,
    solve_body_sway,
    clamp,
)

from mathlab_creature.creature.parts.body_m import (
    build_body_m,
)

from mathlab_creature.creature.parts.eyes import (
    build_eyes,
)

from mathlab_creature.creature.parts.mouth import (
    build_mouth,
)

from mathlab_creature.creature.parts.nose import (
    build_nose,
)

from mathlab_creature.creature.parts.hat import (
    build_hat,
)

from mathlab_creature.creature.rigs.leg_rig import (
    build_left_leg_rig,
    build_right_leg_rig,
    LegRig,
)

from mathlab_creature.creature.rigs.face_rig import (
    build_face_rig,
)

from mathlab_creature.creature.rigs.arm_rig import (
    build_arm_rig,
)


# =========================================================
# CONFIG
# =========================================================

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

    root_height: float = 0.0

    body_offset_y: float = 1.2

    leg_spacing: float = 0.38


# =========================================================
# BODY RIG
# =========================================================

class BodyRig(VGroup):
    """
    MASTER CREATURE CONTROL RIG.

    Responsibilities:
    - full creature orchestration
    - movement
    - balance
    - visibility
    - root transforms
    - procedural motion
    - gait synchronization
    """

    def __init__(
        self,
        config: BodyRigConfig | None = None,
        name: str = "body_rig",
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.config = config or BodyRigConfig()

        self.rig_name = name

        # -------------------------------------------------
        # ROOT TRANSFORM
        # -------------------------------------------------

        self.root_transform: RootTransformNode = (
            create_root_transform(
                name=f"{name}_root"
            )
        )

        # -------------------------------------------------
        # MOVEMENT STATE
        # -------------------------------------------------

        self.current_position = vec3()

        self.target_position = vec3()

        self.current_velocity = vec3()

        self.current_rotation = 0.0

        self.target_rotation = 0.0

        self.current_scale = vec3(1.0, 1.0, 1.0)

        self.walk_cycle = 0.0

        self.is_hidden = False

        self.is_moving = False

        self.is_grounded = True

        # -------------------------------------------------
        # BALANCE STATE
        # -------------------------------------------------

        self.center_of_mass = vec3()

        self.balance_offset = vec3()

        self.body_tilt = 0.0

        self.body_bounce = 0.0

        self.body_sway = 0.0

        # -------------------------------------------------
        # BUILD
        # -------------------------------------------------

        self._build_parts()

        self._assemble_hierarchy()

        self._position_parts()

        self._register_anchors()

    # =====================================================
    # BUILD
    # =====================================================

    def _build_parts(self):
        """
        Build all major creature systems.
        """

        # -------------------------------------------------
        # BODY
        # -------------------------------------------------

        self.body = build_body_m()

        # -------------------------------------------------
        # FACE
        # -------------------------------------------------

        self.eyes = build_eyes()

        self.mouth = build_mouth()

        self.nose = build_nose()

        self.face_rig = build_face_rig(
            self.eyes,
            self.mouth,
        )

        # -------------------------------------------------
        # HAT
        # -------------------------------------------------

        self.hat = build_hat()

        # -------------------------------------------------
        # ARMS
        # -------------------------------------------------

        self.arm_rig = build_arm_rig()

        # -------------------------------------------------
        # LEGS
        # -------------------------------------------------

        self.left_leg_rig: LegRig = (
            build_left_leg_rig()
        )

        self.right_leg_rig: LegRig = (
            build_right_leg_rig()
        )

    # =====================================================
    # HIERARCHY
    # =====================================================

    def _assemble_hierarchy(self):
        """
        Build master hierarchy.
        """

        self.root_transform.add_child(
            self.left_leg_rig.get_transform_node()
        )

        self.root_transform.add_child(
            self.right_leg_rig.get_transform_node()
        )

        self.root_transform.add_child(
            self.arm_rig.get_transform_node()
        )

        self.root_transform.add_child(
            self.face_rig.get_transform_node()
        )

    # =====================================================
    # POSITIONING
    # =====================================================

    def _position_parts(self):
        """
        Assemble full creature layout.
        """

        # -------------------------------------------------
        # BODY
        # -------------------------------------------------

        self.body.move_to(
            vec3(
                0.0,
                self.config.body_offset_y,
                0.0,
            )
        )

        # -------------------------------------------------
        # FACE
        # -------------------------------------------------

        self.face_rig.move_to(
            vec3(
                0.0,
                self.config.body_offset_y + 0.2,
                0.0,
            )
        )

        # -------------------------------------------------
        # HAT
        # -------------------------------------------------

        self.hat.move_to(
            vec3(
                0.0,
                self.config.body_offset_y + 0.85,
                0.0,
            )
        )

        # -------------------------------------------------
        # LEGS
        # -------------------------------------------------

        self.left_leg_rig.move_to(
            vec3(
                -self.config.leg_spacing,
                0.0,
                0.0,
            )
        )

        self.right_leg_rig.move_to(
            vec3(
                self.config.leg_spacing,
                0.0,
                0.0,
            )
        )

        # -------------------------------------------------
        # ADD
        # -------------------------------------------------

        self.add(
            self.left_leg_rig,
            self.right_leg_rig,
            self.body,
            self.face_rig,
            self.arm_rig,
            self.hat,
        )

    # =====================================================
    # ANCHORS
    # =====================================================

    def _register_anchors(self):
        """
        Register master anchors.
        """

        self.root_anchor = vec3()

        self.center_anchor = vec3(
            0.0,
            self.config.body_offset_y,
            0.0,
        )

        self.root_transform.set_root_pivot(
            self.root_anchor
        )

        self.root_transform.set_center_point(
            self.center_anchor
        )

    # =====================================================
    # MOVEMENT
    # =====================================================

    def move(
        self,
        direction,
        speed: float,
        delta_time: float,
    ):
        """
        High-level procedural movement.
        """

        direction = np.array(
            direction,
            dtype=float,
        )

        magnitude = np.linalg.norm(direction)

        if magnitude <= 1e-5:
            self.is_moving = False
            return

        self.is_moving = True

        direction /= magnitude

        # -------------------------------------------------
        # SPEED
        # -------------------------------------------------

        self.current_velocity = (
            direction * speed
        )

        # -------------------------------------------------
        # POSITION
        # -------------------------------------------------

        movement = (
            self.current_velocity
            * delta_time
        )

        self.current_position += movement

        self.move_to(self.current_position)

        # -------------------------------------------------
        # FACING
        # -------------------------------------------------

        self.root_transform.set_facing_direction(
            direction
        )

        # -------------------------------------------------
        # WALK CYCLE
        # -------------------------------------------------

        self.walk_cycle += (
            delta_time
            * speed
        )

        # -------------------------------------------------
        # LEGS
        # -------------------------------------------------

        self.left_leg_rig.move_in_direction(
            direction,
            speed,
            delta_time,
        )

        self.right_leg_rig.move_in_direction(
            -direction,
            speed,
            delta_time,
        )

        # -------------------------------------------------
        # BALANCE
        # -------------------------------------------------

        self._update_balance()

    # =====================================================
    # BALANCE
    # =====================================================

    def _update_balance(self):
        """
        Solve body balance and weight.
        """

        cycle = (
            np.sin(self.walk_cycle)
            * 0.5
            + 0.5
        )

        # -------------------------------------------------
        # BOUNCE
        # -------------------------------------------------

        self.body_bounce = solve_body_bounce(
            cycle,
            self.config.body_bounce_strength,
        )

        # -------------------------------------------------
        # SWAY
        # -------------------------------------------------

        self.body_sway = solve_body_sway(
            cycle,
            self.config.body_sway_strength,
        )

        # -------------------------------------------------
        # TILT
        # -------------------------------------------------

        self.body_tilt = solve_body_tilt(
            self.current_velocity,
            self.config.body_tilt_strength,
        )

        # -------------------------------------------------
        # CENTER OF MASS
        # -------------------------------------------------

        self.center_of_mass = vec3(
            self.body_sway,
            self.body_bounce,
            0.0,
        )

        # -------------------------------------------------
        # APPLY
        # -------------------------------------------------

        self.body.shift(
            vec3(
                self.body_sway,
                self.body_bounce,
                0.0,
            )
        )

        self.body.rotate(
            self.body_tilt,
            about_point=self.center_anchor,
        )

    # =====================================================
    # ROTATION
    # =====================================================

    def rotate_towards(
        self,
        target_angle: float,
        delta_time: float,
    ):
        """
        Smooth procedural turning.
        """

        self.target_rotation = target_angle

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

    # =====================================================
    # VISIBILITY
    # =====================================================

    def hide_creature(self):
        """
        Hide without destroying state.
        """

        self.is_hidden = True

        self.set_opacity(0.0)

    def show_creature(self):
        """
        Restore creature visibility.
        """

        self.is_hidden = False

        self.set_opacity(1.0)

    def toggle_visibility(self):
        if self.is_hidden:
            self.show_creature()
        else:
            self.hide_creature()

    # =====================================================
    # TELEPORT
    # =====================================================

    def teleport(
        self,
        position,
    ):
        """
        Instant reposition.
        """

        position = np.array(
            position,
            dtype=float,
        )

        self.current_position = position

        self.move_to(position)

    # =====================================================
    # SCALING
    # =====================================================

    def set_creature_scale(
        self,
        scale_value: float,
    ):
        """
        Global creature scaling.
        """

        scale_value = clamp(
            scale_value,
            0.05,
            100.0,
        )

        self.scale(
            scale_value
        )

    # =====================================================
    # ACCESSORS
    # =====================================================

    def get_root_transform(self):
        return self.root_transform

    def get_center_of_mass(self):
        return np.array(
            self.center_of_mass
        )

    def get_velocity(self):
        return np.array(
            self.current_velocity
        )

    def get_facing_direction(self):
        return np.array(
            self.root_transform.facing_direction
        )

    # =====================================================
    # STATE
    # =====================================================

    def creature_is_hidden(self):
        return self.is_hidden

    def creature_is_moving(self):
        return self.is_moving

    # =====================================================
    # RESET
    # =====================================================

    def reset_pose(self):
        """
        Reset full creature state.
        """

        self.current_velocity = vec3()

        self.current_rotation = 0.0

        self.walk_cycle = 0.0

        self.center_of_mass = vec3()

        self.balance_offset = vec3()

        self.body_tilt = 0.0

        self.body_bounce = 0.0

        self.body_sway = 0.0

        self.left_leg_rig.reset_pose()

        self.right_leg_rig.reset_pose()

    # =====================================================
    # DEBUG
    # =====================================================

    def enable_debug(self):
        self.left_leg_rig.enable_debug()

        self.right_leg_rig.enable_debug()

    def disable_debug(self):
        self.left_leg_rig.disable_debug()

        self.right_leg_rig.disable_debug()

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self):
        return (
            f"BodyRig("
            f"name='{self.rig_name}'"
            f")"
        )


# =========================================================
# FACTORY HELPERS
# =========================================================

def build_body_rig(
    position=None,
    config: BodyRigConfig | None = None,
) -> BodyRig:
    """
    Create production-grade creature body rig.
    """

    rig = BodyRig(config=config)

    if position is not None:
        rig.move_to(position)

    return rig