"""
Debug visualization utilities for mathlab-mylinehub-creature.

This module creates optional Manim debug overlays for creature development.

Core responsibilities:
- pivot visualization
- anchor visualization
- local axes drawing
- vector debugging
- hierarchy debugging
- center-point visualization
- transform inspection
- motion debugging
- joint target debugging

Architecture rule:
- debug_draw.py is for development only
- debug overlays are not part of final creature drawing
- debug overlays should be toggled from config/controller/scene code
- debug_draw.py does not control creature movement
- debug_draw.py does not contain audio logic
- audio remains separate and may later be triggered by actions
"""

from __future__ import annotations

from typing import Iterable
from typing import Optional

import numpy as np

from manimlib import Dot
from manimlib import Line
from manimlib import Text
from manimlib import VGroup

from manimlib.constants import BLUE
from manimlib.constants import GREEN
from manimlib.constants import RED
from manimlib.constants import WHITE
from manimlib.constants import YELLOW

from mathlab_creature.config.sizes import ANCHOR_DOT_RADIUS
from mathlab_creature.config.sizes import DEBUG_STROKE_WIDTH
from mathlab_creature.config.sizes import GUIDE_STROKE_WIDTH

from mathlab_creature.core.geometry import as_vec3
from mathlab_creature.core.geometry import normalize
from mathlab_creature.core.geometry import point
from mathlab_creature.core.geometry import zero_vector

from mathlab_creature.core.transforms import TransformNode


# ============================================================
# Type aliases
# ============================================================

Vector3 = np.ndarray
Vec3Like = np.ndarray | Iterable[float]


# ============================================================
# Debug constants
# ============================================================

DEFAULT_AXIS_LENGTH = 0.5
DEFAULT_DOT_RADIUS = ANCHOR_DOT_RADIUS
DEFAULT_FONT_SIZE = 18
DEFAULT_FONT_SCALE = 0.25


# ============================================================
# Internal helpers
# ============================================================

def _coerce_point(
    value: Vec3Like,
    name: str = "point",
) -> Vector3:
    """
    Normalize a point-like value into a 3D numpy vector.
    """
    return as_vec3(
        value,
        name=name,
    )


def _validate_non_negative(
    name: str,
    value: float | int,
) -> float:
    """
    Ensure a non-negative numeric value.
    """
    if not isinstance(value, (int, float)):
        raise TypeError(
            f"{name} must be numeric, got {type(value).__name__}"
        )

    value = float(value)

    if value < 0:
        raise ValueError(
            f"{name} must be >= 0, got {value}"
        )

    return value


def _make_label(
    text: str,
    font_size: int = DEFAULT_FONT_SIZE,
):
    """
    Create a small debug text label.
    """
    return Text(
        str(text),
        font_size=font_size,
    ).scale(DEFAULT_FONT_SCALE)


# ============================================================
# Basic debug primitives
# ============================================================

def create_pivot_dot(
    position: Vec3Like,
    color=RED,
    radius: float = DEFAULT_DOT_RADIUS,
) -> Dot:
    """
    Visualize a pivot point.
    """
    radius = _validate_non_negative(
        "radius",
        radius,
    )

    return Dot(
        point=_coerce_point(position, "position"),
        radius=radius,
        color=color,
    )


def create_anchor_dot(
    position: Vec3Like,
    label: Optional[str] = None,
    color=YELLOW,
    radius: float = DEFAULT_DOT_RADIUS,
) -> VGroup:
    """
    Visualize an anchor point.

    Used for:
    - eye anchors
    - nose anchor
    - mouth anchor
    - shoulder anchors
    - hip anchors
    - skeleton anchors
    """
    group = VGroup()

    position_vec = _coerce_point(
        position,
        "position",
    )

    dot = Dot(
        point=position_vec,
        radius=radius,
        color=color,
    )

    group.add(dot)

    if label:
        text = _make_label(label)
        text.next_to(
            dot,
            direction=point(
                1.0,
                1.0,
                0.0,
            ),
        )
        group.add(text)

    return group


