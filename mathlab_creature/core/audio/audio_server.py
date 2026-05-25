# File: mathlab_creature/core/audio/audio_server.py

"""
Centralized Pyo Audio Server Management
mathlab-mylinehub-creature

Responsibilities:
- boot pyo server
- singleton server lifecycle
- prevent multiple server boots
- safe shutdown handling
- graceful fallback if audio unavailable
- thread-safe initialization
- production-grade logging
- future-ready integration

IMPORTANT:
This module MUST be the ONLY place that boots pyo.

DO NOT:
- boot pyo inside action files
- create multiple Server() instances
- directly manage server lifecycle elsewhere
"""

from __future__ import annotations

import atexit
import threading
from typing import Optional

from mathlab_creature.core.logger import get_logger

logger = get_logger(__name__)


# ============================================================
# OPTIONAL PYO IMPORT
# ============================================================

PYO_AVAILABLE = False

try:
    from pyo import Server

    PYO_AVAILABLE = True

except Exception as exc:
    logger.warning(
        "Pyo import failed. Audio disabled. Reason: %s",
        exc,
    )


# ============================================================
# GLOBAL SINGLETON STATE
# ============================================================

_audio_server: Optional["Server"] = None
_audio_lock = threading.Lock()
_audio_booted = False
_audio_enabled = True


# ============================================================
# INTERNAL HELPERS
# ============================================================


def _is_server_running(server: "Server") -> bool:
    """
    Safely checks whether the pyo server is running.
    """

    try:
        return bool(server.getIsStarted())

    except Exception:
        return False


# ============================================================
# PUBLIC API
# ============================================================


def boot_audio_server(
    sample_rate: int = 44100,
    buffer_size: int = 512,
    duplex: int = 0,
    audio_backend: Optional[str] = None,
) -> Optional["Server"]:
    """
    Boots the global singleton pyo server.

    Safe to call multiple times.

    Returns:
        Optional[pyo.Server]
    """

    global _audio_server
    global _audio_booted
    global _audio_enabled

    with _audio_lock:

        # ----------------------------------------------------
        # AUDIO DISABLED
        # ----------------------------------------------------

        if not _audio_enabled:
            logger.info("Audio system disabled.")
            return None

        # ----------------------------------------------------
        # PYO NOT AVAILABLE
        # ----------------------------------------------------

        if not PYO_AVAILABLE:
            logger.warning(
                "Cannot boot audio server because pyo is unavailable."
            )
            return None

        # ----------------------------------------------------
        # ALREADY RUNNING
        # ----------------------------------------------------

        if _audio_server is not None:

            if _is_server_running(_audio_server):
                logger.debug("Audio server already running.")
                return _audio_server

            logger.warning(
                "Audio server exists but is inactive. Rebooting."
            )

        # ----------------------------------------------------
        # BOOT SERVER
        # ----------------------------------------------------

        try:
            logger.info("Booting pyo audio server...")

            server = Server(
                sr=sample_rate,
                buffersize=buffer_size,
                duplex=duplex,
                audio=audio_backend,
                nchnls=2,
            )

            server.boot()
            server.start()

            _audio_server = server
            _audio_booted = True

            logger.info(
                "Audio server booted successfully | sr=%s | buffer=%s",
                sample_rate,
                buffer_size,
            )

            return _audio_server

        except Exception as exc:

            logger.exception(
                "Failed to boot audio server. Falling back to silent mode."
            )

            logger.error("Audio boot error: %s", exc)

            _audio_server = None
            _audio_booted = False
            _audio_enabled = False

            return None


def get_audio_server() -> Optional["Server"]:
    """
    Returns the singleton audio server instance.
    """

    return _audio_server


def shutdown_audio_server() -> None:
    """
    Safely shuts down the audio server.

    Never raises exceptions.
    """

    global _audio_server
    global _audio_booted

    with _audio_lock:

        if _audio_server is None:
            logger.debug("No active audio server to shutdown.")
            return

        try:
            logger.info("Stopping audio server...")

            if _is_server_running(_audio_server):
                _audio_server.stop()

            logger.info("Shutting down audio server...")

            _audio_server.shutdown()

            logger.info("Audio server shutdown complete.")

        except Exception as exc:

            logger.exception("Error during audio shutdown.")
            logger.error("Shutdown error: %s", exc)

        finally:

            _audio_server = None
            _audio_booted = False


# ============================================================
# OPTIONAL GLOBAL CONTROLS
# ============================================================


def disable_audio() -> None:
    """
    Globally disables audio system.
    """

    global _audio_enabled

    logger.info("Audio system globally disabled.")

    _audio_enabled = False


def enable_audio() -> None:
    """
    Re-enables audio system.
    """

    global _audio_enabled

    logger.info("Audio system globally enabled.")

    _audio_enabled = True


def is_audio_enabled() -> bool:
    """
    Returns whether audio is enabled.
    """

    return _audio_enabled


def is_audio_booted() -> bool:
    """
    Returns whether audio server has been booted.
    """

    return _audio_booted


# ============================================================
# AUTO CLEANUP
# ============================================================

atexit.register(shutdown_audio_server)


# ============================================================
# MODULE READY
# ============================================================

logger.debug("audio_server module initialized.")