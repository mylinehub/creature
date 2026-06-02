"""
Default project settings for mathlab-mylinehub-creature.

This module collects general-purpose defaults shared across the project
that do not belong specifically to colors, sizes, or timings.

Use this file for:
- default visual behavior
- default creature state
- default scene toggles
- default debug toggles
- default naming/state values
- default audio toggles

Design goals:
- lightweight
- easy to scan
- safe to import from many files
- easy to extend without becoming noisy
"""

from __future__ import annotations

from typing import Dict, Final, Tuple

from mathlab_creature.config.colors import BACKGROUND_LIGHT
from mathlab_creature.config.colors import CREATURE_BODY_FILL
from mathlab_creature.config.colors import CREATURE_BODY_STROKE
from mathlab_creature.config.colors import CREATURE_HAT_FILL
from mathlab_creature.config.colors import EYE_WHITE
from mathlab_creature.config.colors import MOUTH_COLOR
from mathlab_creature.config.colors import NOSE_FILL


# ============================================================
# Project identity
# ============================================================

PROJECT_NAME: Final[str] = "mathlab-mylinehub-creature"
PROJECT_SLUG: Final[str] = "mathlab-mylinehub-creature"
CREATURE_NAME: Final[str] = "Myline M Creature"
CREATURE_SHORT_NAME: Final[str] = "MylineM"


# ============================================================
# Default scene behavior
# ============================================================

DEFAULT_SCENE_BACKGROUND_COLOR: Final[str] = BACKGROUND_LIGHT
DEFAULT_WAIT_TIME: Final[float] = 1.0
DEFAULT_PREVIEW_SCALE: Final[float] = 1.0

DEFAULT_SHOW_GUIDES: Final[bool] = False
DEFAULT_SHOW_ANCHORS: Final[bool] = False
DEFAULT_SHOW_DEBUG_LABELS: Final[bool] = False
DEFAULT_SHOW_PART_NAMES: Final[bool] = False


# ============================================================
# Default creature root state
# ============================================================

DEFAULT_ROOT_NAME: Final[str] = "creature_root"
DEFAULT_BODY_CORE_NAME: Final[str] = "body_core"
DEFAULT_SKELETON_NAME: Final[str] = "skeleton"

DEFAULT_CREATURE_SCALE: Final[float] = 1.0
DEFAULT_CREATURE_POSITION: Final[Tuple[float, float, float]] = (
    0.0,
    0.0,
    0.0,
)
DEFAULT_CREATURE_ROTATION_DEGREES: Final[float] = 0.0

DEFAULT_IS_VISIBLE: Final[bool] = True
DEFAULT_IS_FLIPPED: Final[bool] = False


# ============================================================
# Default creature visual state
# ============================================================

DEFAULT_CREATURE_BODY_FILL: Final[str] = CREATURE_BODY_FILL
DEFAULT_CREATURE_BODY_STROKE: Final[str] = CREATURE_BODY_STROKE
DEFAULT_CREATURE_HAT_FILL: Final[str] = CREATURE_HAT_FILL

DEFAULT_EYE_FILL: Final[str] = EYE_WHITE
DEFAULT_NOSE_FILL: Final[str] = NOSE_FILL
DEFAULT_MOUTH_COLOR: Final[str] = MOUTH_COLOR

DEFAULT_EXPRESSION: Final[str] = "neutral"
DEFAULT_LOOK_DIRECTION: Final[str] = "center"


# ============================================================
# Default action behavior
# ============================================================

DEFAULT_ENABLE_IDLE: Final[bool] = True
DEFAULT_ENABLE_BLINK: Final[bool] = True
DEFAULT_ENABLE_LOOK: Final[bool] = True
DEFAULT_ENABLE_WALK: Final[bool] = True
DEFAULT_ENABLE_STEP: Final[bool] = True
DEFAULT_ENABLE_TURN: Final[bool] = True
DEFAULT_ENABLE_WAVE: Final[bool] = True
DEFAULT_ENABLE_POINT: Final[bool] = True
DEFAULT_ENABLE_HOP: Final[bool] = True

DEFAULT_ENABLE_IDLE_BOB: Final[bool] = False
DEFAULT_ENABLE_AUTO_LOOK: Final[bool] = False

DEFAULT_MOVE_RUN_TIME: Final[float] = 1.0
DEFAULT_ROTATE_RUN_TIME: Final[float] = 0.8
DEFAULT_FADE_RUN_TIME: Final[float] = 0.6
DEFAULT_TRANSFORM_RUN_TIME: Final[float] = 0.9

DEFAULT_BLINK_INTERVAL_MIN: Final[float] = 2.4
DEFAULT_BLINK_INTERVAL_MAX: Final[float] = 4.2


