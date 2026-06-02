"""
Leg construction for mathlab-mylinehub-creature.

This file builds connected leg systems for the creature.

Architecture rule:
- legs are connected body parts
- legs attach to hip anchors
- knees connect upper leg to lower leg
- ankles connect lower leg to feet
- feet attach to ankle anchors
- legs.py consumes knee_joint.py, ankle_joint.py, and feet.py
- legs should not move independently in scene code
- leg_rig.py / walk_action.py / step_action.py will control walking later
- audio is not handled here

Connection chain:

    Body / HipJoint
        |
        Left Hip
            |
            Upper Leg
                |
                KneeJoint
                    |
                    Lower Leg
                        |
                        AnkleJoint
                            |
                            Foot

    Body / HipJoint
        |
        Right Hip
            |
            Upper Leg
                |
                KneeJoint
                    |
                    Lower Leg
                        |
                        AnkleJoint
                            |
                            Foot
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
from typing import Optional

import numpy as np

from manimlib import RoundedRectangle
from manimlib import VGroup

from manimlib.constants import BLUE_E
from manimlib.constants import GREY_B

from mathlab_creature.config.defaults import DEBUG_MODE
from mathlab_creature.config.defaults import LOG_CREATURE_BUILD
from mathlab_creature.config.sizes import FOOT_HEIGHT
from mathlab_creature.config.sizes import FOOT_WIDTH
from mathlab_creature.config.sizes import JOINT_RADIUS

from mathlab_creature.core.anchors import get_left_hip_anchor
from mathlab_creature.core.anchors import get_right_hip_anchor
from mathlab_creature.core.geometry import angle_of_vector
from mathlab_creature.core.geometry import as_vec3
from mathlab_creature.core.geometry import direction
from mathlab_creature.core.geometry import distance
from mathlab_creature.core.geometry import midpoint
from mathlab_creature.core.geometry import point
from mathlab_creature.core.geometry import zero_point
from mathlab_creature.core.logger import get_logger
from mathlab_creature.core.naming import creature_pair_part_names
from mathlab_creature.core.naming import creature_part_name
from mathlab_creature.core.transforms import TransformNode
from mathlab_creature.core.transforms import create_transform_node

from mathlab_creature.creature.parts.ankle_joint import AnkleJoint
from mathlab_creature.creature.parts.ankle_joint import build_ankle_joint
from mathlab_creature.creature.parts.feet import Foot
from mathlab_creature.creature.parts.feet import build_left_foot
from mathlab_creature.creature.parts.feet import build_right_foot
from mathlab_creature.creature.parts.knee_joint import KneeJoint
from mathlab_creature.creature.parts.knee_joint import build_knee_joint


logger = get_logger(__name__)


Vector3 = np.ndarray
Vec3Like = np.ndarray | Iterable[float]


@dataclass
class LegConfig:
    """
    Tunable leg proportions.
    """

    upper_leg_length: float = 1.10
    lower_leg_length: float = 1.00

    upper_leg_width: float = 0.26
    lower_leg_width: float = 0.22

    leg_color: str = BLUE_E
    joint_color: str = GREY_B

    corner_radius: float = 0.10
    joint_radius: float = JOINT_RADIUS

    hip_offset_x: float = 0.32
    knee_bend_x: float = 0.12

    foot_width: float = FOOT_WIDTH
    foot_height: float = FOOT_HEIGHT


def _validate_numeric(
    name: str,
    value: float | int,
) -> float:
    if not isinstance(value, (int, float)):
        raise TypeError(
            f"{name} must be numeric, got {type(value).__name__}"
        )

    return float(value)


def _validate_positive(
    name: str,
    value: float | int,
) -> float:
    value = _validate_numeric(name, value)

    if value <= 0:
        raise ValueError(
            f"{name} must be > 0, got {value}"
        )

    return value


def _validate_non_negative(
    name: str,
    value: float | int,
) -> float:
    value = _validate_numeric(name, value)

    if value < 0:
        raise ValueError(
            f"{name} must be >= 0, got {value}"
        )

    return value


def _validate_side(
    side: str,
) -> str:
    if not isinstance(side, str):
        raise TypeError(
            f"side must be str, got {type(side).__name__}"
        )

    side = side.strip().lower()

    if side not in {"left", "right"}:
        raise ValueError(
            "side must be 'left' or 'right'"
        )

    return side


def _coerce_point3(
    value: Optional[Vec3Like],
    name: str = "value",
) -> Vector3:
    if value is None:
        return zero_point()

    return as_vec3(
        value,
        name=name,
    )


def _validated_config(
    config: Optional[LegConfig],
) -> LegConfig:
    config = config or LegConfig()

    config.upper_leg_length = _validate_positive(
        "config.upper_leg_length",
        config.upper_leg_length,
    )
    config.lower_leg_length = _validate_positive(
        "config.lower_leg_length",
        config.lower_leg_length,
    )
    config.upper_leg_width = _validate_positive(
        "config.upper_leg_width",
        config.upper_leg_width,
    )
    config.lower_leg_width = _validate_positive(
        "config.lower_leg_width",
        config.lower_leg_width,
    )
    config.corner_radius = _validate_non_negative(
        "config.corner_radius",
        config.corner_radius,
    )
    config.joint_radius = _validate_positive(
        "config.joint_radius",
        config.joint_radius,
    )
    config.hip_offset_x = _validate_non_negative(
        "config.hip_offset_x",
        config.hip_offset_x,
    )
    config.foot_width = _validate_positive(
        "config.foot_width",
        config.foot_width,
    )
    config.foot_height = _validate_positive(
        "config.foot_height",
        config.foot_height,
    )

    return config


def _segment_rotation_from_top_to_bottom(
    top_point: Vec3Like,
    bottom_point: Vec3Like,
) -> float:
    """
    Return rotation angle for a vertical rounded rectangle segment.

    RoundedRectangle is naturally vertical.
    A downward segment has direction angle -pi/2.
    Rotation needed = current_direction - default_down_direction.
    """
    top = _coerce_point3(top_point, "top_point")
    bottom = _coerce_point3(bottom_point, "bottom_point")

    segment_direction = bottom - top

    return angle_of_vector(segment_direction) + (np.pi / 2.0)


class LegSegment(VGroup):
    """
    Visual leg segment between two anchor points.

    This segment is local visual geometry only.
    It does not solve IK by itself.
    """

    def __init__(
        self,
        start_point: Vec3Like,
        end_point: Vec3Like,
        *,
        width: float,
        color=BLUE_E,
        corner_radius: float = 0.10,
        name: str = "leg_segment",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.segment_name = str(name)

        self.start_point = _coerce_point3(
            start_point,
            "start_point",
        )
        self.end_point = _coerce_point3(
            end_point,
            "end_point",
        )

        self.length = distance(
            self.start_point,
            self.end_point,
        )
        self.width = _validate_positive(
            "width",
            width,
        )
        self.corner_radius = _validate_non_negative(
            "corner_radius",
            corner_radius,
        )

        self.transform_node = create_transform_node(
            name=self.segment_name,
            mobject=self,
        )

        self._build_segment()
        self._position_segment()
        self._register_anchors()

        self.name = self.segment_name
        self.is_creature_leg_segment = True

    def _build_segment(self) -> None:
        """
        Build rounded rectangle segment.
        """
        self.body = RoundedRectangle(
            width=self.width,
            height=max(self.length, 0.001),
            corner_radius=min(
                self.corner_radius,
                self.width / 2.0,
            ),
            stroke_width=0,
            fill_opacity=1.0,
            fill_color=self.color if hasattr(self, "color") else BLUE_E,
        )

        self.add(
            self.body,
        )

    def _position_segment(self) -> None:
        """
        Place segment between start and end.
        """
        center = midpoint(
            self.start_point,
            self.end_point,
        )

        self.move_to(
            center,
        )

        rotation_angle = _segment_rotation_from_top_to_bottom(
            self.start_point,
            self.end_point,
        )

        self.rotate(
            rotation_angle,
            about_point=center,
        )

    def _register_anchors(self) -> None:
        """
        Register local/world anchor metadata.
        """
        self.top_anchor = self.start_point
        self.bottom_anchor = self.end_point
        self.center_anchor = midpoint(
            self.start_point,
            self.end_point,
        )

        self.transform_node.set_center_point(
            self.center_anchor,
        )
        self.transform_node.set_root_pivot(
            self.top_anchor,
        )

    def get_top_anchor(self) -> Vector3:
        return np.array(
            self.top_anchor,
            dtype=float,
        )

    def get_bottom_anchor(self) -> Vector3:
        return np.array(
            self.bottom_anchor,
            dtype=float,
        )

    def get_center_anchor(self) -> Vector3:
        return np.array(
            self.center_anchor,
            dtype=float,
        )

    def get_transform_node(self) -> TransformNode:
        return self.transform_node


class ArticulatedLeg(VGroup):
    """
    Complete connected leg system.

    Structure:
        hip anchor
            -> upper leg
            -> knee joint
            -> lower leg
            -> ankle joint
            -> foot
    """

    def __init__(
        self,
        config: Optional[LegConfig] = None,
        side: str = "left",
        name: str = "leg",
        hip_position: Optional[Vec3Like] = None,
        knee_position: Optional[Vec3Like] = None,
        ankle_position: Optional[Vec3Like] = None,
        foot_position: Optional[Vec3Like] = None,
        include_foot: bool = True,
        debug_enabled: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.config = _validated_config(config)
        self.side = _validate_side(side)
        self.leg_name = str(name)
        self.include_foot = bool(include_foot)
        self.debug_enabled = bool(debug_enabled)

        self.transform_node = create_transform_node(
            name=self.leg_name,
            mobject=self,
        )

        self.hip_anchor = (
            _coerce_point3(
                hip_position,
                "hip_position",
            )
            if hip_position is not None
            else self._default_hip_position()
        )

        self.knee_anchor = (
            _coerce_point3(
                knee_position,
                "knee_position",
            )
            if knee_position is not None
            else self._default_knee_position()
        )

        self.ankle_anchor = (
            _coerce_point3(
                ankle_position,
                "ankle_position",
            )
            if ankle_position is not None
            else self._default_ankle_position()
        )

        self.foot_center = (
            _coerce_point3(
                foot_position,
                "foot_position",
            )
            if foot_position is not None
            else self._default_foot_center()
        )

        self._build_parts()
        self._assemble()
        self._register_anchors()
        self._assemble_transform_hierarchy()

        self.name = self.leg_name
        self.is_creature_leg = True

    def _side_multiplier(self) -> float:
        return -1.0 if self.side == "left" else 1.0

    def _default_hip_position(self) -> Vector3:
        return point(
            self._side_multiplier() * self.config.hip_offset_x,
            0.0,
            0.0,
        )

    def _default_knee_position(self) -> Vector3:
        return point(
            self.hip_anchor[0]
            + self._side_multiplier() * self.config.knee_bend_x,
            self.hip_anchor[1] - self.config.upper_leg_length,
            self.hip_anchor[2],
        )

    def _default_ankle_position(self) -> Vector3:
        return point(
            self.hip_anchor[0],
            self.hip_anchor[1]
            - self.config.upper_leg_length
            - self.config.lower_leg_length,
            self.hip_anchor[2],
        )

    def _default_foot_center(self) -> Vector3:
        return point(
            self.ankle_anchor[0],
            self.ankle_anchor[1] - (self.config.foot_height / 2.0),
            self.ankle_anchor[2],
        )

    def _build_parts(self) -> None:
        """
        Build all leg child parts.
        """
        self.upper_leg = LegSegment(
            self.hip_anchor,
            self.knee_anchor,
            width=self.config.upper_leg_width,
            color=self.config.leg_color,
            corner_radius=self.config.corner_radius,
            name=f"{self.side}_upper_leg",
        )

        self.knee_joint = build_knee_joint(
            position=self.knee_anchor,
            debug_enabled=self.debug_enabled,
        )
        self.knee_joint.side = self.side

        self.lower_leg = LegSegment(
            self.knee_anchor,
            self.ankle_anchor,
            width=self.config.lower_leg_width,
            color=self.config.leg_color,
            corner_radius=self.config.corner_radius,
            name=f"{self.side}_lower_leg",
        )

        self.ankle_joint = build_ankle_joint(
            position=self.ankle_anchor,
            debug_enabled=self.debug_enabled,
        )
        self.ankle_joint.side = self.side

        self.foot = None

        if self.include_foot:
            if self.side == "left":
                self.foot = build_left_foot(
                    position=self.foot_center,
                    debug_enabled=self.debug_enabled,
                )
            else:
                self.foot = build_right_foot(
                    position=self.foot_center,
                    debug_enabled=self.debug_enabled,
                )

            self.foot.side = self.side

    def _assemble(self) -> None:
        """
        Add visual parts in correct order.
        """
        parts = [
            self.upper_leg,
            self.knee_joint,
            self.lower_leg,
            self.ankle_joint,
        ]

        if self.foot is not None:
            parts.append(
                self.foot,
            )

        self.add(
            *parts,
        )

    def _register_anchors(self) -> None:
        """
        Register important leg anchors.
        """
        self.center_anchor = midpoint(
            self.hip_anchor,
            self.ankle_anchor,
        )

        self.transform_node.set_center_point(
            self.center_anchor,
        )
        self.transform_node.set_root_pivot(
            self.hip_anchor,
        )

        self.upper_leg_anchor = self.hip_anchor
        self.lower_leg_anchor = self.knee_anchor
        self.foot_anchor = self.ankle_anchor
        self.end_point = self.foot_center

    def _assemble_transform_hierarchy(self) -> None:
        """
        Build transform-node hierarchy metadata.

        Visual geometry is already placed in Manim.
        These nodes are for future rig/controller use.
        """
        self.transform_node.add_child(
            self.upper_leg.get_transform_node(),
        )
        self.upper_leg.get_transform_node().add_child(
            self.knee_joint.get_transform_node(),
        )
        self.knee_joint.get_transform_node().add_child(
            self.lower_leg.get_transform_node(),
        )
        self.lower_leg.get_transform_node().add_child(
            self.ankle_joint.get_transform_node(),
        )

        if self.foot is not None:
            self.ankle_joint.get_transform_node().add_child(
                self.foot.get_transform_node(),
            )

    def get_transform_node(self) -> TransformNode:
        return self.transform_node

    def get_upper_leg(self) -> LegSegment:
        return self.upper_leg

    def get_lower_leg(self) -> LegSegment:
        return self.lower_leg

    def get_knee_joint(self) -> KneeJoint:
        return self.knee_joint

    def get_ankle_joint(self) -> AnkleJoint:
        return self.ankle_joint

    def get_foot(self) -> Optional[Foot]:
        return self.foot

    def get_hip_anchor(self) -> Vector3:
        return np.array(
            self.hip_anchor,
            dtype=float,
        )

    def get_knee_anchor(self) -> Vector3:
        return np.array(
            self.knee_anchor,
            dtype=float,
        )

    def get_ankle_anchor(self) -> Vector3:
        return np.array(
            self.ankle_anchor,
            dtype=float,
        )

    def get_foot_center(self) -> Vector3:
        return np.array(
            self.foot_center,
            dtype=float,
        )

    def get_center_anchor(self) -> Vector3:
        return np.array(
            self.center_anchor,
            dtype=float,
        )

    def get_anchor_map(self) -> dict[str, Vector3]:
        return {
            "hip": self.get_hip_anchor(),
            "knee": self.get_knee_anchor(),
            "ankle": self.get_ankle_anchor(),
            "foot_center": self.get_foot_center(),
            "center": self.get_center_anchor(),
        }

    def set_knee_angle(
        self,
        angle: float,
    ) -> None:
        """
        Store/update knee angle state.

        Visual IK animation will be handled later by leg_rig.py.
        """
        self.knee_joint.set_joint_angle(
            angle,
        )

    def set_ankle_angle(
        self,
        angle: float,
    ) -> None:
        """
        Store/update ankle angle state.
        """
        self.ankle_joint.set_ankle_angle(
            angle,
        )

    def set_foot_planted(self) -> None:
        """
        Mark ankle/foot as planted.
        """
        self.ankle_joint.set_planted()

        if self.foot is not None:
            self.foot.set_planted()

    def set_foot_lifted(self) -> None:
        """
        Mark ankle/foot as lifted.
        """
        self.ankle_joint.set_lifted()

        if self.foot is not None:
            self.foot.set_lifted()

    def reset_leg_state(self) -> None:
        """
        Reset procedural leg state.
        """
        self.knee_joint.reset_joint()
        self.ankle_joint.reset_joint()

        if self.foot is not None:
            self.foot.reset_foot()

    def print_hierarchy(self) -> None:
        self.transform_node.print_tree()

    def debug_print(self) -> None:
        print("========== LEG DEBUG ==========")
        print("Name:", self.leg_name)
        print("Side:", self.side)
        print("Anchors:", self.get_anchor_map())
        print("Has Foot:", self.foot is not None)
        print("================================")

    def __repr__(self) -> str:
        return (
            "ArticulatedLeg("
            f"name={self.leg_name!r}, "
            f"side={self.side!r}"
            ")"
        )


def build_leg(
    *,
    side: str = "left",
    name: Optional[str] = None,
    hip_position: Optional[Vec3Like] = None,
    knee_position: Optional[Vec3Like] = None,
    ankle_position: Optional[Vec3Like] = None,
    foot_position: Optional[Vec3Like] = None,
    config: Optional[LegConfig] = None,
    include_foot: bool = True,
    debug_enabled: Optional[bool] = None,
) -> ArticulatedLeg:
    """
    Build one connected leg.
    """
    side = _validate_side(
        side,
    )

    if debug_enabled is None:
        debug_enabled = DEBUG_MODE

    if name is None:
        name = creature_part_name(
            f"{side}_leg",
        )

    if LOG_CREATURE_BUILD:
        logger.info(
            "Building %s leg",
            side,
        )

    leg = ArticulatedLeg(
        config=config,
        side=side,
        name=name,
        hip_position=hip_position,
        knee_position=knee_position,
        ankle_position=ankle_position,
        foot_position=foot_position,
        include_foot=include_foot,
        debug_enabled=debug_enabled,
    )

    if LOG_CREATURE_BUILD:
        logger.info(
            "%s leg created successfully",
            side.capitalize(),
        )

    return leg


def build_left_leg(
    body_center: Optional[Vec3Like] = None,
    *,
    hip_position: Optional[Vec3Like] = None,
    knee_position: Optional[Vec3Like] = None,
    ankle_position: Optional[Vec3Like] = None,
    foot_position: Optional[Vec3Like] = None,
    config: Optional[LegConfig] = None,
    include_foot: bool = True,
    debug_enabled: Optional[bool] = None,
) -> ArticulatedLeg:
    """
    Build left connected leg.

    If hip_position is supplied, it overrides body_center anchor.
    """
    resolved_hip = (
        _coerce_point3(
            hip_position,
            "hip_position",
        )
        if hip_position is not None
        else get_left_hip_anchor(
            body_center,
        )
    )

    return build_leg(
        side="left",
        hip_position=resolved_hip,
        knee_position=knee_position,
        ankle_position=ankle_position,
        foot_position=foot_position,
        config=config,
        include_foot=include_foot,
        debug_enabled=debug_enabled,
    )


def build_right_leg(
    body_center: Optional[Vec3Like] = None,
    *,
    hip_position: Optional[Vec3Like] = None,
    knee_position: Optional[Vec3Like] = None,
    ankle_position: Optional[Vec3Like] = None,
    foot_position: Optional[Vec3Like] = None,
    config: Optional[LegConfig] = None,
    include_foot: bool = True,
    debug_enabled: Optional[bool] = None,
) -> ArticulatedLeg:
    """
    Build right connected leg.

    If hip_position is supplied, it overrides body_center anchor.
    """
    resolved_hip = (
        _coerce_point3(
            hip_position,
            "hip_position",
        )
        if hip_position is not None
        else get_right_hip_anchor(
            body_center,
        )
    )

    return build_leg(
        side="right",
        hip_position=resolved_hip,
        knee_position=knee_position,
        ankle_position=ankle_position,
        foot_position=foot_position,
        config=config,
        include_foot=include_foot,
        debug_enabled=debug_enabled,
    )


def build_legs(
    body_center: Optional[Vec3Like] = None,
    *,
    left_hip_position: Optional[Vec3Like] = None,
    right_hip_position: Optional[Vec3Like] = None,
    config: Optional[LegConfig] = None,
    include_feet: bool = True,
    debug_enabled: Optional[bool] = None,
    assign_group_name: bool = True,
) -> VGroup:
    """
    Build both connected legs.
    """
    if LOG_CREATURE_BUILD:
        logger.info(
            "Building both legs"
        )

    left_leg = build_left_leg(
        body_center=body_center,
        hip_position=left_hip_position,
        config=config,
        include_foot=include_feet,
        debug_enabled=debug_enabled,
    )

    right_leg = build_right_leg(
        body_center=body_center,
        hip_position=right_hip_position,
        config=config,
        include_foot=include_feet,
        debug_enabled=debug_enabled,
    )

    legs = VGroup(
        left_leg,
        right_leg,
    )

    if assign_group_name:
        left_name, right_name = creature_pair_part_names(
            "leg",
        )
        legs.name = "creature_legs"
        legs.left_leg_name = left_name
        legs.right_leg_name = right_name

    legs.left_leg = left_leg
    legs.right_leg = right_leg
    legs.left_foot = left_leg.get_foot()
    legs.right_foot = right_leg.get_foot()
    legs.body_center = body_center
    legs.include_feet = include_feet
    legs.is_creature_legs_group = True

    if LOG_CREATURE_BUILD:
        logger.info(
            "Legs created successfully"
        )

    return legs


def build_leg_pair(
    config: Optional[LegConfig] = None,
) -> VGroup:
    """
    Backward-compatible alias.

    Prefer build_legs().
    """
    return build_legs(
        config=config,
    )


def get_leg_hip_anchor(
    leg: ArticulatedLeg,
) -> Vector3:
    return leg.get_hip_anchor()


def get_leg_knee_anchor(
    leg: ArticulatedLeg,
) -> Vector3:
    return leg.get_knee_anchor()


def get_leg_ankle_anchor(
    leg: ArticulatedLeg,
) -> Vector3:
    return leg.get_ankle_anchor()


def get_leg_foot(
    leg: ArticulatedLeg,
) -> Optional[Foot]:
    return leg.get_foot()


__all__ = [
    "Vector3",
    "Vec3Like",
    "LegConfig",
    "LegSegment",
    "ArticulatedLeg",
    "build_leg",
    "build_left_leg",
    "build_right_leg",
    "build_legs",
    "build_leg_pair",
    "get_leg_hip_anchor",
    "get_leg_knee_anchor",
    "get_leg_ankle_anchor",
    "get_leg_foot",
]