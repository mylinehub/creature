"""
Central color definitions for the mathlab-mylinehub-creature project.

This module keeps reusable color values in one place so that:
- the creature stays visually consistent
- later visual changes are easy
- part files do not hardcode random colors
- scene/debug colors remain separate from final design colors

Design rules:
- public colors are uppercase constants
- values are plain hex strings for clean ManimGL usage
- both palette colors and semantic role colors are exposed
"""

from __future__ import annotations

import re
from typing import Dict


# ============================================================
# Internal helpers
# ============================================================

_HEX_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


def _validate_hex_color(name: str, value: str) -> str:
    """
    Validate a color string and return it unchanged.

    This catches typos early, such as:
    - missing '#'
    - wrong length
    - invalid hex characters
    """
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string, got {type(value).__name__}")
    if not _HEX_COLOR_RE.match(value):
        raise ValueError(
            f"{name} must be a 7-character hex color like '#FFFFFF', got {value!r}"
        )
    return value.upper()


# ============================================================
# Core neutrals
# ============================================================

WHITE = _validate_hex_color("WHITE", "#FFFFFF")
BLACK = _validate_hex_color("BLACK", "#000000")

GRAY_50 = _validate_hex_color("GRAY_50", "#FAFAFA")
GRAY_100 = _validate_hex_color("GRAY_100", "#F5F5F5")
GRAY_200 = _validate_hex_color("GRAY_200", "#E5E5E5")
GRAY_300 = _validate_hex_color("GRAY_300", "#D4D4D4")
GRAY_400 = _validate_hex_color("GRAY_400", "#A3A3A3")
GRAY_500 = _validate_hex_color("GRAY_500", "#737373")
GRAY_600 = _validate_hex_color("GRAY_600", "#525252")
GRAY_700 = _validate_hex_color("GRAY_700", "#404040")
GRAY_800 = _validate_hex_color("GRAY_800", "#262626")
GRAY_900 = _validate_hex_color("GRAY_900", "#171717")


# ============================================================
# Brand / project accents
# ============================================================

# Primary brand-inspired dark for the M body.
MYLINEHUB_M_BODY = _validate_hex_color("MYLINEHUB_M_BODY", "#111111")

# Slightly softer dark used for outlines or secondary dark elements.
MYLINEHUB_DARK = _validate_hex_color("MYLINEHUB_DARK", "#1F1F1F")

# Bright accent for highlights, UI-like cards, emphasis, or motion cues.
MYLINEHUB_ACCENT_BLUE = _validate_hex_color("MYLINEHUB_ACCENT_BLUE", "#2563EB")

# Optional warm accent for expressive accessory details.
MYLINEHUB_ACCENT_GOLD = _validate_hex_color("MYLINEHUB_ACCENT_GOLD", "#D4A017")


# ============================================================
# Creature body colors
# ============================================================

CREATURE_BODY_FILL = MYLINEHUB_M_BODY
CREATURE_BODY_STROKE = BLACK

CREATURE_HAT_FILL = _validate_hex_color("CREATURE_HAT_FILL", "#2B2B2B")
CREATURE_HAT_STROKE = BLACK

CREATURE_ARM_COLOR = BLACK
CREATURE_HAND_COLOR = BLACK
CREATURE_LEG_COLOR = BLACK
CREATURE_FOOT_COLOR = BLACK


# ============================================================
# Face colors
# ============================================================

EYE_WHITE = WHITE
EYE_STROKE = BLACK
PUPIL_FILL = BLACK
PUPIL_HIGHLIGHT = WHITE

NOSE_FILL = _validate_hex_color("NOSE_FILL", "#222222")
NOSE_STROKE = BLACK

MOUTH_COLOR = BLACK
FACE_GUIDE_COLOR = GRAY_300


# ============================================================
# Scene and helper colors
# ============================================================

BACKGROUND_LIGHT = WHITE
BACKGROUND_SOFT = GRAY_100
GRID_LIGHT = GRAY_200
GUIDE_COLOR = GRAY_400
ANCHOR_COLOR = _validate_hex_color("ANCHOR_COLOR", "#EF4444")


# ============================================================
# Prop colors
# ============================================================

POINTER_STICK_COLOR = _validate_hex_color("POINTER_STICK_COLOR", "#8B5A2B")
MATH_BOARD_FILL = _validate_hex_color("MATH_BOARD_FILL", "#0F172A")
MATH_BOARD_STROKE = BLACK
FORMULA_CARD_FILL = WHITE
FORMULA_CARD_STROKE = BLACK
AXIS_COLOR = BLACK


# ============================================================
# Logging / debug visual colors
# ============================================================

