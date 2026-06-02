"""
Motion helper utilities for mathlab-mylinehub-creature.

This file contains reusable helpers for:
- interpolation
- easing curves
- simple animation path generation
- timing curves
- small motion utilities
- creature-style root/body motion patterns

Architecture rule:
- motion.py returns numeric values and points only
- motion.py does not create Manim animations directly
- motion.py does not move creature parts directly
- motion.py does not contain audio logic
- audio remains separate and may later be triggered by actions

These helpers support action files such as:
- idle_action.py
- walk_action.py
- step_action.py
- turn_action.py
- wave_action.py
- point_action.py
- hop_action.py
"""

from __future__ import annotations

from collections.abc import Callable
from math import cos
from math import pi
from math import sin
from typing import Iterable

import numpy as np

from mathlab_creature.core.geometry import angle_of_vector
from mathlab_creature.core.geometry import as_vec3
from mathlab_creature.core.geometry import clamp01
from mathlab_creature.core.geometry import direction
from mathlab_creature.core.geometry import lerp
from mathlab_creature.core.geometry import normalize
from mathlab_creature.core.geometry import point


# ============================================================
# Type aliases
# ============================================================

Vec3Like = np.ndarray | Iterable[float]
EasingFunction = Callable[[float], float]


# ============================================================
# Internal helpers
# ============================================================

def _validate_numeric(
    name: str,
    value: float | int,
) -> float:
    """
    Ensure a numeric value and return it as float.
    """
    if not isinstance(value, (int, float)):
        raise TypeError(
            f"{name} must be numeric, got {type(value).__name__}"
        )

    return float(value)


def _validate_non_negative(
    name: str,
    value: float | int,
) -> float:
    """
    Ensure a non-negative numeric value.
    """
    value = _validate_numeric(
        name,
        value,
    )

    if value < 0:
        raise ValueError(
            f"{name} must be >= 0, got {value}"
        )

    return value


def _validate_positive_int(
    name: str,
    value: int,
) -> int:
    """
    Ensure a positive integer.
    """
    if not isinstance(value, int):
        raise TypeError(
            f"{name} must be an int, got {type(value).__name__}"
        )

    if value <= 0:
        raise ValueError(
            f"{name} must be > 0, got {value}"
        )

    return value


def _prepare_t(
    t: float,
    clamp: bool = True,
) -> float:
    """
    Normalize easing input handling.

    Most motion helpers should operate on t in [0, 1].
    """
    t_value = _validate_numeric(
        "t",
        t,
    )

    if clamp:
        return clamp_01(t_value)

    return t_value


def _coerce_point(
    value: Vec3Like,
    name: str = "point",
) -> np.ndarray:
    """
    Normalize incoming point-like data.
    """
    return as_vec3(
        value,
        name=name,
    )


# ============================================================
# Basic clamp / interpolation helpers
# ============================================================

def clamp_01(
    t: float,
) -> float:
    """
    Clamp value to [0, 1].
    """
    return clamp01(
        _validate_numeric(
            "t",
            t,
        )
    )


def interpolate_points(
    p1: Vec3Like,
    p2: Vec3Like,
    t: float,
    clamp: bool = True,
) -> np.ndarray:
    """
    Interpolate between two points.

    By default, t is clamped to [0, 1].
    """
    t_value = _prepare_t(
        t,
        clamp=clamp,
    )

    return lerp(
        _coerce_point(p1, "p1"),
        _coerce_point(p2, "p2"),
        t_value,
    )


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
    a_value = _validate_numeric(
        "a",
        a,
    )
    b_value = _validate_numeric(
        "b",
        b,
    )
    t_value = _prepare_t(
        t,
        clamp=clamp,
    )

    return a_value + (b_value - a_value) * t_value


# ============================================================
# Easing functions
# ============================================================

def ease_linear(
    t: float,
) -> float:
    """
    Linear easing.
    """
    return _prepare_t(t)


def ease_in(
    t: float,
) -> float:
    """
    Starts slow, accelerates.
    """
    t = _prepare_t(t)

    return t * t


def ease_out(
    t: float,
) -> float:
    """
    Starts fast, slows down.
    """
    t = _prepare_t(t)

    return 1.0 - (1.0 - t) * (1.0 - t)


def ease_in_out(
    t: float,
) -> float:
    """
    Smooth acceleration and deceleration.
    """
    t = _prepare_t(t)

    return 3.0 * t * t - 2.0 * t * t * t


def ease_sine(
    t: float,
) -> float:
    """
    Smooth sine-based easing.
    """
    t = _prepare_t(t)

    return 0.5 * (1.0 - cos(pi * t))


def ease_in_cubic(
    t: float,
) -> float:
    """
    Stronger ease-in.
    """
    t = _prepare_t(t)

    return t * t * t


def ease_out_cubic(
    t: float,
) -> float:
    """
    Stronger ease-out.
    """
    t = _prepare_t(t)

    return 1.0 - (1.0 - t) ** 3


def ease_in_out_sine(
    t: float,
) -> float:
    """
    Very smooth sine-based in-out easing.
    """
    t = _prepare_t(t)

    return -(cos(pi * t) - 1.0) / 2.0


