"""
mathlab_creature/core/kinematics.py

Production-grade kinematics utilities
for articulated creature movement systems.

Core Responsibilities
---------------------
- joint math
- bend solving
- angle solving
- leg chain solving
- future IK support
- smooth motion math

Design Goals
------------
- reusable
- deterministic
- animation-safe
- future 3D-ready
- controller-friendly
- procedural-animation-ready
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np

from manimlib.constants import PI


# =========================================================
# VECTOR HELPERS
# =========================================================

Vector3 = np.ndarray


def vec3(x=0.0, y=0.0, z=0.0) -> Vector3:
    return np.array([x, y, z], dtype=float)


def normalize(vector: Vector3) -> Vector3:
    magnitude = np.linalg.norm(vector)

    if magnitude <= 1e-8:
        return vec3()

    return vector / magnitude


def distance(a: Vector3, b: Vector3) -> float:
    return np.linalg.norm(b - a)


def lerp(a, b, t: float):
    return a + (b - a) * t


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))


# =========================================================
# ANGLE HELPERS
# =========================================================

def angle_between_points(a: Vector3, b: Vector3) -> float:
    """
    2D angle from point A to point B.
    """

    direction = b - a

    return np.arctan2(direction[1], direction[0])


def angle_between_vectors(a: Vector3, b: Vector3) -> float:
    """
    Returns angle between normalized vectors.
    """

    a_norm = normalize(a)
    b_norm = normalize(b)

    dot = np.dot(a_norm, b_norm)

    dot = clamp(dot, -1.0, 1.0)

    return np.arccos(dot)


def shortest_angle_difference(
    current: float,
    target: float,
) -> float:
    """
    Smooth shortest-path angle solving.
    """

    difference = (target - current + PI) % (2 * PI) - PI

    return difference


def smooth_rotate_towards(
    current: float,
    target: float,
    speed: float,
    delta_time: float,
) -> float:
    """
    Smooth angle interpolation.
    """

    difference = shortest_angle_difference(
        current,
        target,
    )

    step = speed * delta_time

    if abs(difference) <= step:
        return target

    return current + np.sign(difference) * step


# =========================================================
# JOINT SOLUTION DATA
# =========================================================

@dataclass
class JointSolution:
    """
    Stores solved joint chain data.
    """

    root_position: Vector3
    joint_position: Vector3
    end_position: Vector3

    root_angle: float
    joint_angle: float

    is_reachable: bool


# =========================================================
# TWO-BONE IK / LEG SOLVER
# =========================================================

def solve_two_bone_ik(
    root_position: Vector3,
    target_position: Vector3,
    upper_length: float,
    lower_length: float,
    bend_direction: float = 1.0,
) -> JointSolution:
    """
    Solve a simple 2-bone chain.

    Used for:
    - legs
    - knees
    - elbows
    - procedural stepping

    Structure:
        hip -> knee -> foot
    """

    root_position = np.array(root_position, dtype=float)
    target_position = np.array(target_position, dtype=float)

    direction = target_position - root_position

    target_distance = np.linalg.norm(direction)

    max_reach = upper_length + lower_length

    is_reachable = target_distance <= max_reach

    # Clamp unreachable targets
    if target_distance > max_reach:
        direction = normalize(direction)
        target_position = (
            root_position + direction * max_reach
        )
        target_distance = max_reach

    # Prevent instability
    target_distance = clamp(
        target_distance,
        1e-5,
        max_reach,
    )

    # Law of cosines
    upper_angle_offset = np.arccos(
        clamp(
            (
                upper_length**2
                + target_distance**2
                - lower_length**2
            )
            / (2 * upper_length * target_distance),
            -1.0,
            1.0,
        )
    )

    lower_angle = np.arccos(
        clamp(
            (
                upper_length**2
                + lower_length**2
                - target_distance**2
            )
            / (2 * upper_length * lower_length),
            -1.0,
            1.0,
        )
    )

    base_angle = angle_between_points(
        root_position,
        target_position,
    )

    root_angle = (
        base_angle
        + upper_angle_offset * bend_direction
    )

    joint_angle = (
        PI - lower_angle
    ) * bend_direction

    # Compute knee position
    knee_position = root_position + vec3(
        np.cos(root_angle) * upper_length,
        np.sin(root_angle) * upper_length,
        0.0,
    )

    return JointSolution(
        root_position=root_position,
        joint_position=knee_position,
        end_position=target_position,
        root_angle=root_angle,
        joint_angle=joint_angle,
        is_reachable=is_reachable,
    )


# =========================================================
# LEG STEP SOLVER
# =========================================================

def solve_leg_step_arc(
    start: Vector3,
    end: Vector3,
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

    t = clamp(t, 0.0, 1.0)

    horizontal = lerp(start, end, t)

    lift = np.sin(t * PI) * step_height

    return horizontal + vec3(0.0, lift, 0.0)


# =========================================================
# BODY MOTION HELPERS
# =========================================================

def solve_body_bounce(
    walk_cycle: float,
    amplitude: float = 0.08,
) -> float:
    """
    Vertical body bounce during walking.
    """

    return np.sin(walk_cycle * 2 * PI) * amplitude


def solve_body_sway(
    walk_cycle: float,
    amplitude: float = 0.04,
) -> float:
    """
    Horizontal balance sway.
    """

    return np.cos(walk_cycle * 2 * PI) * amplitude


def solve_body_tilt(
    velocity: Vector3,
    max_tilt: float = 0.15,
) -> float:
    """
    Lean body based on movement velocity.
    """

    speed = np.linalg.norm(velocity)

    if speed <= 1e-5:
        return 0.0

    direction = normalize(velocity)

    return clamp(
        direction[0] * max_tilt,
        -max_tilt,
        max_tilt,
    )


# =========================================================
# FOOT PLACEMENT
# =========================================================

def solve_foot_placement(
    hip_position: Vector3,
    walk_direction: Vector3,
    stride_length: float,
    side_offset: float,
) -> Vector3:
    """
    Compute stable foot placement target.
    """

    walk_direction = normalize(walk_direction)

    side_direction = vec3(
        -walk_direction[1],
        walk_direction[0],
        0.0,
    )

    return (
        hip_position
        + walk_direction * stride_length
        + side_direction * side_offset
    )


# =========================================================
# SPRING / DAMPING
# =========================================================

def damp(
    current: float,
    target: float,
    smoothing: float,
    delta_time: float,
) -> float:
    """
    Smooth damp interpolation.

    Useful for:
    - cinematic movement
    - body smoothing
    - camera follow
    - procedural motion
    """

    return lerp(
        current,
        target,
        1.0 - np.exp(-smoothing * delta_time),
    )


def damp_vector(
    current: Vector3,
    target: Vector3,
    smoothing: float,
    delta_time: float,
) -> Vector3:
    """
    Vector version of damp().
    """

    return lerp(
        current,
        target,
        1.0 - np.exp(-smoothing * delta_time),
    )


# =========================================================
# MOTION CURVES
# =========================================================

def ease_in_out(t: float) -> float:
    """
    Smooth cinematic interpolation curve.
    """

    t = clamp(t, 0.0, 1.0)

    return t * t * (3.0 - 2.0 * t)


def smootherstep(t: float) -> float:
    """
    Ultra-smooth procedural motion curve.
    """

    t = clamp(t, 0.0, 1.0)

    return (
        t * t * t
        * (
            t * (
                t * 6 - 15
            ) + 10
        )
    )


# =========================================================
# FUTURE IK PLACEHOLDERS
# =========================================================

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

    def __init__(self):
        self.joints = []

    def solve(self):
        raise NotImplementedError(
            "Advanced IK system not implemented yet."
        )