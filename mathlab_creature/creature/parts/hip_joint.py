"""
Hip / pelvis joint construction for mathlab-mylinehub-creature.

This file builds the pelvis / hip connector for the connected creature system.

Architecture rule:
- hip joint is a connector part
- hip joint does not build legs
- hip joint provides left/right leg anchors
- legs.py will attach legs to these anchors
- body_m.py/body_core.py will attach hip/pelvis into the creature body
- hip joint should not move independently in scene code
- audio is not handled here; audio may be triggered later by walk/step actions

Connection chain:

    BodyCore / BodyM
        |
        HipJoint / Pelvis
        |
        +-- Left Leg
        |
        +-- Right Leg

So this file connects the body to legs.
Feet are connected later inside legs.py.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
from typing import Optional

import numpy as np

from manimlib import Circle
from manimlib import Dot
from manimlib import Line
from manimlib import RoundedRectangle
from manimlib import Text
from manimlib import VGroup

from manimlib.constants import BLUE_E
from manimlib.constants import GREEN
from manimlib.constants import GREY_B
from manimlib.constants import WHITE
from manimlib.constants import YELLOW

from mathlab_creature.config.defaults import DEBUG_MODE
from mathlab_creature.config.defaults import LOG_CREATURE_BUILD
from mathlab_creature.config.defaults import PELVIS_NAME
from mathlab_creature.config.sizes import DEBUG_STROKE_WIDTH
from mathlab_creature.config.sizes import JOINT_RADIUS
from mathlab_creature.config.sizes import PELVIS_WIDTH

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
class HipJointConfig:
    """
    Tunable pelvis / hip joint configuration.
    """

    pelvis_width: float = PELVIS_WIDTH
    pelvis_height: float = 0.28
    corner_radius: float = 0.12

    pelvis_color: str = BLUE_E

    joint_radius: float = JOINT_RADIUS
    joint_color: str = GREY_B

    leg_spacing: float = PELVIS_WIDTH / 2.0

    debug_axis_length: float = 0.45
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


def _validated_config(config: Optional[HipJointConfig]) -> HipJointConfig:
    config = config or HipJointConfig()

    config.pelvis_width = _validate_positive(
        "config.pelvis_width",
        config.pelvis_width,
    )
    config.pelvis_height = _validate_positive(
        "config.pelvis_height",
        config.pelvis_height,
    )
    config.corner_radius = _validate_non_negative(
        "config.corner_radius",
        config.corner_radius,
    )
    config.joint_radius = _validate_positive(
        "config.joint_radius",
        config.joint_radius,
    )
    config.leg_spacing = _validate_positive(
        "config.leg_spacing",
        config.leg_spacing,
    )
    config.debug_axis_length = _validate_non_negative(
        "config.debug_axis_length",
        config.debug_axis_length,
    )

    return config


class HipJoint(VGroup):
    """
    Pelvis / hip connector.

    Responsibilities:
    - pelvis visual body
    - body attachment anchor
    - left leg root anchor
    - right leg root anchor
    - center-of-mass reference
    - local debug overlays

    This class does not build legs.
    """

    def __init__(
        self,
        config: Optional[HipJointConfig] = None,
        name: str = "hip_joint",
        position: Optional[Vec3Like] = None,
        debug_enabled: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.config = _validated_config(config)
        self.joint_name = str(name)

        self.debug_enabled = bool(debug_enabled)

        self.transform_node = create_transform_node(
            name=self.joint_name,
            mobject=self,
        )

        self._build_pelvis()
        self._build_leg_roots()
        self._register_anchors()
        self._build_debug()
        self._update_debug_visibility()

        if position is not None:
            self.move_to(_coerce_point3(position, "position"))

        self.name = self.joint_name
        self.is_creature_hip_joint = True

    def _build_pelvis(self) -> None:
        """
        Build pelvis body shape.
        """
        self.pelvis = RoundedRectangle(
            width=self.config.pelvis_width,
            height=self.config.pelvis_height,
            corner_radius=self.config.corner_radius,
            stroke_width=0,
            fill_color=self.config.pelvis_color,
            fill_opacity=1.0,
        )

        self.add(self.pelvis)

    def _build_leg_roots(self) -> None:
        """
        Build left/right leg root visual joints.
        """
        spacing = self.config.leg_spacing

        self.left_root = Circle(
            radius=self.config.joint_radius,
            stroke_width=0,
            fill_color=self.config.joint_color,
            fill_opacity=1.0,
        )
        self.left_root.move_to(point(-spacing, 0.0, 0.0))

        self.right_root = Circle(
            radius=self.config.joint_radius,
            stroke_width=0,
            fill_color=self.config.joint_color,
            fill_opacity=1.0,
        )
        self.right_root.move_to(point(spacing, 0.0, 0.0))

        self.add(
            self.left_root,
            self.right_root,
        )

    def _register_anchors(self) -> None:
        """
        Register pelvis anchors in local hip-joint space.
        """
        spacing = self.config.leg_spacing

        self.root_anchor = zero_point()

        self.body_anchor = point(
            0.0,
            self.config.pelvis_height / 2.0,
            0.0,
        )

        self.left_leg_anchor = point(
            -spacing,
            0.0,
            0.0,
        )

        self.right_leg_anchor = point(
            spacing,
            0.0,
            0.0,
        )

        self.center_of_mass = zero_point()

        self.transform_node.set_center_point(self.center_of_mass)
        self.transform_node.set_root_pivot(self.root_anchor)

        self.pelvis_anchor = self.root_anchor
        self.left_hip_anchor = self.left_leg_anchor
        self.right_hip_anchor = self.right_leg_anchor

    def _build_debug(self) -> None:
        """
        Build debug overlays.
        """
        self.debug_group = VGroup()

        self.axes_debug = create_local_axes(
            origin=zero_point(),
            axis_length=self.config.debug_axis_length,
        )

        self.center_dot = Dot(
            point=self.center_of_mass,
            radius=0.035,
            color=YELLOW,
        )

        self.body_anchor_dot = Dot(
            point=self.body_anchor,
            radius=0.03,
            color=GREEN,
        )

        self.left_line = Line(
            self.root_anchor,
            self.left_leg_anchor,
            color=WHITE,
            stroke_width=DEBUG_STROKE_WIDTH,
        )

        self.right_line = Line(
            self.root_anchor,
            self.right_leg_anchor,
            color=WHITE,
            stroke_width=DEBUG_STROKE_WIDTH,
        )

        self.label = (
            Text(
                "hip_joint",
                font_size=18,
            )
            .scale(0.35)
            .move_to(
                point(
                    0.0,
                    self.config.pelvis_height + 0.25,
                    0.0,
                )
            )
        )

        self.debug_group.add(
            self.axes_debug,
            self.center_dot,
            self.body_anchor_dot,
            self.left_line,
            self.right_line,
            self.label,
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

    def get_transform_node(self) -> TransformNode:
        return self.transform_node

    def get_root_anchor(self) -> Vector3:
        return np.array(self.root_anchor, dtype=float)

    def get_body_anchor(self) -> Vector3:
        return np.array(self.body_anchor, dtype=float)

    def get_left_leg_anchor(self) -> Vector3:
        return np.array(self.left_leg_anchor, dtype=float)

    def get_right_leg_anchor(self) -> Vector3:
        return np.array(self.right_leg_anchor, dtype=float)

    def get_left_hip_anchor(self) -> Vector3:
        return self.get_left_leg_anchor()

    def get_right_hip_anchor(self) -> Vector3:
        return self.get_right_leg_anchor()

    def get_center_of_mass(self) -> Vector3:
        return np.array(self.center_of_mass, dtype=float)

    def get_anchor_map(self) -> dict[str, Vector3]:
        """
        Return all important local hip anchors.
        """
        return {
            "root": self.get_root_anchor(),
            "body": self.get_body_anchor(),
            "center_of_mass": self.get_center_of_mass(),
            "left_leg": self.get_left_leg_anchor(),
            "right_leg": self.get_right_leg_anchor(),
            "left_hip": self.get_left_hip_anchor(),
            "right_hip": self.get_right_hip_anchor(),
        }

    def shift_center_of_mass(
        self,
        offset: Vec3Like,
    ) -> None:
        """
        Shift local balance center.

        This updates metadata only.
        BodyCore / body_rig will decide how to animate it.
        """
        offset_vec = _coerce_point3(offset, "offset")

        self.center_of_mass = self.center_of_mass + offset_vec
        self.transform_node.set_center_point(self.center_of_mass)

    def reset_balance(self) -> None:
        """
        Reset center-of-mass shift.
        """
        self.center_of_mass = zero_point()
        self.transform_node.set_center_point(self.center_of_mass)

    def debug_print(self) -> None:
        print("========== HIP DEBUG ==========")
        print("Name:", self.joint_name)
        print("Center:", self.center_of_mass)
        print("Body Anchor:", self.body_anchor)
        print("Left Anchor:", self.left_leg_anchor)
        print("Right Anchor:", self.right_leg_anchor)
        print("================================")

    def __repr__(self) -> str:
        return (
            "HipJoint("
            f"name={self.joint_name!r}"
            ")"
        )


def build_hip_joint(
    *,
    position: Optional[Vec3Like] = None,
    config: Optional[HipJointConfig] = None,
    debug_enabled: Optional[bool] = None,
) -> HipJoint:
    """
    Create hip joint / pelvis connector.
    """
    if debug_enabled is None:
        debug_enabled = DEBUG_MODE

    if LOG_CREATURE_BUILD:
        logger.info("Building hip joint")

    joint = HipJoint(
        config=config,
        name=creature_part_name(PELVIS_NAME),
        position=position,
        debug_enabled=debug_enabled,
    )

    if LOG_CREATURE_BUILD:
        logger.info("Hip joint created successfully")

    return joint


def build_debug_hip_joint(
    *,
    position: Optional[Vec3Like] = None,
    config: Optional[HipJointConfig] = None,
) -> HipJoint:
    """
    Create debug-enabled hip joint.
    """
    return build_hip_joint(
        position=position,
        config=config,
        debug_enabled=True,
    )


__all__ = [
    "Vector3",
    "Vec3Like",
    "HipJointConfig",
    "HipJoint",
    "build_hip_joint",
    "build_debug_hip_joint",
]