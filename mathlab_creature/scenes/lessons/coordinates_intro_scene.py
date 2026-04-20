"""
Coordinates intro lesson scene for mathlab-mylinehub-creature.

Purpose:
- introduce the idea of coordinates (x, y)
- combine mascot + axis plane + point visualization
- show how a point maps to horizontal and vertical values

Scene flow:
1. build creature on left
2. build axis plane on right
3. fade both in
4. blink
5. show a point on the plane
6. draw horizontal (x) projection
7. draw vertical (y) projection
8. mascot points toward the point
"""

from __future__ import annotations

from manimlib import DOWN, UP, RIGHT
from manimlib import Dot, FadeIn, Line, Scene, Text, VGroup, Write

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


class CoordinatesIntroScene(Scene):
    """
    Coordinate system introduction scene.
    """

    CONFIG = {
        "camera_config": {
            "background_color": DEFAULT_SCENE_BACKGROUND_COLOR,
        }
    }

    def construct(self) -> None:
        if LOG_SCENE_EVENTS:
            logger.info("Starting CoordinatesIntroScene")

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

        plane_center = axis_plane.get_center()

        # ----------------------------------------------------
        # Scene title
        # ----------------------------------------------------
        scene_title = Text("A Point Has Coordinates (x, y)")
        scene_title.scale(0.52)
        scene_title.move_to(point(0.0, 3.2, 0.0))

        # ----------------------------------------------------
        # Create a point on the plane
        # ----------------------------------------------------
        px, py = 1.5, 1.0
        point_position = plane_center + point(px, py, 0.0)

        p = Dot(point_position)
        p.name = "coordinates_intro_point"

        # ----------------------------------------------------
        # Projection lines
        # ----------------------------------------------------
        x_projection_target = point(
            plane_center[0] + px,
            plane_center[1],
            0.0,
        )
        y_projection_target = point(
            plane_center[0],
            plane_center[1] + py,
            0.0,
        )

        x_proj = Line(
            x_projection_target,
            point_position,
        )
        y_proj = Line(
            y_projection_target,
            point_position,
        )

        x_proj.name = "coordinates_intro_x_projection"
        y_proj.name = "coordinates_intro_y_projection"

        # ----------------------------------------------------
        # Coordinate labels
        # ----------------------------------------------------
        coord_label = Text(f"({px}, {py})")
        coord_label.scale(0.5)
        coord_label.next_to(p, UP + RIGHT, buff=0.18)

        x_label = Text("x")
        x_label.scale(0.42)
        x_label.next_to(x_proj, DOWN, buff=0.12)

        y_label = Text("y")
        y_label.scale(0.42)
        y_label.next_to(y_proj, RIGHT, buff=0.12)

        lesson_group = VGroup(
            creature_group,
            axis_plane,
            p,
            x_proj,
            y_proj,
            coord_label,
            x_label,
            y_label,
            scene_title,
        )
        lesson_group.name = "coordinates_intro_scene_group"

        # Local pacing values for easier tuning
        intro_pause = 0.30
        blink_pause = 0.20
        point_pause = 0.20
        projection_pause = 0.30
        label_pause = 0.30
        final_pause = DEFAULT_WAIT_TIME

        # ----------------------------------------------------
        # Intro appearance
        # ----------------------------------------------------
        if LOG_SCENE_EVENTS:
            logger.info("Running coordinates-intro fade-in")

        self.play(FadeIn(creature_group), FadeIn(axis_plane), FadeIn(scene_title))
        self.wait(intro_pause)

        # ----------------------------------------------------
        # Blink
        # ----------------------------------------------------
        if LOG_SCENE_EVENTS:
            logger.info("Running coordinates-intro blink")

        self.play(build_blink_animation(eyes_group))
        self.wait(blink_pause)

        # ----------------------------------------------------
        # Show point
        # ----------------------------------------------------
        if LOG_SCENE_EVENTS:
            logger.info("Running coordinates-intro point reveal")

        self.play(FadeIn(p))
        self.wait(point_pause)

        # ----------------------------------------------------
        # Draw projections
        # ----------------------------------------------------
        if LOG_SCENE_EVENTS:
            logger.info("Running coordinates-intro projection draw")

        self.play(Write(x_proj), Write(y_proj))
        self.wait(projection_pause)

        # ----------------------------------------------------
        # Show labels
        # ----------------------------------------------------
        if LOG_SCENE_EVENTS:
            logger.info("Running coordinates-intro label reveal")

        self.play(FadeIn(x_label), FadeIn(y_label), Write(coord_label))
        self.wait(label_pause)

        # ----------------------------------------------------
        # Mascot points
        # ----------------------------------------------------
        if LOG_SCENE_EVENTS:
            logger.info("Running coordinates-intro pointing action")

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
                "CoordinatesIntroScene debug | lesson_group=%s point_center=%s plane_center=%s",
                getattr(lesson_group, "name", "unnamed_lesson_group"),
                p.get_center(),
                plane_center,
            )

        if LOG_SCENE_EVENTS:
            logger.info("Finished CoordinatesIntroScene")