# File: mathlab_creature/scenes/tests/test_master_audio_scene.py

"""
mathlab_creature/scenes/tests/test_master_audio_scene.py

MASTER CINEMATIC AUDIO VALIDATION SCENE

Purpose
-------
End-to-end cinematic procedural audio validation.

This is the MAIN audio showcase scene.

Tests:
- procedural audio pipeline
- cinematic sound timing
- action synchronization
- layered procedural sound
- mascot-style audio behavior
- educational presentation rhythm
- sound toggle safety
- audio server lifecycle
- integrated action audio
- scene pacing support

This scene validates:
FULL AUDIO EXPERIENCE.

IMPORTANT
---------
This is NOT:
- low-level synthesis debugging
- isolated timing debugging
- IK testing
- geometry testing

This is:
THE MAIN CINEMATIC AUDIO DEMO.
"""

from __future__ import annotations

from manimlib import *

from mathlab_creature.core.geometry import (
    point,
)

from mathlab_creature.core.logger import (
    get_logger,
)

from mathlab_creature.core.audio.audio_server import (
    boot_audio_server,
    shutdown_audio_server,
)

from mathlab_creature.creature.rigs.body_rig import (
    build_body_rig,
)

from mathlab_creature.creature.actions.blink_action import (
    build_blink_animation,
)

from mathlab_creature.creature.actions.look_action import (
    build_look_animation,
    build_look_center_animation,
)

from mathlab_creature.creature.actions.wave_action import (
    build_wave_animation,
)

from mathlab_creature.creature.actions.walk_action import (
    build_walk_animation,
)

from mathlab_creature.creature.actions.point_action import (
    build_point_animation,
)

from mathlab_creature.creature.actions.hop_action import (
    build_hop_animation,
)

from mathlab_creature.creature.actions.turn_action import (
    build_turn_action,
)

from mathlab_creature.creature.actions.idle_action import (
    build_idle_action,
)

from mathlab_creature.props.pointer_stick import (
    build_pointer_stick,
)

from mathlab_creature.props.math_board import (
    build_math_board,
)

from mathlab_creature.props.axis_plane import (
    build_axis_plane,
)

from mathlab_creature.props.formula_card import (
    build_formula_card,
)

logger = get_logger(__name__)


# =========================================================
# SCENE
# =========================================================

