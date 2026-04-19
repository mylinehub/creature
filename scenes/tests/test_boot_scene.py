"""
Basic boot test scene for mathlab-mylinehub-creature.

Purpose:
- verify ManimGL project setup is working
- verify scene rendering path is working
- verify text rendering is working
- give a very small first successful scene

This scene is intentionally simple.
It is not the creature scene yet.
"""

from __future__ import annotations

from manimlib import DOWN
from manimlib import Scene
from manimlib import Text
from manimlib import VGroup
from manimlib import Write
from manimlib import FadeIn

from config.defaults import DEFAULT_SCENE_BACKGROUND_COLOR
from config.defaults import DEFAULT_WAIT_TIME
from config.defaults import DEBUG_MODE
from config.defaults import LOG_SCENE_EVENTS
from core.logger import get_logger
from core.naming import test_scene_name

logger = get_logger(__name__)


class TestBootScene(Scene):
    """
    Minimal project boot scene.

    This is the first sanity-check scene for confirming that:
    - the project imports correctly
    - ManimGL can render a scene
    - text objects can be created and animated
    """

    CONFIG = {
        "camera_config": {
            "background_color": DEFAULT_SCENE_BACKGROUND_COLOR,
        }
    }

    def construct(self) -> None:
        if LOG_SCENE_EVENTS:
            logger.info("Starting TestBootScene")

        title = Text("MYLINEHUB Creature Boot OK")
        subtitle = Text("ManimGL project setup is working")
        subtitle.scale(0.55)
        subtitle.next_to(title, DOWN, buff=0.25)

        content = VGroup(title, subtitle)
        content.name = test_scene_name("boot")

        if DEBUG_MODE:
            logger.debug(
                "Boot scene content prepared | group_name=%s title=%s subtitle=%s",
                content.name,
                getattr(title, "text", "title"),
                getattr(subtitle, "text", "subtitle"),
            )

        self.play(Write(title))
        self.play(FadeIn(subtitle))
        self.wait(DEFAULT_WAIT_TIME)

        if LOG_SCENE_EVENTS:
            logger.info("Finished TestBootScene")