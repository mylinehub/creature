"""
Body test scene for mathlab-mylinehub-creature.

Purpose:
- verify that the MYLINEHUB creature builds correctly
- render the first assembled mascot on screen
- confirm that body, eyes, nose, mouth, and hat align properly
- provide a simple test scene before adding limbs and actions

This is the first real creature scene.
"""

from __future__ import annotations

from manimlib import DOWN
from manimlib import FadeIn
from manimlib import Scene
from manimlib import Text
from manimlib import VGroup

from mathlab_creature.config.defaults import DEFAULT_SCENE_BACKGROUND_COLOR
from mathlab_creature.config.defaults import DEFAULT_WAIT_TIME
from mathlab_creature.config.defaults import DEFAULT_SHOW_DEBUG_LABELS
from mathlab_creature.config.defaults import LOG_SCENE_EVENTS
from mathlab_creature.core.logger import get_logger
from mathlab_creature.core.naming import test_scene_name
from mathlab_creature.creature.myline_m_creature import build_myline_m_creature

logger = get_logger(__name__)


class TestBodyScene(Scene):
    """
    Render the first full version of the creature.

    This scene is intentionally simple:
    - build the mascot
    - show it clearly
    - leave enough visual quiet space to inspect alignment
    """

    CONFIG = {
        "camera_config": {
            "background_color": DEFAULT_SCENE_BACKGROUND_COLOR,
        }
    }

    def construct(self) -> None:
        if LOG_SCENE_EVENTS:
            logger.info("Starting TestBodyScene")

        creature = build_myline_m_creature()
        creature.name = "test_body_scene_creature"

        title = Text("MYLINEHUB M Creature")
        title.scale(0.55)
        title.next_to(creature, DOWN, buff=0.6)

        content = VGroup(creature, title)
        content.name = test_scene_name("body")

        if LOG_SCENE_EVENTS:
            logger.info(
                "Creature built for TestBodyScene | has_body=%s has_eyes=%s has_nose=%s has_mouth=%s has_hat=%s",
                creature.body is not None,
                creature.eyes is not None,
                creature.nose is not None,
                creature.mouth is not None,
                creature.hat is not None,
            )

        self.play(FadeIn(creature))
        self.play(FadeIn(title))
        self.wait(DEFAULT_WAIT_TIME)

        if DEFAULT_SHOW_DEBUG_LABELS:
            logger.debug(
                "TestBodyScene debug | creature_name=%s group_name=%s",
                getattr(creature, "name", "unnamed_creature"),
                getattr(content, "name", "unnamed_group"),
            )

        if LOG_SCENE_EVENTS:
            logger.info("Finished TestBodyScene")