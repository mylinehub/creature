# File: mathlab_creature/scenes/tests/test_procedural_audio_scene.py

"""
mathlab_creature/scenes/tests/test_procedural_audio_scene.py

PROCEDURAL AUDIO SYSTEM VALIDATION

Purpose
-------
Tests:
- procedural sound generation
- envelope shaping
- timing systems
- sound layering
- stereo feel
- procedural synthesis stability
- safe playback behavior
- sound rhythm consistency

This scene validates:
- procedural audio quality
- procedural audio architecture
- pyo synthesis pipeline
- layered sound behavior

IMPORTANT
---------
This is NOT:
- animation testing
- locomotion testing
- camera testing
- rig testing

This scene focuses ONLY on:
PROCEDURAL AUDIO SYSTEMS.
"""

from __future__ import annotations

from manimlib import *

from mathlab_creature.core.audio.audio_server import (
    boot_audio_server,
    shutdown_audio_server,
)

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

from mathlab_creature.core.audio.timing import (
    schedule_step_sounds,
    schedule_blink_sound,
    schedule_wave_sound,
    schedule_hop_sound,
    schedule_point_sound,
    schedule_look_sound,
    schedule_turn_sound,
    schedule_rhythm_pattern,
)

from mathlab_creature.core.logger import (
    get_logger,
)

logger = get_logger(__name__)


# =========================================================
# SCENE
# =========================================================

class TestProceduralAudioScene(Scene):
    """
    Procedural synthesis validation scene.
    """

    def construct(self):

        logger.info(
            "Starting TestProceduralAudioScene"
        )

        # =================================================
        # AUDIO BOOT
        # =================================================

        boot_audio_server()

        # =================================================
        # TITLE
        # =================================================

        title = Text(
            "PROCEDURAL AUDIO TEST",
            font_size=36,
        )

        title.to_edge(UP)

        self.play(
            FadeIn(title)
        )

        self.wait(0.5)

        # =================================================
        # TEST 1
        # BASIC GENERATION
        # =================================================

        label = Text(
            "Basic Procedural Generation",
            font_size=28,
        )

        label.move_to(UP * 2)

        self.play(
            FadeIn(label)
        )

        play_walk_step()

        self.wait(1)

        play_blink_sound()

        self.wait(1)

        play_wave_sound()

        self.wait(1)

        play_hop_sound()

        self.wait(1)

        self.play(
            FadeOut(label)
        )

        # =================================================
        # TEST 2
        # ENVELOPE SHAPING
        # =================================================

        label = Text(
            "Envelope Validation",
            font_size=28,
        )

        label.move_to(UP * 2)

        self.play(
            FadeIn(label)
        )

        # -------------------------------------------------
        # SOFT ENVELOPES
        # -------------------------------------------------

        play_walk_step(
            frequency=95,
            volume=0.4,
        )

        self.wait(0.5)

        play_walk_step(
            frequency=110,
            volume=0.5,
        )

        self.wait(0.5)

        play_walk_step(
            frequency=130,
            volume=0.6,
        )

        self.wait(1)

        self.play(
            FadeOut(label)
        )

        # =================================================
        # TEST 3
        # TIMING VALIDATION
        # =================================================

        label = Text(
            "Timing Synchronization",
            font_size=28,
        )

        label.move_to(UP * 2)

        self.play(
            FadeIn(label)
        )

        # -------------------------------------------------
        # STEP RHYTHM
        # -------------------------------------------------

        schedule_step_sounds(
            cycles=4,
            step_interval=0.32,
            with_sound=True,
        )

        self.wait(4)

        self.play(
            FadeOut(label)
        )

        # =================================================
        # TEST 4
        # RHYTHM PATTERN
        # =================================================

        label = Text(
            "Rhythmic Sound Pattern",
            font_size=28,
        )

        label.move_to(UP * 2)

        self.play(
            FadeIn(label)
        )

        schedule_rhythm_pattern(
            play_point_sound,
            [
                0.0,
                0.25,
                0.5,
                0.75,
                1.0,
            ],
            with_sound=True,
        )

        self.wait(2)

        self.play(
            FadeOut(label)
        )

        # =================================================
        # TEST 5
        # SOUND LAYERING
        # =================================================

        label = Text(
            "Layered Procedural Audio",
            font_size=28,
        )

        label.move_to(UP * 2)

        self.play(
            FadeIn(label)
        )

        # -------------------------------------------------
        # MULTI-LAYER STACK
        # -------------------------------------------------

        play_walk_step(
            frequency=105,
            volume=0.45,
        )

        play_wave_sound(
            volume=0.22,
        )

        play_look_sound(
            volume=0.10,
        )

        self.wait(2)

        # -------------------------------------------------
        # SECOND LAYER
        # -------------------------------------------------

        play_hop_sound(
            volume=0.45,
        )

        play_point_sound(
            volume=0.18,
        )

        self.wait(2)

        self.play(
            FadeOut(label)
        )

        # =================================================
        # TEST 6
        # STEREO FEEL
        # =================================================

        label = Text(
            "Stereo Procedural Feel",
            font_size=28,
        )

        label.move_to(UP * 2)

        self.play(
            FadeIn(label)
        )

        for _ in range(6):

            play_walk_step()

            self.wait(0.25)

        self.wait(1)

        self.play(
            FadeOut(label)
        )

        # =================================================
        # TEST 7
        # UI CONFIRMATION
        # =================================================

        label = Text(
            "UI Audio Cue",
            font_size=28,
        )

        label.move_to(UP * 2)

        self.play(
            FadeIn(label)
        )

        play_ui_confirm_sound()

        self.wait(1)

        self.play(
            FadeOut(label)
        )

        # =================================================
        # TEST 8
        # SEQUENTIAL TIMING
        # =================================================

        label = Text(
            "Sequential Audio Timing",
            font_size=28,
        )

        label.move_to(UP * 2)

        self.play(
            FadeIn(label)
        )

        schedule_blink_sound(
            delay=0.0,
            with_sound=True,
        )

        schedule_look_sound(
            delay=0.25,
            with_sound=True,
        )

        schedule_point_sound(
            delay=0.5,
            with_sound=True,
        )

        schedule_wave_sound(
            delay=0.75,
            with_sound=True,
        )

        schedule_hop_sound(
            delay=1.0,
            with_sound=True,
        )

        schedule_turn_sound(
            delay=1.25,
            with_sound=True,
        )

        self.wait(3)

        self.play(
            FadeOut(label)
        )

        # =================================================
        # TEST 9
        # MASCOT SOUND FEEL
        # =================================================

        label = Text(
            "Soft Mascot Audio Feel",
            font_size=28,
        )

        label.move_to(UP * 2)

        self.play(
            FadeIn(label)
        )

        for _ in range(3):

            play_walk_step(
                frequency=102,
                volume=0.35,
            )

            self.wait(0.32)

            play_walk_step(
                frequency=116,
                volume=0.35,
            )

            self.wait(0.32)

        play_blink_sound()

        self.wait(0.5)

        play_wave_sound(
            volume=0.18,
        )

        self.wait(2)

        self.play(
            FadeOut(label)
        )

        # =================================================
        # SUCCESS
        # =================================================

        success = Text(
            "PROCEDURAL AUDIO VALID",
            font_size=34,
        )

        success.move_to(
            DOWN * 2
        )

        self.play(
            FadeIn(success)
        )

        self.wait(2)

        # =================================================
        # AUDIO SHUTDOWN
        # =================================================

        shutdown_audio_server()

        logger.info(
            "Finished TestProceduralAudioScene"
        )

        self.wait(1)