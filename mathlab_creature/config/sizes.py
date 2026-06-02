"""
Central size definitions for the mathlab-mylinehub-creature project.

This module keeps reusable dimensional values in one place so that:
- the creature stays proportionally consistent
- body parts can be tuned without editing many files
- scene files stay clean
- repeated layout math does not get hardcoded everywhere

Design rules:
- public values are uppercase constants
- values are plain numeric constants
- these are project defaults, not absolute restrictions
"""

from __future__ import annotations

from typing import Dict


# ============================================================
# Internal helpers
# ============================================================

def _validate_positive(name: str, value: float | int) -> float | int:
    """Require a strictly positive numeric value."""
    if not isinstance(value, (int, float)):
        raise TypeError(
            f"{name} must be numeric, got {type(value).__name__}"
        )

    if value <= 0:
        raise ValueError(
            f"{name} must be > 0, got {value!r}"
        )

    return value


def _validate_non_negative(name: str, value: float | int) -> float | int:
    """Require a non-negative numeric value."""
    if not isinstance(value, (int, float)):
        raise TypeError(
            f"{name} must be numeric, got {type(value).__name__}"
        )

    if value < 0:
        raise ValueError(
            f"{name} must be >= 0, got {value!r}"
        )

    return value


def _validate_ratio(name: str, value: float | int) -> float | int:
    """Require a ratio in the closed interval [0, 1]."""
    if not isinstance(value, (int, float)):
        raise TypeError(
            f"{name} must be numeric, got {type(value).__name__}"
        )

    if not (0 <= value <= 1):
        raise ValueError(
            f"{name} must be between 0 and 1, got {value!r}"
        )

    return value


# ============================================================
# Base creature scale
# ============================================================

CREATURE_BASE_HEIGHT = _validate_positive(
    "CREATURE_BASE_HEIGHT",
    4.8,
)

CREATURE_BASE_WIDTH = _validate_positive(
    "CREATURE_BASE_WIDTH",
    3.6,
)

CREATURE_SCALE = _validate_positive(
    "CREATURE_SCALE",
    1.0,
)


# ============================================================
# Body / torso sizing
# ============================================================

BODY_M_WIDTH = _validate_positive(
    "BODY_M_WIDTH",
    3.6,
)

BODY_M_HEIGHT = _validate_positive(
    "BODY_M_HEIGHT",
    4.2,
)

BODY_M_STROKE_WIDTH = _validate_positive(
    "BODY_M_STROKE_WIDTH",
    18,
)

BODY_M_CORNER_RADIUS = _validate_non_negative(
    "BODY_M_CORNER_RADIUS",
    0.12,
)

BODY_FACE_ZONE_TOP_RATIO = _validate_ratio(
    "BODY_FACE_ZONE_TOP_RATIO",
    0.24,
)

BODY_FACE_ZONE_HEIGHT_RATIO = _validate_ratio(
    "BODY_FACE_ZONE_HEIGHT_RATIO",
    0.22,
)


# ============================================================
# Body core / skeleton sizing
# ============================================================

BODY_CORE_RADIUS = _validate_positive(
    "BODY_CORE_RADIUS",
    0.12,
)

JOINT_RADIUS = _validate_positive(
    "JOINT_RADIUS",
    0.06,
)

SPINE_LENGTH = _validate_positive(
    "SPINE_LENGTH",
    1.60,
)

HEAD_ATTACHMENT_OFFSET_Y = _validate_positive(
    "HEAD_ATTACHMENT_OFFSET_Y",
    1.20,
)

PELVIS_WIDTH = _validate_positive(
    "PELVIS_WIDTH",
    1.25,
)

SHOULDER_WIDTH = _validate_positive(
    "SHOULDER_WIDTH",
    2.10,
)


# ============================================================
# Eye sizing
# ============================================================

EYE_RADIUS = _validate_positive(
    "EYE_RADIUS",
    0.22,
)

EYE_WIDTH = _validate_positive(
    "EYE_WIDTH",
    0.42,
)

EYE_HEIGHT = _validate_positive(
    "EYE_HEIGHT",
    0.52,
)

EYE_STROKE_WIDTH = _validate_positive(
    "EYE_STROKE_WIDTH",
    2,
)

PUPIL_RADIUS = _validate_positive(
    "PUPIL_RADIUS",
    0.08,
)

PUPIL_MAX_OFFSET = _validate_non_negative(
    "PUPIL_MAX_OFFSET",
    0.07,
)

