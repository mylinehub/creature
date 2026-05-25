"""
mathlab_creature/creature/parts/feet.py

Production-grade articulated foot system
for creature locomotion and balance.

Core Responsibilities
---------------------
- planted state
- lifted state
- foot rotation
- walk contact realism
- foot roll support
- ankle attachment
- ground contact logic

Design Goals
------------
- production-ready
- animation-safe
- hierarchy-safe
- procedural-walk-ready
- future IK-ready
- future 3D-ready
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from manimlib import (
    VGroup,
    RoundedRectangle,
    Dot,
    Line,
    Arc,
    Text,
)

from manimlib.constants import (
    BLUE_E,
    GREY_B,
    WHITE,
    GREEN,
    YELLOW,
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
class FootConfig:
    """
    Tunable foot proportions.
    """

    width: float = 0.55
    height: float = 0.22

    corner_radius: float = 0.11

    foot_color = BLUE_E

    sole_color = GREY_B

    stroke_width: float = 0

    debug_axis_length: float = 0.4

    contact_arc_radius: float = 0.25

    heel_offset: float = 0.12
    toe_offset: float = 0.18


# =========================================================
# FOOT
# =========================================================

class Foot(VGroup):
    """
    Production-grade articulated foot.

    Responsibilities:
    - walk contact realism
    - planted/lifted state
    - foot rotation
    - future foot roll
    - ankle connection
    """

    def __init__(
        self,
        config: FootConfig | None = None,
        side: str = "left",
        name: str = "foot",
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.config = config or FootConfig()

        self.side = side
        self.foot_name = name

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

        self.current_rotation = 0.0

        self.is_planted = True

        self.contact_weight = 1.0

        self.debug_enabled = False

        # -------------------------------------------------
        # BUILD
        # -------------------------------------------------

        self._build_foot()
        self._register_anchors()
        self._build_debug()

        self._update_debug_visibility()

    # =====================================================
    # BUILD FOOT
    # =====================================================

    def _build_foot(self):
        """
        Main foot geometry.
        """

        # -------------------------------------------------
        # MAIN FOOT
        # -------------------------------------------------

        self.foot_body = RoundedRectangle(
            width=self.config.width,
            height=self.config.height,
            corner_radius=self.config.corner_radius,
            stroke_width=self.config.stroke_width,
            fill_color=self.config.foot_color,
            fill_opacity=1.0,
        )

        # -------------------------------------------------
        # SOLE
        # -------------------------------------------------

        self.sole = RoundedRectangle(
            width=self.config.width * 0.92,
            height=self.config.height * 0.28,
            corner_radius=self.config.corner_radius,
            stroke_width=0,
            fill_color=self.config.sole_color,
            fill_opacity=0.85,
        )

        self.sole.move_to(
            vec3(
                0.0,
                -self.config.height * 0.28,
                0.0,
            )
        )

        self.add(
            self.foot_body,
            self.sole,
        )

    # =====================================================
    # ANCHORS
    # =====================================================

    def _register_anchors(self):
        """
        Register important foot anchors.
        """

        half_width = self.config.width / 2.0
        half_height = self.config.height / 2.0

        # -------------------------------------------------
        # ROOT / ANKLE
        # -------------------------------------------------

        self.ankle_anchor = vec3(
            0.0,
            half_height,
            0.0,
        )

        # -------------------------------------------------
        # CENTER
        # -------------------------------------------------

        self.center_anchor = vec3()

        # -------------------------------------------------
        # HEEL
        # -------------------------------------------------

        self.heel_anchor = vec3(
            -half_width + self.config.heel_offset,
            -half_height,
            0.0,
        )

        # -------------------------------------------------
        # TOE
        # -------------------------------------------------

        self.toe_anchor = vec3(
            half_width - self.config.toe_offset,
            -half_height,
            0.0,
        )

        # -------------------------------------------------
        # GROUND CONTACT
        # -------------------------------------------------

        self.contact_anchor = vec3(
            0.0,
            -half_height,
            0.0,
        )

        # -------------------------------------------------
        # TRANSFORM NODE
        # -------------------------------------------------

        self.transform_node.set_center_point(
            self.center_anchor
        )

        self.transform_node.set_root_pivot(
            self.ankle_anchor
        )

    # =====================================================
    # DEBUG BUILD
    # =====================================================

    def _build_debug(self):
        """
        Build debug overlays.
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
        # ANKLE DOT
        # -------------------------------------------------

        self.ankle_dot = Dot(
            point=self.ankle_anchor,
            radius=0.03,
            color=GREEN,
        )

        # -------------------------------------------------
        # HEEL DOT
        # -------------------------------------------------

        self.heel_dot = Dot(
            point=self.heel_anchor,
            radius=0.025,
            color=YELLOW,
        )

        # -------------------------------------------------
        # TOE DOT
        # -------------------------------------------------

        self.toe_dot = Dot(
            point=self.toe_anchor,
            radius=0.025,
            color=RED,
        )

        # -------------------------------------------------
        # CONTACT ARC
        # -------------------------------------------------

        self.contact_arc = Arc(
            radius=self.config.contact_arc_radius,
            start_angle=-PI / 2,
            angle=0.001,
            color=WHITE,
            stroke_width=2,
        )

        # -------------------------------------------------
        # CONTACT VECTOR
        # -------------------------------------------------

        self.contact_line = Line(
            vec3(),
            vec3(0.0, -0.5, 0.0),
            color=WHITE,
            stroke_width=2,
        )

        # -------------------------------------------------
        # ROTATION LABEL
        # -------------------------------------------------

        self.rotation_text = (
            Text(
                "0°",
                font_size=18,
            )
            .scale(0.35)
            .move_to(
                vec3(
                    0.0,
                    0.45,
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
                color=GREEN,
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
            self.ankle_dot,
            self.heel_dot,
            self.toe_dot,
            self.contact_arc,
            self.contact_line,
            self.rotation_text,
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
    # FOOT ROTATION
    # =====================================================

    def set_rotation(
        self,
        angle: float,
    ):
        """
        Set foot articulation angle.
        """

        self.current_rotation = angle

        self._update_visuals()

    def rotate_foot(
        self,
        delta_angle: float,
    ):
        """
        Incremental foot rotation.
        """

        self.current_rotation += delta_angle

        self._update_visuals()

    # =====================================================
    # CONTACT STATES
    # =====================================================

    def set_planted(self):
        """
        Foot fully planted.
        """

        self.is_planted = True

        self.contact_weight = 1.0

        self._update_state_visual()

    def set_lifted(self):
        """
        Foot lifted during walk cycle.
        """

        self.is_planted = False

        self.contact_weight = 0.0

        self._update_state_visual()

    def set_contact_weight(
        self,
        weight: float,
    ):
        """
        Procedural contact blending.
        """

        self.contact_weight = np.clip(
            weight,
            0.0,
            1.0,
        )

    # =====================================================
    # VISUAL UPDATE
    # =====================================================

    def _update_visuals(self):
        """
        Update debug visuals.
        """

        # -------------------------------------------------
        # CONTACT ARC
        # -------------------------------------------------

        new_arc = Arc(
            radius=self.config.contact_arc_radius,
            start_angle=-PI / 2,
            angle=self.current_rotation,
            color=WHITE,
            stroke_width=2,
        )

        self.contact_arc.become(new_arc)

        # -------------------------------------------------
        # CONTACT VECTOR
        # -------------------------------------------------

        direction = vec3(
            np.sin(self.current_rotation),
            -np.cos(self.current_rotation),
            0.0,
        )

        end = direction * 0.5

        new_line = Line(
            vec3(),
            end,
            color=WHITE,
            stroke_width=2,
        )

        self.contact_line.become(new_line)

        # -------------------------------------------------
        # ROTATION LABEL
        # -------------------------------------------------

        degrees = round(
            np.degrees(self.current_rotation),
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
                    0.45,
                    0.0,
                )
            )
        )

        self.rotation_text.become(new_text)

    # =====================================================
    # STATE VISUAL
    # =====================================================

    def _update_state_visual(self):
        """
        Update planted/lifted text.
        """

        label = (
            "PLANTED"
            if self.is_planted
            else "LIFTED"
        )

        color = (
            GREEN
            if self.is_planted
            else YELLOW
        )

        new_text = (
            Text(
                label,
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

        self.state_text.become(new_text)

    # =====================================================
    # ACCESSORS
    # =====================================================

    def get_transform_node(self) -> TransformNode:
        return self.transform_node

    # =====================================================
    # ANCHOR ACCESS
    # =====================================================

    def get_ankle_anchor(self):
        return np.array(self.ankle_anchor)

    def get_heel_anchor(self):
        return np.array(self.heel_anchor)

    def get_toe_anchor(self):
        return np.array(self.toe_anchor)

    def get_contact_anchor(self):
        return np.array(self.contact_anchor)

    def get_center_anchor(self):
        return np.array(self.center_anchor)

    # =====================================================
    # STATE ACCESS
    # =====================================================

    def get_rotation(self) -> float:
        return self.current_rotation

    def foot_is_planted(self) -> bool:
        return self.is_planted

    def get_contact_weight(self) -> float:
        return self.contact_weight

    # =====================================================
    # RESET
    # =====================================================

    def reset_foot(self):
        """
        Reset procedural foot state.
        """

        self.current_rotation = 0.0

        self.is_planted = True

        self.contact_weight = 1.0

        self._update_visuals()
        self._update_state_visual()

    # =====================================================
    # DEBUG PRINT
    # =====================================================

    def debug_print(self):
        print("========== FOOT DEBUG ==========")
        print("Name:", self.foot_name)
        print("Rotation:", self.current_rotation)
        print("Planted:", self.is_planted)
        print("Contact Weight:", self.contact_weight)
        print("================================")

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self):
        return (
            f"Foot("
            f"name='{self.foot_name}', "
            f"rotation={round(self.current_rotation, 3)}"
            f")"
        )


# =========================================================
# FACTORY HELPERS
# =========================================================

def build_left_foot(
    config: FootConfig | None = None,
) -> Foot:
    return Foot(
        config=config,
        side="left",
        name="left_foot",
    )


def build_right_foot(
    config: FootConfig | None = None,
) -> Foot:
    return Foot(
        config=config,
        side="right",
        name="right_foot",
    )


def build_debug_foot(
    config: FootConfig | None = None,
    side: str = "left",
) -> Foot:
    """
    Create debug-enabled foot.
    """

    foot = Foot(
        config=config,
        side=side,
        name=f"{side}_debug_foot",
    )

    foot.enable_debug()

    return foot