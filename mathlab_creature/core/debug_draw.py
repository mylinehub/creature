"""
mathlab_creature/core/debug_draw.py

Production-grade debug visualization utilities
for creature rigging and movement systems.

Core Responsibilities
---------------------
- pivot visualization
- local axes drawing
- vector debugging
- hierarchy debugging
- center-point visualization
- transform inspection
- motion debugging

Design Goals
------------
- lightweight
- toggle-friendly
- hierarchy-safe
- animation-safe
- reusable
- future 3D-ready
"""

from __future__ import annotations

from typing import Iterable, Optional

import numpy as np

from manimlib import (
    VGroup,
    Dot,
    Line,
    Text,
)

from manimlib.constants import (
    RED,
    GREEN,
    BLUE,
    YELLOW,
    WHITE,
)

from mathlab_creature.core.transforms import (
    TransformNode,
    vec3,
)


# =========================================================
# DEBUG CONSTANTS
# =========================================================

DEFAULT_AXIS_LENGTH = 0.5
DEFAULT_DOT_RADIUS = 0.05
DEFAULT_FONT_SCALE = 0.25


# =========================================================
# VECTOR HELPERS
# =========================================================

Vector3 = np.ndarray


def normalize(vector: Vector3) -> Vector3:
    magnitude = np.linalg.norm(vector)

    if magnitude <= 1e-8:
        return vec3()

    return vector / magnitude


# =========================================================
# PIVOT DEBUG
# =========================================================

def create_pivot_dot(
    position: Vector3,
    color=RED,
    radius: float = DEFAULT_DOT_RADIUS,
) -> Dot:
    """
    Visualize a pivot point.
    """

    dot = Dot(
        point=position,
        radius=radius,
        color=color,
    )

    return dot


# =========================================================
# CENTER POINT DEBUG
# =========================================================

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

    label = (
        Text(
            f"{node.name}_center",
            font_size=18,
        )
        .scale(DEFAULT_FONT_SCALE)
        .next_to(dot, direction=np.array([1, 1, 0]))
    )

    group.add(dot)
    group.add(label)

    return group


# =========================================================
# ROOT PIVOT DEBUG
# =========================================================

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

    label = (
        Text(
            f"{node.name}_pivot",
            font_size=18,
        )
        .scale(DEFAULT_FONT_SCALE)
        .next_to(dot, direction=np.array([1, -1, 0]))
    )

    group.add(dot)
    group.add(label)

    return group


# =========================================================
# LOCAL AXES DEBUG
# =========================================================

def create_local_axes(
    origin: Vector3,
    axis_length: float = DEFAULT_AXIS_LENGTH,
) -> VGroup:
    """
    Draw local transform axes.

    X = RED
    Y = GREEN
    Z = BLUE
    """

    group = VGroup()

    x_axis = Line(
        origin,
        origin + vec3(axis_length, 0, 0),
        color=RED,
    )

    y_axis = Line(
        origin,
        origin + vec3(0, axis_length, 0),
        color=GREEN,
    )

    z_axis = Line(
        origin,
        origin + vec3(0, 0, axis_length),
        color=BLUE,
    )

    group.add(x_axis)
    group.add(y_axis)
    group.add(z_axis)

    return group


# =========================================================
# VECTOR DEBUG
# =========================================================

def create_vector_debug(
    start: Vector3,
    vector: Vector3,
    color=WHITE,
    label: Optional[str] = None,
) -> VGroup:
    """
    Draw debug vector.
    """

    group = VGroup()

    end = start + vector

    line = Line(
        start,
        end,
        color=color,
    )

    group.add(line)

    if label is not None:
        text = (
            Text(
                label,
                font_size=18,
            )
            .scale(DEFAULT_FONT_SCALE)
            .next_to(line, direction=np.array([1, 1, 0]))
        )

        group.add(text)

    return group


# =========================================================
# HIERARCHY DEBUG
# =========================================================

def create_hierarchy_lines(
    root_node: TransformNode,
    color=WHITE,
) -> VGroup:
    """
    Draw parent-child hierarchy connections.
    """

    group = VGroup()

    def recurse(node: TransformNode):
        parent_position = node.get_world_position()

        for child in node.children:
            child_position = child.get_world_position()

            line = Line(
                parent_position,
                child_position,
                color=color,
            )

            group.add(line)

            recurse(child)

    recurse(root_node)

    return group


