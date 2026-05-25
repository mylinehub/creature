# File: mathlab_creature/creature/actions/point_action.py

"""
Point action helpers for mathlab-mylinehub-creature
with cinematic procedural audio integration.

This file provides a simple pointing animation for the creature.

Features:
- extend one arm into a pointing pose
- optional hold timing
- optional return to neutral
- procedural point cue sound
- educational presentation feel
- optional sound toggle
- cinematic gesture timing
- safe audio integration

Design Goals:
- readable movement
- educational mascot style
- expressive but subtle
- production-ready
- future extensible

Audio Goals:
- tiny attention cue
- educational focus sound
- soft gesture support
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
    POINT_HOLD_TIME,
    POINT_REACH_TIME,
    POINT_RETURN_TIME,
)

from mathlab_creature.core.logger import (
    get_logger,
)

from mathlab_creature.core.audio.helpers import (
    maybe_play_sound,
)

from mathlab_creature.core.audio.procedural import (
    play_point_sound,
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
    "group",
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


def _normalize_side(
    side: str,
) -> str:
    """
    Normalize and validate side.
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
    Validate point-action rig shape.
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
    Return directional rotation sign.
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

def _play_point_audio(
    with_sound: bool = True,
):
    """
    Trigger procedural point sound safely.
    """

    maybe_play_sound(
        with_sound,
        play_point_sound,
    )


# ============================================================
# PUBLIC BUILDERS
# ============================================================

def build_point_reach_animation(
    rig: dict,
    *,
    side: str = "right",
    point_degrees: float = 80.0,
    with_sound: bool = True,
):
    """
    Build pointing reach animation.

    Includes:
    - strong readable gesture
    - educational cue sound
    """

    _validate_rig(rig)

    side = _normalize_side(side)

    point_degrees = _validate_positive(
        "point_degrees",
        point_degrees,
    )

    if LOG_ANIMATION_EVENTS:

        logger.info(
            "Building point reach animation | side=%s point_degrees=%.3f with_sound=%s",
            side,
            point_degrees,
            with_sound,
        )

    # --------------------------------------------------------
    # AUDIO
    # --------------------------------------------------------

    _play_point_audio(
        with_sound=with_sound,
    )

    arm, hand = _get_arm_and_hand(
        rig,
        side,
    )

    signed_degrees = (
        _rotation_sign_for_side(side)
        * point_degrees
    )

    if DEBUG_MODE:

        logger.debug(
            "Point reach setup | side=%s arm=%s hand=%s signed_degrees=%.3f",
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
    rig: dict,
    *,
    hold_time: float = POINT_HOLD_TIME,
):
    """
    Build optional point hold.
    """

    _validate_rig(rig)

    hold_time = _validate_positive(
        "hold_time",
        hold_time,
    )

    if LOG_ANIMATION_EVENTS:

        logger.info(
            "Building point hold animation | hold_time=%.3f",
            hold_time,
        )

    creature_group = rig["group"]

    return ApplyMethod(
        creature_group.shift,
        [0.0, 0.0, 0.0],
        run_time=hold_time,
    )


def build_point_return_animation(
    rig: dict,
    *,
    side: str = "right",
    point_degrees: float = 80.0,
):
    """
    Return arm toward neutral pose.
    """

    _validate_rig(rig)

    side = _normalize_side(side)

    point_degrees = _validate_positive(
        "point_degrees",
        point_degrees,
    )

    if LOG_ANIMATION_EVENTS:

        logger.info(
            "Building point return animation | side=%s point_degrees=%.3f",
            side,
            point_degrees,
        )

    arm, hand = _get_arm_and_hand(
        rig,
        side,
    )

    signed_degrees = (
        -_rotation_sign_for_side(side)
        * point_degrees
    )

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
    with_sound: bool = True,
):
    """
    Build complete point action.

    Flow:
    - point reach
    - optional hold
    - optional return

    Features:
    - educational presentation feel
    - optional procedural sound
    - cinematic gesture timing
    """

    _validate_rig(rig)

    side = _normalize_side(side)

    point_degrees = _validate_positive(
        "point_degrees",
        point_degrees,
    )

    if not isinstance(hold, bool):
        raise TypeError(
            f"hold must be bool, "
            f"got {type(hold).__name__}"
        )

    if not isinstance(return_to_neutral, bool):
        raise TypeError(
            "return_to_neutral must be bool"
        )

    if not isinstance(with_sound, bool):
        raise TypeError(
            f"with_sound must be bool, "
            f"got {type(with_sound).__name__}"
        )

    hold_time = _validate_positive(
        "hold_time",
        hold_time,
    )

    if LOG_ANIMATION_EVENTS:

        logger.info(
            "Building full point animation | side=%s point_degrees=%.3f hold=%s hold_time=%.3f return_to_neutral=%s with_sound=%s",
            side,
            point_degrees,
            hold,
            hold_time,
            return_to_neutral,
            with_sound,
        )

    animations = [
        build_point_reach_animation(
            rig,
            side=side,
            point_degrees=point_degrees,
            with_sound=with_sound,
        )
    ]

    if hold:

        animations.append(
            build_point_hold_animation(
                rig,
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

    return AnimationGroup(
        *animations,
        lag_ratio=0.0,
    )