"""
Axis plane prop for mathlab-mylinehub-creature.

This file builds a simple 2D coordinate axis plane that can be used for:
- vector explanations
- linear algebra visuals
- plotting simple functions
- teaching coordinate systems

Version 1 goals:
- clean X and Y axes
- readable axis endpoints
- optional light grid
- centered at origin
- easy to move/scale in scenes

This file only builds the axis plane.
It does not plot functions yet.
"""

from __future__ import annotations

from manimlib import Line, VGroup

from config.colors import AXIS_COLOR
from config.colors import GRID_LIGHT
from config.defaults import DEBUG_MODE
from config.defaults import LOG_CREATURE_BUILD

from core.geometry import point
from core.logger import get_logger

logger = get_logger(__name__)


# ============================================================
# Internal constants
# ============================================================

# Local defaults used because these were not part of the earlier
# shared config.sizes file set.
DEFAULT_AXIS_HALF_LENGTH = 3.0
DEFAULT_AXIS_STROKE_WIDTH = 2.5
DEFAULT_GRID_SPACING = 0.5
DEFAULT_GRID_STROKE_WIDTH = 1.0
DEFAULT_GRID_OPACITY = 0.30

# Small visual end markers to make positive directions read more clearly
# without introducing a heavier arrow-tip dependency.
DEFAULT_AXIS_END_TICK_SIZE = 0.10
DEFAULT_NEGATIVE_END_TICK_SIZE = 0.06


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


def _build_axis_end_tick(
    *,
    center_x: float,
    center_y: float,
    size: float,
    vertical: bool,
    color: str,
    stroke_width: float,
) -> Line:
    """
    Build a small tick mark used at axis endpoints.

    vertical=True  -> small vertical tick
    vertical=False -> small horizontal tick
    """
    size = _validate_positive("size", size)
    stroke_width = _validate_positive("stroke_width", stroke_width)

    half = size / 2.0

    if vertical:
        start = point(center_x, center_y - half, 0.0)
        end = point(center_x, center_y + half, 0.0)
    else:
        start = point(center_x - half, center_y, 0.0)
        end = point(center_x + half, center_y, 0.0)

    tick = Line(start, end)
    tick.set_stroke(color, width=stroke_width)
    return tick


def _build_axes(
    *,
    axis_half_length: float,
    axis_stroke_width: float,
    axis_color: str,
    include_end_ticks: bool,
) -> VGroup:
    """
    Build X and Y axes centered at the origin.
    """
    axis_half_length = _validate_positive("axis_half_length", axis_half_length)
    axis_stroke_width = _validate_positive("axis_stroke_width", axis_stroke_width)

    x_axis = Line(
        point(-axis_half_length, 0.0, 0.0),
        point(axis_half_length, 0.0, 0.0),
    )
    x_axis.set_stroke(axis_color, width=axis_stroke_width)

    y_axis = Line(
        point(0.0, -axis_half_length, 0.0),
        point(0.0, axis_half_length, 0.0),
    )
    y_axis.set_stroke(axis_color, width=axis_stroke_width)

    parts = [x_axis, y_axis]

    if include_end_ticks:
        # Positive ends slightly more visible
        x_pos_tick = _build_axis_end_tick(
            center_x=axis_half_length,
            center_y=0.0,
            size=DEFAULT_AXIS_END_TICK_SIZE,
            vertical=True,
            color=axis_color,
            stroke_width=axis_stroke_width,
        )
        y_pos_tick = _build_axis_end_tick(
            center_x=0.0,
            center_y=axis_half_length,
            size=DEFAULT_AXIS_END_TICK_SIZE,
            vertical=False,
            color=axis_color,
            stroke_width=axis_stroke_width,
        )

        # Negative ends slightly smaller/subtler
        x_neg_tick = _build_axis_end_tick(
            center_x=-axis_half_length,
            center_y=0.0,
            size=DEFAULT_NEGATIVE_END_TICK_SIZE,
            vertical=True,
            color=axis_color,
            stroke_width=axis_stroke_width,
        )
        y_neg_tick = _build_axis_end_tick(
            center_x=0.0,
            center_y=-axis_half_length,
            size=DEFAULT_NEGATIVE_END_TICK_SIZE,
            vertical=False,
            color=axis_color,
            stroke_width=axis_stroke_width,
        )

        x_pos_tick.name = "axis_plane_x_positive_tick"
        y_pos_tick.name = "axis_plane_y_positive_tick"
        x_neg_tick.name = "axis_plane_x_negative_tick"
        y_neg_tick.name = "axis_plane_y_negative_tick"

        parts.extend([x_pos_tick, y_pos_tick, x_neg_tick, y_neg_tick])

    axes = VGroup(*parts)
    x_axis.name = "axis_plane_x_axis"
    y_axis.name = "axis_plane_y_axis"

    # Lightweight metadata
    axes.x_axis = x_axis
    axes.y_axis = y_axis
    axes.axis_half_length = axis_half_length
    axes.axis_stroke_width = axis_stroke_width

    return axes


