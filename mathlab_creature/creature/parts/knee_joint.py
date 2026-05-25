"""
mathlab_creature/creature/parts/knee_joint.py

Production-grade articulated knee joint
for creature rigging systems.

Core Responsibilities
---------------------
- knee pivot
- bend visualization
- hierarchy-safe rotation
- debug support
- future deformation support

Design Goals
------------
- animation-safe
- IK-ready
- hierarchy-safe
- visually readable
- reusable
- future 3D-ready
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from manimlib import (
    VGroup,
    Circle,
    Dot,
    Line,
    Arc,
    Text,
)

from manimlib.constants import (
    GREY_B,
    BLUE_E,
    YELLOW,
    WHITE,
    RED,
    GREEN,
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
class KneeJointConfig:
    """
    Tunable knee configuration.
    """

    radius: float = 0.09

    fill_color = GREY_B
    outline_color = WHITE

    debug_color = YELLOW

    stroke_width: float = 2.0

    angle_arc_radius: float = 0.28

    axis_length: float = 0.35

    show_debug_axes: bool = False
    show_angle_text: bool = False


# =========================================================
# KNEE JOINT
# =========================================================

class KneeJoint(VGroup):
    """
    Production-grade articulated knee joint.

    Features:
    - rotation pivot
    - angle visualization
    - debug overlays
    - future IK support
    - transform hierarchy support
    """

    def __init__(
        self,
        config: KneeJointConfig | None = None,
        name: str = "knee_joint",
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.config = config or KneeJointConfig()

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

        # -------------------------------------------------
        # BUILD
        # -------------------------------------------------

        self._build_joint()
        self._build_debug_elements()

        self._update_debug_visibility()

    # =====================================================
    # BUILD
    # =====================================================

    def _build_joint(self):
        """
        Build visible joint geometry.
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
            color=BLUE_E,
        )

        self.add(
            self.outer_joint,
            self.inner_joint,
        )

    # =====================================================
    # DEBUG BUILD
    # =====================================================

    def _build_debug_elements(self):
        """
        Build all debug visualization.
        """

        self.debug_group = VGroup()

        # -------------------------------------------------
        # LOCAL AXES
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
            start_angle=0,
            angle=0.001,
            color=self.config.debug_color,
            stroke_width=3,
        )

        # -------------------------------------------------
        # ANGLE TEXT
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
                    self.config.angle_arc_radius + 0.2,
                    0.0,
                )
            )
        )

        # -------------------------------------------------
        # BEND DIRECTION LINE
        # -------------------------------------------------

        self.bend_line = Line(
            vec3(),
            vec3(0.0, -0.45, 0.0),
            color=RED,
            stroke_width=2,
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
        # ASSEMBLE
        # -------------------------------------------------

        self.debug_group.add(
            self.axes_debug,
            self.angle_arc,
            self.angle_text,
            self.bend_line,
            self.pivot_dot,
        )

        self.add(self.debug_group)

    # =====================================================
    # DEBUG VISIBILITY
    # =====================================================

    def _update_debug_visibility(self):
        """
        Toggle debug visibility.
        """

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
    # ANGLE CONTROL
    # =====================================================

    def set_joint_angle(
        self,
        angle: float,
    ):
        """
        Set knee bend angle.
        """

        self.current_angle = angle

        self._update_angle_visualization()

    def rotate_joint(
        self,
        delta_angle: float,
    ):
        """
        Incremental rotation.
        """

        self.current_angle += delta_angle

        self._update_angle_visualization()

    # =====================================================
    # ANGLE VISUALIZATION
    # =====================================================

    def _update_angle_visualization(self):
        """
        Update debug angle graphics.
        """

        # -------------------------------------------------
        # UPDATE ARC
        # -------------------------------------------------

        new_arc = Arc(
            radius=self.config.angle_arc_radius,
            start_angle=-PI / 2,
            angle=self.current_angle,
            color=self.config.debug_color,
            stroke_width=3,
        )

        self.angle_arc.become(new_arc)

        # -------------------------------------------------
        # UPDATE TEXT
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
                    self.config.angle_arc_radius + 0.2,
                    0.0,
                )
            )
        )

        self.angle_text.become(new_text)

        # -------------------------------------------------
        # UPDATE BEND LINE
        # -------------------------------------------------

        direction = vec3(
            np.sin(self.current_angle),
            -np.cos(self.current_angle),
            0.0,
        )

        end = direction * 0.45

        new_line = Line(
            vec3(),
            end,
            color=RED,
            stroke_width=2,
        )

        self.bend_line.become(new_line)

    # =====================================================
    # TRANSFORM ACCESS
    # =====================================================

    def get_transform_node(self) -> TransformNode:
        return self.transform_node

    # =====================================================
    # PIVOT ACCESS
    # =====================================================

    def get_pivot_position(self):
        return vec3()

    def get_center_position(self):
        return vec3()

    # =====================================================
    # STATE
    # =====================================================

    def get_joint_angle(self) -> float:
        return self.current_angle

    # =====================================================
    # RESET
    # =====================================================

    def reset_joint(self):
        """
        Reset knee state.
        """

        self.current_angle = 0.0

        self._update_angle_visualization()

    # =====================================================
    # DEBUG PRINT
    # =====================================================

    def debug_print(self):
        print("========== KNEE DEBUG ==========")
        print("Name:", self.joint_name)
        print("Angle:", self.current_angle)
        print("Debug Enabled:", self.debug_enabled)
        print("================================")

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self):
        return (
            f"KneeJoint("
            f"name='{self.joint_name}', "
            f"angle={round(self.current_angle, 3)}"
            f")"
        )


# =========================================================
# FACTORY HELPERS
# =========================================================

def build_knee_joint(
    config: KneeJointConfig | None = None,
) -> KneeJoint:
    """
    Create production-ready knee joint.
    """

    return KneeJoint(
        config=config,
    )


def build_debug_knee_joint(
    config: KneeJointConfig | None = None,
) -> KneeJoint:
    """
    Create knee joint with debug enabled.
    """

    joint = KneeJoint(config=config)

    joint.enable_debug()

    return joint