"""
Central timing definitions for the mathlab-mylinehub-creature project.

This module stores reusable animation durations and pause values so that:
- scene timing stays consistent
- actions feel related to each other
- later tuning is easy from one place
- motion pacing stays readable and intentional

All values are plain numeric constants in seconds.
"""

from __future__ import annotations

from typing import Dict


# ============================================================
# Internal helpers
# ============================================================

def _validate_positive_time(name: str, value: float | int) -> float:
    """
    Require a strictly positive numeric duration.
    """
    if not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be numeric, got {type(value).__name__}")
    if value <= 0:
        raise ValueError(f"{name} must be > 0, got {value!r}")
    return float(value)


# ============================================================
# General scene timing
# ============================================================

DEFAULT_WAIT_TIME = _validate_positive_time("DEFAULT_WAIT_TIME", 1.0)
SHORT_WAIT_TIME = _validate_positive_time("SHORT_WAIT_TIME", 0.4)
LONG_WAIT_TIME = _validate_positive_time("LONG_WAIT_TIME", 1.8)


# ============================================================
# Basic object animation timing
# ============================================================

FADE_IN_TIME = _validate_positive_time("FADE_IN_TIME", 0.6)
FADE_OUT_TIME = _validate_positive_time("FADE_OUT_TIME", 0.5)
WRITE_TIME = _validate_positive_time("WRITE_TIME", 1.2)
CREATE_TIME = _validate_positive_time("CREATE_TIME", 1.0)
TRANSFORM_TIME = _validate_positive_time("TRANSFORM_TIME", 0.9)
MOVE_TIME = _validate_positive_time("MOVE_TIME", 1.0)
ROTATE_TIME = _validate_positive_time("ROTATE_TIME", 0.8)
SCALE_TIME = _validate_positive_time("SCALE_TIME", 0.8)


# ============================================================
# Creature entrance / exit timing
# ============================================================

CREATURE_INTRO_TIME = _validate_positive_time("CREATURE_INTRO_TIME", 1.4)
CREATURE_EXIT_TIME = _validate_positive_time("CREATURE_EXIT_TIME", 0.9)
CREATURE_LOOK_SETTLE_TIME = _validate_positive_time("CREATURE_LOOK_SETTLE_TIME", 0.35)


# ============================================================
# Face timing
# ============================================================

BLINK_CLOSE_TIME = _validate_positive_time("BLINK_CLOSE_TIME", 0.08)
BLINK_OPEN_TIME = _validate_positive_time("BLINK_OPEN_TIME", 0.12)
BLINK_TOTAL_TIME = BLINK_CLOSE_TIME + BLINK_OPEN_TIME

LOOK_SHIFT_TIME = _validate_positive_time("LOOK_SHIFT_TIME", 0.25)
LOOK_RETURN_TIME = _validate_positive_time("LOOK_RETURN_TIME", 0.30)
LOOK_TOTAL_TIME = LOOK_SHIFT_TIME + LOOK_RETURN_TIME

SMILE_TRANSFORM_TIME = _validate_positive_time("SMILE_TRANSFORM_TIME", 0.35)
MOUTH_REACT_TIME = _validate_positive_time("MOUTH_REACT_TIME", 0.30)


# ============================================================
# Body idle timing
# ============================================================

IDLE_BOB_UP_TIME = _validate_positive_time("IDLE_BOB_UP_TIME", 0.45)
IDLE_BOB_DOWN_TIME = _validate_positive_time("IDLE_BOB_DOWN_TIME", 0.45)
IDLE_BOB_CYCLE_TIME = IDLE_BOB_UP_TIME + IDLE_BOB_DOWN_TIME

IDLE_TILT_TIME = _validate_positive_time("IDLE_TILT_TIME", 0.40)


# ============================================================
# Arm / hand timing
# ============================================================

ARM_RAISE_TIME = _validate_positive_time("ARM_RAISE_TIME", 0.45)
ARM_LOWER_TIME = _validate_positive_time("ARM_LOWER_TIME", 0.40)
ARM_LIFT_CYCLE_TIME = ARM_RAISE_TIME + ARM_LOWER_TIME

WAVE_OUT_TIME = _validate_positive_time("WAVE_OUT_TIME", 0.25)
WAVE_BACK_TIME = _validate_positive_time("WAVE_BACK_TIME", 0.25)
WAVE_CYCLE_TIME = WAVE_OUT_TIME + WAVE_BACK_TIME

