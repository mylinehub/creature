"""
Hand construction for mathlab-mylinehub-creature.

This file builds simple hand shapes for the connected creature system.

Architecture rule:
- hands are visual parts only
- hands do not build arms
- hands do not import arms
- hands attach to arm end points supplied by arms.py
- hands should never move independently in scene code
- audio is not handled here; audio may be triggered later by actions

Hands are intentionally simple in this version.
Finger-level detail can be added later without changing the public API.
"""

from __future__ import annotations

from typing import Iterable
from typing import Optional

import numpy as np

from manimlib import Circle
from manimlib import VGroup

from mathlab_creature.config.colors import CREATURE_HAND_COLOR
from mathlab_creature.config.defaults import DEBUG_MODE
from mathlab_creature.config.defaults import LEFT_HAND_NAME
from mathlab_creature.config.defaults import LOG_CREATURE_BUILD
from mathlab_creature.config.defaults import RIGHT_HAND_NAME
from mathlab_creature.config.sizes import HAND_RADIUS

from mathlab_creature.core.geometry import as_vec3
from mathlab_creature.core.geometry import point
from mathlab_creature.core.geometry import zero_point
from mathlab_creature.core.logger import get_logger
from mathlab_creature.core.naming import creature_pair_part_names
from mathlab_creature.core.naming import creature_part_name


logger = get_logger(__name__)


# ============================================================
# Type aliases
# ============================================================

Vector3 = np.ndarray
Vec3Like = np.ndarray | Iterable[float]


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


