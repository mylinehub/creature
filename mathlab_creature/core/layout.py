"""
Layout helper utilities for mathlab-mylinehub-creature.

This file contains small reusable helpers for arranging numeric points in a
clean, predictable way.

Architecture rule:
- layout.py works with points only
- layout.py does not create Manim objects
- layout.py does not move creature parts directly
- layout.py does not contain audio logic
- audio remains separate and may later be triggered by actions

This file focuses on:
- horizontal and vertical point arrangement
- centered row / column point generation
- bounds helpers
- relative placement helpers
- simple scene guide anchors
- multi-point span helpers
"""

from __future__ import annotations

from typing import Iterable
from typing import Optional

import numpy as np

from mathlab_creature.config.sizes import DEFAULT_EDGE_BUFFER
from mathlab_creature.config.sizes import DEFAULT_OBJECT_BUFFER

from mathlab_creature.core.geometry import as_vec3
from mathlab_creature.core.geometry import midpoint
from mathlab_creature.core.geometry import offset
from mathlab_creature.core.geometry import point
from mathlab_creature.core.geometry import zero_point


# ============================================================
# Type aliases
# ============================================================

Vec3Like = np.ndarray | Iterable[float]
BoundsMap = dict[str, np.ndarray]
SpanMap = dict[str, np.ndarray | float]


# ============================================================
# Internal helpers
# ============================================================

def _coerce_point(
    value: Optional[Vec3Like] = None,
    name: str = "point",
) -> np.ndarray:
    """
    Normalize an incoming point-like value into a clean 3D numpy point.

    Accepted:
    - None -> origin
    - numpy array with shape (3,)
    - list/tuple/iterable with exactly 3 numeric values
    """
    if value is None:
        return zero_point()

    return as_vec3(
        value,
        name=name,
    )


def _validate_count(
    count: int,
) -> int:
    """
    Ensure count is a non-negative integer.
    """
    if not isinstance(count, int):
        raise TypeError(
            f"count must be an int, got {type(count).__name__}"
        )

    if count < 0:
        raise ValueError(
            f"count must be >= 0, got {count}"
        )

    return count


def _validate_gap(
    gap: float,
) -> float:
    """
    Ensure a gap value is non-negative.
    """
    if not isinstance(gap, (int, float)):
        raise TypeError(
            f"gap must be numeric, got {type(gap).__name__}"
        )

    if gap < 0:
        raise ValueError(
            f"gap must be >= 0, got {gap}"
        )

    return float(gap)


def _validate_distance(
    distance: float,
) -> float:
    """
    Ensure a relative placement distance is numeric.

    Negative values are allowed because they can be intentional.
    """
    if not isinstance(distance, (int, float)):
        raise TypeError(
            f"distance must be numeric, got {type(distance).__name__}"
        )

    return float(distance)


def _validate_dimension(
    name: str,
    value: float,
) -> float:
    """
    Ensure width/height values are non-negative numeric values.
    """
    if not isinstance(value, (int, float)):
        raise TypeError(
            f"{name} must be numeric, got {type(value).__name__}"
        )

    if value < 0:
        raise ValueError(
            f"{name} must be >= 0, got {value}"
        )

    return float(value)


# ============================================================
# Basic spacing helpers
# ============================================================

def gap_after(
    index: int,
    gap: float = DEFAULT_OBJECT_BUFFER,
) -> float:
    """
    Return the cumulative gap after a given zero-based index.

    Example:
        index=0, gap=0.25 -> 0.0
        index=1, gap=0.25 -> 0.25
        index=2, gap=0.25 -> 0.50
    """
    if not isinstance(index, int):
        raise TypeError(
            f"index must be an int, got {type(index).__name__}"
        )

    if index < 0:
        raise ValueError(
            f"index must be >= 0, got {index}"
        )

    gap = _validate_gap(gap)

    return index * gap


def total_gaps(
    count: int,
    gap: float = DEFAULT_OBJECT_BUFFER,
) -> float:
    """
    Total spacing occupied by gaps between count items.

    Example:
        count = 1 -> 0 gaps
        count = 2 -> 1 gap
        count = 3 -> 2 gaps
    """
    count = _validate_count(count)
    gap = _validate_gap(gap)

    if count <= 1:
        return 0.0

    return (count - 1) * gap


def total_span(
    count: int,
    gap: float = DEFAULT_OBJECT_BUFFER,
) -> float:
    """
    Return the total center-to-center span for count items spaced by gap.
    """
    return total_gaps(
        count,
        gap,
    )


