"""
MASTER RENDER SCENE (ENHANCED)
mathlab-mylinehub-creature

Upgrades:
- strong scene pacing
- attention control (look → show → point)
- micro pauses
- reusable section structure
- cleaner teaching flow
- closer to 3b1b storytelling rhythm
"""

from __future__ import annotations

from manimlib import Scene, FadeIn, FadeOut, Text, VGroup, Write

from core.logger import get_logger
from core.geometry import point

from creature.rigs.body_rig import build_body_rig
from creature.actions.blink_action import build_blink_animation
from creature.actions.look_action import (
    build_look_animation,
    build_look_center_animation,
)
from creature.actions.wave_action import build_wave_animation
from creature.actions.walk_action import build_walk_animation
from creature.actions.point_action import build_point_animation
from creature.actions.hop_action import build_hop_animation

from props.pointer_stick import build_pointer_stick
from props.math_board import build_math_board
from props.axis_plane import build_axis_plane
from props.formula_card import build_formula_card

logger = get_logger(__name__)


class MasterRenderScene(Scene):

    def construct(self):
        logger.info("Starting MasterRenderScene")

        # =====================================================
        # BUILD CORE
        # =====================================================

        rig = build_body_rig(point(0, 0, 0))
        creature = rig["group"]
        eyes = rig["face"]["eyes"]

        # =====================================================
        # TITLE
        # =====================================================

        title = Text("MYLINEHUB MathLab").scale(0.7)
        title.to_edge([0, 1, 0])

        self.play(FadeIn(creature), FadeIn(title))
        self.wait(0.6)

        self.play(build_blink_animation(eyes))
        self.wait(0.3)

        # =====================================================
        # SECTION 1 — GREETING (Wave)
        # =====================================================

        self.play(build_look_center_animation(eyes))
        self.wait(0.2)

        self.play(build_wave_animation(rig, cycles=2))
        self.wait(0.6)

        # =====================================================
        # SECTION 2 — MOVEMENT (Walk)
        # =====================================================

        self.play(build_walk_animation(rig, cycles=2))
        self.wait(0.5)

        # Reset position cleanly
        self.play(creature.animate.move_to(point(0, 0, 0)))
        self.wait(0.3)

        # =====================================================
        # SECTION 3 — ATTENTION DEMO
        # =====================================================

        label = Text("Focus Here").scale(0.5)
        label.move_to(point(3, 1, 0))

        self.play(FadeIn(label))

        # 🔥 IMPORTANT: LOOK FIRST (3b1b rule)
        self.play(build_look_animation(eyes, "right"))
        self.wait(0.25)

        self.play(build_point_animation(rig, hold=True))
        self.wait(0.6)

        self.play(FadeOut(label))
        self.wait(0.3)

        # =====================================================
        # SECTION 4 — TEACH MODE (Board + Pointer)
        # =====================================================

        board = build_math_board().scale(0.7)
        board.move_to(point(3, 0.5, 0))

        pointer = build_pointer_stick().scale(0.8)

        right_hand = rig["arms"]["right_hand"]
        pointer.move_to(right_hand.get_center())
        pointer.rotate(-0.6)

        self.play(FadeIn(board), FadeIn(pointer))

        # LOOK → POINT
        self.play(build_look_animation(eyes, "right"))
        self.wait(0.2)

        self.play(build_point_animation(rig, hold=True))
        self.wait(0.6)

        self.play(FadeOut(board), FadeOut(pointer))
        self.wait(0.3)

        # =====================================================
        # SECTION 5 — COORDINATES
        # =====================================================

        axis = build_axis_plane().scale(0.5)
        axis.move_to(point(3, 0, 0))

        dot_label = Text("(x, y)").scale(0.4)
        dot_label.move_to(point(3.5, 1, 0))

        self.play(FadeIn(axis))
        self.wait(0.2)

        self.play(Write(dot_label))
        self.wait(0.2)

        self.play(build_look_animation(eyes, "right"))
        self.wait(0.2)

        self.play(build_point_animation(rig, hold=True))
        self.wait(0.6)

        self.play(FadeOut(dot_label), FadeOut(axis))
        self.wait(0.3)

        # =====================================================
        # SECTION 6 — VECTOR INTRO
        # =====================================================

        axis = build_axis_plane().scale(0.5)
        axis.move_to(point(3, 0, 0))

        vector_text = Text("Vector = direction + magnitude").scale(0.4)
        vector_text.move_to(point(3.5, 1, 0))

        self.play(FadeIn(axis))
        self.wait(0.2)

        self.play(Write(vector_text))
        self.wait(0.2)

        self.play(build_look_animation(eyes, "right"))
        self.wait(0.2)

        self.play(build_point_animation(rig, hold=True))
        self.wait(0.6)

        self.play(FadeOut(axis), FadeOut(vector_text))
        self.wait(0.3)

        # =====================================================
        # SECTION 7 — MATRIX INTRO
        # =====================================================

        card = build_formula_card().scale(0.9)
        card.move_to(point(3, 0.5, 0))

        matrix = Text("[1 2]\n[3 4]").scale(0.6)
        matrix.move_to(card.get_center())

        label = Text("Matrix").scale(0.4)
        label.move_to(point(3, 1.5, 0))

        self.play(FadeIn(card))
        self.wait(0.2)

        self.play(Write(matrix), Write(label))
        self.wait(0.2)

        self.play(build_look_animation(eyes, "right"))
        self.wait(0.2)

        self.play(build_point_animation(rig, hold=True))
        self.wait(0.8)

        self.play(FadeOut(card), FadeOut(matrix), FadeOut(label))
        self.wait(0.3)

        # =====================================================
        # FINAL
        # =====================================================

        final_text = Text("Math becomes visual.").scale(0.6)
        final_text.move_to(point(0, 2, 0))

        self.play(Write(final_text))
        self.wait(0.2)

        self.play(build_hop_animation(rig))
        self.wait(1.2)

        logger.info("Finished MasterRenderScene")