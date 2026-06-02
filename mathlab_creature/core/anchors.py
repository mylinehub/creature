"""
Anchor helper utilities for mathlab-mylinehub-creature.

This file defines reusable anchor-point calculations for the creature.

Anchors are important named positions used for:
- root placement
- body core placement
- skeleton construction
- face attachment
- eye / nose / mouth placement
- arm attachment
- leg attachment
- hat placement
- debug visualization

Architecture rule:
- anchors are numeric positions only
- anchors do not create Manim objects
- anchors do not move body parts directly
- anchors do not contain audio logic
- audio remains separate and may later be triggered by actions

All anchors are returned as 3D numpy vectors.
"""

from __future__ import annotations

from typing import Iterable
from typing import Optional

import numpy as np

from mathlab_creature.config.sizes import ARM_SHOULDER_OFFSET_X
from mathlab_creature.config.sizes import ARM_SHOULDER_OFFSET_Y
from mathlab_creature.config.sizes import BODY_BOTTOM_Y
from mathlab_creature.config.sizes import BODY_FACE_ZONE_HEIGHT_RATIO
from mathlab_creature.config.sizes import BODY_FACE_ZONE_TOP_RATIO
from mathlab_creature.config.sizes import BODY_LEFT_X
from mathlab_creature.config.sizes import BODY_M_HEIGHT
from mathlab_creature.config.sizes import BODY_M_WIDTH
from mathlab_creature.config.sizes import BODY_RIGHT_X
from mathlab_creature.config.sizes import BODY_TOP_Y
from mathlab_creature.config.sizes import EYE_CENTER_TO_CENTER
from mathlab_creature.config.sizes import HAT_HEIGHT
from mathlab_creature.config.sizes import HAT_OFFSET_ABOVE_HEAD
from mathlab_creature.config.sizes import HEAD_ATTACHMENT_OFFSET_Y
from mathlab_creature.config.sizes import HIP_LEFT_X
from mathlab_creature.config.sizes import HIP_RIGHT_X
from mathlab_creature.config.sizes import HIP_Y
from mathlab_creature.config.sizes import JOINT_RADIUS
from mathlab_creature.config.sizes import LEG_HIP_OFFSET_X
from mathlab_creature.config.sizes import LEG_HIP_OFFSET_Y
from mathlab_creature.config.sizes import MOUTH_CENTER_Y
from mathlab_creature.config.sizes import NOSE_CENTER_Y
from mathlab_creature.config.sizes import PELVIS_LEFT_X
from mathlab_creature.config.sizes import PELVIS_RIGHT_X
from mathlab_creature.config.sizes import PELVIS_Y
from mathlab_creature.config.sizes import SHOULDER_LEFT_X
from mathlab_creature.config.sizes import SHOULDER_RIGHT_X
from mathlab_creature.config.sizes import SHOULDER_Y
from mathlab_creature.config.sizes import SPINE_LENGTH

from mathlab_creature.core.geometry import along_x
from mathlab_creature.core.geometry import along_y
from mathlab_creature.core.geometry import as_vec3
from mathlab_creature.core.geometry import local_to_world
from mathlab_creature.core.geometry import midpoint
from mathlab_creature.core.geometry import point
from mathlab_creature.core.geometry import zero_point


# ============================================================
# Type aliases
# ============================================================

Vec3Like = np.ndarray | Iterable[float]
AnchorMap = dict[str, np.ndarray]


# ============================================================
# Internal helpers
# ============================================================

def _coerce_center(
    center: Optional[Vec3Like] = None,
    name: str = "center",
) -> np.ndarray:
    """
    Normalize a center point into a clean 3D numpy point.

    Accepted:
    - None -> origin
    - numpy array with shape (3,)
    - list/tuple/iterable with 3 values
    """
    if center is None:
        return zero_point()

    return as_vec3(
        center,
        name=name,
    )


def _anchor_from_local(
    parent_center: Optional[Vec3Like],
    local_anchor: Vec3Like,
) -> np.ndarray:
    """
    Convert a local anchor into world space using a parent center.
    """
    parent = _coerce_center(
        parent_center,
        "parent_center",
    )

    local = as_vec3(
        local_anchor,
        "local_anchor",
    )

    return local_to_world(
        local,
        parent,
    )


