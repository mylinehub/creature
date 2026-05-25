# File: mathlab_creature/scenes/tests/test_body_scene.py

"""
mathlab_creature/scenes/tests/test_body_scene.py

MASTER BODY RIG VALIDATION SCENE

Purpose
-------
Final full-creature assembly verification.

This scene validates:
- body rig integrity
- hierarchy correctness
- transform stability
- leg attachment
- face attachment
- procedural balance
- visibility systems
- camera integration
- controller integration
- scaling stability
- root pivot correctness

IMPORTANT
---------
FIXED FOR:
- ManimGL v1.7.2
- no MovingCameraScene support

This scene now uses:
    Scene

instead of:
    MovingCameraScene

because installed ManimGL does not expose:
    MovingCameraScene
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

from mathlab_creature.creature.controllers.movement_controller import (
    build_movement_controller,
)

from mathlab_creature.creature.controllers.rotation_controller import (
    build_rotation_controller,
)

from mathlab_creature.creature.controllers.visibility_controller import (
    build_visibility_controller,
)

from mathlab_creature.creature.controllers.camera_controller import (
    build_camera_controller,
)


# =========================================================
# SCENE
# =========================================================

class TestBodyScene(Scene):
    """
    Full creature assembly verification scene.
    """

    def construct(self):

        # -------------------------------------------------
        # GRID
        # -------------------------------------------------

        plane = NumberPlane(
            x_range=(-12, 12, 1),
            y_range=(-7, 7, 1),
            background_line_style={
                "stroke_opacity": 0.15,
            },
        )

        self.add(plane)

        # -------------------------------------------------
        # TITLE
        # -------------------------------------------------

        title = Text(
            "BODY RIG VALIDATION",
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

        self.add(creature)

        # -------------------------------------------------
        # DEBUG
        # -------------------------------------------------

        if hasattr(creature, "enable_debug"):

            creature.enable_debug()

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

        visibility_controller = (
            build_visibility_controller(
                creature
            )
        )

        camera_controller = (
            build_camera_controller(
                self,
                creature,
            )
        )

        # -------------------------------------------------
        # UPDATE SYSTEM
        # -------------------------------------------------

        def master_update(_, dt):

            if hasattr(
                movement_controller,
                "update",
            ):
                movement_controller.update(dt)

            if hasattr(
                rotation_controller,
                "update",
            ):
                rotation_controller.update(dt)

            if hasattr(
                visibility_controller,
                "update",
            ):
                visibility_controller.update(dt)

            if hasattr(
                camera_controller,
                "update",
            ):
                camera_controller.update(dt)

        creature.add_updater(
            master_update
        )

        # =================================================
        # TEST 1
        # INITIAL POSE
        # =================================================

        self.wait(2)

        # =================================================
        # TEST 2
        # ROOT ROTATION
        # =================================================

        self.play(
            Rotate(
                creature,
                angle=PI / 4,
                run_time=2,
            )
        )

        self.wait(1)

        self.play(
            Rotate(
                creature,
                angle=-PI / 2,
                run_time=2,
            )
        )

        self.wait(1)

        # =================================================
        # TEST 3
        # SCALING
        # =================================================

        self.play(
            creature.animate.scale(1.2),
            run_time=2,
        )

        self.wait(1)

        self.play(
            creature.animate.scale(0.83),
            run_time=2,
        )

        self.wait(1)

        # =================================================
        # TEST 4
        # TELEPORT
        # =================================================

        if hasattr(
            movement_controller,
            "teleport",
        ):

            movement_controller.teleport(
                vec3(
                    -4.0,
                    -1.0,
                    0.0,
                )
            )

            self.wait(2)

            movement_controller.teleport(
                vec3(
                    4.0,
                    -1.0,
                    0.0,
                )
            )

            self.wait(2)

        # =================================================
        # TEST 5
        # WALK VALIDATION
        # =================================================

        if hasattr(
            movement_controller,
            "walk_to",
        ):

            movement_controller.walk_to(
                vec3(
                    0.0,
                    -1.0,
                    0.0,
                ),
                speed=1.0,
            )

            self.wait(5)

        # =================================================
        # TEST 6
        # TURN VALIDATION
        # =================================================

        if hasattr(
            rotation_controller,
            "rotate_left",
        ):

            rotation_controller.rotate_left()

            self.wait(2)

            if hasattr(
                rotation_controller,
                "stop_rotation",
            ):
                rotation_controller.stop_rotation()

            self.wait(1)

            if hasattr(
                rotation_controller,
                "rotate_right",
            ):

                rotation_controller.rotate_right()

                self.wait(2)

                rotation_controller.stop_rotation()

                self.wait(1)

        # =================================================
        # TEST 7
        # VISIBILITY VALIDATION
        # =================================================

        if hasattr(
            visibility_controller,
            "hide",
        ):

            visibility_controller.hide(
                animated=True
            )

            self.wait(2)

            visibility_controller.show(
                animated=True
            )

            self.wait(2)

        # =================================================
        # TEST 8
        # CAMERA FOLLOW
        # =================================================

        if hasattr(
            camera_controller,
            "follow_creature",
        ):

            camera_controller.follow_creature()

        if hasattr(
            movement_controller,
            "walk_to",
        ):

            movement_controller.walk_to(
                vec3(
                    5.0,
                    1.5,
                    0.0,
                ),
                speed=1.1,
            )

            self.wait(5)

        # =================================================
        # TEST 9
        # ORBIT CAMERA
        # =================================================

        if hasattr(
            camera_controller,
            "orbit_creature",
        ):

            camera_controller.orbit_creature()

            self.wait(5)

        # =================================================
        # TEST 10
        # CINEMATIC CAMERA
        # =================================================

        if hasattr(
            camera_controller,
            "cinematic_mode",
        ):

            camera_controller.cinematic_mode()

        if hasattr(
            movement_controller,
            "walk_to",
        ):

            movement_controller.walk_to(
                vec3(
                    -5.0,
                    0.0,
                    0.0,
                ),
                speed=1.3,
            )

            self.wait(6)

        # =================================================
        # TEST 11
        # IDLE VALIDATION
        # =================================================

        if hasattr(
            movement_controller,
            "stop",
        ):

            movement_controller.stop()

        self.wait(6)

        # =================================================
        # TEST 12
        # FINAL CENTER VALIDATION
        # =================================================

        center_dot = Dot(
            creature.get_center(),
            radius=0.08,
            color=RED,
        )

        self.add(center_dot)

        self.wait(3)

        # -------------------------------------------------
        # CLEANUP
        # -------------------------------------------------

        creature.remove_updater(
            master_update
        )

        self.wait(1)