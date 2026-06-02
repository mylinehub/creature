"""
Ankle joint construction for mathlab-mylinehub-creature.

This file builds the ankle connector for the connected creature system.

Architecture rule:
- ankle joint is a connector part
- ankle joint does not build feet
- ankle joint does not build legs
- legs.py will place this joint between lower leg and foot
- feet.py provides the foot object
- leg_rig.py / kinematics.py will calculate ankle angle later
- ankle joint should not move independently in scene code
- audio is not handled here; audio may be triggered later by walk/step actions

Connection chain:

    HipJoint
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

from manimlib import Arc
from manimlib import Circle
from manimlib import Dot
from manimlib import Line
from manimlib import Text
from manimlib import VGroup

from manimlib.constants import BLUE_E
from manimlib.constants import GREEN
from manimlib.constants import GREY_B
from manimlib.constants import RED
from manimlib.constants import WHITE
from manimlib.constants import YELLOW

from mathlab_creature.config.defaults import DEBUG_MODE
from mathlab_creature.config.defaults import LOG_CREATURE_BUILD
from mathlab_creature.config.sizes import DEBUG_STROKE_WIDTH
from mathlab_creature.config.sizes import JOINT_RADIUS

from mathlab_creature.core.debug_draw import create_local_axes
from mathlab_creature.core.geometry import as_vec3
from mathlab_creature.core.geometry import point
from mathlab_creature.core.geometry import zero_point
from mathlab_creature.core.logger import get_logger
from mathlab_creature.core.naming import creature_part_name
from mathlab_creature.core.transforms import TransformNode
from mathlab_creature.core.transforms import create_transform_node


logger = get_logger(__name__)


Vector3 = np.ndarray
Vec3Like = np.ndarray | Iterable[float]


@dataclass
class AnkleJointConfig:
    """
    Tunable ankle joint configuration.
    """

    radius: float = JOINT_RADIUS

    fill_color: str = GREY_B
    outline_color: str = WHITE
    foot_direction_color: str = BLUE_E
    debug_color: str = YELLOW

    stroke_width: float = 2.0

    axis_length: float = 0.35
    angle_arc_radius: float = 0.24

    show_debug_axes: bool = False


def _validate_numeric(name: str, value: float | int) -> float:
    if not isinstance(value, (int, float)):
        raise TypeError(
            f"{name} must be numeric, got {type(value).__name__}"
        )
    return float(value)


def _validate_positive(name: str, value: float | int) -> float:
    value = _validate_numeric(name, value)
    if value <= 0:
        raise ValueError(f"{name} must be > 0, got {value}")
    return value


def _validate_non_negative(name: str, value: float | int) -> float:
    value = _validate_numeric(name, value)
    if value < 0:
        raise ValueError(f"{name} must be >= 0, got {value}")
    return value


def _coerce_point3(
    value: Optional[Vec3Like],
    name: str = "value",
) -> Vector3:
    if value is None:
        return zero_point()

    return as_vec3(value, name=name)


def _validated_config(config: Optional[AnkleJointConfig]) -> AnkleJointConfig:
    config = config or AnkleJointConfig()

    config.radius = _validate_positive("config.radius", config.radius)
    config.stroke_width = _validate_non_negative(
        "config.stroke_width",
        config.stroke_width,
    )
    config.axis_length = _validate_non_negative(
        "config.axis_length",
        config.axis_length,
    )
    config.angle_arc_radius = _validate_non_negative(
        "config.angle_arc_radius",
        config.angle_arc_radius,
    )

    return config


class AnkleJoint(VGroup):
    """
    Local ankle connector.

    Responsibilities:
    - visible ankle pivot
    - local ankle angle state
    - foot attachment anchor
    - lower leg attachment anchor
    - planted/lifted metadata
    - optional debug visualization

    This class does not build legs or feet.
    """

    def __init__(
        self,
        config: Optional[AnkleJointConfig] = None,
        name: str = "ankle_joint",
        position: Optional[Vec3Like] = None,
        debug_enabled: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.config = _validated_config(config)
        self.joint_name = str(name)

        self.current_angle = 0.0
        self.debug_enabled = bool(debug_enabled)
        self.is_planted = True

        self.transform_node = create_transform_node(
            name=self.joint_name,
            mobject=self,
        )

        self.transform_node.set_center_point(zero_point())
        self.transform_node.set_root_pivot(zero_point())

        self._register_anchors()
        self._build_joint()
        self._build_debug()
        self._update_debug_visibility()

        if position is not None:
            self.move_to(_coerce_point3(position, "position"))

        self.name = self.joint_name
        self.is_creature_ankle_joint = True

    def _register_anchors(self) -> None:
        """
        Register local ankle anchors.

        legs.py decides where ankle sits in the full leg chain.
        """
        self.root_anchor = zero_point()
        self.center_anchor = zero_point()

        self.lower_leg_anchor = point(
            0.0,
            self.config.radius,
            0.0,
        )

        self.foot_attachment_anchor = point(
            0.0,
            -self.config.radius,
            0.0,
        )

        self.upper_attachment_anchor = self.lower_leg_anchor

        self.transform_node.set_center_point(self.center_anchor)
        self.transform_node.set_root_pivot(self.root_anchor)

    def _build_joint(self) -> None:
        """
        Build main ankle geometry.
        """
        self.outer_joint = Circle(
            radius=self.config.radius,
            stroke_color=self.config.outline_color,
            stroke_width=self.config.stroke_width,
            fill_color=self.config.fill_color,
            fill_opacity=1.0,
        )

        self.inner_joint = Dot(
            point=zero_point(),
            radius=self.config.radius * 0.35,
            color=self.config.foot_direction_color,
        )

        self.foot_direction_line = Line(
            zero_point(),
            point(0.0, -0.38, 0.0),
            color=self.config.foot_direction_color,
            stroke_width=DEBUG_STROKE_WIDTH,
        )

        self.add(
            self.outer_joint,
            self.inner_joint,
            self.foot_direction_line,
        )

    def _build_debug(self) -> None:
        """
        Build ankle debug overlays.
        """
        self.debug_group = VGroup()

        self.axes_debug = create_local_axes(
            origin=zero_point(),
            axis_length=self.config.axis_length,
        )

        self.angle_arc = Arc(
            radius=self.config.angle_arc_radius,
            start_angle=-np.pi / 2.0,
            angle=0.001,
            color=self.config.debug_color,
            stroke_width=DEBUG_STROKE_WIDTH,
        )

        self.pivot_dot = Dot(
            point=self.root_anchor,
            radius=0.025,
            color=GREEN,
        )

        self.foot_target_line = Line(
            zero_point(),
            point(0.0, -0.55, 0.0),
            color=RED,
            stroke_width=DEBUG_STROKE_WIDTH,
        )

        self.angle_text = (
            Text(
                "0°",
                font_size=18,
            )
            .scale(0.35)
            .move_to(
                point(
                    0.0,
                    self.config.angle_arc_radius + 0.18,
                    0.0,
                )
            )
        )

        self.state_text = (
            Text(
                "PLANTED",
                font_size=18,
                color=GREEN,
            )
            .scale(0.35)
            .move_to(
                point(0.0, -0.45, 0.0)
            )
        )

        self.debug_group.add(
            self.axes_debug,
            self.angle_arc,
            self.pivot_dot,
            self.foot_target_line,
            self.angle_text,
            self.state_text,
        )

        self.add(self.debug_group)

    def _update_debug_visibility(self) -> None:
        opacity = 1.0 if self.debug_enabled else 0.0
        self.debug_group.set_opacity(opacity)

    def enable_debug(self) -> None:
        self.debug_enabled = True
        self._update_debug_visibility()

    def disable_debug(self) -> None:
        self.debug_enabled = False
        self._update_debug_visibility()

    def toggle_debug(self) -> None:
        self.debug_enabled = not self.debug_enabled
        self._update_debug_visibility()

    def set_ankle_angle(self, angle: float) -> None:
        """
        Set ankle articulation angle.

        This updates local state and debug visuals only.
        legs.py / leg_rig.py should control actual segment placement.
        """
        self.current_angle = _validate_numeric("angle", angle)
        self._update_visuals()

    def rotate_ankle(self, delta_angle: float) -> None:
        """
        Increment ankle articulation angle.
        """
        self.current_angle += _validate_numeric(
            "delta_angle",
            delta_angle,
        )
        self._update_visuals()

    def set_planted(self) -> None:
        """
        Mark connected foot as planted.
        """
        self.is_planted = True
        self._update_state_visual()

    def set_lifted(self) -> None:
        """
        Mark connected foot as lifted.
        """
        self.is_planted = False
        self._update_state_visual()

    def _update_visuals(self) -> None:
        """
        Update ankle debug angle visuals.
        """
        direction = point(
            np.sin(self.current_angle),
            -np.cos(self.current_angle),
            0.0,
        )

        new_line = Line(
            zero_point(),
            direction * 0.38,
            color=self.config.foot_direction_color,
            stroke_width=DEBUG_STROKE_WIDTH,
        )
        self.foot_direction_line.become(new_line)

        new_arc = Arc(
            radius=self.config.angle_arc_radius,
            start_angle=-np.pi / 2.0,
            angle=self.current_angle,
            color=self.config.debug_color,
            stroke_width=DEBUG_STROKE_WIDTH,
        )
        self.angle_arc.become(new_arc)

        degrees_value = round(float(np.degrees(self.current_angle)), 1)

        new_text = (
            Text(
                f"{degrees_value}°",
                font_size=18,
            )
            .scale(0.35)
            .move_to(
                point(
                    0.0,
                    self.config.angle_arc_radius + 0.18,
                    0.0,
                )
            )
        )
        self.angle_text.become(new_text)

        new_target_line = Line(
            zero_point(),
            direction * 0.55,
            color=RED,
            stroke_width=DEBUG_STROKE_WIDTH,
        )
        self.foot_target_line.become(new_target_line)

    def _update_state_visual(self) -> None:
        """
        Update planted/lifted state text.
        """
        state_label = "PLANTED" if self.is_planted else "LIFTED"
        color = GREEN if self.is_planted else YELLOW

        new_state = (
            Text(
                state_label,
                font_size=18,
                color=color,
            )
            .scale(0.35)
            .move_to(
                point(0.0, -0.45, 0.0)
            )
        )

        self.state_text.become(new_state)

    def get_transform_node(self) -> TransformNode:
        return self.transform_node

    def get_root_anchor(self) -> Vector3:
        return np.array(self.root_anchor, dtype=float)

    def get_lower_leg_anchor(self) -> Vector3:
        return np.array(self.lower_leg_anchor, dtype=float)

    def get_upper_attachment_anchor(self) -> Vector3:
        return self.get_lower_leg_anchor()

    def get_foot_attachment_anchor(self) -> Vector3:
        return np.array(self.foot_attachment_anchor, dtype=float)

    def get_center_anchor(self) -> Vector3:
        return np.array(self.center_anchor, dtype=float)

    def get_anchor_map(self) -> dict[str, Vector3]:
        return {
            "root": self.get_root_anchor(),
            "center": self.get_center_anchor(),
            "lower_leg": self.get_lower_leg_anchor(),
            "upper_attachment": self.get_upper_attachment_anchor(),
            "foot_attachment": self.get_foot_attachment_anchor(),
        }

    def get_ankle_angle(self) -> float:
        return float(self.current_angle)

    def foot_is_planted(self) -> bool:
        return bool(self.is_planted)

    def reset_joint(self) -> None:
        """
        Reset ankle state.
        """
        self.current_angle = 0.0
        self.is_planted = True

        self._update_visuals()
        self._update_state_visual()

    def debug_print(self) -> None:
        print("========== ANKLE DEBUG ==========")
        print("Name:", self.joint_name)
        print("Angle:", self.current_angle)
        print("Planted:", self.is_planted)
        print("Anchors:", self.get_anchor_map())
        print("=================================")

    def __repr__(self) -> str:
        return (
            "AnkleJoint("
            f"name={self.joint_name!r}, "
            f"angle={round(self.current_angle, 3)}"
            ")"
        )


def build_ankle_joint(
    *,
    position: Optional[Vec3Like] = None,
    config: Optional[AnkleJointConfig] = None,
    debug_enabled: Optional[bool] = None,
) -> AnkleJoint:
    """
    Create ankle joint connector.
    """
    if debug_enabled is None:
        debug_enabled = DEBUG_MODE

    if LOG_CREATURE_BUILD:
        logger.info("Building ankle joint")

    joint = AnkleJoint(
        config=config,
        name=creature_part_name("ankle_joint"),
        position=position,
        debug_enabled=debug_enabled,
    )

    if LOG_CREATURE_BUILD:
        logger.info("Ankle joint created successfully")

    return joint


def build_debug_ankle_joint(
    *,
    position: Optional[Vec3Like] = None,
    config: Optional[AnkleJointConfig] = None,
) -> AnkleJoint:
    """
    Create debug-enabled ankle joint.
    """
    return build_ankle_joint(
        position=position,
        config=config,
        debug_enabled=True,
    )


__all__ = [
    "Vector3",
    "Vec3Like",
    "AnkleJointConfig",
    "AnkleJoint",
    "build_ankle_joint",
    "build_debug_ankle_joint",
]