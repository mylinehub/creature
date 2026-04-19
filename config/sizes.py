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
        raise TypeError(f"{name} must be numeric, got {type(value).__name__}")
    if value <= 0:
        raise ValueError(f"{name} must be > 0, got {value!r}")
    return value


def _validate_non_negative(name: str, value: float | int) -> float | int:
    """Require a non-negative numeric value."""
    if not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be numeric, got {type(value).__name__}")
    if value < 0:
        raise ValueError(f"{name} must be >= 0, got {value!r}")
    return value


def _validate_ratio(name: str, value: float | int) -> float | int:
    """Require a ratio in the closed interval [0, 1]."""
    if not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be numeric, got {type(value).__name__}")
    if not (0 <= value <= 1):
        raise ValueError(f"{name} must be between 0 and 1, got {value!r}")
    return value


# ============================================================
# Base creature scale
# ============================================================

# Overall target height for the mascot when assembled.
CREATURE_BASE_HEIGHT = _validate_positive("CREATURE_BASE_HEIGHT", 4.8)

# Overall target width for the mascot footprint.
CREATURE_BASE_WIDTH = _validate_positive("CREATURE_BASE_WIDTH", 3.6)

# Default scale multiplier for uniform scaling.
CREATURE_SCALE = _validate_positive("CREATURE_SCALE", 1.0)


# ============================================================
# Body M sizing
# ============================================================

# Outer width/height of the M-shaped body.
BODY_M_WIDTH = _validate_positive("BODY_M_WIDTH", 3.6)
BODY_M_HEIGHT = _validate_positive("BODY_M_HEIGHT", 4.2)

# Visual stroke width if the M body is drawn with thick line segments.
BODY_M_STROKE_WIDTH = _validate_positive("BODY_M_STROKE_WIDTH", 18)

# Corner softness / rounding, if later used in custom construction.
BODY_M_CORNER_RADIUS = _validate_non_negative("BODY_M_CORNER_RADIUS", 0.12)

# Internal spacing guides for placing face elements.
BODY_FACE_ZONE_TOP_RATIO = _validate_ratio("BODY_FACE_ZONE_TOP_RATIO", 0.24)
BODY_FACE_ZONE_HEIGHT_RATIO = _validate_ratio("BODY_FACE_ZONE_HEIGHT_RATIO", 0.22)


# ============================================================
# Eye sizing
# ============================================================

EYE_RADIUS = _validate_positive("EYE_RADIUS", 0.22)
EYE_WIDTH = _validate_positive("EYE_WIDTH", 0.42)
EYE_HEIGHT = _validate_positive("EYE_HEIGHT", 0.52)
EYE_STROKE_WIDTH = _validate_positive("EYE_STROKE_WIDTH", 2)

PUPIL_RADIUS = _validate_positive("PUPIL_RADIUS", 0.08)
PUPIL_MAX_OFFSET = _validate_non_negative("PUPIL_MAX_OFFSET", 0.07)

EYE_GAP = _validate_non_negative("EYE_GAP", 0.42)


# ============================================================
# Nose sizing
# ============================================================

NOSE_WIDTH = _validate_positive("NOSE_WIDTH", 0.14)
NOSE_HEIGHT = _validate_positive("NOSE_HEIGHT", 0.20)
NOSE_STROKE_WIDTH = _validate_positive("NOSE_STROKE_WIDTH", 2)


# ============================================================
# Mouth sizing
# ============================================================

MOUTH_WIDTH = _validate_positive("MOUTH_WIDTH", 0.48)
MOUTH_HEIGHT = _validate_positive("MOUTH_HEIGHT", 0.18)
MOUTH_STROKE_WIDTH = _validate_positive("MOUTH_STROKE_WIDTH", 4)

SMILE_ARC_ANGLE = _validate_positive("SMILE_ARC_ANGLE", 1.8)
NEUTRAL_MOUTH_WIDTH = _validate_positive("NEUTRAL_MOUTH_WIDTH", 0.30)


# ============================================================
# Hat sizing
# ============================================================

HAT_WIDTH = _validate_positive("HAT_WIDTH", 1.25)
HAT_HEIGHT = _validate_positive("HAT_HEIGHT", 0.72)
HAT_BRIM_WIDTH = _validate_positive("HAT_BRIM_WIDTH", 1.05)
HAT_BRIM_HEIGHT = _validate_positive("HAT_BRIM_HEIGHT", 0.08)
HAT_OFFSET_ABOVE_HEAD = _validate_non_negative("HAT_OFFSET_ABOVE_HEAD", 0.12)


# ============================================================
# Arm sizing
# ============================================================

ARM_LENGTH = _validate_positive("ARM_LENGTH", 1.15)
ARM_STROKE_WIDTH = _validate_positive("ARM_STROKE_WIDTH", 10)
ARM_SHOULDER_OFFSET_X = _validate_positive("ARM_SHOULDER_OFFSET_X", 1.05)
ARM_SHOULDER_OFFSET_Y = _validate_non_negative("ARM_SHOULDER_OFFSET_Y", 0.10)

HAND_RADIUS = _validate_positive("HAND_RADIUS", 0.11)


# ============================================================
# Leg sizing
# ============================================================

LEG_LENGTH = _validate_positive("LEG_LENGTH", 1.15)
LEG_STROKE_WIDTH = _validate_positive("LEG_STROKE_WIDTH", 10)
LEG_HIP_OFFSET_X = _validate_positive("LEG_HIP_OFFSET_X", 0.62)
LEG_HIP_OFFSET_Y = _validate_positive("LEG_HIP_OFFSET_Y", 1.88)

