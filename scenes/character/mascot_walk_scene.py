"""
Mascot walk scene for mathlab-mylinehub-creature.

Purpose:
- present the MYLINEHUB M creature in a simple walking scene
- test the walk action in a real character scene
- show horizontal movement with readable stepping motion

Scene flow:
1. build creature rig
2. place creature slightly left
3. fade creature in
4. blink once
5. walk to the right
6. hold final frame
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

from core.geometry import point
from core.logger import get_logger

from creature.actions.blink_action import build_blink_animation
from creature.actions.walk_action import build_walk_animation
from creature.rigs.body_rig import build_body_rig

logger = get_logger(__name__)


class MascotWalkScene(Scene):
    """
    Simple walking scene for the mascot.

    This scene is meant to show:
    - a clean creature entrance
    - a small blink before movement
    - readable horizontal walking motion
    - a stable finishing hold
    """

    CONFIG = {
        "camera_config": {
            "background_color": DEFAULT_SCENE_BACKGROUND_COLOR,
        }
    }

    def construct(self) -> None:
        if LOG_SCENE_EVENTS:
            logger.info("Starting MascotWalkScene")

        # ----------------------------------------------------
        # Build creature rig slightly left of center
        # ----------------------------------------------------
        rig = build_body_rig(point(-3.5, 0.0, 0.0))
        creature_group = rig["group"]
        eyes_group = rig["face"]["eyes"]

        title = Text("MYLINEHUB Mascot Walk")
        title.scale(0.5)
        title.next_to(creature_group, DOWN, buff=0.7)

        scene_group = VGroup(creature_group, title)
        scene_group.name = "mascot_walk_scene_group"

        # Local pacing values for easy tuning
        intro_pause = 0.20
        blink_pause = 0.15
        final_pause = DEFAULT_WAIT_TIME

        # ----------------------------------------------------
        # Intro appearance
        # ----------------------------------------------------
        if LOG_SCENE_EVENTS:
            logger.info("Running walk-scene fade-in")

        self.play(FadeIn(creature_group))
        self.play(FadeIn(title))
        self.wait(intro_pause)

        # ----------------------------------------------------
        # Blink before movement
        # ----------------------------------------------------
        if LOG_SCENE_EVENTS:
            logger.info("Running walk-scene blink")

        self.play(build_blink_animation(eyes_group))
        self.wait(blink_pause)

        # ----------------------------------------------------
        # Walk
        # ----------------------------------------------------
        if LOG_SCENE_EVENTS:
            logger.info("Running walk-scene walk action")

        self.play(build_walk_animation(rig, cycles=3))
        self.wait(final_pause)

        if DEFAULT_SHOW_DEBUG_LABELS:
            logger.debug(
                "MascotWalkScene debug | scene_group=%s creature_group=%s final_center=%s",
                getattr(scene_group, "name", "unnamed_scene_group"),
                getattr(creature_group, "name", "unnamed_creature_group"),
                creature_group.get_center(),
            )

        if LOG_SCENE_EVENTS:
            logger.info("Finished MascotWalkScene")