"""
Pointer stick for mathlab-mylinehub-creature.

This file builds a simple pointer stick that the creature can hold
in teaching / pointing scenes.

Version 1 goals:
- clean straight stick
- small rounded tip
- easy to position in hand
- lightweight (no heavy styling yet)

This file only builds the prop.
It does NOT attach it to the creature automatically.
"""

from __future__ import annotations

from manimlib import Circle, Line, VGroup

from config.colors import POINTER_STICK_COLOR
from config.defaults import DEBUG_MODE
from config.defaults import LOG_CREATURE_BUILD
from config.sizes import POINTER_STICK_LENGTH
from config.sizes import POINTER_STICK_STROKE_WIDTH

from core.geometry import point
from core.logger import get_logger

logger = get_logger(__name__)


# ============================================================
# Internal constants
# ============================================================

# Local default until/unless a dedicated POINTER_TIP_RADIUS is added
# to config.sizes. This keeps the file wired correctly right now.
DEFAULT_POINTER_TIP_RADIUS = 0.055


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


# ============================================================
# Internal builders
# ============================================================

def _build_pointer_body(
    *,
    length: float = POINTER_STICK_LENGTH,
    stroke_width: float = POINTER_STICK_STROKE_WIDTH,
    stroke_color: str = POINTER_STICK_COLOR,
) -> Line:
    """
    Build the main stick line.

    Version 1 builds the stick along the +X axis from origin.
    This makes later rotation/positioning easy.
    """
    length = _validate_positive("length", length)
    stroke_width = _validate_positive("stroke_width", stroke_width)

    start = point(0.0, 0.0, 0.0)
    end = point(length, 0.0, 0.0)

    stick = Line(start, end)
    stick.set_stroke(stroke_color, width=stroke_width)

    # Lightweight metadata
    stick.pointer_start = start
    stick.pointer_end = end
    stick.pointer_length = length
    stick.pointer_stroke_width = stroke_width

    return stick


def _build_pointer_tip(
    end_point,
    *,
    radius: float = DEFAULT_POINTER_TIP_RADIUS,
    fill_color: str = POINTER_STICK_COLOR,
    stroke_color: str = POINTER_STICK_COLOR,
    stroke_width: float = 0.0,
) -> Circle:
    """
    Build a small circular tip at the end of the stick.
    """
    radius = _validate_positive("radius", radius)
    stroke_width = _validate_numeric("stroke_width", stroke_width)

    tip = Circle(radius=radius)
    tip.set_fill(fill_color, opacity=1.0)
    tip.set_stroke(stroke_color, width=stroke_width)
    tip.move_to(end_point)

    # Lightweight metadata
    tip.pointer_tip_center = end_point
    tip.pointer_tip_radius = radius

    return tip


# ============================================================
# Public builder
# ============================================================

def build_pointer_stick(
    *,
    length: float = POINTER_STICK_LENGTH,
    stroke_width: float = POINTER_STICK_STROKE_WIDTH,
    color: str = POINTER_STICK_COLOR,
    tip_radius: float = DEFAULT_POINTER_TIP_RADIUS,
    assign_name: bool = True,
) -> VGroup:
    """
    Build the full pointer stick.

    Parameters:
        length:
            Pointer stick length.

        stroke_width:
            Pointer line stroke width.

        color:
            Shared pointer color.

        tip_radius:
            Radius of the rounded tip.

        assign_name:
            If True, assign stable names to the group and subparts.

    Returns:
        VGroup(stick_line, tip_circle)
    """
    length = _validate_positive("length", length)
    stroke_width = _validate_positive("stroke_width", stroke_width)
    tip_radius = _validate_positive("tip_radius", tip_radius)

    if LOG_CREATURE_BUILD:
        logger.info(
            "Building pointer stick | length=%.3f stroke_width=%.3f tip_radius=%.3f",
            length,
            stroke_width,
            tip_radius,
        )

    stick = _build_pointer_body(
        length=length,
        stroke_width=stroke_width,
        stroke_color=color,
    )

    tip = _build_pointer_tip(
        stick.get_end(),
        radius=tip_radius,
        fill_color=color,
        stroke_color=color,
        stroke_width=0.0,
    )

    pointer = VGroup(stick, tip)

    if assign_name:
        pointer.name = "pointer_stick"
        stick.name = "pointer_stick_body"
        tip.name = "pointer_stick_tip"

    # Lightweight metadata for later hand-attachment / teaching scenes
    pointer.stick = stick
    pointer.tip = tip
    pointer.pointer_length = length
    pointer.pointer_tip_radius = tip_radius

    if DEBUG_MODE:
        logger.debug(
            "Pointer stick built | start=%s end=%s",
            stick.get_start(),
            stick.get_end(),
        )

    if LOG_CREATURE_BUILD:
        logger.info("Pointer stick created successfully")

    return pointer