"""
Face test scene for mathlab-mylinehub-creature.

Purpose:
- verify the face parts clearly and separately
- check eye spacing
- check nose placement
- check mouth placement
- make face debugging easier than the full creature scene

This scene focuses on the facial region, not the full presentation.
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
from creature.parts.mouth import build_mouth
from creature.parts.nose import build_nose

logger = get_logger(__name__)


class TestFaceScene(Scene):
    """
    Render body plus face parts for focused facial alignment testing.

    This scene is meant to make facial inspection easier than the
    full-creature scene by limiting the number of visible components.
    """

    CONFIG = {
        "camera_config": {
            "background_color": DEFAULT_SCENE_BACKGROUND_COLOR,
        }
    }

    def construct(self) -> None:
        if LOG_SCENE_EVENTS:
            logger.info("Starting TestFaceScene")

        body = build_body_m()
        eyes = build_eyes()
        nose = build_nose()
        mouth = build_mouth()

        face_test_group = VGroup(
            body,
            eyes,
            nose,
            mouth,
        )
        face_test_group.name = "test_face_scene_group"

        title = Text("Face Alignment Test")
        title.scale(0.5)
        title.next_to(face_test_group, DOWN, buff=0.6)

        scene_group = VGroup(face_test_group, title)
        scene_group.name = test_scene_name("face")

        if LOG_SCENE_EVENTS:
            logger.info(
                "Face test content built | body=%s eyes=%s nose=%s mouth=%s",
                body is not None,
                eyes is not None,
                nose is not None,
                mouth is not None,
            )

        self.play(FadeIn(face_test_group))
        self.play(FadeIn(title))
        self.wait(DEFAULT_WAIT_TIME)

        if DEFAULT_SHOW_DEBUG_LABELS:
            logger.debug(
                "TestFaceScene debug | face_group=%s scene_group=%s",
                getattr(face_test_group, "name", "unnamed_face_group"),
                getattr(scene_group, "name", "unnamed_scene_group"),
            )

        if LOG_SCENE_EVENTS:
            logger.info("Finished TestFaceScene")