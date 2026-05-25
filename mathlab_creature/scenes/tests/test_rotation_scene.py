"""
mathlab_creature/scenes/tests/test_rotation_scene.py

ROTATION VALIDATION SCENE

Purpose
-------
Procedural turning and orientation validation.

Tests:
- turning
- facing
- smooth rotation
- directional alignment
- movement-facing sync
- cinematic turning
- rotational damping
- procedural lean

IMPORTANT
---------
This scene ONLY validates:
ROTATION QUALITY.

NOT:
- gait tuning
- hierarchy debugging
- IK debugging
- camera debugging
"""

from __future__ import annotations

import numpy as np

from manimlib import *

from mathlab_creature.core.transforms import (
    vec3,
)

from mathlab_creature.creature.rigs.body_rig import (
    build_body_rig,
)

from mathlab_creature.creature.controllers.rotation_controller import (
    build_rotation_controller,
)

from mathlab_creature.creature.controllers.camera_controller import (
    build_camera_controller,
)

from mathlab_creature.creature.controllers.movement_controller import (
    build_movement_controller,
)


# =========================================================
# SCENE
# =========================================================

class TestRotationScene(MovingCameraScene):
    """
    Procedural turning validation scene.
    """

    def construct(self):

        # -------------------------------------------------
        # GRID
        # -------------------------------------------------

        plane = NumberPlane(
            x_range=(-12, 12, 1),
            y_range=(-8, 8, 1),
            background_line_style={
                "stroke_opacity": 0.15,
            },
        )

        self.add(plane)

        # -------------------------------------------------
        # TITLE
        # -------------------------------------------------

        title = Text(
            "ROTATION TEST",
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

        rotation_controller = (
            build_rotation_controller(
                creature
            )
        )

        movement_controller = (
            build_movement_controller(
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
        # UPDATE LOOP
        # -------------------------------------------------

        def update_system(_, dt):

            rotation_controller.update(dt)

            movement_controller.update(dt)

            camera_controller.update(dt)

        creature.add_updater(
            update_system
        )

        # =================================================
        # TEST 1
        # FACE RIGHT
        # =================================================

        rotation_controller.face_direction(
            vec3(
                1.0,
                0.0,
                0.0,
            )
        )

        self.wait(4)

        # =================================================
        # TEST 2
        # FACE LEFT
        # =================================================

        rotation_controller.face_direction(
            vec3(
                -1.0,
                0.0,
                0.0,
            )
        )

        self.wait(4)

        # =================================================
        # TEST 3
        # FACE UP
        # =================================================

        rotation_controller.face_direction(
            vec3(
                0.0,
                1.0,
                0.0,
            )
        )

        self.wait(4)

        # =================================================
        # TEST 4
        # FACE DOWN
        # =================================================

        rotation_controller.face_direction(
            vec3(
                0.0,
                -1.0,
                0.0,
            )
        )

        self.wait(4)

        # =================================================
        # TEST 5
        # DIAGONAL TURN
        # =================================================

        rotation_controller.face_direction(
            vec3(
                1.0,
                1.0,
                0.0,
            )
        )

        self.wait(4)

        # =================================================
        # TEST 6
        # MANUAL LEFT TURN
        # =================================================

        rotation_controller.rotate_left()

        self.wait(5)

        rotation_controller.stop_rotation()

        self.wait(2)

        # =================================================
        # TEST 7
        # MANUAL RIGHT TURN
        # =================================================

        rotation_controller.rotate_right()

        self.wait(5)

        rotation_controller.stop_rotation()

        self.wait(2)

        # =================================================
        # TEST 8
        # LOOK AT TARGETS
        # =================================================

        target_a = Dot(
            vec3(
                -4.0,
                2.0,
                0.0,
            ),
            color=YELLOW,
        )

        target_b = Dot(
            vec3(
                4.0,
                2.0,
                0.0,
            ),
            color=RED,
        )

        target_c = Dot(
            vec3(
                0.0,
                -4.0,
                0.0,
            ),
            color=GREEN,
        )

        self.add(
            target_a,
            target_b,
            target_c,
        )

        rotation_controller.look_at(
            target_a.get_center()
        )

        self.wait(3)

        rotation_controller.look_at(
            target_b.get_center()
        )

        self.wait(3)

        rotation_controller.look_at(
            target_c.get_center()
        )

        self.wait(3)

        # =================================================
        # TEST 9
        # MOVEMENT + ROTATION
        # =================================================

        movement_controller.walk_to(
            vec3(
                5.0,
                0.0,
                0.0,
            ),
            speed=1.0,
        )

        rotation_controller.face_movement_direction()

        self.wait(6)

        # =================================================
        # TEST 10
        # DIAGONAL MOVEMENT FACING
        # =================================================

        movement_controller.walk_to(
            vec3(
                -4.0,
                3.0,
                0.0,
            ),
            speed=1.2,
        )

        self.wait(6)

        # =================================================
        # TEST 11
        # ORBIT CAMERA
        # =================================================

        camera_controller.orbit_creature()

        rotation_controller.rotate_left()

        self.wait(8)

        rotation_controller.stop_rotation()

        # =================================================
        # TEST 12
        # CINEMATIC TURNING
        # =================================================

        camera_controller.cinematic_mode()

        directions = [
            vec3(1, 0, 0),
            vec3(1, 1, 0),
            vec3(0, 1, 0),
            vec3(-1, 1, 0),
            vec3(-1, 0, 0),
            vec3(-1, -1, 0),
            vec3(0, -1, 0),
            vec3(1, -1, 0),
        ]

        for direction in directions:

            rotation_controller.face_direction(
                direction
            )

            self.wait(2)

        # =================================================
        # TEST 13
        # RESET
        # =================================================

        rotation_controller.reset()

        self.wait(3)

        # -------------------------------------------------
        # CLEANUP
        # -------------------------------------------------

        creature.remove_updater(
            update_system
        )

        self.wait(1)