# ============================================================
# Point row / column generation
# ============================================================

def horizontal_points(
    count: int,
    start: Optional[Vec3Like] = None,
    gap: float = DEFAULT_OBJECT_BUFFER,
) -> list[np.ndarray]:
    """
    Create equally spaced points horizontally.

    Example:
        count=3, start=(0,0,0), gap=1
        -> [(0,0,0), (1,0,0), (2,0,0)]
    """
    count = _validate_count(count)
    gap = _validate_gap(gap)
    start_point = _coerce_point(
        start,
        "start",
    )

    return [
        offset(
            start_point,
            i * gap,
            0.0,
            0.0,
        )
        for i in range(count)
    ]


def vertical_points(
    count: int,
    start: Optional[Vec3Like] = None,
    gap: float = DEFAULT_OBJECT_BUFFER,
) -> list[np.ndarray]:
    """
    Create equally spaced points vertically.

    Example:
        count=3, start=(0,0,0), gap=1
        -> [(0,0,0), (0,1,0), (0,2,0)]
    """
    count = _validate_count(count)
    gap = _validate_gap(gap)
    start_point = _coerce_point(
        start,
        "start",
    )

    return [
        offset(
            start_point,
            0.0,
            i * gap,
            0.0,
        )
        for i in range(count)
    ]


# ============================================================
# Centered row / column generation
# ============================================================

def centered_horizontal_points(
    count: int,
    center: Optional[Vec3Like] = None,
    gap: float = DEFAULT_OBJECT_BUFFER,
) -> list[np.ndarray]:
    """
    Create a centered horizontal row of points around a center point.

    Example:
        count=3, center=(0,0,0), gap=1
        -> [(-1,0,0), (0,0,0), (1,0,0)]
    """
    count = _validate_count(count)
    gap = _validate_gap(gap)
    center_point = _coerce_point(
        center,
        "center",
    )

    if count == 0:
        return []

    total_width = total_gaps(
        count,
        gap,
    )
    start_x = center_point[0] - total_width / 2.0
    start = point(
        start_x,
        center_point[1],
        center_point[2],
    )

    return horizontal_points(
        count=count,
        start=start,
        gap=gap,
    )


def centered_vertical_points(
    count: int,
    center: Optional[Vec3Like] = None,
    gap: float = DEFAULT_OBJECT_BUFFER,
) -> list[np.ndarray]:
    """
    Create a centered vertical column of points around a center point.

    Example:
        count=3, center=(0,0,0), gap=1
        -> [(0,-1,0), (0,0,0), (0,1,0)]
    """
    count = _validate_count(count)
    gap = _validate_gap(gap)
    center_point = _coerce_point(
        center,
        "center",
    )

    if count == 0:
        return []

    total_height = total_gaps(
        count,
        gap,
    )
    start_y = center_point[1] - total_height / 2.0
    start = point(
        center_point[0],
        start_y,
        center_point[2],
    )

    return vertical_points(
        count=count,
        start=start,
        gap=gap,
    )


# ============================================================
# Bounds and frame helpers
# ============================================================

def bounds_from_center(
    center: Vec3Like,
    width: float,
    height: float,
) -> BoundsMap:
    """
    Return common bounding points from a center, width, and height.
    """
    center_point = _coerce_point(
        center,
        "center",
    )
    width = _validate_dimension(
        "width",
        width,
    )
    height = _validate_dimension(
        "height",
        height,
    )

    half_w = width / 2.0
    half_h = height / 2.0

    return {
        "center": center_point,
        "top": point(center_point[0], center_point[1] + half_h, center_point[2]),
        "bottom": point(center_point[0], center_point[1] - half_h, center_point[2]),
        "left": point(center_point[0] - half_w, center_point[1], center_point[2]),
        "right": point(center_point[0] + half_w, center_point[1], center_point[2]),
        "top_left": point(center_point[0] - half_w, center_point[1] + half_h, center_point[2]),
        "top_right": point(center_point[0] + half_w, center_point[1] + half_h, center_point[2]),
        "bottom_left": point(center_point[0] - half_w, center_point[1] - half_h, center_point[2]),
        "bottom_right": point(center_point[0] + half_w, center_point[1] - half_h, center_point[2]),
    }


