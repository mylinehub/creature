"""
Arm rig for mathlab-mylinehub-creature.

This file controls already-built arm systems.

Architecture rule:
- arm_rig.py does not create disconnected floating parts
- arm_rig.py can build fallback arms if needed
- arm_rig.py controls arm/hand metadata
- arm_rig.py does not animate directly
- wave_action.py and point_action.py will call this rig later
- audio is not handled here

Connection chain:

    Action
        |
        ArmRig
            |
            Left Arm System
                |
                Arm Line
                Hand
            |
            Right Arm System
                |
                Arm Line
                Hand
"""

from __future__ import annotations

from typing import Optional

from manimlib import VGroup

from mathlab_creature.config.defaults import DEBUG_MODE
from mathlab_creature.config.defaults import LOG_CREATURE_BUILD

from mathlab_creature.core.logger import get_logger
from mathlab_creature.core.transforms import TransformNode
from mathlab_creature.core.transforms import create_transform_node

from mathlab_creature.creature.parts.arms import build_arms
from mathlab_creature.creature.parts.arms import build_left_arm
from mathlab_creature.creature.parts.arms import build_right_arm
from mathlab_creature.creature.parts.arms import get_arm_hand
from mathlab_creature.creature.parts.arms import get_arm_hand_anchor
from mathlab_creature.creature.parts.arms import get_arm_line
from mathlab_creature.creature.parts.arms import get_arm_shoulder_anchor


logger = get_logger(__name__)


_LEFT_SYSTEM_INDEX = 0
_RIGHT_SYSTEM_INDEX = 1
_ARM_RIG_MIN_SYSTEM_COUNT = 2


def _validate_arm_system(
    system: VGroup,
) -> None:
    if not isinstance(system, VGroup):
        raise TypeError(
            f"arm system must be VGroup, got {type(system).__name__}"
        )

    if not hasattr(system, "arm_line"):
        raise AttributeError(
            "arm system must have arm_line metadata"
        )


def _validate_arm_rig_group(
    group: VGroup,
) -> None:
    if not isinstance(group, VGroup):
        raise TypeError(
            f"arm_rig_group must be VGroup, got {type(group).__name__}"
        )

    if len(group) < _ARM_RIG_MIN_SYSTEM_COUNT:
        raise ValueError(
            "arm_rig_group must contain at least 2 arm systems"
        )


def _attach_arm_system_metadata(
    system: VGroup,
    *,
    side: str,
    direction: str = "down",
) -> VGroup:
    _validate_arm_system(system)

    system.side = side
    system.direction = direction

    system.arm = system.arm_line
    system.hand = getattr(system, "hand", None)

    system.shoulder_anchor = get_arm_shoulder_anchor(system)
    system.hand_anchor = get_arm_hand_anchor(system)

    if not hasattr(system, "transform_node"):
        system.transform_node = create_transform_node(
            name=f"{side}_arm_system",
            mobject=system,
        )
        system.get_transform_node = lambda: system.transform_node

    system.is_creature_arm_system = True

    return system


def _refresh_arm_rig_metadata(
    group: VGroup,
) -> VGroup:
    _validate_arm_rig_group(group)

    left_system = group[_LEFT_SYSTEM_INDEX]
    right_system = group[_RIGHT_SYSTEM_INDEX]

    _attach_arm_system_metadata(
        left_system,
        side="left",
        direction=getattr(left_system, "direction", "down"),
    )
    _attach_arm_system_metadata(
        right_system,
        side="right",
        direction=getattr(right_system, "direction", "down"),
    )

    group.left_system = left_system
    group.right_system = right_system

    group.left_arm = left_system.arm
    group.right_arm = right_system.arm

    group.left_hand = left_system.hand
    group.right_hand = right_system.hand

    if not hasattr(group, "transform_node"):
        group.transform_node = create_transform_node(
            name="creature_arm_rig",
            mobject=group,
        )
        group.get_transform_node = lambda: group.transform_node

    group.name = "creature_arm_rig"
    group.is_creature_arm_rig_group = True

    return group


