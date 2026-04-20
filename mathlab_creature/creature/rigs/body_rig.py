"""
Body rig for mathlab-mylinehub-creature.

This file assembles a structured, controllable rig for the full creature.

It combines:
- body (M)
- face rig
- arm rig
- leg rig
- hat

into a clean hierarchy that is easy to:
- access
- animate
- replace parts
- build poses on top of

This is the bridge between:

raw parts  →  animation system
"""

from __future__ import annotations

import numpy as np
from manimlib import VGroup

from mathlab_creature.creature.parts.body_m import build_body_m
from mathlab_creature.creature.parts.hat import build_hat

from mathlab_creature.creature.rigs.arm_rig import build_arm_rig_map
from mathlab_creature.creature.rigs.face_rig import build_face_rig_map
from mathlab_creature.creature.rigs.leg_rig import build_leg_rig_map

from mathlab_creature.config.defaults import DEBUG_MODE
from mathlab_creature.config.defaults import LOG_CREATURE_BUILD

from mathlab_creature.core.geometry import point
from mathlab_creature.core.logger import get_logger

logger = get_logger(__name__)


# ============================================================
# Internal helpers
# ============================================================

_REQUIRED_RIG_KEYS = ("body", "hat", "face", "arms", "legs", "group")


def _coerce_body_center(body_center=None) -> np.ndarray:
    """
    Normalize body_center into a clean 3D point.

    Accepted:
    - None
    - numpy.ndarray with shape (3,)
    - tuple/list with 3 numeric values
    """
    if body_center is None:
        return point(0.0, 0.0, 0.0)

    if isinstance(body_center, np.ndarray):
        if body_center.shape != (3,):
            raise ValueError(f"body_center must have shape (3,), got {body_center.shape}")
        return body_center.astype(float)

    if isinstance(body_center, (tuple, list)):
        if len(body_center) != 3:
            raise ValueError(
                f"body_center must contain exactly 3 values, got {len(body_center)}"
            )
        return point(body_center[0], body_center[1], body_center[2])

    raise TypeError(
        "body_center must be None, a numpy.ndarray of shape (3,), "
        "or a 3-item tuple/list"
    )


def _validate_rig_dict(rig: dict) -> None:
    """
    Validate that the incoming rig dictionary has the expected shape.
    """
    if not isinstance(rig, dict):
        raise TypeError(f"rig must be a dict, got {type(rig).__name__}")

    missing = [key for key in _REQUIRED_RIG_KEYS if key not in rig]
    if missing:
        raise KeyError(f"rig is missing required keys: {missing}")


# ============================================================
# Main rig builder
# ============================================================

def build_body_rig(body_center=None) -> dict[str, object]:
    """
    Build the full structured body rig.

    Returns a dictionary containing:
    - all parts
    - grouped structure
    - sub-rigs (face, arms, legs)
    """
    body_center = _coerce_body_center(body_center)

    if LOG_CREATURE_BUILD:
        logger.info("Building full body rig | center=%s", body_center)

    # --------------------------------------------------------
    # Core body + hat
    # --------------------------------------------------------

    body = build_body_m(
        center=(body_center[0], body_center[1], body_center[2]),
    )

    hat = build_hat(body_center)

    # --------------------------------------------------------
    # Sub rigs
    # --------------------------------------------------------

    face_rig = build_face_rig_map(body_center)
    arm_rig = build_arm_rig_map(body_center)
    leg_rig = build_leg_rig_map(body_center)

    # --------------------------------------------------------
    # Assemble full visual group
    # --------------------------------------------------------

    full_group = VGroup(
        body,
        face_rig["group"],
        hat,
        arm_rig["group"],
        leg_rig["group"],
    )
    full_group.name = "creature_body_rig_group"

    rig = {
        # Core
        "body": body,
        "hat": hat,

        # Sub rigs
        "face": face_rig,
        "arms": arm_rig,
        "legs": leg_rig,

        # Shared metadata
        "body_center": body_center,

        # Master group
        "group": full_group,
    }

    if DEBUG_MODE:
        logger.debug(
            "Body rig metadata | body=%s hat=%s face_group=%s arm_group=%s leg_group=%s",
            getattr(body, "name", "body"),
            getattr(hat, "name", "hat"),
            getattr(face_rig["group"], "name", "face_group"),
            getattr(arm_rig["group"], "name", "arm_group"),
            getattr(leg_rig["group"], "name", "leg_group"),
        )

    if LOG_CREATURE_BUILD:
        logger.info("Body rig assembled successfully")

    return rig


