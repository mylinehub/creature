"""
Geometry helper utilities for mathlab-mylinehub-creature.

This module provides small, reusable math helpers for working with:
- points
- vectors
- distances
- interpolation
- rotations
- local/world offsets
- simple transform-safe geometry

Architecture rule:
- geometry.py must stay independent
- no Manim objects are created here
- no audio logic lives here
- no creature part movement lives here
- this file only returns numeric/vector values

The creature system can use these helpers later from:
- anchors.py
- layout.py
- transforms.py
- kinematics.py
- skeleton.py
- body_core.py
"""

from __future__ import annotations

from math import atan2
from math import cos
from math import degrees
from math import radians
from math import sin
from typing import Iterable
from typing import Optional

import numpy as np


# ============================================================
# Constants
# ============================================================

EPSILON = 1e-8

ORIGIN = np.array(
    [0.0, 0.0, 0.0],
    dtype=float,
)

UNIT_X = np.array(
    [1.0, 0.0, 0.0],
    dtype=float,
)

UNIT_Y = np.array(
    [0.0, 1.0, 0.0],
    dtype=float,
)

UNIT_Z = np.array(
    [0.0, 0.0, 1.0],
    dtype=float,
)


# ============================================================
# Internal validation helpers
# ============================================================

def _ensure_numeric(
    value: float | int,
    name: str,
) -> float:
    """
    Ensure a value is numeric and return it as float.
    """
    if not isinstance(value, (int, float)):
        raise TypeError(
            f"{name} must be numeric, got {type(value).__name__}"
        )

    return float(value)


def _ensure_vec3(
    value: np.ndarray | Iterable[float],
    name: str = "vector",
) -> np.ndarray:
    """
    Ensure input is a 3D numpy vector.

    Accepts:
    - numpy array with shape (3,)
    - iterable with exactly 3 numeric values

    Returns:
    - float numpy array with shape (3,)
    """
    if isinstance(value, np.ndarray):
        arr = value.astype(
            float,
            copy=False,
        )
    else:
        arr = np.array(
            list(value),
            dtype=float,
        )

    if arr.shape != (3,):
        raise ValueError(
            f"{name} must be shape (3,), got {arr.shape}"
        )

    return arr


def _ensure_t(
    t: float | int,
    name: str = "t",
) -> float:
    """
    Ensure interpolation parameter is numeric.
    """
    return _ensure_numeric(
        t,
        name,
    )


# ============================================================
# Basic point / vector creation
# ============================================================

def point(
    x: float,
    y: float,
    z: float = 0.0,
) -> np.ndarray:
    """
    Create a 3D point.

    This is Manim-compatible because Manim uses 3D numpy vectors.
    """
    return np.array(
        [
            _ensure_numeric(x, "x"),
            _ensure_numeric(y, "y"),
            _ensure_numeric(z, "z"),
        ],
        dtype=float,
    )


def vec(
    x: float,
    y: float,
    z: float = 0.0,
) -> np.ndarray:
    """
    Create a 3D vector.

    Alias for point(), kept for semantic clarity.
    """
    return point(
        x,
        y,
        z,
    )


def zero_point() -> np.ndarray:
    """
    Return origin point (0, 0, 0).
    """
    return ORIGIN.copy()


def zero_vector() -> np.ndarray:
    """
    Return zero vector (0, 0, 0).
    """
    return ORIGIN.copy()


def as_vec3(
    value: np.ndarray | Iterable[float],
    name: str = "value",
) -> np.ndarray:
    """
    Public safe conversion helper.
    """
    return _ensure_vec3(
        value,
        name,
    ).copy()


# ============================================================
# Distance and magnitude
# ============================================================

def distance(
    p1: np.ndarray | Iterable[float],
    p2: np.ndarray | Iterable[float],
) -> float:
    """
    Euclidean distance between two points.
    """
    p1_vec = _ensure_vec3(
        p1,
        "p1",
    )
    p2_vec = _ensure_vec3(
        p2,
        "p2",
    )

    return float(
        np.linalg.norm(
            p2_vec - p1_vec,
        )
    )


def squared_distance(
    p1: np.ndarray | Iterable[float],
    p2: np.ndarray | Iterable[float],
) -> float:
    """
    Squared Euclidean distance between two points.

    Useful when comparing distances without needing sqrt.
    """
    p1_vec = _ensure_vec3(
        p1,
        "p1",
    )
    p2_vec = _ensure_vec3(
        p2,
        "p2",
    )

    delta = p2_vec - p1_vec

    return float(
        np.dot(
            delta,
            delta,
        )
    )


def magnitude(
    value: np.ndarray | Iterable[float],
) -> float:
    """
    Length of a vector.
    """
    value_vec = _ensure_vec3(
        value,
        "value",
    )

    return float(
        np.linalg.norm(value_vec)
    )


