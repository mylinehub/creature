"""
Limbs test scene for mathlab-mylinehub-creature.

Purpose:
- verify full creature body structure with limbs
- check arm and hand placement
- check leg and foot placement
- confirm full silhouette before rigs and poses are added

This scene renders the current complete static creature:
- body
- eyes
- nose
- mouth
- hat
- arms
- hands
- legs
- feet
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
from creature.parts.nose import build_nose
from creature.parts.mouth import build_mouth
from creature.parts.hat import build_hat
from creature.parts.arms import build_arms
from creature.parts.hands import build_hands
from creature.parts.legs import build_legs
from creature.parts.feet import build_feet

logger = get_logger(__name__)


class TestLimbsScene(Scene):
    """
    Render the full static creature with limbs.

    This scene is meant to verify:
    - upper-body composition
    - lower-body composition
    - hand attachment to actual arm endpoints
    - foot attachment to actual leg endpoints
    - overall silhouette readability before rigging begins
    """

    CONFIG = {
        "camera_config": {
            "background_color": DEFAULT_SCENE_BACKGROUND_COLOR,
        }
    }

    def construct(self) -> None:
        if LOG_SCENE_EVENTS:
            logger.info("Starting TestLimbsScene")

        # ----------------------------------------------------
        # Build main body + face + hat
        # ----------------------------------------------------
        body = build_body_m()
        eyes = build_eyes()
        nose = build_nose()
        mouth = build_mouth()
        hat = build_hat()

        # ----------------------------------------------------
        # Build limbs
        # ----------------------------------------------------
        #
        # Important:
        # hands should attach to the actual arms used in this scene
        # feet should attach to the actual legs used in this scene
        #
        arms = build_arms()
        hands = build_hands(
            left_arm=arms.left_arm,
            right_arm=arms.right_arm,
        )

        legs = build_legs()
        feet = build_feet(
            left_leg=legs.left_leg,
            right_leg=legs.right_leg,
        )

        creature_with_limbs = VGroup(
            body,
            eyes,
            nose,
            mouth,
            hat,
            arms,
            hands,
            legs,
            feet,
        )
        creature_with_limbs.name = "test_limbs_scene_creature"

        title = Text("Full Static Creature With Limbs")
        title.scale(0.5)
        title.next_to(creature_with_limbs, DOWN, buff=0.7)

        scene_group = VGroup(creature_with_limbs, title)
        scene_group.name = test_scene_name("limbs")

        if LOG_SCENE_EVENTS:
            logger.info(
                "Limbs test content built | arms=%s hands=%s legs=%s feet=%s",
                arms is not None,
                hands is not None,
                legs is not None,
                feet is not None,
            )

        self.play(FadeIn(creature_with_limbs))
        self.play(FadeIn(title))
        self.wait(DEFAULT_WAIT_TIME)

        if DEFAULT_SHOW_DEBUG_LABELS:
            logger.debug(
                "TestLimbsScene debug | creature_group=%s scene_group=%s",
                getattr(creature_with_limbs, "name", "unnamed_creature_group"),
                getattr(scene_group, "name", "unnamed_scene_group"),
            )

        if LOG_SCENE_EVENTS:
            logger.info("Finished TestLimbsScene")