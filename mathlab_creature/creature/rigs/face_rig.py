"""
Face rig helpers for mathlab-mylinehub-creature.

This file provides lightweight face-rig utilities for:
- collecting face parts together
- building a face-only group
- replacing or updating face parts cleanly
- preparing for later expressions and blinking

Version 1 goals:
- keep the rig simple
- avoid heavy abstraction too early
- make later expression systems easier
- keep all face part access in one place

This file does not yet animate the face.
It organizes face parts and exposes simple rig helpers.
"""

from __future__ import annotations

from manimlib import VGroup

from mathlab_creature.config.defaults import DEBUG_MODE
from mathlab_creature.config.defaults import LOG_CREATURE_BUILD
from mathlab_creature.creature.parts.eyes import build_eyes
from mathlab_creature.creature.parts.mouth import build_mouth
from mathlab_creature.creature.parts.nose import build_nose
from mathlab_creature.core.logger import get_logger

logger = get_logger(__name__)


# ============================================================
# Internal helpers
# ============================================================

_FACE_EYES_INDEX = 0
_FACE_NOSE_INDEX = 1
_FACE_MOUTH_INDEX = 2
_FACE_MIN_PART_COUNT = 3


def _validate_face_group(face_group: VGroup, *, require_full: bool = True) -> None:
    """
    Validate that the incoming face group is usable.

    Args:
        face_group:
            VGroup expected to contain eyes, nose, and mouth.

        require_full:
            If True, require all three parts to exist.
    """
    if not isinstance(face_group, VGroup):
        raise TypeError(
            f"face_group must be a VGroup, got {type(face_group).__name__}"
        )

    if require_full and len(face_group) < _FACE_MIN_PART_COUNT:
        raise ValueError(
            f"face_group must contain at least {_FACE_MIN_PART_COUNT} parts, "
            f"got {len(face_group)}"
        )


def _build_face_parts(body_center=None) -> tuple[object, object, object]:
    """
    Build the three major face parts once and return them together.
    """
    eyes = build_eyes(body_center)
    nose = build_nose(body_center)
    mouth = build_mouth(body_center)
    return eyes, nose, mouth


def _build_face_group_from_parts(
    eyes,
    nose,
    mouth,
    *,
    body_center=None,
    assign_name: bool = True,
) -> VGroup:
    """
    Build a face group from already-created parts and attach metadata.
    """
    face_group = VGroup(eyes, nose, mouth)

    if assign_name:
        face_group.name = "creature_face"

    # Lightweight metadata for later face rigging
    face_group.eyes = eyes
    face_group.nose = nose
    face_group.mouth = mouth
    face_group.body_center = body_center
    face_group.face_part_order = ("eyes", "nose", "mouth")

    return face_group


def _refresh_face_group_metadata(face_group: VGroup, *, body_center=None) -> VGroup:
    """
    Refresh standard metadata after one or more face parts are replaced.
    """
    _validate_face_group(face_group, require_full=True)

    face_group.eyes = face_group[_FACE_EYES_INDEX]
    face_group.nose = face_group[_FACE_NOSE_INDEX]
    face_group.mouth = face_group[_FACE_MOUTH_INDEX]

    if body_center is not None:
        face_group.body_center = body_center

    return face_group


def _replace_face_part(
    face_group: VGroup,
    index: int,
    new_part,
    *,
    body_center=None,
    log_label: str = "face part",
) -> VGroup:
    """
    Replace one part inside the face group and refresh metadata.
    """
    _validate_face_group(face_group, require_full=True)

    face_group.submobjects[index] = new_part
    _refresh_face_group_metadata(face_group, body_center=body_center)

    if LOG_CREATURE_BUILD:
        logger.info("%s rebuilt successfully", log_label)

    return face_group


# ============================================================
# Face build helpers
# ============================================================

def build_face_group(body_center=None) -> VGroup:
    """
    Build the complete face group.

    Returns:
        VGroup(eyes, nose, mouth)
    """
    if LOG_CREATURE_BUILD:
        logger.info("Building face group")

    eyes, nose, mouth = _build_face_parts(body_center)

    face_group = _build_face_group_from_parts(
        eyes,
        nose,
        mouth,
        body_center=body_center,
    )

    if DEBUG_MODE:
        logger.debug(
            "Face group built | eyes=%s nose=%s mouth=%s",
            getattr(eyes, "name", "eyes"),
            getattr(nose, "name", "nose"),
            getattr(mouth, "name", "mouth"),
        )

    if LOG_CREATURE_BUILD:
        logger.info("Face group created successfully")

    return face_group


