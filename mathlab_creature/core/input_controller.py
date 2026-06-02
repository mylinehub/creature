"""
Input and command routing system for mathlab-mylinehub-creature.

This module handles reusable input state for creature movement and interaction.

Core responsibilities:
- keyboard input state
- arrow key movement
- ctrl / shift / alt modifiers
- action state
- command routing
- future controller expansion
- future AI-input support
- future network-input support

Architecture rule:
- input_controller.py does not move Manim objects directly
- input_controller.py does not move creature parts directly
- input_controller.py produces command/state data only
- movement_controller.py later decides how CreatureRoot moves
- audio is not handled here; audio can be triggered later by actions
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import Optional

import numpy as np

from mathlab_creature.core.geometry import normalize
from mathlab_creature.core.geometry import zero_vector


# ============================================================
# Type aliases
# ============================================================

Vector3 = np.ndarray
CommandHandler = Callable[..., object]


# ============================================================
# Input enums
# ============================================================

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


# ============================================================
# Input state
# ============================================================

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
        default_factory=zero_vector,
    )

    rotation_direction: float = 0.0

    is_moving: bool = False
    is_rotating: bool = False
    is_jumping: bool = False

    movement_state: MovementState = MovementState.IDLE
    active_action: InputAction = InputAction.IDLE

    modifiers: ModifierState = field(
        default_factory=ModifierState,
    )


# ============================================================
# Command router
# ============================================================

class CommandRouter:
    """
    Routes high-level commands to registered handlers.

    This allows:
    - keyboard control
    - AI control
    - network control
    - scripted control

    using the same command layer.
    """

    def __init__(self) -> None:
        self.handlers: dict[InputAction, CommandHandler] = {}

    def register(
        self,
        action: InputAction,
        handler: CommandHandler,
    ) -> None:
        """
        Register a command handler for an action.
        """
        if not isinstance(action, InputAction):
            raise TypeError(
                f"action must be InputAction, got {type(action).__name__}"
            )

        if not callable(handler):
            raise TypeError(
                "handler must be callable"
            )

        self.handlers[action] = handler

    def unregister(
        self,
        action: InputAction,
    ) -> None:
        """
        Remove a command handler.
        """
        self.handlers.pop(
            action,
            None,
        )

    def execute(
        self,
        action: InputAction,
        *args,
        **kwargs,
    ):
        """
        Execute handler for action if registered.
        """
        handler = self.handlers.get(action)

        if handler is None:
            return None

        return handler(
            *args,
            **kwargs,
        )

    def has_handler(
        self,
        action: InputAction,
    ) -> bool:
        """
        Return True if action has a registered handler.
        """
        return action in self.handlers

    def clear(self) -> None:
        """
        Remove all registered handlers.
        """
        self.handlers.clear()


# ============================================================
# Input controller
# ============================================================

class InputController:
    """
    Main creature input controller.

    Handles:
    - key state
    - movement vectors
    - modifiers
    - command dispatch
    - action state

    It does not directly move the creature.
    """

    DEFAULT_KEYMAP: dict[str, InputAction] = {
        "UP": InputAction.WALK_FORWARD,
        "DOWN": InputAction.WALK_BACKWARD,
        "LEFT": InputAction.ROTATE_LEFT,
        "RIGHT": InputAction.ROTATE_RIGHT,
        "SPACE": InputAction.JUMP,
        "R": InputAction.RESET,
        "T": InputAction.TOGGLE_DEBUG,
        "G": InputAction.TOGGLE_JOINTS,
    }

    MODIFIER_KEYS: set[str] = {
        "SHIFT",
        "CTRL",
        "ALT",
    }

    def __init__(self) -> None:
        self.input_state = InputState()
        self.command_router = CommandRouter()

        self.keymap = dict(self.DEFAULT_KEYMAP)
        self.pressed_keys: set[str] = set()

        self.walk_speed = 1.0
        self.run_multiplier = 2.0
        self.precision_multiplier = 0.35
        self.rotation_speed = 1.0

    # ========================================================
    # Keyboard input
    # ========================================================

    def press_key(
        self,
        key: str,
    ) -> None:
        """
        Register key press.
        """
        normalized_key = self._normalize_key(key)

        self.pressed_keys.add(normalized_key)

        self._update_modifier_state(normalized_key)
        self._rebuild_input_state()

    def release_key(
        self,
        key: str,
    ) -> None:
        """
        Register key release.
        """
        normalized_key = self._normalize_key(key)

        self.pressed_keys.discard(normalized_key)

        self._update_modifier_release(normalized_key)
        self._rebuild_input_state()

    def set_pressed_keys(
        self,
        keys: set[str],
    ) -> None:
        """
        Replace current pressed-key set.

        Useful for scripted or AI-driven input.
        """
        self.pressed_keys = {
            self._normalize_key(key)
            for key in keys
        }

        self._sync_modifier_state_from_pressed_keys()
        self._rebuild_input_state()

    def clear_pressed_keys(self) -> None:
        """
        Clear all pressed keys.
        """
        self.pressed_keys.clear()
        self._sync_modifier_state_from_pressed_keys()
        self._rebuild_input_state()

    # ========================================================
    # Modifier handling
    # ========================================================

    def _normalize_key(
        self,
        key: str,
    ) -> str:
        """
        Normalize key string.
        """
        if not isinstance(key, str):
            raise TypeError(
                f"key must be str, got {type(key).__name__}"
            )

        cleaned = key.strip().upper()

        if not cleaned:
            raise ValueError(
                "key must not be empty"
            )

        return cleaned

    def _update_modifier_state(
        self,
        key: str,
    ) -> None:
        """
        Mark modifier as pressed.
        """
        if key == "SHIFT":
            self.input_state.modifiers.shift = True
        elif key == "CTRL":
            self.input_state.modifiers.ctrl = True
        elif key == "ALT":
            self.input_state.modifiers.alt = True

    def _update_modifier_release(
        self,
        key: str,
    ) -> None:
        """
        Mark modifier as released.
        """
        if key == "SHIFT":
            self.input_state.modifiers.shift = False
        elif key == "CTRL":
            self.input_state.modifiers.ctrl = False
        elif key == "ALT":
            self.input_state.modifiers.alt = False

    def _sync_modifier_state_from_pressed_keys(self) -> None:
        """
        Recompute modifier state from current pressed keys.
        """
        self.input_state.modifiers.shift = "SHIFT" in self.pressed_keys
        self.input_state.modifiers.ctrl = "CTRL" in self.pressed_keys
        self.input_state.modifiers.alt = "ALT" in self.pressed_keys

    # ========================================================
    # Input state building
    # ========================================================

    def _rebuild_input_state(self) -> None:
        """
        Recompute movement/action state.
        """
        state = self.input_state

        state.move_vector = zero_vector()
        state.rotation_direction = 0.0

        state.is_moving = False
        state.is_rotating = False
        state.is_jumping = False

        state.active_action = InputAction.IDLE
        state.movement_state = MovementState.IDLE

        if "UP" in self.pressed_keys:
            state.move_vector += np.array(
                [0.0, 1.0, 0.0],
                dtype=float,
            )
            state.is_moving = True
            state.active_action = InputAction.WALK_FORWARD

        if "DOWN" in self.pressed_keys:
            state.move_vector += np.array(
                [0.0, -1.0, 0.0],
                dtype=float,
            )
            state.is_moving = True
            state.active_action = InputAction.WALK_BACKWARD

        if "LEFT" in self.pressed_keys:
            state.rotation_direction = 1.0
            state.is_rotating = True

            if not state.is_moving:
                state.active_action = InputAction.ROTATE_LEFT

        if "RIGHT" in self.pressed_keys:
            state.rotation_direction = -1.0
            state.is_rotating = True

            if not state.is_moving:
                state.active_action = InputAction.ROTATE_RIGHT

        if "SPACE" in self.pressed_keys:
            state.is_jumping = True
            state.active_action = InputAction.JUMP
            state.movement_state = MovementState.JUMPING

        elif state.is_moving:
            if state.modifiers.shift:
                state.movement_state = MovementState.RUNNING
            else:
                state.movement_state = MovementState.WALKING

        elif state.is_rotating:
            state.movement_state = MovementState.ROTATING

    # ========================================================
    # Speed helpers
    # ========================================================

    def get_speed_multiplier(self) -> float:
        """
        Return movement speed multiplier from modifiers.

        shift -> run
        ctrl  -> precision
        normal -> 1.0
        """
        modifiers = self.input_state.modifiers

        if modifiers.shift:
            return self.run_multiplier

        if modifiers.ctrl:
            return self.precision_multiplier

        return 1.0

    def get_current_move_speed(self) -> float:
        """
        Return final movement speed.
        """
        return (
            self.walk_speed
            * self.get_speed_multiplier()
        )

    def get_current_rotation_speed(self) -> float:
        """
        Return final rotation speed.
        """
        return (
            self.rotation_speed
            * self.get_speed_multiplier()
        )

    # ========================================================
    # Movement vectors
    # ========================================================

    def get_movement_vector(self) -> Vector3:
        """
        Return normalized movement direction.
        """
        vector = self.input_state.move_vector

        if np.linalg.norm(vector) <= 1e-8:
            return zero_vector()

        return normalize(vector)

    def get_scaled_movement_vector(self) -> Vector3:
        """
        Return speed-scaled movement vector.
        """
        return (
            self.get_movement_vector()
            * self.get_current_move_speed()
        )

    def get_rotation_direction(self) -> float:
        """
        Return rotation direction.

        left  -> +1
        right -> -1
        none  -> 0
        """
        return float(
            self.input_state.rotation_direction
        )

    def get_scaled_rotation_amount(self) -> float:
        """
        Return speed-scaled rotation value.
        """
        return (
            self.get_rotation_direction()
            * self.get_current_rotation_speed()
        )

    # ========================================================
    # Command routing
    # ========================================================

    def route_current_action(self):
        """
        Execute current action handler.
        """
        action = self.input_state.active_action

        return self.command_router.execute(
            action,
            self.input_state,
        )

    def register_action_handler(
        self,
        action: InputAction,
        handler: CommandHandler,
    ) -> None:
        """
        Register action handler.
        """
        self.command_router.register(
            action,
            handler,
        )

    def unregister_action_handler(
        self,
        action: InputAction,
    ) -> None:
        """
        Remove action handler.
        """
        self.command_router.unregister(
            action,
        )

    # ========================================================
    # Action helpers
    # ========================================================

    def has_input(self) -> bool:
        """
        Return True if any meaningful key is currently pressed.
        """
        return bool(
            self.pressed_keys
        )

    def current_action_name(self) -> str:
        """
        Return current action as plain string.
        """
        return self.input_state.active_action.value

    def current_movement_state_name(self) -> str:
        """
        Return movement state as plain string.
        """
        return self.input_state.movement_state.value

    def is_idle(self) -> bool:
        return self.input_state.movement_state == MovementState.IDLE

    def is_walking(self) -> bool:
        return self.input_state.movement_state == MovementState.WALKING

    def is_running(self) -> bool:
        return self.input_state.movement_state == MovementState.RUNNING

    def is_rotating(self) -> bool:
        return self.input_state.movement_state == MovementState.ROTATING

    def is_jumping(self) -> bool:
        return self.input_state.movement_state == MovementState.JUMPING

    def is_turning_left(self) -> bool:
        return (
            self.input_state.is_rotating
            and self.input_state.rotation_direction > 0
        )

    def is_turning_right(self) -> bool:
        return (
            self.input_state.is_rotating
            and self.input_state.rotation_direction < 0
        )

    def is_debug_toggle_requested(self) -> bool:
        return "T" in self.pressed_keys

    def is_joint_toggle_requested(self) -> bool:
        return "G" in self.pressed_keys

    def is_reset_requested(self) -> bool:
        return "R" in self.pressed_keys

    # ========================================================
    # Configuration
    # ========================================================

    def set_walk_speed(
        self,
        speed: float,
    ) -> None:
        """
        Set base walk speed.
        """
        self.walk_speed = max(
            0.0,
            float(speed),
        )

    def set_run_multiplier(
        self,
        multiplier: float,
    ) -> None:
        """
        Set shift/run multiplier.
        """
        self.run_multiplier = max(
            1.0,
            float(multiplier),
        )

    def set_precision_multiplier(
        self,
        multiplier: float,
    ) -> None:
        """
        Set ctrl/precision multiplier.
        """
        self.precision_multiplier = max(
            0.01,
            float(multiplier),
        )

    def set_rotation_speed(
        self,
        speed: float,
    ) -> None:
        """
        Set base rotation speed.
        """
        self.rotation_speed = max(
            0.0,
            float(speed),
        )

    # ========================================================
    # State access
    # ========================================================

    def get_state(self) -> InputState:
        """
        Return current input state.
        """
        return self.input_state

    def copy_pressed_keys(self) -> set[str]:
        """
        Return copy of pressed keys.
        """
        return set(
            self.pressed_keys
        )

    # ========================================================
    # Reset
    # ========================================================

    def reset(self) -> None:
        """
        Reset entire input state.
        """
        self.pressed_keys.clear()
        self.input_state = InputState()

    # ========================================================
    # Debug
    # ========================================================

    def debug_print(self) -> None:
        """
        Print input state for debugging.
        """
        state = self.input_state

        print("========== INPUT DEBUG ==========")
        print("Pressed Keys:", self.pressed_keys)
        print("Movement State:", state.movement_state)
        print("Active Action:", state.active_action)
        print("Move Vector:", state.move_vector)
        print("Rotation:", state.rotation_direction)
        print("Modifiers:", state.modifiers)
        print("=================================")


# ============================================================
# Export control
# ============================================================

__all__ = [
    "Vector3",
    "CommandHandler",
    "InputAction",
    "MovementState",
    "ModifierState",
    "InputState",
    "CommandRouter",
    "InputController",
]