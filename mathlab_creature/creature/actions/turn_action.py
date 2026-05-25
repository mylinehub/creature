# File: mathlab_creature/creature/actions/turn_action.py

"""
mathlab_creature/creature/actions/turn_action.py

Production-grade procedural turning system
with cinematic procedural audio integration.

Core Responsibilities
---------------------
- smooth turning
- directional rotation
- facing control
- rotational damping
- balance-aware turning
- procedural turn blending
- procedural turn audio
- cinematic turning rhythm

Design Goals
------------
- production-ready
- cinematic turning
- smooth motion
- animation-safe
- hierarchy-safe
- future AI-ready
- future 3D-ready
- educational mascot feel
- subtle expressive motion

Audio Goals
-----------
- soft sweep
- subtle directional cue
- airy turn motion
- alive but not annoying
- not harsh robotic movement
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from mathlab_creature.core.transforms import (
    vec3,
)

from mathlab_creature.core.kinematics import (
    shortest_angle_difference,
    smooth_rotate_towards,
    clamp,
    damp,
)

from mathlab_creature.core.logger import (
    get_logger,
)

from mathlab_creature.core.audio.helpers import (
    maybe_play_sound,
)

from mathlab_creature.core.audio.procedural import (
    play_turn_sound,
)

from mathlab_creature.creature.rigs.body_rig import (
    BodyRig,
)

logger = get_logger(__name__)


# =========================================================
# CONFIG
# =========================================================

@dataclass
class TurnActionConfig:
    """
    Tunable procedural turning settings.
    """

    turn_speed: float = 4.5

    turn_acceleration: float = 8.0

    turn_damping: float = 0.88

    max_turn_speed: float = 8.0

    body_lean_strength: float = 0.14

    foot_adjustment_strength: float = 0.18

    hip_shift_strength: float = 0.06

    minimum_turn_threshold: float = 0.001

    auto_face_movement: bool = True

    # -----------------------------------------------------
    # AUDIO SETTINGS
    # -----------------------------------------------------

    enable_audio: bool = True

    turn_sound_volume: float = 1.0

    turn_sound_velocity_threshold: float = 1.2

    turn_sound_cooldown: float = 0.24


# =========================================================
# TURN ACTION
# =========================================================

class TurnAction:
    """
    Production-grade smooth turning controller.

    Features:
    - smooth rotation
    - cinematic facing
    - procedural leaning
    - rotational damping
    - movement-aligned facing
    - procedural audio support
    """

    def __init__(
        self,
        body_rig: BodyRig,
        config: TurnActionConfig | None = None,
        with_sound: bool = True,
    ):
        self.body_rig = body_rig

        self.config = config or TurnActionConfig()

        self.with_sound = with_sound

        # -------------------------------------------------
        # INTERNAL STATE
        # -------------------------------------------------

        self.current_angle = 0.0

        self.target_angle = 0.0

        self.current_turn_velocity = 0.0

        self.turn_input = 0.0

        self.is_turning = False

        self.auto_rotate_enabled = True

        # -------------------------------------------------
        # BALANCE
        # -------------------------------------------------

        self.current_body_lean = 0.0

        self.current_hip_shift = 0.0

        # -------------------------------------------------
        # AUDIO STATE
        # -------------------------------------------------

        self.turn_sound_timer = 0.0

        self.turn_sound_triggered = False

    # =====================================================
    # TURN INPUT
    # =====================================================

    def turn_left(
        self,
        intensity: float = 1.0,
    ):
        """
        Begin left turn.
        """

        self.turn_input = abs(intensity)

        self.is_turning = True

    def turn_right(
        self,
        intensity: float = 1.0,
    ):
        """
        Begin right turn.
        """

        self.turn_input = -abs(intensity)

        self.is_turning = True

    def stop_turning(self):
        """
        Stop active turning.
        """

        self.turn_input = 0.0

        self.is_turning = False

    # =====================================================
    # TARGET ROTATION
    # =====================================================

    def set_target_angle(
        self,
        angle: float,
    ):
        """
        Explicitly set desired facing angle.
        """

        self.target_angle = angle

    def face_direction(
        self,
        direction,
    ):
        """
        Rotate creature toward vector direction.
        """

        direction = np.array(
            direction,
            dtype=float,
        )

        magnitude = np.linalg.norm(direction)

        if magnitude <= 1e-5:
            return

        direction /= magnitude

        target_angle = np.arctan2(
            direction[1],
            direction[0],
        )

        self.target_angle = target_angle

    # =====================================================
    # UPDATE
    # =====================================================

    def update(
        self,
        delta_time: float,
    ):
        """
        Advance procedural turning.
        """

        # -------------------------------------------------
        # AUDIO TIMER
        # -------------------------------------------------

        self.turn_sound_timer += delta_time

        # -------------------------------------------------
        # TURN INPUT
        # -------------------------------------------------

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

        # -------------------------------------------------
        # ROTATION SOLVE
        # -------------------------------------------------

        self.current_angle = (
            smooth_rotate_towards(
                self.current_angle,
                self.target_angle,
                self.config.turn_speed,
                delta_time,
            )
        )

        # -------------------------------------------------
        # APPLY ROTATION
        # -------------------------------------------------

        self.body_rig.rotate_to(
            self.current_angle
        )

        # -------------------------------------------------
        # BODY LEAN
        # -------------------------------------------------

        self._update_body_lean(
            delta_time
        )

        # -------------------------------------------------
        # HIP BALANCE
        # -------------------------------------------------

        self._update_hip_shift(
            delta_time
        )

        # -------------------------------------------------
        # FOOT ADJUSTMENT
        # -------------------------------------------------

        self._update_feet()

        # -------------------------------------------------
        # TURN AUDIO
        # -------------------------------------------------

        self._update_turn_audio()

    # =====================================================
    # BODY LEAN
    # =====================================================

    def _update_body_lean(
        self,
        delta_time: float,
    ):
        """
        Procedural turning lean.
        """

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

        self.body_rig.body.rotate(
            self.current_body_lean,
            about_point=self.body_rig.center_anchor,
        )

    # =====================================================
    # HIP SHIFT
    # =====================================================

    def _update_hip_shift(
        self,
        delta_time: float,
    ):
        """
        Procedural balance shifting.
        """

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

        self.body_rig.center_of_mass = vec3(
            self.current_hip_shift,
            0.0,
            0.0,
        )

    # =====================================================
    # FOOT ADJUSTMENT
    # =====================================================

    def _update_feet(self):
        """
        Subtle procedural foot rotation.
        """

        foot_adjustment = (
            self.current_turn_velocity
            * self.config.foot_adjustment_strength
        )

        self.body_rig.left_leg_rig.foot.set_rotation(
            foot_adjustment
        )

        self.body_rig.right_leg_rig.foot.set_rotation(
            -foot_adjustment
        )

    # =====================================================
    # AUDIO
    # =====================================================

    def _update_turn_audio(self):
        """
        Procedural turning sound timing.

        Goals:
        - soft directional sweep
        - educational mascot feel
        - subtle cinematic motion
        """

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

        maybe_play_sound(
            self.with_sound,
            play_turn_sound,
            volume=self.config.turn_sound_volume,
        )

        self.turn_sound_triggered = True

        self.turn_sound_timer = 0.0

    # =====================================================
    # AUTO FACE MOVEMENT
    # =====================================================

    def update_from_velocity(
        self,
        velocity,
    ):
        """
        Auto-orient toward movement direction.
        """

        if not self.auto_rotate_enabled:
            return

        velocity = np.array(
            velocity,
            dtype=float,
        )

        magnitude = np.linalg.norm(velocity)

        if magnitude <= 1e-5:
            return

        self.face_direction(
            velocity
        )

    # =====================================================
    # STATE
    # =====================================================

    def turning(self):
        return (
            abs(self.current_turn_velocity)
            > self.config.minimum_turn_threshold
        )

    def get_current_angle(self):
        return self.current_angle

    def get_target_angle(self):
        return self.target_angle

    def get_turn_velocity(self):
        return self.current_turn_velocity

    # =====================================================
    # AUDIO CONTROL
    # =====================================================

    def enable_sound(self):
        """
        Enable procedural turn audio.
        """

        self.with_sound = True

    def disable_sound(self):
        """
        Disable procedural turn audio.
        """

        self.with_sound = False

    # =====================================================
    # CONFIG
    # =====================================================

    def enable_auto_rotate(self):
        self.auto_rotate_enabled = True

    def disable_auto_rotate(self):
        self.auto_rotate_enabled = False

    # =====================================================
    # RESET
    # =====================================================

    def reset(self):
        """
        Reset turning state.
        """

        self.current_angle = 0.0

        self.target_angle = 0.0

        self.current_turn_velocity = 0.0

        self.turn_input = 0.0

        self.current_body_lean = 0.0

        self.current_hip_shift = 0.0

        self.turn_sound_timer = 0.0

        self.turn_sound_triggered = False

        self.is_turning = False

    # =====================================================
    # DEBUG
    # =====================================================

    def debug_print(self):
        print("========== TURN ACTION ==========")
        print("Current Angle:", self.current_angle)
        print("Target Angle:", self.target_angle)
        print("Turn Velocity:", self.current_turn_velocity)
        print("Turning:", self.is_turning)
        print("Sound Enabled:", self.with_sound)
        print("=================================")

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self):
        return (
            f"TurnAction("
            f"angle={round(self.current_angle, 3)}, "
            f"velocity={round(self.current_turn_velocity, 3)}"
            f")"
        )


# =========================================================
# FACTORY HELPERS
# =========================================================

def build_turn_action(
    body_rig: BodyRig,
    config: TurnActionConfig | None = None,
    with_sound: bool = True,
) -> TurnAction:
    """
    Create production-grade turn controller.
    """

    return TurnAction(
        body_rig=body_rig,
        config=config,
        with_sound=with_sound,
    )