def _validate_positive(
    name: str,
    value: float | int,
) -> float:
    """
    Ensure a positive numeric value.
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


def _coerce_point3(
    value: Optional[Vec3Like],
    name: str = "value",
) -> Vector3:
    """
    Normalize a point-like input into a clean 3D numpy point.

    None becomes origin.
    """
    if value is None:
        return zero_point()

    return as_vec3(
        value,
        name=name,
    )


def _get_mobject_end_point(
    mobject,
    name: str,
) -> Vector3:
    """
    Get an end point from a Manim object-like value.

    Expected for arm integration:
    - Line-like objects usually expose get_end()
    - Custom arm groups may expose hand_anchor or end_point metadata
    """
    if mobject is None:
        raise ValueError(
            f"{name} must not be None when end point is not provided"
        )

    if hasattr(mobject, "get_end") and callable(mobject.get_end):
        return as_vec3(
            mobject.get_end(),
            name=f"{name}.get_end()",
        )

    if hasattr(mobject, "hand_anchor"):
        return as_vec3(
            mobject.hand_anchor,
            name=f"{name}.hand_anchor",
        )

    if hasattr(mobject, "end_point"):
        return as_vec3(
            mobject.end_point,
            name=f"{name}.end_point",
        )

    raise TypeError(
        f"{name} must provide get_end(), hand_anchor, or end_point"
    )


# ============================================================
# Shape builders
# ============================================================

def build_hand_shape(
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
    radius = _validate_positive(
        "radius",
        radius,
    )
    stroke_width = _validate_non_negative(
        "stroke_width",
        stroke_width,
    )

    hand = Circle(
        radius=radius,
    )
    hand.set_fill(
        fill_color,
        opacity=1.0,
    )
    hand.set_stroke(
        stroke_color,
        width=stroke_width,
    )

    hand.hand_radius = radius

    return hand


def build_hand_at(
    position: Optional[Vec3Like] = None,
    *,
    hand_name: str = "hand",
    radius: float = HAND_RADIUS,
    fill_color: str = CREATURE_HAND_COLOR,
    stroke_color: str = CREATURE_HAND_COLOR,
    stroke_width: float = 0.0,
) -> Circle:
    """
    Build a single hand positioned at a supplied point.

    This is the preferred low-level builder.

    Arms should call this with their own computed end point.
    """
    hand_center = _coerce_point3(
        position,
        "position",
    )

    hand = build_hand_shape(
        radius=radius,
        fill_color=fill_color,
        stroke_color=stroke_color,
        stroke_width=stroke_width,
    )

    hand.move_to(
        hand_center,
    )

    hand.name = hand_name
    hand.hand_center = hand_center
    hand.hand_anchor = hand_center
    hand.is_creature_hand = True

    if DEBUG_MODE:
        logger.debug(
            "Built hand | name=%s center=%s radius=%.3f",
            hand_name,
            hand_center,
            radius,
        )

    return hand


# ============================================================
# Public single-hand builders
# ============================================================

def build_left_hand(
    position: Optional[Vec3Like] = None,
    *,
    arm=None,
    radius: float = HAND_RADIUS,
    fill_color: str = CREATURE_HAND_COLOR,
    stroke_color: str = CREATURE_HAND_COLOR,
    stroke_width: float = 0.0,
) -> Circle:
    """
    Build left hand.

    Parameters:
        position:
            Explicit hand center.

        arm:
            Optional prebuilt arm object.
            If position is not supplied, the hand uses arm.get_end(),
            arm.hand_anchor, or arm.end_point.

    Important:
        This function does not build the arm.
        arms.py owns arm construction.
    """
    if LOG_CREATURE_BUILD:
        logger.info(
            "Building left hand"
        )

    if position is None and arm is not None:
        position = _get_mobject_end_point(
            arm,
            "arm",
        )

    hand = build_hand_at(
        position=position,
        hand_name=creature_part_name(LEFT_HAND_NAME),
        radius=radius,
        fill_color=fill_color,
        stroke_color=stroke_color,
        stroke_width=stroke_width,
    )

    hand.side = "left"
    hand.source_arm = arm

    if LOG_CREATURE_BUILD:
        logger.info(
            "Left hand created successfully"
        )

    return hand


def build_right_hand(
    position: Optional[Vec3Like] = None,
    *,
    arm=None,
    radius: float = HAND_RADIUS,
    fill_color: str = CREATURE_HAND_COLOR,
    stroke_color: str = CREATURE_HAND_COLOR,
    stroke_width: float = 0.0,
) -> Circle:
    """
    Build right hand.

    Parameters:
        position:
            Explicit hand center.

        arm:
            Optional prebuilt arm object.
            If position is not supplied, the hand uses arm.get_end(),
            arm.hand_anchor, or arm.end_point.

    Important:
        This function does not build the arm.
        arms.py owns arm construction.
    """
    if LOG_CREATURE_BUILD:
        logger.info(
            "Building right hand"
        )

    if position is None and arm is not None:
        position = _get_mobject_end_point(
            arm,
            "arm",
        )

    hand = build_hand_at(
        position=position,
        hand_name=creature_part_name(RIGHT_HAND_NAME),
        radius=radius,
        fill_color=fill_color,
        stroke_color=stroke_color,
        stroke_width=stroke_width,
    )

    hand.side = "right"
    hand.source_arm = arm

    if LOG_CREATURE_BUILD:
        logger.info(
            "Right hand created successfully"
        )

    return hand


def build_hands(
    *,
    left_position: Optional[Vec3Like] = None,
    right_position: Optional[Vec3Like] = None,
    left_arm=None,
    right_arm=None,
    radius: float = HAND_RADIUS,
    fill_color: str = CREATURE_HAND_COLOR,
    stroke_color: str = CREATURE_HAND_COLOR,
    stroke_width: float = 0.0,
    assign_group_name: bool = True,
) -> VGroup:
    """
    Build both hands together.

    Parameters:
        left_position:
            Explicit left hand center.

        right_position:
            Explicit right hand center.

        left_arm:
            Optional prebuilt left arm.

        right_arm:
            Optional prebuilt right arm.

    Returns:
        VGroup(left_hand, right_hand)

    Important:
        This function does not build arms.
        It only builds hands and optionally attaches metadata to supplied arms.
    """
    if LOG_CREATURE_BUILD:
        logger.info(
            "Building both hands"
        )

    left_hand = build_left_hand(
        position=left_position,
        arm=left_arm,
        radius=radius,
        fill_color=fill_color,
        stroke_color=stroke_color,
        stroke_width=stroke_width,
    )

    right_hand = build_right_hand(
        position=right_position,
        arm=right_arm,
        radius=radius,
        fill_color=fill_color,
        stroke_color=stroke_color,
        stroke_width=stroke_width,
    )

    hands = VGroup(
        left_hand,
        right_hand,
    )

    if assign_group_name:
        left_name, right_name = creature_pair_part_names(
            "hand",
        )
        hands.name = "creature_hands"
        hands.left_hand_name = left_name
        hands.right_hand_name = right_name

    hands.left_hand = left_hand
    hands.right_hand = right_hand
    hands.hand_radius = radius
    hands.is_creature_hands_group = True

    if LOG_CREATURE_BUILD:
        logger.info(
            "Hands created successfully"
        )

    return hands


# ============================================================
# Utility helpers
# ============================================================

def get_hand_center(
    hand: Circle,
) -> Vector3:
    """
    Return hand center.

    Prefer metadata if present, otherwise use Manim center.
    """
    if hasattr(hand, "hand_center"):
        return as_vec3(
            hand.hand_center,
            name="hand.hand_center",
        )

    return as_vec3(
        hand.get_center(),
        name="hand.get_center()",
    )


def set_hand_center_metadata(
    hand: Circle,
    center: Vec3Like,
) -> None:
    """
    Update hand center metadata.

    This does not move the hand.
    It only updates metadata used by rigs/controllers.
    """
    center_vec = as_vec3(
        center,
        name="center",
    )

    hand.hand_center = center_vec
    hand.hand_anchor = center_vec


# ============================================================
# Export control
# ============================================================

__all__ = [
    "Vector3",
    "Vec3Like",
    "build_hand_shape",
    "build_hand_at",
    "build_left_hand",
    "build_right_hand",
    "build_hands",
    "get_hand_center",
    "set_hand_center_metadata",
]