def create_labeled_dot(
    position: Vec3Like,
    label: str,
    color=YELLOW,
    radius: float = DEFAULT_DOT_RADIUS,
) -> VGroup:
    """
    Create a dot with a label.
    """
    return create_anchor_dot(
        position=position,
        label=label,
        color=color,
        radius=radius,
    )


# ============================================================
# Center / pivot debug
# ============================================================

def create_center_debug(
    node: TransformNode,
    color=YELLOW,
) -> VGroup:
    """
    Visualize transform center point.
    """
    group = VGroup()

    center = node.get_center_point()

    dot = Dot(
        point=center,
        radius=DEFAULT_DOT_RADIUS,
        color=color,
    )

    label = _make_label(
        f"{node.name}_center"
    )
    label.next_to(
        dot,
        direction=point(
            1.0,
            1.0,
            0.0,
        ),
    )

    group.add(dot)
    group.add(label)

    return group


def create_root_pivot_debug(
    node: TransformNode,
    color=RED,
) -> VGroup:
    """
    Visualize root pivot.
    """
    group = VGroup()

    pivot = node.root_pivot

    dot = Dot(
        point=pivot,
        radius=DEFAULT_DOT_RADIUS,
        color=color,
    )

    label = _make_label(
        f"{node.name}_pivot"
    )
    label.next_to(
        dot,
        direction=point(
            1.0,
            -1.0,
            0.0,
        ),
    )

    group.add(dot)
    group.add(label)

    return group


# ============================================================
# Local axes debug
# ============================================================

def create_local_axes(
    origin: Vec3Like,
    axis_length: float = DEFAULT_AXIS_LENGTH,
) -> VGroup:
    """
    Draw local transform axes.

    X = RED
    Y = GREEN
    Z = BLUE
    """
    axis_length = _validate_non_negative(
        "axis_length",
        axis_length,
    )
    origin_vec = _coerce_point(
        origin,
        "origin",
    )

    group = VGroup()

    x_axis = Line(
        origin_vec,
        origin_vec + point(axis_length, 0.0, 0.0),
        color=RED,
        stroke_width=GUIDE_STROKE_WIDTH,
    )

    y_axis = Line(
        origin_vec,
        origin_vec + point(0.0, axis_length, 0.0),
        color=GREEN,
        stroke_width=GUIDE_STROKE_WIDTH,
    )

    z_axis = Line(
        origin_vec,
        origin_vec + point(0.0, 0.0, axis_length),
        color=BLUE,
        stroke_width=GUIDE_STROKE_WIDTH,
    )

    group.add(x_axis)
    group.add(y_axis)
    group.add(z_axis)

    return group


# ============================================================
# Vector debug
# ============================================================

def create_vector_debug(
    start: Vec3Like,
    vector: Vec3Like,
    color=WHITE,
    label: Optional[str] = None,
) -> VGroup:
    """
    Draw debug vector from start to start + vector.
    """
    group = VGroup()

    start_vec = _coerce_point(
        start,
        "start",
    )
    vector_vec = _coerce_point(
        vector,
        "vector",
    )
    end_vec = start_vec + vector_vec

    line = Line(
        start_vec,
        end_vec,
        color=color,
        stroke_width=DEBUG_STROKE_WIDTH,
    )

    group.add(line)

    if label is not None:
        text = _make_label(label)
        text.next_to(
            line,
            direction=point(
                1.0,
                1.0,
                0.0,
            ),
        )
        group.add(text)

    return group


# ============================================================
# Anchor map debug
# ============================================================

def create_anchor_map_debug(
    anchors: dict[str, Vec3Like],
    color=YELLOW,
) -> VGroup:
    """
    Create debug dots for every anchor in an anchor map.
    """
    group = VGroup()

    for name, position in anchors.items():
        anchor_debug = create_anchor_dot(
            position=position,
            label=name,
            color=color,
            radius=DEFAULT_DOT_RADIUS,
        )
        group.add(anchor_debug)

    return group


# ============================================================
# Hierarchy debug
# ============================================================

