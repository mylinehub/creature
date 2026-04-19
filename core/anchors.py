"""
Anchor helper utilities for mathlab-mylinehub-creature.

This file defines reusable anchor-point calculations for the creature.
Anchors are important named positions used for:

- placing eyes, nose, mouth, hat
- attaching arms and legs
- aligning props
- guiding animation and poses

These helpers are written against simple geometric assumptions first.
As the creature design evolves, these functions can be refined without
forcing large changes across scene and part files.
"""

from __future__ import annotations

import numpy as np

from config.sizes import ARM_SHOULDER_OFFSET_X
from config.sizes import ARM_SHOULDER_OFFSET_Y
from config.sizes import BODY_FACE_ZONE_HEIGHT_RATIO
from config.sizes import BODY_FACE_ZONE_TOP_RATIO
from config.sizes import BODY_M_HEIGHT
from config.sizes import BODY_M_WIDTH
from config.sizes import EYE_GAP
from config.sizes import HAT_HEIGHT
from config.sizes import HAT_OFFSET_ABOVE_HEAD
from config.sizes import LEG_HIP_OFFSET_X
from config.sizes import LEG_HIP_OFFSET_Y
from config.sizes import MOUTH_HEIGHT
from config.sizes import NOSE_HEIGHT

from core.geometry import along_x
from core.geometry import along_y
from core.geometry import midpoint
from core.geometry import point


# ============================================================
# Internal helpers
# ============================================================

