"""
mathlab_creature/core/input_controller.py

Production-grade input + command routing system
for creature movement and interaction.

Core Responsibilities
---------------------
- keyboard input state
- arrow key movement
- ctrl/shift modifiers
- action states
- command routing
- future controller expansion
- reusable movement commands

Design Goals
------------
- engine-safe
- reusable
- deterministic
- controller-friendly
- future multiplayer-ready
- future AI-input-ready
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, Optional

import numpy as np


# =========================================================
# VECTOR HELPERS
# =========================================================

Vector3 = np.ndarray


def vec3(x=0.0, y=0.0, z=0.0) -> Vector3:
    return np.array([x, y, z], dtype=float)


# =========================================================
# INPUT ENUMS
# =========================================================

class InputAction(str, Enum):
    """
    High-level creature actions.
    """

    IDLE = "idle"
    WALK_FORWARD = "walk_forward"
    WALK_BACKWARD = "walk_backward"
    ROTATE_LEFT = "rotate_left"
    ROTATE_RIGHT = "rotate_right"
    JUMP = "jump"
    RESET = "reset"
    TOGGLE_DEBUG = "toggle_debug"
    TOGGLE_JOINTS = "toggle_joints"


class MovementState(str, Enum):
    """
    Creature movement modes.
    """

    IDLE = "idle"
    WALKING = "walking"
    RUNNING = "running"
    ROTATING = "rotating"
    JUMPING = "jumping"


# =========================================================
# INPUT STATE
# =========================================================

@dataclass
class ModifierState:
    """
    Keyboard modifier states.
    """

    shift: bool = False
    ctrl: bool = False
    alt: bool = False


@dataclass
class InputState:
    """
    Runtime input state.
    """

    move_vector: Vector3 = field(
        default_factory=lambda: vec3()
    )

    rotation_direction: float = 0.0

    is_moving: bool = False
    is_rotating: bool = False
    is_jumping: bool = False

    movement_state: MovementState = (
        MovementState.IDLE
    )

    active_action: InputAction = (
        InputAction.IDLE
    )

    modifiers: ModifierState = field(
        default_factory=ModifierState
    )


# =========================================================
# COMMAND ROUTER
# =========================================================

class CommandRouter:
    """
    Routes high-level commands
    to registered handlers.

    This allows:
    - keyboard control
    - AI control
    - network control
    - scripted control

    using SAME command layer.
    """

    def __init__(self):
        self.handlers: Dict[
            InputAction,
            Callable
        ] = {}

    def register(
        self,
        action: InputAction,
        handler: Callable,
    ) -> None:
        self.handlers[action] = handler

    def execute(
        self,
        action: InputAction,
        *args,
        **kwargs,
    ):
        handler = self.handlers.get(action)

        if handler is None:
            return None

        return handler(*args, **kwargs)


# =========================================================
# INPUT CONTROLLER
# =========================================================

class InputController:
    """
    Main creature input controller.

    Handles:
    - key state
    - movement vectors
    - modifiers
    - command dispatch
    - action state
    """

    # -----------------------------------------------------
    # KEY MAPPING
    # -----------------------------------------------------

    DEFAULT_KEYMAP = {
        "UP": InputAction.WALK_FORWARD,
        "DOWN": InputAction.WALK_BACKWARD,
        "LEFT": InputAction.ROTATE_LEFT,
        "RIGHT": InputAction.ROTATE_RIGHT,
        "SPACE": InputAction.JUMP,
        "R": InputAction.RESET,
        "T": InputAction.TOGGLE_DEBUG,
        "G": InputAction.TOGGLE_JOINTS,
    }

    def __init__(self):
        self.input_state = InputState()

        self.command_router = CommandRouter()

        self.keymap = dict(self.DEFAULT_KEYMAP)

        self.pressed_keys = set()

        self.walk_speed = 1.0
        self.run_multiplier = 2.0
        self.precision_multiplier = 0.35

        self.rotation_speed = 1.0

    # =====================================================
    # KEYBOARD INPUT
    # =====================================================

    def press_key(self, key: str) -> None:
        """
        Register key press.
        """

        key = key.upper()

        self.pressed_keys.add(key)

        self._update_modifier_state(key)

        self._rebuild_input_state()

    def release_key(self, key: str) -> None:
        """
        Register key release.
        """

        key = key.upper()

        if key in self.pressed_keys:
            self.pressed_keys.remove(key)

        self._update_modifier_release(key)

        self._rebuild_input_state()

    # =====================================================
    # MODIFIERS
    # =====================================================

    def _update_modifier_state(self, key: str):
        if key == "SHIFT":
            self.input_state.modifiers.shift = True

        elif key == "CTRL":
            self.input_state.modifiers.ctrl = True

        elif key == "ALT":
            self.input_state.modifiers.alt = True

    def _update_modifier_release(self, key: str):
        if key == "SHIFT":
            self.input_state.modifiers.shift = False

        elif key == "CTRL":
            self.input_state.modifiers.ctrl = False

        elif key == "ALT":
            self.input_state.modifiers.alt = False

    # =====================================================
    # INPUT STATE BUILDING
    # =====================================================

    def _rebuild_input_state(self):
        """
        Recompute movement/action state.
        """

        state = self.input_state

        state.move_vector = vec3()

        state.rotation_direction = 0.0

        state.is_moving = False
        state.is_rotating = False
        state.is_jumping = False

        state.active_action = InputAction.IDLE
        state.movement_state = MovementState.IDLE

        # -------------------------------------------------
        # FORWARD / BACKWARD
        # -------------------------------------------------

        if "UP" in self.pressed_keys:
            state.move_vector += vec3(0.0, 1.0, 0.0)

            state.is_moving = True
            state.active_action = (
                InputAction.WALK_FORWARD
            )

        if "DOWN" in self.pressed_keys:
            state.move_vector += vec3(0.0, -1.0, 0.0)

            state.is_moving = True
            state.active_action = (
                InputAction.WALK_BACKWARD
            )

        # -------------------------------------------------
        # ROTATION
        # -------------------------------------------------

        if "LEFT" in self.pressed_keys:
            state.rotation_direction = 1.0

            state.is_rotating = True

            if not state.is_moving:
                state.active_action = (
                    InputAction.ROTATE_LEFT
                )

        if "RIGHT" in self.pressed_keys:
            state.rotation_direction = -1.0

            state.is_rotating = True

            if not state.is_moving:
                state.active_action = (
                    InputAction.ROTATE_RIGHT
                )

        # -------------------------------------------------
        # JUMP
        # -------------------------------------------------

        if "SPACE" in self.pressed_keys:
            state.is_jumping = True

            state.active_action = (
                InputAction.JUMP
            )

            state.movement_state = (
                MovementState.JUMPING
            )

        # -------------------------------------------------
        # WALK / RUN
        # -------------------------------------------------

        elif state.is_moving:
            if state.modifiers.shift:
                state.movement_state = (
                    MovementState.RUNNING
                )

            else:
                state.movement_state = (
                    MovementState.WALKING
                )

        elif state.is_rotating:
            state.movement_state = (
                MovementState.ROTATING
            )

    # =====================================================
    # SPEED HELPERS
    # =====================================================

    def get_speed_multiplier(self) -> float:
        """
        Speed modifier handling.
        """

        modifiers = self.input_state.modifiers

        if modifiers.shift:
            return self.run_multiplier

        if modifiers.ctrl:
            return self.precision_multiplier

        return 1.0

    def get_current_move_speed(self) -> float:
        return (
            self.walk_speed
            * self.get_speed_multiplier()
        )

    # =====================================================
    # MOVEMENT VECTORS
    # =====================================================

    def get_movement_vector(self) -> Vector3:
        """
        Normalized movement direction.
        """

        vector = self.input_state.move_vector

        magnitude = np.linalg.norm(vector)

        if magnitude <= 1e-8:
            return vec3()

        return vector / magnitude

    def get_scaled_movement_vector(self) -> Vector3:
        """
        Speed-scaled movement vector.
        """

        return (
            self.get_movement_vector()
            * self.get_current_move_speed()
        )

    # =====================================================
    # COMMAND ROUTING
    # =====================================================

    def route_current_action(self):
        """
        Execute current action handler.
        """

        action = self.input_state.active_action

        return self.command_router.execute(
            action,
            self.input_state,
        )

    # =====================================================
    # ACTION HELPERS
    # =====================================================

    def is_idle(self) -> bool:
        return (
            self.input_state.movement_state
            == MovementState.IDLE
        )

    def is_walking(self) -> bool:
        return (
            self.input_state.movement_state
            == MovementState.WALKING
        )

    def is_running(self) -> bool:
        return (
            self.input_state.movement_state
            == MovementState.RUNNING
        )

    def is_rotating(self) -> bool:
        return (
            self.input_state.movement_state
            == MovementState.ROTATING
        )

    def is_jumping(self) -> bool:
        return (
            self.input_state.movement_state
            == MovementState.JUMPING
        )

    # =====================================================
    # CONFIGURATION
    # =====================================================

    def set_walk_speed(self, speed: float):
        self.walk_speed = max(0.0, speed)

    def set_run_multiplier(self, multiplier: float):
        self.run_multiplier = max(1.0, multiplier)

    def set_precision_multiplier(
        self,
        multiplier: float,
    ):
        self.precision_multiplier = max(
            0.01,
            multiplier,
        )

    def set_rotation_speed(self, speed: float):
        self.rotation_speed = max(0.0, speed)

    # =====================================================
    # RESET
    # =====================================================

    def reset(self):
        """
        Reset entire input state.
        """

        self.pressed_keys.clear()

        self.input_state = InputState()

    # =====================================================
    # DEBUG
    # =====================================================

    def debug_print(self):
        state = self.input_state

        print("========== INPUT DEBUG ==========")
        print("Pressed Keys:", self.pressed_keys)
        print("Movement State:", state.movement_state)
        print("Active Action:", state.active_action)
        print("Move Vector:", state.move_vector)
        print("Rotation:", state.rotation_direction)
        print("Modifiers:", state.modifiers)
        print("=================================")