"""
mathlab_creature/creature/controllers/rotation_controller.py

Production-grade creature orientation controller.

Core Responsibilities
---------------------
- smooth facing
- orientation control
- procedural turning
- directional alignment
- movement-facing synchronization
- cinematic rotation blending

Design Goals
------------
- production-ready
- cinematic motion
- smooth turning
- future AI-ready
- future 3D-ready
- controller-safe
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np

from mathlab_creature.core.transforms import (
    vec3,
)

from mathlab_creature.core.kinematics import (
    smooth_rotate_towards,
    shortest_angle_difference,
    damp,
    clamp,
)

from mathlab_creature.creature.rigs.body_rig import (
    BodyRig,
)

from mathlab_creature.creature.actions.turn_action import (
    TurnAction,
    build_turn_action,
)


# =========================================================
# ENUMS
# =========================================================

class RotationMode(str, Enum):
    """
    Rotation controller states.
    """

    IDLE = "idle"

    FACE_DIRECTION = "face_direction"

    FACE_TARGET = "face_target"

    FACE_MOVEMENT = "face_movement"

    MANUAL_ROTATION = "manual_rotation"


# =========================================================
# CONFIG
# =========================================================

@dataclass
class RotationControllerConfig:
    """
    Tunable orientation settings.
    """

    rotation_speed: float = 5.0

    rotation_damping: float = 0.88

    turn_smoothing: float = 7.0

    max_rotation_speed: float = 10.0

    auto_face_movement: bool = True

    facing_threshold: float = 0.001

    lean_strength: float = 0.14

    predictive_rotation: bool = True


# =========================================================
# ROTATION CONTROLLER
# =========================================================

class RotationController:
    """
    MASTER ORIENTATION CONTROLLER.

    Responsibilities:
    - creature facing
    - smooth turning
    - movement orientation
    - cinematic rotation
    - directional tracking
    """

    def __init__(
        self,
        body_rig: BodyRig,
        config: RotationControllerConfig | None = None,
    ):
        self.body_rig = body_rig

        self.config = (
            config
            or RotationControllerConfig()
        )

        # -------------------------------------------------
        # TURN ACTION
        # -------------------------------------------------

        self.turn_action: TurnAction = (
            build_turn_action(
                body_rig
            )
        )

        # -------------------------------------------------
        # ROTATION STATE
        # -------------------------------------------------

        self.mode = RotationMode.IDLE

        self.current_angle = 0.0

        self.target_angle = 0.0

        self.rotation_velocity = 0.0

        self.manual_input = 0.0

        # -------------------------------------------------
        # TARGET TRACKING
        # -------------------------------------------------

        self.target_position = vec3()

        self.current_direction = vec3(
            0.0,
            1.0,
            0.0,
        )

        self.auto_face_enabled = True

        self.is_rotating = False

    # =====================================================
    # UPDATE
    # =====================================================

    def update(
        self,
        delta_time: float,
    ):
        """
        Main orientation update.
        """

        # -------------------------------------------------
        # AUTO FACE MOVEMENT
        # -------------------------------------------------

        if (
            self.auto_face_enabled
            and self.mode
            == RotationMode.FACE_MOVEMENT
        ):
            self._update_face_movement()

        # -------------------------------------------------
        # FACE TARGET
        # -------------------------------------------------

        if (
            self.mode
            == RotationMode.FACE_TARGET
        ):
            self._update_face_target()

        # -------------------------------------------------
        # TURN ACTION
        # -------------------------------------------------

        self.turn_action.update(
            delta_time
        )

        # -------------------------------------------------
        # STATE
        # -------------------------------------------------

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

    # =====================================================
    # FACE DIRECTION
    # =====================================================

    def face_direction(
        self,
        direction,
    ):
        """
        Rotate toward vector direction.
        """

        direction = np.array(
            direction,
            dtype=float,
        )

        magnitude = np.linalg.norm(direction)

        if magnitude <= 1e-5:
            return

        direction /= magnitude

        self.current_direction = direction

        target_angle = np.arctan2(
            direction[1],
            direction[0],
        )

        self.target_angle = target_angle

        self.turn_action.set_target_angle(
            target_angle
        )

        self.mode = (
            RotationMode.FACE_DIRECTION
        )

    # =====================================================
    # FACE POSITION
    # =====================================================

    def face_position(
        self,
        world_position,
    ):
        """
        Rotate toward world-space target.
        """

        world_position = np.array(
            world_position,
            dtype=float,
        )

        self.target_position = (
            world_position
        )

        self.mode = (
            RotationMode.FACE_TARGET
        )

        self._update_face_target()

    # =====================================================
    # FACE TARGET UPDATE
    # =====================================================

    def _update_face_target(self):
        """
        Track target position.
        """

        creature_position = (
            self.body_rig.current_position
        )

        direction = (
            self.target_position
            - creature_position
        )

        magnitude = np.linalg.norm(
            direction
        )

        if magnitude <= 1e-5:
            return

        direction /= magnitude

        self.face_direction(
            direction
        )

    # =====================================================
    # FACE MOVEMENT
    # =====================================================

    def face_movement_direction(self):
        """
        Automatically orient toward velocity.
        """

        self.mode = (
            RotationMode.FACE_MOVEMENT
        )

    def _update_face_movement(self):
        """
        Movement-direction tracking.
        """

        velocity = (
            self.body_rig.current_velocity
        )

        magnitude = np.linalg.norm(
            velocity
        )

        if magnitude <= 1e-5:
            return

        velocity /= magnitude

        self.face_direction(
            velocity
        )

    # =====================================================
    # MANUAL ROTATION
    # =====================================================

    def rotate_left(
        self,
        intensity: float = 1.0,
    ):
        """
        Manual left turning.
        """

        self.manual_input = abs(
            intensity
        )

        self.turn_action.turn_left(
            intensity
        )

        self.mode = (
            RotationMode.MANUAL_ROTATION
        )

    def rotate_right(
        self,
        intensity: float = 1.0,
    ):
        """
        Manual right turning.
        """

        self.manual_input = -abs(
            intensity
        )

        self.turn_action.turn_right(
            intensity
        )

        self.mode = (
            RotationMode.MANUAL_ROTATION
        )

    def stop_rotation(self):
        """
        Stop active turning.
        """

        self.manual_input = 0.0

        self.turn_action.stop_turning()

        self.mode = RotationMode.IDLE

    # =====================================================
    # ABSOLUTE ROTATION
    # =====================================================

    def rotate_to(
        self,
        angle: float,
    ):
        """
        Rotate toward exact angle.
        """

        self.target_angle = angle

        self.turn_action.set_target_angle(
            angle
        )

        self.mode = (
            RotationMode.FACE_DIRECTION
        )

    # =====================================================
    # LOOK AT
    # =====================================================

    def look_at(
        self,
        target_position,
    ):
        """
        Cinematic look-at behavior.
        """

        self.face_position(
            target_position
        )

    # =====================================================
    # AUTO FACE
    # =====================================================

    def enable_auto_face(self):
        self.auto_face_enabled = True

    def disable_auto_face(self):
        self.auto_face_enabled = False

    # =====================================================
    # STATE
    # =====================================================

    def rotating(self):
        return self.is_rotating

    def get_current_angle(self):
        return self.turn_action.current_angle

    def get_target_angle(self):
        return self.target_angle

    def get_mode(self):
        return self.mode

    def get_facing_direction(self):
        return np.array(
            self.current_direction
        )

    # =====================================================
    # RESET
    # =====================================================

    def reset(self):
        """
        Reset orientation controller.
        """

        self.current_angle = 0.0

        self.target_angle = 0.0

        self.rotation_velocity = 0.0

        self.manual_input = 0.0

        self.current_direction = vec3(
            0.0,
            1.0,
            0.0,
        )

        self.mode = RotationMode.IDLE

        self.is_rotating = False

        self.turn_action.reset()

    # =====================================================
    # DEBUG
    # =====================================================

    def debug_print(self):
        print("======= ROTATION CONTROLLER =======")
        print("Mode:", self.mode)
        print("Current Angle:", self.current_angle)
        print("Target Angle:", self.target_angle)
        print("Direction:", self.current_direction)
        print("Rotating:", self.is_rotating)
        print("===================================")

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self):
        return (
            f"RotationController("
            f"mode='{self.mode}'"
            f")"
        )


# =========================================================
# FACTORY HELPERS
# =========================================================

def build_rotation_controller(
    body_rig: BodyRig,
    config: RotationControllerConfig | None = None,
) -> RotationController:
    """
    Create production-grade orientation controller.
    """

    return RotationController(
        body_rig=body_rig,
        config=config,
    )