def squared_magnitude(
    value: np.ndarray | Iterable[float],
) -> float:
    """
    Squared length of a vector.
    """
    value_vec = _ensure_vec3(
        value,
        "value",
    )

    return float(
        np.dot(
            value_vec,
            value_vec,
        )
    )


# ============================================================
# Direction and normalization
# ============================================================

def normalize(
    value: np.ndarray | Iterable[float],
) -> np.ndarray:
    """
    Return unit vector in the direction of value.

    If vector is near zero, return zero vector.
    """
    value_vec = _ensure_vec3(
        value,
        "value",
    )

    norm = np.linalg.norm(value_vec)

    if norm < EPSILON:
        return zero_vector()

    return value_vec / norm


def direction(
    p1: np.ndarray | Iterable[float],
    p2: np.ndarray | Iterable[float],
) -> np.ndarray:
    """
    Unit direction vector from p1 to p2.
    """
    p1_vec = _ensure_vec3(
        p1,
        "p1",
    )
    p2_vec = _ensure_vec3(
        p2,
        "p2",
    )

    return normalize(
        p2_vec - p1_vec,
    )


def vector_between(
    p1: np.ndarray | Iterable[float],
    p2: np.ndarray | Iterable[float],
) -> np.ndarray:
    """
    Raw vector from p1 to p2.
    """
    p1_vec = _ensure_vec3(
        p1,
        "p1",
    )
    p2_vec = _ensure_vec3(
        p2,
        "p2",
    )

    return p2_vec - p1_vec


# ============================================================
# Midpoint and interpolation
# ============================================================

def midpoint(
    p1: np.ndarray | Iterable[float],
    p2: np.ndarray | Iterable[float],
) -> np.ndarray:
    """
    Midpoint between two points.
    """
    p1_vec = _ensure_vec3(
        p1,
        "p1",
    )
    p2_vec = _ensure_vec3(
        p2,
        "p2",
    )

    return (p1_vec + p2_vec) * 0.5


def lerp(
    p1: np.ndarray | Iterable[float],
    p2: np.ndarray | Iterable[float],
    t: float,
) -> np.ndarray:
    """
    Linear interpolation between p1 and p2.

    t = 0 -> p1
    t = 1 -> p2
    """
    p1_vec = _ensure_vec3(
        p1,
        "p1",
    )
    p2_vec = _ensure_vec3(
        p2,
        "p2",
    )
    t_value = _ensure_t(t)

    return p1_vec + (p2_vec - p1_vec) * t_value


def clamp(
    value: float,
    min_value: float,
    max_value: float,
) -> float:
    """
    Clamp a numeric value between min_value and max_value.
    """
    value = _ensure_numeric(
        value,
        "value",
    )
    min_value = _ensure_numeric(
        min_value,
        "min_value",
    )
    max_value = _ensure_numeric(
        max_value,
        "max_value",
    )

    if min_value > max_value:
        raise ValueError(
            "min_value must be <= max_value"
        )

    return max(
        min_value,
        min(
            max_value,
            value,
        ),
    )


def clamp01(
    value: float,
) -> float:
    """
    Clamp a numeric value to [0, 1].
    """
    return clamp(
        value,
        0.0,
        1.0,
    )


def lerp_clamped(
    p1: np.ndarray | Iterable[float],
    p2: np.ndarray | Iterable[float],
    t: float,
) -> np.ndarray:
    """
    Linear interpolation with t clamped to [0, 1].
    """
    return lerp(
        p1,
        p2,
        clamp01(t),
    )


# ============================================================
# Angle utilities
# ============================================================

def angle_of_vector(
    value: np.ndarray | Iterable[float],
) -> float:
    """
    Angle of vector in the x-y plane, in radians.
    """
    value_vec = _ensure_vec3(
        value,
        "value",
    )

    return float(
        atan2(
            value_vec[1],
            value_vec[0],
        )
    )


def angle_between(
    v1: np.ndarray | Iterable[float],
    v2: np.ndarray | Iterable[float],
) -> float:
    """
    Angle between two vectors, in radians.
    """
    v1_unit = normalize(v1)
    v2_unit = normalize(v2)

    if is_zero(v1_unit) or is_zero(v2_unit):
        return 0.0

    dot_value = np.clip(
        np.dot(
            v1_unit,
            v2_unit,
        ),
        -1.0,
        1.0,
    )

    return float(
        np.arccos(dot_value)
    )


def angle_to_degrees(
    angle_radians: float,
) -> float:
    """
    Convert radians to degrees.
    """
    return float(
        degrees(
            _ensure_numeric(
                angle_radians,
                "angle_radians",
            )
        )
    )


def degrees_to_angle(
    angle_degrees: float,
) -> float:
    """
    Convert degrees to radians.
    """
    return float(
        radians(
            _ensure_numeric(
                angle_degrees,
                "angle_degrees",
            )
        )
    )


