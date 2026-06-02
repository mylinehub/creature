"""
Foot construction for mathlab-mylinehub-creature.

This file builds simple articulated feet for the connected creature system.

Architecture rule:
- feet are visual parts only
- feet do not build legs
- feet attach to ankle points supplied by legs.py
- feet should never move independently in scene code
- foot state is local: planted, lifted, rotation, contact weight
- audio is not handled here; audio may be triggered later by walk/step actions

Feet are intentionally simple in this version.
More advanced foot roll / IK behavior can be added later through legs.py,
leg_rig.py, and walk_action.py.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
from typing import Optional

import numpy as np

from manimlib import Arc
from manimlib import Dot
from manimlib import Line
from manimlib import RoundedRectangle
from manimlib import Text
from manimlib import VGroup

from manimlib.constants import BLUE
from manimlib.constants import BLUE_E
from manimlib.constants import GREEN
from manimlib.constants import GREY_B
from manimlib.constants import RED
from manimlib.constants import WHITE
from manimlib.constants import YELLOW

from mathlab_creature.config.defaults import DEBUG_MODE
from mathlab_creature.config.defaults import LEFT_FOOT_NAME
from mathlab_creature.config.defaults import LOG_CREATURE_BUILD
from mathlab_creature.config.defaults import RIGHT_FOOT_NAME
from mathlab_creature.config.sizes import FOOT_HEIGHT
from mathlab_creature.config.sizes import FOOT_WIDTH
from mathlab_creature.config.sizes import GUIDE_STROKE_WIDTH

from mathlab_creature.core.debug_draw import create_local_axes
from mathlab_creature.core.geometry import as_vec3
from mathlab_creature.core.geometry import clamp01
from mathlab_creature.core.geometry import point
from mathlab_creature.core.geometry import zero_point
from mathlab_creature.core.logger import get_logger
from mathlab_creature.core.naming import creature_pair_part_names
from mathlab_creature.core.naming import creature_part_name
from mathlab_creature.core.transforms import TransformNode
from mathlab_creature.core.transforms import create_transform_node


logger = get_logger(__name__)


# ============================================================
# Type aliases
# ============================================================

Vector3 = np.ndarray
Vec3Like = np.ndarray | Iterable[float]


# ============================================================
# Configuration
# ============================================================

@dataclass
class FootConfig:
    """
    Tunable foot proportions.
    """

    width: float = FOOT_WIDTH
    height: float = FOOT_HEIGHT

    corner_radius: float = 0.05

    foot_color: str = BLUE_E
    sole_color: str = GREY_B

    stroke_width: float = 0.0

    debug_axis_length: float = 0.35
    contact_arc_radius: float = 0.20

    heel_offset: float = 0.08
    toe_offset: float = 0.08


# ============================================================
# Internal helpers
# ============================================================

def _validate_numeric(
    name: str,
    value: float | int,
) -> float:
    """
    Ensure a numeric value and return it as float.
    """
    if not isinstance(value, (int, float)):
        raise TypeError(
            f"{name} must be numeric, got {type(value).__name__}"
        )

    return float(value)


def _validate_positive(
    name: str,
    value: float | int,
) -> float:
    """
    Ensure a strictly positive numeric value.
    """
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
    """
    Ensure a non-negative numeric value.
    """
    value = _validate_numeric(
        name,
        value,
    )

    if value < 0:
        raise ValueError(
            f"{name} must be >= 0, got {value}"
        )

    return value


def _coerce_point3(
    value: Optional[Vec3Like],
    name: str = "value",
) -> Vector3:
    """
    Normalize a point-like input into a clean 3D numpy point.

    None becomes origin.
    """
    if value is None:
        return zero_point()

    return as_vec3(
        value,
        name=name,
    )


def _validate_side(
    side: str,
) -> str:
    """
    Validate side string.
    """
    if not isinstance(side, str):
        raise TypeError(
            f"side must be str, got {type(side).__name__}"
        )

    side = side.strip().lower()

    if side not in {"left", "right", "center"}:
        raise ValueError(
            "side must be 'left', 'right', or 'center'"
        )

    return side


def _validated_config(
    config: Optional[FootConfig],
) -> FootConfig:
    """
    Return validated foot config.
    """
    config = config or FootConfig()

    config.width = _validate_positive(
        "config.width",
        config.width,
    )
    config.height = _validate_positive(
        "config.height",
        config.height,
    )
    config.corner_radius = _validate_non_negative(
        "config.corner_radius",
        config.corner_radius,
    )
    config.stroke_width = _validate_non_negative(
        "config.stroke_width",
        config.stroke_width,
    )
    config.debug_axis_length = _validate_non_negative(
        "config.debug_axis_length",
        config.debug_axis_length,
    )
    config.contact_arc_radius = _validate_non_negative(
        "config.contact_arc_radius",
        config.contact_arc_radius,
    )
    config.heel_offset = _validate_non_negative(
        "config.heel_offset",
        config.heel_offset,
    )
    config.toe_offset = _validate_non_negative(
        "config.toe_offset",
        config.toe_offset,
    )

    return config


# ============================================================
# Foot object
# ============================================================

class Foot(VGroup):
    """
    Local foot visual object.

    Responsibilities:
    - foot shape
    - ankle / heel / toe / contact anchors
    - planted/lifted state
    - local foot rotation state
    - optional debug overlay

    This class does not build legs.
    legs.py owns leg chains and attaches feet to ankles.
    """

    def __init__(
        self,
        config: Optional[FootConfig] = None,
        side: str = "left",
        name: str = "foot",
        position: Optional[Vec3Like] = None,
        debug_enabled: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.config = _validated_config(config)
        self.side = _validate_side(side)
        self.foot_name = str(name)

        self.current_rotation = 0.0
        self.is_planted = True
        self.contact_weight = 1.0
        self.debug_enabled = bool(debug_enabled)

        self.transform_node = create_transform_node(
            name=self.foot_name,
            mobject=self,
        )

        self._build_foot()
        self._register_anchors()
        self._build_debug()
        self._update_debug_visibility()

        if position is not None:
            self.move_to(
                _coerce_point3(
                    position,
                    "position",
                )
            )

        self.name = self.foot_name
        self.is_creature_foot = True

    # ========================================================
    # Build
    # ========================================================

    def _build_foot(self) -> None:
        """
        Build main foot geometry.
        """
        self.foot_body = RoundedRectangle(
            width=self.config.width,
            height=self.config.height,
            corner_radius=self.config.corner_radius,
            stroke_width=self.config.stroke_width,
            fill_color=self.config.foot_color,
            fill_opacity=1.0,
        )

        self.sole = RoundedRectangle(
            width=self.config.width * 0.92,
            height=self.config.height * 0.28,
            corner_radius=min(
                self.config.corner_radius,
                self.config.height * 0.14,
            ),
            stroke_width=0,
            fill_color=self.config.sole_color,
            fill_opacity=0.85,
        )

        self.sole.move_to(
            point(
                0.0,
                -self.config.height * 0.28,
                0.0,
            )
        )

        self.add(
            self.foot_body,
            self.sole,
        )

    # ========================================================
    # Anchors
    # ========================================================

    def _register_anchors(self) -> None:
        """
        Register important foot anchors in local foot space.
        """
        half_width = self.config.width / 2.0
        half_height = self.config.height / 2.0

        self.ankle_anchor = point(
            0.0,
            half_height,
            0.0,
        )

        self.center_anchor = zero_point()

        self.heel_anchor = point(
            -half_width + self.config.heel_offset,
            -half_height,
            0.0,
        )

        self.toe_anchor = point(
            half_width - self.config.toe_offset,
            -half_height,
            0.0,
        )

        self.contact_anchor = point(
            0.0,
            -half_height,
            0.0,
        )

        self.transform_node.set_center_point(
            self.center_anchor,
        )
        self.transform_node.set_root_pivot(
            self.ankle_anchor,
        )

        self.foot_anchor = self.ankle_anchor
        self.end_point = self.contact_anchor

    # ========================================================
    # Debug
    # ========================================================

    def _build_debug(self) -> None:
        """
        Build debug overlays.
        """
        self.debug_group = VGroup()

        self.axes_debug = create_local_axes(
            origin=zero_point(),
            axis_length=self.config.debug_axis_length,
        )

        self.ankle_dot = Dot(
            point=self.ankle_anchor,
            radius=0.03,
            color=GREEN,
        )

        self.heel_dot = Dot(
            point=self.heel_anchor,
            radius=0.025,
            color=YELLOW,
        )

        self.toe_dot = Dot(
            point=self.toe_anchor,
            radius=0.025,
            color=RED,
        )

        self.contact_arc = Arc(
            radius=self.config.contact_arc_radius,
            start_angle=-np.pi / 2.0,
            angle=0.001,
            color=WHITE,
            stroke_width=GUIDE_STROKE_WIDTH,
        )

        self.contact_line = Line(
            zero_point(),
            point(
                0.0,
                -0.5,
                0.0,
            ),
            color=WHITE,
            stroke_width=GUIDE_STROKE_WIDTH,
        )

        self.rotation_text = (
            Text(
                "0°",
                font_size=18,
            )
            .scale(0.35)
            .move_to(
                point(
                    0.0,
                    0.45,
                    0.0,
                )
            )
        )

        self.state_text = (
            Text(
                "PLANTED",
                font_size=18,
                color=GREEN,
            )
            .scale(0.35)
            .move_to(
                point(
                    0.0,
                    -0.45,
                    0.0,
                )
            )
        )

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

        self.add(
            self.debug_group,
        )

    def _update_debug_visibility(self) -> None:
        """
        Update debug overlay visibility.
        """
        opacity = 1.0 if self.debug_enabled else 0.0

        self.debug_group.set_opacity(
            opacity,
        )

    def enable_debug(self) -> None:
        """
        Show debug overlays.
        """
        self.debug_enabled = True
        self._update_debug_visibility()

    def disable_debug(self) -> None:
        """
        Hide debug overlays.
        """
        self.debug_enabled = False
        self._update_debug_visibility()

    def toggle_debug(self) -> None:
        """
        Toggle debug overlays.
        """
        self.debug_enabled = not self.debug_enabled
        self._update_debug_visibility()

    # ========================================================
    # Foot rotation / contact state
    # ========================================================

    def set_rotation(
        self,
        angle: float,
    ) -> None:
        """
        Set local foot articulation angle.

        This stores state and updates debug visuals only.
        The final leg/ankle transform should be controlled by legs.py/leg_rig.py.
        """
        self.current_rotation = _validate_numeric(
            "angle",
            angle,
        )

        self._update_visuals()

    def rotate_foot(
        self,
        delta_angle: float,
    ) -> None:
        """
        Increment local foot rotation state.
        """
        self.current_rotation += _validate_numeric(
            "delta_angle",
            delta_angle,
        )

        self._update_visuals()

    def set_planted(self) -> None:
        """
        Mark foot as fully planted.
        """
        self.is_planted = True
        self.contact_weight = 1.0

        self._update_state_visual()

    def set_lifted(self) -> None:
        """
        Mark foot as lifted during walk cycle.
        """
        self.is_planted = False
        self.contact_weight = 0.0

        self._update_state_visual()

    def set_contact_weight(
        self,
        weight: float,
    ) -> None:
        """
        Set procedural contact blending weight.
        """
        self.contact_weight = clamp01(
            _validate_numeric(
                "weight",
                weight,
            )
        )

    # ========================================================
    # Visual updates
    # ========================================================

    def _update_visuals(self) -> None:
        """
        Update debug visuals.
        """
        new_arc = Arc(
            radius=self.config.contact_arc_radius,
            start_angle=-np.pi / 2.0,
            angle=self.current_rotation,
            color=WHITE,
            stroke_width=GUIDE_STROKE_WIDTH,
        )

        self.contact_arc.become(
            new_arc,
        )

        direction = point(
            np.sin(self.current_rotation),
            -np.cos(self.current_rotation),
            0.0,
        )

        end = direction * 0.5

        new_line = Line(
            zero_point(),
            end,
            color=WHITE,
            stroke_width=GUIDE_STROKE_WIDTH,
        )

        self.contact_line.become(
            new_line,
        )

        degrees_value = round(
            float(np.degrees(self.current_rotation)),
            1,
        )

        new_text = (
            Text(
                f"{degrees_value}°",
                font_size=18,
            )
            .scale(0.35)
            .move_to(
                point(
                    0.0,
                    0.45,
                    0.0,
                )
            )
        )

        self.rotation_text.become(
            new_text,
        )

    def _update_state_visual(self) -> None:
        """
        Update planted/lifted text.
        """
        label = "PLANTED" if self.is_planted else "LIFTED"
        color = GREEN if self.is_planted else YELLOW

        new_text = (
            Text(
                label,
                font_size=18,
                color=color,
            )
            .scale(0.35)
            .move_to(
                point(
                    0.0,
                    -0.45,
                    0.0,
                )
            )
        )

        self.state_text.become(
            new_text,
        )

    # ========================================================
    # Transform access
    # ========================================================

    def get_transform_node(self) -> TransformNode:
        """
        Return transform node.
        """
        return self.transform_node

    # ========================================================
    # Anchor access
    # ========================================================

    def get_ankle_anchor(self) -> Vector3:
        return np.array(
            self.ankle_anchor,
            dtype=float,
        )

    def get_heel_anchor(self) -> Vector3:
        return np.array(
            self.heel_anchor,
            dtype=float,
        )

    def get_toe_anchor(self) -> Vector3:
        return np.array(
            self.toe_anchor,
            dtype=float,
        )

    def get_contact_anchor(self) -> Vector3:
        return np.array(
            self.contact_anchor,
            dtype=float,
        )

    def get_center_anchor(self) -> Vector3:
        return np.array(
            self.center_anchor,
            dtype=float,
        )

    def get_anchor_map(self) -> dict[str, Vector3]:
        """
        Return all important local foot anchors.
        """
        return {
            "ankle": self.get_ankle_anchor(),
            "heel": self.get_heel_anchor(),
            "toe": self.get_toe_anchor(),
            "contact": self.get_contact_anchor(),
            "center": self.get_center_anchor(),
        }

    # ========================================================
    # State access
    # ========================================================

    def get_rotation(self) -> float:
        return float(
            self.current_rotation,
        )

    def foot_is_planted(self) -> bool:
        return bool(
            self.is_planted,
        )

    def get_contact_weight(self) -> float:
        return float(
            self.contact_weight,
        )

    # ========================================================
    # Reset
    # ========================================================

    def reset_foot(self) -> None:
        """
        Reset procedural foot state.
        """
        self.current_rotation = 0.0
        self.is_planted = True
        self.contact_weight = 1.0

        self._update_visuals()
        self._update_state_visual()

    # ========================================================
    # Debug print
    # ========================================================

    def debug_print(self) -> None:
        """
        Print foot debug state.
        """
        print("========== FOOT DEBUG ==========")
        print("Name:", self.foot_name)
        print("Side:", self.side)
        print("Rotation:", self.current_rotation)
        print("Planted:", self.is_planted)
        print("Contact Weight:", self.contact_weight)
        print("Anchors:", self.get_anchor_map())
        print("================================")

    # ========================================================
    # Representation
    # ========================================================

    def __repr__(self) -> str:
        return (
            "Foot("
            f"name={self.foot_name!r}, "
            f"side={self.side!r}, "
            f"rotation={round(self.current_rotation, 3)}"
            ")"
        )


# ============================================================
# Factory helpers
# ============================================================

def build_foot(
    *,
    side: str = "center",
    name: str = "foot",
    position: Optional[Vec3Like] = None,
    config: Optional[FootConfig] = None,
    debug_enabled: Optional[bool] = None,
) -> Foot:
    """
    Build a generic foot.
    """
    if debug_enabled is None:
        debug_enabled = DEBUG_MODE

    if LOG_CREATURE_BUILD:
        logger.info(
            "Building foot | side=%s name=%s",
            side,
            name,
        )

    foot = Foot(
        config=config,
        side=side,
        name=name,
        position=position,
        debug_enabled=debug_enabled,
    )

    if LOG_CREATURE_BUILD:
        logger.info(
            "Foot created successfully | side=%s name=%s",
            side,
            name,
        )

    return foot


def build_left_foot(
    *,
    position: Optional[Vec3Like] = None,
    config: Optional[FootConfig] = None,
    debug_enabled: Optional[bool] = None,
) -> Foot:
    """
    Build left foot.
    """
    return build_foot(
        side="left",
        name=creature_part_name(LEFT_FOOT_NAME),
        position=position,
        config=config,
        debug_enabled=debug_enabled,
    )


def build_right_foot(
    *,
    position: Optional[Vec3Like] = None,
    config: Optional[FootConfig] = None,
    debug_enabled: Optional[bool] = None,
) -> Foot:
    """
    Build right foot.
    """
    return build_foot(
        side="right",
        name=creature_part_name(RIGHT_FOOT_NAME),
        position=position,
        config=config,
        debug_enabled=debug_enabled,
    )


def build_feet(
    *,
    left_position: Optional[Vec3Like] = None,
    right_position: Optional[Vec3Like] = None,
    config: Optional[FootConfig] = None,
    debug_enabled: Optional[bool] = None,
    assign_group_name: bool = True,
) -> VGroup:
    """
    Build both feet together.

    This function does not build legs.
    legs.py owns leg construction and attaches feet to ankles.
    """
    if LOG_CREATURE_BUILD:
        logger.info(
            "Building both feet"
        )

    left_foot = build_left_foot(
        position=left_position,
        config=config,
        debug_enabled=debug_enabled,
    )

    right_foot = build_right_foot(
        position=right_position,
        config=config,
        debug_enabled=debug_enabled,
    )

    feet = VGroup(
        left_foot,
        right_foot,
    )

    if assign_group_name:
        left_name, right_name = creature_pair_part_names(
            "foot",
        )
        feet.name = "creature_feet"
        feet.left_foot_name = left_name
        feet.right_foot_name = right_name

    feet.left_foot = left_foot
    feet.right_foot = right_foot
    feet.is_creature_feet_group = True

    if LOG_CREATURE_BUILD:
        logger.info(
            "Feet created successfully"
        )

    return feet


def build_debug_foot(
    *,
    side: str = "left",
    position: Optional[Vec3Like] = None,
    config: Optional[FootConfig] = None,
) -> Foot:
    """
    Create debug-enabled foot.
    """
    return build_foot(
        side=side,
        name=f"{side}_debug_foot",
        position=position,
        config=config,
        debug_enabled=True,
    )


# ============================================================
# Export control
# ============================================================

__all__ = [
    "Vector3",
    "Vec3Like",
    "FootConfig",
    "Foot",
    "build_foot",
    "build_left_foot",
    "build_right_foot",
    "build_feet",
    "build_debug_foot",
]