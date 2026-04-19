"""
Foot construction for mathlab-mylinehub-creature.

This file builds the creature's feet as small rounded horizontal shapes
attached to the ends of the leg lines.

Version 1 goals:
- keep feet simple and readable
- attach feet cleanly to leg ends
- support a stable standing silhouette
- keep styling controlled by config

This file only builds foot geometry.
Detailed shoe-like styling is intentionally not added yet.
"""

from __future__ import annotations

import numpy as np
from manimlib import RoundedRectangle, VGroup

from config.colors import CREATURE_FOOT_COLOR
from config.defaults import DEBUG_MODE
from config.defaults import LEFT_FOOT_NAME
from config.defaults import LOG_CREATURE_BUILD
from config.defaults import RIGHT_FOOT_NAME
from config.sizes import FOOT_HEIGHT
from config.sizes import FOOT_WIDTH

from creature.parts.legs import build_left_leg
from creature.parts.legs import build_right_leg

from core.geometry import point
from core.logger import get_logger
from core.naming import creature_pair_part_names
from core.naming import creature_part_name

logger = get_logger(__name__)


# ============================================================
# Internal helpers
# ============================================================

def _validate_numeric(name: str, value: float | int) -> float:
    """
    Ensure a numeric value and return it as float.
    """
    if not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be numeric, got {type(value).__name__}")
    return float(value)


def _validate_positive(name: str, value: float | int) -> float:
    """
    Ensure a positive numeric value.
    """
    value = _validate_numeric(name, value)
    if value <= 0:
        raise ValueError(f"{name} must be > 0, got {value}")
    return value


def _validate_non_negative(name: str, value: float | int) -> float:
    """
    Ensure a non-negative numeric value.
    """
    value = _validate_numeric(name, value)
    if value < 0:
        raise ValueError(f"{name} must be >= 0, got {value}")
    return value


def _coerce_point3(value, name: str = "value") -> np.ndarray:
    """
    Normalize a point-like input into a clean 3D numpy point.
    """
    if isinstance(value, np.ndarray):
        if value.shape != (3,):
            raise ValueError(f"{name} must have shape (3,), got {value.shape}")
        return value.astype(float)

    if isinstance(value, (tuple, list)):
        if len(value) != 3:
            raise ValueError(f"{name} must contain exactly 3 values, got {len(value)}")
        return point(value[0], value[1], value[2])

    raise TypeError(f"{name} must be a numpy.ndarray or 3-item tuple/list")


# ============================================================
# Internal builder
# ============================================================

def _build_foot_shape(
    *,
    width: float = FOOT_WIDTH,
    height: float = FOOT_HEIGHT,
    fill_color: str = CREATURE_FOOT_COLOR,
    stroke_color: str = CREATURE_FOOT_COLOR,
    stroke_width: float = 0.0,
    corner_radius_ratio: float = 0.45,
) -> RoundedRectangle:
    """
    Build a simple foot shape.

    Version 1 uses a small rounded rectangle so the foot is:
    - easy to see
    - stable-looking
    - easy to replace later
    """
    width = _validate_positive("width", width)
    height = _validate_positive("height", height)
    stroke_width = _validate_non_negative("stroke_width", stroke_width)
    corner_radius_ratio = _validate_non_negative("corner_radius_ratio", corner_radius_ratio)

    foot = RoundedRectangle(
        width=width,
        height=height,
        corner_radius=height * corner_radius_ratio,
    )
    foot.set_fill(fill_color, opacity=1.0)
    foot.set_stroke(stroke_color, width=stroke_width)
    return foot


def _build_single_foot(
    end_point,
    *,
    foot_name: str = "foot",
    width: float = FOOT_WIDTH,
    height: float = FOOT_HEIGHT,
    fill_color: str = CREATURE_FOOT_COLOR,
    stroke_color: str = CREATURE_FOOT_COLOR,
    stroke_width: float = 0.0,
    corner_radius_ratio: float = 0.45,
) -> RoundedRectangle:
    """
    Build a single foot positioned at a supplied leg-end point.
    """
    end_point = _coerce_point3(end_point, "end_point")

    foot = _build_foot_shape(
        width=width,
        height=height,
        fill_color=fill_color,
        stroke_color=stroke_color,
        stroke_width=stroke_width,
        corner_radius_ratio=corner_radius_ratio,
    )
    foot.move_to(end_point)
    foot.name = foot_name

    # Lightweight metadata for later standing / walk logic
    foot.foot_center = end_point
    foot.foot_width = width
    foot.foot_height = height

    if DEBUG_MODE:
        logger.debug(
            "Built foot | name=%s center=%s width=%.3f height=%.3f",
            foot_name,
            end_point,
            width,
            height,
        )

    return foot


# ============================================================
# Public builders
# ============================================================

