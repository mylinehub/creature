"""
Layout helper utilities for mathlab-mylinehub-creature.

This file contains small reusable helpers for arranging objects and points in a
clean, predictable way. These helpers are intentionally lightweight and are
meant to reduce repeated spacing/alignment code across scenes and creature
assembly files.

This file focuses on:
- horizontal and vertical arrangement
- simple row / column point generation
- centering helpers
- gap / spacing helpers
- edge placement helpers for scene layout
"""

from __future__ import annotations

import numpy as np

from config.sizes import DEFAULT_EDGE_BUFFER
from config.sizes import DEFAULT_OBJECT_BUFFER
from core.geometry import midpoint
from core.geometry import offset
from core.geometry import point


# ============================================================
# Internal helpers
# ============================================================

def _coerce_point(p: np.ndarray | list[float] | tuple[float, float, float] | None) -> np.ndarray:
    """
    Normalize an incoming point-like value into a clean 3D numpy point.

    Accepted:
    - None -> origin
    - numpy array with shape (3,)
    - list/tuple with exactly 3 numeric values
    """
    if p is None:
        return point(0.0, 0.0, 0.0)

    if isinstance(p, np.ndarray):
        if p.shape != (3,):
            raise ValueError(f"Point must have shape (3,), got {p.shape}")
        return p.astype(float)

    if isinstance(p, (list, tuple)):
        if len(p) != 3:
            raise ValueError(f"Point-like sequence must have 3 values, got {len(p)}")
        return point(p[0], p[1], p[2])

    raise TypeError("Point must be None, a numpy.ndarray, or a 3-item list/tuple")


def _validate_count(count: int) -> int:
    """
    Ensure count is a non-negative integer.
    """
    if not isinstance(count, int):
        raise TypeError(f"count must be an int, got {type(count).__name__}")
    if count < 0:
        raise ValueError(f"count must be >= 0, got {count}")
    return count


def _validate_gap(gap: float) -> float:
    """
    Ensure a gap value is non-negative.
    """
    if not isinstance(gap, (int, float)):
        raise TypeError(f"gap must be numeric, got {type(gap).__name__}")
    if gap < 0:
        raise ValueError(f"gap must be >= 0, got {gap}")
    return float(gap)


def _validate_distance(distance: float) -> float:
    """
    Ensure a relative placement distance is numeric.
    Negative values are allowed because they can be intentional.
    """
    if not isinstance(distance, (int, float)):
        raise TypeError(f"distance must be numeric, got {type(distance).__name__}")
    return float(distance)


def _validate_dimension(name: str, value: float) -> float:
    """
    Ensure width/height values are non-negative numeric values.
    """
    if not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be numeric, got {type(value).__name__}")
    if value < 0:
        raise ValueError(f"{name} must be >= 0, got {value}")
    return float(value)


# ============================================================
# Basic spacing helpers
# ============================================================

def gap_after(index: int, gap: float = DEFAULT_OBJECT_BUFFER) -> float:
    """
    Return the cumulative gap after a given zero-based index.

    Example:
        index=0, gap=0.25 -> 0.0
        index=1, gap=0.25 -> 0.25
        index=2, gap=0.25 -> 0.50
    """
    if not isinstance(index, int):
        raise TypeError(f"index must be an int, got {type(index).__name__}")
    if index < 0:
        raise ValueError(f"index must be >= 0, got {index}")

    gap = _validate_gap(gap)
    return index * gap


def total_gaps(count: int, gap: float = DEFAULT_OBJECT_BUFFER) -> float:
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


def total_span(count: int, gap: float = DEFAULT_OBJECT_BUFFER) -> float:
    """
    Return the total center-to-center span for count items spaced by gap.

    This is effectively the same as total_gaps(), but the name reads better
    in some layout contexts.
    """
    return total_gaps(count, gap)


# ============================================================
# Point row / column generation
# ============================================================

