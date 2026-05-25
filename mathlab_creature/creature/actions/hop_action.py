# File: mathlab_creature/creature/actions/hop_action.py

"""
Hop action helpers for mathlab-mylinehub-creature
with cinematic procedural audio integration.

This file provides a simple hop animation for the creature.

Features:
- readable mascot hop
- squash and stretch
- upward movement
- soft landing
- procedural hop sound
- optional sound toggle
- cinematic educational motion
- safe audio integration

Design Goals:
- expressive
- lightweight
- production-ready
- educational mascot feel
- readable motion
- future extensible

Audio Goals:
- soft spring
- subtle landing body
- playful movement
- alive but not annoying
"""

from __future__ import annotations

from manimlib import AnimationGroup
from manimlib import ApplyMethod

from mathlab_creature.config.defaults import (
    DEBUG_MODE,
    LOG_ANIMATION_EVENTS,
)

from mathlab_creature.config.timings import (
    HOP_DOWN_TIME,
    HOP_LAND_TIME,
    HOP_UP_TIME,
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
    play_hop_sound,
)

logger = get_logger(__name__)


# ============================================================
# INTERNAL CONSTANTS
# ============================================================

_REQUIRED_RIG_KEYS = (
    "group",
)

DEFAULT_HOP_SQUASH_FACTOR = 0.92

DEFAULT_HOP_HEIGHT = 0.45


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


def _validate_squash_factor(
    squash_factor: float,
) -> float:
    """
    Validate squash factor.
    """

    squash_factor = _validate_positive(
        "squash_factor",
        squash_factor,
    )

    return squash_factor


def _validate_rig(
    rig: dict,
) -> None:
    """
    Validate hop rig shape.
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

    if rig["group"] is None:
        raise ValueError(
            "rig['group'] must not be None"
        )


def _get_creature_group(
    rig: dict,
):
    """
    Return full creature group.
    """

    _validate_rig(rig)

    return rig["group"]


def _vertical_shift_vector(
    amount: float,
):
    """
    Return vertical movement vector.
    """

    amount = _validate_numeric(
        "amount",
        amount,
    )

    return point(
        0.0,
        amount,
        0.0,
    )


# ============================================================
# AUDIO HELPERS
# ============================================================

def _play_hop_audio(
    with_sound: bool = True,
):
    """
    Trigger procedural hop sound safely.
    """

    maybe_play_sound(
        with_sound,
        play_hop_sound,
    )


# ============================================================
# PUBLIC BUILDERS
# ============================================================

def build_hop_down_animation(
    rig: dict,
    *,
    squash_factor: float = DEFAULT_HOP_SQUASH_FACTOR,
    run_time: float = HOP_DOWN_TIME,
):
    """
    Build squash preparation phase.
    """

    _validate_rig(rig)

    squash_factor = _validate_squash_factor(
        squash_factor
    )

    run_time = _validate_positive(
        "run_time",
        run_time,
    )

    if LOG_ANIMATION_EVENTS:

        logger.info(
            "Building hop-down animation | squash_factor=%.3f run_time=%.3f",
            squash_factor,
            run_time,
        )

    creature_group = _get_creature_group(
        rig
    )

    if DEBUG_MODE:

        logger.debug(
            "Hop down setup | group=%s squash_factor=%.3f",
            getattr(
                creature_group,
                "name",
                "creature_group",
            ),
            squash_factor,
        )

    return ApplyMethod(
        creature_group.stretch,
        squash_factor,
        1,
        run_time=run_time,
    )


def build_hop_up_animation(
    rig: dict,
    *,
    hop_height: float = DEFAULT_HOP_HEIGHT,
    squash_factor: float = DEFAULT_HOP_SQUASH_FACTOR,
    run_time: float = HOP_UP_TIME,
    with_sound: bool = True,
):
    """
    Build upward hop phase.

    Includes:
    - vertical launch
    - squash restoration
    - procedural hop sound
    """

    _validate_rig(rig)

    hop_height = _validate_positive(
        "hop_height",
        hop_height,
    )

    squash_factor = _validate_squash_factor(
        squash_factor
    )

    run_time = _validate_positive(
        "run_time",
        run_time,
    )

    if LOG_ANIMATION_EVENTS:

        logger.info(
            "Building hop-up animation | hop_height=%.3f squash_factor=%.3f run_time=%.3f",
            hop_height,
            squash_factor,
            run_time,
        )

    # --------------------------------------------------------
    # AUDIO
    # --------------------------------------------------------

    _play_hop_audio(
        with_sound=with_sound,
    )

    creature_group = _get_creature_group(
        rig
    )

    return AnimationGroup(
        ApplyMethod(
            creature_group.stretch,
            1.0 / squash_factor,
            1,
            run_time=run_time,
        ),
        ApplyMethod(
            creature_group.shift,
            _vertical_shift_vector(
                hop_height
            ),
            run_time=run_time,
        ),
        lag_ratio=0.0,
    )


def build_hop_land_animation(
    rig: dict,
    *,
    hop_height: float = DEFAULT_HOP_HEIGHT,
    run_time: float = HOP_LAND_TIME,
):
    """
    Build landing phase.
    """

    _validate_rig(rig)

    hop_height = _validate_positive(
        "hop_height",
        hop_height,
    )

    run_time = _validate_positive(
        "run_time",
        run_time,
    )

    if LOG_ANIMATION_EVENTS:

        logger.info(
            "Building hop-land animation | hop_height=%.3f run_time=%.3f",
            hop_height,
            run_time,
        )

    creature_group = _get_creature_group(
        rig
    )

    return ApplyMethod(
        creature_group.shift,
        _vertical_shift_vector(
            -hop_height
        ),
        run_time=run_time,
    )


def build_hop_animation(
    rig: dict,
    *,
    hop_height: float = DEFAULT_HOP_HEIGHT,
    squash_factor: float = DEFAULT_HOP_SQUASH_FACTOR,
    down_run_time: float = HOP_DOWN_TIME,
    up_run_time: float = HOP_UP_TIME,
    land_run_time: float = HOP_LAND_TIME,
    with_sound: bool = True,
):
    """
    Build complete hop action.

    Flow:
    - squash downward
    - upward hop
    - landing recovery

    Features:
    - optional procedural sound
    - cinematic squash/stretch
    - soft mascot timing
    """

    _validate_rig(rig)

    hop_height = _validate_positive(
        "hop_height",
        hop_height,
    )

    squash_factor = _validate_squash_factor(
        squash_factor
    )

    down_run_time = _validate_positive(
        "down_run_time",
        down_run_time,
    )

    up_run_time = _validate_positive(
        "up_run_time",
        up_run_time,
    )

    land_run_time = _validate_positive(
        "land_run_time",
        land_run_time,
    )

    if LOG_ANIMATION_EVENTS:

        logger.info(
            "Building full hop animation | hop_height=%.3f squash_factor=%.3f down=%.3f up=%.3f land=%.3f with_sound=%s",
            hop_height,
            squash_factor,
            down_run_time,
            up_run_time,
            land_run_time,
            with_sound,
        )

    return AnimationGroup(
        build_hop_down_animation(
            rig,
            squash_factor=squash_factor,
            run_time=down_run_time,
        ),
        build_hop_up_animation(
            rig,
            hop_height=hop_height,
            squash_factor=squash_factor,
            run_time=up_run_time,
            with_sound=with_sound,
        ),
        build_hop_land_animation(
            rig,
            hop_height=hop_height,
            run_time=land_run_time,
        ),
        lag_ratio=0.0,
    )