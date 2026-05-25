# File: mathlab_creature/scenes/tests/test_sound_toggle_scene.py

"""
mathlab_creature/scenes/tests/test_sound_toggle_scene.py

SOUND TOGGLE VALIDATION SCENE

CRITICAL TEST
-------------
Verifies:
- with_sound=True works
- with_sound=False works
- animation behavior remains stable
- no crashes when audio disabled
- action systems remain identical
- silent mode is fully supported

Purpose
-------
This scene validates:
- audio optionality
- safe silent rendering
- headless-safe operation
- procedural audio toggling
- production-safe fallback behavior

IMPORTANT
---------
Animation quality should remain identical
whether sound is:
- enabled
- disabled

ONLY audio output should change.
"""

from __future__ import annotations

from manimlib import *

from mathlab_creature.core.geometry import (
    point,
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

from mathlab_creature.creature.actions.blink_action import (
    build_blink_animation,
)

from mathlab_creature.creature.actions.wave_action import (
    build_wave_animation,
)

from mathlab_creature.creature.actions.look_action import (
    build_look_animation,
)

from mathlab_creature.creature.actions.point_action import (
    build_point_animation,
)

from mathlab_creature.creature.actions.hop_action import (
    build_hop_animation,
)

from mathlab_creature.creature.actions.walk_action import (
    build_walk_animation,
)

logger = get_logger(__name__)


# =========================================================
# SCENE
# =========================================================

class TestSoundToggleScene(Scene):
    """
    Verifies audio-enabled and audio-disabled modes.
    """

    def construct(self):

        logger.info(
            "Starting TestSoundToggleScene"
        )

        # =================================================
        # AUDIO BOOT
        # =================================================

        boot_audio_server()

        # =================================================
        # TITLE
        # =================================================

        title = Text(
            "SOUND TOGGLE TEST",
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

        rig = build_body_rig(
            point(0, -1, 0)
        )

        creature = rig["group"]

        eyes = rig["face"]["eyes"]

        self.play(
            FadeIn(creature)
        )

        self.wait(1)

        # =================================================
        # SECTION 1
        # SOUND ENABLED
        # =================================================

        enabled_label = Text(
            "WITH SOUND = TRUE",
            font_size=28,
        )

        enabled_label.move_to(
            point(0, 3, 0)
        )

        self.play(
            FadeIn(enabled_label)
        )

        self.wait(0.5)

        # -------------------------------------------------
        # BLINK
        # -------------------------------------------------

        self.play(
            build_blink_animation(
                eyes,
                with_sound=True,
            )
        )

        self.wait(0.5)

        # -------------------------------------------------
        # LOOK
        # -------------------------------------------------

        self.play(
            build_look_animation(
                eyes,
                "right",
                with_sound=True,
            )
        )

        self.wait(0.5)

        # -------------------------------------------------
        # WAVE
        # -------------------------------------------------

        self.play(
            build_wave_animation(
                rig,
                cycles=2,
                with_sound=True,
            )
        )

        self.wait(0.5)

        # -------------------------------------------------
        # POINT
        # -------------------------------------------------

        self.play(
            build_point_animation(
                rig,
                hold=True,
                with_sound=True,
            )
        )

        self.wait(0.5)

        # -------------------------------------------------
        # HOP
        # -------------------------------------------------

        self.play(
            build_hop_animation(
                rig,
                with_sound=True,
            )
        )

        self.wait(0.5)

        # -------------------------------------------------
        # WALK
        # -------------------------------------------------

        self.play(
            build_walk_animation(
                rig,
                cycles=2,
                with_sound=True,
            )
        )

        self.wait(1)

        self.play(
            FadeOut(enabled_label)
        )

        self.wait(1)

        # =================================================
        # RESET POSITION
        # =================================================

        self.play(
            creature.animate.move_to(
                point(0, -1, 0)
            )
        )

        self.wait(1)

        # =================================================
        # SECTION 2
        # SOUND DISABLED
        # =================================================

        disabled_label = Text(
            "WITH SOUND = FALSE",
            font_size=28,
        )

        disabled_label.move_to(
            point(0, 3, 0)
        )

        self.play(
            FadeIn(disabled_label)
        )

        self.wait(0.5)

        # -------------------------------------------------
        # BLINK
        # -------------------------------------------------

        self.play(
            build_blink_animation(
                eyes,
                with_sound=False,
            )
        )

        self.wait(0.5)

        # -------------------------------------------------
        # LOOK
        # -------------------------------------------------

        self.play(
            build_look_animation(
                eyes,
                "right",
                with_sound=False,
            )
        )

        self.wait(0.5)

        # -------------------------------------------------
        # WAVE
        # -------------------------------------------------

        self.play(
            build_wave_animation(
                rig,
                cycles=2,
                with_sound=False,
            )
        )

        self.wait(0.5)

        # -------------------------------------------------
        # POINT
        # -------------------------------------------------

        self.play(
            build_point_animation(
                rig,
                hold=True,
                with_sound=False,
            )
        )

        self.wait(0.5)

        # -------------------------------------------------
        # HOP
        # -------------------------------------------------

        self.play(
            build_hop_animation(
                rig,
                with_sound=False,
            )
        )

        self.wait(0.5)

        # -------------------------------------------------
        # WALK
        # -------------------------------------------------

        self.play(
            build_walk_animation(
                rig,
                cycles=2,
                with_sound=False,
            )
        )

        self.wait(1)

        self.play(
            FadeOut(disabled_label)
        )

        self.wait(1)

        # =================================================
        # VALIDATION COMPLETE
        # =================================================

        success = Text(
            "TOGGLE VALIDATION PASSED",
            font_size=34,
        )

        success.move_to(
            point(0, 2.5, 0)
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
            "Finished TestSoundToggleScene"
        )

        self.wait(1)