class ArmRig:
    """
    Controller wrapper for arm systems.

    Controls:
    - access to left/right arms
    - access to left/right hands
    - pointing/waving state metadata
    - rebuild helpers
    """

    def __init__(
        self,
        arm_group: Optional[VGroup] = None,
        *,
        left_system: Optional[VGroup] = None,
        right_system: Optional[VGroup] = None,
        body_center=None,
        left_direction: str = "down",
        right_direction: str = "down",
    ) -> None:
        if arm_group is None:
            if left_system is None:
                left_system = build_left_arm(
                    body_center=body_center,
                    direction=left_direction,
                    include_hand=True,
                )

            if right_system is None:
                right_system = build_right_arm(
                    body_center=body_center,
                    direction=right_direction,
                    include_hand=True,
                )

            arm_group = VGroup(
                left_system,
                right_system,
            )
        else:
            _validate_arm_rig_group(arm_group)

        _refresh_arm_rig_metadata(arm_group)

        self.group = arm_group
        self.body_center = body_center

        self.left_system = arm_group.left_system
        self.right_system = arm_group.right_system

        self.left_arm = arm_group.left_arm
        self.right_arm = arm_group.right_arm

        self.left_hand = arm_group.left_hand
        self.right_hand = arm_group.right_hand

        self.transform_node = arm_group.transform_node

        self.current_pose = "rest"
        self.active_side = None

    def _sync_from_group(self) -> None:
        _refresh_arm_rig_metadata(self.group)

        self.left_system = self.group.left_system
        self.right_system = self.group.right_system

        self.left_arm = self.group.left_arm
        self.right_arm = self.group.right_arm

        self.left_hand = self.group.left_hand
        self.right_hand = self.group.right_hand

        self.transform_node = self.group.transform_node

    def get_group(self) -> VGroup:
        return self.group

    def get_transform_node(self) -> TransformNode:
        return self.transform_node

    def get_left_system(self) -> VGroup:
        return self.left_system

    def get_right_system(self) -> VGroup:
        return self.right_system

    def get_left_arm(self):
        return self.left_arm

    def get_right_arm(self):
        return self.right_arm

    def get_left_hand(self):
        return self.left_hand

    def get_right_hand(self):
        return self.right_hand

    def set_pose(
        self,
        pose_name: str,
        *,
        side: Optional[str] = None,
    ) -> None:
        """
        Store arm pose state.

        Actual movement will be performed later by wave_action.py,
        point_action.py, and animation controllers.
        """
        if not isinstance(pose_name, str):
            raise TypeError(
                f"pose_name must be str, got {type(pose_name).__name__}"
            )

        self.current_pose = pose_name.strip().lower()

        if side is not None:
            side = side.strip().lower()

            if side not in {"left", "right", "both"}:
                raise ValueError(
                    "side must be 'left', 'right', 'both', or None"
                )

        self.active_side = side

    def set_wave_pose(
        self,
        *,
        side: str = "right",
    ) -> None:
        self.set_pose(
            "wave",
            side=side,
        )

    def set_point_pose(
        self,
        *,
        side: str = "right",
    ) -> None:
        self.set_pose(
            "point",
            side=side,
        )

    def reset_pose(self) -> None:
        self.current_pose = "rest"
        self.active_side = None

    def rebuild_left_system(
        self,
        *,
        direction: str = "down",
    ) -> VGroup:
        self.group = rebuild_left_arm_system(
            self.group,
            body_center=self.body_center,
            direction=direction,
        )
        self._sync_from_group()
        return self.group

    def rebuild_right_system(
        self,
        *,
        direction: str = "down",
    ) -> VGroup:
        self.group = rebuild_right_arm_system(
            self.group,
            body_center=self.body_center,
            direction=direction,
        )
        self._sync_from_group()
        return self.group

    def debug_print(self) -> None:
        print("========== ARM RIG DEBUG ==========")
        print("Body Center:", self.body_center)
        print("Current Pose:", self.current_pose)
        print("Active Side:", self.active_side)
        print("Left System:", getattr(self.left_system, "name", "left_system"))
        print("Right System:", getattr(self.right_system, "name", "right_system"))
        print("Left Arm:", getattr(self.left_arm, "name", "left_arm"))
        print("Right Arm:", getattr(self.right_arm, "name", "right_arm"))
        print("Left Hand:", getattr(self.left_hand, "name", "left_hand"))
        print("Right Hand:", getattr(self.right_hand, "name", "right_hand"))
        print("===================================")


def build_left_arm_system(
    body_center=None,
    *,
    direction: str = "down",
) -> VGroup:
    """
    Build connected left arm system.
    """
    if LOG_CREATURE_BUILD:
        logger.info("Building left arm system")

    system = build_left_arm(
        body_center=body_center,
        direction=direction,
        include_hand=True,
    )

    _attach_arm_system_metadata(
        system,
        side="left",
        direction=direction,
    )

    if DEBUG_MODE:
        logger.debug(
            "Left arm system built | arm=%s hand=%s",
            getattr(system.arm, "name", "arm"),
            getattr(system.hand, "name", "hand"),
        )

    return system


def build_right_arm_system(
    body_center=None,
    *,
    direction: str = "down",
) -> VGroup:
    """
    Build connected right arm system.
    """
    if LOG_CREATURE_BUILD:
        logger.info("Building right arm system")

    system = build_right_arm(
        body_center=body_center,
        direction=direction,
        include_hand=True,
    )

    _attach_arm_system_metadata(
        system,
        side="right",
        direction=direction,
    )

    if DEBUG_MODE:
        logger.debug(
            "Right arm system built | arm=%s hand=%s",
            getattr(system.arm, "name", "arm"),
            getattr(system.hand, "name", "hand"),
        )

    return system