# =========================================================
# NODE DEBUG
# =========================================================

def create_node_debug(
    node: TransformNode,
    show_axes: bool = True,
    show_center: bool = True,
    show_pivot: bool = True,
    show_label: bool = True,
) -> VGroup:
    """
    Complete debug visualization for a node.
    """

    group = VGroup()

    world_position = node.get_world_position()

    # -----------------------------------------------------
    # CENTER
    # -----------------------------------------------------

    if show_center:
        center_dot = Dot(
            point=world_position,
            radius=DEFAULT_DOT_RADIUS,
            color=YELLOW,
        )

        group.add(center_dot)

    # -----------------------------------------------------
    # AXES
    # -----------------------------------------------------

    if show_axes:
        axes = create_local_axes(world_position)

        group.add(axes)

    # -----------------------------------------------------
    # ROOT PIVOT
    # -----------------------------------------------------

    if show_pivot:
        pivot_debug = create_root_pivot_debug(node)

        group.add(pivot_debug)

    # -----------------------------------------------------
    # LABEL
    # -----------------------------------------------------

    if show_label:
        label = (
            Text(
                node.name,
                font_size=20,
            )
            .scale(DEFAULT_FONT_SCALE)
            .move_to(
                world_position
                + vec3(0.0, 0.35, 0.0)
            )
        )

        group.add(label)

    return group


# =========================================================
# FULL HIERARCHY DEBUG
# =========================================================

def create_full_hierarchy_debug(
    root_node: TransformNode,
) -> VGroup:
    """
    Visualize complete hierarchy tree.
    """

    group = VGroup()

    hierarchy_lines = create_hierarchy_lines(
        root_node
    )

    group.add(hierarchy_lines)

    def recurse(node: TransformNode):
        node_debug = create_node_debug(node)

        group.add(node_debug)

        for child in node.children:
            recurse(child)

    recurse(root_node)

    return group


# =========================================================
# VELOCITY DEBUG
# =========================================================

def create_velocity_debug(
    position: Vector3,
    velocity: Vector3,
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


# =========================================================
# FACING DIRECTION DEBUG
# =========================================================

def create_facing_direction_debug(
    position: Vector3,
    facing_direction: Vector3,
    scale: float = 0.7,
) -> VGroup:
    """
    Visualize creature facing direction.
    """

    direction = normalize(facing_direction)

    return create_vector_debug(
        start=position,
        vector=direction * scale,
        color=GREEN,
        label="forward",
    )


# =========================================================
# FOOT TARGET DEBUG
# =========================================================

def create_foot_target_debug(
    target_position: Vector3,
) -> VGroup:
    """
    Visualize procedural foot target.
    """

    group = VGroup()

    dot = Dot(
        point=target_position,
        radius=DEFAULT_DOT_RADIUS,
        color=BLUE,
    )

    label = (
        Text(
            "foot_target",
            font_size=18,
        )
        .scale(DEFAULT_FONT_SCALE)
        .next_to(dot, direction=np.array([1, 0, 0]))
    )

    group.add(dot)
    group.add(label)

    return group


# =========================================================
# JOINT ANGLE DEBUG
# =========================================================

def create_joint_angle_debug(
    joint_position: Vector3,
    angle: float,
    label: str = "angle",
) -> VGroup:
    """
    Display joint angle text.
    """

    group = VGroup()

    text = (
        Text(
            f"{label}: {round(np.degrees(angle), 2)}°",
            font_size=18,
        )
        .scale(DEFAULT_FONT_SCALE)
        .move_to(
            joint_position
            + vec3(0.3, 0.3, 0.0)
        )
    )

    group.add(text)

    return group


# =========================================================
# DEBUG REGISTRY
# =========================================================

class DebugOverlayRegistry:
    """
    Central registry for debug overlays.

    Allows:
    - toggle systems
    - grouped overlays
    - runtime visibility control
    """

    def __init__(self):
        self.overlays = {}

    def register(
        self,
        name: str,
        overlay,
    ):
        self.overlays[name] = overlay

    def get(self, name: str):
        return self.overlays.get(name)

    def remove(self, name: str):
        if name in self.overlays:
            del self.overlays[name]

    def clear(self):
        self.overlays.clear()

    def all(self) -> Iterable:
        return self.overlays.values()