def _get_face_zone_height() -> float:
    """
    Height of the face zone inside the body bounding area.
    """
    return BODY_M_HEIGHT * BODY_FACE_ZONE_HEIGHT_RATIO


def _get_face_zone_top_offset() -> float:
    """
    Vertical offset down from the body top to the top of the face zone.
    """
    return BODY_M_HEIGHT * BODY_FACE_ZONE_TOP_RATIO


# ============================================================
# Root / body core anchors
# ============================================================

def get_root_anchor(
    root_center: Optional[Vec3Like] = None,
) -> np.ndarray:
    """
    Root anchor of the full creature.

    This is the global point from which the creature is placed.
    """
    return _coerce_center(
        root_center,
        "root_center",
    )


def get_body_core_anchor(
    root_center: Optional[Vec3Like] = None,
) -> np.ndarray:
    """
    Body core anchor.

    This is the center-of-mass style control point.
    For now it is the same as root center.
    """
    return get_root_anchor(
        root_center,
    )


def get_body_center(
    body_center: Optional[Vec3Like] = None,
) -> np.ndarray:
    """
    Return the body center.

    If no center is provided, use origin.
    """
    return _coerce_center(
        body_center,
        "body_center",
    )


# ============================================================
# Body frame anchors
# ============================================================

def get_body_top_center(
    body_center: Optional[Vec3Like] = None,
) -> np.ndarray:
    """
    Top center of the M body bounding zone.
    """
    center = get_body_center(body_center)

    return along_y(
        center,
        BODY_M_HEIGHT / 2.0,
    )


def get_body_bottom_center(
    body_center: Optional[Vec3Like] = None,
) -> np.ndarray:
    """
    Bottom center of the M body bounding zone.
    """
    center = get_body_center(body_center)

    return along_y(
        center,
        -BODY_M_HEIGHT / 2.0,
    )


def get_body_left_center(
    body_center: Optional[Vec3Like] = None,
) -> np.ndarray:
    """
    Left center of the M body bounding zone.
    """
    center = get_body_center(body_center)

    return along_x(
        center,
        -BODY_M_WIDTH / 2.0,
    )


def get_body_right_center(
    body_center: Optional[Vec3Like] = None,
) -> np.ndarray:
    """
    Right center of the M body bounding zone.
    """
    center = get_body_center(body_center)

    return along_x(
        center,
        BODY_M_WIDTH / 2.0,
    )


def get_body_top_left(
    body_center: Optional[Vec3Like] = None,
) -> np.ndarray:
    """
    Top-left corner of the body bounding zone.
    """
    top_center = get_body_top_center(body_center)

    return along_x(
        top_center,
        -BODY_M_WIDTH / 2.0,
    )


def get_body_top_right(
    body_center: Optional[Vec3Like] = None,
) -> np.ndarray:
    """
    Top-right corner of the body bounding zone.
    """
    top_center = get_body_top_center(body_center)

    return along_x(
        top_center,
        BODY_M_WIDTH / 2.0,
    )


def get_body_bottom_left(
    body_center: Optional[Vec3Like] = None,
) -> np.ndarray:
    """
    Bottom-left corner of the body bounding zone.
    """
    bottom_center = get_body_bottom_center(body_center)

    return along_x(
        bottom_center,
        -BODY_M_WIDTH / 2.0,
    )


def get_body_bottom_right(
    body_center: Optional[Vec3Like] = None,
) -> np.ndarray:
    """
    Bottom-right corner of the body bounding zone.
    """
    bottom_center = get_body_bottom_center(body_center)

    return along_x(
        bottom_center,
        BODY_M_WIDTH / 2.0,
    )


# ============================================================
# Skeleton anchors
# ============================================================

def get_spine_base_anchor(
    body_center: Optional[Vec3Like] = None,
) -> np.ndarray:
    """
    Spine base anchor.

    Currently starts at body core.
    """
    return get_body_core_anchor(
        body_center,
    )


def get_spine_top_anchor(
    body_center: Optional[Vec3Like] = None,
) -> np.ndarray:
    """
    Spine top anchor.
    """
    base = get_spine_base_anchor(body_center)

    return along_y(
        base,
        SPINE_LENGTH,
    )