# ============================================================
# Default audio behavior
# ============================================================

DEFAULT_AUDIO_ENABLED: Final[bool] = True
DEFAULT_PROCEDURAL_AUDIO_ENABLED: Final[bool] = True
DEFAULT_NARRATION_ENABLED: Final[bool] = False
DEFAULT_ACTION_SOUND_ENABLED: Final[bool] = True


# ============================================================
# Debug and development flags
# ============================================================

DEBUG_MODE: Final[bool] = True
STRICT_MODE: Final[bool] = False

LOG_CREATURE_BUILD: Final[bool] = True
LOG_SCENE_EVENTS: Final[bool] = True
LOG_ANIMATION_EVENTS: Final[bool] = True
LOG_LAYOUT_EVENTS: Final[bool] = False
LOG_GEOMETRY_EVENTS: Final[bool] = False
LOG_AUDIO_EVENTS: Final[bool] = False

SHOW_BUILD_STEPS: Final[bool] = False
SHOW_PART_BOUNDING_BOXES: Final[bool] = False
SHOW_ANCHOR_COORDINATES: Final[bool] = False
SHOW_FACE_ZONE_GUIDES: Final[bool] = False
SHOW_SKELETON_GUIDES: Final[bool] = False
SHOW_BODY_CORE_GUIDE: Final[bool] = False


# ============================================================
# Naming defaults
# ============================================================

ROOT_NAME: Final[str] = "creature_root"
BODY_CORE_NAME: Final[str] = "body_core"
SKELETON_NAME: Final[str] = "skeleton"
SPINE_NAME: Final[str] = "spine"
HEAD_NAME: Final[str] = "head"
PELVIS_NAME: Final[str] = "pelvis"

BODY_NAME: Final[str] = "body_m"
LEFT_EYE_NAME: Final[str] = "left_eye"
RIGHT_EYE_NAME: Final[str] = "right_eye"
NOSE_NAME: Final[str] = "nose"
MOUTH_NAME: Final[str] = "mouth"
HAT_NAME: Final[str] = "hat"

LEFT_SHOULDER_NAME: Final[str] = "left_shoulder"
RIGHT_SHOULDER_NAME: Final[str] = "right_shoulder"
LEFT_ARM_NAME: Final[str] = "left_arm"
RIGHT_ARM_NAME: Final[str] = "right_arm"
LEFT_HAND_NAME: Final[str] = "left_hand"
RIGHT_HAND_NAME: Final[str] = "right_hand"

LEFT_HIP_NAME: Final[str] = "left_hip"
RIGHT_HIP_NAME: Final[str] = "right_hip"
LEFT_LEG_NAME: Final[str] = "left_leg"
RIGHT_LEG_NAME: Final[str] = "right_leg"
LEFT_FOOT_NAME: Final[str] = "left_foot"
RIGHT_FOOT_NAME: Final[str] = "right_foot"


# ============================================================
# Allowed default state values
# ============================================================

ALLOWED_EXPRESSIONS: Final[Tuple[str, ...]] = (
    "neutral",
    "happy",
    "thinking",
    "surprised",
)

ALLOWED_LOOK_DIRECTIONS: Final[Tuple[str, ...]] = (
    "center",
    "left",
    "right",
    "up",
    "down",
    "up_left",
    "up_right",
    "down_left",
    "down_right",
)

ALLOWED_ACTIONS: Final[Tuple[str, ...]] = (
    "idle",
    "blink",
    "look",
    "walk",
    "step",
    "turn",
    "wave",
    "point",
    "hop",
)


# ============================================================
# Grouped default dictionaries
# ============================================================

SCENE_DEFAULTS: Final[Dict[str, object]] = {
    "background_color": DEFAULT_SCENE_BACKGROUND_COLOR,
    "wait_time": DEFAULT_WAIT_TIME,
    "preview_scale": DEFAULT_PREVIEW_SCALE,
    "show_guides": DEFAULT_SHOW_GUIDES,
    "show_anchors": DEFAULT_SHOW_ANCHORS,
    "show_debug_labels": DEFAULT_SHOW_DEBUG_LABELS,
    "show_part_names": DEFAULT_SHOW_PART_NAMES,
}

