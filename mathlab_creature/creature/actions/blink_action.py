"""
Blink action helpers for mathlab-mylinehub-creature.

This file provides simple blink-related utilities for the creature.

Version 1 goals:
- support a lightweight blink effect
- keep implementation simple and easy to understand
- avoid overcomplicated eye deformation at this stage
- work with the current eye structure:
    VGroup(left_eye_group, right_eye_group)

Important:
This file does not permanently rebuild the eye design.
It provides a simple animation helper that can be used in scenes later.
"""

from __future__ import annotations

from manimlib import AnimationGroup
from manimlib import ApplyMethod

from mathlab_creature.config.defaults import DEBUG_MODE
from mathlab_creature.config.defaults import LOG_ANIMATION_EVENTS
from mathlab_creature.config.timings import BLINK_CLOSE_TIME
from mathlab_creature.config.timings import BLINK_OPEN_TIME
from mathlab_creature.core.logger import get_logger

logger = get_logger(__name__)


# ============================================================
# Internal constants
# ============================================================

_LEFT_EYE_INDEX = 0
_RIGHT_EYE_INDEX = 1
_MIN_EYE_COUNT = 2

# Vertical squash factor used for blink closing.
# Lower means flatter eyes during the closed phase.
DEFAULT_BLINK_SQUASH_FACTOR = 0.08


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


def _validate_blink_factor(factor: float) -> float:
    """
    Ensure blink squash factor is valid.

    Expected range:
    - > 0
    - typically <= 1
    """
    factor = _validate_numeric("factor", factor)
    if factor <= 0:
        raise ValueError(f"factor must be > 0, got {factor}")
    return factor


def _validate_eyes_group(eyes_group) -> None:
    """
    Validate the expected eyes-group structure.

    Expected:
        eyes_group[0] -> left eye group
        eyes_group[1] -> right eye group
    """
    if eyes_group is None:
        raise ValueError("eyes_group must not be None")

    if len(eyes_group) < _MIN_EYE_COUNT:
        raise ValueError(
            f"eyes_group must contain at least {_MIN_EYE_COUNT} eye groups, "
            f"got {len(eyes_group)}"
        )


def _get_left_eye(eyes_group):
    """
    Return the left eye group from the eyes group.
    """
    _validate_eyes_group(eyes_group)
    return eyes_group[_LEFT_EYE_INDEX]


def _get_right_eye(eyes_group):
    """
    Return the right eye group from the eyes group.
    """
    _validate_eyes_group(eyes_group)
    return eyes_group[_RIGHT_EYE_INDEX]


def _close_single_eye(eye_group, *, squash_factor: float = DEFAULT_BLINK_SQUASH_FACTOR):
    """
    Return an animation that visually squashes one eye vertically.

    eye_group structure:
        eye_group[0] -> eye white
        eye_group[1] -> pupil
        eye_group[2] -> highlight
    """
    squash_factor = _validate_blink_factor(squash_factor)

    return ApplyMethod(
        eye_group.stretch,
        squash_factor,
        1,
        run_time=BLINK_CLOSE_TIME,
    )


def _open_single_eye(eye_group, *, squash_factor: float = DEFAULT_BLINK_SQUASH_FACTOR):
    """
    Return an animation that restores one eye vertically.

    This assumes the blink close step already squashed the eye group.
    """
    squash_factor = _validate_blink_factor(squash_factor)

    return ApplyMethod(
        eye_group.stretch,
        1.0 / squash_factor,
        1,
        run_time=BLINK_OPEN_TIME,
    )


# ============================================================
# Public blink builders
# ============================================================

def build_blink_close_animation(
    eyes_group,
    *,
    squash_factor: float = DEFAULT_BLINK_SQUASH_FACTOR,
):
    """
    Build the eye-closing half of a blink.

    eyes_group structure:
        eyes_group[0] -> left eye group
        eyes_group[1] -> right eye group
    """
    _validate_eyes_group(eyes_group)
    squash_factor = _validate_blink_factor(squash_factor)

    if LOG_ANIMATION_EVENTS:
        logger.info("Building blink close animation")

    left_eye = _get_left_eye(eyes_group)
    right_eye = _get_right_eye(eyes_group)

    if DEBUG_MODE:
        logger.debug(
            "Blink close | left_eye=%s right_eye=%s squash_factor=%.3f",
            getattr(left_eye, "name", "left_eye"),
            getattr(right_eye, "name", "right_eye"),
            squash_factor,
        )

    return AnimationGroup(
        _close_single_eye(left_eye, squash_factor=squash_factor),
        _close_single_eye(right_eye, squash_factor=squash_factor),
        lag_ratio=0.0,
    )


def build_blink_open_animation(
    eyes_group,
    *,
    squash_factor: float = DEFAULT_BLINK_SQUASH_FACTOR,
):
    """
    Build the eye-opening half of a blink.
    """
    _validate_eyes_group(eyes_group)
    squash_factor = _validate_blink_factor(squash_factor)

    if LOG_ANIMATION_EVENTS:
        logger.info("Building blink open animation")

    left_eye = _get_left_eye(eyes_group)
    right_eye = _get_right_eye(eyes_group)

    if DEBUG_MODE:
        logger.debug(
            "Blink open | left_eye=%s right_eye=%s squash_factor=%.3f",
            getattr(left_eye, "name", "left_eye"),
            getattr(right_eye, "name", "right_eye"),
            squash_factor,
        )

    return AnimationGroup(
        _open_single_eye(left_eye, squash_factor=squash_factor),
        _open_single_eye(right_eye, squash_factor=squash_factor),
        lag_ratio=0.0,
    )


def build_blink_animation(
    eyes_group,
    *,
    squash_factor: float = DEFAULT_BLINK_SQUASH_FACTOR,
):
    """
    Build a full blink animation:
    - close both eyes
    - reopen both eyes
    """
    _validate_eyes_group(eyes_group)
    squash_factor = _validate_blink_factor(squash_factor)

    if LOG_ANIMATION_EVENTS:
        logger.info("Building full blink animation")

    return AnimationGroup(
        build_blink_close_animation(
            eyes_group,
            squash_factor=squash_factor,
        ),
        build_blink_open_animation(
            eyes_group,
            squash_factor=squash_factor,
        ),
        lag_ratio=0.0,
    )