DEBUG_SUCCESS = _validate_hex_color("DEBUG_SUCCESS", "#16A34A")
DEBUG_WARNING = _validate_hex_color("DEBUG_WARNING", "#F59E0B")
DEBUG_ERROR = _validate_hex_color("DEBUG_ERROR", "#DC2626")
DEBUG_INFO = _validate_hex_color("DEBUG_INFO", "#2563EB")


# ============================================================
# Semantic aliases
# ============================================================
# These make later code more readable. Example:
# use OUTLINE_COLOR instead of remembering which dark/black constant to pick.

OUTLINE_COLOR = BLACK
PRIMARY_TEXT_COLOR = BLACK
SECONDARY_TEXT_COLOR = GRAY_700

CREATURE_PRIMARY_COLOR = CREATURE_BODY_FILL
CREATURE_SECONDARY_COLOR = CREATURE_HAT_FILL

SCENE_BACKGROUND_COLOR = BACKGROUND_LIGHT
SCENE_GRID_COLOR = GRID_LIGHT
SCENE_GUIDE_COLOR = GUIDE_COLOR


# ============================================================
# Grouped palettes (optional convenience)
# ============================================================

NEUTRAL_PALETTE: Dict[str, str] = {
    "WHITE": WHITE,
    "BLACK": BLACK,
    "GRAY_50": GRAY_50,
    "GRAY_100": GRAY_100,
    "GRAY_200": GRAY_200,
    "GRAY_300": GRAY_300,
    "GRAY_400": GRAY_400,
    "GRAY_500": GRAY_500,
    "GRAY_600": GRAY_600,
    "GRAY_700": GRAY_700,
    "GRAY_800": GRAY_800,
    "GRAY_900": GRAY_900,
}

BRAND_PALETTE: Dict[str, str] = {
    "MYLINEHUB_M_BODY": MYLINEHUB_M_BODY,
    "MYLINEHUB_DARK": MYLINEHUB_DARK,
    "MYLINEHUB_ACCENT_BLUE": MYLINEHUB_ACCENT_BLUE,
    "MYLINEHUB_ACCENT_GOLD": MYLINEHUB_ACCENT_GOLD,
}

DEBUG_PALETTE: Dict[str, str] = {
    "DEBUG_SUCCESS": DEBUG_SUCCESS,
    "DEBUG_WARNING": DEBUG_WARNING,
    "DEBUG_ERROR": DEBUG_ERROR,
    "DEBUG_INFO": DEBUG_INFO,
}


# ============================================================
# Export control
# ============================================================

__all__ = [
    "WHITE",
    "BLACK",
    "GRAY_50",
    "GRAY_100",
    "GRAY_200",
    "GRAY_300",
    "GRAY_400",
    "GRAY_500",
    "GRAY_600",
    "GRAY_700",
    "GRAY_800",
    "GRAY_900",
    "MYLINEHUB_M_BODY",
    "MYLINEHUB_DARK",
    "MYLINEHUB_ACCENT_BLUE",
    "MYLINEHUB_ACCENT_GOLD",
    "CREATURE_BODY_FILL",
    "CREATURE_BODY_STROKE",
    "CREATURE_HAT_FILL",
    "CREATURE_HAT_STROKE",
    "CREATURE_ARM_COLOR",
    "CREATURE_HAND_COLOR",
    "CREATURE_LEG_COLOR",
    "CREATURE_FOOT_COLOR",
    "EYE_WHITE",
    "EYE_STROKE",
    "PUPIL_FILL",
    "PUPIL_HIGHLIGHT",
    "NOSE_FILL",
    "NOSE_STROKE",
    "MOUTH_COLOR",
    "FACE_GUIDE_COLOR",
    "BACKGROUND_LIGHT",
    "BACKGROUND_SOFT",
    "GRID_LIGHT",
    "GUIDE_COLOR",
    "ANCHOR_COLOR",
    "POINTER_STICK_COLOR",
    "MATH_BOARD_FILL",
    "MATH_BOARD_STROKE",
    "FORMULA_CARD_FILL",
    "FORMULA_CARD_STROKE",
    "AXIS_COLOR",
    "DEBUG_SUCCESS",
    "DEBUG_WARNING",
    "DEBUG_ERROR",
    "DEBUG_INFO",
    "OUTLINE_COLOR",
    "PRIMARY_TEXT_COLOR",
    "SECONDARY_TEXT_COLOR",
    "CREATURE_PRIMARY_COLOR",
    "CREATURE_SECONDARY_COLOR",
    "SCENE_BACKGROUND_COLOR",
    "SCENE_GRID_COLOR",
    "SCENE_GUIDE_COLOR",
    "NEUTRAL_PALETTE",
    "BRAND_PALETTE",
    "DEBUG_PALETTE",
]