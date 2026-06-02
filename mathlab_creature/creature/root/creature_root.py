"""
Creature root for mathlab-mylinehub-creature.

This is the single top-level creature object.

Architecture rule:
- external code should not control parts directly
- external code talks to CreatureRoot
- CreatureRoot owns BodyRig
- BodyRig owns BodyM
- controllers/actions work through rigs
- one creature moves as one organism
"""

from __future__ import annotations

from typing import Optional

from manimlib import VGroup

from mathlab_creature.creature.rigs.body_rig import BodyRig
from mathlab_creature.creature.rigs.body_rig import build_body_rig

from mathlab_creature.creature.actions.blink_action import build_blink_animation
from mathlab_creature.creature.actions.look_action import build_look_animation
from mathlab_creature.creature.actions.look_action import build_look_center_animation
from mathlab_creature.creature.actions.look_action import build_look_and_return_animation
from mathlab_creature.creature.actions.wave_action import build_wave_animation
from mathlab_creature.creature.actions.point_action import build_point_animation
from mathlab_creature.creature.actions.hop_action import build_hop_animation

from mathlab_creature.creature.controllers.movement_controller import MovementController
from mathlab_creature.creature.controllers.movement_controller import build_movement_controller
from mathlab_creature.creature.controllers.rotation_controller import RotationController
from mathlab_creature.creature.controllers.rotation_controller import build_rotation_controller
from mathlab_creature.creature.controllers.visibility_controller import VisibilityController
from mathlab_creature.creature.controllers.visibility_controller import build_visibility_controller


class CreatureRoot(VGroup):
    """
    One connected creature root.

    Public scene code should use this object only.
    """

    def __init__(
        self,
        *,
        position=None,
        with_sound: bool = True,
        debug_enabled: Optional[bool] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.with_sound = bool(with_sound)
        self.debug_enabled = debug_enabled

        self.body_rig: BodyRig = build_body_rig(
            position=position,
        )

        self.add(self.body_rig)

        self.movement_controller: MovementController = build_movement_controller(
            self.body_rig,
        )

        self.rotation_controller: RotationController = build_rotation_controller(
            self.body_rig,
        )

        self.visibility_controller: VisibilityController = build_visibility_controller(
            self.body_rig,
        )

        self.name = "creature_root"
        self.is_creature_root = True

    def update_creature(
        self,
        delta_time: float,
    ) -> None:
        """
        Update all creature controllers.
        """
        self.movement_controller.update(delta_time)
        self.rotation_controller.update(delta_time)
        self.visibility_controller.update(delta_time)

    def move_to_root(
        self,
        position,
    ) -> None:
        """
        Move whole creature root instantly.
        """
        self.body_rig.teleport(position)

    def move_to_position(
        self,
        position,
    ) -> None:
        """
        Smooth movement target.
        """
        self.movement_controller.move_to(position)

    def walk_to(
        self,
        position,
        speed: float | None = None,
    ) -> None:
        """
        Walk creature toward target position.
        """
        self.movement_controller.walk_to(
            position,
            speed=speed,
        )

    def teleport(
        self,
        position,
    ) -> None:
        """
        Instantly teleport creature.
        """
        self.movement_controller.teleport(position)

    def stop(
        self,
    ) -> None:
        """
        Stop creature movement.
        """
        self.movement_controller.stop()

    def face_direction(
        self,
        direction,
    ) -> None:
        """
        Rotate creature toward direction.
        """
        self.rotation_controller.face_direction(direction)

    def rotate_to(
        self,
        angle: float,
    ) -> None:
        """
        Rotate creature toward exact angle.
        """
        self.rotation_controller.rotate_to(angle)

    def hide_creature(
        self,
        animated: bool = False,
    ) -> None:
        """
        Hide whole creature.
        """
        self.visibility_controller.hide(animated=animated)

    def show_creature(
        self,
        animated: bool = False,
    ) -> None:
        """
        Show whole creature.
        """
        self.visibility_controller.show(animated=animated)

    def blink(
        self,
        *,
        with_sound: Optional[bool] = None,
    ):
        """
        Build blink animation.
        """
        face_rig = self.body_rig.get_face_rig()

        return build_blink_animation(
            face_rig,
            with_sound=self.with_sound if with_sound is None else with_sound,
        )

    def look(
        self,
        direction_name: str,
        *,
        with_sound: Optional[bool] = None,
    ):
        """
        Build look animation.
        """
        face_rig = self.body_rig.get_face_rig()

        return build_look_animation(
            face_rig,
            direction_name,
            with_sound=self.with_sound if with_sound is None else with_sound,
        )

    def look_center(
        self,
    ):
        """
        Build look-center animation.
        """
        face_rig = self.body_rig.get_face_rig()

        return build_look_center_animation(
            face_rig,
        )

    def look_and_return(
        self,
        direction_name: str,
        *,
        with_sound: Optional[bool] = None,
    ):
        """
        Build look and return animation.
        """
        face_rig = self.body_rig.get_face_rig()

        return build_look_and_return_animation(
            face_rig,
            direction_name,
            with_sound=self.with_sound if with_sound is None else with_sound,
        )

    def wave(
        self,
        *,
        side: str = "right",
        cycles: int = 2,
        with_sound: Optional[bool] = None,
    ):
        """
        Build wave animation.
        """
        arm_rig = self.body_rig.get_arm_rig()

        return build_wave_animation(
            arm_rig,
            side=side,
            cycles=cycles,
            with_sound=self.with_sound if with_sound is None else with_sound,
        )

    def point(
        self,
        *,
        side: str = "right",
        return_to_neutral: bool = True,
        with_sound: Optional[bool] = None,
    ):
        """
        Build point animation.
        """
        arm_rig = self.body_rig.get_arm_rig()

        return build_point_animation(
            arm_rig,
            side=side,
            return_to_neutral=return_to_neutral,
            with_sound=self.with_sound if with_sound is None else with_sound,
        )

    def hop(
        self,
        *,
        with_sound: Optional[bool] = None,
    ):
        """
        Build hop animation.
        """
        return build_hop_animation(
            self.body_rig,
            with_sound=self.with_sound if with_sound is None else with_sound,
        )

    def get_body_rig(self) -> BodyRig:
        return self.body_rig

    def get_body(self):
        return self.body_rig.get_body()

    def get_movement_controller(self) -> MovementController:
        return self.movement_controller

    def get_rotation_controller(self) -> RotationController:
        return self.rotation_controller

    def get_visibility_controller(self) -> VisibilityController:
        return self.visibility_controller

    def debug_print(self) -> None:
        print("========== CREATURE ROOT ==========")
        print("Name:", self.name)
        print("Sound:", self.with_sound)
        print("Has BodyRig:", self.body_rig is not None)
        print("Has MovementController:", self.movement_controller is not None)
        print("Has RotationController:", self.rotation_controller is not None)
        print("Has VisibilityController:", self.visibility_controller is not None)
        print("===================================")


__all__ = [
    "CreatureRoot",
]