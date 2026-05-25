"""
mathlab_creature/creature/rigs/leg_rig.py

Production-grade articulated leg rig system
for procedural creature locomotion.

Core Responsibilities
---------------------
- procedural stepping
- hip control
- knee solving
- ankle solving
- gait support
- stride generation
- walk-cycle control
- balance-aware motion

Design Goals
------------
- production-ready
- controller-friendly
- animation-safe
- hierarchy-safe
- procedural-animation-ready
- future IK-ready
- future 3D-ready
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from manimlib import VGroup

from mathlab_creature.core.transforms import (
    TransformNode,
    create_transform_node,
    vec3,
)

from mathlab_creature.core.kinematics import (
    solve_two_bone_ik,
    solve_leg_step_arc,
    solve_body_bounce,
    solve_body_sway,
    smooth_rotate_towards,
    clamp,
)

from mathlab_creature.creature.parts.legs import (
    ArticulatedLeg,
    LegConfig,
)

from mathlab_creature.creature.parts.feet import (
    Foot,
    FootConfig,
)

from mathlab_creature.creature.parts.hip_joint import (
    HipJoint,
    HipJointConfig,
)

from mathlab_creature.creature.parts.knee_joint import (
    KneeJoint,
)

from mathlab_creature.creature.parts.ankle_joint import (
    AnkleJoint,
)


# =========================================================
# CONFIG
# =========================================================

@dataclass
class LegRigConfig:
    """
    Tunable locomotion settings.
    """

    stride_length: float = 0.7

    step_height: float = 0.28

    walk_cycle_speed: float = 1.5

    hip_bounce_amplitude: float = 0.08

    hip_sway_amplitude: float = 0.05

    foot_lift_threshold: float = 0.55

    upper_leg_length: float = 1.1
    lower_leg_length: float = 1.0

    max_foot_rotation: float = 0.35

    turn_speed: float = 5.0

    movement_smoothing: float = 8.0


# =========================================================
# LEG RIG
# =========================================================

class LegRig(VGroup):
    """
    Production-grade procedural leg rig.

    Structure:
        hip_joint
           ↓
        articulated_leg
           ↓
        ankle_joint
           ↓
            foot

    Features:
    - procedural stepping
    - gait solving
    - IK-ready structure
    - balance support
    - realistic motion timing
    """

    def __init__(
        self,
        config: LegRigConfig | None = None,
        side: str = "left",
        name: str = "leg_rig",
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.config = config or LegRigConfig()

        self.side = side

        self.rig_name = name

        # -------------------------------------------------
        # ROOT TRANSFORM
        # -------------------------------------------------

        self.transform_node = create_transform_node(
            name=name,
            mobject=self,
        )

        # -------------------------------------------------
        # MOVEMENT STATE
        # -------------------------------------------------

        self.walk_cycle = 0.0

        self.walk_speed = 1.0

        self.current_velocity = vec3()

        self.target_position = vec3()

        self.current_rotation = 0.0

        self.is_walking = False

        self.foot_planted = True

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
        Build complete rig parts.
        """

        # -------------------------------------------------
        # HIP
        # -------------------------------------------------

        self.hip_joint = HipJoint(
            config=HipJointConfig(),
            name=f"{self.side}_hip_joint",
        )

        # -------------------------------------------------
        # LEG
        # -------------------------------------------------

        leg_config = LegConfig(
            upper_leg_length=self.config.upper_leg_length,
            lower_leg_length=self.config.lower_leg_length,
        )

        self.leg = ArticulatedLeg(
            config=leg_config,
            side=self.side,
            name=f"{self.side}_leg",
        )

        # -------------------------------------------------
        # KNEE
        # -------------------------------------------------

        self.knee_joint = KneeJoint(
            name=f"{self.side}_knee",
        )

        # -------------------------------------------------
        # ANKLE
        # -------------------------------------------------

        self.ankle_joint = AnkleJoint(
            name=f"{self.side}_ankle",
        )

        # -------------------------------------------------
        # FOOT
        # -------------------------------------------------

        self.foot = Foot(
            config=FootConfig(),
            side=self.side,
            name=f"{self.side}_foot",
        )

    # =====================================================
    # HIERARCHY
    # =====================================================

    def _assemble_hierarchy(self):
        """
        Build transform hierarchy.
        """

        self.transform_node.add_child(
            self.hip_joint.get_transform_node()
        )

        self.hip_joint.get_transform_node().add_child(
            self.leg.get_transform_node()
        )

        self.leg.get_transform_node().add_child(
            self.knee_joint.get_transform_node()
        )

        self.knee_joint.get_transform_node().add_child(
            self.ankle_joint.get_transform_node()
        )

        self.ankle_joint.get_transform_node().add_child(
            self.foot.get_transform_node()
        )

    # =====================================================
    # POSITIONING
    # =====================================================

    def _position_parts(self):
        """
        Position visual hierarchy.
        """

        # ---------------------------------------------
        # KNEE
        # ---------------------------------------------

        self.knee_joint.move_to(
            self.leg.get_knee_anchor()
        )

        # ---------------------------------------------
        # ANKLE
        # ---------------------------------------------

        self.ankle_joint.move_to(
            self.leg.get_ankle_anchor()
        )

        # ---------------------------------------------
        # FOOT
        # ---------------------------------------------

        foot_offset = vec3(
            0.0,
            -0.12,
            0.0,
        )

        self.foot.move_to(
            self.leg.get_ankle_anchor()
            + foot_offset
        )

        # ---------------------------------------------
        # ADD TO GROUP
        # ---------------------------------------------

        self.add(
            self.hip_joint,
            self.leg,
            self.knee_joint,
            self.ankle_joint,
            self.foot,
        )

    # =====================================================
    # ANCHORS
    # =====================================================

    def _register_anchors(self):
        """
        Register important rig anchors.
        """

        self.root_anchor = vec3()

        self.hip_anchor = (
            self.hip_joint.get_center_of_mass()
        )

        self.foot_anchor = (
            self.foot.get_contact_anchor()
        )

        self.transform_node.set_root_pivot(
            self.root_anchor
        )

        self.transform_node.set_center_point(
            self.hip_anchor
        )

    # =====================================================
    # WALK CYCLE
    # =====================================================

    def update_walk_cycle(
        self,
        delta_time: float,
        movement_speed: float = 1.0,
    ):
        """
        Advance procedural gait cycle.
        """

        self.walk_cycle += (
            delta_time
            * self.config.walk_cycle_speed
            * movement_speed
        )

    # =====================================================
    # PROCEDURAL STEP
    # =====================================================

    def solve_procedural_step(
        self,
        walk_direction,
    ):
        """
        Solve procedural foot placement.
        """

        cycle = (
            np.sin(self.walk_cycle * np.pi)
            * 0.5
            + 0.5
        )

        stride = (
            walk_direction
            * self.config.stride_length
        )

        foot_target = solve_leg_step_arc(
            start=vec3(),
            end=stride,
            step_height=self.config.step_height,
            t=cycle,
        )

        self.solve_leg_ik(foot_target)

        self._update_foot_state(cycle)

        self._update_body_motion(cycle)

    # =====================================================
    # LEG IK
    # =====================================================

    def solve_leg_ik(
        self,
        foot_target,
    ):
        """
        Solve articulated leg chain.
        """

        solution = solve_two_bone_ik(
            root_position=self.hip_anchor,
            target_position=foot_target,
            upper_length=self.config.upper_leg_length,
            lower_length=self.config.lower_leg_length,
            bend_direction=1.0,
        )

        # ---------------------------------------------
        # APPLY ROTATIONS
        # ---------------------------------------------

        self.leg.set_upper_leg_rotation(
            solution.root_angle
        )

        self.leg.set_lower_leg_rotation(
            solution.joint_angle
        )

        self.knee_joint.set_joint_angle(
            solution.joint_angle
        )

        # ---------------------------------------------
        # FOOT ROTATION
        # ---------------------------------------------

        foot_angle = clamp(
            -solution.joint_angle * 0.35,
            -self.config.max_foot_rotation,
            self.config.max_foot_rotation,
        )

        self.foot.set_rotation(
            foot_angle
        )

        self.ankle_joint.set_ankle_angle(
            foot_angle
        )

    # =====================================================
    # FOOT STATE
    # =====================================================

    def _update_foot_state(
        self,
        cycle_value: float,
    ):
        """
        Handle planted/lifted transitions.
        """

        if (
            cycle_value
            > self.config.foot_lift_threshold
        ):
            self.foot.set_lifted()

            self.ankle_joint.set_lifted()

            self.foot_planted = False

        else:
            self.foot.set_planted()

            self.ankle_joint.set_planted()

            self.foot_planted = True

    # =====================================================
    # BODY MOTION
    # =====================================================

    def _update_body_motion(
        self,
        cycle_value: float,
    ):
        """
        Add natural body motion.
        """

        bounce = solve_body_bounce(
            cycle_value,
            self.config.hip_bounce_amplitude,
        )

        sway = solve_body_sway(
            cycle_value,
            self.config.hip_sway_amplitude,
        )

        self.hip_joint.shift_center_of_mass(
            vec3(
                sway,
                bounce,
                0.0,
            )
        )

    # =====================================================
    # MOVEMENT
    # =====================================================

    def move_in_direction(
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
            self.is_walking = False
            return

        self.is_walking = True

        direction /= magnitude

        self.current_velocity = (
            direction * speed
        )

        movement = (
            self.current_velocity
            * delta_time
        )

        self.shift(movement)

        self.update_walk_cycle(
            delta_time,
            movement_speed=speed,
        )

        self.solve_procedural_step(
            direction,
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

        self.current_rotation = (
            smooth_rotate_towards(
                self.current_rotation,
                target_angle,
                self.config.turn_speed,
                delta_time,
            )
        )

        self.rotate(
            self.current_rotation,
            about_point=self.root_anchor,
        )

    # =====================================================
    # ACCESSORS
    # =====================================================

    def get_transform_node(self):
        return self.transform_node

    def get_hip_joint(self):
        return self.hip_joint

    def get_leg(self):
        return self.leg

    def get_knee_joint(self):
        return self.knee_joint

    def get_ankle_joint(self):
        return self.ankle_joint

    def get_foot(self):
        return self.foot

    # =====================================================
    # STATE ACCESS
    # =====================================================

    def foot_is_planted(self):
        return self.foot_planted

    def get_walk_cycle(self):
        return self.walk_cycle

    def get_velocity(self):
        return np.array(
            self.current_velocity
        )

    # =====================================================
    # RESET
    # =====================================================

    def reset_pose(self):
        """
        Reset entire rig state.
        """

        self.walk_cycle = 0.0

        self.current_velocity = vec3()

        self.current_rotation = 0.0

        self.leg.reset_pose()

        self.knee_joint.reset_joint()

        self.ankle_joint.reset_joint()

        self.foot.reset_foot()

        self.hip_joint.reset_balance()

    # =====================================================
    # DEBUG
    # =====================================================

    def enable_debug(self):
        self.hip_joint.enable_debug()

        self.knee_joint.enable_debug()

        self.ankle_joint.enable_debug()

        self.foot.enable_debug()

    def disable_debug(self):
        self.hip_joint.disable_debug()

        self.knee_joint.disable_debug()

        self.ankle_joint.disable_debug()

        self.foot.disable_debug()

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self):
        return (
            f"LegRig("
            f"name='{self.rig_name}', "
            f"side='{self.side}'"
            f")"
        )


# =========================================================
# FACTORY HELPERS
# =========================================================

def build_left_leg_rig(
    config: LegRigConfig | None = None,
) -> LegRig:
    return LegRig(
        config=config,
        side="left",
        name="left_leg_rig",
    )


def build_right_leg_rig(
    config: LegRigConfig | None = None,
) -> LegRig:
    return LegRig(
        config=config,
        side="right",
        name="right_leg_rig",
    )