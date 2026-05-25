"""
mathlab_creature/creature/controllers/movement_controller.py

Production-grade high-level creature movement controller.

Core Responsibilities
---------------------
- move_to
- walk_to
- teleport
- hide/show
- follow path
- movement orchestration
- action coordination
- navigation state

Design Goals
------------
- production-ready
- controller-driven architecture
- future AI-ready
- future pathfinding-ready
- future multiplayer-ready
- cinematic movement ready
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np

from mathlab_creature.core.transforms import (
    vec3,
)

from mathlab_creature.core.kinematics import (
    damp_vector,
    clamp,
)

from mathlab_creature.creature.rigs.body_rig import (
    BodyRig,
)

from mathlab_creature.creature.actions.walk_action import (
    WalkAction,
    build_walk_action,
)

from mathlab_creature.creature.actions.idle_action import (
    IdleAction,
    build_idle_action,
)

from mathlab_creature.creature.actions.turn_action import (
    TurnAction,
    build_turn_action,
)


# =========================================================
# ENUMS
# =========================================================

class MovementMode(str, Enum):
    """
    High-level movement states.
    """

    IDLE = "idle"

    WALKING = "walking"

    MOVING = "moving"

    FOLLOWING_PATH = "following_path"

    TELEPORTING = "teleporting"

    HIDDEN = "hidden"


# =========================================================
# CONFIG
# =========================================================

@dataclass
class MovementControllerConfig:
    """
    Tunable movement settings.
    """

    move_speed: float = 1.0

    run_speed: float = 2.0

    precision_speed: float = 0.35

    rotation_speed: float = 5.0

    arrival_threshold: float = 0.05

    path_point_threshold: float = 0.08

    movement_damping: float = 8.0

    auto_rotate: bool = True

    enable_idle_animation: bool = True


# =========================================================
# MOVEMENT CONTROLLER
# =========================================================

class MovementController:
    """
    MASTER MOVEMENT CONTROLLER.

    Responsibilities:
    - high-level movement commands
    - movement state management
    - path following
    - locomotion coordination
    - visibility management
    """

    def __init__(
        self,
        body_rig: BodyRig,
        config: MovementControllerConfig | None = None,
    ):
        self.body_rig = body_rig

        self.config = (
            config
            or MovementControllerConfig()
        )

        # -------------------------------------------------
        # ACTIONS
        # -------------------------------------------------

        self.walk_action: WalkAction = (
            build_walk_action(
                body_rig
            )
        )

        self.idle_action: IdleAction = (
            build_idle_action(
                body_rig
            )
        )

        self.turn_action: TurnAction = (
            build_turn_action(
                body_rig
            )
        )

        # -------------------------------------------------
        # MOVEMENT STATE
        # -------------------------------------------------

        self.mode = MovementMode.IDLE

        self.current_target = vec3()

        self.current_velocity = vec3()

        self.current_direction = vec3(
            0.0,
            1.0,
            0.0,
        )

        self.current_speed = 0.0

        self.is_hidden = False

        # -------------------------------------------------
        # PATH FOLLOWING
        # -------------------------------------------------

        self.path_points = []

        self.current_path_index = 0

        self.path_active = False

    # =====================================================
    # UPDATE
    # =====================================================

    def update(
        self,
        delta_time: float,
    ):
        """
        Main controller update.
        """

        # -------------------------------------------------
        # PATH FOLLOWING
        # -------------------------------------------------

        if self.path_active:
            self._update_path_following(
                delta_time
            )

        # -------------------------------------------------
        # WALK ACTION
        # -------------------------------------------------

        self.walk_action.update(
            delta_time
        )

        # -------------------------------------------------
        # TURN ACTION
        # -------------------------------------------------

        self.turn_action.update(
            delta_time
        )

        # -------------------------------------------------
        # IDLE
        # -------------------------------------------------

        if (
            self.mode
            == MovementMode.IDLE
        ):
            if (
                self.config.enable_idle_animation
            ):
                self.idle_action.update(
                    delta_time
                )

    # =====================================================
    # MOVE TO
    # =====================================================

    def move_to(
        self,
        position,
    ):
        """
        Smooth non-walking movement.
        """

        position = np.array(
            position,
            dtype=float,
        )

        self.current_target = position

        self.mode = MovementMode.MOVING

        self.body_rig.move_to(
            position
        )

    # =====================================================
    # WALK TO
    # =====================================================

    def walk_to(
        self,
        target_position,
        speed: float | None = None,
    ):
        """
        Procedural walking toward target.
        """

        target_position = np.array(
            target_position,
            dtype=float,
        )

        speed = (
            speed
            if speed is not None
            else self.config.move_speed
        )

        self.current_target = target_position

        current_position = (
            self.body_rig.current_position
        )

        direction = (
            target_position
            - current_position
        )

        distance = np.linalg.norm(
            direction
        )

        if (
            distance
            <= self.config.arrival_threshold
        ):
            self.stop()

            return

        direction /= distance

        self.current_direction = direction

        self.current_speed = speed

        # -------------------------------------------------
        # TURN
        # -------------------------------------------------

        if self.config.auto_rotate:
            self.turn_action.face_direction(
                direction
            )

        # -------------------------------------------------
        # WALK
        # -------------------------------------------------

        self.walk_action.start(
            direction=direction,
            speed=speed,
        )

        self.mode = MovementMode.WALKING

    # =====================================================
    # TELEPORT
    # =====================================================

    def teleport(
        self,
        position,
    ):
        """
        Instant reposition.
        """

        position = np.array(
            position,
            dtype=float,
        )

        self.mode = (
            MovementMode.TELEPORTING
        )

        self.body_rig.teleport(
            position
        )

        self.current_target = position

        self.mode = MovementMode.IDLE

    # =====================================================
    # FOLLOW PATH
    # =====================================================

    def follow_path(
        self,
        path_points,
        speed: float | None = None,
    ):
        """
        Begin procedural path following.
        """

        if len(path_points) == 0:
            return

        self.path_points = [
            np.array(
                point,
                dtype=float,
            )
            for point in path_points
        ]

        self.current_path_index = 0

        self.path_active = True

        self.mode = (
            MovementMode.FOLLOWING_PATH
        )

        self.current_speed = (
            speed
            if speed is not None
            else self.config.move_speed
        )

    # =====================================================
    # PATH UPDATE
    # =====================================================

    def _update_path_following(
        self,
        delta_time: float,
    ):
        """
        Procedural path traversal.
        """

        if (
            self.current_path_index
            >= len(self.path_points)
        ):
            self.stop_path()

            return

        target = self.path_points[
            self.current_path_index
        ]

        current_position = (
            self.body_rig.current_position
        )

        direction = (
            target
            - current_position
        )

        distance = np.linalg.norm(
            direction
        )

        # -------------------------------------------------
        # NEXT POINT
        # -------------------------------------------------

        if (
            distance
            <= self.config.path_point_threshold
        ):
            self.current_path_index += 1

            return

        # -------------------------------------------------
        # NORMALIZE
        # -------------------------------------------------

        direction /= max(distance, 1e-5)

        self.current_direction = direction

        # -------------------------------------------------
        # TURN
        # -------------------------------------------------

        self.turn_action.face_direction(
            direction
        )

        # -------------------------------------------------
        # WALK
        # -------------------------------------------------

        self.walk_action.start(
            direction,
            self.current_speed,
        )

    # =====================================================
    # VISIBILITY
    # =====================================================

    def hide(self):
        """
        Hide creature without state loss.
        """

        self.body_rig.hide_creature()

        self.is_hidden = True

        self.mode = MovementMode.HIDDEN

    def show(self):
        """
        Restore creature visibility.
        """

        self.body_rig.show_creature()

        self.is_hidden = False

        self.mode = MovementMode.IDLE

    def toggle_visibility(self):
        if self.is_hidden:
            self.show()
        else:
            self.hide()

    # =====================================================
    # STOP
    # =====================================================

    def stop(self):
        """
        Stop locomotion.
        """

        self.walk_action.stop()

        self.current_velocity = vec3()

        self.current_speed = 0.0

        self.mode = MovementMode.IDLE

    def stop_path(self):
        """
        Stop active path following.
        """

        self.path_active = False

        self.path_points.clear()

        self.current_path_index = 0

        self.stop()

    # =====================================================
    # ROTATION
    # =====================================================

    def face_direction(
        self,
        direction,
    ):
        """
        Rotate creature toward direction.
        """

        self.turn_action.face_direction(
            direction
        )

    # =====================================================
    # SPEED CONTROL
    # =====================================================

    def set_move_speed(
        self,
        speed: float,
    ):
        self.config.move_speed = max(
            0.0,
            speed,
        )

    def sprint(self):
        self.current_speed = (
            self.config.run_speed
        )

    def precision_move(self):
        self.current_speed = (
            self.config.precision_speed
        )

    # =====================================================
    # STATE
    # =====================================================

    def moving(self):
        return (
            self.mode
            != MovementMode.IDLE
        )

    def hidden(self):
        return self.is_hidden

    def following_path(self):
        return self.path_active

    def get_mode(self):
        return self.mode

    def get_current_target(self):
        return np.array(
            self.current_target
        )

    # =====================================================
    # RESET
    # =====================================================

    def reset(self):
        """
        Reset controller state.
        """

        self.stop_path()

        self.walk_action.reset()

        self.turn_action.reset()

        self.idle_action.reset()

        self.current_target = vec3()

        self.current_velocity = vec3()

        self.current_direction = vec3(
            0.0,
            1.0,
            0.0,
        )

        self.current_speed = 0.0

        self.mode = MovementMode.IDLE

    # =====================================================
    # DEBUG
    # =====================================================

    def debug_print(self):
        print("======= MOVEMENT CONTROLLER =======")
        print("Mode:", self.mode)
        print("Target:", self.current_target)
        print("Direction:", self.current_direction)
        print("Speed:", self.current_speed)
        print("Path Active:", self.path_active)
        print("Path Index:", self.current_path_index)
        print("===================================")

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self):
        return (
            f"MovementController("
            f"mode='{self.mode}'"
            f")"
        )


# =========================================================
# FACTORY HELPERS
# =========================================================

def build_movement_controller(
    body_rig: BodyRig,
    config: MovementControllerConfig | None = None,
) -> MovementController:
    """
    Create production-grade movement controller.
    """

    return MovementController(
        body_rig=body_rig,
        config=config,
    )