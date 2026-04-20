"""
Motion helper utilities for mathlab-mylinehub-creature.

This file contains reusable helpers for:
- interpolation
- easing curves
- simple animation path generation
- timing curves
- small motion utilities

These helpers do NOT replace Manim animations.
They support them by providing math and reusable motion patterns.
"""

from __future__ import annotations

import numpy as np
from math import cos, pi, sin

from mathlab_creature.core.geometry import lerp
from mathlab_creature.core.geometry import normalize
from mathlab_creature.core.geometry import point


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


def _validate_non_negative(name: str, value: float | int) -> float:
    """
    Ensure a non-negative numeric value.
    """
    value = _validate_numeric(name, value)
    if value < 0:
        raise ValueError(f"{name} must be >= 0, got {value}")
    return value


def _validate_positive_int(name: str, value: int) -> int:
    """
    Ensure a positive integer.
    """
    if not isinstance(value, int):
        raise TypeError(f"{name} must be an int, got {type(value).__name__}")
    if value <= 0:
        raise ValueError(f"{name} must be > 0, got {value}")
    return value


def clamp_01(t: float) -> float:
    """
    Clamp value to [0, 1].
    """
    t = _validate_numeric("t", t)
    return max(0.0, min(1.0, t))


def _prepare_t(t: float, clamp: bool = True) -> float:
    """
    Normalize easing input handling.

    Most motion helpers should operate on t in [0, 1].
    """
    t = _validate_numeric("t", t)
    return clamp_01(t) if clamp else t


# ============================================================
# Basic interpolation helpers
# ============================================================

def interpolate_points(
    p1: np.ndarray,
    p2: np.ndarray,
    t: float,
    clamp: bool = True,
) -> np.ndarray:
    """
    Interpolate between two points.

    By default, t is clamped to [0, 1].
    """
    t = _prepare_t(t, clamp=clamp)
    return lerp(p1, p2, t)


def interpolate_scalar(
    a: float,
    b: float,
    t: float,
    clamp: bool = True,
) -> float:
    """
    Interpolate between two scalar values.

    By default, t is clamped to [0, 1].
    """
    a = _validate_numeric("a", a)
    b = _validate_numeric("b", b)
    t = _prepare_t(t, clamp=clamp)
    return a + (b - a) * t


# ============================================================
# Easing functions (0 → 1 input, 0 → 1 output)
# ============================================================

def ease_linear(t: float) -> float:
    """
    Linear easing.
    """
    return _prepare_t(t)


def ease_in(t: float) -> float:
    """
    Starts slow, accelerates.
    """
    t = _prepare_t(t)
    return t * t


def ease_out(t: float) -> float:
    """
    Starts fast, slows down.
    """
    t = _prepare_t(t)
    return 1.0 - (1.0 - t) * (1.0 - t)


def ease_in_out(t: float) -> float:
    """
    Smooth acceleration and deceleration.
    """
    t = _prepare_t(t)
    return 3.0 * t * t - 2.0 * t * t * t


def ease_sine(t: float) -> float:
    """
    Smooth sine-based easing.
    """
    t = _prepare_t(t)
    return 0.5 * (1.0 - cos(pi * t))


def ease_in_cubic(t: float) -> float:
    """
    Stronger ease-in.
    """
    t = _prepare_t(t)
    return t * t * t


def ease_out_cubic(t: float) -> float:
    """
    Stronger ease-out.
    """
    t = _prepare_t(t)
    return 1.0 - (1.0 - t) ** 3


def ease_in_out_sine(t: float) -> float:
    """
    Very smooth sine-based in-out easing.
    """
    t = _prepare_t(t)
    return -(cos(pi * t) - 1.0) / 2.0


# ============================================================
# Time normalization helpers
# ============================================================

def normalize_time(
    current_time: float,
    total_time: float,
) -> float:
    """
    Normalize time into range [0, 1].

    If total_time <= 0, return 0.0.
    """
    current_time = _validate_numeric("current_time", current_time)
    total_time = _validate_numeric("total_time", total_time)

    if total_time <= 0:
        return 0.0

    return clamp_01(current_time / total_time)


def progress_steps(steps: int) -> list[float]:
    """
    Return evenly spaced normalized progress values from 0 to 1 inclusive.

    Example:
        steps=4 -> [0.0, 0.25, 0.5, 0.75, 1.0]
    """
    steps = _validate_positive_int("steps", steps)
    return [i / steps for i in range(steps + 1)]


# ============================================================
# Shared stepped path generation
# ============================================================

def _sample_motion(
    steps: int,
    easing_func,
) -> list[float]:
    """
    Generate eased t-samples from 0 to 1 inclusive.
    """
    steps = _validate_positive_int("steps", steps)

    samples: list[float] = []
    for raw_t in progress_steps(steps):
        eased_t = easing_func(raw_t)
        samples.append(clamp_01(eased_t))
    return samples


# ============================================================
# Path generators
# ============================================================

def straight_path(
    start: np.ndarray,
    end: np.ndarray,
    steps: int = 20,
    easing_func=ease_linear,
) -> list[np.ndarray]:
    """
    Generate a list of points along a straight path.
    """
    return [
        interpolate_points(start, end, t)
        for t in _sample_motion(steps, easing_func)
    ]


