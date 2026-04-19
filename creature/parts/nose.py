"""
Nose construction for mathlab-mylinehub-creature.

This file builds the creature's nose as a small simple shape placed
using face anchors.

Version 1 goals:
- keep the nose minimal
- keep placement controlled by anchors
- keep styling controlled by config
- make later expression changes easy

This file only builds the nose object.
It does not animate the nose.
"""

from __future__ import annotations

from manimlib import RoundedRectangle

from config.colors import NOSE_FILL
from config.colors import NOSE_STROKE
from config.defaults import DEBUG_MODE
from config.defaults import LOG_CREATURE_BUILD
from config.defaults import NOSE_NAME
from config.sizes import NOSE_HEIGHT
from config.sizes import NOSE_STROKE_WIDTH
from config.sizes import NOSE_WIDTH

from core.anchors import get_nose_center
from core.logger import get_logger
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


# ============================================================
# Internal builder
# ============================================================

def _build_nose_shape(
    *,
    width: float = NOSE_WIDTH,
    height: float = NOSE_HEIGHT,
    stroke_width: float = NOSE_STROKE_WIDTH,
    fill_color: str = NOSE_FILL,
    stroke_color: str = NOSE_STROKE,
    corner_radius_ratio: float = 0.30,
) -> RoundedRectangle:
    """
    Build the base nose shape.

    Version 1 uses a tiny rounded rectangle so the nose stays:
    - readable
    - simple
    - slightly soft
    """
    width = _validate_positive("width", width)
    height = _validate_positive("height", height)
    stroke_width = _validate_non_negative("stroke_width", stroke_width)
    corner_radius_ratio = _validate_non_negative("corner_radius_ratio", corner_radius_ratio)

    corner_radius = min(width, height) * corner_radius_ratio

    nose = RoundedRectangle(
        width=width,
        height=height,
        corner_radius=corner_radius,
    )
    nose.set_fill(fill_color, opacity=1.0)
    nose.set_stroke(stroke_color, width=stroke_width)

    return nose


# ============================================================
# Public builder
# ============================================================

def build_nose(
    body_center=None,
    *,
    width: float = NOSE_WIDTH,
    height: float = NOSE_HEIGHT,
    stroke_width: float = NOSE_STROKE_WIDTH,
    fill_color: str = NOSE_FILL,
    stroke_color: str = NOSE_STROKE,
    corner_radius_ratio: float = 0.30,
    assign_name: bool = True,
) -> RoundedRectangle:
    """
    Build the creature nose and place it using anchor helpers.

    Args:
        body_center:
            Optional body center point. If omitted, origin-based anchors are used.

        width:
            Nose width.

        height:
            Nose height.

        stroke_width:
            Nose stroke width.

        fill_color:
            Nose fill color.

        stroke_color:
            Nose stroke color.

        corner_radius_ratio:
            Rounded-corner ratio relative to the smaller nose dimension.

        assign_name:
            If True, assign a stable object name.

    Returns:
        RoundedRectangle nose object.
    """
    if LOG_CREATURE_BUILD:
        logger.info(
            "Building nose | width=%.3f height=%.3f stroke_width=%.3f",
            width,
            height,
            stroke_width,
        )

    nose = _build_nose_shape(
        width=width,
        height=height,
        stroke_width=stroke_width,
        fill_color=fill_color,
        stroke_color=stroke_color,
        corner_radius_ratio=corner_radius_ratio,
    )

    nose_center = get_nose_center(body_center)
    nose.move_to(nose_center)

    if assign_name:
        nose.name = creature_part_name(NOSE_NAME)

    # Lightweight metadata for later expression / rig work
    nose.nose_center = nose_center
    nose.nose_width = width
    nose.nose_height = height
    nose.nose_stroke_width = stroke_width
    nose.nose_corner_radius_ratio = corner_radius_ratio

    if DEBUG_MODE:
        logger.debug(
            "Nose placed | center=%s width=%.3f height=%.3f",
            nose_center,
            width,
            height,
        )

    if LOG_CREATURE_BUILD:
        logger.info("Nose created successfully")

    return nose