EYE_GAP = _validate_non_negative(
    "EYE_GAP",
    0.42,
)


# ============================================================
# Nose sizing
# ============================================================

NOSE_WIDTH = _validate_positive(
    "NOSE_WIDTH",
    0.14,
)

NOSE_HEIGHT = _validate_positive(
    "NOSE_HEIGHT",
    0.20,
)

NOSE_STROKE_WIDTH = _validate_positive(
    "NOSE_STROKE_WIDTH",
    2,
)


# ============================================================
# Mouth sizing
# ============================================================

MOUTH_WIDTH = _validate_positive(
    "MOUTH_WIDTH",
    0.48,
)

MOUTH_HEIGHT = _validate_positive(
    "MOUTH_HEIGHT",
    0.18,
)

MOUTH_STROKE_WIDTH = _validate_positive(
    "MOUTH_STROKE_WIDTH",
    4,
)

SMILE_ARC_ANGLE = _validate_positive(
    "SMILE_ARC_ANGLE",
    1.8,
)

NEUTRAL_MOUTH_WIDTH = _validate_positive(
    "NEUTRAL_MOUTH_WIDTH",
    0.30,
)


# ============================================================
# Hat sizing
# ============================================================

HAT_WIDTH = _validate_positive(
    "HAT_WIDTH",
    1.25,
)

HAT_HEIGHT = _validate_positive(
    "HAT_HEIGHT",
    0.72,
)

HAT_BRIM_WIDTH = _validate_positive(
    "HAT_BRIM_WIDTH",
    1.05,
)

HAT_BRIM_HEIGHT = _validate_positive(
    "HAT_BRIM_HEIGHT",
    0.08,
)

HAT_OFFSET_ABOVE_HEAD = _validate_non_negative(
    "HAT_OFFSET_ABOVE_HEAD",
    0.12,
)


# ============================================================
# Arm sizing
# ============================================================

ARM_LENGTH = _validate_positive(
    "ARM_LENGTH",
    1.15,
)

UPPER_ARM_LENGTH_RATIO = _validate_ratio(
    "UPPER_ARM_LENGTH_RATIO",
    0.52,
)

FOREARM_LENGTH_RATIO = _validate_ratio(
    "FOREARM_LENGTH_RATIO",
    0.48,
)

ARM_STROKE_WIDTH = _validate_positive(
    "ARM_STROKE_WIDTH",
    10,
)

ARM_SHOULDER_OFFSET_X = _validate_positive(
    "ARM_SHOULDER_OFFSET_X",
    1.05,
)

ARM_SHOULDER_OFFSET_Y = _validate_non_negative(
    "ARM_SHOULDER_OFFSET_Y",
    0.10,
)

HAND_RADIUS = _validate_positive(
    "HAND_RADIUS",
    0.11,
)


# ============================================================
# Leg sizing
# ============================================================

LEG_LENGTH = _validate_positive(
    "LEG_LENGTH",
    1.15,
)

UPPER_LEG_LENGTH_RATIO = _validate_ratio(
    "UPPER_LEG_LENGTH_RATIO",
    0.52,
)

LOWER_LEG_LENGTH_RATIO = _validate_ratio(
    "LOWER_LEG_LENGTH_RATIO",
    0.48,
)

LEG_STROKE_WIDTH = _validate_positive(
    "LEG_STROKE_WIDTH",
    10,
)

LEG_HIP_OFFSET_X = _validate_positive(
    "LEG_HIP_OFFSET_X",
    0.62,
)

LEG_HIP_OFFSET_Y = _validate_positive(
    "LEG_HIP_OFFSET_Y",
    1.88,
)

FOOT_WIDTH = _validate_positive(
    "FOOT_WIDTH",
    0.30,
)

FOOT_HEIGHT = _validate_positive(
    "FOOT_HEIGHT",
    0.10,
)


# ============================================================
# Anchor / debug marker sizing
# ============================================================

ANCHOR_DOT_RADIUS = _validate_positive(
    "ANCHOR_DOT_RADIUS",
    0.04,
)

GUIDE_STROKE_WIDTH = _validate_positive(
    "GUIDE_STROKE_WIDTH",
    1,
)

DEBUG_STROKE_WIDTH = _validate_positive(
    "DEBUG_STROKE_WIDTH",
    2,
)


# ============================================================
# Scene layout defaults
# ============================================================

