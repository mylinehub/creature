"""
Action test scene for mathlab-mylinehub-creature.

Purpose:
- verify action helpers work on the full creature rig
- test blink
- test look
- test wave
- test point
- test hop
- test walk

This scene is a development playground for early action validation.
It is intentionally simple and sequential.
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
from core.naming import test_scene_name

from creature.actions.blink_action import build_blink_animation
from creature.actions.hop_action import build_hop_animation
from creature.actions.look_action import build_look_animation
from creature.actions.look_action import build_look_center_animation
from creature.actions.point_action import build_point_animation
from creature.actions.walk_action import build_walk_animation
from creature.actions.wave_action import build_wave_animation
from creature.rigs.body_rig import build_body_rig

logger = get_logger(__name__)


class TestActionsScene(Scene):
    """
    Render one creature rig and run early action tests in sequence.
    """

    CONFIG = {
        "camera_config": {
            "background_color": DEFAULT_SCENE_BACKGROUND_COLOR,
        }
    }

    def construct(self) -> None:
        if LOG_SCENE_EVENTS:
            logger.info("Starting TestActionsScene")

        # ----------------------------------------------------
        # Build rig
        # ----------------------------------------------------
        rig = build_body_rig()
        creature_group = rig["group"]
        eyes_group = rig["face"]["eyes"]

        title = Text("Creature Action Test")
        title.scale(0.5)
        title.next_to(creature_group, DOWN, buff=0.7)

        scene_group = VGroup(creature_group, title)
        scene_group.name = test_scene_name("actions")

        self.play(FadeIn(creature_group))
        self.play(FadeIn(title))
        self.wait(DEFAULT_WAIT_TIME)

        # Small local waits used between action checks.
        blink_pause = 0.4
        look_pause = 0.25
        action_pause = 0.5

        # ----------------------------------------------------
        # Blink
        # ----------------------------------------------------
        if LOG_SCENE_EVENTS:
            logger.info("Running blink test")

        self.play(build_blink_animation(eyes_group))
        self.wait(blink_pause)

        # ----------------------------------------------------
        # Look
        # ----------------------------------------------------
        if LOG_SCENE_EVENTS:
            logger.info("Running look test")

        self.play(build_look_animation(eyes_group, "left"))
        self.wait(look_pause)

        self.play(build_look_animation(eyes_group, "right"))
        self.wait(look_pause)

        self.play(build_look_animation(eyes_group, "up"))
        self.wait(look_pause)

        self.play(build_look_center_animation(eyes_group))
        self.wait(blink_pause)

        # ----------------------------------------------------
        # Wave
        # ----------------------------------------------------
        if LOG_SCENE_EVENTS:
            logger.info("Running wave test")

        self.play(build_wave_animation(rig, cycles=2))
        self.wait(action_pause)

        # ----------------------------------------------------
        # Point
        # ----------------------------------------------------
        if LOG_SCENE_EVENTS:
            logger.info("Running point test")

        self.play(build_point_animation(rig, hold=True, return_to_neutral=True))
        self.wait(action_pause)

        # ----------------------------------------------------
        # Hop
        # ----------------------------------------------------
        if LOG_SCENE_EVENTS:
            logger.info("Running hop test")

        self.play(build_hop_animation(rig, hop_height=0.45))
        self.wait(action_pause)

        # ----------------------------------------------------
        # Walk
        # ----------------------------------------------------
        if LOG_SCENE_EVENTS:
            logger.info("Running walk test")

        self.play(build_walk_animation(rig, cycles=2))
        self.wait(DEFAULT_WAIT_TIME)

        if DEFAULT_SHOW_DEBUG_LABELS:
            logger.debug(
                "TestActionsScene debug | scene_group=%s creature_group=%s",
                getattr(scene_group, "name", "unnamed_scene_group"),
                getattr(creature_group, "name", "unnamed_creature_group"),
            )

        if LOG_SCENE_EVENTS:
            logger.info("Finished TestActionsScene")