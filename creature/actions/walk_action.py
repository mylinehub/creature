"""
Walk action helpers for mathlab-mylinehub-creature.

This file provides a simple version 1 walking action for the creature.

Version 1 goals:
- create a readable left-right stepping feel
- move the full creature horizontally
- alternate leg and arm motion in a simple way
- keep hands and feet attached after each pose change
- keep implementation understandable and stable

This file animates an existing rig from body_rig.py.
It does not rebuild the rig.
"""

from __future__ import annotations

from math import radians

from manimlib import AnimationGroup
from manimlib import ApplyMethod

from config.defaults import DEBUG_MODE, LOG_ANIMATION_EVENTS
from config.timings import STEP_TIME
from core.geometry import point
from core.logger import get_logger
from creature.poses.neutral_pose import apply_neutral_pose

logger = get_logger(__name__)


# ============================================================
# Constants
# ============================================================

STEP_FORWARD_DISTANCE = 0.35

LEFT_LEG_FORWARD = 14
RIGHT_LEG_BACK = -10

RIGHT_LEG_FORWARD = -14
LEFT_LEG_BACK = 10

ARM_FORWARD = -12
ARM_BACK = 8


# ============================================================
# Validation
# ============================================================

def _validate_rig(rig: dict):
    if not isinstance(rig, dict):
        raise TypeError("rig must be dict")

    if "group" not in rig or "arms" not in rig or "legs" not in rig:
        raise KeyError("rig missing required structure")


def _validate_cycles(cycles: int) -> int:
    if not isinstance(cycles, int):
        raise TypeError("cycles must be int")
    if cycles <= 0:
        raise ValueError("cycles must be > 0")
    return cycles


# ============================================================
# Sync helpers
# ============================================================

def _sync_limbs(rig: dict):
    """
    Keep hands and feet attached after rotations.
    """
    rig["arms"]["left_hand"].move_to(rig["arms"]["left_arm"].get_end())
    rig["arms"]["right_hand"].move_to(rig["arms"]["right_arm"].get_end())

    rig["legs"]["left_foot"].move_to(rig["legs"]["left_leg"].get_end())
    rig["legs"]["right_foot"].move_to(rig["legs"]["right_leg"].get_end())


# ============================================================
# Step builders
# ============================================================

def _build_left_step(rig: dict):
    """
    Left leg forward step.
    """
    left_arm = rig["arms"]["left_arm"]
    right_arm = rig["arms"]["right_arm"]
    left_leg = rig["legs"]["left_leg"]
    right_leg = rig["legs"]["right_leg"]
    group = rig["group"]

    return AnimationGroup(
        ApplyMethod(left_leg.rotate, radians(LEFT_LEG_FORWARD), {"about_point": left_leg.get_start()}, run_time=STEP_TIME),
        ApplyMethod(right_leg.rotate, radians(RIGHT_LEG_BACK), {"about_point": right_leg.get_start()}, run_time=STEP_TIME),
        ApplyMethod(right_arm.rotate, radians(ARM_FORWARD), {"about_point": right_arm.get_start()}, run_time=STEP_TIME),
        ApplyMethod(left_arm.rotate, radians(ARM_BACK), {"about_point": left_arm.get_start()}, run_time=STEP_TIME),
        ApplyMethod(group.shift, point(STEP_FORWARD_DISTANCE, 0, 0), run_time=STEP_TIME),
        lag_ratio=0.0,
    )


def _build_right_step(rig: dict):
    """
    Right leg forward step.
    """
    left_arm = rig["arms"]["left_arm"]
    right_arm = rig["arms"]["right_arm"]
    left_leg = rig["legs"]["left_leg"]
    right_leg = rig["legs"]["right_leg"]
    group = rig["group"]

    return AnimationGroup(
        ApplyMethod(right_leg.rotate, radians(RIGHT_LEG_FORWARD), {"about_point": right_leg.get_start()}, run_time=STEP_TIME),
        ApplyMethod(left_leg.rotate, radians(LEFT_LEG_BACK), {"about_point": left_leg.get_start()}, run_time=STEP_TIME),
        ApplyMethod(left_arm.rotate, radians(-ARM_FORWARD), {"about_point": left_arm.get_start()}, run_time=STEP_TIME),
        ApplyMethod(right_arm.rotate, radians(-ARM_BACK), {"about_point": right_arm.get_start()}, run_time=STEP_TIME),
        ApplyMethod(group.shift, point(STEP_FORWARD_DISTANCE, 0, 0), run_time=STEP_TIME),
        lag_ratio=0.0,
    )


# ============================================================
# Public builder
# ============================================================

def build_walk_animation(rig: dict, cycles: int = 2):
    """
    Build a simple walk animation.

    Flow:
    - start from neutral
    - alternate steps
    - maintain forward motion

    Args:
        rig:
            Creature rig
        cycles:
            number of walk cycles
    """

    _validate_rig(rig)
    cycles = _validate_cycles(cycles)

    if LOG_ANIMATION_EVENTS:
        logger.info("Building walk animation | cycles=%d", cycles)

    # Start clean
    apply_neutral_pose(rig)
    _sync_limbs(rig)

    animations = []

    for i in range(cycles):
        if DEBUG_MODE:
            logger.debug("Walk cycle %d", i)

        animations.append(_build_left_step(rig))
        animations.append(_build_right_step(rig))

    return AnimationGroup(*animations, lag_ratio=0.0)