def bounds_size(
    width: float,
    height: float,
) -> dict[str, float]:
    """
    Return width/height and their halves.
    """
    width = _validate_dimension(
        "width",
        width,
    )
    height = _validate_dimension(
        "height",
        height,
    )

    return {
        "width": width,
        "height": height,
        "half_width": width / 2.0,
        "half_height": height / 2.0,
    }


# ============================================================
# Relative alignment helpers
# ============================================================

def place_right_of(
    base_point: Vec3Like,
    distance: float = DEFAULT_OBJECT_BUFFER,
) -> np.ndarray:
    """
    Return a point to the right of base_point.
    """
    return offset(
        _coerce_point(base_point, "base_point"),
        _validate_distance(distance),
        0.0,
        0.0,
    )


def place_left_of(
    base_point: Vec3Like,
    distance: float = DEFAULT_OBJECT_BUFFER,
) -> np.ndarray:
    """
    Return a point to the left of base_point.
    """
    return offset(
        _coerce_point(base_point, "base_point"),
        -_validate_distance(distance),
        0.0,
        0.0,
    )


def place_above(
    base_point: Vec3Like,
    distance: float = DEFAULT_OBJECT_BUFFER,
) -> np.ndarray:
    """
    Return a point above base_point.
    """
    return offset(
        _coerce_point(base_point, "base_point"),
        0.0,
        _validate_distance(distance),
        0.0,
    )


def place_below(
    base_point: Vec3Like,
    distance: float = DEFAULT_OBJECT_BUFFER,
) -> np.ndarray:
    """
    Return a point below base_point.
    """
    return offset(
        _coerce_point(base_point, "base_point"),
        0.0,
        -_validate_distance(distance),
        0.0,
    )


# ============================================================
# Two-object / three-object layout helpers
# ============================================================

