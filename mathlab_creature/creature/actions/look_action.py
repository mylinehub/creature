"""
Look action for mathlab-mylinehub-creature.

This file builds gaze/look animations.

Architecture rule:
- look_action.py does not build eyes
- look_action.py does not move creature root
- look_action.py acts on FaceRig or eyes group
- look_action.py controls only local pupil/highlight movement
- audio is optional and safely ignored if audio modules are unavailable

Connection chain:

    look_action.py
        |
        FaceRig / eyes group
            |
            Eyes
"""

from __future__ import annotations

from manimlib import AnimationGroup
from manimlib import ApplyMethod
from manimlib import Succession

from mathlab_creature.config.defaults import DEBUG_MODE
from mathlab_creature.config.defaults import LOG_ANIMATION_EVENTS
from mathlab_creature.config.sizes import PUPIL_MAX_OFFSET
from mathlab_creature.config.timings import LOOK_RETURN_TIME
from mathlab_creature.config.timings import LOOK_SHIFT_TIME
from mathlab_creature.core.geometry import point
from mathlab_creature.core.logger import get_logger


logger = get_logger(__name__)


try:
    from mathlab_creature.core.audio.helpers import maybe_play_sound
    from mathlab_creature.core.audio.procedural import play_look_sound
except Exception:
    maybe_play_sound = None
    play_look_sound = None


_LEFT_EYE_INDEX = 0
_RIGHT_EYE_INDEX = 1

_EYE_WHITE_INDEX = 0
_PUPIL_INDEX = 1
_HIGHLIGHT_INDEX = 2

_MIN_EYE_COUNT = 2
_MIN_EYE_PART_COUNT = 3