def ease_out_back(
    t: float,
    overshoot: float = 1.70158,
) -> float:
    """
    Ease-out with a small overshoot.

    Useful for playful creature gestures.
    """
    t = _prepare_t(t)
    overshoot = _validate_numeric(
        "overshoot",
        overshoot,
    )

    shifted = t - 1.0

    return 1.0 + (overshoot + 1.0) * shifted**3 + overshoot * shifted**2


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
    current_time = _validate_numeric(
        "current_time",
        current_time,
    )
    total_time = _validate_numeric(
        "total_time",
        total_time,
    )

    if total_time <= 0:
        return 0.0

    return clamp_01(
        current_time / total_time,
    )


def progress_steps(
    steps: int,
) -> list[float]:
    """
    Return evenly spaced normalized progress values from 0 to 1 inclusive.

    Example:
        steps=4 -> [0.0, 0.25, 0.5, 0.75, 1.0]
    """
    steps = _validate_positive_int(
        "steps",
        steps,
    )

    return [
        i / steps
        for i in range(steps + 1)
    ]


def sample_eased_progress(
    steps: int,
    easing_func: EasingFunction = ease_linear,
) -> list[float]:
    """
    Generate eased t-samples from 0 to 1 inclusive.
    """
    steps = _validate_positive_int(
        "steps",
        steps,
    )

    samples: list[float] = []

    for raw_t in progress_steps(steps):
        eased_t = easing_func(raw_t)
        samples.append(
            clamp_01(eased_t)
        )

    return samples


# ============================================================
# Path generators
# ============================================================

def straight_path(
    start: Vec3Like,
    end: Vec3Like,
    steps: int = 20,
    easing_func: EasingFunction = ease_linear,
) -> list[np.ndarray]:
    """
    Generate a list of points along a straight path.
    """
    start_point = _coerce_point(
        start,
        "start",
    )
    end_point = _coerce_point(
        end,
        "end",
    )

    return [
        interpolate_points(
            start_point,
            end_point,
            t,
        )
        for t in sample_eased_progress(
            steps,
            easing_func,
        )
    ]


def arc_path(
    center: Vec3Like,
    radius: float,
    start_angle: float,
    end_angle: float,
    steps: int = 20,
    easing_func: EasingFunction = ease_linear,
) -> list[np.ndarray]:
    """
    Generate a circular arc path in the XY plane.
    """
    center_point = _coerce_point(
        center,
        "center",
    )
    radius = _validate_non_negative(
        "radius",
        radius,
    )
    start_angle = _validate_numeric(
        "start_angle",
        start_angle,
    )
    end_angle = _validate_numeric(
        "end_angle",
        end_angle,
    )

    points: list[np.ndarray] = []

    for raw_t in sample_eased_progress(
        steps,
        easing_func,
    ):
        angle = start_angle + (end_angle - start_angle) * raw_t
        x_value = center_point[0] + radius * cos(angle)
        y_value = center_point[1] + radius * sin(angle)
        z_value = center_point[2]

        points.append(
            point(
                x_value,
                y_value,
                z_value,
            )
        )

    return points


def wave_path(
    start: Vec3Like,
    end: Vec3Like,
    amplitude: float = 0.2,
    cycles: float = 1.0,
    steps: int = 20,
    easing_func: EasingFunction = ease_linear,
) -> list[np.ndarray]:
    """
    Generate a wavy path between start and end.

    The base path is straight, with sinusoidal offset added on Y.
    """
    start_point = _coerce_point(
        start,
        "start",
    )
    end_point = _coerce_point(
        end,
        "end",
    )
    amplitude = _validate_non_negative(
        "amplitude",
        amplitude,
    )
    cycles = _validate_non_negative(
        "cycles",
        cycles,
    )
    _validate_positive_int(
        "steps",
        steps,
    )

    result: list[np.ndarray] = []

    for raw_t in progress_steps(steps):
        eased_t = easing_func(raw_t)
        base = interpolate_points(
            start_point,
            end_point,
            eased_t,
        )
        y_offset = amplitude * sin(2.0 * pi * cycles * raw_t)

        result.append(
            point(
                base[0],
                base[1] + y_offset,
                base[2],
            )
        )

    return result


def hop_path(
    start: Vec3Like,
    end: Vec3Like,
    height: float = 0.35,
    steps: int = 20,
    easing_func: EasingFunction = ease_in_out,
) -> list[np.ndarray]:
    """
    Generate a simple hop arc from start to end.

    Useful for hop_action.py.
    """
    start_point = _coerce_point(
        start,
        "start",
    )
    end_point = _coerce_point(
        end,
        "end",
    )
    height = _validate_non_negative(
        "height",
        height,
    )

    result: list[np.ndarray] = []

    for raw_t in progress_steps(steps):
        eased_t = easing_func(raw_t)
        base = interpolate_points(
            start_point,
            end_point,
            eased_t,
        )
        y_offset = height * sin(pi * raw_t)

        result.append(
            point(
                base[0],
                base[1] + y_offset,
                base[2],
            )
        )

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
    amplitude = _validate_non_negative(
        "amplitude",
        amplitude,
    )
    cycles = _validate_non_negative(
        "cycles",
        cycles,
    )

    return amplitude * sin(2.0 * pi * cycles * t)


