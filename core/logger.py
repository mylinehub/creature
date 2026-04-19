"""
Logger helper for mathlab-mylinehub-creature.

This file provides a centralized way to create and use loggers across the project.

It uses configuration from:
- config/logging_config.py

Goals:
- single point of logging setup
- consistent formatting
- easy access via get_logger(...)
- avoid duplicate handler setup
"""

from __future__ import annotations

import logging
import os
from typing import Optional

from config.logging_config import (
    LOGGER_NAME,
    LOGGER_NAMESPACE_SEPARATOR,
    ENABLE_LOGGING,
    ENABLE_CONSOLE_LOGGING,
    ENABLE_FILE_LOGGING,
    CLEAR_EXISTING_HANDLERS_ON_SETUP,
    ENABLE_LOGGER_PROPAGATION,
    LOG_FILE_PATH,
    LOG_FILE_ENCODING,
    LOG_FILE_MODE,
    DEFAULT_LOGGING_MODE,
    DEFAULT_LOG_LEVEL,
    DEFAULT_HANDLER_LEVEL,
    DEFAULT_CONSOLE_FORMAT,
    DEFAULT_FILE_FORMAT,
    DEFAULT_DATE_FORMAT,
    CONSOLE_HANDLER_NAME,
    FILE_HANDLER_NAME,
    RAISE_ON_LOG_SETUP_ERROR,
    WARN_ON_REPEATED_SETUP,
    SHOW_DEBUG_BANNER,
    build_logging_settings,
)


# ============================================================
# Internal state
# ============================================================

_LOGGER_INITIALIZED = False
_INITIALIZED_MODE: str | None = None


# ============================================================
# Internal helpers
# ============================================================

def _ensure_string(value: object, name: str) -> str:
    """
    Ensure a value is a string.
    """
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string, got {type(value).__name__}")
    return value


def _clean_child_logger_name(name: str) -> str:
    """
    Normalize a child logger name.

    This keeps logger naming stable and avoids accidental duplicate separators.
    """
    name = _ensure_string(name, "name").strip()

    if not name:
        return ""

    while name.startswith(LOGGER_NAMESPACE_SEPARATOR):
        name = name[len(LOGGER_NAMESPACE_SEPARATOR):]

    return name


def _ensure_log_directory(file_path: str) -> None:
    """
    Ensure directory for log file exists.
    """
    file_path = _ensure_string(file_path, "file_path")
    directory = os.path.dirname(file_path)

    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def _build_formatter(fmt: str, datefmt: str) -> logging.Formatter:
    """
    Create a logging formatter.
    """
    return logging.Formatter(fmt=fmt, datefmt=datefmt)


def _attach_console_handler(
    logger: logging.Logger,
    handler_level: int,
    fmt: str,
    datefmt: str,
) -> None:
    """
    Attach a console handler to the logger.
    """
    console_handler = logging.StreamHandler()
    console_handler.set_name(CONSOLE_HANDLER_NAME)
    console_handler.setLevel(handler_level)
    console_handler.setFormatter(_build_formatter(fmt, datefmt))
    logger.addHandler(console_handler)


def _attach_file_handler(
    logger: logging.Logger,
    file_path: str,
    handler_level: int,
    fmt: str,
    datefmt: str,
) -> None:
    """
    Attach a file handler to the logger.
    """
    _ensure_log_directory(file_path)

    file_handler = logging.FileHandler(
        filename=file_path,
        mode=LOG_FILE_MODE,
        encoding=LOG_FILE_ENCODING,
    )
    file_handler.set_name(FILE_HANDLER_NAME)
    file_handler.setLevel(handler_level)
    file_handler.setFormatter(_build_formatter(fmt, datefmt))
    logger.addHandler(file_handler)


def _disable_logger(logger: logging.Logger) -> logging.Logger:
    """
    Disable logging cleanly for the project logger.
    """
    logger.disabled = True
    logger.propagate = False
    return logger


# ============================================================
# Setup logic
# ============================================================

