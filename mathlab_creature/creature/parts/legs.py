"""
mathlab_creature/creature/parts/legs.py

Production-grade articulated leg system
for MathLab creature rigging.

Core Responsibilities
---------------------
- upper leg geometry
- lower leg geometry
- joint hierarchy
- pivot-safe transforms
- realistic proportions
- center anchors
- reusable limb architecture

Design Goals
------------
- production-ready
- hierarchy-safe
- animation-safe
- future IK-ready
- future 3D-ready
- procedural-animation-ready
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from manimlib import (
    VGroup,
    RoundedRectangle,
    Circle,
)

from manimlib.constants import (
    WHITE,
    BLUE_E,
    GREY_B,
    ORIGIN,
)

from mathlab_creature.core.transforms import (
    TransformNode,
    create_transform_node,
    vec3,
)


# =========================================================
# LEG CONFIG
# =========================================================

@dataclass
class LegConfig:
    """
    Tunable leg proportions.
    """

    upper_leg_length: float = 1.1
    lower_leg_length: float = 1.0

    upper_leg_width: float = 0.28
    lower_leg_width: float = 0.24

    joint_radius: float = 0.09

    leg_color = BLUE_E
    joint_color = GREY_B

    corner_radius: float = 0.12

    hip_offset_x: float = 0.32
    foot_spacing: float = 0.25


# =========================================================
# LEG SEGMENT
# =========================================================

class LegSegment(VGroup):
    """
    Generic articulated limb segment.

    Supports:
    - pivot transforms
    - hierarchy-safe movement
    - center anchors
    """

    def __init__(
        self,
        length: float,
        width: float,
        color=WHITE,
        corner_radius: float = 0.1,
        name: str = "segment",
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.segment_name = name

        # -------------------------------------------------
        # GEOMETRY
        # -------------------------------------------------

        self.body = RoundedRectangle(
            width=width,
            height=length,
            corner_radius=corner_radius,
            stroke_width=0,
            fill_opacity=1.0,
            fill_color=color,
        )

        self.add(self.body)

        # -------------------------------------------------
        # TRANSFORM NODE
        # -------------------------------------------------

        self.transform_node = create_transform_node(
            name=name,
            mobject=self,
        )

        # -------------------------------------------------
        # PIVOT SYSTEM
        # -------------------------------------------------

        self.top_anchor = vec3(0.0, length / 2.0, 0.0)
        self.bottom_anchor = vec3(0.0, -length / 2.0, 0.0)

        self.center_anchor = vec3()

        self.transform_node.set_center_point(
            self.center_anchor
        )

        # Rotate around top by default
        self.transform_node.set_root_pivot(
            self.top_anchor
        )

    # =====================================================
    # ANCHORS
    # =====================================================

    def get_top_anchor(self):
        return np.array(self.top_anchor)

    def get_bottom_anchor(self):
        return np.array(self.bottom_anchor)

    def get_center_anchor(self):
        return np.array(self.center_anchor)

    # =====================================================
    # TRANSFORM
    # =====================================================

    def get_transform_node(self):
        return self.transform_node


# =========================================================
# KNEE JOINT
# =========================================================

class KneeJoint(VGroup):
    """
    Visual knee connector.

    Used for:
    - articulation
    - debugging
    - future deformation support
    """

    def __init__(
        self,
        radius: float = 0.08,
        color=GREY_B,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.joint = Circle(
            radius=radius,
            stroke_width=0,
            fill_opacity=1.0,
            fill_color=color,
        )

        self.add(self.joint)

        self.transform_node = create_transform_node(
            name="knee_joint",
            mobject=self,
        )

        self.transform_node.set_center_point(
            vec3()
        )

        self.transform_node.set_root_pivot(
            vec3()
        )

    def get_transform_node(self):
        return self.transform_node


# =========================================================
# ARTICULATED LEG
# =========================================================

class ArticulatedLeg(VGroup):
    """
    Full articulated creature leg.

    Structure:
        hip
         ↓
    upper_leg
         ↓
      knee
         ↓
    lower_leg
         ↓
      ankle
    """

    def __init__(
        self,
        config: LegConfig | None = None,
        side: str = "left",
        name: str = "leg",
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.config = config or LegConfig()

        self.side = side
        self.leg_name = name

        # -------------------------------------------------
        # ROOT TRANSFORM
        # -------------------------------------------------

        self.transform_node = create_transform_node(
            name=name,
            mobject=self,
        )

        # -------------------------------------------------
        # BUILD
        # -------------------------------------------------

        self._build_upper_leg()
        self._build_knee()
        self._build_lower_leg()

        self._assemble_hierarchy()

        self._position_parts()

        self._register_anchors()

    # =====================================================
    # BUILD PARTS
    # =====================================================

    def _build_upper_leg(self):
        self.upper_leg = LegSegment(
            length=self.config.upper_leg_length,
            width=self.config.upper_leg_width,
            color=self.config.leg_color,
            corner_radius=self.config.corner_radius,
            name=f"{self.side}_upper_leg",
        )

    def _build_knee(self):
        self.knee_joint = KneeJoint(
            radius=self.config.joint_radius,
            color=self.config.joint_color,
        )

    def _build_lower_leg(self):
        self.lower_leg = LegSegment(
            length=self.config.lower_leg_length,
            width=self.config.lower_leg_width,
            color=self.config.leg_color,
            corner_radius=self.config.corner_radius,
            name=f"{self.side}_lower_leg",
        )

    # =====================================================
    # HIERARCHY
    # =====================================================

    def _assemble_hierarchy(self):
        """
        Build transform hierarchy.
        """

        self.transform_node.add_child(
            self.upper_leg.get_transform_node()
        )

        self.upper_leg.get_transform_node().add_child(
            self.knee_joint.get_transform_node()
        )

        self.knee_joint.get_transform_node().add_child(
            self.lower_leg.get_transform_node()
        )

    # =====================================================
    # POSITIONING
    # =====================================================

    def _position_parts(self):
        """
        Assemble visual geometry.
        """

        upper_half = (
            self.config.upper_leg_length / 2.0
        )

        lower_half = (
            self.config.lower_leg_length / 2.0
        )

        # ---------------------------------------------
        # KNEE POSITION
        # ---------------------------------------------

        knee_y = -upper_half

        self.knee_joint.move_to(
            vec3(0.0, knee_y, 0.0)
        )

        # ---------------------------------------------
        # LOWER LEG POSITION
        # ---------------------------------------------

        lower_y = (
            knee_y - lower_half
        )

        self.lower_leg.move_to(
            vec3(0.0, lower_y, 0.0)
        )

        # ---------------------------------------------
        # ROOT OFFSET
        # ---------------------------------------------

        side_multiplier = (
            -1.0 if self.side == "left"
            else 1.0
        )

        root_offset = vec3(
            side_multiplier
            * self.config.hip_offset_x,
            0.0,
            0.0,
        )

        self.move_to(root_offset)

        # ---------------------------------------------
        # ADD TO GROUP
        # ---------------------------------------------

        self.add(
            self.upper_leg,
            self.knee_joint,
            self.lower_leg,
        )

    # =====================================================
    # ANCHORS
    # =====================================================

    def _register_anchors(self):
        """
        Register important anchor points.
        """

        self.hip_anchor = vec3(
            0.0,
            self.config.upper_leg_length / 2.0,
            0.0,
        )

        self.knee_anchor = vec3(
            0.0,
            -self.config.upper_leg_length / 2.0,
            0.0,
        )

        self.ankle_anchor = vec3(
            0.0,
            -(
                self.config.upper_leg_length
                + self.config.lower_leg_length
            ),
            0.0,
        )

        self.center_anchor = vec3(
            0.0,
            -(
                self.config.upper_leg_length
                + self.config.lower_leg_length
            ) / 2.0,
            0.0,
        )

        self.transform_node.set_center_point(
            self.center_anchor
        )

        self.transform_node.set_root_pivot(
            self.hip_anchor
        )

    # =====================================================
    # ACCESSORS
    # =====================================================

    def get_transform_node(self):
        return self.transform_node

    def get_upper_leg(self):
        return self.upper_leg

    def get_lower_leg(self):
        return self.lower_leg

    def get_knee_joint(self):
        return self.knee_joint

    # =====================================================
    # ANCHORS
    # =====================================================

    def get_hip_anchor(self):
        return np.array(self.hip_anchor)

    def get_knee_anchor(self):
        return np.array(self.knee_anchor)

    def get_ankle_anchor(self):
        return np.array(self.ankle_anchor)

    def get_center_anchor(self):
        return np.array(self.center_anchor)

    # =====================================================
    # POSE CONTROL
    # =====================================================

    def set_upper_leg_rotation(
        self,
        angle: float,
    ):
        self.upper_leg.rotate(
            angle,
            about_point=self.upper_leg.get_top_anchor(),
        )

    def set_lower_leg_rotation(
        self,
        angle: float,
    ):
        self.lower_leg.rotate(
            angle,
            about_point=self.lower_leg.get_top_anchor(),
        )

    # =====================================================
    # RESET
    # =====================================================

    def reset_pose(self):
        """
        Reset procedural transforms.
        """

        self.upper_leg.restore()
        self.lower_leg.restore()

    # =====================================================
    # DEBUG
    # =====================================================

    def print_hierarchy(self):
        self.transform_node.print_tree()


# =========================================================
# FACTORY HELPERS
# =========================================================

def build_left_leg(
    config: LegConfig | None = None,
) -> ArticulatedLeg:
    return ArticulatedLeg(
        config=config,
        side="left",
        name="left_leg",
    )


def build_right_leg(
    config: LegConfig | None = None,
) -> ArticulatedLeg:
    return ArticulatedLeg(
        config=config,
        side="right",
        name="right_leg",
    )


def build_leg_pair(
    config: LegConfig | None = None,
) -> VGroup:
    """
    Create complete creature leg pair.
    """

    config = config or LegConfig()

    left_leg = build_left_leg(config)
    right_leg = build_right_leg(config)

    return VGroup(
        left_leg,
        right_leg,
    )