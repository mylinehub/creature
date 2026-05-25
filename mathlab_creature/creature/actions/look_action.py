# File: mathlab_creature/creature/actions/look_action.py

"""
Look action helpers for mathlab-mylinehub-creature
with cinematic procedural audio integration.

This file provides simple gaze-control helpers
for the creature's eyes.

Features:
- move pupils inside eyes
- support look directions
- procedural look sound
- soft educational eye timing
- optional sound toggle
- cinematic gaze motion
- safe audio integration

Design Goals:
- readable eye motion
- subtle expressive movement
- educational mascot style
- production-ready
- alive but not distracting

Audio Goals:
- tiny soft sweep
- subtle focus movement
- airy motion cue
- alive but not annoying
"""

from __future__ import annotations

from manimlib import AnimationGroup
from manimlib import ApplyMethod

from mathlab_creature.config.defaults import (
    DEBUG_MODE,
    LOG_ANIMATION_EVENTS,
)

from mathlab_creature.config.sizes import (
    PUPIL_MAX_OFFSET,
)

from mathlab_creature.config.timings import (
    LOOK_RETURN_TIME,
    LOOK_SHIFT_TIME,
)

from mathlab_creature.core.geometry import (
    point,
)

from mathlab_creature.core.logger import (
    get_logger,
)

from mathlab_creature.core.audio.helpers import (
    maybe_play_sound,
)

from mathlab_creature.core.audio.procedural import (
    play_look_sound,
)

logger = get_logger(__name__)


# ============================================================
# INTERNAL CONSTANTS
# ============================================================

_LEFT_EYE_INDEX = 0
_RIGHT_EYE_INDEX = 1

_EYE_WHITE_INDEX = 0
_PUPIL_INDEX = 1
_HIGHLIGHT_INDEX = 2

_MIN_EYE_COUNT = 2
_MIN_EYE_PART_COUNT = 3


# ============================================================
# LOOK DIRECTION MAP
# ============================================================

_LOOK_DIRECTION_MAP = {
    "center": point(
        0.0,
        0.0,
        0.0,
    ),
    "left": point(
        -PUPIL_MAX_OFFSET,
        0.0,
        0.0,
    ),
    "right": point(
        PUPIL_MAX_OFFSET,
        0.0,
        0.0,
    ),
    "up": point(
        0.0,
        PUPIL_MAX_OFFSET,
        0.0,
    ),
    "down": point(
        0.0,
        -PUPIL_MAX_OFFSET,
        0.0,
    ),
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


# ============================================================
# INTERNAL HELPERS
# ============================================================

def _validate_numeric(
    name: str,
    value: float | int,
) -> float:
    """
    Ensure numeric value.
    """

    if not isinstance(value, (int, float)):
        raise TypeError(
            f"{name} must be numeric, "
            f"got {type(value).__name__}"
        )

    return float(value)


def _validate_run_time(
    run_time: float,
) -> float:
    """
    Ensure positive runtime.
    """

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
    """
    Normalize and validate direction.
    """

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
            f"Unsupported direction_name "
            f"{direction_name!r}"
        )

    return normalized


def _validate_eyes_group(
    eyes_group,
) -> None:
    """
    Validate eye group structure.
    """

    if eyes_group is None:
        raise ValueError(
            "eyes_group must not be None"
        )

    if len(eyes_group) < _MIN_EYE_COUNT:
        raise ValueError(
            f"eyes_group must contain "
            f"{_MIN_EYE_COUNT} eyes"
        )


def _validate_eye_group(
    eye_group,
) -> None:
    """
    Validate single eye structure.
    """

    if eye_group is None:
        raise ValueError(
            "eye_group must not be None"
        )

    if len(eye_group) < _MIN_EYE_PART_COUNT:
        raise ValueError(
            f"eye_group must contain "
            f"{_MIN_EYE_PART_COUNT} parts"
        )


def _get_left_eye(
    eyes_group,
):
    """
    Return left eye group.
    """

    _validate_eyes_group(
        eyes_group
    )

    return eyes_group[
        _LEFT_EYE_INDEX
    ]


def _get_right_eye(
    eyes_group,
):
    """
    Return right eye group.
    """

    _validate_eyes_group(
        eyes_group
    )

    return eyes_group[
        _RIGHT_EYE_INDEX
    ]


