"""
Turn action for mathlab-mylinehub-creature.

Controls smooth turning for one connected creature.

Architecture:

    TurnAction
        |
        BodyRig
            |
            Creature Root

TurnAction never manipulates body parts directly.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from mathlab_creature.core.geometry import as_vec3
from mathlab_creature.core.geometry import point
from mathlab_creature.core.kinematics import damp
from mathlab_creature.core.kinematics import smooth_rotate_towards
from mathlab_creature.core.logger import get_logger
from mathlab_creature.creature.rigs.body_rig import BodyRig


logger = get_logger(__name__)


try:
    from mathlab_creature.core.audio.helpers import maybe_play_sound
    from mathlab_creature.core.audio.procedural import play_turn_sound
except Exception:
    maybe_play_sound = None
    play_turn_sound = None


@dataclass
class TurnActionConfig:
    turn_speed: float = 4.5

    turn_acceleration: float = 8.0

    turn_damping: float = 0.88

    max_turn_speed: float = 8.0

    body_lean_strength: float = 0.14

    hip_shift_strength: float = 0.06

    minimum_turn_threshold: float = 0.001

    auto_face_movement: bool = True

    enable_audio: bool = True

    turn_sound_volume: float = 1.0

    turn_sound_velocity_threshold: float = 1.2

    turn_sound_cooldown: float = 0.24


class TurnAction:
    """
    Smooth turning controller.

    Works through BodyRig only.
    """

    def __init__(
        self,
        body_rig: BodyRig,
        config: TurnActionConfig | None = None,
        with_sound: bool = True,
    ):
        if not isinstance(body_rig, BodyRig):
            raise TypeError(
                f"body_rig must be BodyRig, got {type(body_rig).__name__}"
            )

        self.body_rig = body_rig

        self.config = config or TurnActionConfig()

        self.with_sound = bool(with_sound)

        self.current_angle = 0.0
        self.target_angle = 0.0

        self.current_turn_velocity = 0.0

        self.turn_input = 0.0

        self.is_turning = False

        self.auto_rotate_enabled = True

        self.current_body_lean = 0.0
        self.current_hip_shift = 0.0

        self.turn_sound_timer = 0.0
        self.turn_sound_triggered = False

    def turn_left(
        self,
        intensity: float = 1.0,
    ):
        self.turn_input = abs(float(intensity))
        self.is_turning = True

    def turn_right(
        self,
        intensity: float = 1.0,
    ):
        self.turn_input = -abs(float(intensity))
        self.is_turning = True

    def stop_turning(self):
        self.turn_input = 0.0
        self.is_turning = False

    def set_target_angle(
        self,
        angle: float,
    ):
        self.target_angle = float(angle)

    def face_direction(
        self,
        direction,
    ):
        direction = as_vec3(
            direction,
            name="direction",
        )

        magnitude = np.linalg.norm(direction)

        if magnitude <= 1e-8:
            return

        direction = direction / magnitude

        self.target_angle = np.arctan2(
            direction[1],
            direction[0],
        )

    def update(
        self,
        delta_time: float,
    ):
        delta_time = float(delta_time)

        if delta_time <= 0:
            return

        self.turn_sound_timer += delta_time

        if self.is_turning:

            target_velocity = (
                self.turn_input
                * self.config.max_turn_speed
            )

            self.current_turn_velocity = damp(
                self.current_turn_velocity,
                target_velocity,
                self.config.turn_acceleration,
                delta_time,
            )

            self.target_angle += (
                self.current_turn_velocity
                * delta_time
            )

        self.current_angle = smooth_rotate_towards(
            self.current_angle,
            self.target_angle,
            self.config.turn_speed,
            delta_time,
        )

        self.body_rig.rotate_towards(
            self.current_angle,
            delta_time,
        )

        self._update_balance(
            delta_time,
        )

        self._update_audio()

    def _update_balance(
        self,
        delta_time: float,
    ):
        lean_target = (
            -self.current_turn_velocity
            * self.config.body_lean_strength
        )

        self.current_body_lean = damp(
            self.current_body_lean,
            lean_target,
            10.0,
            delta_time,
        )

        shift_target = (
            self.current_turn_velocity
            * self.config.hip_shift_strength
        )

        self.current_hip_shift = damp(
            self.current_hip_shift,
            shift_target,
            8.0,
            delta_time,
        )

        self.body_rig.body_tilt = (
            self.current_body_lean
        )

        self.body_rig.center_of_mass = point(
            self.current_hip_shift,
            0.0,
            0.0,
        )

    def _update_audio(
        self,
    ):
        if not self.with_sound:
            return

        if not self.config.enable_audio:
            return

        if (
            self.turn_sound_timer
            < self.config.turn_sound_cooldown
        ):
            return

        velocity = abs(
            self.current_turn_velocity
        )

        if (
            velocity
            < self.config.turn_sound_velocity_threshold
        ):
            self.turn_sound_triggered = False
            return

        if self.turn_sound_triggered:
            return

        if maybe_play_sound is None:
            return

        if play_turn_sound is None:
            return

        maybe_play_sound(
            self.with_sound,
            play_turn_sound,
            volume=self.config.turn_sound_volume,
        )

        self.turn_sound_triggered = True
        self.turn_sound_timer = 0.0

    def update_from_velocity(
        self,
        velocity,
    ):
        if not self.auto_rotate_enabled:
            return

        velocity = as_vec3(
            velocity,
            name="velocity",
        )

        magnitude = np.linalg.norm(
            velocity,
        )

        if magnitude <= 1e-8:
            return

        self.face_direction(
            velocity,
        )

    def turning(
        self,
    ):
        return (
            abs(self.current_turn_velocity)
            > self.config.minimum_turn_threshold
        )

    def get_current_angle(
        self,
    ):
        return self.current_angle

    def get_target_angle(
        self,
    ):
        return self.target_angle

    def get_turn_velocity(
        self,
    ):
        return self.current_turn_velocity

    def enable_sound(
        self,
    ):
        self.with_sound = True

    def disable_sound(
        self,
    ):
        self.with_sound = False

    def enable_auto_rotate(
        self,
    ):
        self.auto_rotate_enabled = True

    def disable_auto_rotate(
        self,
    ):
        self.auto_rotate_enabled = False

    def reset(
        self,
    ):
        self.current_angle = 0.0
        self.target_angle = 0.0

        self.current_turn_velocity = 0.0

        self.turn_input = 0.0

        self.current_body_lean = 0.0
        self.current_hip_shift = 0.0

        self.turn_sound_timer = 0.0
        self.turn_sound_triggered = False

        self.is_turning = False

    def debug_print(
        self,
    ):
        print("========== TURN ACTION ==========")
        print("Current Angle:", self.current_angle)
        print("Target Angle:", self.target_angle)
        print("Turn Velocity:", self.current_turn_velocity)
        print("Turning:", self.is_turning)
        print("Sound Enabled:", self.with_sound)
        print("=================================")

    def __repr__(
        self,
    ):
        return (
            f"TurnAction("
            f"angle={round(self.current_angle, 3)}, "
            f"velocity={round(self.current_turn_velocity, 3)}"
            f")"
        )


def build_turn_action(
    body_rig: BodyRig,
    config: TurnActionConfig | None = None,
    with_sound: bool = True,
):
    return TurnAction(
        body_rig=body_rig,
        config=config,
        with_sound=with_sound,
    )


__all__ = [
    "TurnActionConfig",
    "TurnAction",
    "build_turn_action",
]