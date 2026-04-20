"""
Mascot intro scene for mathlab-mylinehub-creature.

Purpose:
- introduce the MYLINEHUB M creature on screen
- use a simple readable sequence
- combine full creature rig with a small welcoming motion
- serve as the first character-focused scene beyond test scenes

Scene flow:
1. build creature rig
2. fade creature in
3. blink
4. look around briefly
5. do a small hop
6. hold final pose

This scene is intentionally simple and friendly.
"""

from __future__ import annotations

from manimlib import FadeIn
from manimlib import Scene
from manimlib import Text
from manimlib import DOWN
from manimlib import VGroup

from mathlab_creature.config.defaults import DEFAULT_SCENE_BACKGROUND_COLOR
from mathlab_creature.config.defaults import DEFAULT_WAIT_TIME
from mathlab_creature.config.defaults import DEFAULT_SHOW_DEBUG_LABELS
from mathlab_creature.config.defaults import LOG_SCENE_EVENTS

from mathlab_creature.core.logger import get_logger

from mathlab_creature.creature.rigs.body_rig import build_body_rig
from mathlab_creature.creature.actions.blink_action import build_blink_animation
from mathlab_creature.creature.actions.look_action import build_look_animation
from mathlab_creature.creature.actions.look_action import build_look_center_animation
from mathlab_creature.creature.actions.hop_action import build_hop_animation

logger = get_logger(__name__)


class MascotIntroScene(Scene):
    """
    First simple mascot introduction scene.
    """

    CONFIG = {
        "camera_config": {
            "background_color": DEFAULT_SCENE_BACKGROUND_COLOR,
        }
    }

    def construct(self) -> None:
        if LOG_SCENE_EVENTS:
            logger.info("Starting MascotIntroScene")

        # ----------------------------------------------------
        # Build creature rig
        # ----------------------------------------------------
        rig = build_body_rig()
        creature_group = rig["group"]
        eyes_group = rig["face"]["eyes"]

        # Optional light scene label for identity/readability
        title = Text("MYLINEHUB Mascot")
        title.scale(0.5)
        title.next_to(creature_group, DOWN, buff=0.7)

        intro_group = VGroup(creature_group, title)
        intro_group.name = "mascot_intro_scene_group"

        # Local pacing values for easy tuning
        intro_pause = 0.35
        blink_pause = 0.20
        look_pause = 0.18
        center_pause = 0.20
        hop_pause = DEFAULT_WAIT_TIME

        # ----------------------------------------------------
        # Intro appearance
        # ----------------------------------------------------
        if LOG_SCENE_EVENTS:
            logger.info("Running intro fade-in")

        self.play(FadeIn(creature_group))
        self.play(FadeIn(title))
        self.wait(intro_pause)

        # ----------------------------------------------------
        # Blink
        # ----------------------------------------------------
        if LOG_SCENE_EVENTS:
            logger.info("Running intro blink")

        self.play(build_blink_animation(eyes_group))
        self.wait(blink_pause)

        # ----------------------------------------------------
        # Look around
        # ----------------------------------------------------
        if LOG_SCENE_EVENTS:
            logger.info("Running intro look-around")

        self.play(build_look_animation(eyes_group, "left"))
        self.wait(look_pause)

        self.play(build_look_animation(eyes_group, "right"))
        self.wait(look_pause)

        self.play(build_look_center_animation(eyes_group))
        self.wait(center_pause)

        # ----------------------------------------------------
        # Small welcoming hop
        # ----------------------------------------------------
        if LOG_SCENE_EVENTS:
            logger.info("Running intro hop")

        self.play(build_hop_animation(rig, hop_height=0.35))
        self.wait(hop_pause)

        if DEFAULT_SHOW_DEBUG_LABELS:
            logger.debug(
                "MascotIntroScene debug | intro_group=%s creature_group=%s",
                getattr(intro_group, "name", "unnamed_intro_group"),
                getattr(creature_group, "name", "unnamed_creature_group"),
            )

        if LOG_SCENE_EVENTS:
            logger.info("Finished MascotIntroScene")