def _build_grid(
    *,
    axis_half_length: float,
    grid_spacing: float,
    grid_color: str,
    grid_stroke_width: float,
    grid_opacity: float,
) -> VGroup:
    """
    Build a light grid behind the axes.
    """
    axis_half_length = _validate_positive("axis_half_length", axis_half_length)
    grid_spacing = _validate_positive("grid_spacing", grid_spacing)
    grid_stroke_width = _validate_positive("grid_stroke_width", grid_stroke_width)
    grid_opacity = _validate_positive("grid_opacity", grid_opacity)

    grid = VGroup()

    # Use integer step counts instead of float while-loops
    # to avoid accumulation drift.
    count_each_side = int(round(axis_half_length / grid_spacing))
    values = [
        i * grid_spacing
        for i in range(-count_each_side, count_each_side + 1)
    ]

    # vertical lines
    for x in values:
        line = Line(
            point(x, -axis_half_length, 0.0),
            point(x, axis_half_length, 0.0),
        )
        line.set_stroke(grid_color, width=grid_stroke_width, opacity=grid_opacity)
        grid.add(line)

    # horizontal lines
    for y in values:
        line = Line(
            point(-axis_half_length, y, 0.0),
            point(axis_half_length, y, 0.0),
        )
        line.set_stroke(grid_color, width=grid_stroke_width, opacity=grid_opacity)
        grid.add(line)

    grid.name = "axis_plane_grid"

    # Lightweight metadata
    grid.axis_half_length = axis_half_length
    grid.grid_spacing = grid_spacing
    grid.grid_line_count = len(grid)

    return grid


# ============================================================
# Public builder
# ============================================================

def build_axis_plane(
    *,
    show_grid: bool = True,
    axis_half_length: float = DEFAULT_AXIS_HALF_LENGTH,
    axis_stroke_width: float = DEFAULT_AXIS_STROKE_WIDTH,
    grid_spacing: float = DEFAULT_GRID_SPACING,
    grid_stroke_width: float = DEFAULT_GRID_STROKE_WIDTH,
    grid_opacity: float = DEFAULT_GRID_OPACITY,
    axis_color: str = AXIS_COLOR,
    grid_color: str = GRID_LIGHT,
    include_end_ticks: bool = True,
    assign_name: bool = True,
) -> VGroup:
    """
    Build the full axis plane.

    Args:
        show_grid:
            If True, include background grid.

        axis_half_length:
            Half-length of each axis from the origin.

        axis_stroke_width:
            Stroke width for the main axes.

        grid_spacing:
            Distance between grid lines.

        grid_stroke_width:
            Stroke width for grid lines.

        grid_opacity:
            Opacity for grid lines.

        axis_color:
            Axis stroke color.

        grid_color:
            Grid stroke color.

        include_end_ticks:
            If True, include small endpoint tick markers for readability.

        assign_name:
            If True, assign a stable name to the plane group.

    Returns:
        VGroup(grid?, axes)
    """
    axis_half_length = _validate_positive("axis_half_length", axis_half_length)
    axis_stroke_width = _validate_positive("axis_stroke_width", axis_stroke_width)
    grid_spacing = _validate_positive("grid_spacing", grid_spacing)
    grid_stroke_width = _validate_positive("grid_stroke_width", grid_stroke_width)
    grid_opacity = _validate_positive("grid_opacity", grid_opacity)

    if LOG_CREATURE_BUILD:
        logger.info(
            "Building axis plane | show_grid=%s axis_half_length=%.3f grid_spacing=%.3f",
            show_grid,
            axis_half_length,
            grid_spacing,
        )

    axes = _build_axes(
        axis_half_length=axis_half_length,
        axis_stroke_width=axis_stroke_width,
        axis_color=axis_color,
        include_end_ticks=include_end_ticks,
    )

    grid = None
    if show_grid:
        grid = _build_grid(
            axis_half_length=axis_half_length,
            grid_spacing=grid_spacing,
            grid_color=grid_color,
            grid_stroke_width=grid_stroke_width,
            grid_opacity=grid_opacity,
        )
        plane = VGroup(grid, axes)
    else:
        plane = VGroup(axes)

    if assign_name:
        plane.name = "axis_plane"

    # Lightweight metadata for lesson scenes
    plane.axes = axes
    plane.grid = grid
    plane.show_grid = show_grid
    plane.axis_half_length = axis_half_length
    plane.grid_spacing = grid_spacing

    if DEBUG_MODE:
        logger.debug(
            "Axis plane built | show_grid=%s axis_half_length=%.3f include_end_ticks=%s",
            show_grid,
            axis_half_length,
            include_end_ticks,
        )

    if LOG_CREATURE_BUILD:
        logger.info("Axis plane created successfully")

    return plane