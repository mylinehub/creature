# File: render_scene.py

"""
MASTER RENDER SCENE (ENHANCED + AUDIO)
mathlab-mylinehub-creature

Upgrades:
- strong scene pacing
- attention control (look → show → point)
- micro pauses
- reusable section structure
- cleaner teaching flow
- closer to 3b1b storytelling rhythm
- procedural audio integration
- optional sound-enabled actions
"""

from __future__ import annotations

from manimlib import (
    Scene,
    FadeIn,
    FadeOut,
    Text,
    Write,
)

from mathlab_creature.core.logger import (
    get_logger,
)

from mathlab_creature.core.geometry import (
    point,
)

from mathlab_creature.core.audio.audio_server import (
    boot_audio_server,
    shutdown_audio_server,
)

from mathlab_creature.creature.rigs.body_rig import (
    build_body_rig,
)

from mathlab_creature.creature.actions.blink_action import (
    build_blink_animation,
)

from mathlab_creature.creature.actions.look_action import (
    build_look_animation,
    build_look_center_animation,
)

from mathlab_creature.creature.actions.wave_action import (
    build_wave_animation,
)

from mathlab_creature.creature.actions.walk_action import (
    build_walk_animation,
)

from mathlab_creature.creature.actions.point_action import (
    build_point_animation,
)

from mathlab_creature.creature.actions.hop_action import (
    build_hop_animation,
)

from mathlab_creature.props.pointer_stick import (
    build_pointer_stick,
)

from mathlab_creature.props.math_board import (
    build_math_board,
)

from mathlab_creature.props.axis_plane import (
    build_axis_plane,
)

from mathlab_creature.props.formula_card import (
    build_formula_card,
)

logger = get_logger(__name__)


