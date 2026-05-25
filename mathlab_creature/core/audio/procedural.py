# File: mathlab_creature/core/audio/procedural.py

"""
Procedural Audio Generators
mathlab-mylinehub-creature

Purpose:
- procedural sound synthesis
- expressive mascot motion audio
- soft cinematic educational sound design
- reusable action sound generators
- lightweight runtime synthesis
- future-ready sound layering system

Sound Design Goals:
- alive but not annoying
- soft and expressive
- subtle Pixar-style support
- educational rhythm
- minimal and elegant
- never overpower visuals

IMPORTANT:
This module should ONLY:
- generate procedural sounds
- synthesize motion audio
- trigger short-lived audio events

DO NOT:
- boot pyo server
- manage audio lifecycle
- manage scene timing
- directly control animation flow
"""

from __future__ import annotations

import random
from typing import List

from mathlab_creature.core.logger import get_logger

from mathlab_creature.core.audio.audio_config import (
    AUDIO_ENABLED,
    MASTER_VOLUME,
    WALK_VOLUME,
    BLINK_VOLUME,
    WAVE_VOLUME,
    HOP_VOLUME,
    POINT_VOLUME,
    LOOK_VOLUME,
    TURN_VOLUME,
    WALK_BASE_FREQUENCY,
    WALK_PITCH_VARIATION,
    WALK_VOLUME_VARIATION,
    BLINK_BASE_FREQUENCY,
    BLINK_NOISE_AMOUNT,
    HOP_BASE_FREQUENCY,
    HOP_LANDING_FREQUENCY,
    WAVE_SWISH_FREQUENCY,
    WAVE_NOISE_AMOUNT,
    POINT_CLICK_FREQUENCY,
    LOOK_SWEEP_FREQUENCY,
    TURN_SWEEP_FREQUENCY,
    DEFAULT_ATTACK,
    DEFAULT_RELEASE,
)

from mathlab_creature.core.audio.audio_server import (
    boot_audio_server,
    get_audio_server,
)

logger = get_logger(__name__)


# ============================================================
# OPTIONAL PYO IMPORT
# ============================================================

PYO_AVAILABLE = False

try:
    from pyo import (
        Fader,
        Sine,
        Noise,
        ButLP,
        Pan,
        Adsr,
    )

    PYO_AVAILABLE = True

except Exception as exc:
    logger.warning(
        "Pyo procedural audio unavailable. Reason: %s",
        exc,
    )


# ============================================================
# INTERNAL HELPERS
# ============================================================


def _audio_ready() -> bool:
    """
    Ensures audio system is available and booted.
    """

    if not AUDIO_ENABLED:
        return False

    if not PYO_AVAILABLE:
        return False

    server = get_audio_server()

    if server is None:
        server = boot_audio_server()

    return server is not None


def _random_pan() -> float:
    """
    Small stereo randomness for life-like feel.
    """

    return random.uniform(0.35, 0.65)


def _safe_out(audio_object):
    """
    Safely outputs audio object.
    """

    try:
        audio_object.out()

    except Exception as exc:
        logger.debug("Audio output failed: %s", exc)


# ============================================================
# WALK SOUND
# ============================================================


def play_walk_step(
    volume: float = WALK_VOLUME,
    frequency: float = WALK_BASE_FREQUENCY,
) -> List:
    """
    Soft mascot footstep sound.

    Design:
    - soft low sine
    - tiny transient
    - slight pitch randomness
    - soft envelope
    """

    if not _audio_ready():
        return []

    pitch = frequency + random.uniform(
        -WALK_PITCH_VARIATION,
        WALK_PITCH_VARIATION,
    )

    amp = volume + random.uniform(
        -WALK_VOLUME_VARIATION,
        WALK_VOLUME_VARIATION,
    )

    env = Fader(
        fadein=0.002,
        fadeout=0.08,
        dur=0.12,
        mul=amp * MASTER_VOLUME,
    ).play()

    body = Sine(
        freq=pitch,
        mul=env * 0.8,
    )

    transient_noise = ButLP(
        Noise(mul=env * 0.08),
        freq=450,
    )

    stereo = Pan(
        body + transient_noise,
        outs=2,
        pan=_random_pan(),
    )

    _safe_out(stereo)

    return [env, body, transient_noise, stereo]


# ============================================================
# BLINK SOUND
# ============================================================


def play_blink_sound(
    volume: float = BLINK_VOLUME,
) -> List:
    """
    Tiny cute blink sound.

    Design:
    - tiny airy transient
    - subtle high sine
    - extremely lightweight
    """

    if not _audio_ready():
        return []

    env = Fader(
        fadein=0.001,
        fadeout=0.03,
        dur=0.04,
        mul=volume * MASTER_VOLUME,
    ).play()

    tone = Sine(
        freq=BLINK_BASE_FREQUENCY + random.uniform(-40, 40),
        mul=env * 0.12,
    )

    noise = ButLP(
        Noise(mul=env * BLINK_NOISE_AMOUNT),
        freq=3000,
    )

    stereo = Pan(
        tone + noise,
        outs=2,
        pan=_random_pan(),
    )

    _safe_out(stereo)

    return [env, tone, noise, stereo]


