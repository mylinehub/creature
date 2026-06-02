"""
Rotation controller for mathlab-mylinehub-creature.

Controls high-level facing/orientation for one connected creature.

Architecture rule:
- rotation_controller.py does not rotate body parts directly
- rotation_controller.py works through TurnAction
- TurnAction works through BodyRig
- BodyRig owns creature root rotation
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np

from mathlab_creature.core.geometry import as_vec3
from mathlab_creature.core.geometry import zero_vector
from mathlab_creature.core.kinematics import shortest_angle_difference
from mathlab_creature.creature.rigs.body_rig import BodyRig
from mathlab_creature.creature.actions.turn_action import TurnAction
from mathlab_creature.creature.actions.turn_action import build_turn_action


class RotationMode(str, Enum):
    IDLE = "idle"
    FACE_DIRECTION = "face_direction"
    FACE_TARGET = "face_target"
    FACE_MOVEMENT = "face_movement"
    MANUAL_ROTATION = "manual_rotation"


@dataclass
class RotationControllerConfig:
    facing_threshold: float = 0.001
    auto_face_movement: bool = True


class RotationController:
    """
    High-level orientation controller.
    """

    def __init__(
        self,
        body_rig: BodyRig,
        config: RotationControllerConfig | None = None,
    ) -> None:
        if not isinstance(body_rig, BodyRig):
            raise TypeError(
                f"body_rig must be BodyRig, got {type(body_rig).__name__}"
            )

        self.body_rig = body_rig
        self.config = config or RotationControllerConfig()

        self.turn_action: TurnAction = build_turn_action(body_rig)

        self.mode = RotationMode.IDLE

        self.current_angle = 0.0
        self.target_angle = 0.0
        self.rotation_velocity = 0.0
        self.manual_input = 0.0

        self.target_position = zero_vector()

        self.current_direction = zero_vector()
        self.current_direction[1] = 1.0

        self.auto_face_enabled = self.config.auto_face_movement
        self.is_rotating = False

    def update(
        self,
        delta_time: float,
    ) -> None:
        delta_time = float(delta_time)

        if delta_time <= 0:
            return

        if (
            self.auto_face_enabled
            and self.mode == RotationMode.FACE_MOVEMENT
        ):
            self._update_face_movement()

        if self.mode == RotationMode.FACE_TARGET:
            self._update_face_target()

        self.turn_action.update(delta_time)

        self.current_angle = self.turn_action.get_current_angle()

        angle_difference = abs(
            shortest_angle_difference(
                self.current_angle,
                self.target_angle,
            )
        )

        self.is_rotating = (
            angle_difference
            > self.config.facing_threshold
        )

    def face_direction(
        self,
        direction,
    ) -> None:
        direction_vec = as_vec3(
            direction,
            name="direction",
        )

        magnitude = np.linalg.norm(direction_vec)

        if magnitude <= 1e-8:
            return

        direction_vec = direction_vec / magnitude

        self.current_direction = direction_vec

        target_angle = np.arctan2(
            direction_vec[1],
            direction_vec[0],
        )

        self.target_angle = target_angle
        self.turn_action.set_target_angle(target_angle)

        self.mode = RotationMode.FACE_DIRECTION

    def face_position(
        self,
        world_position,
    ) -> None:
        self.target_position = as_vec3(
            world_position,
            name="world_position",
        )

        self.mode = RotationMode.FACE_TARGET
        self._update_face_target()

    def _update_face_target(self) -> None:
        direction = (
            self.target_position
            - self.body_rig.current_position
        )

        magnitude = np.linalg.norm(direction)

        if magnitude <= 1e-8:
            return

        self.face_direction(
            direction / magnitude,
        )

    def face_movement_direction(self) -> None:
        self.mode = RotationMode.FACE_MOVEMENT

    def _update_face_movement(self) -> None:
        velocity = self.body_rig.current_velocity
        magnitude = np.linalg.norm(velocity)

        if magnitude <= 1e-8:
            return

        self.face_direction(
            velocity / magnitude,
        )

    def rotate_left(
        self,
        intensity: float = 1.0,
    ) -> None:
        self.manual_input = abs(float(intensity))
        self.turn_action.turn_left(intensity)
        self.mode = RotationMode.MANUAL_ROTATION

    def rotate_right(
        self,
        intensity: float = 1.0,
    ) -> None:
        self.manual_input = -abs(float(intensity))
        self.turn_action.turn_right(intensity)
        self.mode = RotationMode.MANUAL_ROTATION

    def stop_rotation(self) -> None:
        self.manual_input = 0.0
        self.turn_action.stop_turning()
        self.mode = RotationMode.IDLE

    def rotate_to(
        self,
        angle: float,
    ) -> None:
        self.target_angle = float(angle)
        self.turn_action.set_target_angle(self.target_angle)
        self.mode = RotationMode.FACE_DIRECTION

    def look_at(
        self,
        target_position,
    ) -> None:
        self.face_position(target_position)

    def enable_auto_face(self) -> None:
        self.auto_face_enabled = True

    def disable_auto_face(self) -> None:
        self.auto_face_enabled = False

    def rotating(self) -> bool:
        return bool(self.is_rotating)

    def get_current_angle(self) -> float:
        return float(self.turn_action.get_current_angle())

    def get_target_angle(self) -> float:
        return float(self.target_angle)

    def get_mode(self) -> RotationMode:
        return self.mode

    def get_facing_direction(self):
        return np.array(
            self.current_direction,
            dtype=float,
        )

    def reset(self) -> None:
        self.current_angle = 0.0
        self.target_angle = 0.0
        self.rotation_velocity = 0.0
        self.manual_input = 0.0

        self.current_direction = zero_vector()
        self.current_direction[1] = 1.0

        self.mode = RotationMode.IDLE
        self.is_rotating = False

        self.turn_action.reset()

    def debug_print(self) -> None:
        print("======= ROTATION CONTROLLER =======")
        print("Mode:", self.mode)
        print("Current Angle:", self.current_angle)
        print("Target Angle:", self.target_angle)
        print("Direction:", self.current_direction)
        print("Rotating:", self.is_rotating)
        print("===================================")

    def __repr__(self) -> str:
        return f"RotationController(mode={self.mode!r})"


def build_rotation_controller(
    body_rig: BodyRig,
    config: RotationControllerConfig | None = None,
) -> RotationController:
    return RotationController(
        body_rig=body_rig,
        config=config,
    )


__all__ = [
    "RotationMode",
    "RotationControllerConfig",
    "RotationController",
    "build_rotation_controller",
]