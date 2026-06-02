"""
Kinematics utilities for mathlab-mylinehub-creature.

This module provides reusable math helpers for articulated creature movement.

Core responsibilities:
- angle solving
- joint solving
- two-bone IK
- simple leg / arm bend math
- procedural step arcs
- body bounce / sway / tilt helpers
- damping helpers

Architecture rule:
- kinematics.py is pure math
- no Manim objects are created here
- no audio logic lives here
- audio remains separate and may later be triggered by actions
- body parts should use these helpers through rigs/controllers/actions

Used later by:
- arm_rig.py
- leg_rig.py
- walk_action.py
- step_action.py
- hop_action.py
- body_core.py
"""

from __future__ import annotations

from dataclasses import dataclass
from math import atan2
from math import cos
from math import pi
from math import sin
from typing import Iterable

import numpy as np

from mathlab_creature.core.geometry import angle_between
from mathlab_creature.core.geometry import as_vec3
from mathlab_creature.core.geometry import clamp
from mathlab_creature.core.geometry import direction
from mathlab_creature.core.geometry import distance
from mathlab_creature.core.geometry import lerp
from mathlab_creature.core.geometry import normalize
from mathlab_creature.core.geometry import point
from mathlab_creature.core.geometry import vector_between
from mathlab_creature.core.geometry import zero_vector


# ============================================================
# Type aliases
# ============================================================

Vector3 = np.ndarray
Vec3Like = np.ndarray | Iterable[float]


# ============================================================
# Validation helpers
# ============================================================

def _validate_numeric(
    name: str,
    value: float | int,
) -> float:
    """
    Ensure numeric value.
    """
    if not isinstance(value, (int, float)):
        raise TypeError(
            f"{name} must be numeric, got {type(value).__name__}"
        )

    return float(value)


def _validate_positive(
    name: str,
    value: float | int,
) -> float:
    """
    Ensure strictly positive numeric value.
    """
    value = _validate_numeric(
        name,
        value,
    )

    if value <= 0:
        raise ValueError(
            f"{name} must be > 0, got {value}"
        )

    return value


