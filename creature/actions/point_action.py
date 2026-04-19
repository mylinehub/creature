"""
Point action helpers for mathlab-mylinehub-creature.

This file provides a simple pointing animation for the creature.

Version 1 goals:
- extend one arm into a pointing pose
- optionally hold the point for a moment
- optionally return back toward neutral
- keep the hand attached to the arm end
- keep implementation simple and readable

This file does not rebuild the rig.
It animates an existing rig created by body_rig.py.
"""

from __future__ import annotations

from math import radians

from manimlib import AnimationGroup
from manimlib import ApplyMethod
from manimlib import Wait

from config.defaults import DEBUG_MODE
from config.defaults import LOG_ANIMATION_EVENTS
from config.timings import POINT_HOLD_TIME
from config.timings import POINT_REACH_TIME
from config.timings import POINT_RETURN_TIME
from core.logger import get_logger

logger = get_logger(__name__)


# ============================================================
# Internal constants
# ============================================================

_ALLOWED_SIDES = {"left", "right"}
_REQUIRED_RIG_KEYS = ("arms",)


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


def _normalize_side(side: str) -> str:
    """
    Normalize and validate pointing side.
    """
    if not isinstance(side, str):
        raise TypeError(f"side must be a string, got {type(side).__name__}")

    normalized = side.strip().lower()
    if normalized not in _ALLOWED_SIDES:
        raise ValueError(f"side must be one of {_ALLOWED_SIDES}, got {side!r}")

    return normalized


def _validate_rig(rig: dict) -> None:
    """
    Validate the minimum rig shape needed for point actions.
    """
    if not isinstance(rig, dict):
        raise TypeError(f"rig must be a dict, got {type(rig).__name__}")

    missing = [key for key in _REQUIRED_RIG_KEYS if key not in rig]
    if missing:
        raise KeyError(f"rig is missing required keys: {missing}")


def _get_arm_and_hand(rig: dict, side: str):
    """
    Return arm and hand from the rig for one side.
    """
    _validate_rig(rig)
    side = _normalize_side(side)

    if side == "right":
        arm = rig["arms"]["right_arm"]
        hand = rig["arms"]["right_hand"]
    else:
        arm = rig["arms"]["left_arm"]
        hand = rig["arms"]["left_hand"]

    return arm, hand


def _rotation_sign_for_side(side: str) -> float:
    """
    Return the base rotation sign for one side.

    Right-side pointing uses negative rotation.
    Left-side pointing uses positive rotation.
    """
    side = _normalize_side(side)
    return -1.0 if side == "right" else 1.0


def _hand_sync_animation(hand, arm, *, run_time: float):
    """
    Build a hand sync animation for the current arm endpoint.

    This is used step-by-step for each action segment.
    """
    run_time = _validate_positive("run_time", run_time)

    return ApplyMethod(
        hand.move_to,
        arm.get_end(),
        run_time=run_time,
    )


def _arm_rotate_animation(arm, degrees: float, *, run_time: float):
    """
    Build a shoulder-based arm rotation animation.
    """
    run_time = _validate_positive("run_time", run_time)
    degrees = _validate_numeric("degrees", degrees)

    return ApplyMethod(
        arm.rotate,
        radians(degrees),
        {"about_point": arm.get_start()},
        run_time=run_time,
    )


# ============================================================
# Public builders
# ============================================================