def get_head_anchor(
    body_center: Optional[Vec3Like] = None,
) -> np.ndarray:
    """
    Head attachment anchor.

    Face parts must attach relative to this/head system,
    not float independently.
    """
    spine_top = get_spine_top_anchor(body_center)

    return along_y(
        spine_top,
        HEAD_ATTACHMENT_OFFSET_Y,
    )


def get_pelvis_center_anchor(
    body_center: Optional[Vec3Like] = None,
) -> np.ndarray:
    """
    Pelvis center anchor.

    Legs attach through pelvis / hip anchors.
    """
    center = get_body_center(body_center)

    return point(
        center[0],
        center[1] + PELVIS_Y,
        center[2],
    )


def get_left_pelvis_anchor(
    body_center: Optional[Vec3Like] = None,
) -> np.ndarray:
    """
    Left pelvis anchor.
    """
    center = get_body_center(body_center)

    return point(
        center[0] + PELVIS_LEFT_X,
        center[1] + PELVIS_Y,
        center[2],
    )


def get_right_pelvis_anchor(
    body_center: Optional[Vec3Like] = None,
) -> np.ndarray:
    """
    Right pelvis anchor.
    """
    center = get_body_center(body_center)

    return point(
        center[0] + PELVIS_RIGHT_X,
        center[1] + PELVIS_Y,
        center[2],
    )


def get_left_shoulder_anchor(
    body_center: Optional[Vec3Like] = None,
) -> np.ndarray:
    """
    Left shoulder attachment point.

    Arms must attach from shoulder.
    Hands must never move as independent world objects.
    """
    center = get_body_center(body_center)

    return point(
        center[0] + SHOULDER_LEFT_X,
        center[1] + SHOULDER_Y,
        center[2],
    )


def get_right_shoulder_anchor(
    body_center: Optional[Vec3Like] = None,
) -> np.ndarray:
    """
    Right shoulder attachment point.

    Arms must attach from shoulder.
    Hands must never move as independent world objects.
    """
    center = get_body_center(body_center)

    return point(
        center[0] + SHOULDER_RIGHT_X,
        center[1] + SHOULDER_Y,
        center[2],
    )


def get_left_hip_anchor(
    body_center: Optional[Vec3Like] = None,
) -> np.ndarray:
    """
    Left hip / upper leg attachment point.
    """
    center = get_body_center(body_center)

    return point(
        center[0] + HIP_LEFT_X,
        center[1] + HIP_Y,
        center[2],
    )


def get_right_hip_anchor(
    body_center: Optional[Vec3Like] = None,
) -> np.ndarray:
    """
    Right hip / upper leg attachment point.
    """
    center = get_body_center(body_center)

    return point(
        center[0] + HIP_RIGHT_X,
        center[1] + HIP_Y,
        center[2],
    )


# ============================================================
# Face zone anchors
# ============================================================

def get_face_zone_top(
    body_center: Optional[Vec3Like] = None,
) -> np.ndarray:
    """
    Top anchor of the face zone inside the body/head area.
    """
    body_top = get_body_top_center(body_center)

    return along_y(
        body_top,
        -_get_face_zone_top_offset(),
    )


def get_face_zone_bottom(
    body_center: Optional[Vec3Like] = None,
) -> np.ndarray:
    """
    Bottom anchor of the face zone.
    """
    face_top = get_face_zone_top(body_center)

    return along_y(
        face_top,
        -_get_face_zone_height(),
    )


def get_face_zone_center(
    body_center: Optional[Vec3Like] = None,
) -> np.ndarray:
    """
    Center anchor of the face zone.
    """
    face_top = get_face_zone_top(body_center)
    face_zone_height = _get_face_zone_height()

    return along_y(
        face_top,
        -face_zone_height / 2.0,
    )


def get_face_zone_left(
    body_center: Optional[Vec3Like] = None,
) -> np.ndarray:
    """
    Left-side center anchor of the face zone.
    """
    face_center = get_face_zone_center(body_center)

    return along_x(
        face_center,
        -BODY_M_WIDTH / 4.0,
    )


