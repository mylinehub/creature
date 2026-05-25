"""
mathlab_creature/scenes/tests/test_balance_scene.py

BALANCE VALIDATION SCENE

Purpose
-------
Procedural balance and center-of-mass validation.

Tests:
- body lean
- center-of-mass
- stability
- balance recovery
- sway
- body tilt
- grounded feeling
- procedural weight shifting

IMPORTANT
---------
This scene ONLY validates:
BALANCE + WEIGHT.

NOT:
- walk-cycle tuning
- hierarchy debugging
- IK debugging
- controller debugging
"""

from __future__ import annotations

import numpy as np

from manimlib import *

from mathlab_creature.core.transforms import (
    vec3,
)

from mathlab_creature.core.debug_draw import (
    create_vector_debug,
)

from mathlab_creature.creature.rigs.body_rig import (
    build_body_rig,
)

from mathlab_creature.creature.controllers.movement_controller import (
    build_movement_controller,
)

from mathlab_creature.creature.controllers.rotation_controller import (
    build_rotation_controller,
)

from mathlab_creature.creature.controllers.camera_controller import (
    build_camera_controller,
)


# =========================================================
# SCENE
# =========================================================

class TestBalanceScene(MovingCameraScene):
    """
    Procedural balance validation scene.
    """

    def construct(self):

        # -------------------------------------------------
        # GRID
        # -------------------------------------------------

        plane = NumberPlane(
            x_range=(-14, 14, 1),
            y_range=(-8, 8, 1),
            background_line_style={
                "stroke_opacity": 0.15,
            },
        )

        self.add(plane)

        # -------------------------------------------------
        # GROUND
        # -------------------------------------------------

        ground = Line(
            vec3(-20.0, -2.0, 0.0),
            vec3(20.0, -2.0, 0.0),
            color=GREY_B,
            stroke_width=4,
        )

        self.add(ground)

        # -------------------------------------------------
        # TITLE
        # -------------------------------------------------

        title = Text(
            "BALANCE TEST",
            font_size=34,
        )

        title.to_edge(UP)

        self.add(title)

        # -------------------------------------------------
        # CREATURE
        # -------------------------------------------------

        creature = build_body_rig()

        creature.move_to(
            vec3(
                0.0,
                -1.0,
                0.0,
            )
        )

        creature.enable_debug()

        self.add(creature)

        # -------------------------------------------------
        # CONTROLLERS
        # -------------------------------------------------

        movement_controller = (
            build_movement_controller(
                creature
            )
        )

        rotation_controller = (
            build_rotation_controller(
                creature
            )
        )

        camera_controller = (
            build_camera_controller(
                self,
                creature,
            )
        )

        camera_controller.follow_creature()

        # -------------------------------------------------
        # CENTER OF MASS MARKER
        # -------------------------------------------------

        center_mass_dot = Dot(
            radius=0.08,
            color=RED,
        )

        self.add(center_mass_dot)

        # -------------------------------------------------
        # BALANCE VECTOR
        # -------------------------------------------------

        balance_vector = always_redraw(
            lambda: Arrow(
                creature.get_center(),
                creature.get_center()
                + creature.get_center_of_mass(),
                buff=0.0,
                color=YELLOW,
                stroke_width=4,
            )
        )

        self.add(balance_vector)

        # -------------------------------------------------
        # UPDATE LOOP
        # -------------------------------------------------

        def update_system(_, dt):

            movement_controller.update(dt)

            rotation_controller.update(dt)

            camera_controller.update(dt)

            center_mass_dot.move_to(
                creature.get_center()
                + creature.get_center_of_mass()
            )

        creature.add_updater(
            update_system
        )

        # =================================================
        # TEST 1
        # STATIC BALANCE
        # =================================================

        self.wait(3)

        # =================================================
        # TEST 2
        # LEFT LEAN
        # =================================================

        self.play(
            Rotate(
                creature.body,
                angle=PI / 10,
                about_point=creature.center_anchor,
            ),
            run_time=3,
        )

        self.wait(2)

        # =================================================
        # TEST 3
        # RIGHT LEAN
        # =================================================

        self.play(
            Rotate(
                creature.body,
                angle=-PI / 5,
                about_point=creature.center_anchor,
            ),
            run_time=3,
        )

        self.wait(2)

        # =================================================
        # TEST 4
        # RESET BALANCE
        # =================================================

        self.play(
            Rotate(
                creature.body,
                angle=PI / 10,
                about_point=creature.center_anchor,
            ),
            run_time=3,
        )

        self.wait(2)

        # =================================================
        # TEST 5
        # WALK STABILITY
        # =================================================

        movement_controller.walk_to(
            vec3(
                5.0,
                -1.0,
                0.0,
            ),
            speed=1.0,
        )

        self.wait(6)

        # =================================================
        # TEST 6
        # DIRECTION CHANGE
        # =================================================

        movement_controller.walk_to(
            vec3(
                -4.0,
                2.0,
                0.0,
            ),
            speed=1.25,
        )

        self.wait(6)

        # =================================================
        # TEST 7
        # RAPID TURN BALANCE
        # =================================================

        rotation_controller.rotate_left()

        self.wait(4)

        rotation_controller.stop_rotation()

        self.wait(1)

        rotation_controller.rotate_right()

        self.wait(4)

        rotation_controller.stop_rotation()

        self.wait(2)

        # =================================================
        # TEST 8
        # BODY SWAY
        # =================================================

        sway_cycles = 4

        for _ in range(sway_cycles):

            self.play(
                creature.animate.shift(
                    vec3(
                        0.35,
                        0.0,
                        0.0,
                    )
                ),
                run_time=1.2,
            )

            self.play(
                creature.animate.shift(
                    vec3(
                        -0.35,
                        0.0,
                        0.0,
                    )
                ),
                run_time=1.2,
            )

        self.wait(2)

        # =================================================
        # TEST 9
        # LOW CENTER OF MASS
        # =================================================

        self.play(
            creature.animate.scale(
                0.85
            ),
            run_time=3,
        )

        self.wait(3)

        # =================================================
        # TEST 10
        # HIGH CENTER OF MASS
        # =================================================

        self.play(
            creature.animate.scale(
                1.3
            ),
            run_time=3,
        )

        self.wait(3)

        # =================================================
        # TEST 11
        # RESET SCALE
        # =================================================

        self.play(
            creature.animate.scale(
                0.9
            ),
            run_time=3,
        )

        self.wait(2)

        # =================================================
        # TEST 12
        # CAMERA ORBIT
        # =================================================

        camera_controller.orbit_creature()

        movement_controller.walk_to(
            vec3(
                6.0,
                0.0,
                0.0,
            ),
            speed=1.1,
        )

        self.wait(8)

        # =================================================
        # TEST 13
        # CINEMATIC BALANCE
        # =================================================

        camera_controller.cinematic_mode()

        movement_controller.walk_to(
            vec3(
                -5.0,
                -1.0,
                0.0,
            ),
            speed=1.35,
        )

        self.wait(8)

        # =================================================
        # TEST 14
        # IDLE BALANCE
        # =================================================

        movement_controller.stop()

        self.wait(6)

        # =================================================
        # TEST 15
        # FINAL CENTER VALIDATION
        # =================================================

        final_dot = Dot(
            creature.get_center(),
            radius=0.08,
            color=GREEN,
        )

        self.add(final_dot)

        self.wait(3)

        # -------------------------------------------------
        # CLEANUP
        # -------------------------------------------------

        creature.remove_updater(
            update_system
        )

        self.wait(1)