DEFAULT_EDGE_BUFFER = _validate_non_negative(
    "DEFAULT_EDGE_BUFFER",
    0.40,
)

DEFAULT_OBJECT_BUFFER = _validate_non_negative(
    "DEFAULT_OBJECT_BUFFER",
    0.25,
)

DEFAULT_TITLE_TOP_BUFFER = _validate_non_negative(
    "DEFAULT_TITLE_TOP_BUFFER",
    0.50,
)


# ============================================================
# Derived body layout helpers
# ============================================================

BODY_M_HALF_WIDTH = BODY_M_WIDTH / 2
BODY_M_HALF_HEIGHT = BODY_M_HEIGHT / 2

FACE_ZONE_TOP_Y = BODY_M_HEIGHT * (0.5 - BODY_FACE_ZONE_TOP_RATIO)
FACE_ZONE_HEIGHT = BODY_M_HEIGHT * BODY_FACE_ZONE_HEIGHT_RATIO
FACE_ZONE_BOTTOM_Y = FACE_ZONE_TOP_Y - FACE_ZONE_HEIGHT
FACE_ZONE_CENTER_Y = (FACE_ZONE_TOP_Y + FACE_ZONE_BOTTOM_Y) / 2

BODY_TOP_Y = BODY_M_HALF_HEIGHT
BODY_BOTTOM_Y = -BODY_M_HALF_HEIGHT
BODY_LEFT_X = -BODY_M_HALF_WIDTH
BODY_RIGHT_X = BODY_M_HALF_WIDTH


# ============================================================
# Derived face placement helpers
# ============================================================

EYE_PAIR_WIDTH = (2 * EYE_WIDTH) + EYE_GAP
EYE_CENTER_TO_CENTER = EYE_WIDTH + EYE_GAP

LEFT_EYE_OFFSET_X = -(EYE_CENTER_TO_CENTER / 2)
RIGHT_EYE_OFFSET_X = EYE_CENTER_TO_CENTER / 2

NOSE_CENTER_Y = FACE_ZONE_CENTER_Y - 0.05
MOUTH_CENTER_Y = NOSE_CENTER_Y - 0.34


# ============================================================
# Derived skeleton placement helpers
# ============================================================

BODY_CORE_X = 0.0
BODY_CORE_Y = 0.0

SPINE_BASE_X = BODY_CORE_X
SPINE_BASE_Y = BODY_CORE_Y

SPINE_TOP_X = BODY_CORE_X
SPINE_TOP_Y = BODY_CORE_Y + SPINE_LENGTH

HEAD_ATTACHMENT_X = SPINE_TOP_X
HEAD_ATTACHMENT_Y = SPINE_TOP_Y + HEAD_ATTACHMENT_OFFSET_Y

SHOULDER_LEFT_X = -(SHOULDER_WIDTH / 2)
SHOULDER_RIGHT_X = SHOULDER_WIDTH / 2
SHOULDER_Y = BODY_CORE_Y + ARM_SHOULDER_OFFSET_Y

PELVIS_LEFT_X = -(PELVIS_WIDTH / 2)
PELVIS_RIGHT_X = PELVIS_WIDTH / 2
PELVIS_Y = BODY_CORE_Y - LEG_HIP_OFFSET_Y

HIP_LEFT_X = -LEG_HIP_OFFSET_X
HIP_RIGHT_X = LEG_HIP_OFFSET_X
HIP_Y = PELVIS_Y


# ============================================================
# Derived hat / limb helpers
# ============================================================

HAT_TOP_Y = BODY_TOP_Y + HAT_OFFSET_ABOVE_HEAD + HAT_HEIGHT
HAT_BASE_Y = BODY_TOP_Y + HAT_OFFSET_ABOVE_HEAD

UPPER_ARM_LENGTH = ARM_LENGTH * UPPER_ARM_LENGTH_RATIO
FOREARM_LENGTH = ARM_LENGTH * FOREARM_LENGTH_RATIO

UPPER_LEG_LENGTH = LEG_LENGTH * UPPER_LEG_LENGTH_RATIO
LOWER_LEG_LENGTH = LEG_LENGTH * LOWER_LEG_LENGTH_RATIO


# ============================================================
# Derived overall extents
# ============================================================

CREATURE_ESTIMATED_TOP = max(
    BODY_TOP_Y,
    HAT_TOP_Y,
    HEAD_ATTACHMENT_Y + HAT_HEIGHT,
)