# ============================================================
# WAVE SOUND
# ============================================================


def play_wave_sound(
    volume: float = WAVE_VOLUME,
) -> List:
    """
    Soft hand wave whoosh.

    Design:
    - airy movement
    - soft filtered noise
    - light tonal support
    """

    if not _audio_ready():
        return []

    env = Adsr(
        attack=0.01,
        decay=0.03,
        sustain=0.2,
        release=0.12,
        dur=0.22,
        mul=volume * MASTER_VOLUME,
    ).play()

    whoosh = ButLP(
        Noise(mul=env * WAVE_NOISE_AMOUNT),
        freq=WAVE_SWISH_FREQUENCY,
    )

    shimmer = Sine(
        freq=900 + random.uniform(-50, 50),
        mul=env * 0.05,
    )

    stereo = Pan(
        whoosh + shimmer,
        outs=2,
        pan=_random_pan(),
    )

    _safe_out(stereo)

    return [env, whoosh, shimmer, stereo]


# ============================================================
# HOP SOUND
# ============================================================


def play_hop_sound(
    volume: float = HOP_VOLUME,
) -> List:
    """
    Soft springy hop sound.

    Design:
    - upward playful tone
    - soft landing body
    - subtle cartoon elasticity
    """

    if not _audio_ready():
        return []

    env = Adsr(
        attack=0.005,
        decay=0.04,
        sustain=0.3,
        release=0.15,
        dur=0.28,
        mul=volume * MASTER_VOLUME,
    ).play()

    spring = Sine(
        freq=[
            HOP_BASE_FREQUENCY,
            HOP_BASE_FREQUENCY * 1.5,
        ],
        mul=env * 0.18,
    )

    landing = Sine(
        freq=HOP_LANDING_FREQUENCY,
        mul=env * 0.12,
    )

    stereo = Pan(
        spring + landing,
        outs=2,
        pan=_random_pan(),
    )

    _safe_out(stereo)

    return [env, spring, landing, stereo]


# ============================================================
# POINT SOUND
# ============================================================


def play_point_sound(
    volume: float = POINT_VOLUME,
) -> List:
    """
    Educational cue / point sound.

    Design:
    - tiny click
    - subtle focus tone
    - attention guidance
    """

    if not _audio_ready():
        return []

    env = Fader(
        fadein=0.001,
        fadeout=0.06,
        dur=0.08,
        mul=volume * MASTER_VOLUME,
    ).play()

    click = Sine(
        freq=POINT_CLICK_FREQUENCY,
        mul=env * 0.15,
    )

    stereo = Pan(
        click,
        outs=2,
        pan=_random_pan(),
    )

    _safe_out(stereo)

    return [env, click, stereo]


# ============================================================
# LOOK SOUND
# ============================================================


def play_look_sound(
    volume: float = LOOK_VOLUME,
) -> List:
    """
    Tiny focus movement sound.

    Design:
    - gentle sweep
    - subtle movement cue
    """

    if not _audio_ready():
        return []

    env = Fader(
        fadein=0.002,
        fadeout=0.04,
        dur=0.06,
        mul=volume * MASTER_VOLUME,
    ).play()

    sweep = Sine(
        freq=LOOK_SWEEP_FREQUENCY + random.uniform(-25, 25),
        mul=env * 0.08,
    )

    stereo = Pan(
        sweep,
        outs=2,
        pan=_random_pan(),
    )

    _safe_out(stereo)

    return [env, sweep, stereo]


# ============================================================
# TURN SOUND
# ============================================================


def play_turn_sound(
    volume: float = TURN_VOLUME,
) -> List:
    """
    Directional swipe sound.

    Design:
    - soft turning sweep
    - lightweight movement support
    """

    if not _audio_ready():
        return []

    env = Adsr(
        attack=0.01,
        decay=0.04,
        sustain=0.15,
        release=0.08,
        dur=0.16,
        mul=volume * MASTER_VOLUME,
    ).play()

    sweep = Sine(
        freq=TURN_SWEEP_FREQUENCY + random.uniform(-40, 40),
        mul=env * 0.10,
    )

    noise = ButLP(
        Noise(mul=env * 0.03),
        freq=1200,
    )

    stereo = Pan(
        sweep + noise,
        outs=2,
        pan=_random_pan(),
    )

    _safe_out(stereo)

    return [env, sweep, noise, stereo]


# ============================================================
# GENERIC UI SOUND
# ============================================================


def play_ui_confirm_sound() -> List:
    """
    Generic UI confirmation sound.
    """

    if not _audio_ready():
        return []

    env = Fader(
        fadein=0.001,
        fadeout=0.08,
        dur=0.10,
        mul=0.15 * MASTER_VOLUME,
    ).play()

    tone = Sine(
        freq=[660, 880],
        mul=env * 0.08,
    )

    stereo = Pan(
        tone,
        outs=2,
        pan=0.5,
    )

    _safe_out(stereo)

    return [env, tone, stereo]


# ============================================================
# MODULE READY
# ============================================================

logger.debug("procedural audio module initialized.")