def horizontal_points(
    count: int,
    start: np.ndarray | list[float] | tuple[float, float, float] | None = None,
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
    start = _coerce_point(start)

    return [offset(start, i * gap, 0.0, 0.0) for i in range(count)]


def vertical_points(
    count: int,
    start: np.ndarray | list[float] | tuple[float, float, float] | None = None,
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
    start = _coerce_point(start)

    return [offset(start, 0.0, i * gap, 0.0) for i in range(count)]


# ============================================================
# Centered row / column generation
# ============================================================

def centered_horizontal_points(
    count: int,
    center: np.ndarray | list[float] | tuple[float, float, float] | None = None,
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
    center = _coerce_point(center)

    if count == 0:
        return []

    total_width = total_gaps(count, gap)
    start_x = center[0] - total_width / 2.0
    start = point(start_x, center[1], center[2])

    return horizontal_points(count=count, start=start, gap=gap)


def centered_vertical_points(
    count: int,
    center: np.ndarray | list[float] | tuple[float, float, float] | None = None,
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
    center = _coerce_point(center)

    if count == 0:
        return []

    total_height = total_gaps(count, gap)
    start_y = center[1] - total_height / 2.0
    start = point(center[0], start_y, center[2])

    return vertical_points(count=count, start=start, gap=gap)


# ============================================================
# Bounds and frame helpers
# ============================================================

def bounds_from_center(
    center: np.ndarray | list[float] | tuple[float, float, float],
    width: float,
    height: float,
) -> dict[str, np.ndarray]:
    """
    Return common bounding points from a center, width, and height.
    """
    center = _coerce_point(center)
    width = _validate_dimension("width", width)
    height = _validate_dimension("height", height)

    half_w = width / 2.0
    half_h = height / 2.0

    return {
        "center": center,
        "top": point(center[0], center[1] + half_h, center[2]),
        "bottom": point(center[0], center[1] - half_h, center[2]),
        "left": point(center[0] - half_w, center[1], center[2]),
        "right": point(center[0] + half_w, center[1], center[2]),
        "top_left": point(center[0] - half_w, center[1] + half_h, center[2]),
        "top_right": point(center[0] + half_w, center[1] + half_h, center[2]),
        "bottom_left": point(center[0] - half_w, center[1] - half_h, center[2]),
        "bottom_right": point(center[0] + half_w, center[1] - half_h, center[2]),
    }


def bounds_size(width: float, height: float) -> dict[str, float]:
    """
    Small semantic helper returning width/height and their halves.

    Useful when writing explicit layout code and wanting to avoid repeated
    half-width/half-height math.
    """
    width = _validate_dimension("width", width)
    height = _validate_dimension("height", height)

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
    base_point: np.ndarray | list[float] | tuple[float, float, float],
    distance: float = DEFAULT_OBJECT_BUFFER,
) -> np.ndarray:
    """
    Return a point to the right of base_point.
    """
    return offset(_coerce_point(base_point), _validate_distance(distance), 0.0, 0.0)


def place_left_of(
    base_point: np.ndarray | list[float] | tuple[float, float, float],
    distance: float = DEFAULT_OBJECT_BUFFER,
) -> np.ndarray:
    """
    Return a point to the left of base_point.
    """
    return offset(_coerce_point(base_point), -_validate_distance(distance), 0.0, 0.0)


def place_above(
    base_point: np.ndarray | list[float] | tuple[float, float, float],
    distance: float = DEFAULT_OBJECT_BUFFER,
) -> np.ndarray:
    """
    Return a point above base_point.
    """
    return offset(_coerce_point(base_point), 0.0, _validate_distance(distance), 0.0)


def place_below(
    base_point: np.ndarray | list[float] | tuple[float, float, float],
    distance: float = DEFAULT_OBJECT_BUFFER,
) -> np.ndarray:
    """
    Return a point below base_point.
    """
    return offset(_coerce_point(base_point), 0.0, -_validate_distance(distance), 0.0)


# ============================================================
# Two-object layout helpers
# ============================================================

def centers_for_horizontal_pair(
    center: np.ndarray | list[float] | tuple[float, float, float] | None = None,
    gap: float = DEFAULT_OBJECT_BUFFER,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Return left and right centers for a simple horizontal pair.
    """
    center = _coerce_point(center)
    gap = _validate_gap(gap)

    half_gap = gap / 2.0
    left = offset(center, -half_gap, 0.0, 0.0)
    right = offset(center, half_gap, 0.0, 0.0)
    return left, right


def centers_for_vertical_pair(
    center: np.ndarray | list[float] | tuple[float, float, float] | None = None,
    gap: float = DEFAULT_OBJECT_BUFFER,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Return bottom and top centers for a simple vertical pair.
    """
    center = _coerce_point(center)
    gap = _validate_gap(gap)

    half_gap = gap / 2.0
    bottom = offset(center, 0.0, -half_gap, 0.0)
    top = offset(center, 0.0, half_gap, 0.0)
    return bottom, top


def centers_for_horizontal_triplet(
    center: np.ndarray | list[float] | tuple[float, float, float] | None = None,
    gap: float = DEFAULT_OBJECT_BUFFER,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Return left, center, and right points for a simple horizontal triplet.
    """
    center = _coerce_point(center)
    gap = _validate_gap(gap)

    left = offset(center, -gap, 0.0, 0.0)
    right = offset(center, gap, 0.0, 0.0)
    return left, center, right


def centers_for_vertical_triplet(
    center: np.ndarray | list[float] | tuple[float, float, float] | None = None,
    gap: float = DEFAULT_OBJECT_BUFFER,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Return bottom, center, and top points for a simple vertical triplet.
    """
    center = _coerce_point(center)
    gap = _validate_gap(gap)

    bottom = offset(center, 0.0, -gap, 0.0)
    top = offset(center, 0.0, gap, 0.0)
    return bottom, center, top


# ============================================================
# Scene guide layout helpers
# ============================================================

def scene_title_anchor(
    frame_top_center: np.ndarray | list[float] | tuple[float, float, float],
    top_buffer: float = DEFAULT_EDGE_BUFFER,
) -> np.ndarray:
    """
    Anchor for placing a title slightly below the top frame center.
    """
    return offset(_coerce_point(frame_top_center), 0.0, -_validate_gap(top_buffer), 0.0)


def scene_footer_anchor(
    frame_bottom_center: np.ndarray | list[float] | tuple[float, float, float],
    bottom_buffer: float = DEFAULT_EDGE_BUFFER,
) -> np.ndarray:
    """
    Anchor for placing content slightly above the bottom frame center.
    """
    return offset(_coerce_point(frame_bottom_center), 0.0, _validate_gap(bottom_buffer), 0.0)


def scene_left_anchor(
    frame_left_center: np.ndarray | list[float] | tuple[float, float, float],
    left_buffer: float = DEFAULT_EDGE_BUFFER,
) -> np.ndarray:
    """
    Anchor for placing content slightly inside the left frame edge.
    """
    return offset(_coerce_point(frame_left_center), _validate_gap(left_buffer), 0.0, 0.0)


def scene_right_anchor(
    frame_right_center: np.ndarray | list[float] | tuple[float, float, float],
    right_buffer: float = DEFAULT_EDGE_BUFFER,
) -> np.ndarray:
    """
    Anchor for placing content slightly inside the right frame edge.
    """
    return offset(_coerce_point(frame_right_center), -_validate_gap(right_buffer), 0.0, 0.0)


# ============================================================
# Multi-point convenience helpers
# ============================================================

def center_of_points(points: list[np.ndarray]) -> np.ndarray:
    """
    Return average center of a list of points.

    If the list is empty, return origin.
    """
    if not points:
        return point(0.0, 0.0, 0.0)

    normalized_points: list[np.ndarray] = [_coerce_point(p) for p in points]
    stacked = np.array(normalized_points, dtype=float)
    return np.mean(stacked, axis=0)


def span_midpoint(p1: np.ndarray, p2: np.ndarray) -> np.ndarray:
    """
    Small wrapper around midpoint for semantic readability in layout code.
    """
    return midpoint(_coerce_point(p1), _coerce_point(p2))


def span_between_points(points: list[np.ndarray]) -> dict[str, np.ndarray | float]:
    """
    Return simple span information for a set of points.

    Useful for quick layout inspection and debug helpers.
    """
    if not points:
        origin = point(0.0, 0.0, 0.0)
        return {
            "min": origin,
            "max": origin,
            "center": origin,
            "width": 0.0,
            "height": 0.0,
            "depth": 0.0,
        }

    normalized_points: list[np.ndarray] = [_coerce_point(p) for p in points]
    stacked = np.array(normalized_points, dtype=float)

    min_vals = np.min(stacked, axis=0)
    max_vals = np.max(stacked, axis=0)
    center = (min_vals + max_vals) / 2.0

    return {
        "min": point(min_vals[0], min_vals[1], min_vals[2]),
        "max": point(max_vals[0], max_vals[1], max_vals[2]),
        "center": point(center[0], center[1], center[2]),
        "width": float(max_vals[0] - min_vals[0]),
        "height": float(max_vals[1] - min_vals[1]),
        "depth": float(max_vals[2] - min_vals[2]),
    }