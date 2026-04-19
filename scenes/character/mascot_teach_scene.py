"""
Mascot teaching scene for mathlab-mylinehub-creature.

Purpose:
- combine mascot + props into a first teaching-style scene
- simulate a simple "explaining something on a board" moment
- use pointer + board + pointing action together

Scene flow:
1. build creature rig slightly left
2. build math board on the right
3. build pointer stick
4. attach pointer to right hand
5. fade everything in
6. blink
7. point toward board (with pointer)
8. hold teaching pose
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

from creature.actions.blink_action import build_blink_animation
from creature.actions.point_action import build_point_animation
from creature.rigs.body_rig import build_body_rig

from props.math_board import build_math_board
from props.pointer_stick import build_pointer_stick

logger = get_logger(__name__)


class MascotTeachScene(Scene):
    """
    First teaching-style scene combining mascot and props.
    """

    CONFIG = {
        "camera_config": {
            "background_color": DEFAULT_SCENE_BACKGROUND_COLOR,
        }
    }

    def _attach_pointer_to_right_hand(self, rig: dict, pointer) -> None:
        """
        Attach pointer to the current right-hand position.

        Version 1 keeps the attachment simple:
        - place pointer center at right hand center
        - use one readable teaching angle
        """
        right_hand = rig["arms"]["right_hand"]
        pointer.move_to(right_hand.get_center())
        pointer.rotate(-0.6)

    def construct(self) -> None:
        if LOG_SCENE_EVENTS:
            logger.info("Starting MascotTeachScene")

        # ----------------------------------------------------
        # Build creature
        # ----------------------------------------------------
        rig = build_body_rig(point(-3.0, 0.0, 0.0))
        creature_group = rig["group"]
        eyes_group = rig["face"]["eyes"]

        # ----------------------------------------------------
        # Build props
        # ----------------------------------------------------
        board = build_math_board()
        board.scale(0.7)
        board.move_to(point(3.2, 0.8, 0.0))

        pointer = build_pointer_stick()
        pointer.scale(0.9)

        # ----------------------------------------------------
        # Attach pointer to right hand
        # ----------------------------------------------------
        self._attach_pointer_to_right_hand(rig, pointer)

        # ----------------------------------------------------
        # Optional scene title
        # ----------------------------------------------------
        title = Text("MYLINEHUB Teaching Scene")
        title.scale(0.48)
        title.next_to(creature_group, DOWN, buff=0.7)

        scene_group = VGroup(
            creature_group,
            board,
            pointer,
            title,
        )
        scene_group.name = "mascot_teach_scene_group"

        # Local pacing values
        intro_pause = 0.20
        blink_pause = 0.15
        final_pause = DEFAULT_WAIT_TIME

        # ----------------------------------------------------
        # Intro appearance
        # ----------------------------------------------------
        if LOG_SCENE_EVENTS:
            logger.info("Running teach-scene fade-in")

        self.play(FadeIn(creature_group), FadeIn(board), FadeIn(pointer))
        self.play(FadeIn(title))
        self.wait(intro_pause)

        # ----------------------------------------------------
        # Blink before teaching
        # ----------------------------------------------------
        if LOG_SCENE_EVENTS:
            logger.info("Running teach-scene blink")

        self.play(build_blink_animation(eyes_group))
        self.wait(blink_pause)

        # ----------------------------------------------------
        # Point toward board
        # ----------------------------------------------------
        if LOG_SCENE_EVENTS:
            logger.info("Running teach-scene pointing action")

        self.play(
            build_point_animation(
                rig,
                side="right",
                hold=True,
                return_to_neutral=False,
            )
        )

        # Reattach pointer after the arm/hand motion so it stays visually aligned.
        self._attach_pointer_to_right_hand(rig, pointer)

        self.wait(final_pause)

        if DEFAULT_SHOW_DEBUG_LABELS:
            logger.debug(
                "MascotTeachScene debug | scene_group=%s board_center=%s pointer_center=%s",
                getattr(scene_group, "name", "unnamed_scene_group"),
                board.get_center(),
                pointer.get_center(),
            )

        if LOG_SCENE_EVENTS:
            logger.info("Finished MascotTeachScene")