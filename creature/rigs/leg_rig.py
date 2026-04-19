"""
Leg rig helpers for mathlab-mylinehub-creature.

This file provides lightweight leg-rig utilities for:
- building leg + foot systems
- accessing left/right leg systems cleanly
- rebuilding leg or foot parts
- preparing for later walk / step / hop actions

Version 1 goals:
- keep the rig simple
- avoid overengineering
- make leg access predictable
- support later animation work cleanly

This file does not animate the legs yet.
It organizes them for later control.
"""

from __future__ import annotations

from manimlib import VGroup

from config.defaults import DEBUG_MODE
from config.defaults import LOG_CREATURE_BUILD

from creature.parts.feet import build_left_foot
from creature.parts.feet import build_right_foot
from creature.parts.legs import build_left_leg
from creature.parts.legs import build_right_leg

from core.logger import get_logger

logger = get_logger(__name__)


# ============================================================
# Internal constants
# ============================================================

_LEFT_SYSTEM_INDEX = 0
_RIGHT_SYSTEM_INDEX = 1
_SYSTEM_LEG_INDEX = 0
_SYSTEM_FOOT_INDEX = 1
_MIN_RIG_SYSTEM_COUNT = 2
_MIN_LEG_SYSTEM_PART_COUNT = 2


# ============================================================
# Internal helpers
# ============================================================

def _validate_leg_rig_group(leg_rig_group: VGroup) -> None:
    """
    Validate the top-level leg rig group.

    Expected structure:
        leg_rig_group[0] -> left_leg_system
        leg_rig_group[1] -> right_leg_system
    """
    if not isinstance(leg_rig_group, VGroup):
        raise TypeError(
            f"leg_rig_group must be a VGroup, got {type(leg_rig_group).__name__}"
        )

    if len(leg_rig_group) < _MIN_RIG_SYSTEM_COUNT:
        raise ValueError(
            f"leg_rig_group must contain at least {_MIN_RIG_SYSTEM_COUNT} systems, "
            f"got {len(leg_rig_group)}"
        )


def _validate_leg_system(leg_system: VGroup) -> None:
    """
    Validate one leg system.

    Expected structure:
        leg_system[0] -> leg
        leg_system[1] -> foot
    """
    if not isinstance(leg_system, VGroup):
        raise TypeError(
            f"leg_system must be a VGroup, got {type(leg_system).__name__}"
        )

    if len(leg_system) < _MIN_LEG_SYSTEM_PART_COUNT:
        raise ValueError(
            f"leg_system must contain at least {_MIN_LEG_SYSTEM_PART_COUNT} parts, "
            f"got {len(leg_system)}"
        )


def _build_leg_system(
    *,
    side: str,
    body_center=None,
    direction: str = "down",
) -> VGroup:
    """
    Build one leg system (leg + foot) correctly linked.

    The foot is attached to the actual leg instance built here.
    """
    if side == "left":
        leg = build_left_leg(
            body_center=body_center,
            direction=direction,
        )
        foot = build_left_foot(
            body_center=body_center,
            leg=leg,
        )
        system_name = "creature_left_leg_system"

    elif side == "right":
        leg = build_right_leg(
            body_center=body_center,
            direction=direction,
        )
        foot = build_right_foot(
            body_center=body_center,
            leg=leg,
        )
        system_name = "creature_right_leg_system"

    else:
        raise ValueError(f"Unsupported side {side!r}. Expected 'left' or 'right'.")

    leg_system = VGroup(leg, foot)
    leg_system.name = system_name

    # Lightweight metadata for later rig/action work
    leg_system.leg = leg
    leg_system.foot = foot
    leg_system.side = side
    leg_system.direction = direction
    leg_system.body_center = body_center

    if DEBUG_MODE:
        logger.debug(
            "Built leg system | side=%s leg=%s foot=%s direction=%s",
            side,
            getattr(leg, "name", "leg"),
            getattr(foot, "name", "foot"),
            direction,
        )

    return leg_system


def _refresh_leg_rig_group_metadata(leg_rig_group: VGroup, *, body_center=None) -> VGroup:
    """
    Refresh standard metadata after one or more systems are replaced.
    """
    _validate_leg_rig_group(leg_rig_group)

    left_system = leg_rig_group[_LEFT_SYSTEM_INDEX]
    right_system = leg_rig_group[_RIGHT_SYSTEM_INDEX]

    _validate_leg_system(left_system)
    _validate_leg_system(right_system)

    leg_rig_group.left_system = left_system
    leg_rig_group.right_system = right_system

    leg_rig_group.left_leg = left_system[_SYSTEM_LEG_INDEX]
    leg_rig_group.left_foot = left_system[_SYSTEM_FOOT_INDEX]
    leg_rig_group.right_leg = right_system[_SYSTEM_LEG_INDEX]
    leg_rig_group.right_foot = right_system[_SYSTEM_FOOT_INDEX]

    if body_center is not None:
        leg_rig_group.body_center = body_center

    return leg_rig_group


# ============================================================
# Leg system builders
# ============================================================

def build_left_leg_system(
    body_center=None,
    *,
    direction: str = "down",
) -> VGroup:
    """
    Build left leg + left foot together.

    Returns:
        VGroup(left_leg, left_foot)
    """
    if LOG_CREATURE_BUILD:
        logger.info("Building left leg system")

    left_leg_system = _build_leg_system(
        side="left",
        body_center=body_center,
        direction=direction,
    )

    if LOG_CREATURE_BUILD:
        logger.info("Left leg system created successfully")

    return left_leg_system


