"""
Leg construction for mathlab-mylinehub-creature.

This file builds the creature's legs as simple line segments
attached to hip anchors.

Version 1 goals:
- clean, readable leg structure
- correct attachment to left/right hip anchors
- symmetric left/right legs
- easy to animate later (walk, hop, step)

This file only builds leg geometry.
Feet will be added separately.
"""

from __future__ import annotations

import numpy as np
from manimlib import Line, VGroup

from config.colors import CREATURE_LEG_COLOR
from config.defaults import DEBUG_MODE
from config.defaults import LEFT_LEG_NAME
from config.defaults import LOG_CREATURE_BUILD
from config.defaults import RIGHT_LEG_NAME
from config.sizes import LEG_LENGTH
from config.sizes import LEG_STROKE_WIDTH

from core.anchors import get_left_hip_anchor
from core.anchors import get_right_hip_anchor
from core.geometry import point
from core.logger import get_logger
from core.naming import creature_pair_part_names
from core.naming import creature_part_name

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


def _leg_end_point(
    start_point: np.ndarray,
    length: float,
    direction: str,
) -> np.ndarray:
    """
    Compute the end point of a leg from a start point, length, and direction.
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
# Internal builder
# ============================================================

def _build_single_leg(
    start_point,
    *,
    leg_name: str = "leg",
    length: float = LEG_LENGTH,
    stroke_width: float = LEG_STROKE_WIDTH,
    stroke_color: str = CREATURE_LEG_COLOR,
    direction: str = "down",
) -> Line:
    """
    Build a single leg from a hip anchor.

    Args:
        start_point:
            Hip anchor point.

        leg_name:
            Stable object name for the leg.

        length:
            Leg length.

        stroke_width:
            Leg stroke width.

        stroke_color:
            Leg stroke color.

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
        Line representing one leg.
    """
    start_point = _coerce_point3(start_point, "start_point")
    length = _validate_positive("length", length)
    stroke_width = _validate_positive("stroke_width", stroke_width)
    direction = _normalize_direction(direction)

    end_point = _leg_end_point(
        start_point=start_point,
        length=length,
        direction=direction,
    )

    leg = Line(start_point, end_point)
    leg.set_stroke(stroke_color, width=stroke_width)
    leg.name = leg_name

    # Lightweight metadata for later rigging / animation
    leg.leg_start = start_point
    leg.leg_end = end_point
    leg.leg_length = length
    leg.leg_direction = direction
    leg.leg_stroke_width = stroke_width

    if DEBUG_MODE:
        logger.debug(
            "Built leg | name=%s start=%s end=%s direction=%s",
            leg_name,
            start_point,
            end_point,
            direction,
        )

    return leg


# ============================================================
# Public builders
# ============================================================

def build_left_leg(
    body_center=None,
    *,
    direction: str = "down",
    length: float = LEG_LENGTH,
    stroke_width: float = LEG_STROKE_WIDTH,
    stroke_color: str = CREATURE_LEG_COLOR,
) -> Line:
    """
    Build left leg attached to left hip anchor.
    """
    if LOG_CREATURE_BUILD:
        logger.info("Building left leg")

    left_hip = get_left_hip_anchor(body_center)

    left_leg = _build_single_leg(
        left_hip,
        leg_name=creature_part_name(LEFT_LEG_NAME),
        length=length,
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        direction=direction,
    )

    if LOG_CREATURE_BUILD:
        logger.info("Left leg created successfully")

    return left_leg


def build_right_leg(
    body_center=None,
    *,
    direction: str = "down",
    length: float = LEG_LENGTH,
    stroke_width: float = LEG_STROKE_WIDTH,
    stroke_color: str = CREATURE_LEG_COLOR,
) -> Line:
    """
    Build right leg attached to right hip anchor.
    """
    if LOG_CREATURE_BUILD:
        logger.info("Building right leg")

    right_hip = get_right_hip_anchor(body_center)

    right_leg = _build_single_leg(
        right_hip,
        leg_name=creature_part_name(RIGHT_LEG_NAME),
        length=length,
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        direction=direction,
    )

    if LOG_CREATURE_BUILD:
        logger.info("Right leg created successfully")

    return right_leg


def build_legs(
    body_center=None,
    *,
    left_direction: str = "down",
    right_direction: str = "down",
    length: float = LEG_LENGTH,
    stroke_width: float = LEG_STROKE_WIDTH,
    stroke_color: str = CREATURE_LEG_COLOR,
    assign_group_name: bool = True,
) -> VGroup:
    """
    Build both legs together.

    Parameters:
        body_center:
            Optional body center used by hip anchors.

        left_direction:
            Direction for left leg.

        right_direction:
            Direction for right leg.

        length:
            Shared leg length.

        stroke_width:
            Shared leg stroke width.

        stroke_color:
            Shared leg stroke color.

        assign_group_name:
            If True, assign a stable name to the group.

    Returns:
        VGroup(left_leg, right_leg)
    """
    if LOG_CREATURE_BUILD:
        logger.info("Building both legs")

    left_leg = build_left_leg(
        body_center=body_center,
        direction=left_direction,
        length=length,
        stroke_width=stroke_width,
        stroke_color=stroke_color,
    )

    right_leg = build_right_leg(
        body_center=body_center,
        direction=right_direction,
        length=length,
        stroke_width=stroke_width,
        stroke_color=stroke_color,
    )

    legs = VGroup(left_leg, right_leg)

    if assign_group_name:
        left_name, right_name = creature_pair_part_names("leg")
        legs.name = "creature_legs"
        legs.left_leg_name = left_name
        legs.right_leg_name = right_name

    # Lightweight metadata for later rigging
    legs.left_leg = left_leg
    legs.right_leg = right_leg
    legs.body_center = body_center
    legs.leg_length = length

    if LOG_CREATURE_BUILD:
        logger.info("Legs created successfully")

    return legs