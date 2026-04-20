"""
Thinking pose for mathlab-mylinehub-creature.

This file defines a simple reflective / thinking pose for the creature.

Version 1 goals:
- one arm slightly raised as if considering an idea
- the other arm remains relaxed
- pose feels different from happy / teacher / pointing
- legs remain stable
- hands stay attached to arm ends

This file modifies an existing rig.
It does NOT rebuild the creature from scratch.
"""

from __future__ import annotations

from math import radians

from manimlib import VGroup

from mathlab_creature.config.defaults import DEBUG_MODE
from mathlab_creature.config.defaults import LOG_CREATURE_BUILD

from mathlab_creature.core.logger import get_logger
from mathlab_creature.creature.poses.neutral_pose import apply_neutral_pose

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

def apply_thinking_pose(
    rig: dict,
    *,
    thinking_side: str = "left",
    thinking_arm_degrees: float = 40.0,
) -> VGroup:
    """
    Apply a thinking pose to the creature rig.

    Thinking pose idea:
    - reset to neutral first
    - raise one arm modestly so the pose feels reflective
    - keep the other arm relaxed
    - keep legs stable

    Args:
        rig:
            Existing body rig dictionary.

        thinking_side:
            Which arm takes the thinking gesture. Allowed:
            - "left"
            - "right"

        thinking_arm_degrees:
            Rotation amount for the thinking arm.

    Returns:
        The updated full group (for chaining)
    """
    _validate_rig(rig)

    if thinking_side not in {"left", "right"}:
        raise ValueError(
            f"thinking_side must be 'left' or 'right', got {thinking_side!r}"
        )

    if not isinstance(thinking_arm_degrees, (int, float)):
        raise TypeError(
            f"thinking_arm_degrees must be numeric, got {type(thinking_arm_degrees).__name__}"
        )

    if LOG_CREATURE_BUILD:
        logger.info(
            "Applying thinking pose | thinking_side=%s thinking_arm_degrees=%.3f",
            thinking_side,
            thinking_arm_degrees,
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

    # Lift one arm modestly so it feels reflective rather than excited.
    if thinking_side == "left":
        left_arm.rotate(
            radians(thinking_arm_degrees),
            about_point=left_arm.get_start(),
        )
    else:
        right_arm.rotate(
            radians(-thinking_arm_degrees),
            about_point=right_arm.get_start(),
        )

    # --------------------------------------------------------
    # Hands
    # --------------------------------------------------------
    _refresh_arm_hand_alignment(rig)

    # --------------------------------------------------------
    # Legs
    # --------------------------------------------------------
    # Keep legs stable for version 1 thinking pose.

    # --------------------------------------------------------
    # Refresh master group
    # --------------------------------------------------------
    full_group = _refresh_body_rig_group(rig)

    if DEBUG_MODE:
        logger.debug(
            "Thinking pose applied | thinking_side=%s left_arm_end=%s right_arm_end=%s",
            thinking_side,
            left_arm.get_end(),
            right_arm.get_end(),
        )

    if LOG_CREATURE_BUILD:
        logger.info("Thinking pose applied successfully")

    return full_group