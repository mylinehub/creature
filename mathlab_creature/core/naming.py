"""
Naming helpers for mathlab-mylinehub-creature.

This file keeps reusable naming logic in one place so that:
- object names stay consistent
- debug labels are predictable
- future grouping / logging becomes easier
- scene and creature parts follow one naming style

Current architecture:
- one connected creature
- one root
- one body core
- one skeleton
- internal parts only
- audio retained as separate subsystem

This file is intentionally simple.
"""

from __future__ import annotations

import re
from typing import Iterable


# ============================================================
# Internal helpers
# ============================================================

_MULTIPLE_UNDERSCORE_RE = re.compile(r"_+")
_NON_NAME_CHAR_RE = re.compile(r"[^a-z0-9_]")


def _ensure_string(
    value: object,
    name: str = "value",
) -> str:
    """
    Ensure the given value is a string.

    This fails early instead of silently producing strange names.
    """
    if not isinstance(value, str):
        raise TypeError(
            f"{name} must be a string, got {type(value).__name__}"
        )

    return value


def _collapse_underscores(value: str) -> str:
    """
    Replace repeated underscores with a single underscore.
    """
    return _MULTIPLE_UNDERSCORE_RE.sub(
        "_",
        value,
    )


def _strip_edge_underscores(value: str) -> str:
    """
    Remove leading and trailing underscores.
    """
    return value.strip("_")


# ============================================================
# Basic string helpers
# ============================================================

def clean_name(value: str) -> str:
    """
    Normalize a raw string into a clean internal name.

    Rules:
    - strip outer spaces
    - lowercase
    - replace spaces and dashes with underscores
    - remove unsupported characters
    - collapse repeated underscores
    - remove leading/trailing underscores

    Examples:
    - " Left Eye " -> "left_eye"
    - "test-body-scene" -> "test_body_scene"
    - "Debug: Anchor #1" -> "debug_anchor_1"
    """
    value = _ensure_string(
        value,
        "value",
    )

    cleaned = value.strip().lower()
    cleaned = cleaned.replace(" ", "_").replace("-", "_")
    cleaned = _NON_NAME_CHAR_RE.sub(
        "_",
        cleaned,
    )
    cleaned = _collapse_underscores(cleaned)
    cleaned = _strip_edge_underscores(cleaned)

    return cleaned


def default_if_empty(
    value: str,
    fallback: str,
) -> str:
    """
    Return cleaned value if it is non-empty, else fallback.
    """
    value = _ensure_string(
        value,
        "value",
    )
    fallback = _ensure_string(
        fallback,
        "fallback",
    )

    cleaned = clean_name(value)

    if cleaned:
        return cleaned

    return clean_name(fallback)


def join_name_parts(
    *parts: str | None,
) -> str:
    """
    Join multiple name parts into one underscore-separated name.

    Empty parts are ignored.
    Each part is normalized with clean_name().
    """
    cleaned_parts: list[str] = []

    for part in parts:
        if part is None:
            continue

        part = _ensure_string(
            part,
            "part",
        )

        normalized = clean_name(part)

        if normalized:
            cleaned_parts.append(normalized)

    return "_".join(cleaned_parts)


def join_name_iterable(
    parts: Iterable[str | None],
) -> str:
    """
    Join an iterable of optional name parts.

    Useful when a caller already has a list/tuple of components.
    """
    return join_name_parts(*parts)


def prefix_name(
    prefix: str,
    value: str,
) -> str:
    """
    Prefix a name with another name part.

    Example:
        prefix_name("debug", "eye_anchor") -> "debug_eye_anchor"
    """
    return join_name_parts(
        prefix,
        value,
    )


def suffix_name(
    value: str,
    suffix: str,
) -> str:
    """
    Suffix a name with another name part.

    Example:
        suffix_name("eye", "guide") -> "eye_guide"
    """
    return join_name_parts(
        value,
        suffix,
    )


def tag_name(
    base_name: str,
    *tags: str,
) -> str:
    """
    Build a name with optional extra tags.

    Example:
        tag_name("left_eye", "debug", "active")
        -> "left_eye_debug_active"
    """
    return join_name_parts(
        base_name,
        *tags,
    )


# ============================================================
# Root / hierarchy naming
# ============================================================

def root_name() -> str:
    """
    Return the standard creature root name.
    """
    return "creature_root"


def body_core_name() -> str:
    """
    Return the standard body core name.
    """
    return "body_core"


def skeleton_name() -> str:
    """
    Return the standard skeleton name.
    """
    return "skeleton"


def spine_name() -> str:
    """
    Return the standard spine name.
    """
    return "spine"