def breathing_scale(
    t: float,
    base_scale: float = 1.0,
    amplitude: float = 0.025,
    cycles: float = 1.0,
) -> float:
    """
    Small breathing-style scale around a base value.

    Useful for BodyCore idle motion.
    """
    return pulse_scale(
        t=t,
        base_scale=base_scale,
        amplitude=amplitude,
        cycles=cycles,
    )


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
    base_scale = _validate_numeric(
        "base_scale",
        base_scale,
    )
    amplitude = _validate_non_negative(
        "amplitude",
        amplitude,
    )
    cycles = _validate_non_negative(
        "cycles",
        cycles,
    )

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
    min_val = _validate_numeric(
        "min_val",
        min_val,
    )
    max_val = _validate_numeric(
        "max_val",
        max_val,
    )
    cycles = _validate_non_negative(
        "cycles",
        cycles,
    )

    low = min(
        min_val,
        max_val,
    )
    high = max(
        min_val,
        max_val,
    )

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
    Oscillation with simple exponential-like damping.

    Useful later for:
    - settling after hop
    - hat wobble
    - arm recoil
    - body core recovery
    """
    t = _prepare_t(t)
    amplitude = _validate_non_negative(
        "amplitude",
        amplitude,
    )
    damping = _validate_non_negative(
        "damping",
        damping,
    )
    cycles = _validate_non_negative(
        "cycles",
        cycles,
    )

    decay = np.exp(
        -damping * t,
    )

    return float(
        amplitude
        * decay
        * sin(2.0 * pi * cycles * t)
    )


def sway_offset(
    t: float,
    amplitude: float = 0.08,
    cycles: float = 1.0,
) -> float:
    """
    Horizontal sway value.

    Useful for BodyCore and walking balance.
    """
    t = _prepare_t(t)
    amplitude = _validate_non_negative(
        "amplitude",
        amplitude,
    )
    cycles = _validate_non_negative(
        "cycles",
        cycles,
    )

    return amplitude * sin(2.0 * pi * cycles * t)


def foot_lift_offset(
    t: float,
    height: float = 0.18,
) -> float:
    """
    Foot lift curve for walking/stepping.

    0 at start, rises in middle, returns to 0.
    """
    t = _prepare_t(t)
    height = _validate_non_negative(
        "height",
        height,
    )

    return height * sin(pi * t)


# ============================================================
# Direction-based movement
# ============================================================

def move_along_direction(
    start: Vec3Like,
    direction_vector: Vec3Like,
    distance: float,
) -> np.ndarray:
    """
    Move from start in a given direction.
    """
    start_point = _coerce_point(
        start,
        "start",
    )
    distance = _validate_numeric(
        "distance",
        distance,
    )

    dir_norm = normalize(
        _coerce_point(
            direction_vector,
            "direction_vector",
        )
    )

    return start_point + dir_norm * distance


def look_at_direction(
    origin: Vec3Like,
    target: Vec3Like,
) -> np.ndarray:
    """
    Return normalized direction vector from origin to target.
    """
    return direction(
        origin,
        target,
    )


def look_angle_to_target(
    origin: Vec3Like,
    target: Vec3Like,
) -> float:
    """
    Return x-y plane angle from origin to target.
    """
    dir_vec = look_at_direction(
        origin,
        target,
    )

    return angle_of_vector(
        dir_vec,
    )


# ============================================================
# Step-based motion helpers
# ============================================================

def step_positions(
    start: Vec3Like,
    end: Vec3Like,
    steps: int,
    easing_func: EasingFunction = ease_in_out,
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
    easing_func: EasingFunction = ease_in_out,
) -> list[float]:
    """
    Generate eased scalar values from start to end.
    """
    start = _validate_numeric(
        "start",
        start,
    )
    end = _validate_numeric(
        "end",
        end,
    )

    return [
        interpolate_scalar(
            start,
            end,
            t,
        )
        for t in sample_eased_progress(
            steps,
            easing_func,
        )
    ]


# ============================================================
# Export control
# ============================================================

__all__ = [
    "Vec3Like",
    "EasingFunction",
    "clamp_01",
    "interpolate_points",
    "interpolate_scalar",
    "ease_linear",
    "ease_in",
    "ease_out",
    "ease_in_out",
    "ease_sine",
    "ease_in_cubic",
    "ease_out_cubic",
    "ease_in_out_sine",
    "ease_out_back",
    "normalize_time",
    "progress_steps",
    "sample_eased_progress",
    "straight_path",
    "arc_path",
    "wave_path",
    "hop_path",
    "bobbing_offset",
    "breathing_scale",
    "pulse_scale",
    "oscillate",
    "damped_oscillation",
    "sway_offset",
    "foot_lift_offset",
    "move_along_direction",
    "look_at_direction",
    "look_angle_to_target",
    "step_positions",
    "scalar_steps",
]