def create_hierarchy_lines(
    root_node: TransformNode,
    color=WHITE,
) -> VGroup:
    """
    Draw parent-child hierarchy connections.
    """
    group = VGroup()

    def recurse(node: TransformNode) -> None:
        parent_position = node.get_world_position()

        for child in node.children:
            child_position = child.get_world_position()

            line = Line(
                parent_position,
                child_position,
                color=color,
                stroke_width=GUIDE_STROKE_WIDTH,
            )

            group.add(line)

            recurse(child)

    recurse(root_node)

    return group


# ============================================================
# Node debug
# ============================================================

def create_node_debug(
    node: TransformNode,
    show_axes: bool = True,
    show_center: bool = True,
    show_pivot: bool = False,
    show_label: bool = True,
) -> VGroup:
    """
    Complete debug visualization for a single transform node.
    """
    group = VGroup()

    world_position = node.get_world_position()

    if show_center:
        center_dot = Dot(
            point=world_position,
            radius=DEFAULT_DOT_RADIUS,
            color=YELLOW,
        )
        group.add(center_dot)

    if show_axes:
        axes = create_local_axes(
            world_position,
        )
        group.add(axes)

    if show_pivot:
        pivot_debug = create_root_pivot_debug(
            node,
        )
        group.add(pivot_debug)

    if show_label:
        label = _make_label(
            node.name,
            font_size=20,
        )
        label.move_to(
            world_position
            + point(
                0.0,
                0.35,
                0.0,
            )
        )
        group.add(label)

    return group


# ============================================================
# Full hierarchy debug
# ============================================================

def create_full_hierarchy_debug(
    root_node: TransformNode,
    show_axes: bool = True,
    show_center: bool = True,
    show_pivot: bool = False,
    show_label: bool = True,
) -> VGroup:
    """
    Visualize complete hierarchy tree.
    """
    group = VGroup()

    root_node.update_world_transform()

    hierarchy_lines = create_hierarchy_lines(
        root_node,
    )

    group.add(hierarchy_lines)

    def recurse(node: TransformNode) -> None:
        node_debug = create_node_debug(
            node=node,
            show_axes=show_axes,
            show_center=show_center,
            show_pivot=show_pivot,
            show_label=show_label,
        )

        group.add(node_debug)

        for child in node.children:
            recurse(child)

    recurse(root_node)

    return group


# ============================================================
# Motion debug
# ============================================================

def create_velocity_debug(
    position: Vec3Like,
    velocity: Vec3Like,
) -> VGroup:
    """
    Visualize movement velocity.
    """
    return create_vector_debug(
        start=position,
        vector=velocity,
        color=BLUE,
        label="velocity",
    )


def create_facing_direction_debug(
    position: Vec3Like,
    facing_direction: Vec3Like,
    scale: float = 0.7,
) -> VGroup:
    """
    Visualize creature facing direction.
    """
    scale = _validate_non_negative(
        "scale",
        scale,
    )

    direction = normalize(
        _coerce_point(
            facing_direction,
            "facing_direction",
        )
    )

    if np.linalg.norm(direction) <= 1e-8:
        direction = zero_vector()

    return create_vector_debug(
        start=position,
        vector=direction * scale,
        color=GREEN,
        label="forward",
    )


# ============================================================
# Joint / target debug
# ============================================================

def create_foot_target_debug(
    target_position: Vec3Like,
    label: str = "foot_target",
) -> VGroup:
    """
    Visualize procedural foot target.
    """
    return create_labeled_dot(
        position=target_position,
        label=label,
        color=BLUE,
        radius=DEFAULT_DOT_RADIUS,
    )


def create_hand_target_debug(
    target_position: Vec3Like,
    label: str = "hand_target",
) -> VGroup:
    """
    Visualize procedural hand target.
    """
    return create_labeled_dot(
        position=target_position,
        label=label,
        color=GREEN,
        radius=DEFAULT_DOT_RADIUS,
    )


