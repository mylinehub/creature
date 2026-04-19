"""
Props test scene for mathlab-mylinehub-creature.

Purpose:
- verify all current props can be built together
- compare their scale visually
- make prop debugging easier before final teaching scenes
- serve as one shared prop playground

This scene tests:
- pointer stick
- math board
- formula card
- axis plane
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

from core.geometry import point
from core.logger import get_logger
from core.naming import test_scene_name

from props.axis_plane import build_axis_plane
from props.formula_card import build_formula_card
from props.math_board import build_math_board
from props.pointer_stick import build_pointer_stick

logger = get_logger(__name__)


class TestPropsScene(Scene):
    """
    Render all current props together for visual testing.

    This scene is a shared prop playground for:
    - scale comparison
    - spacing comparison
    - rough layout validation
    - early visual debugging
    """

    CONFIG = {
        "camera_config": {
            "background_color": DEFAULT_SCENE_BACKGROUND_COLOR,
        }
    }

    def construct(self) -> None:
        if LOG_SCENE_EVENTS:
            logger.info("Starting TestPropsScene")

        # ----------------------------------------------------
        # Build props
        # ----------------------------------------------------
        pointer = build_pointer_stick()
        board = build_math_board()
        formula_card = build_formula_card()
        axis_plane = build_axis_plane(show_grid=True)

        # ----------------------------------------------------
        # Scale props for test layout
        # ----------------------------------------------------
        pointer.scale(1.2)
        board.scale(0.55)
        formula_card.scale(0.85)
        axis_plane.scale(0.42)

        # ----------------------------------------------------
        # Position props
        # ----------------------------------------------------
        board.move_to(point(-3.6, 1.0, 0.0))
        formula_card.move_to(point(3.5, 1.3, 0.0))
        axis_plane.move_to(point(3.5, -1.3, 0.0))

        pointer.rotate(-0.55)
        pointer.move_to(point(-3.6, -1.5, 0.0))

        # ----------------------------------------------------
        # Labels
        # ----------------------------------------------------
        board_label = Text("Math Board").scale(0.35)
        board_label.next_to(board, DOWN, buff=0.2)

        card_label = Text("Formula Card").scale(0.35)
        card_label.next_to(formula_card, DOWN, buff=0.2)

        plane_label = Text("Axis Plane").scale(0.35)
        plane_label.next_to(axis_plane, DOWN, buff=0.2)

        pointer_label = Text("Pointer Stick").scale(0.35)
        pointer_label.next_to(pointer, DOWN, buff=0.2)

        # ----------------------------------------------------
        # Group everything
        # ----------------------------------------------------
        prop_gallery = VGroup(
            board,
            formula_card,
            axis_plane,
            pointer,
            board_label,
            card_label,
            plane_label,
            pointer_label,
        )
        prop_gallery.name = test_scene_name("props")

        if LOG_SCENE_EVENTS:
            logger.info(
                "Props test content built | pointer=%s board=%s formula_card=%s axis_plane=%s",
                pointer is not None,
                board is not None,
                formula_card is not None,
                axis_plane is not None,
            )

        self.play(FadeIn(prop_gallery))
        self.wait(DEFAULT_WAIT_TIME)

        if DEFAULT_SHOW_DEBUG_LABELS:
            logger.debug(
                "TestPropsScene debug | gallery_name=%s",
                getattr(prop_gallery, "name", "unnamed_prop_gallery"),
            )

        if LOG_SCENE_EVENTS:
            logger.info("Finished TestPropsScene")