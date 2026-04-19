"""
Hand construction for mathlab-mylinehub-creature.

This file builds the creature's hands as simple rounded hand tips
that attach to the ends of the arm lines.

Version 1 goals:
- keep hands simple and readable
- attach hands cleanly to arm ends
- make later gestures easier
- keep styling controlled by config

This file only builds hand geometry.
Finger-level detail is intentionally not added yet.
"""

from __future__ import annotations

import numpy as np
from manimlib import Circle, VGroup

from config.colors import CREATURE_HAND_COLOR
from config.defaults import DEBUG_MODE
from config.defaults import LEFT_HAND_NAME
from config.defaults import LOG_CREATURE_BUILD
from config.defaults import RIGHT_HAND_NAME
from config.sizes import HAND_RADIUS

from creature.parts.arms import build_left_arm
from creature.parts.arms import build_right_arm

from core.geometry import point
from core.logger import get_logger
from core.naming import creature_pair_part_names
from core.naming import creature_part_name

logger = get_logger(__name__)


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


# ============================================================
# Internal builder
# ============================================================

def _build_hand_shape(
    *,
    radius: float = HAND_RADIUS,
    fill_color: str = CREATURE_HAND_COLOR,
    stroke_color: str = CREATURE_HAND_COLOR,
    stroke_width: float = 0.0,
) -> Circle:
    """
    Build a simple hand shape.

    Version 1 uses a small filled circle so the hand is:
    - easy to see
    - easy to animate
    - easy to replace later
    """
    radius = _validate_positive("radius", radius)
    stroke_width = _validate_numeric("stroke_width", stroke_width)

    hand = Circle(radius=radius)
    hand.set_fill(fill_color, opacity=1.0)
    hand.set_stroke(stroke_color, width=stroke_width)
    return hand


def _build_single_hand(
    end_point,
    *,
    hand_name: str = "hand",
    radius: float = HAND_RADIUS,
    fill_color: str = CREATURE_HAND_COLOR,
    stroke_color: str = CREATURE_HAND_COLOR,
    stroke_width: float = 0.0,
) -> Circle:
    """
    Build a single hand positioned at a supplied arm-end point.
    """
    end_point = _coerce_point3(end_point, "end_point")

    hand = _build_hand_shape(
        radius=radius,
        fill_color=fill_color,
        stroke_color=stroke_color,
        stroke_width=stroke_width,
    )
    hand.move_to(end_point)
    hand.name = hand_name

    # Lightweight metadata for later rigging / gesture logic
    hand.hand_center = end_point
    hand.hand_radius = radius

    if DEBUG_MODE:
        logger.debug(
            "Built hand | name=%s center=%s radius=%.3f",
            hand_name,
            end_point,
            radius,
        )

    return hand


# ============================================================
# Public builders
# ============================================================

def build_left_hand(
    body_center=None,
    *,
    arm=None,
    arm_direction: str = "down",
    radius: float = HAND_RADIUS,
    fill_color: str = CREATURE_HAND_COLOR,
    stroke_color: str = CREATURE_HAND_COLOR,
    stroke_width: float = 0.0,
) -> Circle:
    """
    Build left hand at the end of the left arm.

    Parameters:
        body_center:
            Optional body center used if an arm is built internally.

        arm:
            Optional prebuilt arm object. If provided, its end point is used.

        arm_direction:
            Direction used only when arm is not provided.

        radius:
            Hand radius.

        fill_color:
            Hand fill color.

        stroke_color:
            Hand stroke color.

        stroke_width:
            Hand stroke width.
    """
    if LOG_CREATURE_BUILD:
        logger.info("Building left hand")

    if arm is None:
        arm = build_left_arm(
            body_center=body_center,
            direction=arm_direction,
        )

    hand = _build_single_hand(
        arm.get_end(),
        hand_name=creature_part_name(LEFT_HAND_NAME),
        radius=radius,
        fill_color=fill_color,
        stroke_color=stroke_color,
        stroke_width=stroke_width,
    )

    # Relationship metadata
    hand.source_arm = arm

    if LOG_CREATURE_BUILD:
        logger.info("Left hand created successfully")

    return hand


def build_right_hand(
    body_center=None,
    *,
    arm=None,
    arm_direction: str = "down",
    radius: float = HAND_RADIUS,
    fill_color: str = CREATURE_HAND_COLOR,
    stroke_color: str = CREATURE_HAND_COLOR,
    stroke_width: float = 0.0,
) -> Circle:
    """
    Build right hand at the end of the right arm.

    Parameters:
        body_center:
            Optional body center used if an arm is built internally.

        arm:
            Optional prebuilt arm object. If provided, its end point is used.

        arm_direction:
            Direction used only when arm is not provided.

        radius:
            Hand radius.

        fill_color:
            Hand fill color.

        stroke_color:
            Hand stroke color.

        stroke_width:
            Hand stroke width.
    """
    if LOG_CREATURE_BUILD:
        logger.info("Building right hand")

    if arm is None:
        arm = build_right_arm(
            body_center=body_center,
            direction=arm_direction,
        )

    hand = _build_single_hand(
        arm.get_end(),
        hand_name=creature_part_name(RIGHT_HAND_NAME),
        radius=radius,
        fill_color=fill_color,
        stroke_color=stroke_color,
        stroke_width=stroke_width,
    )

    # Relationship metadata
    hand.source_arm = arm

    if LOG_CREATURE_BUILD:
        logger.info("Right hand created successfully")

    return hand


def build_hands(
    body_center=None,
    *,
    left_arm=None,
    right_arm=None,
    left_arm_direction: str = "down",
    right_arm_direction: str = "down",
    radius: float = HAND_RADIUS,
    fill_color: str = CREATURE_HAND_COLOR,
    stroke_color: str = CREATURE_HAND_COLOR,
    stroke_width: float = 0.0,
    assign_group_name: bool = True,
) -> VGroup:
    """
    Build both hands together.

    Parameters:
        body_center:
            Optional body center used if arms are built internally.

        left_arm:
            Optional prebuilt left arm.

        right_arm:
            Optional prebuilt right arm.

        left_arm_direction:
            Direction used only when left_arm is not provided.

        right_arm_direction:
            Direction used only when right_arm is not provided.

        radius:
            Shared hand radius.

        fill_color:
            Shared hand fill color.

        stroke_color:
            Shared hand stroke color.

        stroke_width:
            Shared hand stroke width.

        assign_group_name:
            If True, assign a stable name to the hands group.

    Returns:
        VGroup(left_hand, right_hand)
    """
    if LOG_CREATURE_BUILD:
        logger.info("Building both hands")

    left_hand = build_left_hand(
        body_center=body_center,
        arm=left_arm,
        arm_direction=left_arm_direction,
        radius=radius,
        fill_color=fill_color,
        stroke_color=stroke_color,
        stroke_width=stroke_width,
    )

    right_hand = build_right_hand(
        body_center=body_center,
        arm=right_arm,
        arm_direction=right_arm_direction,
        radius=radius,
        fill_color=fill_color,
        stroke_color=stroke_color,
        stroke_width=stroke_width,
    )

    hands = VGroup(left_hand, right_hand)

    if assign_group_name:
        left_name, right_name = creature_pair_part_names("hand")
        hands.name = "creature_hands"
        hands.left_hand_name = left_name
        hands.right_hand_name = right_name

    # Lightweight metadata for later rigging / gestures
    hands.left_hand = left_hand
    hands.right_hand = right_hand
    hands.body_center = body_center
    hands.hand_radius = radius

    if LOG_CREATURE_BUILD:
        logger.info("Hands created successfully")

    return hands