def _get_eye_parts(
    eye_group,
):
    """
    Extract eye components.
    """

    _validate_eye_group(
        eye_group
    )

    eye_white = eye_group[
        _EYE_WHITE_INDEX
    ]

    pupil = eye_group[
        _PUPIL_INDEX
    ]

    highlight = eye_group[
        _HIGHLIGHT_INDEX
    ]

    return (
        eye_white,
        pupil,
        highlight,
    )


def _get_eye_center(
    eye_group,
):
    """
    Return eye center.
    """

    eye_white, _, _ = (
        _get_eye_parts(
            eye_group
        )
    )

    return eye_white.get_center()


def _get_look_offset(
    direction_name: str,
):
    """
    Return configured look offset.
    """

    direction_name = (
        _normalize_direction_name(
            direction_name
        )
    )

    return _LOOK_DIRECTION_MAP[
        direction_name
    ]


def _highlight_offset(
    highlight,
):
    """
    Offset highlight slightly.
    """

    return point(
        -highlight.radius * 0.5,
        highlight.radius * 0.5,
        0.0,
    )


def _target_positions_for_eye(
    eye_group,
    direction_name: str,
):
    """
    Compute pupil/highlight targets.
    """

    (
        _,
        pupil,
        highlight,
    ) = _get_eye_parts(
        eye_group
    )

    eye_center = _get_eye_center(
        eye_group
    )

    offset_vector = _get_look_offset(
        direction_name
    )

    pupil_target = (
        eye_center
        + offset_vector
    )

    highlight_target = (
        pupil_target
        + _highlight_offset(
            highlight
        )
    )

    return (
        pupil,
        highlight,
        pupil_target,
        highlight_target,
    )


def _build_single_eye_look_animation(
    eye_group,
    direction_name: str,
    run_time: float,
):
    """
    Build look animation for one eye.
    """

    direction_name = (
        _normalize_direction_name(
            direction_name
        )
    )

    run_time = _validate_run_time(
        run_time
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


# ============================================================
# AUDIO HELPERS
# ============================================================

def _play_look_audio(
    with_sound: bool = True,
):
    """
    Trigger procedural look sound safely.
    """

    maybe_play_sound(
        with_sound,
        play_look_sound,
    )


# ============================================================
# PUBLIC BUILDERS
# ============================================================

def build_look_animation(
    eyes_group,
    direction_name: str,
    *,
    run_time: float = LOOK_SHIFT_TIME,
    with_sound: bool = True,
):
    """
    Build directional gaze animation.

    Features:
    - subtle eye movement
    - procedural look sound
    - educational focus motion
    """

    _validate_eyes_group(
        eyes_group
    )

    direction_name = (
        _normalize_direction_name(
            direction_name
        )
    )

    run_time = _validate_run_time(
        run_time
    )

    if LOG_ANIMATION_EVENTS:

        logger.info(
            "Building look animation | direction=%s with_sound=%s",
            direction_name,
            with_sound,
        )

    # --------------------------------------------------------
    # AUDIO
    # --------------------------------------------------------

    _play_look_audio(
        with_sound=with_sound,
    )

    left_eye = _get_left_eye(
        eyes_group
    )

    right_eye = _get_right_eye(
        eyes_group
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
    eyes_group,
    *,
    run_time: float = LOOK_RETURN_TIME,
):
    """
    Return gaze to center.
    """

    _validate_eyes_group(
        eyes_group
    )

    run_time = _validate_run_time(
        run_time
    )

    if LOG_ANIMATION_EVENTS:

        logger.info(
            "Building look-center animation"
        )

    left_eye = _get_left_eye(
        eyes_group
    )

    right_eye = _get_right_eye(
        eyes_group
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
    eyes_group,
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

    Features:
    - optional procedural sound
    - soft educational eye rhythm
    - cinematic timing
    """

    _validate_eyes_group(
        eyes_group
    )

    direction_name = (
        _normalize_direction_name(
            direction_name
        )
    )

    look_run_time = _validate_run_time(
        look_run_time
    )

    return_run_time = _validate_run_time(
        return_run_time
    )

    if LOG_ANIMATION_EVENTS:

        logger.info(
            "Building look-and-return animation | direction=%s with_sound=%s",
            direction_name,
            with_sound,
        )

    return AnimationGroup(
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
        lag_ratio=0.0,
    )