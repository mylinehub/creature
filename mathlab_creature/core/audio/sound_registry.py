# File: mathlab_creature/core/audio/sound_registry.py

"""
Sound Registry System
mathlab-mylinehub-creature

Purpose:
- central sound mapping registry
- action-to-sound routing
- reusable sound lookup
- future automation support
- AI-triggerable sound events
- editor/timeline integration
- cinematic sound orchestration

This module creates a clean abstraction layer between:
    actions -> procedural sound generators

IMPORTANT:
DO NOT:
- generate sound here
- boot audio server here
- create pyo objects here

ONLY:
- register sounds
- map action names
- provide lookup utilities
"""

from __future__ import annotations

from typing import Callable, Dict, Optional

from mathlab_creature.core.logger import get_logger

from mathlab_creature.core.audio.procedural import (
    play_walk_step,
    play_blink_sound,
    play_wave_sound,
    play_hop_sound,
    play_point_sound,
    play_look_sound,
    play_turn_sound,
    play_ui_confirm_sound,
)

logger = get_logger(__name__)


# ============================================================
# SOUND REGISTRY
# ============================================================

SOUND_REGISTRY: Dict[str, Callable] = {
    # --------------------------------------------------------
    # MOVEMENT
    # --------------------------------------------------------
    "walk": play_walk_step,
    "step": play_walk_step,
    "hop": play_hop_sound,
    "turn": play_turn_sound,

    # --------------------------------------------------------
    # FACE / EXPRESSION
    # --------------------------------------------------------
    "blink": play_blink_sound,
    "look": play_look_sound,

    # --------------------------------------------------------
    # GESTURES
    # --------------------------------------------------------
    "wave": play_wave_sound,
    "point": play_point_sound,

    # --------------------------------------------------------
    # UI / SYSTEM
    # --------------------------------------------------------
    "ui_confirm": play_ui_confirm_sound,
}


# ============================================================
# REGISTRY HELPERS
# ============================================================


def get_sound(sound_name: str) -> Optional[Callable]:
    """
    Returns registered sound generator.

    Args:
        sound_name:
            Registry key.

    Returns:
        Optional[Callable]
    """

    sound = SOUND_REGISTRY.get(sound_name)

    if sound is None:
        logger.debug(
            "Sound '%s' not found in registry.",
            sound_name,
        )

    return sound


def has_sound(sound_name: str) -> bool:
    """
    Checks whether sound exists in registry.
    """

    return sound_name in SOUND_REGISTRY


def register_sound(
    sound_name: str,
    sound_callable: Callable,
) -> None:
    """
    Registers a new sound generator.

    Args:
        sound_name:
            Registry key.

        sound_callable:
            Function that generates sound.
    """

    if sound_name in SOUND_REGISTRY:

        logger.warning(
            "Overwriting existing sound registry entry: %s",
            sound_name,
        )

    SOUND_REGISTRY[sound_name] = sound_callable

    logger.info(
        "Registered sound: %s",
        sound_name,
    )


def unregister_sound(sound_name: str) -> None:
    """
    Removes sound from registry.
    """

    if sound_name not in SOUND_REGISTRY:

        logger.warning(
            "Cannot unregister missing sound: %s",
            sound_name,
        )

        return

    del SOUND_REGISTRY[sound_name]

    logger.info(
        "Unregistered sound: %s",
        sound_name,
    )


def play_registered_sound(
    sound_name: str,
    *args,
    **kwargs,
):
    """
    Plays sound from registry safely.

    Example:
        play_registered_sound("walk")

    Returns:
        Whatever the sound generator returns.
    """

    sound_callable = get_sound(sound_name)

    if sound_callable is None:

        logger.debug(
            "Skipping playback. Unknown sound: %s",
            sound_name,
        )

        return None

    try:
        return sound_callable(*args, **kwargs)

    except Exception as exc:

        logger.exception(
            "Failed to play registered sound: %s",
            sound_name,
        )

        logger.error("Playback error: %s", exc)

        return None


def list_registered_sounds() -> list[str]:
    """
    Returns sorted registry keys.
    """

    return sorted(SOUND_REGISTRY.keys())


def clear_sound_registry() -> None:
    """
    Clears registry.

    Mostly useful for:
    - testing
    - hot reload systems
    - editor tooling
    """

    SOUND_REGISTRY.clear()

    logger.warning("Sound registry cleared.")


# ============================================================
# FUTURE AUTOMATION SUPPORT
# ============================================================

ACTION_SOUND_MAP = {
    "walk_action": "walk",
    "blink_action": "blink",
    "wave_action": "wave",
    "hop_action": "hop",
    "point_action": "point",
    "look_action": "look",
    "turn_action": "turn",
}


def get_action_sound(action_name: str) -> Optional[str]:
    """
    Maps action name -> sound name.

    Useful for:
    - timeline systems
    - AI orchestration
    - scene automation
    - editor integrations
    """

    return ACTION_SOUND_MAP.get(action_name)


# ============================================================
# MODULE READY
# ============================================================

logger.debug(
    "Sound registry initialized with %s sounds.",
    len(SOUND_REGISTRY),
)