def arc_path(
    center: np.ndarray,
    radius: float,
    start_angle: float,
    end_angle: float,
    steps: int = 20,
) -> list[np.ndarray]:
    """
    Generate a circular arc path in the XY plane.
    """
    center = np.array(center, dtype=float)
    radius = _validate_non_negative("radius", radius)
    steps = _validate_positive_int("steps", steps)
    start_angle = _validate_numeric("start_angle", start_angle)
    end_angle = _validate_numeric("end_angle", end_angle)

    points: list[np.ndarray] = []

    for raw_t in progress_steps(steps):
        angle = start_angle + (end_angle - start_angle) * raw_t
        x = center[0] + radius * cos(angle)
        y = center[1] + radius * sin(angle)
        z = center[2]
        points.append(point(x, y, z))

    return points


def wave_path(
    start: np.ndarray,
    end: np.ndarray,
    amplitude: float = 0.2,
    steps: int = 20,
    easing_func=ease_linear,
) -> list[np.ndarray]:
    """
    Generate a wavy path between start and end.

    The base path is straight, with sinusoidal offset added on Y.
    Useful later for playful or expressive motion.
    """
    amplitude = _validate_non_negative("amplitude", amplitude)
    steps = _validate_positive_int("steps", steps)

    result: list[np.ndarray] = []
    for raw_t in progress_steps(steps):
        eased_t = easing_func(raw_t)
        base = interpolate_points(start, end, eased_t)
        y_offset = amplitude * sin(2.0 * pi * raw_t)
        result.append(point(base[0], base[1] + y_offset, base[2]))

    return result


# ============================================================
# Motion patterns
# ============================================================

def bobbing_offset(
    t: float,
    amplitude: float = 0.1,
    cycles: float = 1.0,
) -> float:
    """
    Vertical bobbing motion based on a sine wave.
    """
    t = _prepare_t(t)
    amplitude = _validate_non_negative("amplitude", amplitude)
    cycles = _validate_non_negative("cycles", cycles)

    return amplitude * sin(2.0 * pi * cycles * t)


def pulse_scale(
    t: float,
    base_scale: float = 1.0,
    amplitude: float = 0.1,
    cycles: float = 1.0,
) -> float:
    """
    Scale oscillation around a base scale.
    """
    t = _prepare_t(t)
    base_scale = _validate_numeric("base_scale", base_scale)
    amplitude = _validate_non_negative("amplitude", amplitude)
    cycles = _validate_non_negative("cycles", cycles)

    return base_scale + amplitude * sin(2.0 * pi * cycles * t)


def oscillate(
    t: float,
    min_val: float,
    max_val: float,
    cycles: float = 1.0,
) -> float:
    """
    Oscillate smoothly between two values.
    """
    t = _prepare_t(t)
    min_val = _validate_numeric("min_val", min_val)
    max_val = _validate_numeric("max_val", max_val)
    cycles = _validate_non_negative("cycles", cycles)

    low = min(min_val, max_val)
    high = max(min_val, max_val)

    mid = (low + high) / 2.0
    amp = (high - low) / 2.0

    return mid + amp * sin(2.0 * pi * cycles * t)


def damped_oscillation(
    t: float,
    amplitude: float = 1.0,
    damping: float = 3.0,
    cycles: float = 2.0,
) -> float:
    """
    Oscillation with simple exponential-like damping feel.

    This is useful later for reactions like:
    - settling after hop
    - hat wobble
    - pointer recoil
    """
    t = _prepare_t(t)
    amplitude = _validate_non_negative("amplitude", amplitude)
    damping = _validate_non_negative("damping", damping)
    cycles = _validate_non_negative("cycles", cycles)

    decay = np.exp(-damping * t)
    return amplitude * decay * sin(2.0 * pi * cycles * t)


# ============================================================
# Direction-based movement
# ============================================================

def move_along_direction(
    start: np.ndarray,
    direction_vector: np.ndarray,
    distance: float,
) -> np.ndarray:
    """
    Move from start in a given direction.
    """
    start = np.array(start, dtype=float)
    distance = _validate_numeric("distance", distance)

    dir_norm = normalize(np.array(direction_vector, dtype=float))
    return start + dir_norm * distance


def look_at_direction(
    origin: np.ndarray,
    target: np.ndarray,
) -> np.ndarray:
    """
    Return normalized direction vector from origin to target.
    """
    origin = np.array(origin, dtype=float)
    target = np.array(target, dtype=float)
    return normalize(target - origin)


# ============================================================
# Step-based motion helpers
# ============================================================

def step_positions(
    start: np.ndarray,
    end: np.ndarray,
    steps: int,
    easing_func=ease_in_out,
) -> list[np.ndarray]:
    """
    Generate step-by-step positions for controlled motion.
    """
    return straight_path(
        start=start,
        end=end,
        steps=steps,
        easing_func=easing_func,
    )


def scalar_steps(
    start: float,
    end: float,
    steps: int,
    easing_func=ease_in_out,
) -> list[float]:
    """
    Generate eased scalar values from start to end.
    """
    start = _validate_numeric("start", start)
    end = _validate_numeric("end", end)

    return [
        interpolate_scalar(start, end, t)
        for t in _sample_motion(steps, easing_func)
    ]