POINT_REACH_TIME = _validate_positive_time("POINT_REACH_TIME", 0.40)
POINT_HOLD_TIME = _validate_positive_time("POINT_HOLD_TIME", 0.60)
POINT_RETURN_TIME = _validate_positive_time("POINT_RETURN_TIME", 0.35)
POINT_TOTAL_TIME = POINT_REACH_TIME + POINT_HOLD_TIME + POINT_RETURN_TIME


# ============================================================
# Leg / movement timing
# ============================================================

STEP_TIME = _validate_positive_time("STEP_TIME", 0.35)
WALK_CYCLE_TIME = STEP_TIME * 2

HOP_DOWN_TIME = _validate_positive_time("HOP_DOWN_TIME", 0.16)
HOP_UP_TIME = _validate_positive_time("HOP_UP_TIME", 0.22)
HOP_LAND_TIME = _validate_positive_time("HOP_LAND_TIME", 0.18)
HOP_TOTAL_TIME = HOP_DOWN_TIME + HOP_UP_TIME + HOP_LAND_TIME


# ============================================================
# Pose timing
# ============================================================

POSE_CHANGE_TIME = _validate_positive_time("POSE_CHANGE_TIME", 0.6)
EXPRESSION_CHANGE_TIME = _validate_positive_time("EXPRESSION_CHANGE_TIME", 0.3)


# ============================================================
# Teaching / presentation timing
# ============================================================

POINTER_APPEAR_TIME = _validate_positive_time("POINTER_APPEAR_TIME", 0.5)
FORMULA_CARD_APPEAR_TIME = _validate_positive_time("FORMULA_CARD_APPEAR_TIME", 0.7)
BOARD_APPEAR_TIME = _validate_positive_time("BOARD_APPEAR_TIME", 0.8)
TEACHING_PAUSE_TIME = _validate_positive_time("TEACHING_PAUSE_TIME", 1.2)


# ============================================================
# Debug / preview timing
# ============================================================

DEBUG_FLASH_TIME = _validate_positive_time("DEBUG_FLASH_TIME", 0.25)
ANCHOR_SHOW_TIME = _validate_positive_time("ANCHOR_SHOW_TIME", 0.5)
GUIDE_SHOW_TIME = _validate_positive_time("GUIDE_SHOW_TIME", 0.5)


# ============================================================
# Timing presets / semantic aliases
# ============================================================

FAST_TIME = SHORT_WAIT_TIME
NORMAL_TIME = DEFAULT_WAIT_TIME
SLOW_TIME = LONG_WAIT_TIME

DEFAULT_CREATURE_ACTION_TIME = MOVE_TIME
DEFAULT_CREATURE_REACTION_TIME = EXPRESSION_CHANGE_TIME
DEFAULT_SCENE_PAUSE_TIME = DEFAULT_WAIT_TIME


# ============================================================
# Grouped timing collections
# ============================================================

SCENE_TIMINGS: Dict[str, float] = {
    "default_wait": DEFAULT_WAIT_TIME,
    "short_wait": SHORT_WAIT_TIME,
    "long_wait": LONG_WAIT_TIME,
}

BASIC_ANIMATION_TIMINGS: Dict[str, float] = {
    "fade_in": FADE_IN_TIME,
    "fade_out": FADE_OUT_TIME,
    "write": WRITE_TIME,
    "create": CREATE_TIME,
    "transform": TRANSFORM_TIME,
    "move": MOVE_TIME,
    "rotate": ROTATE_TIME,
    "scale": SCALE_TIME,
}

FACE_TIMINGS: Dict[str, float] = {
    "blink_close": BLINK_CLOSE_TIME,
    "blink_open": BLINK_OPEN_TIME,
    "blink_total": BLINK_TOTAL_TIME,
    "look_shift": LOOK_SHIFT_TIME,
    "look_return": LOOK_RETURN_TIME,
    "look_total": LOOK_TOTAL_TIME,
    "smile_transform": SMILE_TRANSFORM_TIME,
    "mouth_react": MOUTH_REACT_TIME,
}

IDLE_TIMINGS: Dict[str, float] = {
    "idle_bob_up": IDLE_BOB_UP_TIME,
    "idle_bob_down": IDLE_BOB_DOWN_TIME,
    "idle_bob_cycle": IDLE_BOB_CYCLE_TIME,
    "idle_tilt": IDLE_TILT_TIME,
}

