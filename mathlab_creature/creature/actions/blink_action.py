# File: mathlab_creature/creature/actions/blink_action.py

"""
Blink action helpers for mathlab-mylinehub-creature
with cinematic procedural audio integration.

This file provides blink-related utilities for the creature.

Features:
- lightweight blink effect
- procedural blink sound
- soft mascot eye timing
- educational character rhythm
- safe audio integration
- optional sound toggle

Design Goals:
- simple
- animation-safe
- production-ready
- subtle expressive motion
- alive but not annoying

Audio Goals:
- tiny cute blink sound
- subtle airy transient
- barely noticeable
- expressive but soft
"""

from __future__ import annotations

from manimlib import AnimationGroup
from manimlib import ApplyMethod

from mathlab_creature.config.defaults import DEBUG_MODE
from mathlab_creature.config.defaults import LOG_ANIMATION_EVENTS

from mathlab_creature.config.timings import (
    BLINK_CLOSE_TIME,
    BLINK_OPEN_TIME,
)

from mathlab_creature.core.logger import (
    get_logger,
)

from mathlab_creature.core.audio.helpers import (
    maybe_play_sound,
)

from mathlab_creature.core.audio.procedural import (
    play_blink_sound,
)

logger = get_logger(__name__)


# ============================================================
# INTERNAL CONSTANTS
# ============================================================

_LEFT_EYE_INDEX = 0
_RIGHT_EYE_INDEX = 1
_MIN_EYE_COUNT = 2

# Lower means flatter eyes during blink close.
DEFAULT_BLINK_SQUASH_FACTOR = 0.08


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


def _validate_blink_factor(
    factor: float,
) -> float:
    """
    Validate blink squash factor.
    """

    factor = _validate_numeric(
        "factor",
        factor,
    )

    if factor <= 0:
        raise ValueError(
            f"factor must be > 0, got {factor}"
        )

    return factor


def _validate_eyes_group(
    eyes_group,
) -> None:
    """
    Validate expected eyes structure.
    """

    if eyes_group is None:
        raise ValueError(
            "eyes_group must not be None"
        )

    if len(eyes_group) < _MIN_EYE_COUNT:
        raise ValueError(
            f"eyes_group must contain at least "
            f"{_MIN_EYE_COUNT} eye groups, "
            f"got {len(eyes_group)}"
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


def _close_single_eye(
    eye_group,
    *,
    squash_factor: float = DEFAULT_BLINK_SQUASH_FACTOR,
):
    """
    Create close-eye animation.
    """

    squash_factor = (
        _validate_blink_factor(
            squash_factor
        )
    )

    return ApplyMethod(
        eye_group.stretch,
        squash_factor,
        1,
        run_time=BLINK_CLOSE_TIME,
    )


def _open_single_eye(
    eye_group,
    *,
    squash_factor: float = DEFAULT_BLINK_SQUASH_FACTOR,
):
    """
    Create reopen-eye animation.
    """

    squash_factor = (
        _validate_blink_factor(
            squash_factor
        )
    )

    return ApplyMethod(
        eye_group.stretch,
        1.0 / squash_factor,
        1,
        run_time=BLINK_OPEN_TIME,
    )


# ============================================================
# AUDIO HELPERS
# ============================================================

def _play_blink_audio(
    with_sound: bool = True,
):
    """
    Trigger procedural blink sound safely.
    """

    maybe_play_sound(
        with_sound,
        play_blink_sound,
    )


# ============================================================
# PUBLIC BLINK BUILDERS
# ============================================================

def build_blink_close_animation(
    eyes_group,
    *,
    squash_factor: float = DEFAULT_BLINK_SQUASH_FACTOR,
):
    """
    Build eye-closing half of blink.
    """

    _validate_eyes_group(
        eyes_group
    )

    squash_factor = (
        _validate_blink_factor(
            squash_factor
        )
    )

    if LOG_ANIMATION_EVENTS:
        logger.info(
            "Building blink close animation"
        )

    left_eye = _get_left_eye(
        eyes_group
    )

    right_eye = _get_right_eye(
        eyes_group
    )

    if DEBUG_MODE:
        logger.debug(
            "Blink close | left_eye=%s right_eye=%s squash_factor=%.3f",
            getattr(
                left_eye,
                "name",
                "left_eye",
            ),
            getattr(
                right_eye,
                "name",
                "right_eye",
            ),
            squash_factor,
        )

    return AnimationGroup(
        _close_single_eye(
            left_eye,
            squash_factor=squash_factor,
        ),
        _close_single_eye(
            right_eye,
            squash_factor=squash_factor,
        ),
        lag_ratio=0.0,
    )


def build_blink_open_animation(
    eyes_group,
    *,
    squash_factor: float = DEFAULT_BLINK_SQUASH_FACTOR,
):
    """
    Build eye-opening half of blink.
    """

    _validate_eyes_group(
        eyes_group
    )

    squash_factor = (
        _validate_blink_factor(
            squash_factor
        )
    )

    if LOG_ANIMATION_EVENTS:
        logger.info(
            "Building blink open animation"
        )

    left_eye = _get_left_eye(
        eyes_group
    )

    right_eye = _get_right_eye(
        eyes_group
    )

    if DEBUG_MODE:
        logger.debug(
            "Blink open | left_eye=%s right_eye=%s squash_factor=%.3f",
            getattr(
                left_eye,
                "name",
                "left_eye",
            ),
            getattr(
                right_eye,
                "name",
                "right_eye",
            ),
            squash_factor,
        )

    return AnimationGroup(
        _open_single_eye(
            left_eye,
            squash_factor=squash_factor,
        ),
        _open_single_eye(
            right_eye,
            squash_factor=squash_factor,
        ),
        lag_ratio=0.0,
    )


def build_blink_animation(
    eyes_group,
    *,
    squash_factor: float = DEFAULT_BLINK_SQUASH_FACTOR,
    with_sound: bool = True,
):
    """
    Build full blink animation.

    Features:
    - close eyes
    - reopen eyes
    - optional procedural sound
    """

    _validate_eyes_group(
        eyes_group
    )

    squash_factor = (
        _validate_blink_factor(
            squash_factor
        )
    )

    if LOG_ANIMATION_EVENTS:
        logger.info(
            "Building full blink animation"
        )

    # --------------------------------------------------------
    # AUDIO
    # --------------------------------------------------------

    _play_blink_audio(
        with_sound=with_sound,
    )

    # --------------------------------------------------------
    # ANIMATION
    # --------------------------------------------------------

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