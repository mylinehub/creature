"""
Math board prop for mathlab-mylinehub-creature.

This file builds a simple teaching board that can be used in:
- mascot teaching scenes
- formula explanation scenes
- vector / matrix intro scenes

Version 1 goals:
- clean readable board
- dark board surface
- visible border
- optional title strip area
- easy to place formulas/text on top later

This file only builds the board prop.
It does not populate the board with formulas yet.
"""

from __future__ import annotations

from manimlib import RoundedRectangle, VGroup

from config.colors import MATH_BOARD_FILL
from config.colors import MATH_BOARD_STROKE
from config.defaults import DEBUG_MODE
from config.defaults import LOG_CREATURE_BUILD
from config.sizes import MATH_BOARD_HEIGHT
from config.sizes import MATH_BOARD_WIDTH

from core.geometry import point
from core.logger import get_logger

logger = get_logger(__name__)


# ============================================================
# Internal constants
# ============================================================

DEFAULT_BOARD_CORNER_RADIUS = 0.12
DEFAULT_BOARD_STROKE_WIDTH = 3.0

DEFAULT_TITLE_STRIP_WIDTH_RATIO = 0.92
DEFAULT_TITLE_STRIP_HEIGHT_RATIO = 0.12
DEFAULT_TITLE_STRIP_CORNER_RADIUS = 0.06
DEFAULT_TITLE_STRIP_OPACITY = 0.08
DEFAULT_TITLE_STRIP_TOP_INSET_RATIO = 0.85


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

def _build_board_surface(
    *,
    width: float = MATH_BOARD_WIDTH,
    height: float = MATH_BOARD_HEIGHT,
    corner_radius: float = DEFAULT_BOARD_CORNER_RADIUS,
    fill_color: str = MATH_BOARD_FILL,
    stroke_color: str = MATH_BOARD_STROKE,
    stroke_width: float = DEFAULT_BOARD_STROKE_WIDTH,
) -> RoundedRectangle:
    """
    Build the main board surface.
    """
    width = _validate_positive("width", width)
    height = _validate_positive("height", height)
    corner_radius = _validate_non_negative("corner_radius", corner_radius)
    stroke_width = _validate_non_negative("stroke_width", stroke_width)

    board = RoundedRectangle(
        width=width,
        height=height,
        corner_radius=corner_radius,
    )
    board.set_fill(fill_color, opacity=1.0)
    board.set_stroke(stroke_color, width=stroke_width)

    # Lightweight metadata
    board.board_width = width
    board.board_height = height
    board.board_corner_radius = corner_radius
    board.board_stroke_width = stroke_width

    return board


def _build_title_strip(
    *,
    board_width: float = MATH_BOARD_WIDTH,
    board_height: float = MATH_BOARD_HEIGHT,
    width_ratio: float = DEFAULT_TITLE_STRIP_WIDTH_RATIO,
    height_ratio: float = DEFAULT_TITLE_STRIP_HEIGHT_RATIO,
    corner_radius: float = DEFAULT_TITLE_STRIP_CORNER_RADIUS,
    fill_color: str = MATH_BOARD_STROKE,
    fill_opacity: float = DEFAULT_TITLE_STRIP_OPACITY,
) -> RoundedRectangle:
    """
    Build a subtle top strip area for later headings if needed.
    """
    board_width = _validate_positive("board_width", board_width)
    board_height = _validate_positive("board_height", board_height)
    width_ratio = _validate_positive("width_ratio", width_ratio)
    height_ratio = _validate_positive("height_ratio", height_ratio)
    corner_radius = _validate_non_negative("corner_radius", corner_radius)
    fill_opacity = _validate_non_negative("fill_opacity", fill_opacity)

    strip = RoundedRectangle(
        width=board_width * width_ratio,
        height=board_height * height_ratio,
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

def build_math_board(
    *,
    width: float = MATH_BOARD_WIDTH,
    height: float = MATH_BOARD_HEIGHT,
    include_title_strip: bool = True,
    board_corner_radius: float = DEFAULT_BOARD_CORNER_RADIUS,
    board_stroke_width: float = DEFAULT_BOARD_STROKE_WIDTH,
    title_strip_width_ratio: float = DEFAULT_TITLE_STRIP_WIDTH_RATIO,
    title_strip_height_ratio: float = DEFAULT_TITLE_STRIP_HEIGHT_RATIO,
    title_strip_opacity: float = DEFAULT_TITLE_STRIP_OPACITY,
    title_strip_top_inset_ratio: float = DEFAULT_TITLE_STRIP_TOP_INSET_RATIO,
    assign_name: bool = True,
) -> VGroup:
    """
    Build the full math board prop.

    Parameters:
        width:
            Board width.

        height:
            Board height.

        include_title_strip:
            If True, include the subtle top title strip.

        board_corner_radius:
            Corner radius for the main board surface.

        board_stroke_width:
            Stroke width for the board border.

        title_strip_width_ratio:
            Width ratio of the title strip relative to board width.

        title_strip_height_ratio:
            Height ratio of the title strip relative to board height.

        title_strip_opacity:
            Opacity of the title strip fill.

        title_strip_top_inset_ratio:
            Controls how far the title strip sits below the top edge.

        assign_name:
            If True, assign stable names to the group and subparts.

    Returns:
        VGroup(board_surface, optional_title_strip)
    """
    width = _validate_positive("width", width)
    height = _validate_positive("height", height)
    board_corner_radius = _validate_non_negative(
        "board_corner_radius",
        board_corner_radius,
    )
    board_stroke_width = _validate_non_negative(
        "board_stroke_width",
        board_stroke_width,
    )
    title_strip_width_ratio = _validate_positive(
        "title_strip_width_ratio",
        title_strip_width_ratio,
    )
    title_strip_height_ratio = _validate_positive(
        "title_strip_height_ratio",
        title_strip_height_ratio,
    )
    title_strip_opacity = _validate_non_negative(
        "title_strip_opacity",
        title_strip_opacity,
    )
    title_strip_top_inset_ratio = _validate_non_negative(
        "title_strip_top_inset_ratio",
        title_strip_top_inset_ratio,
    )

    if LOG_CREATURE_BUILD:
        logger.info(
            "Building math board | width=%.3f height=%.3f include_title_strip=%s",
            width,
            height,
            include_title_strip,
        )

    board_surface = _build_board_surface(
        width=width,
        height=height,
        corner_radius=board_corner_radius,
        stroke_width=board_stroke_width,
    )

    parts = [board_surface]
    title_strip = None

    if include_title_strip:
        title_strip = _build_title_strip(
            board_width=width,
            board_height=height,
            width_ratio=title_strip_width_ratio,
            height_ratio=title_strip_height_ratio,
            fill_opacity=title_strip_opacity,
        )

        title_strip.move_to(board_surface.get_top())
        title_strip.shift(
            point(
                0.0,
                -(title_strip.get_height() * title_strip_top_inset_ratio),
                0.0,
            )
        )

        parts.append(title_strip)

    board = VGroup(*parts)

    if assign_name:
        board.name = "math_board"
        board_surface.name = "math_board_surface"
        if title_strip is not None:
            title_strip.name = "math_board_title_strip"

    # Lightweight metadata for later teaching scenes
    board.surface = board_surface
    board.title_strip = title_strip
    board.board_width = width
    board.board_height = height
    board.has_title_strip = include_title_strip

    if DEBUG_MODE:
        logger.debug(
            "Math board built | width=%.3f height=%.3f title_strip=%s",
            width,
            height,
            include_title_strip,
        )

    if LOG_CREATURE_BUILD:
        logger.info("Math board created successfully")

    return board