def get_face_zone_right(
    body_center: Optional[Vec3Like] = None,
) -> np.ndarray:
    """
    Right-side center anchor of the face zone.
    """
    face_center = get_face_zone_center(body_center)

    return along_x(
        face_center,
        BODY_M_WIDTH / 4.0,
    )


# ============================================================
# Eye anchors
# ============================================================

def get_left_eye_center(
    body_center: Optional[Vec3Like] = None,
) -> np.ndarray:
    """
    Left eye center in the face zone.

    Eye white stays attached to head.
    Pupil may move locally later.
    """
    face_center = get_face_zone_center(body_center)

    return along_x(
        face_center,
        -EYE_CENTER_TO_CENTER / 2.0,
    )


def get_right_eye_center(
    body_center: Optional[Vec3Like] = None,
) -> np.ndarray:
    """
    Right eye center in the face zone.

    Eye white stays attached to head.
    Pupil may move locally later.
    """
    face_center = get_face_zone_center(body_center)

    return along_x(
        face_center,
        EYE_CENTER_TO_CENTER / 2.0,
    )


def get_eye_midpoint(
    body_center: Optional[Vec3Like] = None,
) -> np.ndarray:
    """
    Midpoint between left and right eye centers.
    """
    left_eye = get_left_eye_center(body_center)
    right_eye = get_right_eye_center(body_center)

    return midpoint(
        left_eye,
        right_eye,
    )


# ============================================================
# Nose and mouth anchors
# ============================================================

def get_nose_center(
    body_center: Optional[Vec3Like] = None,
) -> np.ndarray:
    """
    Nose center.

    Nose remains face-local.
    """
    face_center = get_face_zone_center(body_center)

    return point(
        face_center[0],
        get_body_center(body_center)[1] + NOSE_CENTER_Y,
        face_center[2],
    )


def get_mouth_center(
    body_center: Optional[Vec3Like] = None,
) -> np.ndarray:
    """
    Mouth center.

    Mouth remains face-local.
    """
    face_center = get_face_zone_center(body_center)

    return point(
        face_center[0],
        get_body_center(body_center)[1] + MOUTH_CENTER_Y,
        face_center[2],
    )


# ============================================================
# Hat anchors
# ============================================================

def get_hat_base_center(
    body_center: Optional[Vec3Like] = None,
) -> np.ndarray:
    """
    Base center for placing the hat above the body/head area.
    """
    body_top = get_body_top_center(body_center)

    return along_y(
        body_top,
        HAT_OFFSET_ABOVE_HEAD,
    )


def get_hat_tip_center(
    body_center: Optional[Vec3Like] = None,
) -> np.ndarray:
    """
    Approximate top point of the hat.
    """
    hat_base = get_hat_base_center(body_center)

    return along_y(
        hat_base,
        HAT_HEIGHT,
    )


# ============================================================
# Local anchor helpers
# ============================================================

def get_local_body_anchor_map() -> AnchorMap:
    """
    Return body anchors in local creature/body space.
    """
    return get_body_anchor_map(
        zero_point(),
    )


def get_local_face_anchor_map() -> AnchorMap:
    """
    Return face anchors in local creature/body space.
    """
    return get_face_anchor_map(
        zero_point(),
    )


def get_local_skeleton_anchor_map() -> AnchorMap:
    """
    Return skeleton anchors in local creature/body space.
    """
    return get_skeleton_anchor_map(
        zero_point(),
    )


# ============================================================
# Grouped anchor sets
# ============================================================

def get_skeleton_anchor_map(
    body_center: Optional[Vec3Like] = None,
) -> AnchorMap:
    """
    Return major skeleton anchors together.

    These anchors define the connected creature structure.
    """
    return {
        "root": get_root_anchor(body_center),
        "body_core": get_body_core_anchor(body_center),
        "spine_base": get_spine_base_anchor(body_center),
        "spine_top": get_spine_top_anchor(body_center),
        "head": get_head_anchor(body_center),
        "pelvis_center": get_pelvis_center_anchor(body_center),
        "left_pelvis": get_left_pelvis_anchor(body_center),
        "right_pelvis": get_right_pelvis_anchor(body_center),
        "left_shoulder": get_left_shoulder_anchor(body_center),
        "right_shoulder": get_right_shoulder_anchor(body_center),
        "left_hip": get_left_hip_anchor(body_center),
        "right_hip": get_right_hip_anchor(body_center),
    }


