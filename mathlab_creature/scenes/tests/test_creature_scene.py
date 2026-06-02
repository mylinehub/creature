"""
Single creature test scene.

Purpose:
- verify public API works
- verify one connected creature builds
- verify basic actions work
- avoid direct imports from parts, rigs, actions, or controllers

Run:

    manimgl mathlab_creature/scenes/tests/test_creature_scene.py TestCreatureScene
"""

from __future__ import annotations

from manimlib import Scene
from manimlib import UP
from manimlib import RIGHT
from manimlib import LEFT
from manimlib import Text

from mathlab_creature import build_creature


class TestCreatureScene(Scene):
    """
    First stable connected-creature test.

    Scene rule:
    only import build_creature.
    """

    def construct(self) -> None:
        title = Text("MYLINEHUB Creature Test")
        title.scale(0.55)
        title.to_edge(UP)

        creature = build_creature(
            position=[0.0, -0.8, 0.0],
            with_sound=True,
            debug_enabled=False,
        )

        self.add(title)
        self.add(creature)

        self.wait(0.5)

        self.play(
            creature.blink(),
        )
        self.wait(0.25)

        self.play(
            creature.look_and_return("left"),
        )
        self.wait(0.25)

        self.play(
            creature.look_and_return("right"),
        )
        self.wait(0.25)

        self.play(
            creature.wave(
                side="right",
                cycles=2,
            ),
        )
        self.wait(0.25)

        self.play(
            creature.point(
                side="left",
                return_to_neutral=True,
            ),
        )
        self.wait(0.25)

        self.play(
            creature.hop(),
        )
        self.wait(0.25)

        creature.face_direction(RIGHT)
        creature.update_creature(0.016)
        self.wait(0.25)

        creature.face_direction(LEFT)
        creature.update_creature(0.016)
        self.wait(0.25)

        creature.move_to_root([1.2, -0.8, 0.0])
        self.wait(0.5)

        creature.move_to_root([-1.2, -0.8, 0.0])
        self.wait(0.5)

        creature.move_to_root([0.0, -0.8, 0.0])
        self.wait(0.75)