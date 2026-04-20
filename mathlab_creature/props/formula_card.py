"""
Formula card prop for mathlab-mylinehub-creature.

This file builds a simple formula card that can be used for:
- showing one formula near the mascot
- highlighting a concept
- displaying short math statements
- presenting a focused equation outside the board

Version 1 goals:
- clean rectangular card
- readable border
- optional header strip
- easy area for later text/formula placement

This file only builds the card prop.
It does not populate it with LaTeX or text yet.
"""

from __future__ import annotations

from manimlib import RoundedRectangle, VGroup

from mathlab_creature.config.colors import FORMULA_CARD_FILL
from mathlab_creature.config.colors import FORMULA_CARD_STROKE
from mathlab_creature.config.defaults import DEBUG_MODE
from mathlab_creature.config.defaults import LOG_CREATURE_BUILD
from mathlab_creature.config.sizes import FORMULA_CARD_HEIGHT
from mathlab_creature.config.sizes import FORMULA_CARD_WIDTH

from mathlab_creature.core.geometry import point
from mathlab_creature.core.logger import get_logger

logger = get_logger(__name__)


# ============================================================
# Internal constants
# ============================================================

DEFAULT_CARD_CORNER_RADIUS = 0.10
DEFAULT_CARD_STROKE_WIDTH = 2.0

DEFAULT_HEADER_STRIP_WIDTH_RATIO = 0.90
DEFAULT_HEADER_STRIP_HEIGHT_RATIO = 0.14
DEFAULT_HEADER_STRIP_CORNER_RADIUS = 0.05
DEFAULT_HEADER_STRIP_OPACITY = 0.06
DEFAULT_HEADER_STRIP_TOP_INSET_RATIO = 0.90


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
# Internal builders
# ============================================================

def _build_card_surface(
    *,
    width: float = FORMULA_CARD_WIDTH,
    height: float = FORMULA_CARD_HEIGHT,
    corner_radius: float = DEFAULT_CARD_CORNER_RADIUS,
    fill_color: str = FORMULA_CARD_FILL,
    stroke_color: str = FORMULA_CARD_STROKE,
    stroke_width: float = DEFAULT_CARD_STROKE_WIDTH,
) -> RoundedRectangle:
    """
    Build the main formula card surface.
    """
    width = _validate_positive("width", width)
    height = _validate_positive("height", height)
    corner_radius = _validate_non_negative("corner_radius", corner_radius)
    stroke_width = _validate_non_negative("stroke_width", stroke_width)

    card = RoundedRectangle(
        width=width,
        height=height,
        corner_radius=corner_radius,
    )
    card.set_fill(fill_color, opacity=1.0)
    card.set_stroke(stroke_color, width=stroke_width)

    # Lightweight metadata
    card.card_width = width
    card.card_height = height
    card.card_corner_radius = corner_radius
    card.card_stroke_width = stroke_width

    return card


def _build_header_strip(
    *,
    card_width: float = FORMULA_CARD_WIDTH,
    card_height: float = FORMULA_CARD_HEIGHT,
    width_ratio: float = DEFAULT_HEADER_STRIP_WIDTH_RATIO,
    height_ratio: float = DEFAULT_HEADER_STRIP_HEIGHT_RATIO,
    corner_radius: float = DEFAULT_HEADER_STRIP_CORNER_RADIUS,
    fill_color: str = FORMULA_CARD_STROKE,
    fill_opacity: float = DEFAULT_HEADER_STRIP_OPACITY,
) -> RoundedRectangle:
    """
    Build a subtle top strip that can later hold a label or topic name.
    """
    card_width = _validate_positive("card_width", card_width)
    card_height = _validate_positive("card_height", card_height)
    width_ratio = _validate_positive("width_ratio", width_ratio)
    height_ratio = _validate_positive("height_ratio", height_ratio)
    corner_radius = _validate_non_negative("corner_radius", corner_radius)
    fill_opacity = _validate_non_negative("fill_opacity", fill_opacity)

    strip = RoundedRectangle(
        width=card_width * width_ratio,
        height=card_height * height_ratio,
        corner_radius=corner_radius,
    )
    strip.set_fill(fill_color, opacity=fill_opacity)
    strip.set_stroke(fill_color, width=0)

    # Lightweight metadata
    strip.strip_width_ratio = width_ratio
    strip.strip_height_ratio = height_ratio
    strip.strip_fill_opacity = fill_opacity

    return strip


