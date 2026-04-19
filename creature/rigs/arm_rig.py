"""
Arm rig helpers for mathlab-mylinehub-creature.

This file provides lightweight arm-rig utilities for:
- building arm + hand groups
- accessing left/right arm systems cleanly
- rebuilding arm or hand parts
- preparing for later wave / point / raise-arm actions

Version 1 goals:
- keep the rig simple
- avoid overengineering
- make arm access predictable
- support later animation work cleanly

This file does not animate the arms yet.
It organizes them for later control.
"""

from __future__ import annotations

from manimlib import VGroup

from config.defaults import DEBUG_MODE, LOG_CREATURE_BUILD
from creature.parts.arms import build_left_arm, build_right_arm
from creature.parts.hands import build_left_hand, build_right_hand
from core.logger import get_logger

logger = get_logger(__name__)


# ============================================================
# Internal helpers
# ============================================================

def _validate_arm_rig_group(group: VGroup) -> None:
    if not isinstance(group, VGroup):
        raise TypeError(f"arm_rig_group must be a VGroup, got {type(group).__name__}")
    if len(group) < 2:
        raise ValueError("arm_rig_group must contain at least 2 systems")


def _build_arm_system(
    *,
    body_center=None,
    side: str,
    direction: str = "down",
) -> VGroup:
    """
    Build one arm system (arm + hand) correctly linked.
    """
    if side == "left":
        arm = build_left_arm(body_center=body_center, direction=direction)
        hand = build_left_hand(body_center=body_center, arm=arm)
    elif side == "right":
        arm = build_right_arm(body_center=body_center, direction=direction)
        hand = build_right_hand(body_center=body_center, arm=arm)
    else:
        raise ValueError(f"Invalid side: {side}")

    system = VGroup(arm, hand)

    # metadata
    system.arm = arm
    system.hand = hand
    system.side = side

    if DEBUG_MODE:
        logger.debug(
            "Built arm system | side=%s arm=%s hand=%s",
            side,
            getattr(arm, "name", "arm"),
            getattr(hand, "name", "hand"),
        )

    return system


# ============================================================
# Public builders
# ============================================================

def build_left_arm_system(body_center=None, *, direction: str = "down") -> VGroup:
    if LOG_CREATURE_BUILD:
        logger.info("Building left arm system")

    return _build_arm_system(
        body_center=body_center,
        side="left",
        direction=direction,
    )


def build_right_arm_system(body_center=None, *, direction: str = "down") -> VGroup:
    if LOG_CREATURE_BUILD:
        logger.info("Building right arm system")

    return _build_arm_system(
        body_center=body_center,
        side="right",
        direction=direction,
    )


def build_arm_rig_group(
    body_center=None,
    *,
    left_direction: str = "down",
    right_direction: str = "down",
) -> VGroup:
    """
    Build both arm systems together.
    """
    if LOG_CREATURE_BUILD:
        logger.info("Building full arm rig group")

    left_system = build_left_arm_system(
        body_center=body_center,
        direction=left_direction,
    )
    right_system = build_right_arm_system(
        body_center=body_center,
        direction=right_direction,
    )

    group = VGroup(left_system, right_system)

    # metadata
    group.left_system = left_system
    group.right_system = right_system
    group.left_arm = left_system.arm
    group.right_arm = right_system.arm
    group.left_hand = left_system.hand
    group.right_hand = right_system.hand

    if LOG_CREATURE_BUILD:
        logger.info("Arm rig group created successfully")

    return group


# ============================================================
# Arm rig map
# ============================================================

def build_arm_rig_map(body_center=None) -> dict[str, object]:
    """
    Build a simple arm rig map for clean access later.
    """
    if LOG_CREATURE_BUILD:
        logger.info("Building arm rig map")

    group = build_arm_rig_group(body_center)

    rig_map = {
        "left_arm": group.left_arm,
        "left_hand": group.left_hand,
        "right_arm": group.right_arm,
        "right_hand": group.right_hand,
        "left_system": group.left_system,
        "right_system": group.right_system,
        "group": group,
    }

    return rig_map


# ============================================================
# Rebuild helpers
# ============================================================

def rebuild_left_arm_system(
    arm_rig_group: VGroup,
    body_center=None,
    *,
    direction: str = "down",
) -> VGroup:
    if LOG_CREATURE_BUILD:
        logger.info("Rebuilding left arm system")

    _validate_arm_rig_group(arm_rig_group)

    arm_rig_group.submobjects[0] = build_left_arm_system(
        body_center=body_center,
        direction=direction,
    )

    return arm_rig_group


def rebuild_right_arm_system(
    arm_rig_group: VGroup,
    body_center=None,
    *,
    direction: str = "down",
) -> VGroup:
    if LOG_CREATURE_BUILD:
        logger.info("Rebuilding right arm system")

    _validate_arm_rig_group(arm_rig_group)

    arm_rig_group.submobjects[1] = build_right_arm_system(
        body_center=body_center,
        direction=direction,
    )

    return arm_rig_group


# ============================================================
# Access helpers
# ============================================================

def get_left_arm_system(group: VGroup):
    _validate_arm_rig_group(group)
    return group[0]


def get_right_arm_system(group: VGroup):
    _validate_arm_rig_group(group)
    return group[1]


def get_left_arm(system: VGroup):
    return system.arm


def get_left_hand(system: VGroup):
    return system.hand


def get_right_arm(system: VGroup):
    return system.arm


def get_right_hand(system: VGroup):
    return system.hand