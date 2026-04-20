"""
Wave action helpers for mathlab-mylinehub-creature.

This file provides a simple wave animation for the creature.

Version 1 goals:
- wave using the right arm by default
- keep the movement easy to read
- keep the hand attached to the arm end after motion
- keep implementation simple and reliable

This file does not rebuild the rig.
It animates an existing arm system inside the rig.
"""

from __future__ import annotations

from math import radians

from manimlib import AnimationGroup
from manimlib import ApplyMethod

from mathlab_creature.config.defaults import DEBUG_MODE
from mathlab_creature.config.defaults import LOG_ANIMATION_EVENTS
from mathlab_creature.config.timings import ARM_RAISE_TIME
from mathlab_creature.config.timings import WAVE_BACK_TIME
from mathlab_creature.config.timings import WAVE_OUT_TIME

from mathlab_creature.core.logger import get_logger

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


def _validate_cycles(cycles: int) -> int:
    """
    Ensure cycles is a positive integer.
    """
    if not isinstance(cycles, int):
        raise TypeError(f"cycles must be an int, got {type(cycles).__name__}")
    if cycles <= 0:
        raise ValueError(f"cycles must be > 0, got {cycles}")
    return cycles


def _normalize_side(side: str) -> str:
    """
    Normalize and validate waving side.
    """
    if not isinstance(side, str):
        raise TypeError(f"side must be a string, got {type(side).__name__}")

    normalized = side.strip().lower()
    if normalized not in _ALLOWED_SIDES:
        raise ValueError(f"side must be one of {_ALLOWED_SIDES}, got {side!r}")

    return normalized


def _validate_rig(rig: dict) -> None:
    """
    Validate the minimum rig shape needed for wave actions.
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
    Return default rotation sign for one side.

    Right-side arm lifts with negative angle.
    Left-side arm lifts with positive angle.
    """
    side = _normalize_side(side)
    return -1.0 if side == "right" else 1.0


def _hand_sync_animation(hand, arm, *, run_time: float):
    """
    Build a hand sync animation for the current arm endpoint.

    This uses the arm endpoint value at the moment this sub-animation
    is created, which is correct when called step-by-step for each pose
    change segment.
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

def build_raise_arm_animation(
    rig: dict,
    *,
    side: str = "right",
    raise_degrees: float = 55.0,
):
    """
    Raise one arm into a wave-ready position.
    """
    _validate_rig(rig)
    side = _normalize_side(side)
    raise_degrees = _validate_positive("raise_degrees", raise_degrees)

    if LOG_ANIMATION_EVENTS:
        logger.info(
            "Building raise-arm animation | side=%s raise_degrees=%.3f",
            side,
            raise_degrees,
        )

    arm, hand = _get_arm_and_hand(rig, side)
    signed_raise = _rotation_sign_for_side(side) * raise_degrees

    if DEBUG_MODE:
        logger.debug(
            "Raise arm setup | side=%s arm=%s hand=%s signed_raise=%.3f",
            side,
            getattr(arm, "name", "arm"),
            getattr(hand, "name", "hand"),
            signed_raise,
        )

    return AnimationGroup(
        _arm_rotate_animation(
            arm,
            signed_raise,
            run_time=ARM_RAISE_TIME,
        ),
        _hand_sync_animation(
            hand,
            arm,
            run_time=ARM_RAISE_TIME,
        ),
        lag_ratio=0.0,
    )


def build_wave_once_animation(
    rig: dict,
    *,
    side: str = "right",
    wave_degrees: float = 18.0,
):
    """
    Build one small wave cycle from the raised arm position.

    Note:
    This assumes the arm is already in a raised position.
    """
    _validate_rig(rig)
    side = _normalize_side(side)
    wave_degrees = _validate_positive("wave_degrees", wave_degrees)

    if LOG_ANIMATION_EVENTS:
        logger.info(
            "Building one wave cycle animation | side=%s wave_degrees=%.3f",
            side,
            wave_degrees,
        )

    arm, hand = _get_arm_and_hand(rig, side)
    sign = _rotation_sign_for_side(side)

    wave_out = AnimationGroup(
        _arm_rotate_animation(
            arm,
            -sign * wave_degrees,
            run_time=WAVE_OUT_TIME,
        ),
        _hand_sync_animation(
            hand,
            arm,
            run_time=WAVE_OUT_TIME,
        ),
        lag_ratio=0.0,
    )

    wave_back = AnimationGroup(
        _arm_rotate_animation(
            arm,
            sign * wave_degrees,
            run_time=WAVE_BACK_TIME,
        ),
        _hand_sync_animation(
            hand,
            arm,
            run_time=WAVE_BACK_TIME,
        ),
        lag_ratio=0.0,
    )

    return AnimationGroup(
        wave_out,
        wave_back,
        lag_ratio=0.0,
    )


def build_wave_animation(
    rig: dict,
    *,
    side: str = "right",
    cycles: int = 2,
    raise_degrees: float = 55.0,
    wave_degrees: float = 18.0,
):
    """
    Build a complete wave action.

    Flow:
    - raise one arm
    - perform N small wave cycles

    Args:
        rig:
            Creature rig dictionary from body_rig.py

        side:
            Which side waves. Allowed:
            - "right"
            - "left"

        cycles:
            Number of small wave cycles.

        raise_degrees:
            Initial arm raise amount.

        wave_degrees:
            Small wave swing amount used for each cycle.
    """
    _validate_rig(rig)
    side = _normalize_side(side)
    cycles = _validate_cycles(cycles)
    raise_degrees = _validate_positive("raise_degrees", raise_degrees)
    wave_degrees = _validate_positive("wave_degrees", wave_degrees)

    if LOG_ANIMATION_EVENTS:
        logger.info(
            "Building full wave animation | side=%s cycles=%d raise_degrees=%.3f wave_degrees=%.3f",
            side,
            cycles,
            raise_degrees,
            wave_degrees,
        )

    animations = [
        build_raise_arm_animation(
            rig,
            side=side,
            raise_degrees=raise_degrees,
        )
    ]

    for _ in range(cycles):
        animations.append(
            build_wave_once_animation(
                rig,
                side=side,
                wave_degrees=wave_degrees,
            )
        )

    return AnimationGroup(*animations, lag_ratio=0.0)