def _coerce_body_center(body_center: np.ndarray | None = None) -> np.ndarray:
    """
    Normalize the provided body center into a clean 3D numpy point.

    Accepted:
    - None -> origin
    - numpy array with shape (3,)
    - list/tuple with 3 values

    This stays internal so public anchor helpers remain simple.
    """
    if body_center is None:
        return point(0.0, 0.0, 0.0)

    if isinstance(body_center, np.ndarray):
        if body_center.shape != (3,):
            raise ValueError(
                f"body_center must have shape (3,), got {body_center.shape}"
            )
        return body_center.astype(float)

    if isinstance(body_center, (list, tuple)):
        if len(body_center) != 3:
            raise ValueError(
                f"body_center sequence must contain exactly 3 values, got {len(body_center)}"
            )
        return point(body_center[0], body_center[1], body_center[2])

    raise TypeError(
        "body_center must be None, a numpy.ndarray of shape (3,), "
        "or a 3-item list/tuple"
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
# Base body frame anchors
# ============================================================

def get_body_center(body_center: np.ndarray | None = None) -> np.ndarray:
    """
    Return the body center.

    If no center is provided, use origin.
    """
    return _coerce_body_center(body_center)


def get_body_top_center(body_center: np.ndarray | None = None) -> np.ndarray:
    """
    Top center of the M body bounding zone.
    """
    center = get_body_center(body_center)
    return along_y(center, BODY_M_HEIGHT / 2.0)


def get_body_bottom_center(body_center: np.ndarray | None = None) -> np.ndarray:
    """
    Bottom center of the M body bounding zone.
    """
    center = get_body_center(body_center)
    return along_y(center, -BODY_M_HEIGHT / 2.0)


def get_body_left_center(body_center: np.ndarray | None = None) -> np.ndarray:
    """
    Left center of the M body bounding zone.
    """
    center = get_body_center(body_center)
    return along_x(center, -BODY_M_WIDTH / 2.0)


def get_body_right_center(body_center: np.ndarray | None = None) -> np.ndarray:
    """
    Right center of the M body bounding zone.
    """
    center = get_body_center(body_center)
    return along_x(center, BODY_M_WIDTH / 2.0)


def get_body_top_left(body_center: np.ndarray | None = None) -> np.ndarray:
    """
    Top-left corner of the body bounding zone.
    """
    top_center = get_body_top_center(body_center)
    return along_x(top_center, -BODY_M_WIDTH / 2.0)


def get_body_top_right(body_center: np.ndarray | None = None) -> np.ndarray:
    """
    Top-right corner of the body bounding zone.
    """
    top_center = get_body_top_center(body_center)
    return along_x(top_center, BODY_M_WIDTH / 2.0)


def get_body_bottom_left(body_center: np.ndarray | None = None) -> np.ndarray:
    """
    Bottom-left corner of the body bounding zone.
    """
    bottom_center = get_body_bottom_center(body_center)
    return along_x(bottom_center, -BODY_M_WIDTH / 2.0)


def get_body_bottom_right(body_center: np.ndarray | None = None) -> np.ndarray:
    """
    Bottom-right corner of the body bounding zone.
    """
    bottom_center = get_body_bottom_center(body_center)
    return along_x(bottom_center, BODY_M_WIDTH / 2.0)


# ============================================================
# Face zone anchors
# ============================================================

def get_face_zone_top(body_center: np.ndarray | None = None) -> np.ndarray:
    """
    Top anchor of the face zone inside the body.
    """
    body_top = get_body_top_center(body_center)
    return along_y(body_top, -_get_face_zone_top_offset())


def get_face_zone_bottom(body_center: np.ndarray | None = None) -> np.ndarray:
    """
    Bottom anchor of the face zone inside the body.
    """
    face_top = get_face_zone_top(body_center)
    return along_y(face_top, -_get_face_zone_height())


def get_face_zone_center(body_center: np.ndarray | None = None) -> np.ndarray:
    """
    Center anchor of the face zone.
    """
    face_top = get_face_zone_top(body_center)
    face_zone_height = _get_face_zone_height()
    return along_y(face_top, -face_zone_height / 2.0)


def get_face_zone_left(body_center: np.ndarray | None = None) -> np.ndarray:
    """
    Left-side center anchor of the face zone.
    """
    face_center = get_face_zone_center(body_center)
    return along_x(face_center, -BODY_M_WIDTH / 4.0)


def get_face_zone_right(body_center: np.ndarray | None = None) -> np.ndarray:
    """
    Right-side center anchor of the face zone.
    """
    face_center = get_face_zone_center(body_center)
    return along_x(face_center, BODY_M_WIDTH / 4.0)


# ============================================================
# Eye anchors
# ============================================================

def get_left_eye_center(body_center: np.ndarray | None = None) -> np.ndarray:
    """
    Left eye center in the face zone.
    """
    face_center = get_face_zone_center(body_center)
    return along_x(face_center, -EYE_GAP / 2.0)


def get_right_eye_center(body_center: np.ndarray | None = None) -> np.ndarray:
    """
    Right eye center in the face zone.
    """
    face_center = get_face_zone_center(body_center)
    return along_x(face_center, EYE_GAP / 2.0)


def get_eye_midpoint(body_center: np.ndarray | None = None) -> np.ndarray:
    """
    Midpoint between left and right eye centers.
    """
    left_eye = get_left_eye_center(body_center)
    right_eye = get_right_eye_center(body_center)
    return midpoint(left_eye, right_eye)


# ============================================================
# Nose and mouth anchors
# ============================================================

def get_nose_center(body_center: np.ndarray | None = None) -> np.ndarray:
    """
    Nose center, slightly below the eye midpoint.
    """
    eye_mid = get_eye_midpoint(body_center)
    return along_y(eye_mid, -(NOSE_HEIGHT * 1.4))


def get_mouth_center(body_center: np.ndarray | None = None) -> np.ndarray:
    """
    Mouth center, below the nose.
    """
    nose_center = get_nose_center(body_center)
    return along_y(nose_center, -(MOUTH_HEIGHT * 2.1))


# ============================================================
# Hat anchors
# ============================================================

def get_hat_base_center(body_center: np.ndarray | None = None) -> np.ndarray:
    """
    Base center for placing the hat above the body.
    """
    body_top = get_body_top_center(body_center)
    return along_y(body_top, HAT_OFFSET_ABOVE_HEAD)


def get_hat_tip_center(body_center: np.ndarray | None = None) -> np.ndarray:
    """
    Approximate top point of the hat.
    """
    hat_base = get_hat_base_center(body_center)
    return along_y(hat_base, HAT_HEIGHT)


# ============================================================
# Arm anchors
# ============================================================

def get_left_shoulder_anchor(body_center: np.ndarray | None = None) -> np.ndarray:
    """
    Left shoulder attachment point.
    """
    center = get_body_center(body_center)
    return point(
        center[0] - ARM_SHOULDER_OFFSET_X,
        center[1] + ARM_SHOULDER_OFFSET_Y,
        center[2],
    )


def get_right_shoulder_anchor(body_center: np.ndarray | None = None) -> np.ndarray:
    """
    Right shoulder attachment point.
    """
    center = get_body_center(body_center)
    return point(
        center[0] + ARM_SHOULDER_OFFSET_X,
        center[1] + ARM_SHOULDER_OFFSET_Y,
        center[2],
    )


# ============================================================
# Leg anchors
# ============================================================

def get_left_hip_anchor(body_center: np.ndarray | None = None) -> np.ndarray:
    """
    Left hip / upper leg attachment point.
    """
    center = get_body_center(body_center)
    return point(
        center[0] - LEG_HIP_OFFSET_X,
        center[1] - LEG_HIP_OFFSET_Y,
        center[2],
    )


def get_right_hip_anchor(body_center: np.ndarray | None = None) -> np.ndarray:
    """
    Right hip / upper leg attachment point.
    """
    center = get_body_center(body_center)
    return point(
        center[0] + LEG_HIP_OFFSET_X,
        center[1] - LEG_HIP_OFFSET_Y,
        center[2],
    )


# ============================================================
# Grouped anchor sets
# ============================================================

def get_face_anchor_map(body_center: np.ndarray | None = None) -> dict[str, np.ndarray]:
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


def get_body_anchor_map(body_center: np.ndarray | None = None) -> dict[str, np.ndarray]:
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
        "left_shoulder": get_left_shoulder_anchor(body_center),
        "right_shoulder": get_right_shoulder_anchor(body_center),
        "left_hip": get_left_hip_anchor(body_center),
        "right_hip": get_right_hip_anchor(body_center),
    }


def get_full_anchor_map(body_center: np.ndarray | None = None) -> dict[str, np.ndarray]:
    """
    Return a merged map of major creature anchors.

    Useful for:
    - debug visualization
    - quick inspection
    - building simple guide overlays
    """
    anchors: dict[str, np.ndarray] = {}
    anchors.update(get_body_anchor_map(body_center))
    anchors.update(get_face_anchor_map(body_center))
    return anchors