CREATURE_DEFAULTS: Final[Dict[str, object]] = {
    "root_name": DEFAULT_ROOT_NAME,
    "body_core_name": DEFAULT_BODY_CORE_NAME,
    "skeleton_name": DEFAULT_SKELETON_NAME,
    "scale": DEFAULT_CREATURE_SCALE,
    "position": DEFAULT_CREATURE_POSITION,
    "rotation_degrees": DEFAULT_CREATURE_ROTATION_DEGREES,
    "body_fill": DEFAULT_CREATURE_BODY_FILL,
    "body_stroke": DEFAULT_CREATURE_BODY_STROKE,
    "hat_fill": DEFAULT_CREATURE_HAT_FILL,
    "eye_fill": DEFAULT_EYE_FILL,
    "nose_fill": DEFAULT_NOSE_FILL,
    "mouth_color": DEFAULT_MOUTH_COLOR,
    "expression": DEFAULT_EXPRESSION,
    "look_direction": DEFAULT_LOOK_DIRECTION,
    "is_visible": DEFAULT_IS_VISIBLE,
    "is_flipped": DEFAULT_IS_FLIPPED,
}

ACTION_DEFAULTS: Final[Dict[str, object]] = {
    "enable_idle": DEFAULT_ENABLE_IDLE,
    "enable_blink": DEFAULT_ENABLE_BLINK,
    "enable_look": DEFAULT_ENABLE_LOOK,
    "enable_walk": DEFAULT_ENABLE_WALK,
    "enable_step": DEFAULT_ENABLE_STEP,
    "enable_turn": DEFAULT_ENABLE_TURN,
    "enable_wave": DEFAULT_ENABLE_WAVE,
    "enable_point": DEFAULT_ENABLE_POINT,
    "enable_hop": DEFAULT_ENABLE_HOP,
    "enable_idle_bob": DEFAULT_ENABLE_IDLE_BOB,
    "enable_auto_look": DEFAULT_ENABLE_AUTO_LOOK,
    "move_run_time": DEFAULT_MOVE_RUN_TIME,
    "rotate_run_time": DEFAULT_ROTATE_RUN_TIME,
    "fade_run_time": DEFAULT_FADE_RUN_TIME,
    "transform_run_time": DEFAULT_TRANSFORM_RUN_TIME,
    "blink_interval_min": DEFAULT_BLINK_INTERVAL_MIN,
    "blink_interval_max": DEFAULT_BLINK_INTERVAL_MAX,
}

MOTION_DEFAULTS: Final[Dict[str, object]] = ACTION_DEFAULTS

AUDIO_DEFAULTS: Final[Dict[str, object]] = {
    "audio_enabled": DEFAULT_AUDIO_ENABLED,
    "procedural_audio_enabled": DEFAULT_PROCEDURAL_AUDIO_ENABLED,
    "narration_enabled": DEFAULT_NARRATION_ENABLED,
    "action_sound_enabled": DEFAULT_ACTION_SOUND_ENABLED,
}

DEBUG_DEFAULTS: Final[Dict[str, object]] = {
    "debug_mode": DEBUG_MODE,
    "strict_mode": STRICT_MODE,
    "log_creature_build": LOG_CREATURE_BUILD,
    "log_scene_events": LOG_SCENE_EVENTS,
    "log_animation_events": LOG_ANIMATION_EVENTS,
    "log_layout_events": LOG_LAYOUT_EVENTS,
    "log_geometry_events": LOG_GEOMETRY_EVENTS,
    "log_audio_events": LOG_AUDIO_EVENTS,
    "show_build_steps": SHOW_BUILD_STEPS,
    "show_part_bounding_boxes": SHOW_PART_BOUNDING_BOXES,
    "show_anchor_coordinates": SHOW_ANCHOR_COORDINATES,
    "show_face_zone_guides": SHOW_FACE_ZONE_GUIDES,
    "show_skeleton_guides": SHOW_SKELETON_GUIDES,
    "show_body_core_guide": SHOW_BODY_CORE_GUIDE,
}

PART_NAME_DEFAULTS: Final[Dict[str, str]] = {
    "root": ROOT_NAME,
    "body_core": BODY_CORE_NAME,
    "skeleton": SKELETON_NAME,
    "spine": SPINE_NAME,
    "head": HEAD_NAME,
    "pelvis": PELVIS_NAME,
    "body": BODY_NAME,
    "left_eye": LEFT_EYE_NAME,
    "right_eye": RIGHT_EYE_NAME,
    "nose": NOSE_NAME,
    "mouth": MOUTH_NAME,
    "hat": HAT_NAME,
    "left_shoulder": LEFT_SHOULDER_NAME,
    "right_shoulder": RIGHT_SHOULDER_NAME,
    "left_arm": LEFT_ARM_NAME,
    "right_arm": RIGHT_ARM_NAME,
    "left_hand": LEFT_HAND_NAME,
    "right_hand": RIGHT_HAND_NAME,
    "left_hip": LEFT_HIP_NAME,
    "right_hip": RIGHT_HIP_NAME,
    "left_leg": LEFT_LEG_NAME,
    "right_leg": RIGHT_LEG_NAME,
    "left_foot": LEFT_FOOT_NAME,
    "right_foot": RIGHT_FOOT_NAME,
}