def build_right_leg_system(
    body_center=None,
    *,
    direction: str = "down",
) -> VGroup:
    """
    Build right leg + right foot together.

    Returns:
        VGroup(right_leg, right_foot)
    """
    if LOG_CREATURE_BUILD:
        logger.info("Building right leg system")

    right_leg_system = _build_leg_system(
        side="right",
        body_center=body_center,
        direction=direction,
    )

    if LOG_CREATURE_BUILD:
        logger.info("Right leg system created successfully")

    return right_leg_system


def build_leg_rig_group(
    body_center=None,
    *,
    left_direction: str = "down",
    right_direction: str = "down",
) -> VGroup:
    """
    Build both leg systems together.

    Returns:
        VGroup(left_leg_system, right_leg_system)
    """
    if LOG_CREATURE_BUILD:
        logger.info("Building full leg rig group")

    left_leg_system = build_left_leg_system(
        body_center=body_center,
        direction=left_direction,
    )
    right_leg_system = build_right_leg_system(
        body_center=body_center,
        direction=right_direction,
    )

    leg_rig_group = VGroup(
        left_leg_system,
        right_leg_system,
    )
    leg_rig_group.name = "creature_leg_rig"

    _refresh_leg_rig_group_metadata(
        leg_rig_group,
        body_center=body_center,
    )

    if LOG_CREATURE_BUILD:
        logger.info("Leg rig group created successfully")

    return leg_rig_group


# ============================================================
# Leg rig map
# ============================================================

def build_leg_rig_map(body_center=None) -> dict[str, object]:
    """
    Build a simple leg rig map for clean access later.

    Returns a dictionary containing:
    - left leg
    - left foot
    - right leg
    - right foot
    - grouped systems
    """
    if LOG_CREATURE_BUILD:
        logger.info("Building leg rig map")

    group = build_leg_rig_group(body_center=body_center)

    rig_map = {
        "left_leg": group.left_leg,
        "left_foot": group.left_foot,
        "right_leg": group.right_leg,
        "right_foot": group.right_foot,
        "left_system": group.left_system,
        "right_system": group.right_system,
        "group": group,
        "body_center": body_center,
    }

    if LOG_CREATURE_BUILD:
        logger.info("Leg rig map created successfully")

    return rig_map


# ============================================================
# Rebuild helpers
# ============================================================

def rebuild_left_leg_system(
    leg_rig_group: VGroup,
    body_center=None,
    *,
    direction: str = "down",
) -> VGroup:
    """
    Replace the left leg system inside an existing leg rig group.

    Expected structure:
        leg_rig_group[0] -> left_leg_system
        leg_rig_group[1] -> right_leg_system
    """
    if LOG_CREATURE_BUILD:
        logger.info("Rebuilding left leg system")

    _validate_leg_rig_group(leg_rig_group)

    leg_rig_group.submobjects[_LEFT_SYSTEM_INDEX] = build_left_leg_system(
        body_center=body_center,
        direction=direction,
    )

    _refresh_leg_rig_group_metadata(
        leg_rig_group,
        body_center=body_center,
    )

    if LOG_CREATURE_BUILD:
        logger.info("Left leg system rebuilt successfully")

    return leg_rig_group


def rebuild_right_leg_system(
    leg_rig_group: VGroup,
    body_center=None,
    *,
    direction: str = "down",
) -> VGroup:
    """
    Replace the right leg system inside an existing leg rig group.

    Expected structure:
        leg_rig_group[0] -> left_leg_system
        leg_rig_group[1] -> right_leg_system
    """
    if LOG_CREATURE_BUILD:
        logger.info("Rebuilding right leg system")

    _validate_leg_rig_group(leg_rig_group)

    leg_rig_group.submobjects[_RIGHT_SYSTEM_INDEX] = build_right_leg_system(
        body_center=body_center,
        direction=direction,
    )

    _refresh_leg_rig_group_metadata(
        leg_rig_group,
        body_center=body_center,
    )

    if LOG_CREATURE_BUILD:
        logger.info("Right leg system rebuilt successfully")

    return leg_rig_group


# ============================================================
# Access helpers
# ============================================================

def get_left_leg_system(leg_rig_group: VGroup):
    """
    Return the left leg system.
    """
    _validate_leg_rig_group(leg_rig_group)
    return leg_rig_group[_LEFT_SYSTEM_INDEX]


def get_right_leg_system(leg_rig_group: VGroup):
    """
    Return the right leg system.
    """
    _validate_leg_rig_group(leg_rig_group)
    return leg_rig_group[_RIGHT_SYSTEM_INDEX]


def get_left_leg(left_leg_system: VGroup):
    """
    Return the leg object from the left leg system.
    """
    _validate_leg_system(left_leg_system)
    return left_leg_system[_SYSTEM_LEG_INDEX]


def get_left_foot(left_leg_system: VGroup):
    """
    Return the foot object from the left leg system.
    """
    _validate_leg_system(left_leg_system)
    return left_leg_system[_SYSTEM_FOOT_INDEX]


def get_right_leg(right_leg_system: VGroup):
    """
    Return the leg object from the right leg system.
    """
    _validate_leg_system(right_leg_system)
    return right_leg_system[_SYSTEM_LEG_INDEX]


def get_right_foot(right_leg_system: VGroup):
    """
    Return the foot object from the right leg system.
    """
    _validate_leg_system(right_leg_system)
    return right_leg_system[_SYSTEM_FOOT_INDEX]