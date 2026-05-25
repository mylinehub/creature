# File: mathlab_creature/scenes/tests/test_actions_scene.py

"""
mathlab_creature/scenes/tests/test_actions_scene.py

MASTER ACTION INTEGRATION TEST SCENE
WITH PROCEDURAL AUDIO VALIDATION

Purpose
-------
Integration validation for:
- movement controller
- walk system
- turn system
- idle system
- visibility system
- procedural body rig
- cinematic camera
- procedural audio system
- action audio synchronization

IMPORTANT
---------
This is NOT:
- low-level IK testing
- debug geometry testing
- isolated limb testing

Those belong in dedicated scenes.

This scene validates:
FULL CREATURE BEHAVIOR.
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

from mathlab_creature.creature.actions.blink_action import (
    build_blink_animation,
)

from mathlab_creature.creature.actions.wave_action import (
    build_wave_animation,
)

from mathlab_creature.creature.actions.point_action import (
    build_point_animation,
)

from mathlab_creature.creature.actions.look_action import (
    build_look_animation,
)

from mathlab_creature.creature.actions.hop_action import (
    build_hop_animation,
)


# =========================================================
# SCENE
# =========================================================

class TestActionsScene(MovingCameraScene):
    """
    Production integration scene.

    Tests:
    - movement
    - turning
    - visibility
    - idle
    - camera
    - procedural locomotion
    - procedural audio
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
        # EYES
        # -------------------------------------------------

        eyes = creature["face"]["eyes"]

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
        # DEBUG
        # -------------------------------------------------

        creature.enable_debug()

        # -------------------------------------------------
        # UPDATE LOOP
        # -------------------------------------------------

        delta_time = 1 / 60

        def master_update(_, dt):

            movement_controller.update(dt)

            rotation_controller.update(dt)

            visibility_controller.update(dt)

            camera_controller.update(dt)

        creature.add_updater(
            master_update
        )

        # -------------------------------------------------
        # TITLE
        # -------------------------------------------------

        title = Text(
            "ACTION + AUDIO INTEGRATION TEST",
            font_size=34,
        )

        title.to_edge(UP)

        self.add(title)

        # =================================================
        # TEST 0
        # AUDIO CHECK
        # =================================================

        self.play(
            build_wave_animation(
                creature,
                cycles=1,
                with_sound=WITH_SOUND,
            )
        )

        self.wait(0.5)

        self.play(
            build_blink_animation(
                eyes,
                with_sound=WITH_SOUND,
            )
        )

        self.wait(0.5)

        self.play(
            build_hop_animation(
                creature,
                with_sound=WITH_SOUND,
            )
        )

        self.wait(1)

        # =================================================
        # TEST 1
        # WALK FORWARD
        # =================================================

        movement_controller.walk_to(
            vec3(
                4.0,
                -1.0,
                0.0,
            ),
            speed=1.0,
            with_sound=WITH_SOUND,
        )

        self.wait(4)

        # =================================================
        # TEST 2
        # TURN LEFT
        # =================================================

        rotation_controller.rotate_left(
            with_sound=WITH_SOUND,
        )

        self.wait(2)

        rotation_controller.stop_rotation()

        # =================================================
        # TEST 3
        # WALK BACK
        # =================================================

        movement_controller.walk_to(
            vec3(
                -3.0,
                -1.0,
                0.0,
            ),
            speed=1.4,
            with_sound=WITH_SOUND,
        )

        self.wait(4)

        # =================================================
        # TEST 4
        # LOOK + POINT
        # =================================================

        self.play(
            build_look_animation(
                eyes,
                "right",
                with_sound=WITH_SOUND,
            )
        )

        self.wait(0.3)

        self.play(
            build_point_animation(
                creature,
                hold=True,
                with_sound=WITH_SOUND,
            )
        )

        self.wait(1)

        # =================================================
        # TEST 5
        # VISIBILITY
        # =================================================

        visibility_controller.hide(
            animated=True
        )

        self.wait(2)

        visibility_controller.show(
            animated=True
        )

        self.wait(2)

        # =================================================
        # TEST 6
        # TELEPORT
        # =================================================

        movement_controller.teleport(
            vec3(
                0.0,
                -1.0,
                0.0,
            )
        )

        self.wait(1)

        # =================================================
        # TEST 7
        # ORBIT CAMERA
        # =================================================

        camera_controller.orbit_creature()

        self.wait(5)

        # =================================================
        # TEST 8
        # CINEMATIC MODE
        # =================================================

        camera_controller.cinematic_mode()

        movement_controller.walk_to(
            vec3(
                5.0,
                1.0,
                0.0,
            ),
            speed=1.2,
            with_sound=WITH_SOUND,
        )

        self.wait(5)

        # =================================================
        # TEST 9
        # IDLE STATE
        # =================================================

        movement_controller.stop()

        self.wait(5)

        # =================================================
        # TEST 10
        # AUDIO DISABLED MODE
        # =================================================

        SILENT_MODE = False

        if SILENT_MODE:

            self.play(
                build_wave_animation(
                    creature,
                    cycles=1,
                    with_sound=False,
                )
            )

            self.play(
                build_hop_animation(
                    creature,
                    with_sound=False,
                )
            )

            self.play(
                build_blink_animation(
                    eyes,
                    with_sound=False,
                )
            )

            self.wait(1)

        # -------------------------------------------------
        # CLEANUP
        # -------------------------------------------------

        creature.remove_updater(
            master_update
        )

        # -------------------------------------------------
        # AUDIO SHUTDOWN
        # -------------------------------------------------

        shutdown_audio_server()

        self.wait(1)