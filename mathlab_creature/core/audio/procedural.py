# File: mathlab_creature/core/audio/procedural.py

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
    HOP_BASE_FREQUENCY,
    HOP_LANDING_FREQUENCY,
)

from mathlab_creature.core.audio.audio_server import (
    boot_audio_server,
    get_audio_server,
)

logger = get_logger(__name__)

PYO_AVAILABLE = False

try:

    from pyo import (
        Fader,
        Sine,
        Noise,
        ButLP,
        Pan,
        Adsr,
        CallAfter,
        Compress,
    )

    PYO_AVAILABLE = True

except Exception as exc:

    logger.warning(
        "Pyo procedural audio unavailable. Reason: %s",
        exc,
    )


_ACTIVE_AUDIO_OBJECTS: List = []


# ============================================================
# HELPERS
# ============================================================


def _audio_ready() -> bool:

    if not AUDIO_ENABLED:
        return False

    if not PYO_AVAILABLE:
        return False

    server = get_audio_server()

    if server is None:
        server = boot_audio_server()

    return server is not None


def _retain_audio(
    objects: List,
    duration: float,
):

    _ACTIVE_AUDIO_OBJECTS.extend(objects)

    def _cleanup():

        for obj in objects:

            try:

                if obj in _ACTIVE_AUDIO_OBJECTS:
                    _ACTIVE_AUDIO_OBJECTS.remove(obj)

            except Exception:
                pass

    try:
        CallAfter(_cleanup, duration)

    except Exception:
        pass


def _safe_out(audio_object):

    try:
        audio_object.out()

    except Exception as exc:

        logger.debug(
            "Audio output failed: %s",
            exc,
        )


def _compress(signal):

    return Compress(
        signal,
        thresh=-18,
        ratio=4,
        risetime=0.005,
        falltime=0.10,
    )


# ============================================================
# WALK SOUND
# ============================================================


def play_walk_step(
    volume: float = WALK_VOLUME,
    frequency: float = WALK_BASE_FREQUENCY,
) -> List:

    if not _audio_ready():
        return []

    amp = volume * 60.0 * MASTER_VOLUME

    env = Adsr(
        attack=0.018,
        decay=0.12,
        sustain=0.62,
        release=0.42,
        dur=0.90,
        mul=amp,
    ).play()

    body = Sine(
        freq=[
            frequency,
            frequency * 1.25,
            frequency * 1.8,
        ],
        mul=env * 0.95,
    )

    sub = Sine(
        freq=frequency * 0.5,
        mul=env * 0.35,
    )

    texture = ButLP(
        Noise(
            mul=env * 0.0015,
        ),
        freq=80,
    )

    signal = _compress(
        body + sub + texture
    )

    stereo = Pan(
        signal,
        outs=2,
        pan=0.5,
    )

    _safe_out(stereo)

    objects = [
        env,
        body,
        sub,
        texture,
        signal,
        stereo,
    ]

    _retain_audio(objects, duration=2.0)

    return objects


# ============================================================
# BLINK SOUND
# ============================================================


def play_blink_sound(
    volume: float = BLINK_VOLUME,
) -> List:

    if not _audio_ready():
        return []

    amp = volume * 45.0 * MASTER_VOLUME

    env = Fader(
        fadein=0.03,
        fadeout=0.30,
        dur=0.70,
        mul=amp,
    ).play()

    tone = Sine(
        freq=[
            260,
            420,
        ],
        mul=env * 0.72,
    )

    signal = _compress(tone)

    stereo = Pan(
        signal,
        outs=2,
        pan=0.5,
    )

    _safe_out(stereo)

    objects = [
        env,
        tone,
        signal,
        stereo,
    ]

    _retain_audio(objects, duration=1.8)

    return objects


# ============================================================
# WAVE SOUND
# ============================================================


def play_wave_sound(
    volume: float = WAVE_VOLUME,
) -> List:

    if not _audio_ready():
        return []

    amp = volume * 40.0 * MASTER_VOLUME

    env = Adsr(
        attack=0.08,
        decay=0.18,
        sustain=0.55,
        release=0.55,
        dur=1.10,
        mul=amp,
    ).play()

    body = Sine(
        freq=[
            120,
            180,
            260,
        ],
        mul=env * 0.82,
    )

    air = ButLP(
        Noise(
            mul=env * 0.001,
        ),
        freq=60,
    )

    signal = _compress(
        body + air
    )

    stereo = Pan(
        signal,
        outs=2,
        pan=0.5,
    )

    _safe_out(stereo)

    objects = [
        env,
        body,
        air,
        signal,
        stereo,
    ]

    _retain_audio(objects, duration=2.2)

    return objects


