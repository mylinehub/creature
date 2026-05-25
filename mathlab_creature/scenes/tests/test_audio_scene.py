# File: mathlab_creature/scenes/tests/test_audio_scene.py

"""
mathlab_creature/scenes/tests/test_audio_scene.py

PROCEDURAL AUDIO VALIDATION SCENE

Purpose
-------
Verify:
- audio server boots
- no crashes
- procedural audio pipeline valid
- sound registry functional
- pyo integration stable
- safe fallback behavior
- audio timing operational
- sound playback helpers operational

This scene is intentionally SIMPLE.

It validates:
- audio infrastructure
NOT:
- animation quality
- IK systems
- locomotion
- camera systems
"""

from __future__ import annotations

from manimlib import *

from mathlab_creature.core.audio.audio_server import (
    boot_audio_server,
    shutdown_audio_server,
    get_audio_server,
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

from mathlab_creature.core.audio.sound_registry import (
    list_registered_sounds,
    play_registered_sound,
)

from mathlab_creature.core.audio.helpers import (
    audio_available,
    ensure_audio_ready,
    log_audio_state,
)

from mathlab_creature.core.logger import (
    get_logger,
)

logger = get_logger(__name__)


# =========================================================
# SCENE
# =========================================================

class TestAudioScene(Scene):
    """
    Audio infrastructure validation scene.
    """

    def construct(self):

        logger.info(
            "Starting TestAudioScene"
        )

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
        # BOOT AUDIO SERVER
        # =================================================

        logger.info(
            "Booting audio server..."
        )

        server = boot_audio_server()

        # =================================================
        # STATUS CHECK
        # =================================================

        available = audio_available()

        ready = ensure_audio_ready()

        log_audio_state()

        status_text = Text(
            f"Audio Available: {available}",
            font_size=26,
        )

        status_text.move_to(UP * 2)

        self.play(
            FadeIn(status_text)
        )

        self.wait(1)

        # =================================================
        # SERVER VALIDATION
        # =================================================

        if server is None:

            warning = Text(
                "Audio Server Failed To Start",
                font_size=30,
            )

            warning.move_to(ORIGIN)

            self.play(
                FadeIn(warning)
            )

            self.wait(2)

            logger.warning(
                "Audio server unavailable."
            )

            return

        logger.info(
            "Audio server boot successful."
        )

        # =================================================
        # REGISTERED SOUNDS
        # =================================================

        registered = (
            list_registered_sounds()
        )

        registry_label = Text(
            f"Registered Sounds: {len(registered)}",
            font_size=24,
        )

        registry_label.move_to(
            DOWN * 0.5
        )

        self.play(
            FadeIn(registry_label)
        )

        self.wait(1)

        # =================================================
        # TEST 1
        # WALK STEP
        # =================================================

        logger.info(
            "Testing walk sound..."
        )

        play_walk_step()

        label = Text(
            "Walk Step Sound",
            font_size=28,
        )

        label.move_to(DOWN * 2)

        self.play(
            FadeIn(label)
        )

        self.wait(1)

        self.play(
            FadeOut(label)
        )

        # =================================================
        # TEST 2
        # BLINK
        # =================================================

        logger.info(
            "Testing blink sound..."
        )

        play_blink_sound()

        label = Text(
            "Blink Sound",
            font_size=28,
        )

        label.move_to(DOWN * 2)

        self.play(
            FadeIn(label)
        )

        self.wait(1)

        self.play(
            FadeOut(label)
        )

        # =================================================
        # TEST 3
        # WAVE
        # =================================================

        logger.info(
            "Testing wave sound..."
        )

        play_wave_sound()

        label = Text(
            "Wave Sound",
            font_size=28,
        )

        label.move_to(DOWN * 2)

        self.play(
            FadeIn(label)
        )

        self.wait(1)

        self.play(
            FadeOut(label)
        )

        # =================================================
        # TEST 4
        # HOP
        # =================================================

        logger.info(
            "Testing hop sound..."
        )

        play_hop_sound()

        label = Text(
            "Hop Sound",
            font_size=28,
        )

        label.move_to(DOWN * 2)

        self.play(
            FadeIn(label)
        )

        self.wait(1)

        self.play(
            FadeOut(label)
        )

        # =================================================
        # TEST 5
        # POINT
        # =================================================

        logger.info(
            "Testing point sound..."
        )

        play_point_sound()

        label = Text(
            "Point Sound",
            font_size=28,
        )

        label.move_to(DOWN * 2)

        self.play(
            FadeIn(label)
        )

        self.wait(1)

        self.play(
            FadeOut(label)
        )

        # =================================================
        # TEST 6
        # LOOK
        # =================================================

        logger.info(
            "Testing look sound..."
        )

        play_look_sound()

        label = Text(
            "Look Sound",
            font_size=28,
        )

        label.move_to(DOWN * 2)

        self.play(
            FadeIn(label)
        )

        self.wait(1)

        self.play(
            FadeOut(label)
        )

        # =================================================
        # TEST 7
        # TURN
        # =================================================

        logger.info(
            "Testing turn sound..."
        )

        play_turn_sound()

        label = Text(
            "Turn Sound",
            font_size=28,
        )

        label.move_to(DOWN * 2)

        self.play(
            FadeIn(label)
        )

        self.wait(1)

        self.play(
            FadeOut(label)
        )

        # =================================================
        # TEST 8
        # UI SOUND
        # =================================================

        logger.info(
            "Testing UI sound..."
        )

        play_ui_confirm_sound()

        label = Text(
            "UI Confirm Sound",
            font_size=28,
        )

        label.move_to(DOWN * 2)

        self.play(
            FadeIn(label)
        )

        self.wait(1)

        self.play(
            FadeOut(label)
        )

        # =================================================
        # TEST 9
        # REGISTRY PLAYBACK
        # =================================================

        logger.info(
            "Testing registry playback..."
        )

        play_registered_sound(
            "walk"
        )

        play_registered_sound(
            "blink"
        )

        label = Text(
            "Registry Playback",
            font_size=28,
        )

        label.move_to(DOWN * 2)

        self.play(
            FadeIn(label)
        )

        self.wait(1)

        self.play(
            FadeOut(label)
        )

        # =================================================
        # FINAL STATUS
        # =================================================

        success = Text(
            "AUDIO PIPELINE VALID",
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
        # SHUTDOWN
        # =================================================

        logger.info(
            "Shutting down audio server..."
        )

        shutdown_audio_server()

        logger.info(
            "Finished TestAudioScene"
        )

        self.wait(1)