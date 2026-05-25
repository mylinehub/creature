# File: mathlab_creature/creature/actions/idle_action.py

"""
mathlab_creature/creature/actions/idle_action.py

Production-grade procedural idle animation system
with cinematic procedural audio integration.

Core Responsibilities
---------------------
- breathing
- idle sway
- alive feeling
- micro motion
- balance stabilization
- subtle procedural movement
- cinematic resting motion
- ambient procedural audio
- living mascot presence

Design Goals
------------
- production-ready
- cinematic quality
- subtle realism
- non-robotic movement
- future AI-ready
- future emotion-ready
- procedural-animation-ready
- educational mascot feel

Audio Goals
-----------
- extremely subtle
- airy ambient motion
- alive but not annoying
- soft breathing feel
- gentle living presence
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from mathlab_creature.core.transforms import (
    vec3,
)

from mathlab_creature.core.kinematics import (
    damp,
    damp_vector,
    clamp,
)

from mathlab_creature.core.logger import (
    get_logger,
)

from mathlab_creature.core.audio.helpers import (
    maybe_play_sound,
)

from mathlab_creature.core.audio.procedural import (
    play_look_sound,
)

from mathlab_creature.creature.rigs.body_rig import (
    BodyRig,
)

logger = get_logger(__name__)


# =========================================================
# CONFIG
# =========================================================

@dataclass
class IdleActionConfig:
    """
    Tunable idle animation settings.
    """

    # -----------------------------------------------------
    # BREATHING
    # -----------------------------------------------------

    breathing_speed: float = 1.1

    breathing_strength: float = 0.045

    chest_expansion_strength: float = 0.018

    # -----------------------------------------------------
    # SWAY
    # -----------------------------------------------------

    sway_speed: float = 0.7

    sway_strength: float = 0.035

    # -----------------------------------------------------
    # HEAD MOTION
    # -----------------------------------------------------

    head_tilt_strength: float = 0.02

    head_drift_strength: float = 0.03

    # -----------------------------------------------------
    # BALANCE
    # -----------------------------------------------------

    balance_shift_strength: float = 0.025

    stabilization_speed: float = 8.0

    # -----------------------------------------------------
    # MICRO MOTION
    # -----------------------------------------------------

    micro_motion_strength: float = 0.012

    micro_motion_speed: float = 2.8

    # -----------------------------------------------------
    # FOOT ADJUSTMENT
    # -----------------------------------------------------

    foot_settle_strength: float = 0.01

    # -----------------------------------------------------
    # GENERAL
    # -----------------------------------------------------

    movement_damping: float = 0.92

    # -----------------------------------------------------
    # AUDIO SETTINGS
    # -----------------------------------------------------

    enable_audio: bool = True

    idle_sound_interval: float = 5.5

    idle_sound_volume: float = 0.12


# =========================================================
# IDLE ACTION
# =========================================================

class IdleAction:
    """
    Production-grade procedural idle system.

    Features:
    - breathing
    - subtle balance shifts
    - body sway
    - micro movement
    - living presence
    - cinematic idle behavior
    - ambient procedural audio
    """

    def __init__(
        self,
        body_rig: BodyRig,
        config: IdleActionConfig | None = None,
        with_sound: bool = True,
    ):
        self.body_rig = body_rig

        self.config = config or IdleActionConfig()

        self.with_sound = with_sound

        # -------------------------------------------------
        # INTERNAL STATE
        # -------------------------------------------------

        self.elapsed_time = 0.0

        self.is_active = True

        # -------------------------------------------------
        # BREATHING
        # -------------------------------------------------

        self.breath_cycle = 0.0

        self.current_breath_offset = 0.0

        # -------------------------------------------------
        # SWAY
        # -------------------------------------------------

        self.current_sway = 0.0

        # -------------------------------------------------
        # HEAD MOTION
        # -------------------------------------------------

        self.current_head_tilt = 0.0

        self.current_head_drift = vec3()

        # -------------------------------------------------
        # BALANCE
        # -------------------------------------------------

        self.current_balance_shift = vec3()

        # -------------------------------------------------
        # MICRO MOTION
        # -------------------------------------------------

        self.micro_noise = vec3()

        # -------------------------------------------------
        # AUDIO
        # -------------------------------------------------

        self.idle_sound_timer = 0.0

    # =====================================================
    # UPDATE
    # =====================================================

    def update(
        self,
        delta_time: float,
    ):
        """
        Advance procedural idle animation.
        """

        if not self.is_active:
            return

        # -------------------------------------------------
        # TIME
        # -------------------------------------------------

        self.elapsed_time += delta_time

        self.idle_sound_timer += delta_time

        # -------------------------------------------------
        # BREATHING
        # -------------------------------------------------

        self._update_breathing(
            delta_time
        )

        # -------------------------------------------------
        # SWAY
        # -------------------------------------------------

        self._update_sway(
            delta_time
        )

        # -------------------------------------------------
        # HEAD MOTION
        # -------------------------------------------------

        self._update_head_motion(
            delta_time
        )

        # -------------------------------------------------
        # BALANCE
        # -------------------------------------------------

        self._update_balance(
            delta_time
        )

        # -------------------------------------------------
        # MICRO MOTION
        # -------------------------------------------------

        self._update_micro_motion(
            delta_time
        )

        # -------------------------------------------------
        # FOOT SETTLING
        # -------------------------------------------------

        self._update_feet(
            delta_time
        )

        # -------------------------------------------------
        # IDLE AUDIO
        # -------------------------------------------------

        self._update_idle_audio()

    # =====================================================
    # BREATHING
    # =====================================================

    def _update_breathing(
        self,
        delta_time: float,
    ):
        """
        Procedural breathing motion.
        """

        self.breath_cycle += (
            delta_time
            * self.config.breathing_speed
        )

        breath = (
            np.sin(self.breath_cycle)
            * self.config.breathing_strength
        )

        self.current_breath_offset = damp(
            self.current_breath_offset,
            breath,
            8.0,
            delta_time,
        )

        # -------------------------------------------------
        # BODY MOTION
        # -------------------------------------------------

        self.body_rig.body.shift(
            vec3(
                0.0,
                self.current_breath_offset,
                0.0,
            )
        )

        # -------------------------------------------------
        # CHEST EXPANSION
        # -------------------------------------------------

        chest_scale = (
            1.0
            + abs(
                breath
                * self.config.chest_expansion_strength
            )
        )

        self.body_rig.body.scale(
            chest_scale
        )

    # =====================================================
    # SWAY
    # =====================================================

    def _update_sway(
        self,
        delta_time: float,
    ):
        """
        Subtle body sway.
        """

        sway_target = (
            np.sin(
                self.elapsed_time
                * self.config.sway_speed
            )
            * self.config.sway_strength
        )

        self.current_sway = damp(
            self.current_sway,
            sway_target,
            6.0,
            delta_time,
        )

        self.body_rig.body.shift(
            vec3(
                self.current_sway,
                0.0,
                0.0,
            )
        )

    # =====================================================
    # HEAD MOTION
    # =====================================================

    def _update_head_motion(
        self,
        delta_time: float,
    ):
        """
        Living head motion.
        """

        # -------------------------------------------------
        # TILT
        # -------------------------------------------------

        tilt_target = (
            np.sin(
                self.elapsed_time * 0.8
            )
            * self.config.head_tilt_strength
        )

        self.current_head_tilt = damp(
            self.current_head_tilt,
            tilt_target,
            5.0,
            delta_time,
        )

        # -------------------------------------------------
        # DRIFT
        # -------------------------------------------------

        drift_target = vec3(
            np.sin(
                self.elapsed_time * 0.4
            )
            * self.config.head_drift_strength,
            np.cos(
                self.elapsed_time * 0.5
            )
            * self.config.head_drift_strength
            * 0.5,
            0.0,
        )

        self.current_head_drift = damp_vector(
            self.current_head_drift,
            drift_target,
            4.0,
            delta_time,
        )

        # -------------------------------------------------
        # APPLY
        # -------------------------------------------------

        self.body_rig.face_rig.shift(
            self.current_head_drift
        )

        self.body_rig.face_rig.rotate(
            self.current_head_tilt,
            about_point=self.body_rig.center_anchor,
        )

    # =====================================================
    # BALANCE
    # =====================================================

    def _update_balance(
        self,
        delta_time: float,
    ):
        """
        Procedural balance stabilization.
        """

        balance_target = vec3(
            np.sin(
                self.elapsed_time * 0.6
            )
            * self.config.balance_shift_strength,
            0.0,
            0.0,
        )

        self.current_balance_shift = damp_vector(
            self.current_balance_shift,
            balance_target,
            self.config.stabilization_speed,
            delta_time,
        )

        self.body_rig.center_of_mass = (
            self.current_balance_shift
        )

    # =====================================================
    # MICRO MOTION
    # =====================================================

    def _update_micro_motion(
        self,
        delta_time: float,
    ):
        """
        Tiny non-repeating life-like motion.
        """

        noise = vec3(
            np.sin(
                self.elapsed_time
                * self.config.micro_motion_speed
            )
            * self.config.micro_motion_strength,
            np.cos(
                self.elapsed_time
                * (
                    self.config.micro_motion_speed
                    * 1.37
                )
            )
            * self.config.micro_motion_strength,
            0.0,
        )

        self.micro_noise = damp_vector(
            self.micro_noise,
            noise,
            8.0,
            delta_time,
        )

        self.body_rig.body.shift(
            self.micro_noise
        )

    # =====================================================
    # FOOT SETTLING
    # =====================================================

    def _update_feet(
        self,
        delta_time: float,
    ):
        """
        Tiny foot settling movement.
        """

        settle = (
            np.sin(
                self.elapsed_time * 1.8
            )
            * self.config.foot_settle_strength
        )

        self.body_rig.left_leg_rig.foot.set_rotation(
            settle
        )

        self.body_rig.right_leg_rig.foot.set_rotation(
            -settle
        )

    # =====================================================
    # AUDIO
    # =====================================================

    def _update_idle_audio(self):
        """
        Extremely subtle ambient life sound.

        Goals:
        - barely noticeable
        - soft living presence
        - educational mascot feel
        """

        if not self.with_sound:
            return

        if not self.config.enable_audio:
            return

        if (
            self.idle_sound_timer
            < self.config.idle_sound_interval
        ):
            return

        maybe_play_sound(
            self.with_sound,
            play_look_sound,
            volume=self.config.idle_sound_volume,
        )

        self.idle_sound_timer = 0.0

    # =====================================================
    # CONTROL
    # =====================================================

    def start(self):
        self.is_active = True

    def stop(self):
        self.is_active = False

    def toggle(self):
        self.is_active = not self.is_active

    # =====================================================
    # AUDIO CONTROL
    # =====================================================

    def enable_sound(self):
        """
        Enable idle audio.
        """

        self.with_sound = True

    def disable_sound(self):
        """
        Disable idle audio.
        """

        self.with_sound = False

    # =====================================================
    # STATE
    # =====================================================

    def active(self):
        return self.is_active

    def get_breath_cycle(self):
        return self.breath_cycle

    def get_elapsed_time(self):
        return self.elapsed_time

    # =====================================================
    # RESET
    # =====================================================

    def reset(self):
        """
        Reset idle animation state.
        """

        self.elapsed_time = 0.0

        self.breath_cycle = 0.0

        self.current_breath_offset = 0.0

        self.current_sway = 0.0

        self.current_head_tilt = 0.0

        self.current_head_drift = vec3()

        self.current_balance_shift = vec3()

        self.micro_noise = vec3()

        self.idle_sound_timer = 0.0

    # =====================================================
    # DEBUG
    # =====================================================

    def debug_print(self):
        print("========== IDLE ACTION ==========")
        print("Elapsed Time:", self.elapsed_time)
        print("Breath Offset:", self.current_breath_offset)
        print("Current Sway:", self.current_sway)
        print("Head Tilt:", self.current_head_tilt)
        print("Sound Enabled:", self.with_sound)
        print("=================================")

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self):
        return (
            f"IdleAction("
            f"active={self.is_active}, "
            f"time={round(self.elapsed_time, 3)}"
            f")"
        )


# =========================================================
# FACTORY HELPERS
# =========================================================

def build_idle_action(
    body_rig: BodyRig,
    config: IdleActionConfig | None = None,
    with_sound: bool = True,
) -> IdleAction:
    """
    Create production-grade idle animation.
    """

    return IdleAction(
        body_rig=body_rig,
        config=config,
        with_sound=with_sound,
    )