"""
Mascot point scene for mathlab-mylinehub-creature.

Purpose:
- present the MYLINEHUB M creature in a simple pointing scene
- test the pointing action in a real character scene
- prepare for later teaching / board / formula scenes

Scene flow:
1. build creature rig slightly left of center
2. fade creature in
3. blink once
4. point to the right side of the frame
5. hold the pointing pose briefly
6. optionally return toward neutral
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
from creature.actions.point_action import build_point_animation
from creature.rigs.body_rig import build_body_rig

logger = get_logger(__name__)


class MascotPointScene(Scene):
    """
    Simple pointing scene for the mascot.

    This scene is meant to:
    - show a readable point gesture
    - introduce a simple target on the right side
    - prepare visually for later teaching/board scenes
    """

    CONFIG = {
        "camera_config": {
            "background_color": DEFAULT_SCENE_BACKGROUND_COLOR,
        }
    }

    def construct(self) -> None:
        if LOG_SCENE_EVENTS:
            logger.info("Starting MascotPointScene")

        # ----------------------------------------------------
        # Build creature rig slightly left of center
        # ----------------------------------------------------
        rig = build_body_rig(point(-3.0, 0.0, 0.0))
        creature_group = rig["group"]
        eyes_group = rig["face"]["eyes"]

        scene_title = Text("Mascot Point Scene")
        scene_title.scale(0.48)
        scene_title.next_to(creature_group, DOWN, buff=0.7)

        # ----------------------------------------------------
        # Target label on the right side
        # ----------------------------------------------------
        target_label = Text("Look here")
        target_label.scale(0.6)
        target_label.move_to(point(3.2, 1.0, 0.0))

        # ----------------------------------------------------
        # Group metadata
        # ----------------------------------------------------
        scene_group = VGroup(
            creature_group,
            scene_title,
            target_label,
        )
        scene_group.name = "mascot_point_scene_group"

        # Local pacing values for easy tuning
        intro_pause = 0.20
        blink_pause = 0.15
        final_pause = DEFAULT_WAIT_TIME

        # ----------------------------------------------------
        # Intro appearance
        # ----------------------------------------------------
        if LOG_SCENE_EVENTS:
            logger.info("Running point-scene fade-in")

        self.play(FadeIn(creature_group), FadeIn(target_label))
        self.play(FadeIn(scene_title))
        self.wait(intro_pause)

        # ----------------------------------------------------
        # Blink before pointing
        # ----------------------------------------------------
        if LOG_SCENE_EVENTS:
            logger.info("Running point-scene blink")

        self.play(build_blink_animation(eyes_group))
        self.wait(blink_pause)

        # ----------------------------------------------------
        # Point toward the right side
        # ----------------------------------------------------
        if LOG_SCENE_EVENTS:
            logger.info("Running point-scene pointing action")

        self.play(
            build_point_animation(
                rig,
                side="right",
                hold=True,
                return_to_neutral=False,
            )
        )
        self.wait(final_pause)

        if DEFAULT_SHOW_DEBUG_LABELS:
            logger.debug(
                "MascotPointScene debug | scene_group=%s creature_group=%s target_center=%s",
                getattr(scene_group, "name", "unnamed_scene_group"),
                getattr(creature_group, "name", "unnamed_creature_group"),
                target_label.get_center(),
            )

        if LOG_SCENE_EVENTS:
            logger.info("Finished MascotPointScene")