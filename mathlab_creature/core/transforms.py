
"""
mathlab_creature/core/transforms.py

Production-grade transform + hierarchy utilities
for reusable creature rigging systems.

Core Responsibilities
---------------------
- local/world transforms
- root pivot system
- parent-child hierarchy
- center/root ownership
- visibility state
- teleport/move support
- rotation support
- scalable rig architecture

Design Goals
------------
- reusable across projects
- future 3D-ready
- hierarchy-safe
- animation-safe
- Manim-compatible
- controller-friendly
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np

from manimlib import VGroup
from manimlib.constants import ORIGIN, OUT


# =========================================================
# VECTOR HELPERS
# =========================================================

Vector3 = np.ndarray


def vec3(x: float = 0.0, y: float = 0.0, z: float = 0.0) -> Vector3:
    return np.array([x, y, z], dtype=float)


# =========================================================
# TRANSFORM STATE
# =========================================================

@dataclass
class TransformState:
    """
    Pure transform data container.

    Stores local transform state independent
    from rendering implementation.
    """

    position: Vector3 = field(default_factory=lambda: vec3())
    rotation: float = 0.0
    scale: Vector3 = field(default_factory=lambda: vec3(1.0, 1.0, 1.0))
    visible: bool = True

    def copy(self) -> "TransformState":
        return TransformState(
            position=np.array(self.position),
            rotation=float(self.rotation),
            scale=np.array(self.scale),
            visible=bool(self.visible),
        )


# =========================================================
# TRANSFORM NODE
# =========================================================

class TransformNode:
    """
    Hierarchical transform node.

    This is the FOUNDATION of the entire
    creature architecture.

    Every:
    - body part
    - rig
    - controller
    - root object

    should attach to a TransformNode.
    """

    def __init__(
        self,
        name: str,
        mobject=None,
        parent: Optional["TransformNode"] = None,
    ):
        self.name = name

        self.mobject = mobject

        self.parent: Optional["TransformNode"] = None
        self.children: List["TransformNode"] = []

        self.local = TransformState()
        self.world = TransformState()

        self.root_pivot = vec3()
        self.center_point = vec3()

        self.is_hidden = False

        if parent is not None:
            parent.add_child(self)

    # =====================================================
    # HIERARCHY
    # =====================================================

    def add_child(self, child: "TransformNode") -> None:
        """
        Attach child node.
        """

        if child.parent is not None:
            child.parent.remove_child(child)

        child.parent = self
        self.children.append(child)

    def remove_child(self, child: "TransformNode") -> None:
        """
        Remove child node.
        """

        if child in self.children:
            self.children.remove(child)
            child.parent = None

    # =====================================================
    # LOCAL TRANSFORMS
    # =====================================================

    def set_local_position(self, position: Vector3) -> None:
        self.local.position = np.array(position, dtype=float)

    def move_local(self, offset: Vector3) -> None:
        self.local.position += np.array(offset, dtype=float)

    def set_local_rotation(self, angle: float) -> None:
        self.local.rotation = angle

    def rotate_local(self, angle: float) -> None:
        self.local.rotation += angle

    def set_local_scale(self, scale: Vector3) -> None:
        self.local.scale = np.array(scale, dtype=float)

    # =====================================================
    # WORLD TRANSFORMS
    # =====================================================

    def get_world_position(self) -> Vector3:
        return np.array(self.world.position)

    def get_world_rotation(self) -> float:
        return float(self.world.rotation)

    def get_world_scale(self) -> Vector3:
        return np.array(self.world.scale)

    # =====================================================
    # ROOT / CENTER
    # =====================================================

    def set_root_pivot(self, point: Vector3) -> None:
        self.root_pivot = np.array(point, dtype=float)

    def set_center_point(self, point: Vector3) -> None:
        self.center_point = np.array(point, dtype=float)

    def get_center_point(self) -> Vector3:
        return np.array(self.center_point)

    # =====================================================
    # VISIBILITY
    # =====================================================

    def show(self) -> None:
        """
        Make node visible without destroying state.
        """

        self.is_hidden = False
        self.local.visible = True

        if self.mobject is not None:
            self.mobject.set_opacity(1.0)

    def hide(self) -> None:
        """
        Hide node while preserving hierarchy and transforms.
        """

        self.is_hidden = True
        self.local.visible = False

        if self.mobject is not None:
            self.mobject.set_opacity(0.0)

    def toggle_visibility(self) -> None:
        if self.is_hidden:
            self.show()
        else:
            self.hide()

    # =====================================================
    # TELEPORT / MOVE
    # =====================================================

    def teleport(self, position: Vector3) -> None:
        """
        Instantly move object without animation.
        """

        self.local.position = np.array(position, dtype=float)

    def move_to(self, position: Vector3) -> None:
        """
        Alias for teleport.
        Future-safe for animation systems.
        """

        self.teleport(position)

    # =====================================================
    # UPDATE SYSTEM
    # =====================================================

    def update_world_transform(self) -> None:
        """
        Compute world transform recursively.
        """

        if self.parent is None:
            self.world = self.local.copy()

        else:
            parent_world = self.parent.world

            self.world.position = (
                parent_world.position + self.local.position
            )

            self.world.rotation = (
                parent_world.rotation + self.local.rotation
            )

            self.world.scale = (
                parent_world.scale * self.local.scale
            )

            self.world.visible = (
                parent_world.visible and self.local.visible
            )

        self.apply_to_mobject()

        for child in self.children:
            child.update_world_transform()

    # =====================================================
    # MANIM SYNC
    # =====================================================

    def apply_to_mobject(self) -> None:
        """
        Push transform state into Manim VMobject.
        """

        if self.mobject is None:
            return

        self.mobject.move_to(self.world.position)

        self.mobject.rotate(
            self.world.rotation,
            axis=OUT,
            about_point=self.root_pivot,
        )

        self.mobject.set_opacity(
            1.0 if self.world.visible else 0.0
        )

    # =====================================================
    # DEBUG
    # =====================================================

    def print_tree(self, depth: int = 0) -> None:
        indent = "  " * depth

        print(
            f"{indent}- {self.name}"
            f" | children={len(self.children)}"
        )

        for child in self.children:
            child.print_tree(depth + 1)

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self) -> str:
        return (
            f"TransformNode("
            f"name='{self.name}', "
            f"children={len(self.children)}"
            f")"
        )


# =========================================================
# ROOT TRANSFORM GROUP
# =========================================================

class TransformGroup(VGroup):
    """
    Manim VGroup wrapper with transform node support.

    Allows:
    - visual hierarchy
    - transform hierarchy
    - future rigging systems
    """

    def __init__(self, *mobjects, name: str = "group", **kwargs):
        super().__init__(*mobjects, **kwargs)

        self.transform_node = TransformNode(
            name=name,
            mobject=self,
        )

    def get_transform_node(self) -> TransformNode:
        return self.transform_node


# =========================================================
# ROOT CREATURE TRANSFORM
# =========================================================

class RootTransformNode(TransformNode):
    """
    Master creature root node.

    EVERYTHING attaches here.

    This allows:
    - global movement
    - global rotation
    - visibility control
    - controller ownership
    - future multiplayer/network sync
    """

    def __init__(self, name: str = "creature_root"):
        super().__init__(name=name)

        self.velocity = vec3()
        self.facing_direction = vec3(1.0, 0.0, 0.0)

    def set_velocity(self, velocity: Vector3) -> None:
        self.velocity = np.array(velocity, dtype=float)

    def set_facing_direction(self, direction: Vector3) -> None:
        direction = np.array(direction, dtype=float)

        magnitude = np.linalg.norm(direction)

        if magnitude <= 1e-8:
            return

        self.facing_direction = direction / magnitude


# =========================================================
# FACTORY HELPERS
# =========================================================

def create_transform_node(
    name: str,
    mobject=None,
    parent: Optional[TransformNode] = None,
) -> TransformNode:
    return TransformNode(
        name=name,
        mobject=mobject,
        parent=parent,
    )


def create_root_transform(
    name: str = "creature_root",
) -> RootTransformNode:
    return RootTransformNode(name=name)