class MasterRenderScene(Scene):

    def construct(self):

        logger.info(
            "Starting MasterRenderScene"
        )

        # =====================================================
        # AUDIO BOOT
        # =====================================================

        boot_audio_server()

        # =====================================================
        # GLOBAL AUDIO TOGGLE
        # =====================================================

        WITH_SOUND = True

        # =====================================================
        # BUILD CORE
        # =====================================================

        rig = build_body_rig(
            point(0, 0, 0)
        )

        creature = rig["group"]

        eyes = rig["face"]["eyes"]

        # =====================================================
        # TITLE
        # =====================================================

        title = (
            Text("MYLINEHUB MathLab")
            .scale(0.7)
        )

        title.to_edge([0, 1, 0])

        self.play(
            FadeIn(creature),
            FadeIn(title),
        )

        self.wait(0.6)

        # -----------------------------------------------------
        # BLINK
        # -----------------------------------------------------

        self.play(
            build_blink_animation(
                eyes,
                with_sound=WITH_SOUND,
            )
        )

        self.wait(0.3)

        # =====================================================
        # SECTION 1 — GREETING (Wave)
        # =====================================================

        self.play(
            build_look_center_animation(
                eyes,
            )
        )

        self.wait(0.2)

        self.play(
            build_wave_animation(
                rig,
                cycles=2,
                with_sound=WITH_SOUND,
            )
        )

        self.wait(0.6)

        # =====================================================
        # SECTION 2 — MOVEMENT (Walk)
        # =====================================================

        self.play(
            build_walk_animation(
                rig,
                cycles=2,
                with_sound=WITH_SOUND,
            )
        )

        self.wait(0.5)

        # -----------------------------------------------------
        # RESET POSITION
        # -----------------------------------------------------

        self.play(
            creature.animate.move_to(
                point(0, 0, 0)
            )
        )

        self.wait(0.3)

        # =====================================================
        # SECTION 3 — ATTENTION DEMO
        # =====================================================

        label = (
            Text("Focus Here")
            .scale(0.5)
        )

        label.move_to(
            point(3, 1, 0)
        )

        self.play(
            FadeIn(label)
        )

        # -----------------------------------------------------
        # LOOK FIRST
        # -----------------------------------------------------

        self.play(
            build_look_animation(
                eyes,
                "right",
                with_sound=WITH_SOUND,
            )
        )

        self.wait(0.25)

        # -----------------------------------------------------
        # POINT
        # -----------------------------------------------------

        self.play(
            build_point_animation(
                rig,
                hold=True,
                with_sound=WITH_SOUND,
            )
        )

        self.wait(0.6)

        self.play(
            FadeOut(label)
        )

        self.wait(0.3)

        # =====================================================
        # SECTION 4 — TEACH MODE
        # =====================================================

        board = (
            build_math_board()
            .scale(0.7)
        )

        board.move_to(
            point(3, 0.5, 0)
        )

        pointer = (
            build_pointer_stick()
            .scale(0.8)
        )

        right_hand = (
            rig["arms"]["right_hand"]
        )

        pointer.move_to(
            right_hand.get_center()
        )

        pointer.rotate(-0.6)

        self.play(
            FadeIn(board),
            FadeIn(pointer),
        )

        # -----------------------------------------------------
        # LOOK
        # -----------------------------------------------------

        self.play(
            build_look_animation(
                eyes,
                "right",
                with_sound=WITH_SOUND,
            )
        )

        self.wait(0.2)

        # -----------------------------------------------------
        # POINT
        # -----------------------------------------------------

        self.play(
            build_point_animation(
                rig,
                hold=True,
                with_sound=WITH_SOUND,
            )
        )

        self.wait(0.6)

        self.play(
            FadeOut(board),
            FadeOut(pointer),
        )

        self.wait(0.3)

        # =====================================================
        # SECTION 5 — COORDINATES
        # =====================================================

        axis = (
            build_axis_plane()
            .scale(0.5)
        )

        axis.move_to(
            point(3, 0, 0)
        )

        dot_label = (
            Text("(x, y)")
            .scale(0.4)
        )

        dot_label.move_to(
            point(3.5, 1, 0)
        )

        self.play(
            FadeIn(axis)
        )

        self.wait(0.2)

        self.play(
            Write(dot_label)
        )

        self.wait(0.2)

        self.play(
            build_look_animation(
                eyes,
                "right",
                with_sound=WITH_SOUND,
            )
        )

        self.wait(0.2)

        self.play(
            build_point_animation(
                rig,
                hold=True,
                with_sound=WITH_SOUND,
            )
        )

        self.wait(0.6)

        self.play(
            FadeOut(dot_label),
            FadeOut(axis),
        )

        self.wait(0.3)

        # =====================================================
        # SECTION 6 — VECTOR INTRO
        # =====================================================

        axis = (
            build_axis_plane()
            .scale(0.5)
        )

        axis.move_to(
            point(3, 0, 0)
        )

        vector_text = (
            Text(
                "Vector = direction + magnitude"
            )
            .scale(0.4)
        )

        vector_text.move_to(
            point(3.5, 1, 0)
        )

        self.play(
            FadeIn(axis)
        )

        self.wait(0.2)

        self.play(
            Write(vector_text)
        )

        self.wait(0.2)

        self.play(
            build_look_animation(
                eyes,
                "right",
                with_sound=WITH_SOUND,
            )
        )

        self.wait(0.2)

        self.play(
            build_point_animation(
                rig,
                hold=True,
                with_sound=WITH_SOUND,
            )
        )

        self.wait(0.6)

        self.play(
            FadeOut(axis),
            FadeOut(vector_text),
        )

        self.wait(0.3)

        # =====================================================
        # SECTION 7 — MATRIX INTRO
        # =====================================================

        card = (
            build_formula_card()
            .scale(0.9)
        )

        card.move_to(
            point(3, 0.5, 0)
        )

        matrix = (
            Text("[1 2]\n[3 4]")
            .scale(0.6)
        )

        matrix.move_to(
            card.get_center()
        )

        label = (
            Text("Matrix")
            .scale(0.4)
        )

        label.move_to(
            point(3, 1.5, 0)
        )

        self.play(
            FadeIn(card)
        )

        self.wait(0.2)

        self.play(
            Write(matrix),
            Write(label),
        )

        self.wait(0.2)

        self.play(
            build_look_animation(
                eyes,
                "right",
                with_sound=WITH_SOUND,
            )
        )

        self.wait(0.2)

        self.play(
            build_point_animation(
                rig,
                hold=True,
                with_sound=WITH_SOUND,
            )
        )

        self.wait(0.8)

        self.play(
            FadeOut(card),
            FadeOut(matrix),
            FadeOut(label),
        )

        self.wait(0.3)

        # =====================================================
        # FINAL
        # =====================================================

        final_text = (
            Text("Math becomes visual.")
            .scale(0.6)
        )

        final_text.move_to(
            point(0, 2, 0)
        )

        self.play(
            Write(final_text)
        )

        self.wait(0.2)

        self.play(
            build_hop_animation(
                rig,
                with_sound=WITH_SOUND,
            )
        )

        self.wait(1.2)

        # =====================================================
        # AUDIO SHUTDOWN
        # =====================================================

        shutdown_audio_server()

        logger.info(
            "Finished MasterRenderScene"
        )