ARM_TIMINGS: Dict[str, float] = {
    "arm_raise": ARM_RAISE_TIME,
    "arm_lower": ARM_LOWER_TIME,
    "arm_lift_cycle": ARM_LIFT_CYCLE_TIME,
    "wave_out": WAVE_OUT_TIME,
    "wave_back": WAVE_BACK_TIME,
    "wave_cycle": WAVE_CYCLE_TIME,
    "point_reach": POINT_REACH_TIME,
    "point_hold": POINT_HOLD_TIME,
    "point_return": POINT_RETURN_TIME,
    "point_total": POINT_TOTAL_TIME,
}

LEG_TIMINGS: Dict[str, float] = {
    "step": STEP_TIME,
    "walk_cycle": WALK_CYCLE_TIME,
    "hop_down": HOP_DOWN_TIME,
    "hop_up": HOP_UP_TIME,
    "hop_land": HOP_LAND_TIME,
    "hop_total": HOP_TOTAL_TIME,
}

POSE_TIMINGS: Dict[str, float] = {
    "pose_change": POSE_CHANGE_TIME,
    "expression_change": EXPRESSION_CHANGE_TIME,
}

TEACHING_TIMINGS: Dict[str, float] = {
    "pointer_appear": POINTER_APPEAR_TIME,
    "formula_card_appear": FORMULA_CARD_APPEAR_TIME,
    "board_appear": BOARD_APPEAR_TIME,
    "teaching_pause": TEACHING_PAUSE_TIME,
}

DEBUG_TIMINGS: Dict[str, float] = {
    "debug_flash": DEBUG_FLASH_TIME,
    "anchor_show": ANCHOR_SHOW_TIME,
    "guide_show": GUIDE_SHOW_TIME,
}


# ============================================================
# Export control
# ============================================================

__all__ = [
    "DEFAULT_WAIT_TIME",
    "SHORT_WAIT_TIME",
    "LONG_WAIT_TIME",
    "FADE_IN_TIME",
    "FADE_OUT_TIME",
    "WRITE_TIME",
    "CREATE_TIME",
    "TRANSFORM_TIME",
    "MOVE_TIME",
    "ROTATE_TIME",
    "SCALE_TIME",
    "CREATURE_INTRO_TIME",
    "CREATURE_EXIT_TIME",
    "CREATURE_LOOK_SETTLE_TIME",
    "BLINK_CLOSE_TIME",
    "BLINK_OPEN_TIME",
    "BLINK_TOTAL_TIME",
    "LOOK_SHIFT_TIME",
    "LOOK_RETURN_TIME",
    "LOOK_TOTAL_TIME",
    "SMILE_TRANSFORM_TIME",
    "MOUTH_REACT_TIME",
    "IDLE_BOB_UP_TIME",
    "IDLE_BOB_DOWN_TIME",
    "IDLE_BOB_CYCLE_TIME",
    "IDLE_TILT_TIME",
    "ARM_RAISE_TIME",
    "ARM_LOWER_TIME",
    "ARM_LIFT_CYCLE_TIME",
    "WAVE_OUT_TIME",
    "WAVE_BACK_TIME",
    "WAVE_CYCLE_TIME",
    "POINT_REACH_TIME",
    "POINT_HOLD_TIME",
    "POINT_RETURN_TIME",
    "POINT_TOTAL_TIME",
    "STEP_TIME",
    "WALK_CYCLE_TIME",
    "HOP_DOWN_TIME",
    "HOP_UP_TIME",
    "HOP_LAND_TIME",
    "HOP_TOTAL_TIME",
    "POSE_CHANGE_TIME",
    "EXPRESSION_CHANGE_TIME",
    "POINTER_APPEAR_TIME",
    "FORMULA_CARD_APPEAR_TIME",
    "BOARD_APPEAR_TIME",
    "TEACHING_PAUSE_TIME",
    "DEBUG_FLASH_TIME",
    "ANCHOR_SHOW_TIME",
    "GUIDE_SHOW_TIME",
    "FAST_TIME",
    "NORMAL_TIME",
    "SLOW_TIME",
    "DEFAULT_CREATURE_ACTION_TIME",
    "DEFAULT_CREATURE_REACTION_TIME",
    "DEFAULT_SCENE_PAUSE_TIME",
    "SCENE_TIMINGS",
    "BASIC_ANIMATION_TIMINGS",
    "FACE_TIMINGS",
    "IDLE_TIMINGS",
    "ARM_TIMINGS",
    "LEG_TIMINGS",
    "POSE_TIMINGS",
    "TEACHING_TIMINGS",
    "DEBUG_TIMINGS",
]