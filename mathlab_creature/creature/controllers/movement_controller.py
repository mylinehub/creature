"""
Movement controller for mathlab-mylinehub-creature.

Controls high-level movement for one connected creature.

Architecture rule:
- movement_controller.py does not move body parts directly
- movement_controller.py works through BodyRig and actions
- BodyRig owns root movement
- WalkAction owns walking state
- TurnAction owns turning state
- IdleAction owns idle state
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np

from mathlab_creature.core.geometry import as_vec3
from mathlab_creature.core.geometry import zero_vector
from mathlab_creature.creature.rigs.body_rig import BodyRig
from mathlab_creature.creature.actions.walk_action import WalkAction
from mathlab_creature.creature.actions.walk_action import build_walk_action
from mathlab_creature.creature.actions.idle_action import IdleAction
from mathlab_creature.creature.actions.idle_action import build_idle_action
from mathlab_creature.creature.actions.turn_action import TurnAction
from mathlab_creature.creature.actions.turn_action import build_turn_action


class MovementMode(str, Enum):
    IDLE = "idle"
    WALKING = "walking"
    MOVING = "moving"
    FOLLOWING_PATH = "following_path"
    TELEPORTING = "teleporting"
    HIDDEN = "hidden"


@dataclass
class MovementControllerConfig:
    move_speed: float = 1.0
    run_speed: float = 2.0
    precision_speed: float = 0.35

    arrival_threshold: float = 0.05
    path_point_threshold: float = 0.08

    auto_rotate: bool = True
    enable_idle_animation: bool = True


class MovementController:
    """
    High-level movement controller.
    """

    def __init__(
        self,
        body_rig: BodyRig,
        config: MovementControllerConfig | None = None,
    ) -> None:
        if not isinstance(body_rig, BodyRig):
            raise TypeError(
                f"body_rig must be BodyRig, got {type(body_rig).__name__}"
            )

        self.body_rig = body_rig
        self.config = config or MovementControllerConfig()

        self.walk_action: WalkAction = build_walk_action(body_rig)
        self.idle_action: IdleAction = build_idle_action(body_rig)
        self.turn_action: TurnAction = build_turn_action(body_rig)

        self.mode = MovementMode.IDLE

        self.current_target = zero_vector()
        self.current_velocity = zero_vector()

        self.current_direction = zero_vector()
        self.current_direction[1] = 1.0

        self.current_speed = 0.0
        self.is_hidden = False

        self.path_points: list[np.ndarray] = []
        self.current_path_index = 0
        self.path_active = False

    def update(
        self,
        delta_time: float,
    ) -> None:
        delta_time = float(delta_time)

        if delta_time <= 0:
            return

        if self.path_active:
            self._update_path_following(delta_time)

        self.walk_action.update(delta_time)
        self.turn_action.update(delta_time)

        if (
            self.mode == MovementMode.IDLE
            and self.config.enable_idle_animation
        ):
            self.idle_action.update(delta_time)

    def move_to(
        self,
        position,
    ) -> None:
        """
        Smooth non-walking movement target.
        """
        position_vec = as_vec3(
            position,
            name="position",
        )

        self.current_target = position_vec
        self.mode = MovementMode.MOVING

        self.body_rig.move_towards(
            position_vec,
            delta_time=0.016,
        )

    def walk_to(
        self,
        target_position,
        speed: float | None = None,
    ) -> None:
        target = as_vec3(
            target_position,
            name="target_position",
        )

        speed = (
            float(speed)
            if speed is not None
            else self.config.move_speed
        )

        self.current_target = target

        current_position = self.body_rig.current_position
        direction = target - current_position
        distance = np.linalg.norm(direction)

        if distance <= self.config.arrival_threshold:
            self.stop()
            return

        direction = direction / max(distance, 1e-8)

        self.current_direction = direction
        self.current_speed = speed

        if self.config.auto_rotate:
            self.turn_action.face_direction(direction)

        self.walk_action.start(
            direction=direction,
            speed=speed,
        )

        self.mode = MovementMode.WALKING

    def teleport(
        self,
        position,
    ) -> None:
        position_vec = as_vec3(
            position,
            name="position",
        )

        self.mode = MovementMode.TELEPORTING

        self.body_rig.teleport(position_vec)
        self.current_target = position_vec

        self.mode = MovementMode.IDLE

    def follow_path(
        self,
        path_points,
        speed: float | None = None,
    ) -> None:
        if not path_points:
            return

        self.path_points = [
            as_vec3(point, name="path_point")
            for point in path_points
        ]

        self.current_path_index = 0
        self.path_active = True
        self.mode = MovementMode.FOLLOWING_PATH

        self.current_speed = (
            float(speed)
            if speed is not None
            else self.config.move_speed
        )

    def _update_path_following(
        self,
        delta_time: float,
    ) -> None:
        if self.current_path_index >= len(self.path_points):
            self.stop_path()
            return

        target = self.path_points[self.current_path_index]
        current_position = self.body_rig.current_position

        direction = target - current_position
        distance = np.linalg.norm(direction)

        if distance <= self.config.path_point_threshold:
            self.current_path_index += 1
            return

        direction = direction / max(distance, 1e-8)

        self.current_direction = direction

        if self.config.auto_rotate:
            self.turn_action.face_direction(direction)

        self.walk_action.start(
            direction=direction,
            speed=self.current_speed,
        )

    def hide(self) -> None:
        self.body_rig.hide_creature()
        self.is_hidden = True
        self.mode = MovementMode.HIDDEN

    def show(self) -> None:
        self.body_rig.show_creature()
        self.is_hidden = False
        self.mode = MovementMode.IDLE

    def toggle_visibility(self) -> None:
        if self.is_hidden:
            self.show()
        else:
            self.hide()

    def stop(self) -> None:
        self.walk_action.stop()

        self.current_velocity = zero_vector()
        self.current_speed = 0.0

        self.mode = MovementMode.IDLE

    def stop_path(self) -> None:
        self.path_active = False
        self.path_points.clear()
        self.current_path_index = 0
        self.stop()

    def face_direction(
        self,
        direction,
    ) -> None:
        self.turn_action.face_direction(direction)

    def set_move_speed(
        self,
        speed: float,
    ) -> None:
        self.config.move_speed = max(0.0, float(speed))

    def sprint(self) -> None:
        self.current_speed = self.config.run_speed
        self.walk_action.set_speed(self.current_speed)

    def precision_move(self) -> None:
        self.current_speed = self.config.precision_speed
        self.walk_action.set_speed(self.current_speed)

    def moving(self) -> bool:
        return self.mode != MovementMode.IDLE

    def hidden(self) -> bool:
        return bool(self.is_hidden)

    def following_path(self) -> bool:
        return bool(self.path_active)

    def get_mode(self) -> MovementMode:
        return self.mode

    def get_current_target(self):
        return np.array(
            self.current_target,
            dtype=float,
        )

    def reset(self) -> None:
        self.stop_path()

        self.walk_action.reset()
        self.turn_action.reset()
        self.idle_action.reset()

        self.current_target = zero_vector()
        self.current_velocity = zero_vector()

        self.current_direction = zero_vector()
        self.current_direction[1] = 1.0

        self.current_speed = 0.0
        self.mode = MovementMode.IDLE

    def debug_print(self) -> None:
        print("======= MOVEMENT CONTROLLER =======")
        print("Mode:", self.mode)
        print("Target:", self.current_target)
        print("Direction:", self.current_direction)
        print("Speed:", self.current_speed)
        print("Path Active:", self.path_active)
        print("Path Index:", self.current_path_index)
        print("===================================")

    def __repr__(self) -> str:
        return f"MovementController(mode={self.mode!r})"


def build_movement_controller(
    body_rig: BodyRig,
    config: MovementControllerConfig | None = None,
) -> MovementController:
    return MovementController(
        body_rig=body_rig,
        config=config,
    )


__all__ = [
    "MovementMode",
    "MovementControllerConfig",
    "MovementController",
    "build_movement_controller",
]