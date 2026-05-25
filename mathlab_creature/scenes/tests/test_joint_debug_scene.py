"""
mathlab_creature/scenes/tests/test_joint_debug_scene.py

JOINT DEBUG VALIDATION SCENE

Purpose
-------
Low-level hierarchy and transform debugging.

Tests:
- hierarchy
- axes
- pivots
- vectors
- parent-child transforms
- local/world space validation
- center point validation

IMPORTANT
---------
This scene exists ONLY for:
DEBUGGING TRANSFORM SYSTEMS.

NOT:
- walking
- actions
- cinematic motion
- gameplay logic
"""

from __future__ import annotations

import numpy as np

from manimlib import *

from mathlab_creature.core.transforms import (
    vec3,
)

from mathlab_creature.core.debug_draw import (
    create_world_origin_marker,
    create_local_axes,
    create_vector_arrow,
)

from mathlab_creature.creature.parts.hip_joint import (
    build_debug_hip_joint,
)

from mathlab_creature.creature.parts.knee_joint import (
    build_debug_knee_joint,
)

from mathlab_creature.creature.parts.ankle_joint import (
    build_debug_ankle_joint,
)

from mathlab_creature.creature.parts.feet import (
    build_debug_foot,
)

from mathlab_creature.creature.parts.legs import (
    build_debug_leg,
)


# =========================================================
# SCENE
# =========================================================

class TestJointDebugScene(Scene):
    """
    Transform hierarchy validation scene.
    """

    def construct(self):

        # -------------------------------------------------
        # GRID
        # -------------------------------------------------

        plane = NumberPlane(
            x_range=(-10, 10, 1),
            y_range=(-6, 6, 1),
            background_line_style={
                "stroke_opacity": 0.15,
            },
        )

        self.add(plane)

        # -------------------------------------------------
        # WORLD ORIGIN
        # -------------------------------------------------

        origin_marker = (
            create_world_origin_marker()
        )

        self.add(origin_marker)

        # -------------------------------------------------
        # TITLE
        # -------------------------------------------------

        title = Text(
            "JOINT DEBUG TEST",
            font_size=34,
        )

        title.to_edge(UP)

        self.add(title)

        # =================================================
        # HIP JOINT
        # =================================================

        hip_joint = build_debug_hip_joint()

        hip_joint.move_to(
            vec3(
                -5.0,
                2.0,
                0.0,
            )
        )

        self.add(hip_joint)

        # =================================================
        # KNEE JOINT
        # =================================================

        knee_joint = build_debug_knee_joint()

        knee_joint.move_to(
            vec3(
                -1.5,
                1.5,
                0.0,
            )
        )

        self.add(knee_joint)

        # =================================================
        # ANKLE JOINT
        # =================================================

        ankle_joint = build_debug_ankle_joint()

        ankle_joint.move_to(
            vec3(
                2.0,
                1.0,
                0.0,
            )
        )

        self.add(ankle_joint)

        # =================================================
        # FOOT
        # =================================================

        foot = build_debug_foot()

        foot.move_to(
            vec3(
                5.0,
                0.0,
                0.0,
            )
        )

        self.add(foot)

        # =================================================
        # FULL LEG
        # =================================================

        leg = build_debug_leg()

        leg.move_to(
            vec3(
                0.0,
                -1.0,
                0.0,
            )
        )

        self.add(leg)

        # =================================================
        # TEST 1
        # STATIC VALIDATION
        # =================================================

        self.wait(2)

        # =================================================
        # TEST 2
        # KNEE ROTATION
        # =================================================

        knee_joint.set_joint_angle(
            PI / 4
        )

        self.wait(2)

        knee_joint.set_joint_angle(
            -PI / 6
        )

        self.wait(2)

        knee_joint.reset_joint()

        self.wait(1)

        # =================================================
        # TEST 3
        # ANKLE ROTATION
        # =================================================

        ankle_joint.set_ankle_angle(
            PI / 5
        )

        self.wait(2)

        ankle_joint.set_ankle_angle(
            -PI / 5
        )

        self.wait(2)

        ankle_joint.reset_joint()

        self.wait(1)

        # =================================================
        # TEST 4
        # FOOT ROTATION
        # =================================================

        foot.rotate_foot(
            PI / 8
        )

        self.wait(2)

        foot.rotate_foot(
            -PI / 4
        )

        self.wait(2)

        foot.reset_foot()

        self.wait(1)

        # =================================================
        # TEST 5
        # LEG ROTATION
        # =================================================

        self.play(
            Rotate(
                leg,
                angle=PI / 4,
                about_point=leg.get_center(),
            ),
            run_time=3,
        )

        self.wait(1)

        self.play(
            Rotate(
                leg,
                angle=-PI / 2,
                about_point=leg.get_center(),
            ),
            run_time=3,
        )

        self.wait(1)

        # =================================================
        # TEST 6
        # LOCAL AXIS VALIDATION
        # =================================================

        local_axes = create_local_axes(
            origin=vec3(
                0.0,
                -4.0,
                0.0,
            ),
            axis_length=1.5,
        )

        self.add(local_axes)

        self.wait(2)

        # =================================================
        # TEST 7
        # VECTOR DEBUG
        # =================================================

        vector_a = create_vector_arrow(
            start=vec3(
                -4.0,
                -4.0,
                0.0,
            ),
            end=vec3(
                -2.0,
                -2.0,
                0.0,
            ),
        )

        vector_b = create_vector_arrow(
            start=vec3(
                2.0,
                -4.0,
                0.0,
            ),
            end=vec3(
                4.0,
                -2.5,
                0.0,
            ),
        )

        self.add(vector_a)
        self.add(vector_b)

        self.wait(3)

        # =================================================
        # TEST 8
        # HIERARCHY VALIDATION
        # =================================================

        hierarchy_group = VGroup(
            hip_joint,
            knee_joint,
            ankle_joint,
            foot,
        )

        self.play(
            hierarchy_group.animate.shift(
                vec3(
                    0.0,
                    1.0,
                    0.0,
                )
            ),
            run_time=3,
        )

        self.wait(1)

        self.play(
            hierarchy_group.animate.scale(
                1.15
            ),
            run_time=3,
        )

        self.wait(1)

        # =================================================
        # TEST 9
        # CENTER PIVOT VALIDATION
        # =================================================

        center_dot = Dot(
            leg.get_center(),
            radius=0.08,
            color=RED,
        )

        self.add(center_dot)

        self.wait(3)

        # =================================================
        # TEST 10
        # RESET
        # =================================================

        self.play(
            hierarchy_group.animate.move_to(
                ORIGIN
            ),
            run_time=3,
        )

        self.wait(3)