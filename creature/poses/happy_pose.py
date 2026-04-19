"""
Happy pose for mathlab-mylinehub-creature.

This file defines a simple cheerful standing pose for the creature.

Version 1 goals:
- lift both arms slightly upward
- keep legs stable
- preserve overall balance
- work as a clean static pose before full animation actions exist

This file modifies an existing rig.
It does NOT rebuild the creature from scratch.
"""

from __future__ import annotations

from math import radians

from manimlib import VGroup

from config.defaults import DEBUG_MODE
from config.defaults import LOG_CREATURE_BUILD

from core.logger import get_logger
from creature.poses.neutral_pose import apply_neutral_pose

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


def _refresh_arm_hand_alignment(rig: dict) -> None:
    """
    Reattach hands to the current ends of their arms.

    This is required after arm rotation so the visible hand tips stay
    attached to the actual arm geometry.
    """
    left_arm = rig["arms"]["left_arm"]
    right_arm = rig["arms"]["right_arm"]

    left_hand = rig["arms"]["left_hand"]
    right_hand = rig["arms"]["right_hand"]

    left_hand.move_to(left_arm.get_end())
    right_hand.move_to(right_arm.get_end())


def _refresh_body_rig_group(rig: dict) -> VGroup:
    """
    Refresh the full group ordering after pose updates.

    Expected body rig structure:
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

def apply_happy_pose(
    rig: dict,
    *,
    left_arm_degrees: float = 25.0,
    right_arm_degrees: float = 25.0,
) -> VGroup:
    """
    Apply a happy pose to the creature rig.

    Happy pose idea:
    - reset to neutral first
    - raise left arm outward/upward
    - raise right arm outward/upward
    - keep legs stable

    Args:
        rig:
            Existing body rig dictionary.

        left_arm_degrees:
            Upward/outward rotation amount for the left arm.

        right_arm_degrees:
            Upward/outward rotation amount for the right arm.

    Returns:
        The updated full group (for chaining)
    """
    _validate_rig(rig)

    if LOG_CREATURE_BUILD:
        logger.info(
            "Applying happy pose | left_arm_degrees=%.3f right_arm_degrees=%.3f",
            left_arm_degrees,
            right_arm_degrees,
        )

    # --------------------------------------------------------
    # Start from neutral state
    # --------------------------------------------------------
    apply_neutral_pose(rig)

    # --------------------------------------------------------
    # Arms
    # --------------------------------------------------------
    left_arm = rig["arms"]["left_arm"]
    right_arm = rig["arms"]["right_arm"]

    # Left arm rotates counterclockwise from the shoulder.
    left_arm.rotate(
        radians(left_arm_degrees),
        about_point=left_arm.get_start(),
    )

    # Right arm rotates clockwise from the shoulder.
    right_arm.rotate(
        radians(-right_arm_degrees),
        about_point=right_arm.get_start(),
    )

    # --------------------------------------------------------
    # Hands
    # --------------------------------------------------------
    _refresh_arm_hand_alignment(rig)

    # --------------------------------------------------------
    # Legs
    # --------------------------------------------------------
    # Keep legs unchanged for version 1 happy pose.
    # This keeps the silhouette stable and readable.

    # --------------------------------------------------------
    # Refresh master group
    # --------------------------------------------------------
    full_group = _refresh_body_rig_group(rig)

    if DEBUG_MODE:
        logger.debug(
            "Happy pose applied | left_arm_end=%s right_arm_end=%s",
            left_arm.get_end(),
            right_arm.get_end(),
        )

    if LOG_CREATURE_BUILD:
        logger.info("Happy pose applied successfully")

    return full_group