# ============================================================
# Access helpers
# ============================================================

def get_body(rig: dict):
    """
    Return the core body object.
    """
    _validate_rig_dict(rig)
    return rig["body"]


def get_hat(rig: dict):
    """
    Return the hat object.
    """
    _validate_rig_dict(rig)
    return rig["hat"]


def get_face_group(rig: dict):
    """
    Return the grouped face object.
    """
    _validate_rig_dict(rig)
    return rig["face"]["group"]


def get_arm_group(rig: dict):
    """
    Return the grouped arm rig object.
    """
    _validate_rig_dict(rig)
    return rig["arms"]["group"]


def get_leg_group(rig: dict):
    """
    Return the grouped leg rig object.
    """
    _validate_rig_dict(rig)
    return rig["legs"]["group"]


def get_full_group(rig: dict):
    """
    Return the full master rig group.
    """
    _validate_rig_dict(rig)
    return rig["group"]


def get_body_center(rig: dict):
    """
    Return the shared body center used to build the rig.
    """
    _validate_rig_dict(rig)
    return rig["body_center"]


# ============================================================
# Face access helpers
# ============================================================

def get_face_rig(rig: dict):
    """
    Return the full face rig map.
    """
    _validate_rig_dict(rig)
    return rig["face"]


def get_eyes(rig: dict):
    """
    Return the eyes object from the face rig.
    """
    _validate_rig_dict(rig)
    return rig["face"]["eyes"]


def get_nose(rig: dict):
    """
    Return the nose object from the face rig.
    """
    _validate_rig_dict(rig)
    return rig["face"]["nose"]


def get_mouth(rig: dict):
    """
    Return the mouth object from the face rig.
    """
    _validate_rig_dict(rig)
    return rig["face"]["mouth"]


# ============================================================
# Arm access helpers
# ============================================================

def get_arm_rig(rig: dict):
    """
    Return the full arm rig map.
    """
    _validate_rig_dict(rig)
    return rig["arms"]


def get_left_arm_system(rig: dict):
    """
    Return the left arm system.
    """
    _validate_rig_dict(rig)
    return rig["arms"]["left_system"]


def get_right_arm_system(rig: dict):
    """
    Return the right arm system.
    """
    _validate_rig_dict(rig)
    return rig["arms"]["right_system"]


def get_left_arm(rig: dict):
    """
    Return the left arm object.
    """
    _validate_rig_dict(rig)
    return rig["arms"]["left_arm"]


def get_right_arm(rig: dict):
    """
    Return the right arm object.
    """
    _validate_rig_dict(rig)
    return rig["arms"]["right_arm"]


def get_left_hand(rig: dict):
    """
    Return the left hand object.
    """
    _validate_rig_dict(rig)
    return rig["arms"]["left_hand"]


def get_right_hand(rig: dict):
    """
    Return the right hand object.
    """
    _validate_rig_dict(rig)
    return rig["arms"]["right_hand"]


# ============================================================
# Leg access helpers
# ============================================================

def get_leg_rig(rig: dict):
    """
    Return the full leg rig map.
    """
    _validate_rig_dict(rig)
    return rig["legs"]


def get_left_leg_system(rig: dict):
    """
    Return the left leg system.
    """
    _validate_rig_dict(rig)
    return rig["legs"]["left_system"]


def get_right_leg_system(rig: dict):
    """
    Return the right leg system.
    """
    _validate_rig_dict(rig)
    return rig["legs"]["right_system"]


def get_left_leg(rig: dict):
    """
    Return the left leg object.
    """
    _validate_rig_dict(rig)
    return rig["legs"]["left_leg"]


def get_right_leg(rig: dict):
    """
    Return the right leg object.
    """
    _validate_rig_dict(rig)
    return rig["legs"]["right_leg"]


def get_left_foot(rig: dict):
    """
    Return the left foot object.
    """
    _validate_rig_dict(rig)
    return rig["legs"]["left_foot"]


def get_right_foot(rig: dict):
    """
    Return the right foot object.
    """
    _validate_rig_dict(rig)
    return rig["legs"]["right_foot"]