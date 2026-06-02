"""
Hop action for mathlab-mylinehub-creature.

This file builds hop animations for one connected creature.

Architecture rule:
- hop_action.py works through BodyRig
- hop_action.py never manipulates random groups directly
- hop_action.py moves the creature root
- optional audio support
"""

from __future__ import annotations

from manimlib import AnimationGroup
from manimlib import ApplyMethod
from manimlib import Succession

from mathlab_creature.config.defaults import (
    DEBUG_MODE,
    LOG_ANIMATION_EVENTS,
)

from mathlab_creature.config.timings import (
    HOP_DOWN_TIME,
    HOP_LAND_TIME,
    HOP_UP_TIME,
)

from mathlab_creature.core.logger import get_logger

from mathlab_creature.creature.rigs.body_rig import BodyRig


logger = get_logger(__name__)


try:
    from mathlab_creature.core.audio.helpers import maybe_play_sound
    from mathlab_creature.core.audio.procedural import play_hop_sound
except Exception:
    maybe_play_sound = None
    play_hop_sound = None


DEFAULT_HOP_SQUASH_FACTOR = 0.92
DEFAULT_HOP_HEIGHT = 0.45


def _validate_numeric(
    name: str,
    value: float | int,
) -> float:
    if not isinstance(value, (int, float)):
        raise TypeError(
            f"{name} must be numeric, got {type(value).__name__}"
        )

    return float(value)


def _validate_positive(
    name: str,
    value: float | int,
) -> float:
    value = _validate_numeric(
        name,
        value,
    )

    if value <= 0:
        raise ValueError(
            f"{name} must be > 0, got {value}"
        )

    return value


def _validate_body_rig(
    body_rig,
) -> BodyRig:
    if not isinstance(body_rig, BodyRig):
        raise TypeError(
            f"body_rig must be BodyRig, got {type(body_rig).__name__}"
        )

    return body_rig


def _play_hop_audio(
    with_sound: bool = True,
):
    if not with_sound:
        return

    if maybe_play_sound is None:
        return

    if play_hop_sound is None:
        return

    maybe_play_sound(
        with_sound,
        play_hop_sound,
    )


def build_hop_down_animation(
    body_rig: BodyRig,
    *,
    squash_factor: float = DEFAULT_HOP_SQUASH_FACTOR,
    run_time: float = HOP_DOWN_TIME,
):
    body_rig = _validate_body_rig(
        body_rig,
    )

    squash_factor = _validate_positive(
        "squash_factor",
        squash_factor,
    )

    run_time = _validate_positive(
        "run_time",
        run_time,
    )

    if LOG_ANIMATION_EVENTS:
        logger.info(
            "Building hop-down animation"
        )

    return ApplyMethod(
        body_rig.stretch,
        squash_factor,
        1,
        run_time=run_time,
    )


def build_hop_up_animation(
    body_rig: BodyRig,
    *,
    hop_height: float = DEFAULT_HOP_HEIGHT,
    squash_factor: float = DEFAULT_HOP_SQUASH_FACTOR,
    run_time: float = HOP_UP_TIME,
    with_sound: bool = True,
):
    body_rig = _validate_body_rig(
        body_rig,
    )

    hop_height = _validate_positive(
        "hop_height",
        hop_height,
    )

    squash_factor = _validate_positive(
        "squash_factor",
        squash_factor,
    )

    run_time = _validate_positive(
        "run_time",
        run_time,
    )

    _play_hop_audio(
        with_sound=with_sound,
    )

    return AnimationGroup(
        ApplyMethod(
            body_rig.stretch,
            1.0 / squash_factor,
            1,
            run_time=run_time,
        ),
        ApplyMethod(
            body_rig.shift,
            [0.0, hop_height, 0.0],
            run_time=run_time,
        ),
        lag_ratio=0.0,
    )


def build_hop_land_animation(
    body_rig: BodyRig,
    *,
    hop_height: float = DEFAULT_HOP_HEIGHT,
    run_time: float = HOP_LAND_TIME,
):
    body_rig = _validate_body_rig(
        body_rig,
    )

    hop_height = _validate_positive(
        "hop_height",
        hop_height,
    )

    run_time = _validate_positive(
        "run_time",
        run_time,
    )

    return ApplyMethod(
        body_rig.shift,
        [0.0, -hop_height, 0.0],
        run_time=run_time,
    )


def build_hop_animation(
    body_rig: BodyRig,
    *,
    hop_height: float = DEFAULT_HOP_HEIGHT,
    squash_factor: float = DEFAULT_HOP_SQUASH_FACTOR,
    down_run_time: float = HOP_DOWN_TIME,
    up_run_time: float = HOP_UP_TIME,
    land_run_time: float = HOP_LAND_TIME,
    with_sound: bool = True,
):
    body_rig = _validate_body_rig(
        body_rig,
    )

    if LOG_ANIMATION_EVENTS:
        logger.info(
            "Building full hop animation"
        )

    return Succession(
        build_hop_down_animation(
            body_rig,
            squash_factor=squash_factor,
            run_time=down_run_time,
        ),
        build_hop_up_animation(
            body_rig,
            hop_height=hop_height,
            squash_factor=squash_factor,
            run_time=up_run_time,
            with_sound=with_sound,
        ),
        build_hop_land_animation(
            body_rig,
            hop_height=hop_height,
            run_time=land_run_time,
        ),
    )


__all__ = [
    "DEFAULT_HOP_HEIGHT",
    "DEFAULT_HOP_SQUASH_FACTOR",
    "build_hop_down_animation",
    "build_hop_up_animation",
    "build_hop_land_animation",
    "build_hop_animation",
]