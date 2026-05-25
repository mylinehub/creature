# File: mathlab_creature/scenes/tests/test_walk_audio_scene.py

"""
mathlab_creature/scenes/tests/test_walk_audio_scene.py

WALK AUDIO VALIDATION SCENE

Purpose
-------
Dedicated procedural footstep timing validation.

Tests:
- left/right footstep alternation
- footstep rhythm consistency
- walk audio synchronization
- gait timing alignment
- soft mascot footstep feel
- procedural walk sound stability
- sound toggle safety
- cinematic movement rhythm

IMPORTANT
---------
This scene validates:
- WALK AUDIO QUALITY
- WALK AUDIO TIMING
- FOOTSTEP SYNCHRONIZATION

NOT:
- camera systems
- full animation integration
- controller architecture
"""

from __future__ import annotations

from manimlib import *

from mathlab_creature.core.transforms import (
    vec3,
)

from mathlab_creature.core.audio.audio_server import (
    boot_audio_server,
    shutdown_audio_server,
)

from mathlab_creature.core.logger import (
    get_logger,
)

from mathlab_creature.creature.rigs.body_rig import (
    build_body_rig,
)

from mathlab_creature.creature.actions.walk_action import (
    build_walk_action,
)

logger = get_logger(__name__)


# =========================================================
# SCENE
# =========================================================

class TestWalkAudioScene(Scene):
    """
    Dedicated procedural walk-audio validation scene.
    """

    def construct(self):

        logger.info(
            "Starting TestWalkAudioScene"
        )

        # =================================================
        # AUDIO BOOT
        # =================================================

        boot_audio_server()

        # =================================================
        # TITLE
        # =================================================

        title = Text(
            "WALK AUDIO TEST",
            font_size=36,
        )

        title.to_edge(UP)

        self.play(
            FadeIn(title)
        )

        self.wait(0.5)

        # =================================================
        # CREATURE
        # =================================================

        rig = build_body_rig()

        creature = rig["group"]

        creature.move_to(
            vec3(
                -5.0,
                -1.0,
                0.0,
            )
        )

        self.play(
            FadeIn(creature)
        )

        self.wait(1)

        # =================================================
        # WALK ACTION
        # =================================================

        walk_action = build_walk_action(
            rig,
            with_sound=True,
        )

        # =================================================
        # UPDATE LOOP
        # =================================================

        def update_walk(_, dt):

            walk_action.update(dt)

        creature.add_updater(
            update_walk
        )

        # =================================================
        # TEST 1
        # SLOW WALK
        # =================================================

        label = Text(
            "Slow Walk Timing",
            font_size=28,
        )

        label.move_to(
            vec3(
                0.0,
                3.0,
                0.0,
            )
        )

        self.play(
            FadeIn(label)
        )

        walk_action.start(
            direction=vec3(
                1.0,
                0.0,
                0.0,
            ),
            speed=0.55,
        )

        self.wait(6)

        self.play(
            FadeOut(label)
        )

        # =================================================
        # TEST 2
        # NORMAL WALK
        # =================================================

        label = Text(
            "Normal Walk Timing",
            font_size=28,
        )

        label.move_to(
            vec3(
                0.0,
                3.0,
                0.0,
            )
        )

        self.play(
            FadeIn(label)
        )

        walk_action.set_speed(
            1.0
        )

        self.wait(6)

        self.play(
            FadeOut(label)
        )

        # =================================================
        # TEST 3
        # FAST WALK
        # =================================================

        label = Text(
            "Fast Walk Timing",
            font_size=28,
        )

        label.move_to(
            vec3(
                0.0,
                3.0,
                0.0,
            )
        )

        self.play(
            FadeIn(label)
        )

        walk_action.set_speed(
            1.7
        )

        self.wait(6)

        self.play(
            FadeOut(label)
        )

        # =================================================
        # TEST 4
        # CARTOON MASCOT STYLE
        # =================================================

        label = Text(
            "Soft Mascot Footsteps",
            font_size=28,
        )

        label.move_to(
            vec3(
                0.0,
                3.0,
                0.0,
            )
        )

        self.play(
            FadeIn(label)
        )

        walk_action.config.stride_length = 0.62

        walk_action.config.step_height = 0.32

        walk_action.config.body_bounce_strength = (
            0.10
        )

        walk_action.config.body_sway_strength = (
            0.07
        )

        walk_action.config.footstep_volume = 0.65

        walk_action.set_speed(
            0.9
        )

        self.wait(8)

        self.play(
            FadeOut(label)
        )

        # =================================================
        # TEST 5
        # LEFT / RIGHT RHYTHM
        # =================================================

        label = Text(
            "Left / Right Alternation",
            font_size=28,
        )

        label.move_to(
            vec3(
                0.0,
                3.0,
                0.0,
            )
        )

        self.play(
            FadeIn(label)
        )

        walk_action.config.left_step_pitch_offset = (
            -10
        )

        walk_action.config.right_step_pitch_offset = (
            10
        )

        walk_action.set_speed(
            1.15
        )

        self.wait(8)

        self.play(
            FadeOut(label)
        )

        # =================================================
        # TEST 6
        # DIAGONAL WALK
        # =================================================

        label = Text(
            "Directional Walk Audio",
            font_size=28,
        )

        label.move_to(
            vec3(
                0.0,
                3.0,
                0.0,
            )
        )

        self.play(
            FadeIn(label)
        )

        walk_action.set_direction(
            vec3(
                1.0,
                0.35,
                0.0,
            )
        )

        walk_action.set_speed(
            1.1
        )

        self.wait(6)

        self.play(
            FadeOut(label)
        )

        # =================================================
        # TEST 7
        # SOUND DISABLED
        # =================================================

        label = Text(
            "Silent Walk Mode",
            font_size=28,
        )

        label.move_to(
            vec3(
                0.0,
                3.0,
                0.0,
            )
        )

        self.play(
            FadeIn(label)
        )

        walk_action.disable_sound()

        walk_action.set_speed(
            1.0
        )

        self.wait(5)

        self.play(
            FadeOut(label)
        )

        # =================================================
        # TEST 8
        # SOUND RESTORE
        # =================================================

        label = Text(
            "Audio Restored",
            font_size=28,
        )

        label.move_to(
            vec3(
                0.0,
                3.0,
                0.0,
            )
        )

        self.play(
            FadeIn(label)
        )

        walk_action.enable_sound()

        walk_action.set_speed(
            1.2
        )

        self.wait(5)

        self.play(
            FadeOut(label)
        )

        # =================================================
        # TEST 9
        # STOP
        # =================================================

        label = Text(
            "Walk Stop",
            font_size=28,
        )

        label.move_to(
            vec3(
                0.0,
                3.0,
                0.0,
            )
        )

        self.play(
            FadeIn(label)
        )

        walk_action.stop()

        self.wait(4)

        self.play(
            FadeOut(label)
        )

        # =================================================
        # SUCCESS
        # =================================================

        success = Text(
            "FOOTSTEP TIMING VALID",
            font_size=34,
        )

        success.move_to(
            vec3(
                0.0,
                2.5,
                0.0,
            )
        )

        self.play(
            FadeIn(success)
        )

        self.wait(2)

        # -------------------------------------------------
        # CLEANUP
        # -------------------------------------------------

        creature.remove_updater(
            update_walk
        )

        # -------------------------------------------------
        # AUDIO SHUTDOWN
        # -------------------------------------------------

        shutdown_audio_server()

        logger.info(
            "Finished TestWalkAudioScene"
        )

        self.wait(1)