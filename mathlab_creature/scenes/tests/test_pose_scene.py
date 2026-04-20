"""
Pose test scene for mathlab-mylinehub-creature.

Purpose:
- verify the structured body rig builds correctly
- test pose application on the rig
- compare multiple static poses in one scene
- confirm hands remain attached after arm rotations
- validate pose readability before action animation is added

This scene renders several copies of the creature rig in different poses.
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

from mathlab_creature.core.geometry import point
from mathlab_creature.core.logger import get_logger
from mathlab_creature.core.naming import test_scene_name

from mathlab_creature.creature.poses.happy_pose import apply_happy_pose
from mathlab_creature.creature.poses.neutral_pose import apply_neutral_pose
from mathlab_creature.creature.poses.pointing_pose import apply_pointing_pose
from mathlab_creature.creature.poses.teacher_pose import apply_teacher_pose
from mathlab_creature.creature.poses.thinking_pose import apply_thinking_pose
from mathlab_creature.creature.rigs.body_rig import build_body_rig

logger = get_logger(__name__)


class TestPoseScene(Scene):
    """
    Render multiple rig copies with different poses for pose validation.
    """

    CONFIG = {
        "camera_config": {
            "background_color": DEFAULT_SCENE_BACKGROUND_COLOR,
        }
    }

    def construct(self) -> None:
        if LOG_SCENE_EVENTS:
            logger.info("Starting TestPoseScene")

        # ----------------------------------------------------
        # Build rig copies at different horizontal positions
        # ----------------------------------------------------
        neutral_rig = build_body_rig(point(-5.2, 0.0, 0.0))
        happy_rig = build_body_rig(point(-2.6, 0.0, 0.0))
        teacher_rig = build_body_rig(point(0.0, 0.0, 0.0))
        pointing_rig = build_body_rig(point(2.6, 0.0, 0.0))
        thinking_rig = build_body_rig(point(5.2, 0.0, 0.0))

        # ----------------------------------------------------
        # Apply poses
        # ----------------------------------------------------
        apply_neutral_pose(neutral_rig)
        apply_happy_pose(happy_rig)
        apply_teacher_pose(teacher_rig)
        apply_pointing_pose(pointing_rig)
        apply_thinking_pose(thinking_rig)

        # ----------------------------------------------------
        # Labels
        # ----------------------------------------------------
        neutral_label = Text("Neutral").scale(0.4)
        happy_label = Text("Happy").scale(0.4)
        teacher_label = Text("Teacher").scale(0.4)
        pointing_label = Text("Pointing").scale(0.4)
        thinking_label = Text("Thinking").scale(0.4)

        neutral_label.next_to(neutral_rig["group"], DOWN, buff=0.45)
        happy_label.next_to(happy_rig["group"], DOWN, buff=0.45)
        teacher_label.next_to(teacher_rig["group"], DOWN, buff=0.45)
        pointing_label.next_to(pointing_rig["group"], DOWN, buff=0.45)
        thinking_label.next_to(thinking_rig["group"], DOWN, buff=0.45)

        # ----------------------------------------------------
        # Group all visible rig groups
        # ----------------------------------------------------
        pose_gallery = VGroup(
            neutral_rig["group"],
            happy_rig["group"],
            teacher_rig["group"],
            pointing_rig["group"],
            thinking_rig["group"],
            neutral_label,
            happy_label,
            teacher_label,
            pointing_label,
            thinking_label,
        )
        pose_gallery.name = test_scene_name("pose")

        if LOG_SCENE_EVENTS:
            logger.info(
                "Pose gallery built | neutral=%s happy=%s teacher=%s pointing=%s thinking=%s",
                neutral_rig["group"] is not None,
                happy_rig["group"] is not None,
                teacher_rig["group"] is not None,
                pointing_rig["group"] is not None,
                thinking_rig["group"] is not None,
            )

        self.play(FadeIn(pose_gallery))
        self.wait(DEFAULT_WAIT_TIME)

        if DEFAULT_SHOW_DEBUG_LABELS:
            logger.debug(
                "TestPoseScene debug | gallery_name=%s",
                getattr(pose_gallery, "name", "unnamed_pose_gallery"),
            )

        if LOG_SCENE_EVENTS:
            logger.info("Finished TestPoseScene")