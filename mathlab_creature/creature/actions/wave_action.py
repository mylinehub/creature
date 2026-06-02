"""
Wave action for mathlab-mylinehub-creature.

This file builds wave animations for one connected creature.

Architecture rule:
- wave_action.py does not build arms or hands
- wave_action.py works through ArmRig, arm rig group, or rig map
- wave_action.py moves arm system only through rig-owned arm/hand references
- audio is optional and safely ignored if audio modules are unavailable
"""

from __future__ import annotations

from math import radians

from manimlib import AnimationGroup
from manimlib import ApplyMethod
from manimlib import Succession

from mathlab_creature.config.defaults import DEBUG_MODE
from mathlab_creature.config.defaults import LOG_ANIMATION_EVENTS
from mathlab_creature.config.timings import ARM_RAISE_TIME
from mathlab_creature.config.timings import WAVE_BACK_TIME
from mathlab_creature.config.timings import WAVE_OUT_TIME
from mathlab_creature.core.logger import get_logger


logger = get_logger(__name__)


try:
    from mathlab_creature.core.audio.helpers import maybe_play_sound
    from mathlab_creature.core.audio.procedural import play_wave_sound
except Exception:
    maybe_play_sound = None
    play_wave_sound = None


_ALLOWED_SIDES = {"left", "right"}


def _validate_numeric(name: str, value: float | int) -> float:
    if not isinstance(value, (int, float)):
        raise TypeError(
            f"{name} must be numeric, got {type(value).__name__}"
        )
    return float(value)


def _validate_positive(name: str, value: float | int) -> float:
    value = _validate_numeric(name, value)
    if value <= 0:
        raise ValueError(f"{name} must be > 0, got {value}")
    return value


def _validate_cycles(cycles: int) -> int:
    if not isinstance(cycles, int):
        raise TypeError(f"cycles must be int, got {type(cycles).__name__}")
    if cycles <= 0:
        raise ValueError(f"cycles must be > 0, got {cycles}")
    return cycles


def _normalize_side(side: str) -> str:
    if not isinstance(side, str):
        raise TypeError(f"side must be str, got {type(side).__name__}")

    normalized = side.strip().lower()

    if normalized not in _ALLOWED_SIDES:
        raise ValueError(
            f"side must be one of {_ALLOWED_SIDES}, got {side!r}"
        )

    return normalized


def _resolve_arm_rig_group(rig):
    """
    Accept:
    - ArmRig object
    - arm rig group
    - rig map dict
    """
    if rig is None:
        raise ValueError("rig must not be None")

    if hasattr(rig, "get_group"):
        return rig.get_group()

    if isinstance(rig, dict):
        if "rig" in rig and hasattr(rig["rig"], "get_group"):
            return rig["rig"].get_group()

        if "group" in rig:
            return rig["group"]

    return rig


def _get_arm_system(rig, side: str):
    side = _normalize_side(side)

    if hasattr(rig, "get_left_system") and side == "left":
        return rig.get_left_system()

    if hasattr(rig, "get_right_system") and side == "right":
        return rig.get_right_system()

    group = _resolve_arm_rig_group(rig)

    if side == "left":
        if hasattr(group, "left_system"):
            return group.left_system
        return group[0]

    if hasattr(group, "right_system"):
        return group.right_system

    return group[1]


def _get_arm_and_hand(rig, side: str):
    system = _get_arm_system(rig, side)

    arm = getattr(system, "arm_line", None)
    if arm is None:
        arm = getattr(system, "arm", None)

    hand = getattr(system, "hand", None)

    if arm is None:
        raise AttributeError("arm system must have arm_line or arm metadata")

    if hand is None:
        raise AttributeError("arm system must have hand metadata")

    return arm, hand


def _get_arm_start(arm):
    if hasattr(arm, "get_start"):
        return arm.get_start()

    if hasattr(arm, "arm_start"):
        return arm.arm_start

    raise AttributeError("arm must provide get_start() or arm_start")


def _get_arm_end(arm):
    if hasattr(arm, "get_end"):
        return arm.get_end()

    if hasattr(arm, "arm_end"):
        return arm.arm_end

    if hasattr(arm, "hand_anchor"):
        return arm.hand_anchor

    raise AttributeError("arm must provide get_end(), arm_end, or hand_anchor")


def _rotation_sign_for_side(side: str) -> float:
    side = _normalize_side(side)
    return -1.0 if side == "right" else 1.0


def _hand_sync_animation(
    hand,
    arm,
    *,
    run_time: float,
):
    run_time = _validate_positive("run_time", run_time)

    return ApplyMethod(
        hand.move_to,
        _get_arm_end(arm),
        run_time=run_time,
    )


def _arm_rotate_animation(
    arm,
    degrees: float,
    *,
    run_time: float,
):
    run_time = _validate_positive("run_time", run_time)
    degrees = _validate_numeric("degrees", degrees)

    return ApplyMethod(
        arm.rotate,
        radians(degrees),
        {"about_point": _get_arm_start(arm)},
        run_time=run_time,
    )


def _play_wave_audio(with_sound: bool = True) -> None:
    if not with_sound:
        return

    if maybe_play_sound is None or play_wave_sound is None:
        return

    maybe_play_sound(
        with_sound,
        play_wave_sound,
    )


def build_raise_arm_animation(
    rig,
    *,
    side: str = "right",
    raise_degrees: float = 55.0,
):
    """
    Raise arm into wave-ready position.
    """
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
    rig,
    *,
    side: str = "right",
    wave_degrees: float = 18.0,
    with_sound: bool = True,
):
    """
    Build one small wave cycle.
    """
    side = _normalize_side(side)
    wave_degrees = _validate_positive("wave_degrees", wave_degrees)

    if LOG_ANIMATION_EVENTS:
        logger.info(
            "Building one wave cycle | side=%s wave_degrees=%.3f",
            side,
            wave_degrees,
        )

    _play_wave_audio(with_sound=with_sound)

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

    return Succession(
        wave_out,
        wave_back,
    )


def build_wave_animation(
    rig,
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
    """
    side = _normalize_side(side)
    cycles = _validate_cycles(cycles)
    raise_degrees = _validate_positive("raise_degrees", raise_degrees)
    wave_degrees = _validate_positive("wave_degrees", wave_degrees)

    if LOG_ANIMATION_EVENTS:
        logger.info(
            "Building full wave animation | side=%s cycles=%d "
            "raise_degrees=%.3f wave_degrees=%.3f with_sound=%s",
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

    return Succession(
        *animations,
    )


__all__ = [
    "build_raise_arm_animation",
    "build_wave_once_animation",
    "build_wave_animation",
]