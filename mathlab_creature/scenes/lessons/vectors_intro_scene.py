"""
Vectors intro lesson scene for mathlab-mylinehub-creature.

Purpose:
- first real math teaching scene
- combine mascot + axis plane + vector visualization
- introduce the idea of a vector as direction + magnitude

Scene flow:
1. build creature on left
2. build axis plane on right
3. fade both in
4. blink
5. draw a vector arrow
6. mascot points toward vector
7. slight pause for teaching moment
"""

from __future__ import annotations

from manimlib import DOWN
from manimlib import Arrow
from manimlib import FadeIn
from manimlib import Scene
from manimlib import Text
from manimlib import VGroup
from manimlib import Write

from mathlab_creature.config.defaults import DEFAULT_SCENE_BACKGROUND_COLOR
from mathlab_creature.config.defaults import DEFAULT_WAIT_TIME
from mathlab_creature.config.defaults import DEFAULT_SHOW_DEBUG_LABELS
from mathlab_creature.config.defaults import LOG_SCENE_EVENTS

from mathlab_creature.core.geometry import point
from mathlab_creature.core.logger import get_logger

from mathlab_creature.creature.actions.blink_action import build_blink_animation
from mathlab_creature.creature.actions.point_action import build_point_animation
from mathlab_creature.creature.rigs.body_rig import build_body_rig

from mathlab_creature.props.axis_plane import build_axis_plane

logger = get_logger(__name__)


class VectorsIntroScene(Scene):
    """
    First vector introduction scene.
    """

    CONFIG = {
        "camera_config": {
            "background_color": DEFAULT_SCENE_BACKGROUND_COLOR,
        }
    }

    def construct(self) -> None:
        if LOG_SCENE_EVENTS:
            logger.info("Starting VectorsIntroScene")

        # ----------------------------------------------------
        # Build creature (left)
        # ----------------------------------------------------
        rig = build_body_rig(point(-3.2, 0.0, 0.0))
        creature_group = rig["group"]
        eyes_group = rig["face"]["eyes"]

        # ----------------------------------------------------
        # Build axis plane (right)
        # ----------------------------------------------------
        axis_plane = build_axis_plane(show_grid=True)
        axis_plane.scale(0.6)
        axis_plane.move_to(point(3.0, 0.0, 0.0))

        # ----------------------------------------------------
        # Scene title
        # ----------------------------------------------------
        scene_title = Text("Vector = Direction + Magnitude")
        scene_title.scale(0.52)
        scene_title.move_to(point(0.0, 3.2, 0.0))

        # ----------------------------------------------------
        # Build vector arrow
        # ----------------------------------------------------
        #
        # Build the vector relative to the axis-plane center so the lesson
        # reads clearly as "vector on a coordinate plane".
        plane_center = axis_plane.get_center()
        vector_start = plane_center
        vector_end = plane_center + point(1.05, 0.75, 0.0)

        vector = Arrow(
            start=vector_start,
            end=vector_end,
            buff=0,
        )
        vector.name = "lesson_vector_arrow"

        vector_label = Text("v")
        vector_label.scale(0.48)
        vector_label.next_to(vector.get_end(), DOWN, buff=0.18)

        lesson_group = VGroup(
            creature_group,
            axis_plane,
            vector,
            vector_label,
            scene_title,
        )
        lesson_group.name = "vectors_intro_scene_group"

        # Local pacing values for easier tuning
        intro_pause = 0.30
        blink_pause = 0.20
        vector_pause = 0.30
        final_pause = DEFAULT_WAIT_TIME

        # ----------------------------------------------------
        # Intro appearance
        # ----------------------------------------------------
        if LOG_SCENE_EVENTS:
            logger.info("Running vectors-intro fade-in")

        self.play(FadeIn(creature_group), FadeIn(axis_plane), FadeIn(scene_title))
        self.wait(intro_pause)

        # ----------------------------------------------------
        # Blink before teaching
        # ----------------------------------------------------
        if LOG_SCENE_EVENTS:
            logger.info("Running vectors-intro blink")

        self.play(build_blink_animation(eyes_group))
        self.wait(blink_pause)

        # ----------------------------------------------------
        # Draw vector
        # ----------------------------------------------------
        if LOG_SCENE_EVENTS:
            logger.info("Running vectors-intro vector draw")

        self.play(Write(vector), FadeIn(vector_label))
        self.wait(vector_pause)

        # ----------------------------------------------------
        # Point toward vector
        # ----------------------------------------------------
        if LOG_SCENE_EVENTS:
            logger.info("Running vectors-intro pointing action")

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
                "VectorsIntroScene debug | lesson_group=%s plane_center=%s vector_end=%s",
                getattr(lesson_group, "name", "unnamed_lesson_group"),
                plane_center,
                vector.get_end(),
            )

        if LOG_SCENE_EVENTS:
            logger.info("Finished VectorsIntroScene")