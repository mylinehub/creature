"""
Hop action helpers for mathlab-mylinehub-creature.

This file provides a simple hop animation for the creature.

Version 1 goals:
- make the whole creature do a small readable hop
- include a slight squash before the hop
- include upward motion and landing
- keep implementation simple and reliable

This file animates the full creature group from body_rig.py.
It does not rebuild the rig.
"""

from __future__ import annotations

from manimlib import AnimationGroup
from manimlib import ApplyMethod

from config.defaults import DEBUG_MODE
from config.defaults import LOG_ANIMATION_EVENTS
from config.timings import HOP_DOWN_TIME
from config.timings import HOP_LAND_TIME
from config.timings import HOP_UP_TIME

from core.geometry import point
from core.logger import get_logger

logger = get_logger(__name__)


# ============================================================
# Internal constants
# ============================================================

_REQUIRED_RIG_KEYS = ("group",)
DEFAULT_HOP_SQUASH_FACTOR = 0.92
DEFAULT_HOP_HEIGHT = 0.45


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


def _validate_positive(name: str, value: float | int) -> float:
    """
    Ensure a positive numeric value.
    """
    value = _validate_numeric(name, value)
    if value <= 0:
        raise ValueError(f"{name} must be > 0, got {value}")
    return value


def _validate_squash_factor(squash_factor: float) -> float:
    """
    Ensure squash factor is valid for a vertical stretch.

    Expected:
    - > 0
    - usually < 1 for visible squash
    """
    squash_factor = _validate_positive("squash_factor", squash_factor)
    return squash_factor


def _validate_rig(rig: dict) -> None:
    """
    Validate the minimum rig shape needed for hop actions.
    """
    if not isinstance(rig, dict):
        raise TypeError(f"rig must be a dict, got {type(rig).__name__}")

    missing = [key for key in _REQUIRED_RIG_KEYS if key not in rig]
    if missing:
        raise KeyError(f"rig is missing required keys: {missing}")

    if rig["group"] is None:
        raise ValueError("rig['group'] must not be None")


def _get_creature_group(rig: dict):
    """
    Return the full creature group from the rig.
    """
    _validate_rig(rig)
    return rig["group"]


def _vertical_shift_vector(amount: float):
    """
    Return a vertical shift vector for the given amount.
    """
    amount = _validate_numeric("amount", amount)
    return point(0.0, amount, 0.0)


# ============================================================
# Public builders
# ============================================================

def build_hop_down_animation(
    rig: dict,
    *,
    squash_factor: float = DEFAULT_HOP_SQUASH_FACTOR,
    run_time: float = HOP_DOWN_TIME,
):
    """
    Build the preparation phase of the hop.

    This gives a slight squash before the upward jump.
    """
    _validate_rig(rig)
    squash_factor = _validate_squash_factor(squash_factor)
    run_time = _validate_positive("run_time", run_time)

    if LOG_ANIMATION_EVENTS:
        logger.info(
            "Building hop-down animation | squash_factor=%.3f run_time=%.3f",
            squash_factor,
            run_time,
        )

    creature_group = _get_creature_group(rig)

    if DEBUG_MODE:
        logger.debug(
            "Hop down setup | group=%s squash_factor=%.3f",
            getattr(creature_group, "name", "creature_group"),
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
):
    """
    Build the upward phase of the hop.

    This restores vertical scale and shifts the creature upward.
    """
    _validate_rig(rig)
    hop_height = _validate_positive("hop_height", hop_height)
    squash_factor = _validate_squash_factor(squash_factor)
    run_time = _validate_positive("run_time", run_time)

    if LOG_ANIMATION_EVENTS:
        logger.info(
            "Building hop-up animation | hop_height=%.3f squash_factor=%.3f run_time=%.3f",
            hop_height,
            squash_factor,
            run_time,
        )

    creature_group = _get_creature_group(rig)

    return AnimationGroup(
        ApplyMethod(
            creature_group.stretch,
            1.0 / squash_factor,
            1,
            run_time=run_time,
        ),
        ApplyMethod(
            creature_group.shift,
            _vertical_shift_vector(hop_height),
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
    Build the landing phase of the hop.

    The creature comes back down to its original standing height.
    """
    _validate_rig(rig)
    hop_height = _validate_positive("hop_height", hop_height)
    run_time = _validate_positive("run_time", run_time)

    if LOG_ANIMATION_EVENTS:
        logger.info(
            "Building hop-land animation | hop_height=%.3f run_time=%.3f",
            hop_height,
            run_time,
        )

    creature_group = _get_creature_group(rig)

    return ApplyMethod(
        creature_group.shift,
        _vertical_shift_vector(-hop_height),
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
):
    """
    Build a full hop animation.

    Flow:
    - slight squash downward
    - hop upward
    - land back down

    Args:
        rig:
            Creature rig dictionary from body_rig.py

        hop_height:
            Vertical distance of the hop.

        squash_factor:
            Vertical squash factor used during the prep phase.

        down_run_time:
            Duration of the prep/squash phase.

        up_run_time:
            Duration of the upward phase.

        land_run_time:
            Duration of the landing phase.
    """
    _validate_rig(rig)
    hop_height = _validate_positive("hop_height", hop_height)
    squash_factor = _validate_squash_factor(squash_factor)
    down_run_time = _validate_positive("down_run_time", down_run_time)
    up_run_time = _validate_positive("up_run_time", up_run_time)
    land_run_time = _validate_positive("land_run_time", land_run_time)

    if LOG_ANIMATION_EVENTS:
        logger.info(
            "Building full hop animation | hop_height=%.3f squash_factor=%.3f down=%.3f up=%.3f land=%.3f",
            hop_height,
            squash_factor,
            down_run_time,
            up_run_time,
            land_run_time,
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
        ),
        build_hop_land_animation(
            rig,
            hop_height=hop_height,
            run_time=land_run_time,
        ),
        lag_ratio=0.0,
    )