"""
mathlab_creature/scenes/tests/test_interactive_controller_scene.py

INTERACTIVE CONTROLLER PLAYGROUND

VERY IMPORTANT SCENE

Purpose
-------
Real-time creature interaction sandbox.

This becomes:
- keyboard playground
- movement sandbox
- live debug scene
- controller integration scene
- locomotion tuning space
- future gameplay testbed

Controls
--------
Arrow Keys:
    ↑ move forward
    ↓ move backward
    ← rotate left
    → rotate right

Shift:
    sprint

Ctrl:
    precision movement

Space:
    hop/jump

R:
    reset pose

T:
    toggle debug

G:
    toggle joints

C:
    cinematic camera

O:
    orbit camera

F:
    follow camera

H:
    hide/show creature

IMPORTANT
---------
This is the MAIN realtime interaction scene.
"""

from __future__ import annotations

import numpy as np

from manimlib import *

from mathlab_creature.core.transforms import (
    vec3,
)

from mathlab_creature.core.input_controller import (
    InputController,
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

class TestInteractiveControllerScene(
    MovingCameraScene
):
    """
    Real-time creature interaction sandbox.
    """

    def construct(self):

        # -------------------------------------------------
        # GRID
        # -------------------------------------------------

        plane = NumberPlane(
            x_range=(-30, 30, 1),
            y_range=(-20, 20, 1),
            background_line_style={
                "stroke_opacity": 0.12,
            },
        )

        self.add(plane)

        # -------------------------------------------------
        # TITLE
        # -------------------------------------------------

        title = Text(
            "INTERACTIVE CONTROLLER TEST",
            font_size=34,
        )

        title.to_edge(UP)

        self.add(title)

        # -------------------------------------------------
        # HUD
        # -------------------------------------------------

        controls_text = Text(
            (
                "ARROWS: MOVE | "
                "SHIFT: SPRINT | "
                "CTRL: PRECISE | "
                "SPACE: JUMP | "
                "R: RESET | "
                "T: DEBUG | "
                "G: JOINTS | "
                "C/O/F: CAMERA | "
                "H: HIDE"
            ),
            font_size=20,
        )

        controls_text.to_edge(DOWN)

        self.add(controls_text)

        # -------------------------------------------------
        # CREATURE
        # -------------------------------------------------

        creature = build_body_rig()

        creature.move_to(
            vec3(
                0.0,
                -2.0,
                0.0,
            )
        )

        self.add(creature)

        # -------------------------------------------------
        # INPUT
        # -------------------------------------------------

        input_controller = (
            InputController()
        )

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

        camera_controller.follow_creature()

        # -------------------------------------------------
        # STATE
        # -------------------------------------------------

        debug_enabled = False

        joints_enabled = False

        # =================================================
        # INPUT HANDLING
        # =================================================

        def handle_keyboard():

            # ---------------------------------------------
            # MOVEMENT VECTOR
            # ---------------------------------------------

            movement = vec3()

            # ---------------------------------------------
            # FORWARD
            # ---------------------------------------------

            if self.is_key_pressed(
                "UP"
            ):
                movement += vec3(
                    0.0,
                    1.0,
                    0.0,
                )

            # ---------------------------------------------
            # BACKWARD
            # ---------------------------------------------

            if self.is_key_pressed(
                "DOWN"
            ):
                movement += vec3(
                    0.0,
                    -1.0,
                    0.0,
                )

            # ---------------------------------------------
            # LEFT TURN
            # ---------------------------------------------

            if self.is_key_pressed(
                "LEFT"
            ):
                rotation_controller.rotate_left()

            else:
                rotation_controller.stop_rotation()

            # ---------------------------------------------
            # RIGHT TURN
            # ---------------------------------------------

            if self.is_key_pressed(
                "RIGHT"
            ):
                rotation_controller.rotate_right()

            # ---------------------------------------------
            # SHIFT = SPRINT
            # ---------------------------------------------

            speed = 1.0

            if self.is_key_pressed(
                "SHIFT"
            ):
                speed = 2.2

            # ---------------------------------------------
            # CTRL = PRECISE
            # ---------------------------------------------

            if self.is_key_pressed(
                "CTRL"
            ):
                speed = 0.35

            # ---------------------------------------------
            # WALK
            # ---------------------------------------------

            magnitude = np.linalg.norm(
                movement
            )

            if magnitude > 1e-5:

                movement /= magnitude

                movement_controller.walk_to(
                    creature.current_position
                    + movement,
                    speed=speed,
                )

            else:
                movement_controller.stop()

        # =================================================
        # KEY PRESS CALLBACK
        # =================================================

        def on_key_press(symbol, modifiers):

            nonlocal debug_enabled
            nonlocal joints_enabled

            try:

                key = chr(symbol).lower()

            except Exception:
                return

            # ---------------------------------------------
            # SPACE
            # ---------------------------------------------

            if key == " ":

                self.play(
                    creature.animate.shift(
                        vec3(
                            0.0,
                            0.6,
                            0.0,
                        )
                    ),
                    run_time=0.15,
                )

                self.play(
                    creature.animate.shift(
                        vec3(
                            0.0,
                            -0.6,
                            0.0,
                        )
                    ),
                    run_time=0.2,
                )

            # ---------------------------------------------
            # RESET
            # ---------------------------------------------

            elif key == "r":

                creature.reset_pose()

                movement_controller.reset()

                rotation_controller.reset()

            # ---------------------------------------------
            # DEBUG
            # ---------------------------------------------

            elif key == "t":

                debug_enabled = (
                    not debug_enabled
                )

                if debug_enabled:
                    creature.enable_debug()

                else:
                    creature.disable_debug()

            # ---------------------------------------------
            # JOINTS
            # ---------------------------------------------

            elif key == "g":

                joints_enabled = (
                    not joints_enabled
                )

                if joints_enabled:

                    creature.left_leg_rig.enable_debug()

                    creature.right_leg_rig.enable_debug()

                else:

                    creature.left_leg_rig.disable_debug()

                    creature.right_leg_rig.disable_debug()

            # ---------------------------------------------
            # CINEMATIC CAMERA
            # ---------------------------------------------

            elif key == "c":

                camera_controller.cinematic_mode()

            # ---------------------------------------------
            # ORBIT CAMERA
            # ---------------------------------------------

            elif key == "o":

                camera_controller.orbit_creature()

            # ---------------------------------------------
            # FOLLOW CAMERA
            # ---------------------------------------------

            elif key == "f":

                camera_controller.follow_creature()

            # ---------------------------------------------
            # VISIBILITY
            # ---------------------------------------------

            elif key == "h":

                visibility_controller.toggle_visibility()

        # =================================================
        # UPDATE LOOP
        # =================================================

        def update_system(_, dt):

            handle_keyboard()

            movement_controller.update(dt)

            rotation_controller.update(dt)

            visibility_controller.update(dt)

            camera_controller.update(dt)

        creature.add_updater(
            update_system
        )

        # =================================================
        # WINDOW CALLBACK
        # =================================================

        self.window.on_key_press = (
            on_key_press
        )

        # =================================================
        # LIVE LOOP
        # =================================================

        self.wait(9999)