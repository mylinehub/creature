"""
Transform and hierarchy utilities for mathlab-mylinehub-creature.

This module provides the foundation for connected creature movement.

Core responsibilities:
- local transform state
- world transform state
- parent-child hierarchy
- root-owned movement
- visibility state
- Manim object synchronization
- transform-safe creature rigging

Architecture rule:
- CreatureRoot owns global movement.
- Body parts use local transforms.
- Children follow parents.
- Eyes, hands, legs, nose, and mouth should never move as disconnected world objects.
- Audio does not live here. Audio remains separate and can be triggered later by actions.

This file is used later by:
- skeleton.py
- body_core.py
- body_rig.py
- movement_controller.py
- rotation_controller.py
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Iterable
from typing import Optional

import numpy as np

try:
    from manimlib import VGroup
    from manimlib.constants import OUT
except Exception:  # pragma: no cover - allows non-render tests to import file
    VGroup = object
    OUT = np.array([0.0, 0.0, 1.0], dtype=float)

from mathlab_creature.core.geometry import as_vec3
from mathlab_creature.core.geometry import rotate_vector
from mathlab_creature.core.geometry import zero_vector


# ============================================================
# Type aliases
# ============================================================

Vector3 = np.ndarray
Vec3Like = np.ndarray | Iterable[float]


# ============================================================
# Vector helpers
# ============================================================

def vec3(
    x: float = 0.0,
    y: float = 0.0,
    z: float = 0.0,
) -> Vector3:
    """
    Create a 3D vector.
    """
    return np.array(
        [
            float(x),
            float(y),
            float(z),
        ],
        dtype=float,
    )


def _coerce_vec3(
    value: Vec3Like,
    name: str = "vector",
) -> Vector3:
    """
    Convert a vector-like value into a clean 3D numpy vector.
    """
    return as_vec3(
        value,
        name=name,
    )


def _coerce_scale(
    value: float | int | Vec3Like,
    name: str = "scale",
) -> Vector3:
    """
    Normalize scale input.

    Accepted:
    - scalar -> uniform scale
    - 3D vector -> per-axis scale
    """
    if isinstance(value, (int, float)):
        scalar = float(value)

        return vec3(
            scalar,
            scalar,
            scalar,
        )

    return _coerce_vec3(
        value,
        name=name,
    )


# ============================================================
# Transform state
# ============================================================

@dataclass
class TransformState:
    """
    Pure transform data container.

    Stores local or world transform state independent from rendering.
    """

    position: Vector3 = field(
        default_factory=zero_vector,
    )
    rotation: float = 0.0
    scale: Vector3 = field(
        default_factory=lambda: vec3(
            1.0,
            1.0,
            1.0,
        )
    )
    visible: bool = True

    def copy(self) -> "TransformState":
        """
        Return a safe copy of this transform state.
        """
        return TransformState(
            position=np.array(
                self.position,
                dtype=float,
            ),
            rotation=float(self.rotation),
            scale=np.array(
                self.scale,
                dtype=float,
            ),
            visible=bool(self.visible),
        )


# ============================================================
# Transform node
# ============================================================

class TransformNode:
    """
    Hierarchical transform node.

    This is the transform foundation of the creature architecture.

    Every connected object may attach to one TransformNode.

    Global movement belongs to the root node.
    Child nodes store local movement only.
    """

    def __init__(
        self,
        name: str,
        mobject=None,
        parent: Optional["TransformNode"] = None,
    ) -> None:
        if not isinstance(name, str):
            raise TypeError(
                f"name must be str, got {type(name).__name__}"
            )

        cleaned_name = name.strip()

        if not cleaned_name:
            raise ValueError(
                "name must not be empty"
            )

        self.name = cleaned_name
        self.mobject = mobject

        self.parent: Optional["TransformNode"] = None
        self.children: list["TransformNode"] = []

        self.local = TransformState()
        self.world = TransformState()

        self.root_pivot = zero_vector()
        self.center_point = zero_vector()

        self.is_hidden = False

        if parent is not None:
            parent.add_child(self)

    # ========================================================
    # Hierarchy
    # ========================================================

    def add_child(
        self,
        child: "TransformNode",
    ) -> None:
        """
        Attach child node to this node.
        """
        if not isinstance(child, TransformNode):
            raise TypeError(
                f"child must be TransformNode, got {type(child).__name__}"
            )

        if child is self:
            raise ValueError(
                "A TransformNode cannot be its own child."
            )

        if child.parent is self:
            return

        if child.parent is not None:
            child.parent.remove_child(child)

        child.parent = self
        self.children.append(child)

    def remove_child(
        self,
        child: "TransformNode",
    ) -> None:
        """
        Remove child node from this node.
        """
        if child in self.children:
            self.children.remove(child)
            child.parent = None

    def has_parent(self) -> bool:
        """
        Return True if this node has a parent.
        """
        return self.parent is not None

    def is_root(self) -> bool:
        """
        Return True if this node has no parent.
        """
        return self.parent is None

    def iter_children(self) -> list["TransformNode"]:
        """
        Return direct children as a list copy.
        """
        return list(self.children)

    def iter_descendants(self) -> list["TransformNode"]:
        """
        Return all descendants in depth-first order.
        """
        descendants: list["TransformNode"] = []

        for child in self.children:
            descendants.append(child)
            descendants.extend(child.iter_descendants())

        return descendants

    def find_child(
        self,
        name: str,
    ) -> Optional["TransformNode"]:
        """
        Find a direct child by name.
        """
        for child in self.children:
            if child.name == name:
                return child

        return None

    def find_descendant(
        self,
        name: str,
    ) -> Optional["TransformNode"]:
        """
        Find a descendant by name.
        """
        for child in self.children:
            if child.name == name:
                return child

            found = child.find_descendant(name)

            if found is not None:
                return found

        return None

    # ========================================================
    # Local transforms
    # ========================================================

    def set_local_position(
        self,
        position: Vec3Like,
    ) -> None:
        """
        Set local position relative to parent.
        """
        self.local.position = _coerce_vec3(
            position,
            "position",
        )

    def move_local(
        self,
        offset: Vec3Like,
    ) -> None:
        """
        Move local position relative to parent.
        """
        self.local.position = (
            self.local.position
            + _coerce_vec3(
                offset,
                "offset",
            )
        )

    def set_local_rotation(
        self,
        angle: float,
    ) -> None:
        """
        Set local rotation in radians.
        """
        self.local.rotation = float(angle)

    def rotate_local(
        self,
        angle: float,
    ) -> None:
        """
        Add local rotation in radians.
        """
        self.local.rotation += float(angle)

    def set_local_scale(
        self,
        scale: float | int | Vec3Like,
    ) -> None:
        """
        Set local scale.
        """
        self.local.scale = _coerce_scale(
            scale,
            "scale",
        )

    def set_visible(
        self,
        visible: bool,
    ) -> None:
        """
        Set local visibility.
        """
        self.local.visible = bool(visible)
        self.is_hidden = not bool(visible)

    # ========================================================
    # World transform access
    # ========================================================

    def get_world_position(self) -> Vector3:
        """
        Return world position copy.
        """
        return np.array(
            self.world.position,
            dtype=float,
        )

    def get_world_rotation(self) -> float:
        """
        Return world rotation.
        """
        return float(
            self.world.rotation,
        )

    def get_world_scale(self) -> Vector3:
        """
        Return world scale copy.
        """
        return np.array(
            self.world.scale,
            dtype=float,
        )

    def is_world_visible(self) -> bool:
        """
        Return final inherited visibility.
        """
        return bool(
            self.world.visible,
        )

    # ========================================================
    # Root / center
    # ========================================================

    def set_root_pivot(
        self,
        pivot: Vec3Like,
    ) -> None:
        """
        Set pivot point for rotation sync.
        """
        self.root_pivot = _coerce_vec3(
            pivot,
            "pivot",
        )

    def set_center_point(
        self,
        center: Vec3Like,
    ) -> None:
        """
        Set logical center point for this node.
        """
        self.center_point = _coerce_vec3(
            center,
            "center",
        )

    def get_center_point(self) -> Vector3:
        """
        Return center point copy.
        """
        return np.array(
            self.center_point,
            dtype=float,
        )

    # ========================================================
    # Visibility
    # ========================================================

    def show(self) -> None:
        """
        Make node visible without destroying state.
        """
        self.set_visible(True)

        if self.mobject is not None and hasattr(self.mobject, "set_opacity"):
            self.mobject.set_opacity(1.0)

    def hide(self) -> None:
        """
        Hide node while preserving hierarchy and transforms.
        """
        self.set_visible(False)

        if self.mobject is not None and hasattr(self.mobject, "set_opacity"):
            self.mobject.set_opacity(0.0)

    def toggle_visibility(self) -> None:
        """
        Toggle local visibility.
        """
        if self.is_hidden:
            self.show()
        else:
            self.hide()

    # ========================================================
    # Root-safe movement aliases
    # ========================================================

    def teleport(
        self,
        position: Vec3Like,
    ) -> None:
        """
        Instantly set local position.

        For root node this means global teleport.
        For child node this means local teleport relative to parent.
        """
        self.set_local_position(
            position,
        )

    def move_to(
        self,
        position: Vec3Like,
    ) -> None:
        """
        Alias for teleport.

        Kept for readability.
        """
        self.teleport(
            position,
        )

    # ========================================================
    # Transform calculation
    # ========================================================

    def update_world_transform(self) -> None:
        """
        Compute world transform recursively.
        """
        if self.parent is None:
            self.world = self.local.copy()
        else:
            parent_world = self.parent.world

            rotated_local_position = rotate_vector(
                self.local.position * parent_world.scale,
                parent_world.rotation,
            )

            self.world.position = (
                parent_world.position
                + rotated_local_position
            )

            self.world.rotation = (
                parent_world.rotation
                + self.local.rotation
            )

            self.world.scale = (
                parent_world.scale
                * self.local.scale
            )

            self.world.visible = (
                parent_world.visible
                and self.local.visible
            )

        self.apply_to_mobject()

        for child in self.children:
            child.update_world_transform()

    # ========================================================
    # Manim sync
    # ========================================================

    def apply_to_mobject(self) -> None:
        """
        Push transform state into Manim mobject.

        This is intentionally conservative:
        - move_to is applied
        - opacity is applied
        - rotation is applied relative to stored root pivot

        More advanced animation belongs in action/controller files.
        """
        if self.mobject is None:
            return

        if hasattr(self.mobject, "move_to"):
            self.mobject.move_to(
                self.world.position,
            )

        if hasattr(self.mobject, "set_opacity"):
            self.mobject.set_opacity(
                1.0 if self.world.visible else 0.0,
            )

        if hasattr(self.mobject, "rotate") and abs(self.world.rotation) > 1e-8:
            self.mobject.rotate(
                self.world.rotation,
                axis=OUT,
                about_point=self.root_pivot,
            )

    # ========================================================
    # Debug helpers
    # ========================================================

    def print_tree(
        self,
        depth: int = 0,
    ) -> None:
        """
        Print transform hierarchy.
        """
        indent = "  " * depth

        print(
            f"{indent}- {self.name}"
            f" | children={len(self.children)}"
            f" | world={self.world.position}"
        )

        for child in self.children:
            child.print_tree(
                depth + 1,
            )

    def to_dict(self) -> dict[str, object]:
        """
        Return a debug-friendly dictionary for this node.
        """
        return {
            "name": self.name,
            "parent": self.parent.name if self.parent else None,
            "children": [
                child.name
                for child in self.children
            ],
            "local_position": self.local.position.tolist(),
            "world_position": self.world.position.tolist(),
            "local_rotation": self.local.rotation,
            "world_rotation": self.world.rotation,
            "local_scale": self.local.scale.tolist(),
            "world_scale": self.world.scale.tolist(),
            "visible": self.world.visible,
        }

    # ========================================================
    # Representation
    # ========================================================

    def __repr__(self) -> str:
        return (
            "TransformNode("
            f"name={self.name!r}, "
            f"children={len(self.children)}"
            ")"
        )


# ============================================================
# Transform group
# ============================================================

class TransformGroup(VGroup):
    """
    Manim VGroup wrapper with transform node support.

    Allows:
    - visual grouping
    - transform-node ownership
    - hierarchy-safe root movement
    """

    def __init__(
        self,
        *mobjects,
        name: str = "group",
        **kwargs,
    ) -> None:
        super().__init__(
            *mobjects,
            **kwargs,
        )

        self.transform_node = TransformNode(
            name=name,
            mobject=self,
        )

    def get_transform_node(self) -> TransformNode:
        """
        Return attached transform node.
        """
        return self.transform_node


# ============================================================
# Root creature transform
# ============================================================

class RootTransformNode(TransformNode):
    """
    Master creature root node.

    Everything in the creature hierarchy eventually attaches here.

    This allows:
    - global movement
    - global rotation
    - global visibility
    - controller ownership
    - one connected creature organism
    """

    def __init__(
        self,
        name: str = "creature_root",
        mobject=None,
    ) -> None:
        super().__init__(
            name=name,
            mobject=mobject,
            parent=None,
        )

        self.velocity = zero_vector()
        self.facing_direction = vec3(
            1.0,
            0.0,
            0.0,
        )

    def set_velocity(
        self,
        velocity: Vec3Like,
    ) -> None:
        """
        Set root velocity.
        """
        self.velocity = _coerce_vec3(
            velocity,
            "velocity",
        )

    def get_velocity(self) -> Vector3:
        """
        Return velocity copy.
        """
        return np.array(
            self.velocity,
            dtype=float,
        )

    def set_facing_direction(
        self,
        facing_direction: Vec3Like,
    ) -> None:
        """
        Set normalized facing direction.

        Zero direction is ignored.
        """
        direction_vec = _coerce_vec3(
            facing_direction,
            "facing_direction",
        )

        magnitude = np.linalg.norm(
            direction_vec,
        )

        if magnitude <= 1e-8:
            return

        self.facing_direction = direction_vec / magnitude

    def get_facing_direction(self) -> Vector3:
        """
        Return facing direction copy.
        """
        return np.array(
            self.facing_direction,
            dtype=float,
        )

    def move_root(
        self,
        offset: Vec3Like,
    ) -> None:
        """
        Move root globally.
        """
        self.move_local(
            offset,
        )

    def move_root_to(
        self,
        position: Vec3Like,
    ) -> None:
        """
        Set root global position.
        """
        self.set_local_position(
            position,
        )

    def rotate_root(
        self,
        angle: float,
    ) -> None:
        """
        Rotate root globally.
        """
        self.rotate_local(
            angle,
        )


# ============================================================
# Factory helpers
# ============================================================

def create_transform_node(
    name: str,
    mobject=None,
    parent: Optional[TransformNode] = None,
) -> TransformNode:
    """
    Create a generic transform node.
    """
    return TransformNode(
        name=name,
        mobject=mobject,
        parent=parent,
    )


def create_root_transform(
    name: str = "creature_root",
    mobject=None,
) -> RootTransformNode:
    """
    Create the root transform for the creature.
    """
    return RootTransformNode(
        name=name,
        mobject=mobject,
    )


# ============================================================
# Export control
# ============================================================

__all__ = [
    "Vector3",
    "Vec3Like",
    "vec3",
    "TransformState",
    "TransformNode",
    "TransformGroup",
    "RootTransformNode",
    "create_transform_node",
    "create_root_transform",
]