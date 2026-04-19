"""
Hat test scene for mathlab-mylinehub-creature.

Purpose:
- verify hat placement relative to the body
- verify hat scale and silhouette
- verify body + face + hat composition together
- isolate head-area tuning before limbs are added

This scene focuses on the upper mascot composition.
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
from creature.parts.body_m import build_body_m
from creature.parts.eyes import build_eyes
from creature.parts.hat import build_hat
from creature.parts.mouth import build_mouth
from creature.parts.nose import build_nose

logger = get_logger(__name__)


class TestHatScene(Scene):
    """
    Render body, face, and hat for hat-placement testing.

    This scene is meant to help inspect:
    - hat anchor alignment
    - hat silhouette readability
    - how the hat interacts with the upper face/body composition
    """

    CONFIG = {
        "camera_config": {
            "background_color": DEFAULT_SCENE_BACKGROUND_COLOR,
        }
    }

    def construct(self) -> None:
        if LOG_SCENE_EVENTS:
            logger.info("Starting TestHatScene")

        body = build_body_m()
        eyes = build_eyes()
        nose = build_nose()
        mouth = build_mouth()
        hat = build_hat()

        hat_test_group = VGroup(
            body,
            eyes,
            nose,
            mouth,
            hat,
        )
        hat_test_group.name = "test_hat_scene_group"

        title = Text("Hat Placement Test")
        title.scale(0.5)
        title.next_to(hat_test_group, DOWN, buff=0.6)

        scene_group = VGroup(hat_test_group, title)
        scene_group.name = test_scene_name("hat")

        if LOG_SCENE_EVENTS:
            logger.info(
                "Hat test content built | body=%s eyes=%s nose=%s mouth=%s hat=%s",
                body is not None,
                eyes is not None,
                nose is not None,
                mouth is not None,
                hat is not None,
            )

        self.play(FadeIn(hat_test_group))
        self.play(FadeIn(title))
        self.wait(DEFAULT_WAIT_TIME)

        if DEFAULT_SHOW_DEBUG_LABELS:
            logger.debug(
                "TestHatScene debug | hat_group=%s scene_group=%s hat_name=%s",
                getattr(hat_test_group, "name", "unnamed_hat_group"),
                getattr(scene_group, "name", "unnamed_scene_group"),
                getattr(hat, "name", "unnamed_hat"),
            )

        if LOG_SCENE_EVENTS:
            logger.info("Finished TestHatScene")