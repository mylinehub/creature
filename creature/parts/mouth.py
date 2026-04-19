"""
Mouth construction for mathlab-mylinehub-creature.

This file builds the creature's mouth as a simple expressive curve
positioned using face anchors.

Version 1 goals:
- keep the mouth clean and readable
- support a neutral-friendly slight smile look
- keep all sizing controlled by config
- make future expression replacement easy

This file only builds the mouth object.
It does not animate expressions yet.
"""

from __future__ import annotations

from manimlib import Arc

from config.colors import MOUTH_COLOR
from config.defaults import DEBUG_MODE
from config.defaults import LOG_CREATURE_BUILD
from config.defaults import MOUTH_NAME
from config.sizes import MOUTH_HEIGHT
from config.sizes import MOUTH_STROKE_WIDTH
from config.sizes import MOUTH_WIDTH
from config.sizes import SMILE_ARC_ANGLE

from core.anchors import get_mouth_center
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

def _build_mouth_shape(
    *,
    width: float = MOUTH_WIDTH,
    height: float = MOUTH_HEIGHT,
    stroke_width: float = MOUTH_STROKE_WIDTH,
    stroke_color: str = MOUTH_COLOR,
    arc_angle: float = SMILE_ARC_ANGLE,
) -> Arc:
    """
    Build the base mouth shape.

    Version 1 uses a small upward arc so the mascot feels friendly
    even in its neutral default state.
    """
    width = _validate_positive("width", width)
    height = _validate_positive("height", height)
    stroke_width = _validate_non_negative("stroke_width", stroke_width)
    arc_angle = _validate_positive("arc_angle", arc_angle)

    mouth = Arc(
        angle=arc_angle,
    )
    mouth.set_width(width)
    mouth.set_height(height)
    mouth.set_stroke(stroke_color, width=stroke_width)

    return mouth


# ============================================================
# Public builder
# ============================================================

def build_mouth(
    body_center=None,
    *,
    width: float = MOUTH_WIDTH,
    height: float = MOUTH_HEIGHT,
    stroke_width: float = MOUTH_STROKE_WIDTH,
    stroke_color: str = MOUTH_COLOR,
    arc_angle: float = SMILE_ARC_ANGLE,
    assign_name: bool = True,
) -> Arc:
    """
    Build the creature mouth and place it using anchor helpers.

    Args:
        body_center:
            Optional body center point. If omitted, origin-based anchors are used.

        width:
            Mouth width.

        height:
            Mouth height.

        stroke_width:
            Mouth stroke width.

        stroke_color:
            Mouth stroke color.

        arc_angle:
            Arc angle controlling smile curvature.

        assign_name:
            If True, assign a stable object name.

    Returns:
        Arc mouth object.
    """
    if LOG_CREATURE_BUILD:
        logger.info(
            "Building mouth | width=%.3f height=%.3f stroke_width=%.3f arc_angle=%.3f",
            width,
            height,
            stroke_width,
            arc_angle,
        )

    mouth = _build_mouth_shape(
        width=width,
        height=height,
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        arc_angle=arc_angle,
    )

    mouth_center = get_mouth_center(body_center)
    mouth.move_to(mouth_center)

    if assign_name:
        mouth.name = creature_part_name(MOUTH_NAME)

    # Lightweight metadata for later expression / rig work
    mouth.mouth_center = mouth_center
    mouth.mouth_width = width
    mouth.mouth_height = height
    mouth.mouth_stroke_width = stroke_width
    mouth.mouth_arc_angle = arc_angle

    if DEBUG_MODE:
        logger.debug(
            "Mouth placed | center=%s width=%.3f height=%.3f arc_angle=%.3f",
            mouth_center,
            width,
            height,
            arc_angle,
        )

    if LOG_CREATURE_BUILD:
        logger.info("Mouth created successfully")

    return mouth