def centers_for_horizontal_pair(
    center: Optional[Vec3Like] = None,
    gap: float = DEFAULT_OBJECT_BUFFER,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Return left and right centers for a simple horizontal pair.
    """
    center_point = _coerce_point(
        center,
        "center",
    )
    gap = _validate_gap(gap)

    half_gap = gap / 2.0

    return (
        offset(center_point, -half_gap, 0.0, 0.0),
        offset(center_point, half_gap, 0.0, 0.0),
    )


def centers_for_vertical_pair(
    center: Optional[Vec3Like] = None,
    gap: float = DEFAULT_OBJECT_BUFFER,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Return bottom and top centers for a simple vertical pair.
    """
    center_point = _coerce_point(
        center,
        "center",
    )
    gap = _validate_gap(gap)

    half_gap = gap / 2.0

    return (
        offset(center_point, 0.0, -half_gap, 0.0),
        offset(center_point, 0.0, half_gap, 0.0),
    )


def centers_for_horizontal_triplet(
    center: Optional[Vec3Like] = None,
    gap: float = DEFAULT_OBJECT_BUFFER,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Return left, center, and right points for a horizontal triplet.
    """
    center_point = _coerce_point(
        center,
        "center",
    )
    gap = _validate_gap(gap)

    return (
        offset(center_point, -gap, 0.0, 0.0),
        center_point,
        offset(center_point, gap, 0.0, 0.0),
    )


def centers_for_vertical_triplet(
    center: Optional[Vec3Like] = None,
    gap: float = DEFAULT_OBJECT_BUFFER,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Return bottom, center, and top points for a vertical triplet.
    """
    center_point = _coerce_point(
        center,
        "center",
    )
    gap = _validate_gap(gap)

    return (
        offset(center_point, 0.0, -gap, 0.0),
        center_point,
        offset(center_point, 0.0, gap, 0.0),
    )


# ============================================================
# Scene guide layout helpers
# ============================================================

def scene_title_anchor(
    frame_top_center: Vec3Like,
    top_buffer: float = DEFAULT_EDGE_BUFFER,
) -> np.ndarray:
    """
    Anchor for placing a title slightly below the top frame center.
    """
    return offset(
        _coerce_point(frame_top_center, "frame_top_center"),
        0.0,
        -_validate_gap(top_buffer),
        0.0,
    )


def scene_footer_anchor(
    frame_bottom_center: Vec3Like,
    bottom_buffer: float = DEFAULT_EDGE_BUFFER,
) -> np.ndarray:
    """
    Anchor for placing content slightly above the bottom frame center.
    """
    return offset(
        _coerce_point(frame_bottom_center, "frame_bottom_center"),
        0.0,
        _validate_gap(bottom_buffer),
        0.0,
    )


def scene_left_anchor(
    frame_left_center: Vec3Like,
    left_buffer: float = DEFAULT_EDGE_BUFFER,
) -> np.ndarray:
    """
    Anchor for placing content slightly inside the left frame edge.
    """
    return offset(
        _coerce_point(frame_left_center, "frame_left_center"),
        _validate_gap(left_buffer),
        0.0,
        0.0,
    )


def scene_right_anchor(
    frame_right_center: Vec3Like,
    right_buffer: float = DEFAULT_EDGE_BUFFER,
) -> np.ndarray:
    """
    Anchor for placing content slightly inside the right frame edge.
    """
    return offset(
        _coerce_point(frame_right_center, "frame_right_center"),
        -_validate_gap(right_buffer),
        0.0,
        0.0,
    )


# ============================================================
# Creature layout helpers
# ============================================================

def creature_center_on_scene(
    scene_center: Optional[Vec3Like] = None,
) -> np.ndarray:
    """
    Return the recommended creature root position for a centered scene.
    """
    return _coerce_point(
        scene_center,
        "scene_center",
    )


def creature_left_stage_position(
    scene_center: Optional[Vec3Like] = None,
    distance: float = 2.5,
) -> np.ndarray:
    """
    Return a left-stage creature root position.
    """
    return place_left_of(
        _coerce_point(scene_center, "scene_center"),
        distance,
    )


def creature_right_stage_position(
    scene_center: Optional[Vec3Like] = None,
    distance: float = 2.5,
) -> np.ndarray:
    """
    Return a right-stage creature root position.
    """
    return place_right_of(
        _coerce_point(scene_center, "scene_center"),
        distance,
    )


# ============================================================
# Multi-point convenience helpers
# ============================================================

def center_of_points(
    points: list[Vec3Like],
) -> np.ndarray:
    """
    Return average center of a list of points.

    If the list is empty, return origin.
    """
    if not points:
        return zero_point()

    normalized_points: list[np.ndarray] = [
        _coerce_point(
            p,
            "point",
        )
        for p in points
    ]

    stacked = np.array(
        normalized_points,
        dtype=float,
    )

    return np.mean(
        stacked,
        axis=0,
    )


def span_midpoint(
    p1: Vec3Like,
    p2: Vec3Like,
) -> np.ndarray:
    """
    Small wrapper around midpoint for semantic readability.
    """
    return midpoint(
        _coerce_point(p1, "p1"),
        _coerce_point(p2, "p2"),
    )


def span_between_points(
    points: list[Vec3Like],
) -> SpanMap:
    """
    Return simple span information for a set of points.

    Useful for quick layout inspection and debug helpers.
    """
    if not points:
        origin = zero_point()

        return {
            "min": origin,
            "max": origin,
            "center": origin,
            "width": 0.0,
            "height": 0.0,
            "depth": 0.0,
        }

    normalized_points: list[np.ndarray] = [
        _coerce_point(
            p,
            "point",
        )
        for p in points
    ]

    stacked = np.array(
        normalized_points,
        dtype=float,
    )

    min_vals = np.min(
        stacked,
        axis=0,
    )
    max_vals = np.max(
        stacked,
        axis=0,
    )
    center = (min_vals + max_vals) / 2.0

    return {
        "min": point(min_vals[0], min_vals[1], min_vals[2]),
        "max": point(max_vals[0], max_vals[1], max_vals[2]),
        "center": point(center[0], center[1], center[2]),
        "width": float(max_vals[0] - min_vals[0]),
        "height": float(max_vals[1] - min_vals[1]),
        "depth": float(max_vals[2] - min_vals[2]),
    }


# ============================================================
# Export control
# ============================================================

__all__ = [
    "Vec3Like",
    "BoundsMap",
    "SpanMap",
    "gap_after",
    "total_gaps",
    "total_span",
    "horizontal_points",
    "vertical_points",
    "centered_horizontal_points",
    "centered_vertical_points",
    "bounds_from_center",
    "bounds_size",
    "place_right_of",
    "place_left_of",
    "place_above",
    "place_below",
    "centers_for_horizontal_pair",
    "centers_for_vertical_pair",
    "centers_for_horizontal_triplet",
    "centers_for_vertical_triplet",
    "scene_title_anchor",
    "scene_footer_anchor",
    "scene_left_anchor",
    "scene_right_anchor",
    "creature_center_on_scene",
    "creature_left_stage_position",
    "creature_right_stage_position",
    "center_of_points",
    "span_midpoint",
    "span_between_points",
]