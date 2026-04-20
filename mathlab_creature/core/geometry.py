"""
Geometry helper utilities for mathlab-mylinehub-creature.

This module provides small, reusable math helpers for working with:
- points
- vectors
- distances
- interpolation
- rotations

Design goals:
- simple and explicit
- safe for repeated use
- numerically stable
- compatible with Manim-style workflows
"""

from __future__ import annotations

import numpy as np
from math import cos, sin, atan2
from typing import Optional


# ============================================================
# Constants
# ============================================================

EPSILON = 1e-8


# ============================================================
# Internal validation helpers
# ============================================================

def _ensure_vec3(v: np.ndarray, name: str = "vector") -> np.ndarray:
    """
    Ensure input is a 3D numpy vector.
    """
    if not isinstance(v, np.ndarray):
        raise TypeError(f"{name} must be a numpy.ndarray")
    if v.shape != (3,):
        raise ValueError(f"{name} must be shape (3,), got {v.shape}")
    return v.astype(float)


# ============================================================
# Basic point / vector creation
# ============================================================

def point(x: float, y: float, z: float = 0.0) -> np.ndarray:
    """
    Create a 3D point (Manim-compatible).
    """
    return np.array([float(x), float(y), float(z)], dtype=float)


def zero_point() -> np.ndarray:
    """
    Origin point (0, 0, 0).
    """
    return np.zeros(3, dtype=float)


# ============================================================
# Distance and magnitude
# ============================================================

def distance(p1: np.ndarray, p2: np.ndarray) -> float:
    """
    Euclidean distance between two points.
    """
    p1 = _ensure_vec3(p1, "p1")
    p2 = _ensure_vec3(p2, "p2")
    return float(np.linalg.norm(p2 - p1))


def magnitude(v: np.ndarray) -> float:
    """
    Length of a vector.
    """
    v = _ensure_vec3(v)
    return float(np.linalg.norm(v))


# ============================================================
# Direction and normalization
# ============================================================

def normalize(v: np.ndarray) -> np.ndarray:
    """
    Return unit vector in direction of v.
    If vector is near zero, return zero vector.
    """
    v = _ensure_vec3(v)
    norm = np.linalg.norm(v)

    if norm < EPSILON:
        return zero_point()

    return v / norm


def direction(p1: np.ndarray, p2: np.ndarray) -> np.ndarray:
    """
    Unit direction vector from p1 to p2.
    """
    return normalize(_ensure_vec3(p2) - _ensure_vec3(p1))


# ============================================================
# Midpoint and interpolation
# ============================================================

def midpoint(p1: np.ndarray, p2: np.ndarray) -> np.ndarray:
    """
    Midpoint between two points.
    """
    p1 = _ensure_vec3(p1)
    p2 = _ensure_vec3(p2)
    return (p1 + p2) * 0.5


def lerp(p1: np.ndarray, p2: np.ndarray, t: float) -> np.ndarray:
    """
    Linear interpolation between p1 and p2.

    t = 0 → p1
    t = 1 → p2
    """
    p1 = _ensure_vec3(p1)
    p2 = _ensure_vec3(p2)
    return p1 + (p2 - p1) * float(t)


# ============================================================
# Angle utilities
# ============================================================

def angle_of_vector(v: np.ndarray) -> float:
    """
    Angle of vector in 2D (x-y plane).
    """
    v = _ensure_vec3(v)
    return float(atan2(v[1], v[0]))


def angle_between(v1: np.ndarray, v2: np.ndarray) -> float:
    """
    Angle between two vectors (in radians).
    """
    v1 = normalize(v1)
    v2 = normalize(v2)

    dot = np.clip(np.dot(v1, v2), -1.0, 1.0)
    return float(np.arccos(dot))


# ============================================================
# Rotation
# ============================================================

def rotate_point(p: np.ndarray, angle: float) -> np.ndarray:
    """
    Rotate a point around origin in 2D (x-y plane).
    """
    p = _ensure_vec3(p)
    x, y, z = p

    new_x = x * cos(angle) - y * sin(angle)
    new_y = x * sin(angle) + y * cos(angle)

    return point(new_x, new_y, z)


def rotate_point_about(p: np.ndarray, center: np.ndarray, angle: float) -> np.ndarray:
    """
    Rotate a point around a given center.
    """
    p = _ensure_vec3(p)
    center = _ensure_vec3(center)

    shifted = p - center
    rotated = rotate_point(shifted, angle)

    return rotated + center


# ============================================================
# Offset and movement
# ============================================================

def offset(p: np.ndarray, dx: float, dy: float, dz: float = 0.0) -> np.ndarray:
    """
    Move a point by dx, dy, dz.
    """
    p = _ensure_vec3(p)
    return point(p[0] + dx, p[1] + dy, p[2] + dz)


def move_towards(p: np.ndarray, target: np.ndarray, dist: float) -> np.ndarray:
    """
    Move point p towards target by a fixed distance.
    """
    p = _ensure_vec3(p)
    target = _ensure_vec3(target)

    dir_vec = direction(p, target)
    return p + dir_vec * float(dist)


# ============================================================
# Axis helpers
# ============================================================

def along_x(p: np.ndarray, amount: float) -> np.ndarray:
    return offset(p, amount, 0.0, 0.0)


def along_y(p: np.ndarray, amount: float) -> np.ndarray:
    return offset(p, 0.0, amount, 0.0)


def along_z(p: np.ndarray, amount: float) -> np.ndarray:
    return offset(p, 0.0, 0.0, amount)


# ============================================================
# Scaling
# ============================================================

def scale_point(
    p: np.ndarray,
    factor: float,
    center: Optional[np.ndarray] = None,
) -> np.ndarray:
    """
    Scale a point relative to a center.
    """
    p = _ensure_vec3(p)

    if center is None:
        center = zero_point()
    else:
        center = _ensure_vec3(center)

    return center + (p - center) * float(factor)


# ============================================================
# Utility checks
# ============================================================

def is_close(p1: np.ndarray, p2: np.ndarray, tol: float = 1e-6) -> bool:
    """
    Check if two points are approximately equal.
    """
    return distance(p1, p2) < tol


def is_zero(v: np.ndarray, tol: float = 1e-8) -> bool:
    """
    Check if vector is approximately zero.
    """
    return magnitude(v) < tol