FOOT_WIDTH = _validate_positive("FOOT_WIDTH", 0.30)
FOOT_HEIGHT = _validate_positive("FOOT_HEIGHT", 0.10)


# ============================================================
# Pointer / prop sizing
# ============================================================

POINTER_STICK_LENGTH = _validate_positive("POINTER_STICK_LENGTH", 1.60)
POINTER_STICK_STROKE_WIDTH = _validate_positive("POINTER_STICK_STROKE_WIDTH", 6)

FORMULA_CARD_WIDTH = _validate_positive("FORMULA_CARD_WIDTH", 3.0)
FORMULA_CARD_HEIGHT = _validate_positive("FORMULA_CARD_HEIGHT", 1.6)

MATH_BOARD_WIDTH = _validate_positive("MATH_BOARD_WIDTH", 6.5)
MATH_BOARD_HEIGHT = _validate_positive("MATH_BOARD_HEIGHT", 3.8)


# ============================================================
# Anchor / debug marker sizing
# ============================================================

ANCHOR_DOT_RADIUS = _validate_positive("ANCHOR_DOT_RADIUS", 0.04)
GUIDE_STROKE_WIDTH = _validate_positive("GUIDE_STROKE_WIDTH", 1)
DEBUG_STROKE_WIDTH = _validate_positive("DEBUG_STROKE_WIDTH", 2)


# ============================================================
# Scene layout defaults
# ============================================================

DEFAULT_EDGE_BUFFER = _validate_non_negative("DEFAULT_EDGE_BUFFER", 0.40)
DEFAULT_OBJECT_BUFFER = _validate_non_negative("DEFAULT_OBJECT_BUFFER", 0.25)
DEFAULT_TITLE_TOP_BUFFER = _validate_non_negative("DEFAULT_TITLE_TOP_BUFFER", 0.50)


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
# Derived hat / limb helpers
# ============================================================

HAT_TOP_Y = BODY_TOP_Y + HAT_OFFSET_ABOVE_HEAD + HAT_HEIGHT
HAT_BASE_Y = BODY_TOP_Y + HAT_OFFSET_ABOVE_HEAD

SHOULDER_LEFT_X = -ARM_SHOULDER_OFFSET_X
SHOULDER_RIGHT_X = ARM_SHOULDER_OFFSET_X
SHOULDER_Y = ARM_SHOULDER_OFFSET_Y

HIP_LEFT_X = -LEG_HIP_OFFSET_X
HIP_RIGHT_X = LEG_HIP_OFFSET_X
HIP_Y = -LEG_HIP_OFFSET_Y


# ============================================================
# Derived overall extents
# ============================================================

CREATURE_ESTIMATED_TOP = max(BODY_TOP_Y, HAT_TOP_Y)
CREATURE_ESTIMATED_BOTTOM = BODY_BOTTOM_Y - LEG_LENGTH - FOOT_HEIGHT
CREATURE_ESTIMATED_HEIGHT = CREATURE_ESTIMATED_TOP - CREATURE_ESTIMATED_BOTTOM

CREATURE_ESTIMATED_LEFT = min(BODY_LEFT_X, SHOULDER_LEFT_X - ARM_LENGTH)
CREATURE_ESTIMATED_RIGHT = max(BODY_RIGHT_X, SHOULDER_RIGHT_X + ARM_LENGTH)
CREATURE_ESTIMATED_WIDTH = CREATURE_ESTIMATED_RIGHT - CREATURE_ESTIMATED_LEFT


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
    "ARM_STROKE_WIDTH": ARM_STROKE_WIDTH,
    "HAND_RADIUS": HAND_RADIUS,
    "LEG_LENGTH": LEG_LENGTH,
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
    "ARM_STROKE_WIDTH",
    "ARM_SHOULDER_OFFSET_X",
    "ARM_SHOULDER_OFFSET_Y",
    "HAND_RADIUS",
    "LEG_LENGTH",
    "LEG_STROKE_WIDTH",
    "LEG_HIP_OFFSET_X",
    "LEG_HIP_OFFSET_Y",
    "FOOT_WIDTH",
    "FOOT_HEIGHT",
    "POINTER_STICK_LENGTH",
    "POINTER_STICK_STROKE_WIDTH",
    "FORMULA_CARD_WIDTH",
    "FORMULA_CARD_HEIGHT",
    "MATH_BOARD_WIDTH",
    "MATH_BOARD_HEIGHT",
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
    "HAT_TOP_Y",
    "HAT_BASE_Y",
    "SHOULDER_LEFT_X",
    "SHOULDER_RIGHT_X",
    "SHOULDER_Y",
    "HIP_LEFT_X",
    "HIP_RIGHT_X",
    "HIP_Y",
    "CREATURE_ESTIMATED_TOP",
    "CREATURE_ESTIMATED_BOTTOM",
    "CREATURE_ESTIMATED_HEIGHT",
    "CREATURE_ESTIMATED_LEFT",
    "CREATURE_ESTIMATED_RIGHT",
    "CREATURE_ESTIMATED_WIDTH",
    "BASE_SIZE_GROUP",
    "BODY_SIZE_GROUP",
    "FACE_SIZE_GROUP",
    "LIMB_SIZE_GROUP",
]