class TestMasterAudioScene(Scene):
    """
    End-to-end cinematic procedural audio showcase.
    """

    def construct(self):

        logger.info(
            "Starting TestMasterAudioScene"
        )

        # =================================================
        # AUDIO BOOT
        # =================================================

        boot_audio_server()

        # =================================================
        # GLOBAL AUDIO TOGGLE
        # =================================================

        WITH_SOUND = True

        # =================================================
        # BUILD CREATURE
        # =================================================

        rig = build_body_rig(
            point(0, 0, 0)
        )

        creature = rig["group"]

        eyes = rig["face"]["eyes"]

        self.play(
            FadeIn(creature)
        )

        self.wait(0.5)

        # =================================================
        # TITLE
        # =================================================

        title = Text(
            "MASTER AUDIO VALIDATION",
            font_size=38,
        )

        title.to_edge(UP)

        self.play(
            Write(title)
        )

        self.wait(1)

        # =================================================
        # SECTION 1
        # BLINK + LOOK
        # =================================================

        section = Text(
            "Eye Motion + Audio",
            font_size=28,
        )

        section.move_to(
            point(0, 3, 0)
        )

        self.play(
            FadeIn(section)
        )

        self.play(
            build_blink_animation(
                eyes,
                with_sound=WITH_SOUND,
            )
        )

        self.wait(0.4)

        self.play(
            build_look_animation(
                eyes,
                "right",
                with_sound=WITH_SOUND,
            )
        )

        self.wait(0.4)

        self.play(
            build_look_animation(
                eyes,
                "left",
                with_sound=WITH_SOUND,
            )
        )

        self.wait(0.4)

        self.play(
            build_look_center_animation(
                eyes,
            )
        )

        self.wait(1)

        self.play(
            FadeOut(section)
        )

        # =================================================
        # SECTION 2
        # WAVE
        # =================================================

        section = Text(
            "Wave Gesture Audio",
            font_size=28,
        )

        section.move_to(
            point(0, 3, 0)
        )

        self.play(
            FadeIn(section)
        )

        self.play(
            build_wave_animation(
                rig,
                cycles=3,
                with_sound=WITH_SOUND,
            )
        )

        self.wait(1)

        self.play(
            FadeOut(section)
        )

        # =================================================
        # SECTION 3
        # WALK AUDIO
        # =================================================

        section = Text(
            "Footstep Timing",
            font_size=28,
        )

        section.move_to(
            point(0, 3, 0)
        )

        self.play(
            FadeIn(section)
        )

        self.play(
            build_walk_animation(
                rig,
                cycles=4,
                with_sound=WITH_SOUND,
            )
        )

        self.wait(2)

        self.play(
            creature.animate.move_to(
                point(0, 0, 0)
            )
        )

        self.wait(1)

        self.play(
            FadeOut(section)
        )

        # =================================================
        # SECTION 4
        # POINTING AUDIO
        # =================================================

        section = Text(
            "Educational Cue Audio",
            font_size=28,
        )

        section.move_to(
            point(0, 3, 0)
        )

        self.play(
            FadeIn(section)
        )

        label = Text(
            "Focus Here",
            font_size=26,
        )

        label.move_to(
            point(3, 1, 0)
        )

        self.play(
            FadeIn(label)
        )

        self.play(
            build_look_animation(
                eyes,
                "right",
                with_sound=WITH_SOUND,
            )
        )

        self.wait(0.25)

        self.play(
            build_point_animation(
                rig,
                hold=True,
                with_sound=WITH_SOUND,
            )
        )

        self.wait(1)

        self.play(
            FadeOut(label)
        )

        self.play(
            FadeOut(section)
        )

        # =================================================
        # SECTION 5
        # TEACH MODE
        # =================================================

        section = Text(
            "Teaching Presentation Rhythm",
            font_size=28,
        )

        section.move_to(
            point(0, 3, 0)
        )

        self.play(
            FadeIn(section)
        )

        board = (
            build_math_board()
            .scale(0.7)
        )

        board.move_to(
            point(3, 0.5, 0)
        )

        pointer = (
            build_pointer_stick()
            .scale(0.8)
        )

        right_hand = (
            rig["arms"]["right_hand"]
        )

        pointer.move_to(
            right_hand.get_center()
        )

        pointer.rotate(-0.6)

        self.play(
            FadeIn(board),
            FadeIn(pointer),
        )

        self.play(
            build_look_animation(
                eyes,
                "right",
                with_sound=WITH_SOUND,
            )
        )

        self.wait(0.25)

        self.play(
            build_point_animation(
                rig,
                hold=True,
                with_sound=WITH_SOUND,
            )
        )

        self.wait(1)

        self.play(
            FadeOut(board),
            FadeOut(pointer),
        )

        self.play(
            FadeOut(section)
        )

        # =================================================
        # SECTION 6
        # HOP AUDIO
        # =================================================

        section = Text(
            "Hop + Landing Audio",
            font_size=28,
        )

        section.move_to(
            point(0, 3, 0)
        )

        self.play(
            FadeIn(section)
        )

        self.play(
            build_hop_animation(
                rig,
                with_sound=WITH_SOUND,
            )
        )

        self.wait(1)

        self.play(
            build_hop_animation(
                rig,
                with_sound=WITH_SOUND,
            )
        )

        self.wait(1)

        self.play(
            FadeOut(section)
        )

        # =================================================
        # SECTION 7
        # IDLE AUDIO
        # =================================================

        section = Text(
            "Ambient Idle Presence",
            font_size=28,
        )

        section.move_to(
            point(0, 3, 0)
        )

        self.play(
            FadeIn(section)
        )

        idle_action = build_idle_action(
            rig,
            with_sound=WITH_SOUND,
        )

        def idle_update(_, dt):

            idle_action.update(dt)

        creature.add_updater(
            idle_update
        )

        self.wait(6)

        creature.remove_updater(
            idle_update
        )

        self.play(
            FadeOut(section)
        )

        # =================================================
        # SECTION 8
        # SILENT MODE VALIDATION
        # =================================================

        section = Text(
            "Silent Mode Validation",
            font_size=28,
        )

        section.move_to(
            point(0, 3, 0)
        )

        self.play(
            FadeIn(section)
        )

        self.play(
            build_wave_animation(
                rig,
                cycles=2,
                with_sound=False,
            )
        )

        self.wait(0.5)

        self.play(
            build_blink_animation(
                eyes,
                with_sound=False,
            )
        )

        self.wait(0.5)

        self.play(
            build_hop_animation(
                rig,
                with_sound=False,
            )
        )

        self.wait(1)

        self.play(
            FadeOut(section)
        )

        # =================================================
        # FINAL
        # =================================================

        final_text = Text(
            "PROCEDURAL AUDIO SYSTEM VALID",
            font_size=36,
        )

        final_text.move_to(
            point(0, 2, 0)
        )

        self.play(
            Write(final_text)
        )

        self.wait(2)

        # =================================================
        # AUDIO SHUTDOWN
        # =================================================

        shutdown_audio_server()

        logger.info(
            "Finished TestMasterAudioScene"
        )

        self.wait(1)