def build_arm_rig(
    body_center=None,
    *,
    left_direction: str = "down",
    right_direction: str = "down",
) -> ArmRig:
    """
    Build ArmRig wrapper.

    Existing actions should use this rig to control arm state.
    """
    if LOG_CREATURE_BUILD:
        logger.info("Building full arm rig")

    left_system = build_left_arm_system(
        body_center=body_center,
        direction=left_direction,
    )

    right_system = build_right_arm_system(
        body_center=body_center,
        direction=right_direction,
    )

    rig = ArmRig(
        left_system=left_system,
        right_system=right_system,
        body_center=body_center,
        left_direction=left_direction,
        right_direction=right_direction,
    )

    if LOG_CREATURE_BUILD:
        logger.info("Arm rig created successfully")

    return rig


def build_arm_rig_group(
    body_center=None,
    *,
    left_direction: str = "down",
    right_direction: str = "down",
) -> VGroup:
    """
    Compatibility helper returning only VGroup.
    """
    return build_arm_rig(
        body_center=body_center,
        left_direction=left_direction,
        right_direction=right_direction,
    ).get_group()


def build_arm_rig_map(
    body_center=None,
) -> dict[str, object]:
    """
    Build arm rig and return clean access map.
    """
    if LOG_CREATURE_BUILD:
        logger.info("Building arm rig map")

    rig = build_arm_rig(
        body_center=body_center,
    )

    group = rig.get_group()

    return {
        "rig": rig,
        "left_arm": rig.get_left_arm(),
        "left_hand": rig.get_left_hand(),
        "right_arm": rig.get_right_arm(),
        "right_hand": rig.get_right_hand(),
        "left_system": rig.get_left_system(),
        "right_system": rig.get_right_system(),
        "group": group,
    }


def rebuild_left_arm_system(
    arm_rig_group: VGroup,
    body_center=None,
    *,
    direction: str = "down",
) -> VGroup:
    if LOG_CREATURE_BUILD:
        logger.info("Rebuilding left arm system")

    _validate_arm_rig_group(
        arm_rig_group,
    )

    new_left_system = build_left_arm_system(
        body_center=body_center,
        direction=direction,
    )

    arm_rig_group.submobjects[_LEFT_SYSTEM_INDEX] = new_left_system

    _refresh_arm_rig_metadata(
        arm_rig_group,
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

    _validate_arm_rig_group(
        arm_rig_group,
    )

    new_right_system = build_right_arm_system(
        body_center=body_center,
        direction=direction,
    )

    arm_rig_group.submobjects[_RIGHT_SYSTEM_INDEX] = new_right_system

    _refresh_arm_rig_metadata(
        arm_rig_group,
    )

    return arm_rig_group


def get_left_arm_system(
    group: VGroup,
):
    _validate_arm_rig_group(
        group,
    )

    return group[_LEFT_SYSTEM_INDEX]


def get_right_arm_system(
    group: VGroup,
):
    _validate_arm_rig_group(
        group,
    )

    return group[_RIGHT_SYSTEM_INDEX]


def get_left_arm(
    system_or_group: VGroup,
):
    if hasattr(system_or_group, "left_arm"):
        return system_or_group.left_arm

    if hasattr(system_or_group, "arm"):
        return system_or_group.arm

    if hasattr(system_or_group, "arm_line"):
        return get_arm_line(system_or_group)

    raise AttributeError(
        "object must have left_arm, arm, or arm_line metadata"
    )


def get_left_hand(
    system_or_group: VGroup,
):
    if hasattr(system_or_group, "left_hand"):
        return system_or_group.left_hand

    if hasattr(system_or_group, "hand"):
        return system_or_group.hand

    return get_arm_hand(system_or_group)


def get_right_arm(
    system_or_group: VGroup,
):
    if hasattr(system_or_group, "right_arm"):
        return system_or_group.right_arm

    if hasattr(system_or_group, "arm"):
        return system_or_group.arm

    if hasattr(system_or_group, "arm_line"):
        return get_arm_line(system_or_group)

    raise AttributeError(
        "object must have right_arm, arm, or arm_line metadata"
    )


def get_right_hand(
    system_or_group: VGroup,
):
    if hasattr(system_or_group, "right_hand"):
        return system_or_group.right_hand

    if hasattr(system_or_group, "hand"):
        return system_or_group.hand

    return get_arm_hand(system_or_group)


__all__ = [
    "ArmRig",
    "build_left_arm_system",
    "build_right_arm_system",
    "build_arm_rig",
    "build_arm_rig_group",
    "build_arm_rig_map",
    "rebuild_left_arm_system",
    "rebuild_right_arm_system",
    "get_left_arm_system",
    "get_right_arm_system",
    "get_left_arm",
    "get_left_hand",
    "get_right_arm",
    "get_right_hand",
]