# ============================================================
# Export control
# ============================================================

__all__ = [
    "PROJECT_NAME",
    "PROJECT_SLUG",
    "CREATURE_NAME",
    "CREATURE_SHORT_NAME",
    "DEFAULT_SCENE_BACKGROUND_COLOR",
    "DEFAULT_WAIT_TIME",
    "DEFAULT_PREVIEW_SCALE",
    "DEFAULT_SHOW_GUIDES",
    "DEFAULT_SHOW_ANCHORS",
    "DEFAULT_SHOW_DEBUG_LABELS",
    "DEFAULT_SHOW_PART_NAMES",
    "DEFAULT_ROOT_NAME",
    "DEFAULT_BODY_CORE_NAME",
    "DEFAULT_SKELETON_NAME",
    "DEFAULT_CREATURE_SCALE",
    "DEFAULT_CREATURE_POSITION",
    "DEFAULT_CREATURE_ROTATION_DEGREES",
    "DEFAULT_CREATURE_BODY_FILL",
    "DEFAULT_CREATURE_BODY_STROKE",
    "DEFAULT_CREATURE_HAT_FILL",
    "DEFAULT_EYE_FILL",
    "DEFAULT_NOSE_FILL",
    "DEFAULT_MOUTH_COLOR",
    "DEFAULT_EXPRESSION",
    "DEFAULT_LOOK_DIRECTION",
    "DEFAULT_IS_VISIBLE",
    "DEFAULT_IS_FLIPPED",
    "DEFAULT_ENABLE_IDLE",
    "DEFAULT_ENABLE_BLINK",
    "DEFAULT_ENABLE_LOOK",
    "DEFAULT_ENABLE_WALK",
    "DEFAULT_ENABLE_STEP",
    "DEFAULT_ENABLE_TURN",
    "DEFAULT_ENABLE_WAVE",
    "DEFAULT_ENABLE_POINT",
    "DEFAULT_ENABLE_HOP",
    "DEFAULT_ENABLE_IDLE_BOB",
    "DEFAULT_ENABLE_AUTO_LOOK",
    "DEFAULT_MOVE_RUN_TIME",
    "DEFAULT_ROTATE_RUN_TIME",
    "DEFAULT_FADE_RUN_TIME",
    "DEFAULT_TRANSFORM_RUN_TIME",
    "DEFAULT_BLINK_INTERVAL_MIN",
    "DEFAULT_BLINK_INTERVAL_MAX",
    "DEFAULT_AUDIO_ENABLED",
    "DEFAULT_PROCEDURAL_AUDIO_ENABLED",
    "DEFAULT_NARRATION_ENABLED",
    "DEFAULT_ACTION_SOUND_ENABLED",
    "DEBUG_MODE",
    "STRICT_MODE",
    "LOG_CREATURE_BUILD",
    "LOG_SCENE_EVENTS",
    "LOG_ANIMATION_EVENTS",
    "LOG_LAYOUT_EVENTS",
    "LOG_GEOMETRY_EVENTS",
    "LOG_AUDIO_EVENTS",
    "SHOW_BUILD_STEPS",
    "SHOW_PART_BOUNDING_BOXES",
    "SHOW_ANCHOR_COORDINATES",
    "SHOW_FACE_ZONE_GUIDES",
    "SHOW_SKELETON_GUIDES",
    "SHOW_BODY_CORE_GUIDE",
    "ROOT_NAME",
    "BODY_CORE_NAME",
    "SKELETON_NAME",
    "SPINE_NAME",
    "HEAD_NAME",
    "PELVIS_NAME",
    "BODY_NAME",
    "LEFT_EYE_NAME",
    "RIGHT_EYE_NAME",
    "NOSE_NAME",
    "MOUTH_NAME",
    "HAT_NAME",
    "LEFT_SHOULDER_NAME",
    "RIGHT_SHOULDER_NAME",
    "LEFT_ARM_NAME",
    "RIGHT_ARM_NAME",
    "LEFT_HAND_NAME",
    "RIGHT_HAND_NAME",
    "LEFT_HIP_NAME",
    "RIGHT_HIP_NAME",
    "LEFT_LEG_NAME",
    "RIGHT_LEG_NAME",
    "LEFT_FOOT_NAME",
    "RIGHT_FOOT_NAME",
    "ALLOWED_EXPRESSIONS",
    "ALLOWED_LOOK_DIRECTIONS",
    "ALLOWED_ACTIONS",
    "SCENE_DEFAULTS",
    "CREATURE_DEFAULTS",
    "ACTION_DEFAULTS",
    "MOTION_DEFAULTS",
    "AUDIO_DEFAULTS",
    "DEBUG_DEFAULTS",
    "PART_NAME_DEFAULTS",
]