# ============================================================
# Rotation
# ============================================================

def rotate_point(
    p: np.ndarray | Iterable[float],
    angle: float,
) -> np.ndarray:
    """
    Rotate a point around the origin in the x-y plane.
    """
    p_vec = _ensure_vec3(
        p,
        "p",
    )
    angle_value = _ensure_numeric(
        angle,
        "angle",
    )

    x_value = p_vec[0]
    y_value = p_vec[1]
    z_value = p_vec[2]

    new_x = x_value * cos(angle_value) - y_value * sin(angle_value)
    new_y = x_value * sin(angle_value) + y_value * cos(angle_value)

    return point(
        new_x,
        new_y,
        z_value,
    )


def rotate_vector(
    value: np.ndarray | Iterable[float],
    angle: float,
) -> np.ndarray:
    """
    Rotate a vector around the origin in the x-y plane.
    """
    return rotate_point(
        value,
        angle,
    )


def rotate_point_about(
    p: np.ndarray | Iterable[float],
    center: np.ndarray | Iterable[float],
    angle: float,
) -> np.ndarray:
    """
    Rotate a point around a given center.
    """
    p_vec = _ensure_vec3(
        p,
        "p",
    )
    center_vec = _ensure_vec3(
        center,
        "center",
    )

    shifted = p_vec - center_vec
    rotated = rotate_point(
        shifted,
        angle,
    )

    return rotated + center_vec


# ============================================================
# Offset and movement helpers
# ============================================================

def offset(
    p: np.ndarray | Iterable[float],
    dx: float,
    dy: float,
    dz: float = 0.0,
) -> np.ndarray:
    """
    Return a new point offset by dx, dy, dz.
    """
    p_vec = _ensure_vec3(
        p,
        "p",
    )

    return point(
        p_vec[0] + _ensure_numeric(dx, "dx"),
        p_vec[1] + _ensure_numeric(dy, "dy"),
        p_vec[2] + _ensure_numeric(dz, "dz"),
    )


def add_vector(
    p: np.ndarray | Iterable[float],
    value: np.ndarray | Iterable[float],
) -> np.ndarray:
    """
    Add a vector to a point.
    """
    p_vec = _ensure_vec3(
        p,
        "p",
    )
    value_vec = _ensure_vec3(
        value,
        "value",
    )

    return p_vec + value_vec


def subtract_vector(
    p: np.ndarray | Iterable[float],
    value: np.ndarray | Iterable[float],
) -> np.ndarray:
    """
    Subtract a vector from a point.
    """
    p_vec = _ensure_vec3(
        p,
        "p",
    )
    value_vec = _ensure_vec3(
        value,
        "value",
    )

    return p_vec - value_vec


def move_towards(
    p: np.ndarray | Iterable[float],
    target: np.ndarray | Iterable[float],
    dist: float,
) -> np.ndarray:
    """
    Move point p towards target by a fixed distance.

    If p and target are the same, p is returned unchanged.
    """
    p_vec = _ensure_vec3(
        p,
        "p",
    )
    target_vec = _ensure_vec3(
        target,
        "target",
    )
    dist_value = _ensure_numeric(
        dist,
        "dist",
    )

    if dist_value < 0:
        raise ValueError(
            f"dist must be >= 0, got {dist_value}"
        )

    dir_vec = direction(
        p_vec,
        target_vec,
    )

    if is_zero(dir_vec):
        return p_vec.copy()

    return p_vec + dir_vec * dist_value


# ============================================================
# Axis helpers
# ============================================================

def along_x(
    p: np.ndarray | Iterable[float],
    amount: float,
) -> np.ndarray:
    """
    Offset point along x axis.
    """
    return offset(
        p,
        amount,
        0.0,
        0.0,
    )


def along_y(
    p: np.ndarray | Iterable[float],
    amount: float,
) -> np.ndarray:
    """
    Offset point along y axis.
    """
    return offset(
        p,
        0.0,
        amount,
        0.0,
    )


def along_z(
    p: np.ndarray | Iterable[float],
    amount: float,
) -> np.ndarray:
    """
    Offset point along z axis.
    """
    return offset(
        p,
        0.0,
        0.0,
        amount,
    )


def x_only(
    value: np.ndarray | Iterable[float],
) -> np.ndarray:
    """
    Keep only x component.
    """
    value_vec = _ensure_vec3(
        value,
        "value",
    )

    return point(
        value_vec[0],
        0.0,
        0.0,
    )


def y_only(
    value: np.ndarray | Iterable[float],
) -> np.ndarray:
    """
    Keep only y component.
    """
    value_vec = _ensure_vec3(
        value,
        "value",
    )

    return point(
        0.0,
        value_vec[1],
        0.0,
    )