def get_face_anchor_map(
    body_center: Optional[Vec3Like] = None,
) -> AnchorMap:
    """
    Return all major face anchors together.
    """
    return {
        "face_zone_top": get_face_zone_top(body_center),
        "face_zone_bottom": get_face_zone_bottom(body_center),
        "face_zone_center": get_face_zone_center(body_center),
        "face_zone_left": get_face_zone_left(body_center),
        "face_zone_right": get_face_zone_right(body_center),
        "left_eye": get_left_eye_center(body_center),
        "right_eye": get_right_eye_center(body_center),
        "eye_midpoint": get_eye_midpoint(body_center),
        "nose": get_nose_center(body_center),
        "mouth": get_mouth_center(body_center),
    }


def get_body_anchor_map(
    body_center: Optional[Vec3Like] = None,
) -> AnchorMap:
    """
    Return major body anchors together.
    """
    return {
        "center": get_body_center(body_center),
        "top_center": get_body_top_center(body_center),
        "bottom_center": get_body_bottom_center(body_center),
        "left_center": get_body_left_center(body_center),
        "right_center": get_body_right_center(body_center),
        "top_left": get_body_top_left(body_center),
        "top_right": get_body_top_right(body_center),
        "bottom_left": get_body_bottom_left(body_center),
        "bottom_right": get_body_bottom_right(body_center),
        "hat_base_center": get_hat_base_center(body_center),
        "hat_tip_center": get_hat_tip_center(body_center),
    }


def get_limb_anchor_map(
    body_center: Optional[Vec3Like] = None,
) -> AnchorMap:
    """
    Return limb attachment anchors together.
    """
    return {
        "left_shoulder": get_left_shoulder_anchor(body_center),
        "right_shoulder": get_right_shoulder_anchor(body_center),
        "left_hip": get_left_hip_anchor(body_center),
        "right_hip": get_right_hip_anchor(body_center),
    }


def get_full_anchor_map(
    body_center: Optional[Vec3Like] = None,
) -> AnchorMap:
    """
    Return a merged map of major creature anchors.

    Useful for:
    - debug visualization
    - quick inspection
    - building simple guide overlays
    """
    anchors: AnchorMap = {}

    anchors.update(
        get_body_anchor_map(body_center)
    )
    anchors.update(
        get_skeleton_anchor_map(body_center)
    )
    anchors.update(
        get_face_anchor_map(body_center)
    )
    anchors.update(
        get_limb_anchor_map(body_center)
    )

    return anchors


# ============================================================
# Export control
# ============================================================

__all__ = [
    "Vec3Like",
    "AnchorMap",
    "get_root_anchor",
    "get_body_core_anchor",
    "get_body_center",
    "get_body_top_center",
    "get_body_bottom_center",
    "get_body_left_center",
    "get_body_right_center",
    "get_body_top_left",
    "get_body_top_right",
    "get_body_bottom_left",
    "get_body_bottom_right",
    "get_spine_base_anchor",
    "get_spine_top_anchor",
    "get_head_anchor",
    "get_pelvis_center_anchor",
    "get_left_pelvis_anchor",
    "get_right_pelvis_anchor",
    "get_left_shoulder_anchor",
    "get_right_shoulder_anchor",
    "get_left_hip_anchor",
    "get_right_hip_anchor",
    "get_face_zone_top",
    "get_face_zone_bottom",
    "get_face_zone_center",
    "get_face_zone_left",
    "get_face_zone_right",
    "get_left_eye_center",
    "get_right_eye_center",
    "get_eye_midpoint",
    "get_nose_center",
    "get_mouth_center",
    "get_hat_base_center",
    "get_hat_tip_center",
    "get_local_body_anchor_map",
    "get_local_face_anchor_map",
    "get_local_skeleton_anchor_map",
    "get_skeleton_anchor_map",
    "get_face_anchor_map",
    "get_body_anchor_map",
    "get_limb_anchor_map",
    "get_full_anchor_map",
]