def create_joint_debug(
    joint_position: Vec3Like,
    label: str = "joint",
    color=YELLOW,
) -> VGroup:
    """
    Visualize a joint point.
    """
    return create_labeled_dot(
        position=joint_position,
        label=label,
        color=color,
        radius=DEFAULT_DOT_RADIUS,
    )


def create_joint_angle_debug(
    joint_position: Vec3Like,
    angle: float,
    label: str = "angle",
) -> VGroup:
    """
    Display joint angle text.
    """
    group = VGroup()

    joint_position_vec = _coerce_point(
        joint_position,
        "joint_position",
    )

    text = _make_label(
        f"{label}: {round(float(np.degrees(angle)), 2)}°"
    )
    text.move_to(
        joint_position_vec
        + point(
            0.3,
            0.3,
            0.0,
        )
    )

    group.add(text)

    return group


def create_joint_solution_debug(
    root_position: Vec3Like,
    joint_position: Vec3Like,
    end_position: Vec3Like,
    label: str = "chain",
    color=WHITE,
) -> VGroup:
    """
    Visualize a solved two-bone chain.
    """
    group = VGroup()

    root_vec = _coerce_point(
        root_position,
        "root_position",
    )
    joint_vec = _coerce_point(
        joint_position,
        "joint_position",
    )
    end_vec = _coerce_point(
        end_position,
        "end_position",
    )

    upper_line = Line(
        root_vec,
        joint_vec,
        color=color,
        stroke_width=DEBUG_STROKE_WIDTH,
    )

    lower_line = Line(
        joint_vec,
        end_vec,
        color=color,
        stroke_width=DEBUG_STROKE_WIDTH,
    )

    group.add(upper_line)
    group.add(lower_line)
    group.add(
        create_joint_debug(
            root_vec,
            f"{label}_root",
            color=RED,
        )
    )
    group.add(
        create_joint_debug(
            joint_vec,
            f"{label}_joint",
            color=YELLOW,
        )
    )
    group.add(
        create_joint_debug(
            end_vec,
            f"{label}_end",
            color=BLUE,
        )
    )

    return group


# ============================================================
# Debug registry
# ============================================================

class DebugOverlayRegistry:
    """
    Central registry for debug overlays.

    Allows:
    - toggle systems
    - grouped overlays
    - runtime visibility control
    """

    def __init__(self) -> None:
        self.overlays: dict[str, object] = {}

    def register(
        self,
        name: str,
        overlay,
    ) -> None:
        """
        Register an overlay by name.
        """
        self.overlays[str(name)] = overlay

    def get(
        self,
        name: str,
    ):
        """
        Get an overlay by name.
        """
        return self.overlays.get(
            str(name),
        )

    def remove(
        self,
        name: str,
    ) -> None:
        """
        Remove an overlay by name.
        """
        self.overlays.pop(
            str(name),
            None,
        )

    def clear(self) -> None:
        """
        Clear all overlays.
        """
        self.overlays.clear()

    def all(self) -> Iterable:
        """
        Return all registered overlays.
        """
        return self.overlays.values()

    def names(self) -> list[str]:
        """
        Return registered overlay names.
        """
        return list(
            self.overlays.keys()
        )


# ============================================================
# Export control
# ============================================================

__all__ = [
    "Vector3",
    "Vec3Like",
    "DEFAULT_AXIS_LENGTH",
    "DEFAULT_DOT_RADIUS",
    "DEFAULT_FONT_SIZE",
    "DEFAULT_FONT_SCALE",
    "create_pivot_dot",
    "create_anchor_dot",
    "create_labeled_dot",
    "create_center_debug",
    "create_root_pivot_debug",
    "create_local_axes",
    "create_vector_debug",
    "create_anchor_map_debug",
    "create_hierarchy_lines",
    "create_node_debug",
    "create_full_hierarchy_debug",
    "create_velocity_debug",
    "create_facing_direction_debug",
    "create_foot_target_debug",
    "create_hand_target_debug",
    "create_joint_debug",
    "create_joint_angle_debug",
    "create_joint_solution_debug",
    "DebugOverlayRegistry",
]