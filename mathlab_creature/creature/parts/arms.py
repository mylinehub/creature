"""
Arm construction for mathlab-mylinehub-creature.

This file builds connected arm systems for the creature.

Architecture rule:
- arms are connected body parts
- arms attach to shoulder anchors
- hands attach to arm end points
- hands are not independent scene objects
- arms.py may build hands because hands.py is lower-level
- arms should not move independently in scene code
- arm_rig.py / actions will control waving and pointing later
- audio is not handled here

Connection chain:

    Body
        |
        Left Shoulder
            |
            Left Arm
                |
                Left Hand

    Body
        |
        Right Shoulder
            |
            Right Arm
                |
                Right Hand
"""

from __future__ import annotations

from typing import Iterable
from typing import Optional

import numpy as np

from manimlib import Line
from manimlib import VGroup

from mathlab_creature.config.colors import CREATURE_ARM_COLOR
from mathlab_creature.config.defaults import DEBUG_MODE
from mathlab_creature.config.defaults import LEFT_ARM_NAME
from mathlab_creature.config.defaults import LOG_CREATURE_BUILD
from mathlab_creature.config.defaults import RIGHT_ARM_NAME
from mathlab_creature.config.sizes import ARM_LENGTH
from mathlab_creature.config.sizes import ARM_STROKE_WIDTH

from mathlab_creature.core.anchors import get_left_shoulder_anchor
from mathlab_creature.core.anchors import get_right_shoulder_anchor
from mathlab_creature.core.geometry import as_vec3
from mathlab_creature.core.geometry import normalize
from mathlab_creature.core.geometry import point
from mathlab_creature.core.geometry import zero_point
from mathlab_creature.core.logger import get_logger
from mathlab_creature.core.naming import creature_pair_part_names
from mathlab_creature.core.naming import creature_part_name

from mathlab_creature.creature.parts.hands import build_left_hand
from mathlab_creature.creature.parts.hands import build_right_hand


logger = get_logger(__name__)


Vector3 = np.ndarray
Vec3Like = np.ndarray | Iterable[float]


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


def _validate_numeric(
    name: str,
    value: float | int,
) -> float:
    if not isinstance(value, (int, float)):
        raise TypeError(
            f"{name} must be numeric, got {type(value).__name__}"
        )

    return float(value)


def _validate_positive(
    name: str,
    value: float | int,
) -> float:
    value = _validate_numeric(name, value)

    if value <= 0:
        raise ValueError(
            f"{name} must be > 0, got {value}"
        )

    return value


def _coerce_point3(
    value: Optional[Vec3Like],
    name: str = "value",
) -> Vector3:
    if value is None:
        return zero_point()

    return as_vec3(
        value,
        name=name,
    )


def _normalize_direction(
    direction: str,
) -> str:
    if not isinstance(direction, str):
        raise TypeError(
            f"direction must be str, got {type(direction).__name__}"
        )

    normalized = (
        direction
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )

    if normalized not in _ALLOWED_DIRECTIONS:
        raise ValueError(
            f"Unsupported direction {direction!r}. "
            f"Allowed values: {sorted(_ALLOWED_DIRECTIONS)}"
        )

    return normalized


def _direction_vector(
    direction: str,
) -> Vector3:
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

    return normalize(
        mapping[direction],
    )


def _arm_end_point(
    start_point: Vec3Like,
    length: float,
    direction: str,
) -> Vector3:
    start = _coerce_point3(
        start_point,
        "start_point",
    )
    length = _validate_positive(
        "length",
        length,
    )

    unit_vector = _direction_vector(
        direction,
    )

    return start + unit_vector * length


def build_arm_line(
    start_point: Vec3Like,
    end_point: Vec3Like,
    *,
    arm_name: str = "arm",
    stroke_width: float = ARM_STROKE_WIDTH,
    stroke_color: str = CREATURE_ARM_COLOR,
) -> Line:
    """
    Build raw arm line between shoulder and hand anchor.
    """

    start = _coerce_point3(
        start_point,
        "start_point",
    )
    end = _coerce_point3(
        end_point,
        "end_point",
    )

    stroke_width = _validate_positive(
        "stroke_width",
        stroke_width,
    )

    arm = Line(
        start,
        end,
    )

    arm.set_stroke(
        stroke_color,
        width=stroke_width,
    )

    arm.name = arm_name

    arm.arm_start = start
    arm.arm_end = end
    arm.shoulder_anchor = start
    arm.hand_anchor = end
    arm.end_point = end
    arm.arm_stroke_width = stroke_width
    arm.is_creature_arm_line = True

    return arm


