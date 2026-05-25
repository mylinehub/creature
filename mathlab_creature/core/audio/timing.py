# File: mathlab_creature/core/audio/timing.py

"""
Audio Timing Synchronization
mathlab-mylinehub-creature

Purpose:
- synchronize sounds with animation rhythm
- align procedural audio with actions
- provide reusable scheduling helpers
- support cinematic timing flow
- support future timeline systems
- support future editor integrations

This module helps coordinate:
- footsteps
- blinks
- gestures
- hops
- teaching cues
- scene pacing

IMPORTANT:
This module should:
- schedule sound playback
- coordinate timing
- provide reusable rhythm helpers

This module should NOT:
- generate procedural synthesis
- boot audio server
- contain animation logic
"""

from __future__ import annotations

import threading
import time
from typing import Callable, List, Optional

from mathlab_creature.core.logger import get_logger

from mathlab_creature.core.audio.helpers import (
    maybe_play_sound,
)

from mathlab_creature.core.audio.procedural import (
    play_walk_step,
    play_blink_sound,
    play_wave_sound,
    play_hop_sound,
    play_point_sound,
    play_look_sound,
    play_turn_sound,
)

logger = get_logger(__name__)


# ============================================================
# INTERNAL THREAD TRACKING
# ============================================================

_active_threads: List[threading.Thread] = []


# ============================================================
# INTERNAL HELPERS
# ============================================================


def _run_delayed(
    delay: float,
    callback: Callable,
    *args,
    **kwargs,
) -> threading.Thread:
    """
    Executes callback after delay using daemon thread.
    """

    def worker():

        try:
            time.sleep(max(0.0, delay))
            callback(*args, **kwargs)

        except Exception as exc:

            logger.debug(
                "Audio timing worker failed: %s",
                exc,
            )

    thread = threading.Thread(
        target=worker,
        daemon=True,
    )

    thread.start()

    _active_threads.append(thread)

    return thread


# ============================================================
# GENERIC SCHEDULER
# ============================================================


def schedule_sound(
    delay: float,
    sound_callable: Callable,
    *args,
    **kwargs,
) -> Optional[threading.Thread]:
    """
    Schedules any sound callback.

    Example:
        schedule_sound(
            0.2,
            play_walk_step,
        )
    """

    try:
        return _run_delayed(
            delay,
            sound_callable,
            *args,
            **kwargs,
        )

    except Exception as exc:

        logger.debug(
            "Failed to schedule sound: %s",
            exc,
        )

        return None


# ============================================================
# WALK TIMING
# ============================================================


def schedule_step_sounds(
    cycles: int = 2,
    step_interval: float = 0.32,
    with_sound: bool = True,
) -> List[threading.Thread]:
    """
    Schedules synchronized footstep sounds.

    Designed for:
    - mascot walk cycles
    - educational pacing
    - soft cinematic rhythm

    Args:
        cycles:
            Number of walk cycles.

        step_interval:
            Time between footsteps.

        with_sound:
            Enables/disables sound safely.
    """

    threads = []

    total_steps = max(1, cycles * 2)

    for step_index in range(total_steps):

        delay = step_index * step_interval

        thread = schedule_sound(
            delay,
            maybe_play_sound,
            with_sound,
            play_walk_step,
        )

        if thread is not None:
            threads.append(thread)

    return threads


# ============================================================
# BLINK TIMING
# ============================================================


def schedule_blink_sound(
    delay: float = 0.0,
    with_sound: bool = True,
) -> Optional[threading.Thread]:
    """
    Schedules blink sound.
    """

    return schedule_sound(
        delay,
        maybe_play_sound,
        with_sound,
        play_blink_sound,
    )


# ============================================================
# WAVE TIMING
# ============================================================


def schedule_wave_sound(
    delay: float = 0.0,
    with_sound: bool = True,
) -> Optional[threading.Thread]:
    """
    Schedules wave gesture sound.
    """

    return schedule_sound(
        delay,
        maybe_play_sound,
        with_sound,
        play_wave_sound,
    )


# ============================================================
# HOP TIMING
# ============================================================


def schedule_hop_sound(
    delay: float = 0.0,
    with_sound: bool = True,
) -> Optional[threading.Thread]:
    """
    Schedules hop sound.
    """

    return schedule_sound(
        delay,
        maybe_play_sound,
        with_sound,
        play_hop_sound,
    )


# ============================================================
# POINT TIMING
# ============================================================


def schedule_point_sound(
    delay: float = 0.0,
    with_sound: bool = True,
) -> Optional[threading.Thread]:
    """
    Schedules point cue sound.
    """

    return schedule_sound(
        delay,
        maybe_play_sound,
        with_sound,
        play_point_sound,
    )


# ============================================================
# LOOK TIMING
# ============================================================


def schedule_look_sound(
    delay: float = 0.0,
    with_sound: bool = True,
) -> Optional[threading.Thread]:
    """
    Schedules focus/look sound.
    """

    return schedule_sound(
        delay,
        maybe_play_sound,
        with_sound,
        play_look_sound,
    )


# ============================================================
# TURN TIMING
# ============================================================


def schedule_turn_sound(
    delay: float = 0.0,
    with_sound: bool = True,
) -> Optional[threading.Thread]:
    """
    Schedules turn/swipe sound.
    """

    return schedule_sound(
        delay,
        maybe_play_sound,
        with_sound,
        play_turn_sound,
    )


# ============================================================
# RHYTHM HELPERS
# ============================================================


def schedule_rhythm_pattern(
    sound_callable: Callable,
    beat_times: List[float],
    with_sound: bool = True,
) -> List[threading.Thread]:
    """
    Schedules rhythmic sound patterns.

    Useful for:
    - dance timing
    - educational beats
    - gesture choreography
    - cinematic pacing

    Example:

        schedule_rhythm_pattern(
            play_walk_step,
            [0.0, 0.2, 0.4, 0.6],
        )
    """

    threads = []

    for beat_time in beat_times:

        thread = schedule_sound(
            beat_time,
            maybe_play_sound,
            with_sound,
            sound_callable,
        )

        if thread is not None:
            threads.append(thread)

    return threads


# ============================================================
# CLEANUP
# ============================================================


def cleanup_finished_threads() -> None:
    """
    Removes completed timing threads.
    """

    global _active_threads

    _active_threads = [
        thread
        for thread in _active_threads
        if thread.is_alive()
    ]


def get_active_thread_count() -> int:
    """
    Returns number of active timing threads.
    """

    cleanup_finished_threads()

    return len(_active_threads)


# ============================================================
# MODULE READY
# ============================================================

logger.debug("audio timing system initialized.")