def _validate_non_negative(
    name: str,
    value: float | int,
) -> float:
    """
    Ensure non-negative numeric value.
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


def _coerce_vec3(
    value: Vec3Like,
    name: str = "vector",
) -> Vector3:
    """
    Convert vector-like data to vec3.
    """
    return as_vec3(
        value,
        name=name,
    )


# ============================================================
# Angle helpers
# ============================================================

def angle_between_points(
    a: Vec3Like,
    b: Vec3Like,
) -> float:
    """
    Return 2D angle from point a to point b in the x-y plane.
    """
    a_vec = _coerce_vec3(
        a,
        "a",
    )
    b_vec = _coerce_vec3(
        b,
        "b",
    )

    delta = b_vec - a_vec

    return float(
        atan2(
            delta[1],
            delta[0],
        )
    )


def angle_between_vectors(
    a: Vec3Like,
    b: Vec3Like,
) -> float:
    """
    Return angle between two vectors in radians.
    """
    return angle_between(
        a,
        b,
    )


def shortest_angle_difference(
    current: float,
    target: float,
) -> float:
    """
    Return shortest signed angular difference from current to target.
    """
    current = _validate_numeric(
        "current",
        current,
    )
    target = _validate_numeric(
        "target",
        target,
    )

    return float(
        (target - current + pi) % (2.0 * pi) - pi
    )


def smooth_rotate_towards(
    current: float,
    target: float,
    speed: float,
    delta_time: float,
) -> float:
    """
    Move current angle toward target angle by speed * delta_time.
    """
    current = _validate_numeric(
        "current",
        current,
    )
    target = _validate_numeric(
        "target",
        target,
    )
    speed = _validate_non_negative(
        "speed",
        speed,
    )
    delta_time = _validate_non_negative(
        "delta_time",
        delta_time,
    )

    difference = shortest_angle_difference(
        current,
        target,
    )

    step = speed * delta_time

    if abs(difference) <= step:
        return target

    return current + float(np.sign(difference)) * step


# ============================================================
# Joint solution data
# ============================================================

@dataclass(frozen=True)
class JointSolution:
    """
    Solved two-bone joint chain data.

    Structure:
        root_position -> joint_position -> end_position
    """

    root_position: Vector3
    joint_position: Vector3
    end_position: Vector3

    root_angle: float
    joint_angle: float

    upper_length: float
    lower_length: float

    is_reachable: bool


# ============================================================
# Two-bone IK solver
# ============================================================

def solve_two_bone_ik(
    root_position: Vec3Like,
    target_position: Vec3Like,
    upper_length: float,
    lower_length: float,
    bend_direction: float = 1.0,
) -> JointSolution:
    """
    Solve a simple two-bone chain.

    Used for:
    - hip -> knee -> foot
    - shoulder -> elbow -> hand
    - procedural stepping
    - simple arm pointing

    bend_direction:
        +1.0 bends one side
        -1.0 bends opposite side
    """
    root = _coerce_vec3(
        root_position,
        "root_position",
    )
    target = _coerce_vec3(
        target_position,
        "target_position",
    )

    upper_length = _validate_positive(
        "upper_length",
        upper_length,
    )
    lower_length = _validate_positive(
        "lower_length",
        lower_length,
    )
    bend_direction = _validate_numeric(
        "bend_direction",
        bend_direction,
    )

    raw_direction = target - root
    target_distance = float(
        np.linalg.norm(raw_direction)
    )

    max_reach = upper_length + lower_length
    min_reach = abs(upper_length - lower_length)

    is_reachable = (
        min_reach
        <= target_distance
        <= max_reach
    )

    if target_distance <= 1e-8:
        raw_direction = point(
            1.0,
            0.0,
            0.0,
        )
        target_distance = 1e-8

    direction_unit = normalize(
        raw_direction,
    )

    solved_distance = clamp(
        target_distance,
        max(min_reach, 1e-8),
        max_reach,
    )

    solved_target = root + direction_unit * solved_distance

    upper_angle_offset = float(
        np.arccos(
            clamp(
                (
                    upper_length**2
                    + solved_distance**2
                    - lower_length**2
                )
                / (2.0 * upper_length * solved_distance),
                -1.0,
                1.0,
            )
        )
    )

    lower_inner_angle = float(
        np.arccos(
            clamp(
                (
                    upper_length**2
                    + lower_length**2
                    - solved_distance**2
                )
                / (2.0 * upper_length * lower_length),
                -1.0,
                1.0,
            )
        )
    )

    base_angle = angle_between_points(
        root,
        solved_target,
    )

    root_angle = (
        base_angle
        + upper_angle_offset * bend_direction
    )

    joint_angle = (
        pi - lower_inner_angle
    ) * bend_direction

    joint_position = root + point(
        cos(root_angle) * upper_length,
        sin(root_angle) * upper_length,
        0.0,
    )

    return JointSolution(
        root_position=root,
        joint_position=joint_position,
        end_position=solved_target,
        root_angle=root_angle,
        joint_angle=joint_angle,
        upper_length=upper_length,
        lower_length=lower_length,
        is_reachable=is_reachable,
    )


# ============================================================
# Arm / leg convenience solvers
# ============================================================

def solve_arm_chain(
    shoulder_position: Vec3Like,
    hand_target_position: Vec3Like,
    upper_arm_length: float,
    forearm_length: float,
    bend_direction: float = -1.0,
) -> JointSolution:
    """
    Solve shoulder -> elbow -> hand.
    """
    return solve_two_bone_ik(
        root_position=shoulder_position,
        target_position=hand_target_position,
        upper_length=upper_arm_length,
        lower_length=forearm_length,
        bend_direction=bend_direction,
    )


def solve_leg_chain(
    hip_position: Vec3Like,
    foot_target_position: Vec3Like,
    upper_leg_length: float,
    lower_leg_length: float,
    bend_direction: float = 1.0,
) -> JointSolution:
    """
    Solve hip -> knee -> foot.
    """
    return solve_two_bone_ik(
        root_position=hip_position,
        target_position=foot_target_position,
        upper_length=upper_leg_length,
        lower_length=lower_leg_length,
        bend_direction=bend_direction,
    )


# ============================================================
# Step / foot arc helpers
# ============================================================

def solve_step_arc(
    start: Vec3Like,
    end: Vec3Like,
    step_height: float,
    t: float,
) -> Vector3:
    """
    Procedural foot arc.

    Produces:
    - smooth lift
    - smooth landing
    - natural stepping
    """
    start_vec = _coerce_vec3(
        start,
        "start",
    )
    end_vec = _coerce_vec3(
        end,
        "end",
    )
    step_height = _validate_non_negative(
        "step_height",
        step_height,
    )
    t = clamp(
        _validate_numeric(
            "t",
            t,
        ),
        0.0,
        1.0,
    )

    horizontal = lerp(
        start_vec,
        end_vec,
        t,
    )

    lift = sin(t * pi) * step_height

    return horizontal + point(
        0.0,
        lift,
        0.0,
    )


def solve_leg_step_arc(
    start: Vec3Like,
    end: Vec3Like,
    step_height: float,
    t: float,
) -> Vector3:
    """
    Backward-compatible alias for solve_step_arc().
    """
    return solve_step_arc(
        start=start,
        end=end,
        step_height=step_height,
        t=t,
    )


# ============================================================
# Body motion helpers
# ============================================================

def solve_body_bounce(
    walk_cycle: float,
    amplitude: float = 0.08,
) -> float:
    """
    Vertical body bounce during walking.
    """
    walk_cycle = _validate_numeric(
        "walk_cycle",
        walk_cycle,
    )
    amplitude = _validate_non_negative(
        "amplitude",
        amplitude,
    )

    return float(
        sin(walk_cycle * 2.0 * pi) * amplitude
    )


def solve_body_sway(
    walk_cycle: float,
    amplitude: float = 0.04,
) -> float:
    """
    Horizontal balance sway.
    """
    walk_cycle = _validate_numeric(
        "walk_cycle",
        walk_cycle,
    )
    amplitude = _validate_non_negative(
        "amplitude",
        amplitude,
    )

    return float(
        cos(walk_cycle * 2.0 * pi) * amplitude
    )


def solve_body_tilt(
    velocity: Vec3Like,
    max_tilt: float = 0.15,
) -> float:
    """
    Lean body based on movement velocity.

    This is used by BodyCore / movement controller,
    not by individual loose parts.
    """
    velocity_vec = _coerce_vec3(
        velocity,
        "velocity",
    )
    max_tilt = _validate_non_negative(
        "max_tilt",
        max_tilt,
    )

    speed = float(
        np.linalg.norm(velocity_vec)
    )

    if speed <= 1e-5:
        return 0.0

    velocity_direction = normalize(
        velocity_vec,
    )

    return clamp(
        velocity_direction[0] * max_tilt,
        -max_tilt,
        max_tilt,
    )


# ============================================================
# Foot / hand placement
# ============================================================

def solve_foot_placement(
    hip_position: Vec3Like,
    walk_direction: Vec3Like,
    stride_length: float,
    side_offset: float,
) -> Vector3:
    """
    Compute stable foot placement target.
    """
    hip = _coerce_vec3(
        hip_position,
        "hip_position",
    )
    walk_dir = normalize(
        _coerce_vec3(
            walk_direction,
            "walk_direction",
        )
    )
    stride_length = _validate_numeric(
        "stride_length",
        stride_length,
    )
    side_offset = _validate_numeric(
        "side_offset",
        side_offset,
    )

    if np.linalg.norm(walk_dir) <= 1e-8:
        walk_dir = point(
            1.0,
            0.0,
            0.0,
        )

    side_direction = point(
        -walk_dir[1],
        walk_dir[0],
        0.0,
    )

    return (
        hip
        + walk_dir * stride_length
        + side_direction * side_offset
    )


def solve_hand_placement(
    shoulder_position: Vec3Like,
    reach_direction: Vec3Like,
    reach_length: float,
    side_offset: float = 0.0,
) -> Vector3:
    """
    Compute a simple hand target from shoulder + direction.
    """
    shoulder = _coerce_vec3(
        shoulder_position,
        "shoulder_position",
    )
    reach_dir = normalize(
        _coerce_vec3(
            reach_direction,
            "reach_direction",
        )
    )
    reach_length = _validate_non_negative(
        "reach_length",
        reach_length,
    )
    side_offset = _validate_numeric(
        "side_offset",
        side_offset,
    )

    if np.linalg.norm(reach_dir) <= 1e-8:
        reach_dir = point(
            1.0,
            0.0,
            0.0,
        )

    side_direction = point(
        -reach_dir[1],
        reach_dir[0],
        0.0,
    )

    return (
        shoulder
        + reach_dir * reach_length
        + side_direction * side_offset
    )


# ============================================================
# Spring / damping
# ============================================================

def damp(
    current: float,
    target: float,
    smoothing: float,
    delta_time: float,
) -> float:
    """
    Smooth damp interpolation.

    Useful for:
    - body smoothing
    - camera follow
    - procedural motion
    - controller smoothing
    """
    current = _validate_numeric(
        "current",
        current,
    )
    target = _validate_numeric(
        "target",
        target,
    )
    smoothing = _validate_non_negative(
        "smoothing",
        smoothing,
    )
    delta_time = _validate_non_negative(
        "delta_time",
        delta_time,
    )

    factor = 1.0 - float(
        np.exp(-smoothing * delta_time)
    )

    return float(
        lerp(
            current,
            target,
            factor,
        )
    )


def damp_vector(
    current: Vec3Like,
    target: Vec3Like,
    smoothing: float,
    delta_time: float,
) -> Vector3:
    """
    Vector version of damp().
    """
    current_vec = _coerce_vec3(
        current,
        "current",
    )
    target_vec = _coerce_vec3(
        target,
        "target",
    )
    smoothing = _validate_non_negative(
        "smoothing",
        smoothing,
    )
    delta_time = _validate_non_negative(
        "delta_time",
        delta_time,
    )

    factor = 1.0 - float(
        np.exp(-smoothing * delta_time)
    )

    return lerp(
        current_vec,
        target_vec,
        factor,
    )


# ============================================================
# Motion curves
# ============================================================

def ease_in_out(
    t: float,
) -> float:
    """
    Smooth interpolation curve.
    """
    t = clamp(
        _validate_numeric(
            "t",
            t,
        ),
        0.0,
        1.0,
    )

    return float(
        t * t * (3.0 - 2.0 * t)
    )


def smootherstep(
    t: float,
) -> float:
    """
    Ultra-smooth procedural motion curve.
    """
    t = clamp(
        _validate_numeric(
            "t",
            t,
        ),
        0.0,
        1.0,
    )

    return float(
        t
        * t
        * t
        * (
            t
            * (
                t * 6.0
                - 15.0
            )
            + 10.0
        )
    )


# ============================================================
# Future IK placeholder
# ============================================================

class IKChain:
    """
    Future full IK chain system.

    Reserved for:
    - FABRIK
    - CCD IK
    - terrain walking
    - procedural animation
    - climbing systems
    """

    def __init__(self) -> None:
        self.joints: list[Vector3] = []

    def solve(self) -> None:
        """
        Placeholder for future advanced IK solving.
        """
        raise NotImplementedError(
            "Advanced IK system not implemented yet."
        )


# ============================================================
# Export control
# ============================================================

__all__ = [
    "Vector3",
    "Vec3Like",
    "JointSolution",
    "angle_between_points",
    "angle_between_vectors",
    "shortest_angle_difference",
    "smooth_rotate_towards",
    "solve_two_bone_ik",
    "solve_arm_chain",
    "solve_leg_chain",
    "solve_step_arc",
    "solve_leg_step_arc",
    "solve_body_bounce",
    "solve_body_sway",
    "solve_body_tilt",
    "solve_foot_placement",
    "solve_hand_placement",
    "damp",
    "damp_vector",
    "ease_in_out",
    "smootherstep",
    "IKChain",
]