# ============================================================
# Public builder
# ============================================================

def build_formula_card(
    *,
    width: float = FORMULA_CARD_WIDTH,
    height: float = FORMULA_CARD_HEIGHT,
    include_header_strip: bool = True,
    card_corner_radius: float = DEFAULT_CARD_CORNER_RADIUS,
    card_stroke_width: float = DEFAULT_CARD_STROKE_WIDTH,
    header_strip_width_ratio: float = DEFAULT_HEADER_STRIP_WIDTH_RATIO,
    header_strip_height_ratio: float = DEFAULT_HEADER_STRIP_HEIGHT_RATIO,
    header_strip_opacity: float = DEFAULT_HEADER_STRIP_OPACITY,
    header_strip_top_inset_ratio: float = DEFAULT_HEADER_STRIP_TOP_INSET_RATIO,
    assign_name: bool = True,
) -> VGroup:
    """
    Build the full formula card prop.

    Parameters:
        width:
            Card width.

        height:
            Card height.

        include_header_strip:
            If True, include the subtle top header strip.

        card_corner_radius:
            Corner radius for the main card surface.

        card_stroke_width:
            Stroke width for the card border.

        header_strip_width_ratio:
            Width ratio of the header strip relative to card width.

        header_strip_height_ratio:
            Height ratio of the header strip relative to card height.

        header_strip_opacity:
            Opacity of the header strip fill.

        header_strip_top_inset_ratio:
            Controls how far the strip sits below the top edge.

        assign_name:
            If True, assign stable names to the group and subparts.

    Returns:
        VGroup(card_surface, optional_header_strip)
    """
    width = _validate_positive("width", width)
    height = _validate_positive("height", height)
    card_corner_radius = _validate_non_negative(
        "card_corner_radius",
        card_corner_radius,
    )
    card_stroke_width = _validate_non_negative(
        "card_stroke_width",
        card_stroke_width,
    )
    header_strip_width_ratio = _validate_positive(
        "header_strip_width_ratio",
        header_strip_width_ratio,
    )
    header_strip_height_ratio = _validate_positive(
        "header_strip_height_ratio",
        header_strip_height_ratio,
    )
    header_strip_opacity = _validate_non_negative(
        "header_strip_opacity",
        header_strip_opacity,
    )
    header_strip_top_inset_ratio = _validate_non_negative(
        "header_strip_top_inset_ratio",
        header_strip_top_inset_ratio,
    )

    if LOG_CREATURE_BUILD:
        logger.info(
            "Building formula card | width=%.3f height=%.3f include_header_strip=%s",
            width,
            height,
            include_header_strip,
        )

    card_surface = _build_card_surface(
        width=width,
        height=height,
        corner_radius=card_corner_radius,
        stroke_width=card_stroke_width,
    )

    parts = [card_surface]
    header_strip = None

    if include_header_strip:
        header_strip = _build_header_strip(
            card_width=width,
            card_height=height,
            width_ratio=header_strip_width_ratio,
            height_ratio=header_strip_height_ratio,
            fill_opacity=header_strip_opacity,
        )

        header_strip.move_to(card_surface.get_top())
        header_strip.shift(
            point(
                0.0,
                -(header_strip.get_height() * header_strip_top_inset_ratio),
                0.0,
            )
        )

        parts.append(header_strip)

    card = VGroup(*parts)

    if assign_name:
        card.name = "formula_card"
        card_surface.name = "formula_card_surface"
        if header_strip is not None:
            header_strip.name = "formula_card_header_strip"

    # Lightweight metadata for later teaching / lesson scenes
    card.surface = card_surface
    card.header_strip = header_strip
    card.card_width = width
    card.card_height = height
    card.has_header_strip = include_header_strip

    if DEBUG_MODE:
        logger.debug(
            "Formula card built | width=%.3f height=%.3f header_strip=%s",
            width,
            height,
            include_header_strip,
        )

    if LOG_CREATURE_BUILD:
        logger.info("Formula card created successfully")

    return card