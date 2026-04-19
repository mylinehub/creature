"""
Look action helpers for mathlab-mylinehub-creature.

This file provides simple gaze-control helpers for the creature's eyes.

Version 1 goals:
- move pupils inside the eyes
- support looking left / right / up / down / center
- keep movement small and readable
- avoid moving pupils outside the eye whites

Important:
This file does not rebuild the eyes.
It only moves the pupil + highlight inside each eye group.
"""

from __future__ import annotations

from manimlib import AnimationGroup
from manimlib import ApplyMethod

from config.defaults import DEBUG_MODE
from config.defaults import LOG_ANIMATION_EVENTS
from config.sizes import PUPIL_MAX_OFFSET
from config.timings import LOOK_RETURN_TIME
from config.timings import LOOK_SHIFT_TIME
from core.geometry import point
from core.logger import get_logger

logger = get_logger(__name__)


# ============================================================
# Internal constants
# ============================================================

_LEFT_EYE_INDEX = 0
_RIGHT_EYE_INDEX = 1
_EYE_WHITE_INDEX = 0
_PUPIL_INDEX = 1
_HIGHLIGHT_INDEX = 2

_MIN_EYE_COUNT = 2
_MIN_EYE_PART_COUNT = 3


# ============================================================
# Direction map
# ============================================================

_LOOK_DIRECTION_MAP = {
    "center": point(0.0, 0.0, 0.0),
    "left": point(-PUPIL_MAX_OFFSET, 0.0, 0.0),
    "right": point(PUPIL_MAX_OFFSET, 0.0, 0.0),
    "up": point(0.0, PUPIL_MAX_OFFSET, 0.0),
    "down": point(0.0, -PUPIL_MAX_OFFSET, 0.0),
    "up_left": point(-PUPIL_MAX_OFFSET * 0.75, PUPIL_MAX_OFFSET * 0.75, 0.0),
    "up_right": point(PUPIL_MAX_OFFSET * 0.75, PUPIL_MAX_OFFSET * 0.75, 0.0),
    "down_left": point(-PUPIL_MAX_OFFSET * 0.75, -PUPIL_MAX_OFFSET * 0.75, 0.0),
    "down_right": point(PUPIL_MAX_OFFSET * 0.75, -PUPIL_MAX_OFFSET * 0.75, 0.0),
}


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


def _validate_run_time(run_time: float) -> float:
    """
    Ensure a valid positive run time.
    """
    run_time = _validate_numeric("run_time", run_time)
    if run_time <= 0:
        raise ValueError(f"run_time must be > 0, got {run_time}")
    return run_time


def _normalize_direction_name(direction_name: str) -> str:
    """
    Normalize and validate a direction name.
    """
    if not isinstance(direction_name, str):
        raise TypeError(
            f"direction_name must be a string, got {type(direction_name).__name__}"
        )

    normalized = direction_name.strip().lower().replace("-", "_").replace(" ", "_")

    if normalized not in _LOOK_DIRECTION_MAP:
        raise ValueError(
            f"Unsupported direction_name {direction_name!r}. "
            f"Allowed values: {sorted(_LOOK_DIRECTION_MAP.keys())}"
        )

    return normalized


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


def _validate_eye_group(eye_group) -> None:
    """
    Validate the expected single-eye-group structure.

    Expected:
        eye_group[0] -> eye white
        eye_group[1] -> pupil
        eye_group[2] -> highlight
    """
    if eye_group is None:
        raise ValueError("eye_group must not be None")

    if len(eye_group) < _MIN_EYE_PART_COUNT:
        raise ValueError(
            f"eye_group must contain at least {_MIN_EYE_PART_COUNT} parts, "
            f"got {len(eye_group)}"
        )


def _get_left_eye(eyes_group):
    """
    Return the left eye group.
    """
    _validate_eyes_group(eyes_group)
    return eyes_group[_LEFT_EYE_INDEX]


def _get_right_eye(eyes_group):
    """
    Return the right eye group.
    """
    _validate_eyes_group(eyes_group)
    return eyes_group[_RIGHT_EYE_INDEX]


def _get_eye_parts(eye_group):
    """
    Extract standard eye group parts.

    eye_group structure:
        eye_group[0] -> eye white
        eye_group[1] -> pupil
        eye_group[2] -> highlight
    """
    _validate_eye_group(eye_group)

    eye_white = eye_group[_EYE_WHITE_INDEX]
    pupil = eye_group[_PUPIL_INDEX]
    highlight = eye_group[_HIGHLIGHT_INDEX]

    return eye_white, pupil, highlight


