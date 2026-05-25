# File: mathlab_creature/creature/actions/wave_action.py

"""
Wave action helpers for mathlab-mylinehub-creature
with cinematic procedural audio integration.

This file provides a simple wave animation for the creature.

Features:
- wave using the right arm by default
- soft mascot motion
- procedural wave sound
- educational presentation feel
- optional sound toggle
- cinematic arm timing
- safe audio integration

Design Goals:
- readable movement
- simple and reliable
- expressive but subtle
- educational mascot style
- production-ready
- future extensible

Audio Goals:
- soft swish
- airy movement
- subtle gesture support
- alive but not annoying
"""

from __future__ import annotations

from math import radians

from manimlib import AnimationGroup
from manimlib import ApplyMethod

from mathlab_creature.config.defaults import (
    DEBUG_MODE,
    LOG_ANIMATION_EVENTS,
)

from mathlab_creature.config.timings import (
    ARM_RAISE_TIME,
    WAVE_BACK_TIME,
    WAVE_OUT_TIME,
)

from mathlab_creature.core.logger import (
    get_logger,
)

from mathlab_creature.core.audio.helpers import (
    maybe_play_sound,
)

from mathlab_creature.core.audio.procedural import (
    play_wave_sound,
)

logger = get_logger(__name__)


# ============================================================
# INTERNAL CONSTANTS
# ============================================================

_ALLOWED_SIDES = {
    "left",
    "right",
}

_REQUIRED_RIG_KEYS = (
    "arms",
)


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


def _validate_positive(
    name: str,
    value: float | int,
) -> float:
    """
    Ensure positive numeric value.
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


def _validate_cycles(
    cycles: int,
) -> int:
    """
    Ensure cycles is positive integer.
    """

    if not isinstance(cycles, int):
        raise TypeError(
            f"cycles must be int, "
            f"got {type(cycles).__name__}"
        )

    if cycles <= 0:
        raise ValueError(
            f"cycles must be > 0, got {cycles}"
        )

    return cycles


def _normalize_side(
    side: str,
) -> str:
    """
    Normalize waving side.
    """

    if not isinstance(side, str):
        raise TypeError(
            f"side must be string, "
            f"got {type(side).__name__}"
        )

    normalized = side.strip().lower()

    if normalized not in _ALLOWED_SIDES:
        raise ValueError(
            f"side must be one of "
            f"{_ALLOWED_SIDES}, "
            f"got {side!r}"
        )

    return normalized


def _validate_rig(
    rig: dict,
) -> None:
    """
    Validate minimum rig shape.
    """

    if not isinstance(rig, dict):
        raise TypeError(
            f"rig must be dict, "
            f"got {type(rig).__name__}"
        )

    missing = [
        key
        for key in _REQUIRED_RIG_KEYS
        if key not in rig
    ]

    if missing:
        raise KeyError(
            f"rig missing required keys: {missing}"
        )


def _get_arm_and_hand(
    rig: dict,
    side: str,
):
    """
    Return arm and hand for side.
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


def _rotation_sign_for_side(
    side: str,
) -> float:
    """
    Return rotation direction sign.
    """

    side = _normalize_side(side)

    return -1.0 if side == "right" else 1.0


def _hand_sync_animation(
    hand,
    arm,
    *,
    run_time: float,
):
    """
    Sync hand to arm endpoint.
    """

    run_time = _validate_positive(
        "run_time",
        run_time,
    )

    return ApplyMethod(
        hand.move_to,
        arm.get_end(),
        run_time=run_time,
    )


def _arm_rotate_animation(
    arm,
    degrees: float,
    *,
    run_time: float,
):
    """
    Build shoulder rotation animation.
    """

    run_time = _validate_positive(
        "run_time",
        run_time,
    )

    degrees = _validate_numeric(
        "degrees",
        degrees,
    )

    return ApplyMethod(
        arm.rotate,
        radians(degrees),
        {"about_point": arm.get_start()},
        run_time=run_time,
    )


# ============================================================
# AUDIO HELPERS
# ============================================================

def _play_wave_audio(
    with_sound: bool = True,
):
    """
    Trigger soft procedural wave sound.
    """

    maybe_play_sound(
        with_sound,
        play_wave_sound,
    )


# ============================================================
# PUBLIC BUILDERS
# ============================================================

def build_raise_arm_animation(
    rig: dict,
    *,
    side: str = "right",
    raise_degrees: float = 55.0,
):
    """
    Raise arm into wave-ready position.
    """

    _validate_rig(rig)

    side = _normalize_side(side)

    raise_degrees = _validate_positive(
        "raise_degrees",
        raise_degrees,
    )

    if LOG_ANIMATION_EVENTS:

        logger.info(
            "Building raise-arm animation | side=%s raise_degrees=%.3f",
            side,
            raise_degrees,
        )

    arm, hand = _get_arm_and_hand(
        rig,
        side,
    )

    signed_raise = (
        _rotation_sign_for_side(side)
        * raise_degrees
    )

    if DEBUG_MODE:

        logger.debug(
            "Raise arm setup | side=%s arm=%s hand=%s signed_raise=%.3f",
            side,
            getattr(
                arm,
                "name",
                "arm",
            ),
            getattr(
                hand,
                "name",
                "hand",
            ),
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
    with_sound: bool = True,
):
    """
    Build one small wave cycle.

    Includes:
    - outward swing
    - inward swing
    - soft procedural wave sound
    """

    _validate_rig(rig)

    side = _normalize_side(side)

    wave_degrees = _validate_positive(
        "wave_degrees",
        wave_degrees,
    )

    if LOG_ANIMATION_EVENTS:

        logger.info(
            "Building one wave cycle | side=%s wave_degrees=%.3f",
            side,
            wave_degrees,
        )

    # --------------------------------------------------------
    # AUDIO
    # --------------------------------------------------------

    _play_wave_audio(
        with_sound=with_sound,
    )

    arm, hand = _get_arm_and_hand(
        rig,
        side,
    )

    sign = _rotation_sign_for_side(
        side
    )

    # --------------------------------------------------------
    # WAVE OUT
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # WAVE BACK
    # --------------------------------------------------------

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
    with_sound: bool = True,
):
    """
    Build complete wave action.

    Flow:
    - raise arm
    - perform wave cycles

    Features:
    - optional procedural sound
    - cinematic timing
    - soft mascot motion
    """

    _validate_rig(rig)

    side = _normalize_side(side)

    cycles = _validate_cycles(
        cycles
    )

    raise_degrees = _validate_positive(
        "raise_degrees",
        raise_degrees,
    )

    wave_degrees = _validate_positive(
        "wave_degrees",
        wave_degrees,
    )

    if LOG_ANIMATION_EVENTS:

        logger.info(
            "Building full wave animation | side=%s cycles=%d raise_degrees=%.3f wave_degrees=%.3f with_sound=%s",
            side,
            cycles,
            raise_degrees,
            wave_degrees,
            with_sound,
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
                with_sound=with_sound,
            )
        )

    return AnimationGroup(
        *animations,
        lag_ratio=0.0,
    )