def build_arm_at(
    shoulder_position: Vec3Like,
    *,
    side: str = "left",
    direction: str = "down",
    length: float = ARM_LENGTH,
    stroke_width: float = ARM_STROKE_WIDTH,
    stroke_color: str = CREATURE_ARM_COLOR,
    include_hand: bool = True,
) -> VGroup:
    """
    Build one connected arm system at an explicit shoulder position.

    Returns:
        VGroup(arm_line, hand)

    If include_hand=False:
        returns VGroup(arm_line)
    """

    side = side.strip().lower()

    if side not in {"left", "right"}:
        raise ValueError(
            "side must be 'left' or 'right'"
        )

    shoulder = _coerce_point3(
        shoulder_position,
        "shoulder_position",
    )

    direction = _normalize_direction(
        direction,
    )

    length = _validate_positive(
        "length",
        length,
    )

    hand_anchor = _arm_end_point(
        shoulder,
        length,
        direction,
    )

    arm_name = creature_part_name(
        LEFT_ARM_NAME
        if side == "left"
        else RIGHT_ARM_NAME
    )

    arm_line = build_arm_line(
        shoulder,
        hand_anchor,
        arm_name=arm_name,
        stroke_width=stroke_width,
        stroke_color=stroke_color,
    )

    arm_line.side = side
    arm_line.arm_length = length
    arm_line.arm_direction = direction

    parts = [arm_line]

    hand = None

    if include_hand:
        if side == "left":
            hand = build_left_hand(
                position=hand_anchor,
                arm=arm_line,
            )
        else:
            hand = build_right_hand(
                position=hand_anchor,
                arm=arm_line,
            )

        parts.append(hand)

    arm_group = VGroup(
        *parts,
    )

    arm_group.name = f"creature_{side}_arm_system"
    arm_group.side = side

    arm_group.arm_line = arm_line
    arm_group.hand = hand

    arm_group.shoulder_anchor = shoulder
    arm_group.hand_anchor = hand_anchor
    arm_group.end_point = hand_anchor

    arm_group.arm_length = length
    arm_group.arm_direction = direction

    arm_group.is_creature_arm = True

    if DEBUG_MODE:
        logger.debug(
            "Built %s arm | shoulder=%s hand=%s direction=%s length=%.3f",
            side,
            shoulder,
            hand_anchor,
            direction,
            length,
        )

    return arm_group


def build_left_arm(
    body_center: Optional[Vec3Like] = None,
    *,
    shoulder_position: Optional[Vec3Like] = None,
    direction: str = "down",
    length: float = ARM_LENGTH,
    stroke_width: float = ARM_STROKE_WIDTH,
    stroke_color: str = CREATURE_ARM_COLOR,
    include_hand: bool = True,
) -> VGroup:
    """
    Build left arm connected to left shoulder.

    If shoulder_position is supplied, it overrides body_center anchor.
    """

    if LOG_CREATURE_BUILD:
        logger.info(
            "Building left arm"
        )

    shoulder = (
        _coerce_point3(
            shoulder_position,
            "shoulder_position",
        )
        if shoulder_position is not None
        else get_left_shoulder_anchor(
            body_center,
        )
    )

    arm = build_arm_at(
        shoulder,
        side="left",
        direction=direction,
        length=length,
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        include_hand=include_hand,
    )

    if LOG_CREATURE_BUILD:
        logger.info(
            "Left arm created successfully"
        )

    return arm


def build_right_arm(
    body_center: Optional[Vec3Like] = None,
    *,
    shoulder_position: Optional[Vec3Like] = None,
    direction: str = "down",
    length: float = ARM_LENGTH,
    stroke_width: float = ARM_STROKE_WIDTH,
    stroke_color: str = CREATURE_ARM_COLOR,
    include_hand: bool = True,
) -> VGroup:
    """
    Build right arm connected to right shoulder.

    If shoulder_position is supplied, it overrides body_center anchor.
    """

    if LOG_CREATURE_BUILD:
        logger.info(
            "Building right arm"
        )

    shoulder = (
        _coerce_point3(
            shoulder_position,
            "shoulder_position",
        )
        if shoulder_position is not None
        else get_right_shoulder_anchor(
            body_center,
        )
    )

    arm = build_arm_at(
        shoulder,
        side="right",
        direction=direction,
        length=length,
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        include_hand=include_hand,
    )

    if LOG_CREATURE_BUILD:
        logger.info(
            "Right arm created successfully"
        )

    return arm