def _get_eye_center(eye_group):
    """
    Return the center of the eye white.
    """
    eye_white, _, _ = _get_eye_parts(eye_group)
    return eye_white.get_center()


def _get_look_offset(direction_name: str):
    """
    Return the configured pupil offset vector for one named look direction.
    """
    direction_name = _normalize_direction_name(direction_name)
    return _LOOK_DIRECTION_MAP[direction_name]


def _highlight_offset(highlight) -> object:
    """
    Return the highlight offset relative to the pupil center.

    The highlight sits slightly top-left of the pupil center so the eyes
    stay lively and readable.
    """
    return point(
        -highlight.radius * 0.5,
        highlight.radius * 0.5,
        0.0,
    )


def _target_positions_for_eye(eye_group, direction_name: str):
    """
    Compute target positions for pupil and highlight inside one eye.
    """
    _, pupil, highlight = _get_eye_parts(eye_group)
    eye_center = _get_eye_center(eye_group)
    offset_vector = _get_look_offset(direction_name)

    pupil_target = eye_center + offset_vector
    highlight_target = pupil_target + _highlight_offset(highlight)

    return pupil, highlight, pupil_target, highlight_target


def _build_single_eye_look_animation(
    eye_group,
    direction_name: str,
    run_time: float,
):
    """
    Build pupil + highlight move animation for one eye.
    """
    direction_name = _normalize_direction_name(direction_name)
    run_time = _validate_run_time(run_time)

    pupil, highlight, pupil_target, highlight_target = _target_positions_for_eye(
        eye_group,
        direction_name,
    )

    return AnimationGroup(
        ApplyMethod(pupil.move_to, pupil_target, run_time=run_time),
        ApplyMethod(highlight.move_to, highlight_target, run_time=run_time),
        lag_ratio=0.0,
    )


# ============================================================
# Public builders
# ============================================================

def build_look_animation(
    eyes_group,
    direction_name: str,
    *,
    run_time: float = LOOK_SHIFT_TIME,
):
    """
    Build an animation that moves both eyes to look in one direction.

    Valid direction names:
    - center
    - left
    - right
    - up
    - down
    - up_left
    - up_right
    - down_left
    - down_right
    """
    _validate_eyes_group(eyes_group)
    direction_name = _normalize_direction_name(direction_name)
    run_time = _validate_run_time(run_time)

    if LOG_ANIMATION_EVENTS:
        logger.info("Building look animation | direction=%s", direction_name)

    left_eye = _get_left_eye(eyes_group)
    right_eye = _get_right_eye(eyes_group)

    if DEBUG_MODE:
        logger.debug(
            "Look animation targets prepared | direction=%s left_eye=%s right_eye=%s",
            direction_name,
            getattr(left_eye, "name", "left_eye"),
            getattr(right_eye, "name", "right_eye"),
        )

    return AnimationGroup(
        _build_single_eye_look_animation(left_eye, direction_name, run_time),
        _build_single_eye_look_animation(right_eye, direction_name, run_time),
        lag_ratio=0.0,
    )


def build_look_center_animation(
    eyes_group,
    *,
    run_time: float = LOOK_RETURN_TIME,
):
    """
    Build animation to return gaze to center.
    """
    _validate_eyes_group(eyes_group)
    run_time = _validate_run_time(run_time)

    if LOG_ANIMATION_EVENTS:
        logger.info("Building look-to-center animation")

    left_eye = _get_left_eye(eyes_group)
    right_eye = _get_right_eye(eyes_group)

    return AnimationGroup(
        _build_single_eye_look_animation(left_eye, "center", run_time),
        _build_single_eye_look_animation(right_eye, "center", run_time),
        lag_ratio=0.0,
    )


def build_look_and_return_animation(
    eyes_group,
    direction_name: str,
    *,
    look_run_time: float = LOOK_SHIFT_TIME,
    return_run_time: float = LOOK_RETURN_TIME,
):
    """
    Build a full look action:
    - move gaze to direction
    - return gaze to center
    """
    _validate_eyes_group(eyes_group)
    direction_name = _normalize_direction_name(direction_name)
    look_run_time = _validate_run_time(look_run_time)
    return_run_time = _validate_run_time(return_run_time)

    if LOG_ANIMATION_EVENTS:
        logger.info(
            "Building look-and-return animation | direction=%s",
            direction_name,
        )

    return AnimationGroup(
        build_look_animation(
            eyes_group,
            direction_name,
            run_time=look_run_time,
        ),
        build_look_center_animation(
            eyes_group,
            run_time=return_run_time,
        ),
        lag_ratio=0.0,
    )