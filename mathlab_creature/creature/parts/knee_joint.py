"""
Knee joint construction for mathlab-mylinehub-creature.

This file builds the knee connector for the connected creature system.

Architecture rule:
- knee joint is a connector part
- knee joint does not build legs
- knee joint does not build feet
- legs.py will place this joint between upper leg and lower leg
- leg_rig.py / kinematics.py will calculate knee angle later
- knee joint should not move independently in scene code
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
class KneeJointConfig:
    """
    Tunable knee joint configuration.
    """

    radius: float = JOINT_RADIUS

    fill_color: str = GREY_B
    outline_color: str = WHITE
    inner_color: str = BLUE_E
    debug_color: str = YELLOW

    stroke_width: float = 2.0

    angle_arc_radius: float = 0.28
    axis_length: float = 0.35

    show_debug_axes: bool = False
    show_angle_text: bool = False


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


def _validated_config(config: Optional[KneeJointConfig]) -> KneeJointConfig:
    config = config or KneeJointConfig()

    config.radius = _validate_positive(
        "config.radius",
        config.radius,
    )
    config.stroke_width = _validate_non_negative(
        "config.stroke_width",
        config.stroke_width,
    )
    config.angle_arc_radius = _validate_non_negative(
        "config.angle_arc_radius",
        config.angle_arc_radius,
    )
    config.axis_length = _validate_non_negative(
        "config.axis_length",
        config.axis_length,
    )

    return config


class KneeJoint(VGroup):
    """
    Local knee connector.

    Responsibilities:
    - visible knee pivot
    - local bend angle state
    - angle debug visualization
    - transform node ownership
    - anchor map for leg construction

    This class does not build legs.
    """

    def __init__(
        self,
        config: Optional[KneeJointConfig] = None,
        name: str = "knee_joint",
        position: Optional[Vec3Like] = None,
        debug_enabled: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.config = _validated_config(config)
        self.joint_name = str(name)

        self.current_angle = 0.0
        self.debug_enabled = bool(debug_enabled)

        self.transform_node = create_transform_node(
            name=self.joint_name,
            mobject=self,
        )
        self.transform_node.set_center_point(zero_point())
        self.transform_node.set_root_pivot(zero_point())

        self._register_anchors()
        self._build_joint()
        self._build_debug_elements()
        self._update_debug_visibility()

        if position is not None:
            self.move_to(_coerce_point3(position, "position"))

        self.name = self.joint_name
        self.is_creature_knee_joint = True

    def _register_anchors(self) -> None:
        """
        Register local knee anchors.

        All are local to knee center for now.
        legs.py decides where the knee sits in the chain.
        """
        self.pivot_anchor = zero_point()
        self.upper_leg_anchor = zero_point()
        self.lower_leg_anchor = zero_point()
        self.center_anchor = zero_point()

        self.transform_node.set_center_point(self.center_anchor)
        self.transform_node.set_root_pivot(self.pivot_anchor)

    def _build_joint(self) -> None:
        """
        Build visible joint geometry.
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
            color=self.config.inner_color,
        )

        self.add(
            self.outer_joint,
            self.inner_joint,
        )

    def _build_debug_elements(self) -> None:
        """
        Build debug visualization.
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

        self.angle_text = (
            Text(
                "0°",
                font_size=18,
            )
            .scale(0.35)
            .move_to(
                point(
                    0.0,
                    self.config.angle_arc_radius + 0.2,
                    0.0,
                )
            )
        )

        self.bend_line = Line(
            zero_point(),
            point(0.0, -0.45, 0.0),
            color=RED,
            stroke_width=DEBUG_STROKE_WIDTH,
        )

        self.pivot_dot = Dot(
            point=self.pivot_anchor,
            radius=0.025,
            color=GREEN,
        )

        self.debug_group.add(
            self.axes_debug,
            self.angle_arc,
            self.angle_text,
            self.bend_line,
            self.pivot_dot,
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

    def set_joint_angle(self, angle: float) -> None:
        """
        Set knee bend angle.

        This updates local state and debug visuals only.
        legs.py / leg_rig.py should control actual leg segment placement.
        """
        self.current_angle = _validate_numeric(
            "angle",
            angle,
        )

        self._update_angle_visualization()

    def rotate_joint(self, delta_angle: float) -> None:
        """
        Increment knee bend angle.
        """
        self.current_angle += _validate_numeric(
            "delta_angle",
            delta_angle,
        )

        self._update_angle_visualization()

    def _update_angle_visualization(self) -> None:
        """
        Update debug angle graphics.
        """
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
                    self.config.angle_arc_radius + 0.2,
                    0.0,
                )
            )
        )
        self.angle_text.become(new_text)

        direction = point(
            np.sin(self.current_angle),
            -np.cos(self.current_angle),
            0.0,
        )

        new_line = Line(
            zero_point(),
            direction * 0.45,
            color=RED,
            stroke_width=DEBUG_STROKE_WIDTH,
        )
        self.bend_line.become(new_line)

    def get_transform_node(self) -> TransformNode:
        return self.transform_node

    def get_pivot_position(self) -> Vector3:
        return np.array(self.pivot_anchor, dtype=float)

    def get_center_position(self) -> Vector3:
        return np.array(self.center_anchor, dtype=float)

    def get_upper_leg_anchor(self) -> Vector3:
        return np.array(self.upper_leg_anchor, dtype=float)

    def get_lower_leg_anchor(self) -> Vector3:
        return np.array(self.lower_leg_anchor, dtype=float)

    def get_anchor_map(self) -> dict[str, Vector3]:
        return {
            "pivot": self.get_pivot_position(),
            "center": self.get_center_position(),
            "upper_leg": self.get_upper_leg_anchor(),
            "lower_leg": self.get_lower_leg_anchor(),
        }

    def get_joint_angle(self) -> float:
        return float(self.current_angle)

    def reset_joint(self) -> None:
        """
        Reset knee state.
        """
        self.current_angle = 0.0
        self._update_angle_visualization()

    def debug_print(self) -> None:
        print("========== KNEE DEBUG ==========")
        print("Name:", self.joint_name)
        print("Angle:", self.current_angle)
        print("Debug Enabled:", self.debug_enabled)
        print("Anchors:", self.get_anchor_map())
        print("================================")

    def __repr__(self) -> str:
        return (
            "KneeJoint("
            f"name={self.joint_name!r}, "
            f"angle={round(self.current_angle, 3)}"
            ")"
        )


def build_knee_joint(
    *,
    position: Optional[Vec3Like] = None,
    config: Optional[KneeJointConfig] = None,
    debug_enabled: Optional[bool] = None,
) -> KneeJoint:
    """
    Create knee joint connector.
    """
    if debug_enabled is None:
        debug_enabled = DEBUG_MODE

    if LOG_CREATURE_BUILD:
        logger.info("Building knee joint")

    joint = KneeJoint(
        config=config,
        name=creature_part_name("knee_joint"),
        position=position,
        debug_enabled=debug_enabled,
    )

    if LOG_CREATURE_BUILD:
        logger.info("Knee joint created successfully")

    return joint


def build_debug_knee_joint(
    *,
    position: Optional[Vec3Like] = None,
    config: Optional[KneeJointConfig] = None,
) -> KneeJoint:
    """
    Create debug-enabled knee joint.
    """
    return build_knee_joint(
        position=position,
        config=config,
        debug_enabled=True,
    )


__all__ = [
    "Vector3",
    "Vec3Like",
    "KneeJointConfig",
    "KneeJoint",
    "build_knee_joint",
    "build_debug_knee_joint",
]