def z_only(
    value: np.ndarray | Iterable[float],
) -> np.ndarray:
    """
    Keep only z component.
    """
    value_vec = _ensure_vec3(
        value,
        "value",
    )

    return point(
        0.0,
        0.0,
        value_vec[2],
    )


# ============================================================
# Scaling
# ============================================================

def scale_point(
    p: np.ndarray | Iterable[float],
    factor: float,
    center: Optional[np.ndarray | Iterable[float]] = None,
) -> np.ndarray:
    """
    Scale a point relative to a center.
    """
    p_vec = _ensure_vec3(
        p,
        "p",
    )
    factor_value = _ensure_numeric(
        factor,
        "factor",
    )

    if center is None:
        center_vec = zero_point()
    else:
        center_vec = _ensure_vec3(
            center,
            "center",
        )

    return center_vec + (p_vec - center_vec) * factor_value


def scale_vector(
    value: np.ndarray | Iterable[float],
    factor: float,
) -> np.ndarray:
    """
    Scale a vector by a numeric factor.
    """
    value_vec = _ensure_vec3(
        value,
        "value",
    )
    factor_value = _ensure_numeric(
        factor,
        "factor",
    )

    return value_vec * factor_value


# ============================================================
# Local / world helpers
# ============================================================

def local_to_world(
    local_point: np.ndarray | Iterable[float],
    parent_world_point: np.ndarray | Iterable[float],
) -> np.ndarray:
    """
    Convert a local point into world space using parent world position.

    This is intentionally simple:
        world = parent_world + local

    More advanced rotation/scale transforms belong in transforms.py.
    """
    local_vec = _ensure_vec3(
        local_point,
        "local_point",
    )
    parent_vec = _ensure_vec3(
        parent_world_point,
        "parent_world_point",
    )

    return parent_vec + local_vec


def world_to_local(
    world_point: np.ndarray | Iterable[float],
    parent_world_point: np.ndarray | Iterable[float],
) -> np.ndarray:
    """
    Convert a world point into local space using parent world position.

    This is intentionally simple:
        local = world - parent_world

    More advanced rotation/scale transforms belong in transforms.py.
    """
    world_vec = _ensure_vec3(
        world_point,
        "world_point",
    )
    parent_vec = _ensure_vec3(
        parent_world_point,
        "parent_world_point",
    )

    return world_vec - parent_vec


# ============================================================
# Utility checks
# ============================================================

def is_close(
    p1: np.ndarray | Iterable[float],
    p2: np.ndarray | Iterable[float],
    tol: float = 1e-6,
) -> bool:
    """
    Check if two points are approximately equal.
    """
    tol_value = _ensure_numeric(
        tol,
        "tol",
    )

    if tol_value < 0:
        raise ValueError(
            f"tol must be >= 0, got {tol_value}"
        )

    return distance(
        p1,
        p2,
    ) <= tol_value


def is_zero(
    value: np.ndarray | Iterable[float],
    tol: float = EPSILON,
) -> bool:
    """
    Check if vector is approximately zero.
    """
    tol_value = _ensure_numeric(
        tol,
        "tol",
    )

    if tol_value < 0:
        raise ValueError(
            f"tol must be >= 0, got {tol_value}"
        )

    return magnitude(value) <= tol_value


def nearly_equal(
    a: float,
    b: float,
    tol: float = EPSILON,
) -> bool:
    """
    Check if two numeric values are approximately equal.
    """
    a_value = _ensure_numeric(
        a,
        "a",
    )
    b_value = _ensure_numeric(
        b,
        "b",
    )
    tol_value = _ensure_numeric(
        tol,
        "tol",
    )

    if tol_value < 0:
        raise ValueError(
            f"tol must be >= 0, got {tol_value}"
        )

    return abs(a_value - b_value) <= tol_value


# ============================================================
# Export control
# ============================================================

__all__ = [
    "EPSILON",
    "ORIGIN",
    "UNIT_X",
    "UNIT_Y",
    "UNIT_Z",
    "point",
    "vec",
    "zero_point",
    "zero_vector",
    "as_vec3",
    "distance",
    "squared_distance",
    "magnitude",
    "squared_magnitude",
    "normalize",
    "direction",
    "vector_between",
    "midpoint",
    "lerp",
    "clamp",
    "clamp01",
    "lerp_clamped",
    "angle_of_vector",
    "angle_between",
    "angle_to_degrees",
    "degrees_to_angle",
    "rotate_point",
    "rotate_vector",
    "rotate_point_about",
    "offset",
    "add_vector",
    "subtract_vector",
    "move_towards",
    "along_x",
    "along_y",
    "along_z",
    "x_only",
    "y_only",
    "z_only",
    "scale_point",
    "scale_vector",
    "local_to_world",
    "world_to_local",
    "is_close",
    "is_zero",
    "nearly_equal",
]