# ============================================================
# Face rig map
# ============================================================

def build_face_rig_map(body_center=None) -> dict[str, object]:
    """
    Build a simple face rig map.

    Returns a dictionary containing direct references to major
    face components so later systems can access them cleanly.
    """
    if LOG_CREATURE_BUILD:
        logger.info("Building face rig map")

    eyes, nose, mouth = _build_face_parts(body_center)
    group = _build_face_group_from_parts(
        eyes,
        nose,
        mouth,
        body_center=body_center,
    )

    rig_map = {
        "eyes": eyes,
        "nose": nose,
        "mouth": mouth,
        "group": group,
        "body_center": body_center,
    }

    if LOG_CREATURE_BUILD:
        logger.info("Face rig map created successfully")

    return rig_map


# ============================================================
# Face update helpers
# ============================================================

def rebuild_mouth(face_group: VGroup, body_center=None) -> VGroup:
    """
    Replace the mouth inside an existing face group.

    Expected structure:
        face_group[0] -> eyes
        face_group[1] -> nose
        face_group[2] -> mouth
    """
    if LOG_CREATURE_BUILD:
        logger.info("Rebuilding mouth inside face group")

    _validate_face_group(face_group, require_full=True)
    new_mouth = build_mouth(body_center)

    return _replace_face_part(
        face_group,
        _FACE_MOUTH_INDEX,
        new_mouth,
        body_center=body_center,
        log_label="Mouth",
    )


def rebuild_eyes(face_group: VGroup, body_center=None) -> VGroup:
    """
    Replace the eyes inside an existing face group.

    Expected structure:
        face_group[0] -> eyes
        face_group[1] -> nose
        face_group[2] -> mouth
    """
    if LOG_CREATURE_BUILD:
        logger.info("Rebuilding eyes inside face group")

    _validate_face_group(face_group, require_full=True)
    new_eyes = build_eyes(body_center)

    return _replace_face_part(
        face_group,
        _FACE_EYES_INDEX,
        new_eyes,
        body_center=body_center,
        log_label="Eyes",
    )


def rebuild_nose(face_group: VGroup, body_center=None) -> VGroup:
    """
    Replace the nose inside an existing face group.

    Expected structure:
        face_group[0] -> eyes
        face_group[1] -> nose
        face_group[2] -> mouth
    """
    if LOG_CREATURE_BUILD:
        logger.info("Rebuilding nose inside face group")

    _validate_face_group(face_group, require_full=True)
    new_nose = build_nose(body_center)

    return _replace_face_part(
        face_group,
        _FACE_NOSE_INDEX,
        new_nose,
        body_center=body_center,
        log_label="Nose",
    )


def rebuild_face(face_group: VGroup, body_center=None) -> VGroup:
    """
    Rebuild all major face parts inside an existing face group while
    preserving the original group container.
    """
    if LOG_CREATURE_BUILD:
        logger.info("Rebuilding full face group")

    _validate_face_group(face_group, require_full=True)

    new_eyes, new_nose, new_mouth = _build_face_parts(body_center)

    face_group.submobjects[_FACE_EYES_INDEX] = new_eyes
    face_group.submobjects[_FACE_NOSE_INDEX] = new_nose
    face_group.submobjects[_FACE_MOUTH_INDEX] = new_mouth

    _refresh_face_group_metadata(face_group, body_center=body_center)

    if LOG_CREATURE_BUILD:
        logger.info("Full face group rebuilt successfully")

    return face_group


# ============================================================
# Face access helpers
# ============================================================

def get_eyes(face_group: VGroup):
    """
    Return the eyes object from the face group.
    """
    _validate_face_group(face_group, require_full=True)
    return face_group[_FACE_EYES_INDEX]


def get_nose(face_group: VGroup):
    """
    Return the nose object from the face group.
    """
    _validate_face_group(face_group, require_full=True)
    return face_group[_FACE_NOSE_INDEX]


def get_mouth(face_group: VGroup):
    """
    Return the mouth object from the face group.
    """
    _validate_face_group(face_group, require_full=True)
    return face_group[_FACE_MOUTH_INDEX]


def get_face_parts(face_group: VGroup) -> tuple[object, object, object]:
    """
    Return eyes, nose, and mouth together.
    """
    _validate_face_group(face_group, require_full=True)
    return (
        face_group[_FACE_EYES_INDEX],
        face_group[_FACE_NOSE_INDEX],
        face_group[_FACE_MOUTH_INDEX],
    )