_LOOK_DIRECTION_MAP = {
    "center": point(0.0, 0.0, 0.0),
    "left": point(-PUPIL_MAX_OFFSET, 0.0, 0.0),
    "right": point(PUPIL_MAX_OFFSET, 0.0, 0.0),
    "up": point(0.0, PUPIL_MAX_OFFSET, 0.0),
    "down": point(0.0, -PUPIL_MAX_OFFSET, 0.0),
    "up_left": point(
        -PUPIL_MAX_OFFSET * 0.75,
        PUPIL_MAX_OFFSET * 0.75,
        0.0,
    ),
    "up_right": point(
        PUPIL_MAX_OFFSET * 0.75,
        PUPIL_MAX_OFFSET * 0.75,
        0.0,
    ),
    "down_left": point(
        -PUPIL_MAX_OFFSET * 0.75,
        -PUPIL_MAX_OFFSET * 0.75,
        0.0,
    ),
    "down_right": point(
        PUPIL_MAX_OFFSET * 0.75,
        -PUPIL_MAX_OFFSET * 0.75,
        0.0,
    ),
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


def _validate_run_time(
    run_time: float,
) -> float:
    run_time = _validate_numeric(
        "run_time",
        run_time,
    )

    if run_time <= 0:
        raise ValueError(
            f"run_time must be > 0, got {run_time}"
        )

    return run_time


def _normalize_direction_name(
    direction_name: str,
) -> str:
    if not isinstance(direction_name, str):
        raise TypeError(
            "direction_name must be string"
        )

    normalized = (
        direction_name
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )

    if normalized not in _LOOK_DIRECTION_MAP:
        raise ValueError(
            f"Unsupported direction_name {direction_name!r}. "
            f"Allowed values: {sorted(_LOOK_DIRECTION_MAP)}"
        )

    return normalized


def _resolve_eyes_group(
    face_or_eyes,
):
    """
    Accept either:
    - FaceRig
    - face group with .eyes
    - eyes VGroup directly
    """
    if face_or_eyes is None:
        raise ValueError(
            "face_or_eyes must not be None"
        )

    if hasattr(face_or_eyes, "get_eyes"):
        return face_or_eyes.get_eyes()

    if hasattr(face_or_eyes, "eyes"):
        return face_or_eyes.eyes

    return face_or_eyes


def _validate_eyes_group(
    eyes_group,
) -> None:
    if eyes_group is None:
        raise ValueError(
            "eyes_group must not be None"
        )

    if len(eyes_group) < _MIN_EYE_COUNT:
        raise ValueError(
            f"eyes_group must contain {_MIN_EYE_COUNT} eyes"
        )


def _validate_eye_group(
    eye_group,
) -> None:
    if eye_group is None:
        raise ValueError(
            "eye_group must not be None"
        )

    if len(eye_group) < _MIN_EYE_PART_COUNT:
        raise ValueError(
            f"eye_group must contain {_MIN_EYE_PART_COUNT} parts"
        )


def _get_left_eye(
    eyes_group,
):
    _validate_eyes_group(
        eyes_group,
    )

    return getattr(
        eyes_group,
        "left_eye",
        eyes_group[_LEFT_EYE_INDEX],
    )


def _get_right_eye(
    eyes_group,
):
    _validate_eyes_group(
        eyes_group,
    )

    return getattr(
        eyes_group,
        "right_eye",
        eyes_group[_RIGHT_EYE_INDEX],
    )


def _get_eye_parts(
    eye_group,
):
    _validate_eye_group(
        eye_group,
    )

    eye_white = getattr(
        eye_group,
        "eye_white",
        eye_group[_EYE_WHITE_INDEX],
    )

    pupil = getattr(
        eye_group,
        "pupil",
        eye_group[_PUPIL_INDEX],
    )

    highlight = getattr(
        eye_group,
        "highlight",
        eye_group[_HIGHLIGHT_INDEX],
    )

    return eye_white, pupil, highlight


def _get_eye_center(
    eye_group,
):
    if hasattr(eye_group, "eye_center"):
        return eye_group.eye_center

    eye_white, _, _ = _get_eye_parts(
        eye_group,
    )

    return eye_white.get_center()


def _get_look_offset(
    direction_name: str,
):
    direction_name = _normalize_direction_name(
        direction_name,
    )

    return _LOOK_DIRECTION_MAP[direction_name]


def _highlight_offset(
    highlight,
):
    radius = getattr(
        highlight,
        "radius",
        0.03,
    )

    return point(
        -radius * 0.5,
        radius * 0.5,
        0.0,
    )


def _target_positions_for_eye(
    eye_group,
    direction_name: str,
):
    _, pupil, highlight = _get_eye_parts(
        eye_group,
    )

    eye_center = _get_eye_center(
        eye_group,
    )

    offset_vector = _get_look_offset(
        direction_name,
    )

    pupil_target = eye_center + offset_vector
    highlight_target = pupil_target + _highlight_offset(
        highlight,
    )

    return pupil, highlight, pupil_target, highlight_target


def _build_single_eye_look_animation(
    eye_group,
    direction_name: str,
    run_time: float,
):
    direction_name = _normalize_direction_name(
        direction_name,
    )
    run_time = _validate_run_time(
        run_time,
    )

    (
        pupil,
        highlight,
        pupil_target,
        highlight_target,
    ) = _target_positions_for_eye(
        eye_group,
        direction_name,
    )

    return AnimationGroup(
        ApplyMethod(
            pupil.move_to,
            pupil_target,
            run_time=run_time,
        ),
        ApplyMethod(
            highlight.move_to,
            highlight_target,
            run_time=run_time,
        ),
        lag_ratio=0.0,
    )


def _play_look_audio(
    with_sound: bool = True,
) -> None:
    if not with_sound:
        return

    if maybe_play_sound is None or play_look_sound is None:
        return

    maybe_play_sound(
        with_sound,
        play_look_sound,
    )


def build_look_animation(
    face_or_eyes,
    direction_name: str,
    *,
    run_time: float = LOOK_SHIFT_TIME,
    with_sound: bool = True,
):
    """
    Build directional gaze animation.
    """
    eyes_group = _resolve_eyes_group(
        face_or_eyes,
    )
    _validate_eyes_group(
        eyes_group,
    )

    direction_name = _normalize_direction_name(
        direction_name,
    )
    run_time = _validate_run_time(
        run_time,
    )

    if LOG_ANIMATION_EVENTS:
        logger.info(
            "Building look animation | direction=%s with_sound=%s",
            direction_name,
            with_sound,
        )

    _play_look_audio(
        with_sound=with_sound,
    )

    left_eye = _get_left_eye(
        eyes_group,
    )
    right_eye = _get_right_eye(
        eyes_group,
    )

    if DEBUG_MODE:
        logger.debug(
            "Look targets prepared | direction=%s",
            direction_name,
        )

    return AnimationGroup(
        _build_single_eye_look_animation(
            left_eye,
            direction_name,
            run_time,
        ),
        _build_single_eye_look_animation(
            right_eye,
            direction_name,
            run_time,
        ),
        lag_ratio=0.0,
    )


def build_look_center_animation(
    face_or_eyes,
    *,
    run_time: float = LOOK_RETURN_TIME,
):
    """
    Return gaze to center.
    """
    eyes_group = _resolve_eyes_group(
        face_or_eyes,
    )
    _validate_eyes_group(
        eyes_group,
    )

    run_time = _validate_run_time(
        run_time,
    )

    if LOG_ANIMATION_EVENTS:
        logger.info(
            "Building look-center animation"
        )

    left_eye = _get_left_eye(
        eyes_group,
    )
    right_eye = _get_right_eye(
        eyes_group,
    )

    return AnimationGroup(
        _build_single_eye_look_animation(
            left_eye,
            "center",
            run_time,
        ),
        _build_single_eye_look_animation(
            right_eye,
            "center",
            run_time,
        ),
        lag_ratio=0.0,
    )


def build_look_and_return_animation(
    face_or_eyes,
    direction_name: str,
    *,
    look_run_time: float = LOOK_SHIFT_TIME,
    return_run_time: float = LOOK_RETURN_TIME,
    with_sound: bool = True,
):
    """
    Build complete look action.

    Flow:
    - look toward direction
    - return to center
    """
    eyes_group = _resolve_eyes_group(
        face_or_eyes,
    )
    _validate_eyes_group(
        eyes_group,
    )

    direction_name = _normalize_direction_name(
        direction_name,
    )
    look_run_time = _validate_run_time(
        look_run_time,
    )
    return_run_time = _validate_run_time(
        return_run_time,
    )

    if LOG_ANIMATION_EVENTS:
        logger.info(
            "Building look-and-return animation | direction=%s with_sound=%s",
            direction_name,
            with_sound,
        )

    return Succession(
        build_look_animation(
            eyes_group,
            direction_name,
            run_time=look_run_time,
            with_sound=with_sound,
        ),
        build_look_center_animation(
            eyes_group,
            run_time=return_run_time,
        ),
    )


__all__ = [
    "build_look_animation",
    "build_look_center_animation",
    "build_look_and_return_animation",
]