# ============================================================
# HOP SOUND
# ============================================================


def play_hop_sound(
    volume: float = HOP_VOLUME,
) -> List:

    if not _audio_ready():
        return []

    amp = volume * 40.0 * MASTER_VOLUME

    env = Adsr(
        attack=0.03,
        decay=0.12,
        sustain=0.70,
        release=0.65,
        dur=1.20,
        mul=amp,
    ).play()

    spring = Sine(
        freq=[
            HOP_BASE_FREQUENCY,
            HOP_BASE_FREQUENCY * 1.3,
            HOP_BASE_FREQUENCY * 2.0,
        ],
        mul=env * 0.92,
    )

    landing = Sine(
        freq=HOP_LANDING_FREQUENCY,
        mul=env * 0.42,
    )

    signal = _compress(
        spring + landing
    )

    stereo = Pan(
        signal,
        outs=2,
        pan=0.5,
    )

    _safe_out(stereo)

    objects = [
        env,
        spring,
        landing,
        signal,
        stereo,
    ]

    _retain_audio(objects, duration=2.4)

    return objects


# ============================================================
# POINT SOUND
# ============================================================


def play_point_sound(
    volume: float = POINT_VOLUME,
) -> List:

    if not _audio_ready():
        return []

    amp = volume * 70.0 * MASTER_VOLUME

    env = Fader(
        fadein=0.03,
        fadeout=0.40,
        dur=1.00,
        mul=amp,
    ).play()

    click = Sine(
        freq=[
            180,
            260,
            360,
        ],
        mul=env * 1.00,
    )

    signal = _compress(click)

    stereo = Pan(
        signal,
        outs=2,
        pan=0.5,
    )

    _safe_out(stereo)

    objects = [
        env,
        click,
        signal,
        stereo,
    ]

    _retain_audio(objects, duration=2.4)

    return objects


# ============================================================
# LOOK SOUND
# ============================================================


def play_look_sound(
    volume: float = LOOK_VOLUME,
) -> List:

    if not _audio_ready():
        return []

    amp = volume * 36.0 * MASTER_VOLUME

    env = Fader(
        fadein=0.04,
        fadeout=0.30,
        dur=0.90,
        mul=amp,
    ).play()

    sweep = Sine(
        freq=[
            140,
            220,
        ],
        mul=env * 0.72,
    )

    signal = _compress(sweep)

    stereo = Pan(
        signal,
        outs=2,
        pan=0.5,
    )

    _safe_out(stereo)

    objects = [
        env,
        sweep,
        signal,
        stereo,
    ]

    _retain_audio(objects, duration=2.0)

    return objects


# ============================================================
# TURN SOUND
# ============================================================


def play_turn_sound(
    volume: float = TURN_VOLUME,
) -> List:

    if not _audio_ready():
        return []

    amp = volume * 40.0 * MASTER_VOLUME

    env = Adsr(
        attack=0.08,
        decay=0.16,
        sustain=0.55,
        release=0.50,
        dur=1.10,
        mul=amp,
    ).play()

    sweep = Sine(
        freq=[
            120,
            180,
            260,
        ],
        mul=env * 0.82,
    )

    air = ButLP(
        Noise(
            mul=env * 0.001,
        ),
        freq=80,
    )

    signal = _compress(
        sweep + air
    )

    stereo = Pan(
        signal,
        outs=2,
        pan=0.5,
    )

    _safe_out(stereo)

    objects = [
        env,
        sweep,
        air,
        signal,
        stereo,
    ]

    _retain_audio(objects, duration=2.3)

    return objects


# ============================================================
# UI SOUND
# ============================================================


def play_ui_confirm_sound() -> List:

    if not _audio_ready():
        return []

    env = Fader(
        fadein=0.03,
        fadeout=0.32,
        dur=1.00,
        mul=3.0 * MASTER_VOLUME,
    ).play()

    tone = Sine(
        freq=[
            220,
            340,
            520,
        ],
        mul=env * 0.72,
    )

    signal = _compress(tone)

    stereo = Pan(
        signal,
        outs=2,
        pan=0.5,
    )

    _safe_out(stereo)

    objects = [
        env,
        tone,
        signal,
        stereo,
    ]

    _retain_audio(objects, duration=2.4)

    return objects


logger.debug(
    "procedural audio module initialized."
)