CREATURE_ESTIMATED_BOTTOM = min(
    BODY_BOTTOM_Y,
    HIP_Y - LEG_LENGTH - FOOT_HEIGHT,
)

CREATURE_ESTIMATED_HEIGHT = (
    CREATURE_ESTIMATED_TOP - CREATURE_ESTIMATED_BOTTOM
)

CREATURE_ESTIMATED_LEFT = min(
    BODY_LEFT_X,
    SHOULDER_LEFT_X - ARM_LENGTH,
)

CREATURE_ESTIMATED_RIGHT = max(
    BODY_RIGHT_X,
    SHOULDER_RIGHT_X + ARM_LENGTH,
)

CREATURE_ESTIMATED_WIDTH = (
    CREATURE_ESTIMATED_RIGHT - CREATURE_ESTIMATED_LEFT
)


# ============================================================
# Convenience collections
# ============================================================

BASE_SIZE_GROUP: Dict[str, float] = {
    "CREATURE_BASE_HEIGHT": CREATURE_BASE_HEIGHT,
    "CREATURE_BASE_WIDTH": CREATURE_BASE_WIDTH,
    "CREATURE_SCALE": CREATURE_SCALE,
}

BODY_SIZE_GROUP: Dict[str, float] = {
    "BODY_M_WIDTH": BODY_M_WIDTH,
    "BODY_M_HEIGHT": BODY_M_HEIGHT,
    "BODY_M_STROKE_WIDTH": BODY_M_STROKE_WIDTH,
    "BODY_M_CORNER_RADIUS": BODY_M_CORNER_RADIUS,
    "BODY_CORE_RADIUS": BODY_CORE_RADIUS,
}

SKELETON_SIZE_GROUP: Dict[str, float] = {
    "JOINT_RADIUS": JOINT_RADIUS,
    "SPINE_LENGTH": SPINE_LENGTH,
    "HEAD_ATTACHMENT_OFFSET_Y": HEAD_ATTACHMENT_OFFSET_Y,
    "PELVIS_WIDTH": PELVIS_WIDTH,
    "SHOULDER_WIDTH": SHOULDER_WIDTH,
}

FACE_SIZE_GROUP: Dict[str, float] = {
    "EYE_RADIUS": EYE_RADIUS,
    "EYE_WIDTH": EYE_WIDTH,
    "EYE_HEIGHT": EYE_HEIGHT,
    "EYE_STROKE_WIDTH": EYE_STROKE_WIDTH,
    "PUPIL_RADIUS": PUPIL_RADIUS,
    "PUPIL_MAX_OFFSET": PUPIL_MAX_OFFSET,
    "EYE_GAP": EYE_GAP,
    "NOSE_WIDTH": NOSE_WIDTH,
    "NOSE_HEIGHT": NOSE_HEIGHT,
    "NOSE_STROKE_WIDTH": NOSE_STROKE_WIDTH,
    "MOUTH_WIDTH": MOUTH_WIDTH,
    "MOUTH_HEIGHT": MOUTH_HEIGHT,
    "MOUTH_STROKE_WIDTH": MOUTH_STROKE_WIDTH,
}

LIMB_SIZE_GROUP: Dict[str, float] = {
    "ARM_LENGTH": ARM_LENGTH,
    "UPPER_ARM_LENGTH": UPPER_ARM_LENGTH,
    "FOREARM_LENGTH": FOREARM_LENGTH,
    "ARM_STROKE_WIDTH": ARM_STROKE_WIDTH,
    "HAND_RADIUS": HAND_RADIUS,
    "LEG_LENGTH": LEG_LENGTH,
    "UPPER_LEG_LENGTH": UPPER_LEG_LENGTH,
    "LOWER_LEG_LENGTH": LOWER_LEG_LENGTH,
    "LEG_STROKE_WIDTH": LEG_STROKE_WIDTH,
    "FOOT_WIDTH": FOOT_WIDTH,
    "FOOT_HEIGHT": FOOT_HEIGHT,
}


# ============================================================
# Export control
# ============================================================

