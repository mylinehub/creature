"""
mathlab_creature/creature/parts/hip_joint.py

Production-grade hip/pelvis joint system
for articulated creature rigs.

Core Responsibilities
---------------------
- pelvis anchor
- left/right leg roots
- root leg attachment
- center-of-mass anchor
- hierarchy-safe transforms
- future body balancing support

Design Goals
------------
- production-ready
- animation-safe
- hierarchy-safe
- future IK-ready
- future 3D-ready
- controller-friendly
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from manimlib import (
    VGroup,
    RoundedRectangle,
    Circle,
    Dot,
    Line,
    Text,
)

from manimlib.constants import (
    BLUE_E,
    GREY_B,
    WHITE,
    YELLOW,
    RED,
    GREEN,
)

from mathlab_creature.core.transforms import (
    TransformNode,
    create_transform_node,
    vec3,
)

from mathlab_creature.core.debug_draw import (
    create_local_axes,
)


# =========================================================
# CONFIG
# =========================================================

@dataclass
class HipJointConfig:
    """
    Tunable pelvis configuration.
    """

    pelvis_width: float = 0.85
    pelvis_height: float = 0.28

    corner_radius: float = 0.12

    pelvis_color = BLUE_E

    joint_radius: float = 0.07
    joint_color = GREY_B

    leg_spacing: float = 0.34

    debug_axis_length: float = 0.45

    show_debug_axes: bool = False


# =========================================================
# HIP JOINT
# =========================================================

class HipJoint(VGroup):
    """
    Production-grade pelvis/hip system.

    Responsibilities:
    - left/right leg anchors
    - body attachment root
    - balance anchor
    - center-of-mass reference
    """

    def __init__(
        self,
        config: HipJointConfig | None = None,
        name: str = "hip_joint",
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.config = config or HipJointConfig()

        self.joint_name = name

        # -------------------------------------------------
        # TRANSFORM NODE
        # -------------------------------------------------

        self.transform_node = create_transform_node(
            name=name,
            mobject=self,
        )

        # -------------------------------------------------
        # INTERNAL STATE
        # -------------------------------------------------

        self.debug_enabled = False

        # -------------------------------------------------
        # BUILD
        # -------------------------------------------------

        self._build_pelvis()
        self._build_leg_roots()
        self._register_anchors()
        self._build_debug()

        self._update_debug_visibility()

    # =====================================================
    # BUILD PELVIS
    # =====================================================

    def _build_pelvis(self):
        """
        Main pelvis geometry.
        """

        self.pelvis = RoundedRectangle(
            width=self.config.pelvis_width,
            height=self.config.pelvis_height,
            corner_radius=self.config.corner_radius,
            stroke_width=0,
            fill_color=self.config.pelvis_color,
            fill_opacity=1.0,
        )

        self.add(self.pelvis)

    # =====================================================
    # LEG ROOTS
    # =====================================================

    def _build_leg_roots(self):
        """
        Left/right leg root pivots.
        """

        spacing = self.config.leg_spacing

        # -------------------------------------------------
        # LEFT ROOT
        # -------------------------------------------------

        self.left_root = Circle(
            radius=self.config.joint_radius,
            stroke_width=0,
            fill_color=self.config.joint_color,
            fill_opacity=1.0,
        )

        self.left_root.move_to(
            vec3(-spacing, 0.0, 0.0)
        )

        # -------------------------------------------------
        # RIGHT ROOT
        # -------------------------------------------------

        self.right_root = Circle(
            radius=self.config.joint_radius,
            stroke_width=0,
            fill_color=self.config.joint_color,
            fill_opacity=1.0,
        )

        self.right_root.move_to(
            vec3(spacing, 0.0, 0.0)
        )

        self.add(
            self.left_root,
            self.right_root,
        )

    # =====================================================
    # ANCHORS
    # =====================================================

    def _register_anchors(self):
        """
        Register important pelvis anchors.
        """

        spacing = self.config.leg_spacing

        # -------------------------------------------------
        # ROOT
        # -------------------------------------------------

        self.root_anchor = vec3()

        # -------------------------------------------------
        # BODY ATTACHMENT
        # -------------------------------------------------

        self.body_anchor = vec3(
            0.0,
            self.config.pelvis_height / 2.0,
            0.0,
        )

        # -------------------------------------------------
        # LEFT LEG
        # -------------------------------------------------

        self.left_leg_anchor = vec3(
            -spacing,
            0.0,
            0.0,
        )

        # -------------------------------------------------
        # RIGHT LEG
        # -------------------------------------------------

        self.right_leg_anchor = vec3(
            spacing,
            0.0,
            0.0,
        )

        # -------------------------------------------------
        # CENTER OF MASS
        # -------------------------------------------------

        self.center_of_mass = vec3()

        # -------------------------------------------------
        # TRANSFORM NODE
        # -------------------------------------------------

        self.transform_node.set_center_point(
            self.center_of_mass
        )

        self.transform_node.set_root_pivot(
            self.root_anchor
        )

    # =====================================================
    # DEBUG BUILD
    # =====================================================

    def _build_debug(self):
        """
        Build pelvis debug overlays.
        """

        self.debug_group = VGroup()

        # -------------------------------------------------
        # LOCAL AXES
        # -------------------------------------------------

        self.axes_debug = create_local_axes(
            origin=vec3(),
            axis_length=self.config.debug_axis_length,
        )

        # -------------------------------------------------
        # CENTER OF MASS
        # -------------------------------------------------

        self.center_dot = Dot(
            point=self.center_of_mass,
            radius=0.035,
            color=YELLOW,
        )

        # -------------------------------------------------
        # BODY ANCHOR
        # -------------------------------------------------

        self.body_anchor_dot = Dot(
            point=self.body_anchor,
            radius=0.03,
            color=GREEN,
        )

        # -------------------------------------------------
        # LEFT CONNECTION LINE
        # -------------------------------------------------

        self.left_line = Line(
            self.root_anchor,
            self.left_leg_anchor,
            color=WHITE,
            stroke_width=2,
        )

        # -------------------------------------------------
        # RIGHT CONNECTION LINE
        # -------------------------------------------------

        self.right_line = Line(
            self.root_anchor,
            self.right_leg_anchor,
            color=WHITE,
            stroke_width=2,
        )

        # -------------------------------------------------
        # LABEL
        # -------------------------------------------------

        self.label = (
            Text(
                "hip_joint",
                font_size=18,
            )
            .scale(0.35)
            .move_to(
                vec3(
                    0.0,
                    self.config.pelvis_height
                    + 0.25,
                    0.0,
                )
            )
        )

        # -------------------------------------------------
        # ASSEMBLE
        # -------------------------------------------------

        self.debug_group.add(
            self.axes_debug,
            self.center_dot,
            self.body_anchor_dot,
            self.left_line,
            self.right_line,
            self.label,
        )

        self.add(self.debug_group)

    # =====================================================
    # DEBUG VISIBILITY
    # =====================================================

    def _update_debug_visibility(self):
        opacity = 1.0 if self.debug_enabled else 0.0

        self.debug_group.set_opacity(opacity)

    # =====================================================
    # DEBUG CONTROL
    # =====================================================

    def enable_debug(self):
        self.debug_enabled = True
        self._update_debug_visibility()

    def disable_debug(self):
        self.debug_enabled = False
        self._update_debug_visibility()

    def toggle_debug(self):
        self.debug_enabled = not self.debug_enabled
        self._update_debug_visibility()

    # =====================================================
    # ACCESSORS
    # =====================================================

    def get_transform_node(self) -> TransformNode:
        return self.transform_node

    # =====================================================
    # ANCHOR ACCESS
    # =====================================================

    def get_root_anchor(self):
        return np.array(self.root_anchor)

    def get_body_anchor(self):
        return np.array(self.body_anchor)

    def get_left_leg_anchor(self):
        return np.array(self.left_leg_anchor)

    def get_right_leg_anchor(self):
        return np.array(self.right_leg_anchor)

    def get_center_of_mass(self):
        return np.array(self.center_of_mass)

    # =====================================================
    # MOVEMENT HELPERS
    # =====================================================

    def shift_center_of_mass(
        self,
        offset,
    ):
        """
        Shift balance center.

        Useful for:
        - walking
        - leaning
        - procedural balance
        """

        offset = np.array(offset, dtype=float)

        self.center_of_mass += offset

        self.transform_node.set_center_point(
            self.center_of_mass
        )

    # =====================================================
    # RESET
    # =====================================================

    def reset_balance(self):
        """
        Reset center-of-mass shift.
        """

        self.center_of_mass = vec3()

        self.transform_node.set_center_point(
            self.center_of_mass
        )

    # =====================================================
    # DEBUG PRINT
    # =====================================================

    def debug_print(self):
        print("========== HIP DEBUG ==========")
        print("Name:", self.joint_name)
        print("Center:", self.center_of_mass)
        print("Left Anchor:", self.left_leg_anchor)
        print("Right Anchor:", self.right_leg_anchor)
        print("================================")

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self):
        return (
            f"HipJoint("
            f"name='{self.joint_name}'"
            f")"
        )


# =========================================================
# FACTORY HELPERS
# =========================================================

def build_hip_joint(
    config: HipJointConfig | None = None,
) -> HipJoint:
    """
    Create production-ready hip joint.
    """

    return HipJoint(
        config=config,
    )


def build_debug_hip_joint(
    config: HipJointConfig | None = None,
) -> HipJoint:
    """
    Create hip joint with debug enabled.
    """

    joint = HipJoint(config=config)

    joint.enable_debug()

    return joint