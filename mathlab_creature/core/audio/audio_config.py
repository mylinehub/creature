# File: mathlab_creature/core/audio/audio_config.py

"""
Global Audio Configuration
mathlab-mylinehub-creature

Purpose:
- centralized audio settings
- global volume management
- per-action sound tuning
- future scene presets
- mute controls
- cinematic balancing
- consistent sound behavior across project

IMPORTANT:
This file should ONLY contain:
- configuration values
- audio tuning constants
- sound presets
- lightweight helper functions

DO NOT:
- boot pyo server
- generate sounds
- play sounds
- contain procedural synthesis logic
"""

from __future__ import annotations


# ============================================================
# GLOBAL AUDIO TOGGLES
# ============================================================

# Master enable/disable switch
AUDIO_ENABLED = True

# Global mute
MASTER_MUTE = False

# Enable debug audio logging
AUDIO_DEBUG = False


# ============================================================
# MASTER AUDIO SETTINGS
# ============================================================

# Overall master volume
MASTER_VOLUME = 0.70

# Default fade duration for soft transitions
MASTER_FADE_TIME = 0.05

# Stereo spread amount
STEREO_WIDTH = 1.0

# Global sample rate preference
DEFAULT_SAMPLE_RATE = 44100

# Default audio buffer size
DEFAULT_BUFFER_SIZE = 512


# ============================================================
# ACTION VOLUMES
# ============================================================

# Walk / footstep sounds
WALK_VOLUME = 0.45

# Blink sounds
BLINK_VOLUME = 0.12

# Wave motion sounds
WAVE_VOLUME = 0.35

# Hop motion sounds
HOP_VOLUME = 0.50

# Point gesture sounds
POINT_VOLUME = 0.28

# Look/focus movement sounds
LOOK_VOLUME = 0.18

# Turn/swipe sounds
TURN_VOLUME = 0.30

# Idle ambient sounds
IDLE_VOLUME = 0.10

# UI / educational cue sounds
UI_VOLUME = 0.40


# ============================================================
# TIMING SETTINGS
# ============================================================

# Base procedural envelope attack
DEFAULT_ATTACK = 0.005

# Base procedural release
DEFAULT_RELEASE = 0.08

# Soft cinematic timing multiplier
TIMING_SCALE = 1.0


# ============================================================
# WALK SOUND SETTINGS
# ============================================================

# Base pitch for footsteps
WALK_BASE_FREQUENCY = 110

# Random pitch variation
WALK_PITCH_VARIATION = 8

# Random amplitude variation
WALK_VOLUME_VARIATION = 0.05

# Stereo movement feel
WALK_STEREO_PAN_AMOUNT = 0.20


# ============================================================
# BLINK SOUND SETTINGS
# ============================================================

BLINK_BASE_FREQUENCY = 1400
BLINK_NOISE_AMOUNT = 0.03


# ============================================================
# HOP SOUND SETTINGS
# ============================================================

HOP_BASE_FREQUENCY = 220
HOP_LANDING_FREQUENCY = 90


# ============================================================
# WAVE SOUND SETTINGS
# ============================================================

WAVE_SWISH_FREQUENCY = 600
WAVE_NOISE_AMOUNT = 0.08


# ============================================================
# POINT SOUND SETTINGS
# ============================================================

POINT_CLICK_FREQUENCY = 880
POINT_CLICK_DURATION = 0.07


# ============================================================
# LOOK SOUND SETTINGS
# ============================================================

LOOK_SWEEP_FREQUENCY = 520
LOOK_SWEEP_DURATION = 0.05


# ============================================================
# TURN SOUND SETTINGS
# ============================================================

TURN_SWEEP_FREQUENCY = 350
TURN_SWEEP_DURATION = 0.12


# ============================================================
# FUTURE SCENE PRESETS
# ============================================================

SCENE_AUDIO_PRESETS = {
    "default": {
        "master_volume": 0.70,
        "walk_volume": 0.45,
        "ui_volume": 0.40,
    },
    "teaching": {
        "master_volume": 0.60,
        "walk_volume": 0.30,
        "ui_volume": 0.55,
    },
    "cinematic": {
        "master_volume": 0.85,
        "walk_volume": 0.55,
        "ui_volume": 0.30,
    },
    "quiet": {
        "master_volume": 0.35,
        "walk_volume": 0.18,
        "ui_volume": 0.20,
    },
    "silent": {
        "master_volume": 0.0,
        "walk_volume": 0.0,
        "ui_volume": 0.0,
    },
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================


def is_audio_enabled() -> bool:
    """
    Returns whether audio is globally enabled.
    """

    return AUDIO_ENABLED and not MASTER_MUTE


def get_master_volume() -> float:
    """
    Returns clamped master volume.
    """

    return max(0.0, min(1.0, MASTER_VOLUME))


def apply_scene_preset(preset_name: str) -> dict:
    """
    Returns scene preset configuration.

    Args:
        preset_name:
            Name of preset.

    Returns:
        dict
    """

    return SCENE_AUDIO_PRESETS.get(
        preset_name,
        SCENE_AUDIO_PRESETS["default"],
    )


# ============================================================
# MODULE READY
# ============================================================

if AUDIO_DEBUG:
    print("[audio_config] Audio configuration loaded.")