__all__ = [
    "CREATURE_BASE_HEIGHT",
    "CREATURE_BASE_WIDTH",
    "CREATURE_SCALE",
    "BODY_M_WIDTH",
    "BODY_M_HEIGHT",
    "BODY_M_STROKE_WIDTH",
    "BODY_M_CORNER_RADIUS",
    "BODY_FACE_ZONE_TOP_RATIO",
    "BODY_FACE_ZONE_HEIGHT_RATIO",
    "BODY_CORE_RADIUS",
    "JOINT_RADIUS",
    "SPINE_LENGTH",
    "HEAD_ATTACHMENT_OFFSET_Y",
    "PELVIS_WIDTH",
    "SHOULDER_WIDTH",
    "EYE_RADIUS",
    "EYE_WIDTH",
    "EYE_HEIGHT",
    "EYE_STROKE_WIDTH",
    "PUPIL_RADIUS",
    "PUPIL_MAX_OFFSET",
    "EYE_GAP",
    "NOSE_WIDTH",
    "NOSE_HEIGHT",
    "NOSE_STROKE_WIDTH",
    "MOUTH_WIDTH",
    "MOUTH_HEIGHT",
    "MOUTH_STROKE_WIDTH",
    "SMILE_ARC_ANGLE",
    "NEUTRAL_MOUTH_WIDTH",
    "HAT_WIDTH",
    "HAT_HEIGHT",
    "HAT_BRIM_WIDTH",
    "HAT_BRIM_HEIGHT",
    "HAT_OFFSET_ABOVE_HEAD",
    "ARM_LENGTH",
    "UPPER_ARM_LENGTH_RATIO",
    "FOREARM_LENGTH_RATIO",
    "ARM_STROKE_WIDTH",
    "ARM_SHOULDER_OFFSET_X",
    "ARM_SHOULDER_OFFSET_Y",
    "HAND_RADIUS",
    "LEG_LENGTH",
    "UPPER_LEG_LENGTH_RATIO",
    "LOWER_LEG_LENGTH_RATIO",
    "LEG_STROKE_WIDTH",
    "LEG_HIP_OFFSET_X",
    "LEG_HIP_OFFSET_Y",
    "FOOT_WIDTH",
    "FOOT_HEIGHT",
    "ANCHOR_DOT_RADIUS",
    "GUIDE_STROKE_WIDTH",
    "DEBUG_STROKE_WIDTH",
    "DEFAULT_EDGE_BUFFER",
    "DEFAULT_OBJECT_BUFFER",
    "DEFAULT_TITLE_TOP_BUFFER",
    "BODY_M_HALF_WIDTH",
    "BODY_M_HALF_HEIGHT",
    "FACE_ZONE_TOP_Y",
    "FACE_ZONE_HEIGHT",
    "FACE_ZONE_BOTTOM_Y",
    "FACE_ZONE_CENTER_Y",
    "BODY_TOP_Y",
    "BODY_BOTTOM_Y",
    "BODY_LEFT_X",
    "BODY_RIGHT_X",
    "EYE_PAIR_WIDTH",
    "EYE_CENTER_TO_CENTER",
    "LEFT_EYE_OFFSET_X",
    "RIGHT_EYE_OFFSET_X",
    "NOSE_CENTER_Y",
    "MOUTH_CENTER_Y",
    "BODY_CORE_X",
    "BODY_CORE_Y",
    "SPINE_BASE_X",
    "SPINE_BASE_Y",
    "SPINE_TOP_X",
    "SPINE_TOP_Y",
    "HEAD_ATTACHMENT_X",
    "HEAD_ATTACHMENT_Y",
    "SHOULDER_LEFT_X",
    "SHOULDER_RIGHT_X",
    "SHOULDER_Y",
    "PELVIS_LEFT_X",
    "PELVIS_RIGHT_X",
    "PELVIS_Y",
    "HIP_LEFT_X",
    "HIP_RIGHT_X",
    "HIP_Y",
    "HAT_TOP_Y",
    "HAT_BASE_Y",
    "UPPER_ARM_LENGTH",
    "FOREARM_LENGTH",
    "UPPER_LEG_LENGTH",
    "LOWER_LEG_LENGTH",
    "CREATURE_ESTIMATED_TOP",
    "CREATURE_ESTIMATED_BOTTOM",
    "CREATURE_ESTIMATED_HEIGHT",
    "CREATURE_ESTIMATED_LEFT",
    "CREATURE_ESTIMATED_RIGHT",
    "CREATURE_ESTIMATED_WIDTH",
    "BASE_SIZE_GROUP",
    "BODY_SIZE_GROUP",
    "SKELETON_SIZE_GROUP",
    "FACE_SIZE_GROUP",
    "LIMB_SIZE_GROUP",
]