def build_left_foot(
    body_center=None,
    *,
    leg=None,
    leg_direction: str = "down",
    width: float = FOOT_WIDTH,
    height: float = FOOT_HEIGHT,
    fill_color: str = CREATURE_FOOT_COLOR,
    stroke_color: str = CREATURE_FOOT_COLOR,
    stroke_width: float = 0.0,
    corner_radius_ratio: float = 0.45,
) -> RoundedRectangle:
    """
    Build left foot at the end of the left leg.

    Parameters:
        body_center:
            Optional body center used if a leg is built internally.

        leg:
            Optional prebuilt left leg. If provided, its end point is used.

        leg_direction:
            Direction used only when leg is not provided.

        width:
            Foot width.

        height:
            Foot height.

        fill_color:
            Foot fill color.

        stroke_color:
            Foot stroke color.

        stroke_width:
            Foot stroke width.

        corner_radius_ratio:
            Rounded-corner ratio relative to foot height.
    """
    if LOG_CREATURE_BUILD:
        logger.info("Building left foot")

    if leg is None:
        leg = build_left_leg(
            body_center=body_center,
            direction=leg_direction,
        )

    left_foot = _build_single_foot(
        leg.get_end(),
        foot_name=creature_part_name(LEFT_FOOT_NAME),
        width=width,
        height=height,
        fill_color=fill_color,
        stroke_color=stroke_color,
        stroke_width=stroke_width,
        corner_radius_ratio=corner_radius_ratio,
    )

    # Relationship metadata
    left_foot.source_leg = leg

    if LOG_CREATURE_BUILD:
        logger.info("Left foot created successfully")

    return left_foot


def build_right_foot(
    body_center=None,
    *,
    leg=None,
    leg_direction: str = "down",
    width: float = FOOT_WIDTH,
    height: float = FOOT_HEIGHT,
    fill_color: str = CREATURE_FOOT_COLOR,
    stroke_color: str = CREATURE_FOOT_COLOR,
    stroke_width: float = 0.0,
    corner_radius_ratio: float = 0.45,
) -> RoundedRectangle:
    """
    Build right foot at the end of the right leg.

    Parameters:
        body_center:
            Optional body center used if a leg is built internally.

        leg:
            Optional prebuilt right leg. If provided, its end point is used.

        leg_direction:
            Direction used only when leg is not provided.

        width:
            Foot width.

        height:
            Foot height.

        fill_color:
            Foot fill color.

        stroke_color:
            Foot stroke color.

        stroke_width:
            Foot stroke width.

        corner_radius_ratio:
            Rounded-corner ratio relative to foot height.
    """
    if LOG_CREATURE_BUILD:
        logger.info("Building right foot")

    if leg is None:
        leg = build_right_leg(
            body_center=body_center,
            direction=leg_direction,
        )

    right_foot = _build_single_foot(
        leg.get_end(),
        foot_name=creature_part_name(RIGHT_FOOT_NAME),
        width=width,
        height=height,
        fill_color=fill_color,
        stroke_color=stroke_color,
        stroke_width=stroke_width,
        corner_radius_ratio=corner_radius_ratio,
    )

    # Relationship metadata
    right_foot.source_leg = leg

    if LOG_CREATURE_BUILD:
        logger.info("Right foot created successfully")

    return right_foot


def build_feet(
    body_center=None,
    *,
    left_leg=None,
    right_leg=None,
    left_leg_direction: str = "down",
    right_leg_direction: str = "down",
    width: float = FOOT_WIDTH,
    height: float = FOOT_HEIGHT,
    fill_color: str = CREATURE_FOOT_COLOR,
    stroke_color: str = CREATURE_FOOT_COLOR,
    stroke_width: float = 0.0,
    corner_radius_ratio: float = 0.45,
    assign_group_name: bool = True,
) -> VGroup:
    """
    Build both feet together.

    Parameters:
        body_center:
            Optional body center used if legs are built internally.

        left_leg:
            Optional prebuilt left leg.

        right_leg:
            Optional prebuilt right leg.

        left_leg_direction:
            Direction used only when left_leg is not provided.

        right_leg_direction:
            Direction used only when right_leg is not provided.

        width:
            Shared foot width.

        height:
            Shared foot height.

        fill_color:
            Shared foot fill color.

        stroke_color:
            Shared foot stroke color.

        stroke_width:
            Shared foot stroke width.

        corner_radius_ratio:
            Shared rounded-corner ratio.

        assign_group_name:
            If True, assign a stable name to the feet group.

    Returns:
        VGroup(left_foot, right_foot)
    """
    if LOG_CREATURE_BUILD:
        logger.info("Building both feet")

    left_foot = build_left_foot(
        body_center=body_center,
        leg=left_leg,
        leg_direction=left_leg_direction,
        width=width,
        height=height,
        fill_color=fill_color,
        stroke_color=stroke_color,
        stroke_width=stroke_width,
        corner_radius_ratio=corner_radius_ratio,
    )

    right_foot = build_right_foot(
        body_center=body_center,
        leg=right_leg,
        leg_direction=right_leg_direction,
        width=width,
        height=height,
        fill_color=fill_color,
        stroke_color=stroke_color,
        stroke_width=stroke_width,
        corner_radius_ratio=corner_radius_ratio,
    )

    feet = VGroup(left_foot, right_foot)

    if assign_group_name:
        left_name, right_name = creature_pair_part_names("foot")
        feet.name = "creature_feet"
        feet.left_foot_name = left_name
        feet.right_foot_name = right_name

    # Lightweight metadata for later standing / walk logic
    feet.left_foot = left_foot
    feet.right_foot = right_foot
    feet.body_center = body_center
    feet.foot_width = width
    feet.foot_height = height

    if LOG_CREATURE_BUILD:
        logger.info("Feet created successfully")

    return feet