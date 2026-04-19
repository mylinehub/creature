"""
Teacher pose for mathlab-mylinehub-creature.

This file defines a simple teaching-ready pose for the creature.

Version 1 goals:
- one arm raised as if explaining or presenting
- the other arm relaxed
- legs remain stable
- pose stays readable and balanced

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

def apply_teacher_pose(
    rig: dict,
    *,
    presenting_side: str = "right",
    presenting_arm_degrees: float = 55.0,
) -> VGroup:
    """
    Apply a teacher / presenter pose to the creature rig.

    Teacher pose idea:
    - reset to neutral first
    - raise one arm outward as if presenting
    - keep the other arm relaxed
    - keep legs stable

    Args:
        rig:
            Existing body rig dictionary.

        presenting_side:
            Which arm presents. Allowed:
            - "right"
            - "left"

        presenting_arm_degrees:
            Rotation amount for the presenting arm.

    Returns:
        The updated full group (for chaining)
    """
    _validate_rig(rig)

    if presenting_side not in {"left", "right"}:
        raise ValueError(
            f"presenting_side must be 'left' or 'right', got {presenting_side!r}"
        )

    if not isinstance(presenting_arm_degrees, (int, float)):
        raise TypeError(
            f"presenting_arm_degrees must be numeric, got {type(presenting_arm_degrees).__name__}"
        )

    if LOG_CREATURE_BUILD:
        logger.info(
            "Applying teacher pose | presenting_side=%s presenting_arm_degrees=%.3f",
            presenting_side,
            presenting_arm_degrees,
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

    # Keep one arm relaxed and lift the presenting arm.
    if presenting_side == "right":
        right_arm.rotate(
            radians(-presenting_arm_degrees),
            about_point=right_arm.get_start(),
        )
    else:
        left_arm.rotate(
            radians(presenting_arm_degrees),
            about_point=left_arm.get_start(),
        )

    # --------------------------------------------------------
    # Hands
    # --------------------------------------------------------
    _refresh_arm_hand_alignment(rig)

    # --------------------------------------------------------
    # Legs
    # --------------------------------------------------------
    # Keep legs stable for a grounded teaching pose.

    # --------------------------------------------------------
    # Refresh master group
    # --------------------------------------------------------
    full_group = _refresh_body_rig_group(rig)

    if DEBUG_MODE:
        logger.debug(
            "Teacher pose applied | presenting_side=%s left_arm_end=%s right_arm_end=%s",
            presenting_side,
            left_arm.get_end(),
            right_arm.get_end(),
        )

    if LOG_CREATURE_BUILD:
        logger.info("Teacher pose applied successfully")

    return full_group