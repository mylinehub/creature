"""
Arm construction for mathlab-mylinehub-creature.

This file builds the creature's arms as simple line segments
attached to shoulder anchors.

Version 1 goals:
- clean, readable arm structure
- correct attachment to shoulders
- symmetric left/right arms
- easy to animate later (rotate, wave, point)

This file only builds arm geometry.
Hands will be added separately.
"""

from __future__ import annotations

import numpy as np
from manimlib import Line, VGroup

from mathlab_creature.config.colors import CREATURE_ARM_COLOR
from mathlab_creature.config.defaults import DEBUG_MODE
from mathlab_creature.config.defaults import LEFT_ARM_NAME
from mathlab_creature.config.defaults import LOG_CREATURE_BUILD
from mathlab_creature.config.defaults import RIGHT_ARM_NAME
from mathlab_creature.config.sizes import ARM_LENGTH
from mathlab_creature.config.sizes import ARM_STROKE_WIDTH

from mathlab_creature.core.anchors import get_left_shoulder_anchor
from mathlab_creature.core.anchors import get_right_shoulder_anchor
from mathlab_creature.core.geometry import point
from mathlab_creature.core.logger import get_logger
from mathlab_creature.core.naming import creature_pair_part_names
from mathlab_creature.core.naming import creature_part_name

logger = get_logger(__name__)


# ============================================================
# Internal helpers
# ============================================================

_ALLOWED_DIRECTIONS = {
    "down",
    "up",
    "left",
    "right",
    "down_left",
    "down_right",
    "up_left",
    "up_right",
}


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


def _coerce_point3(value, name: str = "value") -> np.ndarray:
    """
    Normalize a point-like input into a clean 3D numpy point.
    """
    if isinstance(value, np.ndarray):
        if value.shape != (3,):
            raise ValueError(f"{name} must have shape (3,), got {value.shape}")
        return value.astype(float)

    if isinstance(value, (tuple, list)):
        if len(value) != 3:
            raise ValueError(f"{name} must contain exactly 3 values, got {len(value)}")
        return point(value[0], value[1], value[2])

    raise TypeError(f"{name} must be a numpy.ndarray or 3-item tuple/list")


def _normalize_direction(direction: str) -> str:
    """
    Normalize and validate direction text.
    """
    if not isinstance(direction, str):
        raise TypeError(f"direction must be a string, got {type(direction).__name__}")

    normalized = direction.strip().lower().replace("-", "_").replace(" ", "_")

    if normalized not in _ALLOWED_DIRECTIONS:
        raise ValueError(
            f"Unsupported direction {direction!r}. "
            f"Allowed values: {sorted(_ALLOWED_DIRECTIONS)}"
        )

    return normalized


def _direction_vector(direction: str) -> np.ndarray:
    """
    Return a normalized cardinal/diagonal direction vector in XY plane.
    """
    direction = _normalize_direction(direction)

    mapping = {
        "down": point(0.0, -1.0, 0.0),
        "up": point(0.0, 1.0, 0.0),
        "left": point(-1.0, 0.0, 0.0),
        "right": point(1.0, 0.0, 0.0),
        "down_left": point(-1.0, -1.0, 0.0),
        "down_right": point(1.0, -1.0, 0.0),
        "up_left": point(-1.0, 1.0, 0.0),
        "up_right": point(1.0, 1.0, 0.0),
    }

    vec = mapping[direction]
    mag = np.linalg.norm(vec)

    if mag == 0:
        return point(0.0, -1.0, 0.0)

    return vec / mag


def _arm_end_point(
    start_point: np.ndarray,
    length: float,
    direction: str,
) -> np.ndarray:
    """
    Compute the end point of an arm from a start point, length, and direction.
    """
    start_point = _coerce_point3(start_point, "start_point")
    length = _validate_positive("length", length)

    unit_vec = _direction_vector(direction)

    return point(
        start_point[0] + unit_vec[0] * length,
        start_point[1] + unit_vec[1] * length,
        start_point[2] + unit_vec[2] * length,
    )


# ============================================================
# Internal builders
# ============================================================

