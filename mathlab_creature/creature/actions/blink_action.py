"""
Blink action for mathlab-mylinehub-creature.

This file builds blink animations.

Architecture rule:
- blink_action.py does not build eyes
- blink_action.py does not move creature root
- blink_action.py acts on FaceRig or eyes group
- blink_action.py controls only eye blink animation
- audio is optional and safely ignored if audio modules are unavailable

Connection chain:

    blink_action.py
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
from mathlab_creature.config.timings import BLINK_CLOSE_TIME
from mathlab_creature.config.timings import BLINK_OPEN_TIME
from mathlab_creature.core.logger import get_logger


logger = get_logger(__name__)


try:
    from mathlab_creature.core.audio.helpers import maybe_play_sound
    from mathlab_creature.core.audio.procedural import play_blink_sound
except Exception:
    maybe_play_sound = None
    play_blink_sound = None


_LEFT_EYE_INDEX = 0
_RIGHT_EYE_INDEX = 1
_MIN_EYE_COUNT = 2

DEFAULT_BLINK_SQUASH_FACTOR = 0.08


def _validate_numeric(name: str, value: float | int) -> float:
    if not isinstance(value, (int, float)):
        raise TypeError(
            f"{name} must be numeric, got {type(value).__name__}"
        )

    return float(value)


def _validate_blink_factor(factor: float) -> float:
    factor = _validate_numeric("factor", factor)

    if factor <= 0:
        raise ValueError(f"factor must be > 0, got {factor}")

    return factor


def _resolve_eyes_group(face_or_eyes):
    """
    Accept either:
    - FaceRig
    - face group with .eyes
    - eyes VGroup directly
    """
    if face_or_eyes is None:
        raise ValueError("face_or_eyes must not be None")

    if hasattr(face_or_eyes, "get_eyes"):
        return face_or_eyes.get_eyes()

    if hasattr(face_or_eyes, "eyes"):
        return face_or_eyes.eyes

    return face_or_eyes


def _validate_eyes_group(eyes_group) -> None:
    if eyes_group is None:
        raise ValueError("eyes_group must not be None")

    if len(eyes_group) < _MIN_EYE_COUNT:
        raise ValueError(
            f"eyes_group must contain at least {_MIN_EYE_COUNT} eye groups, "
            f"got {len(eyes_group)}"
        )


def _get_left_eye(eyes_group):
    _validate_eyes_group(eyes_group)
    return getattr(eyes_group, "left_eye", eyes_group[_LEFT_EYE_INDEX])


def _get_right_eye(eyes_group):
    _validate_eyes_group(eyes_group)
    return getattr(eyes_group, "right_eye", eyes_group[_RIGHT_EYE_INDEX])


def _close_single_eye(
    eye_group,
    *,
    squash_factor: float = DEFAULT_BLINK_SQUASH_FACTOR,
):
    squash_factor = _validate_blink_factor(squash_factor)

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
    squash_factor = _validate_blink_factor(squash_factor)

    return ApplyMethod(
        eye_group.stretch,
        1.0 / squash_factor,
        1,
        run_time=BLINK_OPEN_TIME,
    )


def _play_blink_audio(with_sound: bool = True) -> None:
    """
    Trigger blink sound only if audio system exists.
    """
    if not with_sound:
        return

    if maybe_play_sound is None or play_blink_sound is None:
        return

    maybe_play_sound(
        with_sound,
        play_blink_sound,
    )


def build_blink_close_animation(
    face_or_eyes,
    *,
    squash_factor: float = DEFAULT_BLINK_SQUASH_FACTOR,
):
    """
    Build eye-closing half of blink.
    """
    eyes_group = _resolve_eyes_group(face_or_eyes)
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
    face_or_eyes,
    *,
    squash_factor: float = DEFAULT_BLINK_SQUASH_FACTOR,
):
    """
    Build eye-opening half of blink.
    """
    eyes_group = _resolve_eyes_group(face_or_eyes)
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
    face_or_eyes,
    *,
    squash_factor: float = DEFAULT_BLINK_SQUASH_FACTOR,
    with_sound: bool = True,
):
    """
    Build full blink animation.
    """
    eyes_group = _resolve_eyes_group(face_or_eyes)
    _validate_eyes_group(eyes_group)

    squash_factor = _validate_blink_factor(squash_factor)

    if LOG_ANIMATION_EVENTS:
        logger.info("Building full blink animation")

    _play_blink_audio(
        with_sound=with_sound,
    )

    return Succession(
        build_blink_close_animation(
            eyes_group,
            squash_factor=squash_factor,
        ),
        build_blink_open_animation(
            eyes_group,
            squash_factor=squash_factor,
        ),
    )


__all__ = [
    "DEFAULT_BLINK_SQUASH_FACTOR",
    "build_blink_close_animation",
    "build_blink_open_animation",
    "build_blink_animation",
]