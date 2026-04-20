"""
Matrix intro lesson scene for mathlab-mylinehub-creature.

Purpose:
- introduce the visual idea of a matrix
- combine mascot + formula card + axis plane
- present a matrix as an organized rectangular array of numbers
- prepare for later lessons on transformations and matrix-vector products

Scene flow:
1. build creature on left
2. build formula card on right
3. build a small matrix text above/inside the card
4. optionally show an axis plane below
5. fade everything in
6. blink
7. mascot points toward the matrix
8. hold final teaching frame
"""

from __future__ import annotations

from manimlib import DOWN
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
from mathlab_creature.props.formula_card import build_formula_card

logger = get_logger(__name__)


class MatrixIntroScene(Scene):
    """
    First matrix introduction scene.
    """

    CONFIG = {
        "camera_config": {
            "background_color": DEFAULT_SCENE_BACKGROUND_COLOR,
        }
    }

    def construct(self) -> None:
        if LOG_SCENE_EVENTS:
            logger.info("Starting MatrixIntroScene")

        # ----------------------------------------------------
        # Build creature (left)
        # ----------------------------------------------------
        rig = build_body_rig(point(-3.3, 0.0, 0.0))
        creature_group = rig["group"]
        eyes_group = rig["face"]["eyes"]

        # ----------------------------------------------------
        # Build formula card (right, upper)
        # ----------------------------------------------------
        formula_card = build_formula_card()
        formula_card.scale(0.95)
        formula_card.move_to(point(3.2, 1.25, 0.0))

        # ----------------------------------------------------
        # Scene title
        # ----------------------------------------------------
        scene_title = Text("A Matrix Is An Organized Number Grid")
        scene_title.scale(0.50)
        scene_title.move_to(point(0.0, 3.2, 0.0))

        # ----------------------------------------------------
        # Build matrix content
        # ----------------------------------------------------
        matrix_title = Text("Matrix")
        matrix_title.scale(0.42)
        matrix_title.move_to(formula_card.get_center() + point(0.0, 0.52, 0.0))

        matrix_text = Text("[ 1   2 ]\n[ 3   4 ]")
        matrix_text.scale(0.55)
        matrix_text.move_to(formula_card.get_center() + point(0.0, -0.08, 0.0))

        matrix_group = VGroup(matrix_title, matrix_text)
        matrix_group.name = "matrix_intro_matrix_group"

        # ----------------------------------------------------
        # Optional axis plane (right, lower)
        # ----------------------------------------------------
        axis_plane = build_axis_plane(show_grid=True)
        axis_plane.scale(0.38)
        axis_plane.move_to(point(3.2, -1.55, 0.0))

        axis_label = Text("Later: matrix acts on vectors")
        axis_label.scale(0.28)
        axis_label.move_to(axis_plane.get_center() + point(0.0, -1.55, 0.0))

        # ----------------------------------------------------
        # Group lesson objects
        # ----------------------------------------------------
        lesson_group = VGroup(
            creature_group,
            formula_card,
            matrix_group,
            axis_plane,
            axis_label,
            scene_title,
        )
        lesson_group.name = "matrix_intro_scene_group"

        # Local pacing values for easier tuning
        intro_pause = 0.30
        blink_pause = 0.20
        matrix_pause = 0.30
        axis_pause = 0.30
        final_pause = DEFAULT_WAIT_TIME

        # ----------------------------------------------------
        # Intro appearance
        # ----------------------------------------------------
        if LOG_SCENE_EVENTS:
            logger.info("Running matrix-intro fade-in")

        self.play(
            FadeIn(creature_group),
            FadeIn(formula_card),
            FadeIn(axis_plane),
            FadeIn(scene_title),
        )
        self.wait(intro_pause)

        # ----------------------------------------------------
        # Blink before teaching
        # ----------------------------------------------------
        if LOG_SCENE_EVENTS:
            logger.info("Running matrix-intro blink")

        self.play(build_blink_animation(eyes_group))
        self.wait(blink_pause)

        # ----------------------------------------------------
        # Show matrix content
        # ----------------------------------------------------
        if LOG_SCENE_EVENTS:
            logger.info("Running matrix-intro matrix reveal")

        self.play(Write(matrix_group))
        self.wait(matrix_pause)

        self.play(Write(axis_label))
        self.wait(axis_pause)

        # ----------------------------------------------------
        # Point toward matrix card
        # ----------------------------------------------------
        if LOG_SCENE_EVENTS:
            logger.info("Running matrix-intro pointing action")

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
                "MatrixIntroScene debug | lesson_group=%s card_center=%s axis_center=%s",
                getattr(lesson_group, "name", "unnamed_lesson_group"),
                formula_card.get_center(),
                axis_plane.get_center(),
            )

        if LOG_SCENE_EVENTS:
            logger.info("Finished MatrixIntroScene")