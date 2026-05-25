"""
mathlab_creature/scenes/tests/test_leg_kinematics_scene.py

LEG KINEMATICS VALIDATION SCENE

Purpose
-------
Low-level articulated leg verification.

Tests:
- knee joints
- pivots
- bend math
- hierarchy stability
- IK solving
- ankle articulation
- foot contact alignment

IMPORTANT
---------
This scene ONLY tests:
LEG KINEMATICS.

NOT:
- walking system
- camera system
- movement controller
- cinematic logic
"""

from __future__ import annotations

import numpy as np

from manimlib import *

from mathlab_creature.core.transforms import (
    vec3,
)

from mathlab_creature.core.debug_draw import (
    create_world_origin_marker,
)

from mathlab_creature.creature.rigs.leg_rig import (
    build_left_leg_rig,
)

from mathlab_creature.core.kinematics import (
    solve_two_bone_ik,
)


# =========================================================
# SCENE
# =========================================================

class TestLegKinematicsScene(Scene):
    """
    Procedural leg kinematics validation.
    """

    def construct(self):

        # -------------------------------------------------
        # GRID
        # -------------------------------------------------

        plane = NumberPlane(
            x_range=(-8, 8, 1),
            y_range=(-5, 5, 1),
            background_line_style={
                "stroke_opacity": 0.15,
            },
        )

        self.add(plane)

        # -------------------------------------------------
        # ORIGIN
        # -------------------------------------------------

        origin_marker = (
            create_world_origin_marker()
        )

        self.add(origin_marker)

        # -------------------------------------------------
        # TITLE
        # -------------------------------------------------

        title = Text(
            "LEG KINEMATICS TEST",
            font_size=34,
        )

        title.to_edge(UP)

        self.add(title)

        # -------------------------------------------------
        # LEG RIG
        # -------------------------------------------------

        leg_rig = build_left_leg_rig()

        leg_rig.move_to(
            vec3(
                0.0,
                1.5,
                0.0,
            )
        )

        leg_rig.enable_debug()

        self.add(leg_rig)

        # -------------------------------------------------
        # TARGET DOT
        # -------------------------------------------------

        target_dot = Dot(
            radius=0.08,
            color=YELLOW,
        )

        target_dot.move_to(
            vec3(
                0.0,
                -1.8,
                0.0,
            )
        )

        self.add(target_dot)

        # =================================================
        # TEST 1
        # STATIC IK
        # =================================================

        initial_target = vec3(
            0.0,
            -1.8,
            0.0,
        )

        leg_rig.solve_leg_ik(
            initial_target
        )

        self.wait(2)

        # =================================================
        # TEST 2
        # LEFT SWEEP
        # =================================================

        left_target = vec3(
            -1.0,
            -1.4,
            0.0,
        )

        self.play(
            target_dot.animate.move_to(
                left_target
            ),
            run_time=2,
        )

        leg_rig.solve_leg_ik(
            left_target
        )

        self.wait(2)

        # =================================================
        # TEST 3
        # RIGHT SWEEP
        # =================================================

        right_target = vec3(
            1.0,
            -1.4,
            0.0,
        )

        self.play(
            target_dot.animate.move_to(
                right_target
            ),
            run_time=2,
        )

        leg_rig.solve_leg_ik(
            right_target
        )

        self.wait(2)

        # =================================================
        # TEST 4
        # DEEP KNEE BEND
        # =================================================

        crouch_target = vec3(
            0.0,
            -0.7,
            0.0,
        )

        self.play(
            target_dot.animate.move_to(
                crouch_target
            ),
            run_time=2,
        )

        leg_rig.solve_leg_ik(
            crouch_target
        )

        self.wait(2)

        # =================================================
        # TEST 5
        # EXTENDED LEG
        # =================================================

        extend_target = vec3(
            0.0,
            -2.4,
            0.0,
        )

        self.play(
            target_dot.animate.move_to(
                extend_target
            ),
            run_time=2,
        )

        leg_rig.solve_leg_ik(
            extend_target
        )

        self.wait(2)

        # =================================================
        # TEST 6
        # CIRCULAR TARGET
        # =================================================

        circle_center = vec3(
            0.0,
            -1.5,
            0.0,
        )

        radius = 0.9

        def orbit_update(mob, alpha):

            angle = TAU * alpha

            target = circle_center + vec3(
                np.cos(angle) * radius,
                np.sin(angle) * radius,
                0.0,
            )

            mob.move_to(target)

            leg_rig.solve_leg_ik(
                target
            )

        self.play(
            UpdateFromAlphaFunc(
                target_dot,
                orbit_update,
            ),
            run_time=6,
            rate_func=linear,
        )

        self.wait(1)

        # =================================================
        # TEST 7
        # FOOT ROTATION
        # =================================================

        self.play(
            Rotate(
                leg_rig.foot,
                angle=PI / 5,
                about_point=leg_rig.foot.get_center(),
            ),
            run_time=2,
        )

        self.wait(1)

        self.play(
            Rotate(
                leg_rig.foot,
                angle=-PI / 5,
                about_point=leg_rig.foot.get_center(),
            ),
            run_time=2,
        )

        self.wait(1)

        # =================================================
        # TEST 8
        # ANKLE ROTATION
        # =================================================

        leg_rig.ankle_joint.set_ankle_angle(
            PI / 6
        )

        self.wait(2)

        leg_rig.ankle_joint.set_ankle_angle(
            -PI / 6
        )

        self.wait(2)

        leg_rig.ankle_joint.reset_joint()

        self.wait(1)

        # =================================================
        # TEST 9
        # KNEE ARTICULATION
        # =================================================

        leg_rig.knee_joint.set_joint_angle(
            PI / 3
        )

        self.wait(2)

        leg_rig.knee_joint.set_joint_angle(
            PI / 6
        )

        self.wait(2)

        leg_rig.knee_joint.reset_joint()

        self.wait(1)

        # =================================================
        # TEST 10
        # FULL RESET
        # =================================================

        leg_rig.reset_pose()

        self.wait(3)