# File: mathlab_creature/scenes/tests/test_walk_cycle_scene.py

"""
mathlab_creature/scenes/tests/test_walk_cycle_scene.py

WALK CYCLE VALIDATION SCENE
WITH PROCEDURAL AUDIO VALIDATION

Purpose
-------
Procedural gait validation and locomotion tuning.

Tests:
- gait quality
- realism
- stride tuning
- foot timing
- body bounce
- body sway
- procedural stepping
- directional movement
- walk stability
- procedural audio timing
- left/right footstep rhythm
- mascot-style walk sound

IMPORTANT
---------
This scene ONLY validates:
WALKING QUALITY.

NOT:
- transform debugging
- controller architecture
- camera debugging
- hierarchy validation
"""

from __future__ import annotations

import numpy as np

from manimlib import *

from mathlab_creature.core.transforms import (
    vec3,
)

from mathlab_creature.core.audio.audio_server import (
    boot_audio_server,
    shutdown_audio_server,
)

from mathlab_creature.creature.rigs.body_rig import (
    build_body_rig,
)

from mathlab_creature.creature.actions.walk_action import (
    build_walk_action,
)

from mathlab_creature.creature.controllers.camera_controller import (
    build_camera_controller,
)


# =========================================================
# SCENE
# =========================================================

class TestWalkCycleScene(MovingCameraScene):
    """
    Procedural locomotion validation scene
    with procedural audio testing.
    """

    def construct(self):

        # -------------------------------------------------
        # AUDIO BOOT
        # -------------------------------------------------

        boot_audio_server()

        # -------------------------------------------------
        # GLOBAL AUDIO TOGGLE
        # -------------------------------------------------

        WITH_SOUND = True

        # -------------------------------------------------
        # GRID
        # -------------------------------------------------

        plane = NumberPlane(
            x_range=(-20, 20, 1),
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
            "WALK CYCLE + AUDIO TEST",
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
                -8.0,
                -1.0,
                0.0,
            )
        )

        creature.enable_debug()

        self.add(creature)

        # -------------------------------------------------
        # WALK ACTION
        # -------------------------------------------------

        walk_action = build_walk_action(
            creature,
            with_sound=WITH_SOUND,
        )

        # -------------------------------------------------
        # CAMERA
        # -------------------------------------------------

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

            walk_action.update(dt)

            camera_controller.update(dt)

        creature.add_updater(
            update_system
        )

        # =================================================
        # TEST 1
        # SLOW WALK
        # =================================================

        walk_action.start(
            direction=vec3(
                1.0,
                0.0,
                0.0,
            ),
            speed=0.6,
        )

        self.wait(6)

        # =================================================
        # TEST 2
        # NORMAL WALK
        # =================================================

        walk_action.set_speed(
            1.0
        )

        self.wait(6)

        # =================================================
        # TEST 3
        # FAST WALK
        # =================================================

        walk_action.set_speed(
            1.7
        )

        self.wait(6)

        # =================================================
        # TEST 4
        # DIAGONAL WALK
        # =================================================

        walk_action.set_direction(
            vec3(
                1.0,
                0.4,
                0.0,
            )
        )

        walk_action.set_speed(
            1.2
        )

        self.wait(6)

        # =================================================
        # TEST 5
        # LEFT MOVEMENT
        # =================================================

        walk_action.set_direction(
            vec3(
                -1.0,
                0.0,
                0.0,
            )
        )

        self.wait(6)

        # =================================================
        # TEST 6
        # FORWARD/BACKWARD
        # =================================================

        walk_action.set_direction(
            vec3(
                0.0,
                1.0,
                0.0,
            )
        )

        self.wait(5)

        walk_action.set_direction(
            vec3(
                0.0,
                -1.0,
                0.0,
            )
        )

        self.wait(5)

        # =================================================
        # TEST 7
        # STRIDE QUALITY
        # =================================================

        walk_action.config.stride_length = 1.2

        walk_action.config.step_height = 0.42

        walk_action.set_direction(
            vec3(
                1.0,
                0.0,
                0.0,
            )
        )

        walk_action.set_speed(
            1.0
        )

        self.wait(6)

        # =================================================
        # TEST 8
        # SMALL STRIDE
        # =================================================

        walk_action.config.stride_length = 0.4

        walk_action.config.step_height = 0.16

        self.wait(6)

        # =================================================
        # TEST 9
        # BODY BOUNCE
        # =================================================

        walk_action.config.body_bounce_strength = (
            0.16
        )

        walk_action.config.body_sway_strength = (
            0.12
        )

        self.wait(6)

        # =================================================
        # TEST 10
        # RESET NATURAL WALK
        # =================================================

        walk_action.config.stride_length = 0.75

        walk_action.config.step_height = 0.3

        walk_action.config.body_bounce_strength = (
            0.08
        )

        walk_action.config.body_sway_strength = (
            0.05
        )

        walk_action.set_speed(
            1.0
        )

        self.wait(6)

        # =================================================
        # TEST 11
        # SOFT CARTOON WALK
        # =================================================

        walk_action.config.stride_length = 0.68

        walk_action.config.step_height = 0.34

        walk_action.config.body_bounce_strength = (
            0.09
        )

        walk_action.config.body_sway_strength = (
            0.07
        )

        walk_action.config.footstep_volume = 0.7

        walk_action.set_direction(
            vec3(
                1.0,
                0.1,
                0.0,
            )
        )

        walk_action.set_speed(
            0.9
        )

        self.wait(8)

        # =================================================
        # TEST 12
        # SILENT WALK MODE
        # =================================================

        walk_action.disable_sound()

        walk_action.set_speed(
            1.0
        )

        walk_action.set_direction(
            vec3(
                1.0,
                0.0,
                0.0,
            )
        )

        self.wait(5)

        # =================================================
        # TEST 13
        # AUDIO RESTORE
        # =================================================

        walk_action.enable_sound()

        walk_action.set_speed(
            1.2
        )

        self.wait(5)

        # =================================================
        # TEST 14
        # ORBIT CAMERA
        # =================================================

        camera_controller.orbit_creature()

        self.wait(8)

        # =================================================
        # TEST 15
        # CINEMATIC MODE
        # =================================================

        camera_controller.cinematic_mode()

        walk_action.set_direction(
            vec3(
                1.0,
                0.2,
                0.0,
            )
        )

        walk_action.set_speed(
            1.25
        )

        self.wait(10)

        # =================================================
        # TEST 16
        # STOP
        # =================================================

        walk_action.stop()

        self.wait(4)

        # -------------------------------------------------
        # CLEANUP
        # -------------------------------------------------

        creature.remove_updater(
            update_system
        )

        # -------------------------------------------------
        # AUDIO SHUTDOWN
        # -------------------------------------------------

        shutdown_audio_server()

        self.wait(1)