def head_name() -> str:
    """
    Return the standard head name.
    """
    return "head"


def pelvis_name() -> str:
    """
    Return the standard pelvis name.
    """
    return "pelvis"


def hierarchy_node_name(
    node_name: str,
) -> str:
    """
    Build a hierarchy node name.

    Example:
        hierarchy_node_name("left_shoulder")
        -> "node_left_shoulder"
    """
    return join_name_parts(
        "node",
        node_name,
    )


def joint_name(
    joint_value: str,
) -> str:
    """
    Build a standard joint name.

    Example:
        joint_name("left_knee") -> "joint_left_knee"
    """
    return join_name_parts(
        "joint",
        joint_value,
    )


# ============================================================
# Creature object naming
# ============================================================

def creature_part_name(
    part_name: str,
) -> str:
    """
    Build a standard creature part name.

    Example:
        creature_part_name("eye") -> "creature_eye"
    """
    return join_name_parts(
        "creature",
        part_name,
    )


def left_part_name(
    part_name: str,
) -> str:
    """
    Build a left-side part name.

    Example:
        left_part_name("eye") -> "left_eye"
    """
    return join_name_parts(
        "left",
        part_name,
    )


def right_part_name(
    part_name: str,
) -> str:
    """
    Build a right-side part name.

    Example:
        right_part_name("arm") -> "right_arm"
    """
    return join_name_parts(
        "right",
        part_name,
    )


def side_part_name(
    side: str,
    part_name: str,
) -> str:
    """
    Build a side part name.

    Example:
        side_part_name("left", "eye") -> "left_eye"
    """
    return join_name_parts(
        side,
        part_name,
    )


def creature_side_part_name(
    side: str,
    part_name: str,
) -> str:
    """
    Build a creature side part name.

    Example:
        creature_side_part_name("left", "eye")
        -> "creature_left_eye"
    """
    return join_name_parts(
        "creature",
        side,
        part_name,
    )


def pair_part_names(
    part_name: str,
) -> tuple[str, str]:
    """
    Return standard left/right part names together.

    Example:
        pair_part_names("eye") -> ("left_eye", "right_eye")
    """
    return (
        left_part_name(part_name),
        right_part_name(part_name),
    )


def creature_pair_part_names(
    part_name: str,
) -> tuple[str, str]:
    """
    Return standard creature-prefixed left/right part names together.

    Example:
        creature_pair_part_names("eye")
        -> ("creature_left_eye", "creature_right_eye")
    """
    return (
        creature_side_part_name(
            "left",
            part_name,
        ),
        creature_side_part_name(
            "right",
            part_name,
        ),
    )


def socket_name(
    base_name: str,
) -> str:
    """
    Build a socket name.

    Example:
        socket_name("left_eye") -> "left_eye_socket"
    """
    return suffix_name(
        base_name,
        "socket",
    )


def anchor_name(
    base_name: str,
) -> str:
    """
    Build a stable anchor name.

    Example:
        anchor_name("left_eye") -> "left_eye_anchor"
    """
    return suffix_name(
        base_name,
        "anchor",
    )


# ============================================================
# Scene naming
# ============================================================

def test_scene_name(
    base_name: str,
) -> str:
    """
    Build a standard test scene name.

    Example:
        test_scene_name("creature") -> "test_creature_scene"
    """
    return join_name_parts(
        "test",
        base_name,
        "scene",
    )


def validation_scene_name() -> str:
    """
    Return the primary validation scene name for the new architecture.
    """
    return "test_creature_scene"


def scene_group_name(
    group_name: str,
) -> str:
    """
    Build a standard scene-group label.

    Example:
        scene_group_name("tests") -> "scene_group_tests"
    """
    return join_name_parts(
        "scene_group",
        group_name,
    )


# ============================================================
# Debug / label naming
# ============================================================

def anchor_label_name(
    anchor_name_value: str,
) -> str:
    """
    Build a standard anchor label name.

    Example:
        anchor_label_name("left_eye") -> "anchor_left_eye"
    """
    return join_name_parts(
        "anchor",
        anchor_name_value,
    )


def guide_name(
    guide_name_value: str,
) -> str:
    """
    Build a standard guide object name.

    Example:
        guide_name("face_zone") -> "guide_face_zone"
    """
    return join_name_parts(
        "guide",
        guide_name_value,
    )


def debug_name(
    debug_value: str,
) -> str:
    """
    Build a standard debug object name.

    Example:
        debug_name("body_bounds") -> "debug_body_bounds"
    """
    return join_name_parts(
        "debug",
        debug_value,
    )


