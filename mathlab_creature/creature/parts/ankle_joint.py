"""
mathlab_creature/creature/parts/ankle_joint.py

Production-grade ankle joint system
for articulated creature rigs.

Core Responsibilities
---------------------
- foot pivot
- ankle rotation
- foot attachment root
- procedural walk support
- balance support
- hierarchy-safe transforms

Design Goals
------------
- production-ready
- animation-safe
- IK-ready
- hierarchy-safe
- future 3D-ready
- procedural-motion-ready
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from manimlib import (
    VGroup,
    Circle,
    Dot,
    Arc,
    Line,
    Text,
)

from manimlib.constants import (
    GREY_B,
    BLUE_E,
    WHITE,
    YELLOW,
    GREEN,
    RED,
    PI,
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
class AnkleJointConfig:
    """
    Tunable ankle configuration.
    """

    radius: float = 0.075

    fill_color = GREY_B
    outline_color = WHITE

    foot_direction_color = BLUE_E

    stroke_width: float = 2.0

    axis_length: float = 0.35

    angle_arc_radius: float = 0.24

    show_debug_axes: bool = False


# =========================================================
# ANKLE JOINT
# =========================================================

class AnkleJoint(VGroup):
    """
    Production-grade ankle joint.

    Responsibilities:
    - foot pivot
    - foot rotation
    - ankle articulation
    - walk support
    - balance support
    """

    def __init__(
        self,
        config: AnkleJointConfig | None = None,
        name: str = "ankle_joint",
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.config = config or AnkleJointConfig()

        self.joint_name = name

        # -------------------------------------------------
        # TRANSFORM NODE
        # -------------------------------------------------

        self.transform_node = create_transform_node(
            name=name,
            mobject=self,
        )

        self.transform_node.set_center_point(
            vec3()
        )

        self.transform_node.set_root_pivot(
            vec3()
        )

        # -------------------------------------------------
        # INTERNAL STATE
        # -------------------------------------------------

        self.current_angle = 0.0

        self.debug_enabled = False

        self.is_planted = True

        # -------------------------------------------------
        # BUILD
        # -------------------------------------------------

        self._build_joint()
        self._register_anchors()
        self._build_debug()

        self._update_debug_visibility()

    # =====================================================
    # BUILD JOINT
    # =====================================================

    def _build_joint(self):
        """
        Main ankle geometry.
        """

        self.outer_joint = Circle(
            radius=self.config.radius,
            stroke_color=self.config.outline_color,
            stroke_width=self.config.stroke_width,
            fill_color=self.config.fill_color,
            fill_opacity=1.0,
        )

        self.inner_joint = Dot(
            point=vec3(),
            radius=self.config.radius * 0.35,
            color=self.config.foot_direction_color,
        )

        # -------------------------------------------------
        # FOOT DIRECTION INDICATOR
        # -------------------------------------------------

        self.foot_direction_line = Line(
            vec3(),
            vec3(0.0, -0.38, 0.0),
            color=self.config.foot_direction_color,
            stroke_width=3,
        )

        self.add(
            self.outer_joint,
            self.inner_joint,
            self.foot_direction_line,
        )

    # =====================================================
    # ANCHORS
    # =====================================================

    def _register_anchors(self):
        """
        Register important ankle anchors.
        """

        self.root_anchor = vec3()

        self.upper_attachment_anchor = vec3(
            0.0,
            self.config.radius,
            0.0,
        )

        self.foot_attachment_anchor = vec3(
            0.0,
            -self.config.radius,
            0.0,
        )

        self.center_anchor = vec3()

        self.transform_node.set_center_point(
            self.center_anchor
        )

        self.transform_node.set_root_pivot(
            self.root_anchor
        )

    # =====================================================
    # DEBUG BUILD
    # =====================================================

    def _build_debug(self):
        """
        Build ankle debug overlays.
        """

        self.debug_group = VGroup()

        # -------------------------------------------------
        # AXES
        # -------------------------------------------------

        self.axes_debug = create_local_axes(
            origin=vec3(),
            axis_length=self.config.axis_length,
        )

        # -------------------------------------------------
        # ANGLE ARC
        # -------------------------------------------------

        self.angle_arc = Arc(
            radius=self.config.angle_arc_radius,
            start_angle=-PI / 2,
            angle=0.001,
            color=YELLOW,
            stroke_width=3,
        )

        # -------------------------------------------------
        # PIVOT DOT
        # -------------------------------------------------

        self.pivot_dot = Dot(
            point=vec3(),
            radius=0.025,
            color=GREEN,
        )

        # -------------------------------------------------
        # FOOT TARGET LINE
        # -------------------------------------------------

        self.foot_target_line = Line(
            vec3(),
            vec3(0.0, -0.55, 0.0),
            color=RED,
            stroke_width=2,
        )

        # -------------------------------------------------
        # ANGLE LABEL
        # -------------------------------------------------

        self.angle_text = (
            Text(
                "0°",
                font_size=18,
            )
            .scale(0.35)
            .move_to(
                vec3(
                    0.0,
                    self.config.angle_arc_radius + 0.18,
                    0.0,
                )
            )
        )

        # -------------------------------------------------
        # STATE LABEL
        # -------------------------------------------------

        self.state_text = (
            Text(
                "PLANTED",
                font_size=18,
            )
            .scale(0.35)
            .move_to(
                vec3(
                    0.0,
                    -0.45,
                    0.0,
                )
            )
        )

        # -------------------------------------------------
        # ASSEMBLE
        # -------------------------------------------------

        self.debug_group.add(
            self.axes_debug,
            self.angle_arc,
            self.pivot_dot,
            self.foot_target_line,
            self.angle_text,
            self.state_text,
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
    # ROTATION
    # =====================================================

    def set_ankle_angle(
        self,
        angle: float,
    ):
        """
        Set ankle articulation angle.
        """

        self.current_angle = angle

        self._update_visuals()

    def rotate_ankle(
        self,
        delta_angle: float,
    ):
        """
        Incremental ankle rotation.
        """

        self.current_angle += delta_angle

        self._update_visuals()

    # =====================================================
    # FOOT STATE
    # =====================================================

    def set_planted(self):
        """
        Foot planted on ground.
        """

        self.is_planted = True

        self._update_state_visual()

    def set_lifted(self):
        """
        Foot lifted during step.
        """

        self.is_planted = False

        self._update_state_visual()

    # =====================================================
    # VISUAL UPDATE
    # =====================================================

    def _update_visuals(self):
        """
        Update angle visuals.
        """

        # -------------------------------------------------
        # DIRECTION LINE
        # -------------------------------------------------

        direction = vec3(
            np.sin(self.current_angle),
            -np.cos(self.current_angle),
            0.0,
        )

        end = direction * 0.38

        new_line = Line(
            vec3(),
            end,
            color=self.config.foot_direction_color,
            stroke_width=3,
        )

        self.foot_direction_line.become(new_line)

        # -------------------------------------------------
        # ARC
        # -------------------------------------------------

        new_arc = Arc(
            radius=self.config.angle_arc_radius,
            start_angle=-PI / 2,
            angle=self.current_angle,
            color=YELLOW,
            stroke_width=3,
        )

        self.angle_arc.become(new_arc)

        # -------------------------------------------------
        # ANGLE LABEL
        # -------------------------------------------------

        degrees = round(
            np.degrees(self.current_angle),
            1,
        )

        new_text = (
            Text(
                f"{degrees}°",
                font_size=18,
            )
            .scale(0.35)
            .move_to(
                vec3(
                    0.0,
                    self.config.angle_arc_radius + 0.18,
                    0.0,
                )
            )
        )

        self.angle_text.become(new_text)

        # -------------------------------------------------
        # TARGET LINE
        # -------------------------------------------------

        foot_end = direction * 0.55

        new_target_line = Line(
            vec3(),
            foot_end,
            color=RED,
            stroke_width=2,
        )

        self.foot_target_line.become(
            new_target_line
        )

    # =====================================================
    # STATE VISUAL
    # =====================================================

    def _update_state_visual(self):
        """
        Update planted/lifted state text.
        """

        state_label = (
            "PLANTED"
            if self.is_planted
            else "LIFTED"
        )

        color = (
            GREEN
            if self.is_planted
            else YELLOW
        )

        new_state = (
            Text(
                state_label,
                font_size=18,
                color=color,
            )
            .scale(0.35)
            .move_to(
                vec3(
                    0.0,
                    -0.45,
                    0.0,
                )
            )
        )

        self.state_text.become(new_state)

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

    def get_upper_attachment_anchor(self):
        return np.array(
            self.upper_attachment_anchor
        )

    def get_foot_attachment_anchor(self):
        return np.array(
            self.foot_attachment_anchor
        )

    def get_center_anchor(self):
        return np.array(self.center_anchor)

    # =====================================================
    # STATE ACCESS
    # =====================================================

    def get_ankle_angle(self) -> float:
        return self.current_angle

    def foot_is_planted(self) -> bool:
        return self.is_planted

    # =====================================================
    # RESET
    # =====================================================

    def reset_joint(self):
        """
        Reset ankle state.
        """

        self.current_angle = 0.0

        self.is_planted = True

        self._update_visuals()
        self._update_state_visual()

    # =====================================================
    # DEBUG PRINT
    # =====================================================

    def debug_print(self):
        print("========== ANKLE DEBUG ==========")
        print("Name:", self.joint_name)
        print("Angle:", self.current_angle)
        print("Planted:", self.is_planted)
        print("=================================")

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self):
        return (
            f"AnkleJoint("
            f"name='{self.joint_name}', "
            f"angle={round(self.current_angle, 3)}"
            f")"
        )


# =========================================================
# FACTORY HELPERS
# =========================================================

def build_ankle_joint(
    config: AnkleJointConfig | None = None,
) -> AnkleJoint:
    """
    Create production-ready ankle joint.
    """

    return AnkleJoint(
        config=config,
    )


def build_debug_ankle_joint(
    config: AnkleJointConfig | None = None,
) -> AnkleJoint:
    """
    Create ankle joint with debug enabled.
    """

    joint = AnkleJoint(config=config)

    joint.enable_debug()

    return joint