# File: mathlab_creature/core/audio/helpers.py

"""
Audio Utility Helpers
mathlab-mylinehub-creature

Purpose:
- safe audio execution
- crash prevention
- silent fallback behavior
- CI/headless-safe helpers
- reusable audio wrappers
- audio guards for actions/scenes

This module protects the animation system from:
- missing pyo installation
- missing audio devices
- audio server failures
- headless rendering environments
- CI pipeline crashes
- runtime audio exceptions

IMPORTANT:
This module should NEVER:
- generate procedural sounds
- boot multiple servers
- contain animation logic

It ONLY provides safe wrappers/utilities.
"""

from __future__ import annotations

import functools
from typing import Any, Callable, Optional

from mathlab_creature.core.logger import get_logger

from mathlab_creature.core.audio.audio_config import (
    AUDIO_ENABLED,
)

from mathlab_creature.core.audio.audio_server import (
    boot_audio_server,
    get_audio_server,
    is_audio_enabled,
)

logger = get_logger(__name__)


# ============================================================
# SAFE PLAY
# ============================================================


def safe_play(
    sound_callable: Callable,
    *args,
    **kwargs,
) -> Optional[Any]:
    """
    Safely executes procedural sound generators.

    This function prevents audio crashes from affecting:
    - animations
    - scene rendering
    - CI pipelines
    - headless environments

    Example:
        safe_play(play_walk_step)

    Returns:
        Optional[Any]
    """

    if not AUDIO_ENABLED:
        return None

    if not is_audio_enabled():
        return None

    try:
        server = get_audio_server()

        if server is None:
            server = boot_audio_server()

        if server is None:
            logger.debug(
                "Audio server unavailable. Skipping sound playback."
            )
            return None

        return sound_callable(*args, **kwargs)

    except Exception as exc:

        logger.debug(
            "safe_play prevented audio crash: %s",
            exc,
        )

        return None


# ============================================================
# AUDIO ENABLED DECORATOR
# ============================================================


def with_audio_enabled(
    sound_function: Callable,
) -> Callable:
    """
    Decorator that safely guards sound functions.

    Example:

        @with_audio_enabled
        def play_custom_sound():
            ...

    Useful for:
    - procedural generators
    - timeline-triggered sounds
    - editor previews
    """

    @functools.wraps(sound_function)
    def wrapper(*args, **kwargs):

        if not AUDIO_ENABLED:
            return None

        if not is_audio_enabled():
            return None

        try:
            server = get_audio_server()

            if server is None:
                server = boot_audio_server()

            if server is None:
                return None

            return sound_function(*args, **kwargs)

        except Exception as exc:

            logger.debug(
                "Audio decorator blocked crash in '%s': %s",
                sound_function.__name__,
                exc,
            )

            return None

    return wrapper


# ============================================================
# SILENT FALLBACK
# ============================================================


def silent_return(*args, **kwargs):
    """
    Safe no-op fallback.

    Useful for:
    - disabled audio
    - testing
    - mock systems
    """

    return None


# ============================================================
# AUDIO ENVIRONMENT CHECKS
# ============================================================


def audio_available() -> bool:
    """
    Returns whether audio is available and enabled.
    """

    if not AUDIO_ENABLED:
        return False

    if not is_audio_enabled():
        return False

    try:
        server = get_audio_server()

        if server is None:
            server = boot_audio_server()

        return server is not None

    except Exception:
        return False


def ensure_audio_ready() -> bool:
    """
    Attempts to safely initialize audio.

    Returns:
        bool
    """

    try:
        server = get_audio_server()

        if server is None:
            server = boot_audio_server()

        return server is not None

    except Exception as exc:

        logger.debug(
            "Failed to prepare audio environment: %s",
            exc,
        )

        return False


# ============================================================
# SAFE OPTIONAL EXECUTION
# ============================================================


def maybe_play_sound(
    enabled: bool,
    sound_callable: Callable,
    *args,
    **kwargs,
):
    """
    Conditionally plays sound safely.

    This is intended for action files.

    Example:

        maybe_play_sound(
            with_sound,
            play_walk_step,
        )

    Returns:
        Optional[Any]
    """

    if not enabled:
        return None

    return safe_play(
        sound_callable,
        *args,
        **kwargs,
    )


# ============================================================
# DEBUG HELPERS
# ============================================================


def log_audio_state() -> None:
    """
    Logs current audio system state.
    """

    try:
        server = get_audio_server()

        logger.info("========== AUDIO STATE ==========")
        logger.info("AUDIO_ENABLED = %s", AUDIO_ENABLED)
        logger.info(
            "SERVER_EXISTS = %s",
            server is not None,
        )

        if server is not None:

            try:
                logger.info(
                    "SERVER_STARTED = %s",
                    server.getIsStarted(),
                )

            except Exception:
                logger.info("SERVER_STARTED = unknown")

        logger.info("=================================")

    except Exception as exc:

        logger.debug(
            "Failed to log audio state: %s",
            exc,
        )


# ============================================================
# HEADLESS / CI HELPERS
# ============================================================


def disable_audio_for_ci() -> None:
    """
    Helper for CI/headless environments.

    Example:
        disable_audio_for_ci()
    """

    logger.info(
        "CI/headless mode detected. Audio-safe mode active."
    )


# ============================================================
# MODULE READY
# ============================================================

logger.debug("audio helper utilities initialized.")