def _build_single_arm(
    start_point,
    *,
    arm_name: str = "arm",
    length: float = ARM_LENGTH,
    stroke_width: float = ARM_STROKE_WIDTH,
    stroke_color: str = CREATURE_ARM_COLOR,
    direction: str = "down",
) -> Line:
    """
    Build a single arm from a start point.

    Args:
        start_point:
            Shoulder anchor point.

        arm_name:
            Stable object name for the arm.

        length:
            Arm length.

        stroke_width:
            Arm stroke width.

        stroke_color:
            Arm stroke color.

        direction:
            Direction keyword such as:
            - down
            - up
            - left
            - right
            - down_left
            - down_right
            - up_left
            - up_right

    Returns:
        Line representing one arm.
    """
    start_point = _coerce_point3(start_point, "start_point")
    length = _validate_positive("length", length)
    stroke_width = _validate_positive("stroke_width", stroke_width)
    direction = _normalize_direction(direction)

    end_point = _arm_end_point(
        start_point=start_point,
        length=length,
        direction=direction,
    )

    arm = Line(start_point, end_point)
    arm.set_stroke(stroke_color, width=stroke_width)
    arm.name = arm_name

    # Lightweight metadata for later rigging / animation
    arm.arm_start = start_point
    arm.arm_end = end_point
    arm.arm_length = length
    arm.arm_direction = direction
    arm.arm_stroke_width = stroke_width

    if DEBUG_MODE:
        logger.debug(
            "Built arm | name=%s start=%s end=%s direction=%s",
            arm_name,
            start_point,
            end_point,
            direction,
        )

    return arm


# ============================================================
# Public builders
# ============================================================

def build_left_arm(
    body_center=None,
    *,
    direction: str = "down",
    length: float = ARM_LENGTH,
    stroke_width: float = ARM_STROKE_WIDTH,
    stroke_color: str = CREATURE_ARM_COLOR,
) -> Line:
    """
    Build left arm attached to left shoulder.
    """
    if LOG_CREATURE_BUILD:
        logger.info("Building left arm")

    left_shoulder = get_left_shoulder_anchor(body_center)

    arm = _build_single_arm(
        left_shoulder,
        arm_name=creature_part_name(LEFT_ARM_NAME),
        length=length,
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        direction=direction,
    )

    return arm


def build_right_arm(
    body_center=None,
    *,
    direction: str = "down",
    length: float = ARM_LENGTH,
    stroke_width: float = ARM_STROKE_WIDTH,
    stroke_color: str = CREATURE_ARM_COLOR,
) -> Line:
    """
    Build right arm attached to right shoulder.
    """
    if LOG_CREATURE_BUILD:
        logger.info("Building right arm")

    right_shoulder = get_right_shoulder_anchor(body_center)

    arm = _build_single_arm(
        right_shoulder,
        arm_name=creature_part_name(RIGHT_ARM_NAME),
        length=length,
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        direction=direction,
    )

    return arm


def build_arms(
    body_center=None,
    *,
    left_direction: str = "down",
    right_direction: str = "down",
    length: float = ARM_LENGTH,
    stroke_width: float = ARM_STROKE_WIDTH,
    stroke_color: str = CREATURE_ARM_COLOR,
    assign_group_name: bool = True,
) -> VGroup:
    """
    Build both arms together.

    Parameters:
        body_center:
            Optional body center used by shoulder anchors.

        left_direction:
            Direction for left arm.

        right_direction:
            Direction for right arm.

        length:
            Shared arm length.

        stroke_width:
            Shared arm stroke width.

        stroke_color:
            Shared arm stroke color.

        assign_group_name:
            If True, assign a stable name to the group.

    Returns:
        VGroup(left_arm, right_arm)
    """
    if LOG_CREATURE_BUILD:
        logger.info("Building both arms")

    left_arm = build_left_arm(
        body_center=body_center,
        direction=left_direction,
        length=length,
        stroke_width=stroke_width,
        stroke_color=stroke_color,
    )

    right_arm = build_right_arm(
        body_center=body_center,
        direction=right_direction,
        length=length,
        stroke_width=stroke_width,
        stroke_color=stroke_color,
    )

    arms = VGroup(left_arm, right_arm)

    if assign_group_name:
        left_name, right_name = creature_pair_part_names("arm")
        arms.name = "creature_arms"
        arms.left_arm_name = left_name
        arms.right_arm_name = right_name

    # Lightweight metadata for later rigging
    arms.left_arm = left_arm
    arms.right_arm = right_arm
    arms.body_center = body_center
    arms.arm_length = length

    if LOG_CREATURE_BUILD:
        logger.info("Arms created successfully")

    return arms