def build_point_reach_animation(
    rig: dict,
    *,
    side: str = "right",
    point_degrees: float = 80.0,
):
    """
    Build the animation that moves one arm into a strong pointing pose.
    """
    _validate_rig(rig)
    side = _normalize_side(side)
    point_degrees = _validate_positive("point_degrees", point_degrees)

    if LOG_ANIMATION_EVENTS:
        logger.info(
            "Building point reach animation | side=%s point_degrees=%.3f",
            side,
            point_degrees,
        )

    arm, hand = _get_arm_and_hand(rig, side)
    signed_degrees = _rotation_sign_for_side(side) * point_degrees

    if DEBUG_MODE:
        logger.debug(
            "Point reach setup | side=%s arm=%s hand=%s signed_degrees=%.3f",
            side,
            getattr(arm, "name", "arm"),
            getattr(hand, "name", "hand"),
            signed_degrees,
        )

    return AnimationGroup(
        _arm_rotate_animation(
            arm,
            signed_degrees,
            run_time=POINT_REACH_TIME,
        ),
        _hand_sync_animation(
            hand,
            arm,
            run_time=POINT_REACH_TIME,
        ),
        lag_ratio=0.0,
    )


def build_point_hold_animation(
    *,
    hold_time: float = POINT_HOLD_TIME,
):
    """
    Build a small hold after the pointing reach.
    """
    hold_time = _validate_positive("hold_time", hold_time)

    if LOG_ANIMATION_EVENTS:
        logger.info("Building point hold animation | hold_time=%.3f", hold_time)

    return Wait(hold_time)


def build_point_return_animation(
    rig: dict,
    *,
    side: str = "right",
    point_degrees: float = 80.0,
):
    """
    Build the animation that returns one arm from pointing toward neutral.
    """
    _validate_rig(rig)
    side = _normalize_side(side)
    point_degrees = _validate_positive("point_degrees", point_degrees)

    if LOG_ANIMATION_EVENTS:
        logger.info(
            "Building point return animation | side=%s point_degrees=%.3f",
            side,
            point_degrees,
        )

    arm, hand = _get_arm_and_hand(rig, side)
    signed_degrees = -_rotation_sign_for_side(side) * point_degrees

    return AnimationGroup(
        _arm_rotate_animation(
            arm,
            signed_degrees,
            run_time=POINT_RETURN_TIME,
        ),
        _hand_sync_animation(
            hand,
            arm,
            run_time=POINT_RETURN_TIME,
        ),
        lag_ratio=0.0,
    )


def build_point_animation(
    rig: dict,
    *,
    side: str = "right",
    point_degrees: float = 80.0,
    hold: bool = True,
    hold_time: float = POINT_HOLD_TIME,
    return_to_neutral: bool = False,
):
    """
    Build a complete point action.

    Flow:
    - move one arm into pointing pose
    - optionally hold the pose
    - optionally return toward neutral

    Args:
        rig:
            Creature rig dictionary from body_rig.py

        side:
            Which side points. Allowed:
            - "right"
            - "left"

        point_degrees:
            Rotation amount used for the pointing reach.

        hold:
            If True, add a short hold after reaching the pointing pose

        hold_time:
            Duration of the optional hold.

        return_to_neutral:
            If True, return the arm back after pointing
    """
    _validate_rig(rig)
    side = _normalize_side(side)
    point_degrees = _validate_positive("point_degrees", point_degrees)

    if not isinstance(hold, bool):
        raise TypeError(f"hold must be a bool, got {type(hold).__name__}")

    if not isinstance(return_to_neutral, bool):
        raise TypeError(
            f"return_to_neutral must be a bool, got {type(return_to_neutral).__name__}"
        )

    hold_time = _validate_positive("hold_time", hold_time)

    if LOG_ANIMATION_EVENTS:
        logger.info(
            "Building full point animation | side=%s point_degrees=%.3f hold=%s hold_time=%.3f return_to_neutral=%s",
            side,
            point_degrees,
            hold,
            hold_time,
            return_to_neutral,
        )

    animations = [
        build_point_reach_animation(
            rig,
            side=side,
            point_degrees=point_degrees,
        )
    ]

    if hold:
        animations.append(
            build_point_hold_animation(
                hold_time=hold_time,
            )
        )

    if return_to_neutral:
        animations.append(
            build_point_return_animation(
                rig,
                side=side,
                point_degrees=point_degrees,
            )
        )

    return AnimationGroup(*animations, lag_ratio=0.0)