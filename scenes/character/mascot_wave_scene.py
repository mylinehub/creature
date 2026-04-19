"""
Mascot wave scene for mathlab-mylinehub-creature.

Purpose:
- present the MYLINEHUB M creature in a friendly greeting scene
- test the wave action in a simple real scene
- combine intro-style presentation with a clear waving gesture

Scene flow:
1. build creature rig
2. fade creature in
3. blink once
4. do a small look-to-center prep
5. wave with the right arm
6. hold final frame

This scene is intentionally simple and readable.
"""

from __future__ import annotations

from manimlib import DOWN
from manimlib import FadeIn
from manimlib import Scene
from manimlib import Text
from manimlib import VGroup

from config.defaults import DEFAULT_SCENE_BACKGROUND_COLOR
from config.defaults import DEFAULT_WAIT_TIME
from config.defaults import DEFAULT_SHOW_DEBUG_LABELS
from config.defaults import LOG_SCENE_EVENTS

from core.logger import get_logger

from creature.actions.blink_action import build_blink_animation
from creature.actions.look_action import build_look_center_animation
from creature.actions.wave_action import build_wave_animation
from creature.rigs.body_rig import build_body_rig

logger = get_logger(__name__)


class MascotWaveScene(Scene):
    """
    Simple greeting / wave scene for the mascot.
    """

    CONFIG = {
        "camera_config": {
            "background_color": DEFAULT_SCENE_BACKGROUND_COLOR,
        }
    }

    def construct(self) -> None:
        if LOG_SCENE_EVENTS:
            logger.info("Starting MascotWaveScene")

        # ----------------------------------------------------
        # Build creature rig
        # ----------------------------------------------------
        rig = build_body_rig()
        creature_group = rig["group"]
        eyes_group = rig["face"]["eyes"]

        title = Text("Hello from MYLINEHUB")
        title.scale(0.5)
        title.next_to(creature_group, DOWN, buff=0.7)

        scene_group = VGroup(creature_group, title)
        scene_group.name = "mascot_wave_scene_group"

        # Local pacing values for easy tuning
        intro_pause = 0.25
        blink_pause = 0.15
        look_pause = 0.15
        final_pause = DEFAULT_WAIT_TIME

        # ----------------------------------------------------
        # Intro appearance
        # ----------------------------------------------------
        if LOG_SCENE_EVENTS:
            logger.info("Running wave-scene fade-in")

        self.play(FadeIn(creature_group))
        self.play(FadeIn(title))
        self.wait(intro_pause)

        # ----------------------------------------------------
        # Small prep blink
        # ----------------------------------------------------
        if LOG_SCENE_EVENTS:
            logger.info("Running wave-scene blink")

        self.play(build_blink_animation(eyes_group))
        self.wait(blink_pause)

        # ----------------------------------------------------
        # Reset gaze to center just before greeting
        # ----------------------------------------------------
        if LOG_SCENE_EVENTS:
            logger.info("Running wave-scene center look")

        self.play(build_look_center_animation(eyes_group))
        self.wait(look_pause)

        # ----------------------------------------------------
        # Wave
        # ----------------------------------------------------
        if LOG_SCENE_EVENTS:
            logger.info("Running wave-scene wave action")

        self.play(build_wave_animation(rig, cycles=2))
        self.wait(final_pause)

        if DEFAULT_SHOW_DEBUG_LABELS:
            logger.debug(
                "MascotWaveScene debug | scene_group=%s creature_group=%s",
                getattr(scene_group, "name", "unnamed_scene_group"),
                getattr(creature_group, "name", "unnamed_creature_group"),
            )

        if LOG_SCENE_EVENTS:
            logger.info("Finished MascotWaveScene")