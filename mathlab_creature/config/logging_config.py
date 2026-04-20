"""
Central logging configuration for mathlab-mylinehub-creature.

This module keeps logging behavior controlled from one place so that:
- log levels are consistent
- debug mode can be turned on/off centrally
- format changes happen in one file
- future file logging can be added without touching many modules

Use this together with:
- core/logger.py

This file does not create loggers directly for every module.
It defines shared configuration values and lightweight helper builders.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Final


# ============================================================
# Project logger identity
# ============================================================

LOGGER_NAME: Final[str] = "mathlab_mylinehub_creature"
LOGGER_NAMESPACE_SEPARATOR: Final[str] = "."


# ============================================================
# Runtime mode naming
# ============================================================

MODE_DEVELOPMENT: Final[str] = "development"
MODE_PRODUCTION: Final[str] = "production"
MODE_TEST: Final[str] = "test"

DEFAULT_LOGGING_MODE: Final[str] = MODE_DEVELOPMENT


# ============================================================
# Global logging switches
# ============================================================

ENABLE_LOGGING: Final[bool] = True
ENABLE_CONSOLE_LOGGING: Final[bool] = True
ENABLE_FILE_LOGGING: Final[bool] = False

# Prevent duplicate handler attachment when setup is called multiple times.
CLEAR_EXISTING_HANDLERS_ON_SETUP: Final[bool] = True

# Control whether project loggers propagate to the root logger.
ENABLE_LOGGER_PROPAGATION: Final[bool] = False

# When file logging is enabled later, this path can be used.
LOG_FILE_PATH: Final[str] = "logs/project.log"
LOG_FILE_ENCODING: Final[str] = "utf-8"
LOG_FILE_MODE: Final[str] = "a"


# ============================================================
# Logging levels
# ============================================================

LOG_LEVEL_DEBUG: Final[int] = logging.DEBUG
LOG_LEVEL_INFO: Final[int] = logging.INFO
LOG_LEVEL_WARNING: Final[int] = logging.WARNING
LOG_LEVEL_ERROR: Final[int] = logging.ERROR
LOG_LEVEL_CRITICAL: Final[int] = logging.CRITICAL

# Primary default log level.
DEFAULT_LOG_LEVEL: Final[int] = LOG_LEVEL_INFO

# Use this for detailed development output.
DEVELOPMENT_LOG_LEVEL: Final[int] = LOG_LEVEL_DEBUG

# Use this for less noisy stable usage.
PRODUCTION_LOG_LEVEL: Final[int] = LOG_LEVEL_WARNING

# Useful for tests where info noise may be unnecessary.
TEST_LOG_LEVEL: Final[int] = LOG_LEVEL_WARNING


# ============================================================
# Handler identity
# ============================================================

CONSOLE_HANDLER_NAME: Final[str] = "console"
FILE_HANDLER_NAME: Final[str] = "file"


# ============================================================
# Format strings
# ============================================================

LOG_FORMAT_STANDARD: Final[str] = (
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)
LOG_FORMAT_SIMPLE: Final[str] = "%(levelname)s | %(message)s"
LOG_FORMAT_DEBUG: Final[str] = (
    "%(asctime)s | %(levelname)-8s | %(name)s | "
    "%(filename)s:%(lineno)d | %(message)s"
)

LOG_DATE_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"


# ============================================================
# Module-specific logging toggles
# ============================================================

LOG_CONFIG_EVENTS: Final[bool] = True
LOG_SCENE_EVENTS: Final[bool] = True
LOG_CREATURE_BUILD: Final[bool] = True
LOG_PART_BUILD: Final[bool] = True
LOG_POSE_EVENTS: Final[bool] = True
LOG_ACTION_EVENTS: Final[bool] = True
LOG_PROP_EVENTS: Final[bool] = True
LOG_RENDER_EVENTS: Final[bool] = True
LOG_LAYOUT_EVENTS: Final[bool] = False
LOG_GEOMETRY_EVENTS: Final[bool] = False


# ============================================================
# Debug behavior flags
# ============================================================

SHOW_DEBUG_BANNER: Final[bool] = False
RAISE_ON_LOG_SETUP_ERROR: Final[bool] = False
WARN_ON_REPEATED_SETUP: Final[bool] = False


# ============================================================
# Default handler behavior
# ============================================================

DEFAULT_HANDLER_LEVEL: Final[int] = DEFAULT_LOG_LEVEL
DEFAULT_CONSOLE_FORMAT: Final[str] = LOG_FORMAT_STANDARD
DEFAULT_FILE_FORMAT: Final[str] = LOG_FORMAT_STANDARD
DEFAULT_DATE_FORMAT: Final[str] = LOG_DATE_FORMAT


# ============================================================
# Lightweight helper builders
# ============================================================

def get_mode_log_level(mode: str) -> int:
    """
    Return the recommended base log level for a named runtime mode.
    """
    mode_normalized = (mode or "").strip().lower()

    if mode_normalized == MODE_DEVELOPMENT:
        return DEVELOPMENT_LOG_LEVEL
    if mode_normalized == MODE_PRODUCTION:
        return PRODUCTION_LOG_LEVEL
    if mode_normalized == MODE_TEST:
        return TEST_LOG_LEVEL

    return DEFAULT_LOG_LEVEL


def build_logging_settings(mode: str = DEFAULT_LOGGING_MODE) -> Dict[str, Any]:
    """
    Build a plain dictionary of shared logging settings.

    This is intentionally lightweight so core/logger.py can decide
    how to translate these settings into actual logger/handler objects.
    """
    resolved_level = get_mode_log_level(mode)

    return {
        "logger_name": LOGGER_NAME,
        "mode": mode,
        "enable_logging": ENABLE_LOGGING,
        "enable_console_logging": ENABLE_CONSOLE_LOGGING,
        "enable_file_logging": ENABLE_FILE_LOGGING,
        "clear_existing_handlers_on_setup": CLEAR_EXISTING_HANDLERS_ON_SETUP,
        "enable_logger_propagation": ENABLE_LOGGER_PROPAGATION,
        "log_file_path": LOG_FILE_PATH,
        "log_file_encoding": LOG_FILE_ENCODING,
        "log_file_mode": LOG_FILE_MODE,
        "resolved_log_level": resolved_level,
        "default_handler_level": DEFAULT_HANDLER_LEVEL,
        "console_handler_name": CONSOLE_HANDLER_NAME,
        "file_handler_name": FILE_HANDLER_NAME,
        "console_format": DEFAULT_CONSOLE_FORMAT,
        "file_format": DEFAULT_FILE_FORMAT,
        "debug_format": LOG_FORMAT_DEBUG,
        "date_format": DEFAULT_DATE_FORMAT,
        "show_debug_banner": SHOW_DEBUG_BANNER,
        "raise_on_log_setup_error": RAISE_ON_LOG_SETUP_ERROR,
        "warn_on_repeated_setup": WARN_ON_REPEATED_SETUP,
    }


# ============================================================
# Export control
# ============================================================

__all__ = [
    "LOGGER_NAME",
    "LOGGER_NAMESPACE_SEPARATOR",
    "MODE_DEVELOPMENT",
    "MODE_PRODUCTION",
    "MODE_TEST",
    "DEFAULT_LOGGING_MODE",
    "ENABLE_LOGGING",
    "ENABLE_CONSOLE_LOGGING",
    "ENABLE_FILE_LOGGING",
    "CLEAR_EXISTING_HANDLERS_ON_SETUP",
    "ENABLE_LOGGER_PROPAGATION",
    "LOG_FILE_PATH",
    "LOG_FILE_ENCODING",
    "LOG_FILE_MODE",
    "LOG_LEVEL_DEBUG",
    "LOG_LEVEL_INFO",
    "LOG_LEVEL_WARNING",
    "LOG_LEVEL_ERROR",
    "LOG_LEVEL_CRITICAL",
    "DEFAULT_LOG_LEVEL",
    "DEVELOPMENT_LOG_LEVEL",
    "PRODUCTION_LOG_LEVEL",
    "TEST_LOG_LEVEL",
    "CONSOLE_HANDLER_NAME",
    "FILE_HANDLER_NAME",
    "LOG_FORMAT_STANDARD",
    "LOG_FORMAT_SIMPLE",
    "LOG_FORMAT_DEBUG",
    "LOG_DATE_FORMAT",
    "LOG_CONFIG_EVENTS",
    "LOG_SCENE_EVENTS",
    "LOG_CREATURE_BUILD",
    "LOG_PART_BUILD",
    "LOG_POSE_EVENTS",
    "LOG_ACTION_EVENTS",
    "LOG_PROP_EVENTS",
    "LOG_RENDER_EVENTS",
    "LOG_LAYOUT_EVENTS",
    "LOG_GEOMETRY_EVENTS",
    "SHOW_DEBUG_BANNER",
    "RAISE_ON_LOG_SETUP_ERROR",
    "WARN_ON_REPEATED_SETUP",
    "DEFAULT_HANDLER_LEVEL",
    "DEFAULT_CONSOLE_FORMAT",
    "DEFAULT_FILE_FORMAT",
    "DEFAULT_DATE_FORMAT",
    "get_mode_log_level",
    "build_logging_settings",
]