# File: mathlab_creature/creature/rigs/arm_rig.py

"""
Arm rig helpers for mathlab-mylinehub-creature.

Responsibilities
----------------
- build arm systems
- organize left/right arm hierarchy
- expose reusable arm rig access
- support future animation systems
- support waving / pointing / gestures
- maintain predictable arm access

FIXES
-----
- added transform-node compatibility
- added get_transform_node()
- compatible with body_rig.py hierarchy system
- preserves all existing functionality
"""

from __future__ import annotations

from manimlib import VGroup

from mathlab_creature.config.defaults import (
    DEBUG_MODE,
    LOG_CREATURE_BUILD,
)

from mathlab_creature.creature.parts.arms import (
    build_left_arm,
    build_right_arm,
)

from mathlab_creature.creature.parts.hands import (
    build_left_hand,
    build_right_hand,
)

from mathlab_creature.core.transforms import (
    create_transform_node,
)

from mathlab_creature.core.logger import (
    get_logger,
)

logger = get_logger(__name__)


# ============================================================
# INTERNAL HELPERS
# ============================================================

def _validate_arm_rig_group(
    group: VGroup,
) -> None:

    if not isinstance(group, VGroup):

        raise TypeError(
            f"arm_rig_group must be a VGroup, "
            f"got {type(group).__name__}"
        )

    if len(group) < 2:

        raise ValueError(
            "arm_rig_group must contain "
            "at least 2 systems"
        )


def _build_arm_system(
    *,
    body_center=None,
    side: str,
    direction: str = "down",
) -> VGroup:
    """
    Build one complete arm system.
    """

    # --------------------------------------------------------
    # LEFT
    # --------------------------------------------------------

    if side == "left":

        arm = build_left_arm(
            body_center=body_center,
            direction=direction,
        )

        hand = build_left_hand(
            body_center=body_center,
            arm=arm,
        )

    # --------------------------------------------------------
    # RIGHT
    # --------------------------------------------------------

    elif side == "right":

        arm = build_right_arm(
            body_center=body_center,
            direction=direction,
        )

        hand = build_right_hand(
            body_center=body_center,
            arm=arm,
        )

    else:

        raise ValueError(
            f"Invalid side: {side}"
        )

    # --------------------------------------------------------
    # SYSTEM
    # --------------------------------------------------------

    system = VGroup(
        arm,
        hand,
    )

    # --------------------------------------------------------
    # TRANSFORM NODE
    # --------------------------------------------------------

    system.transform_node = create_transform_node(
        name=f"{side}_arm_system",
        mobject=system,
    )

    system.get_transform_node = (
        lambda: system.transform_node
    )

    # --------------------------------------------------------
    # METADATA
    # --------------------------------------------------------

    system.arm = arm

    system.hand = hand

    system.side = side

    system.direction = direction

    if DEBUG_MODE:

        logger.debug(
            "Built arm system | side=%s arm=%s hand=%s",
            side,
            getattr(
                arm,
                "name",
                "arm",
            ),
            getattr(
                hand,
                "name",
                "hand",
            ),
        )

    return system


# ============================================================
# PUBLIC BUILDERS
# ============================================================

def build_left_arm_system(
    body_center=None,
    *,
    direction: str = "down",
) -> VGroup:

    if LOG_CREATURE_BUILD:

        logger.info(
            "Building left arm system"
        )

    return _build_arm_system(
        body_center=body_center,
        side="left",
        direction=direction,
    )


def build_right_arm_system(
    body_center=None,
    *,
    direction: str = "down",
) -> VGroup:

    if LOG_CREATURE_BUILD:

        logger.info(
            "Building right arm system"
        )

    return _build_arm_system(
        body_center=body_center,
        side="right",
        direction=direction,
    )


# ============================================================
# MAIN ARM RIG
# ============================================================

def build_arm_rig(
    body_center=None,
    *,
    left_direction: str = "down",
    right_direction: str = "down",
) -> VGroup:
    """
    MAIN compatibility factory.
    """

    if LOG_CREATURE_BUILD:

        logger.info(
            "Building full arm rig"
        )

    left_system = (
        build_left_arm_system(
            body_center=body_center,
            direction=left_direction,
        )
    )

    right_system = (
        build_right_arm_system(
            body_center=body_center,
            direction=right_direction,
        )
    )

    group = VGroup(
        left_system,
        right_system,
    )

    # --------------------------------------------------------
    # TRANSFORM NODE
    # --------------------------------------------------------

    group.transform_node = create_transform_node(
        name="creature_arm_rig",
        mobject=group,
    )

    group.get_transform_node = (
        lambda: group.transform_node
    )

    # --------------------------------------------------------
    # METADATA
    # --------------------------------------------------------

    group.left_system = left_system

    group.right_system = right_system

    group.left_arm = left_system.arm

    group.right_arm = right_system.arm

    group.left_hand = left_system.hand

    group.right_hand = right_system.hand

    group.name = "creature_arm_rig"

    if LOG_CREATURE_BUILD:

        logger.info(
            "Arm rig created successfully"
        )

    return group


# ============================================================
# COMPATIBILITY ALIAS
# ============================================================

def build_arm_rig_group(
    body_center=None,
    *,
    left_direction: str = "down",
    right_direction: str = "down",
) -> VGroup:
    """
    Backward-compatible alias.
    """

    return build_arm_rig(
        body_center=body_center,
        left_direction=left_direction,
        right_direction=right_direction,
    )


# ============================================================
# ARM RIG MAP
# ============================================================

def build_arm_rig_map(
    body_center=None,
) -> dict[str, object]:
    """
    Build clean arm rig access map.
    """

    if LOG_CREATURE_BUILD:

        logger.info(
            "Building arm rig map"
        )

    group = build_arm_rig(
        body_center
    )

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
# REBUILD HELPERS
# ============================================================

def rebuild_left_arm_system(
    arm_rig_group: VGroup,
    body_center=None,
    *,
    direction: str = "down",
) -> VGroup:

    if LOG_CREATURE_BUILD:

        logger.info(
            "Rebuilding left arm system"
        )

    _validate_arm_rig_group(
        arm_rig_group
    )

    arm_rig_group.submobjects[0] = (
        build_left_arm_system(
            body_center=body_center,
            direction=direction,
        )
    )

    return arm_rig_group


def rebuild_right_arm_system(
    arm_rig_group: VGroup,
    body_center=None,
    *,
    direction: str = "down",
) -> VGroup:

    if LOG_CREATURE_BUILD:

        logger.info(
            "Rebuilding right arm system"
        )

    _validate_arm_rig_group(
        arm_rig_group
    )

    arm_rig_group.submobjects[1] = (
        build_right_arm_system(
            body_center=body_center,
            direction=direction,
        )
    )

    return arm_rig_group


# ============================================================
# ACCESS HELPERS
# ============================================================

def get_left_arm_system(
    group: VGroup,
):

    _validate_arm_rig_group(
        group
    )

    return group[0]


def get_right_arm_system(
    group: VGroup,
):

    _validate_arm_rig_group(
        group
    )

    return group[1]


def get_left_arm(
    system: VGroup,
):
    return system.arm


def get_left_hand(
    system: VGroup,
):
    return system.hand


def get_right_arm(
    system: VGroup,
):
    return system.arm


def get_right_hand(
    system: VGroup,
):
    return system.hand