def build_arms(
    body_center: Optional[Vec3Like] = None,
    *,
    left_shoulder_position: Optional[Vec3Like] = None,
    right_shoulder_position: Optional[Vec3Like] = None,
    left_direction: str = "down",
    right_direction: str = "down",
    length: float = ARM_LENGTH,
    stroke_width: float = ARM_STROKE_WIDTH,
    stroke_color: str = CREATURE_ARM_COLOR,
    include_hands: bool = True,
    assign_group_name: bool = True,
) -> VGroup:
    """
    Build both connected arm systems.

    Returns:
        VGroup(left_arm, right_arm)

    Each arm group contains:
        arm_line
        hand
    """

    if LOG_CREATURE_BUILD:
        logger.info(
            "Building both arms"
        )

    left_arm = build_left_arm(
        body_center=body_center,
        shoulder_position=left_shoulder_position,
        direction=left_direction,
        length=length,
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        include_hand=include_hands,
    )

    right_arm = build_right_arm(
        body_center=body_center,
        shoulder_position=right_shoulder_position,
        direction=right_direction,
        length=length,
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        include_hand=include_hands,
    )

    arms = VGroup(
        left_arm,
        right_arm,
    )

    if assign_group_name:
        left_name, right_name = creature_pair_part_names(
            "arm",
        )
        arms.name = "creature_arms"
        arms.left_arm_name = left_name
        arms.right_arm_name = right_name

    arms.left_arm = left_arm
    arms.right_arm = right_arm

    arms.left_hand = getattr(
        left_arm,
        "hand",
        None,
    )
    arms.right_hand = getattr(
        right_arm,
        "hand",
        None,
    )

    arms.body_center = body_center
    arms.arm_length = length
    arms.include_hands = include_hands

    arms.is_creature_arms_group = True

    if LOG_CREATURE_BUILD:
        logger.info(
            "Arms created successfully"
        )

    return arms


def get_arm_shoulder_anchor(
    arm: VGroup,
) -> Vector3:
    """
    Return arm shoulder anchor from metadata.
    """

    if hasattr(
        arm,
        "shoulder_anchor",
    ):
        return as_vec3(
            arm.shoulder_anchor,
            name="arm.shoulder_anchor",
        )

    if hasattr(
        arm,
        "arm_line",
    ) and hasattr(
        arm.arm_line,
        "arm_start",
    ):
        return as_vec3(
            arm.arm_line.arm_start,
            name="arm.arm_line.arm_start",
        )

    raise AttributeError(
        "arm must have shoulder_anchor or arm_line.arm_start metadata"
    )


def get_arm_hand_anchor(
    arm: VGroup,
) -> Vector3:
    """
    Return arm hand anchor from metadata.
    """

    if hasattr(
        arm,
        "hand_anchor",
    ):
        return as_vec3(
            arm.hand_anchor,
            name="arm.hand_anchor",
        )

    if hasattr(
        arm,
        "arm_line",
    ) and hasattr(
        arm.arm_line,
        "arm_end",
    ):
        return as_vec3(
            arm.arm_line.arm_end,
            name="arm.arm_line.arm_end",
        )

    raise AttributeError(
        "arm must have hand_anchor or arm_line.arm_end metadata"
    )


def get_arm_line(
    arm: VGroup,
) -> Line:
    """
    Return arm line from arm group.
    """

    if hasattr(
        arm,
        "arm_line",
    ):
        return arm.arm_line

    raise AttributeError(
        "arm must have arm_line metadata"
    )


def get_arm_hand(
    arm: VGroup,
):
    """
    Return hand object from arm group.
    """

    return getattr(
        arm,
        "hand",
        None,
    )


__all__ = [
    "Vector3",
    "Vec3Like",
    "build_arm_line",
    "build_arm_at",
    "build_left_arm",
    "build_right_arm",
    "build_arms",
    "get_arm_shoulder_anchor",
    "get_arm_hand_anchor",
    "get_arm_line",
    "get_arm_hand",
]