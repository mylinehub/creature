"""
Neutral pose for mathlab-mylinehub-creature.

This file defines the default standing pose of the creature.

Version 1 goals:
- arms relaxed downward
- legs straight and balanced
- face neutral (default already handled by parts)
- clean reset pose that other poses can build on

This file modifies an existing rig.
It does NOT rebuild the creature from scratch.
"""

from __future__ import annotations

from manimlib import VGroup

from config.defaults import DEBUG_MODE
from config.defaults import LOG_CREATURE_BUILD

from creature.rigs.arm_rig import rebuild_left_arm_system
from creature.rigs.arm_rig import rebuild_right_arm_system
from creature.rigs.leg_rig import rebuild_left_leg_system
from creature.rigs.leg_rig import rebuild_right_leg_system

from core.logger import get_logger

logger = get_logger(__name__)


# ============================================================
# Internal helpers
# ============================================================

_REQUIRED_RIG_KEYS = ("arms", "legs", "group")


def _validate_rig(rig: dict) -> None:
    """
    Validate the minimum rig shape required for pose application.
    """
    if not isinstance(rig, dict):
        raise TypeError(f"rig must be a dict, got {type(rig).__name__}")

    missing = [key for key in _REQUIRED_RIG_KEYS if key not in rig]
    if missing:
        raise KeyError(f"rig is missing required keys: {missing}")

    if "group" not in rig or rig["group"] is None:
        raise ValueError("rig['group'] must exist")

    if "body_center" not in rig:
        # not fatal for old rigs, but worth surfacing in debug logs
        if DEBUG_MODE:
            logger.debug("Rig does not include body_center; defaulting pose rebuilds with None")


def _refresh_body_rig_group(rig: dict) -> VGroup:
    """
    Rebuild the master visual group order after sub-rig updates.

    Expected structure in body rig:
    - body
    - face["group"]
    - hat
    - arms["group"]
    - legs["group"]
    """
    rig["group"].submobjects = [
        rig["body"],
        rig["face"]["group"],
        rig["hat"],
        rig["arms"]["group"],
        rig["legs"]["group"],
    ]
    return rig["group"]


# ============================================================
# Pose applier
# ============================================================

def apply_neutral_pose(rig: dict) -> VGroup:
    """
    Apply neutral pose to the creature rig.

    This ensures:
    - arms are straight down
    - legs are straight down
    - hands/feet remain attached through rebuilt limb systems
    - face stays in its existing neutral/default state

    Returns:
        The updated full group (for chaining)
    """
    _validate_rig(rig)

    body_center = rig.get("body_center", None)

    if LOG_CREATURE_BUILD:
        logger.info("Applying neutral pose")

    # --------------------------------------------------------
    # Arms
    # --------------------------------------------------------
    rebuild_left_arm_system(
        rig["arms"]["group"],
        body_center=body_center,
        direction="down",
    )
    rebuild_right_arm_system(
        rig["arms"]["group"],
        body_center=body_center,
        direction="down",
    )

    # Refresh arm rig references after rebuild
    rig["arms"]["left_system"] = rig["arms"]["group"][0]
    rig["arms"]["right_system"] = rig["arms"]["group"][1]
    rig["arms"]["left_arm"] = rig["arms"]["left_system"][0]
    rig["arms"]["left_hand"] = rig["arms"]["left_system"][1]
    rig["arms"]["right_arm"] = rig["arms"]["right_system"][0]
    rig["arms"]["right_hand"] = rig["arms"]["right_system"][1]

    # --------------------------------------------------------
    # Legs
    # --------------------------------------------------------
    rebuild_left_leg_system(
        rig["legs"]["group"],
        body_center=body_center,
        direction="down",
    )
    rebuild_right_leg_system(
        rig["legs"]["group"],
        body_center=body_center,
        direction="down",
    )

    # Refresh leg rig references after rebuild
    rig["legs"]["left_system"] = rig["legs"]["group"][0]
    rig["legs"]["right_system"] = rig["legs"]["group"][1]
    rig["legs"]["left_leg"] = rig["legs"]["left_system"][0]
    rig["legs"]["left_foot"] = rig["legs"]["left_system"][1]
    rig["legs"]["right_leg"] = rig["legs"]["right_system"][0]
    rig["legs"]["right_foot"] = rig["legs"]["right_system"][1]

    # --------------------------------------------------------
    # Refresh master group
    # --------------------------------------------------------
    full_group = _refresh_body_rig_group(rig)

    if DEBUG_MODE:
        logger.debug(
            "Neutral pose applied | left_arm=%s right_arm=%s left_leg=%s right_leg=%s",
            getattr(rig["arms"]["left_arm"], "name", "left_arm"),
            getattr(rig["arms"]["right_arm"], "name", "right_arm"),
            getattr(rig["legs"]["left_leg"], "name", "left_leg"),
            getattr(rig["legs"]["right_leg"], "name", "right_leg"),
        )

    if LOG_CREATURE_BUILD:
        logger.info("Neutral pose applied successfully")

    return full_group