def setup_logger(mode: str = DEFAULT_LOGGING_MODE) -> logging.Logger:
    """
    Initialize the root project logger once.

    This sets:
    - log level
    - console handler
    - optional file handler

    Safe to call multiple times.
    """
    global _LOGGER_INITIALIZED
    global _INITIALIZED_MODE

    logger = logging.getLogger(LOGGER_NAME)

    if not ENABLE_LOGGING:
        return _disable_logger(logger)

    if _LOGGER_INITIALIZED:
        if WARN_ON_REPEATED_SETUP and _INITIALIZED_MODE != mode:
            logger.warning(
                "Logger already initialized in mode '%s'; requested mode '%s' ignored.",
                _INITIALIZED_MODE,
                mode,
            )
        return logger

    settings = build_logging_settings(mode)

    try:
        logger.disabled = False
        logger.setLevel(settings["resolved_log_level"])
        logger.propagate = ENABLE_LOGGER_PROPAGATION

        if CLEAR_EXISTING_HANDLERS_ON_SETUP and logger.handlers:
            logger.handlers.clear()

        if ENABLE_CONSOLE_LOGGING:
            _attach_console_handler(
                logger=logger,
                handler_level=DEFAULT_HANDLER_LEVEL,
                fmt=settings["console_format"],
                datefmt=settings["date_format"],
            )

        if ENABLE_FILE_LOGGING:
            _attach_file_handler(
                logger=logger,
                file_path=settings["log_file_path"],
                handler_level=DEFAULT_HANDLER_LEVEL,
                fmt=settings["file_format"],
                datefmt=settings["date_format"],
            )

        _LOGGER_INITIALIZED = True
        _INITIALIZED_MODE = mode

        if SHOW_DEBUG_BANNER:
            logger.debug(
                "Logger initialized | mode=%s | level=%s | console=%s | file=%s",
                mode,
                settings["resolved_log_level"],
                ENABLE_CONSOLE_LOGGING,
                ENABLE_FILE_LOGGING,
            )
        else:
            logger.info("Logger initialized successfully")

    except Exception as exc:
        if RAISE_ON_LOG_SETUP_ERROR:
            raise

        print(f"[LOGGER ERROR] Failed to initialize logger: {exc}")

    return logger


# ============================================================
# Public access
# ============================================================

def get_logger(name: Optional[str] = None, mode: str = DEFAULT_LOGGING_MODE) -> logging.Logger:
    """
    Get the project logger or a child logger.

    Examples:
        logger = get_logger()
        logger = get_logger(__name__)
    """
    base_logger = setup_logger(mode=mode)

    if not name:
        return base_logger

    child_name = _clean_child_logger_name(name)
    if not child_name:
        return base_logger

    return base_logger.getChild(child_name)


def is_logger_initialized() -> bool:
    """
    Return True if the project logger has been initialized.
    """
    return _LOGGER_INITIALIZED


def reset_logger_state() -> None:
    """
    Reset internal initialization state.

    Useful mainly for tests.
    """
    global _LOGGER_INITIALIZED
    global _INITIALIZED_MODE

    logger = logging.getLogger(LOGGER_NAME)

    for handler in list(logger.handlers):
        try:
            handler.close()
        finally:
            logger.removeHandler(handler)

    logger.disabled = False
    _LOGGER_INITIALIZED = False
    _INITIALIZED_MODE = None


# ============================================================
# Convenience wrappers
# ============================================================

def log_debug(msg: str, *args, **kwargs) -> None:
    get_logger().debug(msg, *args, **kwargs)


def log_info(msg: str, *args, **kwargs) -> None:
    get_logger().info(msg, *args, **kwargs)


def log_warning(msg: str, *args, **kwargs) -> None:
    get_logger().warning(msg, *args, **kwargs)


def log_error(msg: str, *args, **kwargs) -> None:
    get_logger().error(msg, *args, **kwargs)


def log_exception(msg: str, *args, **kwargs) -> None:
    get_logger().exception(msg, *args, **kwargs)