def label_name(
    label_value: str,
) -> str:
    """
    Build a standard generic label name.
    """
    return join_name_parts(
        "label",
        label_value,
    )


def bounds_name(
    bounds_value: str,
) -> str:
    """
    Build a standard bounds/helper name.
    """
    return join_name_parts(
        "bounds",
        bounds_value,
    )


# ============================================================
# Action / controller / audio naming
# ============================================================

def action_name(
    base_name: str,
) -> str:
    """
    Build a standard action name.

    Example:
        action_name("blink") -> "blink_action"
    """
    return join_name_parts(
        base_name,
        "action",
    )


def state_name(
    base_name: str,
) -> str:
    """
    Build a standard generic state name.

    Example:
        state_name("idle") -> "idle_state"
    """
    return join_name_parts(
        base_name,
        "state",
    )


def controller_name(
    base_name: str,
) -> str:
    """
    Build a standard controller name.

    Example:
        controller_name("movement") -> "movement_controller"
    """
    return join_name_parts(
        base_name,
        "controller",
    )


def audio_name(
    base_name: str,
) -> str:
    """
    Build a standard audio object name.

    Example:
        audio_name("walk") -> "walk_audio"
    """
    return join_name_parts(
        base_name,
        "audio",
    )


def sound_name(
    base_name: str,
) -> str:
    """
    Build a standard sound object name.

    Example:
        sound_name("step") -> "step_sound"
    """
    return join_name_parts(
        base_name,
        "sound",
    )


# ============================================================
# Render / output naming
# ============================================================

def render_output_name(
    scene_name: str,
    suffix: str | None = None,
) -> str:
    """
    Build a render output name.

    Examples:
    - render_output_name("test_creature_scene")
      -> "test_creature_scene"
    - render_output_name("test_creature_scene", "preview")
      -> "test_creature_scene_preview"
    """
    scene_name = clean_name(scene_name)

    if suffix is not None:
        suffix = clean_name(suffix)

        if suffix:
            return join_name_parts(
                scene_name,
                suffix,
            )

    return scene_name


def versioned_name(
    base_name: str,
    version: int | str,
) -> str:
    """
    Build a versioned name.

    Examples:
    - versioned_name("hat_shape", 2) -> "hat_shape_v2"
    - versioned_name("face_layout", "3") -> "face_layout_v3"
    """
    if isinstance(version, int):
        if version < 0:
            raise ValueError(
                f"version must be >= 0, got {version}"
            )

        version_part = f"v{version}"

    elif isinstance(version, str):
        version_clean = clean_name(version)

        if not version_clean:
            raise ValueError(
                "version string must not be empty"
            )

        if version_clean.startswith("v"):
            version_part = version_clean
        else:
            version_part = f"v{version_clean}"

    else:
        raise TypeError(
            f"version must be int or str, got {type(version).__name__}"
        )

    return join_name_parts(
        base_name,
        version_part,
    )


# ============================================================
# Collection / grouping naming
# ============================================================

def collection_name(
    base_name: str,
) -> str:
    """
    Build a standard collection/group name.
    """
    return join_name_parts(
        base_name,
        "collection",
    )


def group_name(
    base_name: str,
) -> str:
    """
    Build a standard group name.
    """
    return join_name_parts(
        base_name,
        "group",
    )


def map_name(
    base_name: str,
) -> str:
    """
    Build a standard map/dictionary-style name.
    """
    return join_name_parts(
        base_name,
        "map",
    )


def registry_name(
    base_name: str,
) -> str:
    """
    Build a standard registry name.
    """
    return join_name_parts(
        base_name,
        "registry",
    )


# ============================================================
# Export control
# ============================================================

__all__ = [
    "clean_name",
    "default_if_empty",
    "join_name_parts",
    "join_name_iterable",
    "prefix_name",
    "suffix_name",
    "tag_name",
    "root_name",
    "body_core_name",
    "skeleton_name",
    "spine_name",
    "head_name",
    "pelvis_name",
    "hierarchy_node_name",
    "joint_name",
    "creature_part_name",
    "left_part_name",
    "right_part_name",
    "side_part_name",
    "creature_side_part_name",
    "pair_part_names",
    "creature_pair_part_names",
    "socket_name",
    "anchor_name",
    "test_scene_name",
    "validation_scene_name",
    "scene_group_name",
    "anchor_label_name",
    "guide_name",
    "debug_name",
    "label_name",
    "bounds_name",
    "action_name",
    "state_name",
    "controller_name",
    "audio_name",
    "sound_name",
    "render_output_name",
    "versioned_name",
    "collection_name",
    "group_name",
    "map_name",
    "registry_name",
]