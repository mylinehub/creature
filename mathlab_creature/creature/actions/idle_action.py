"""
Idle action for mathlab-mylinehub-creature.

This file controls idle/living-state metadata for one connected creature.

Architecture rule:
- idle_action.py does not build creature parts
- idle_action.py does not move eyes, hands, feet, or legs directly
- idle_action.py works through BodyRig, FaceRig, ArmRig, and LegRig
- idle_action.py keeps one-creature hierarchy intact
- audio is optional and safely ignored if audio modules are unavailable
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from mathlab_creature.core.geometry import point
from mathlab_creature.core.geometry import zero_vector
from mathlab_creature.core.kinematics import damp
from mathlab_creature.core.kinematics import damp_vector
from mathlab_creature.core.logger import get_logger
from mathlab_creature.creature.rigs.body_rig import BodyRig


logger = get_logger(__name__)


try:
    from mathlab_creature.core.audio.helpers import maybe_play_sound
    from mathlab_creature.core.audio.procedural import play_look_sound
except Exception:
    maybe_play_sound = None
    play_look_sound = None


@dataclass
class IdleActionConfig:
    breathing_speed: float = 1.1
    breathing_strength: float = 0.045

    sway_speed: float = 0.7
    sway_strength: float = 0.035

    head_tilt_strength: float = 0.02
    head_drift_strength: float = 0.03

    balance_shift_strength: float = 0.025
    stabilization_speed: float = 8.0

    micro_motion_strength: float = 0.012
    micro_motion_speed: float = 2.8

    foot_settle_strength: float = 0.01

    enable_audio: bool = True
    idle_sound_interval: float = 5.5
    idle_sound_volume: float = 0.12


class IdleAction:
    """
    Procedural idle controller.

    It stores and updates idle state on BodyRig.
    It avoids direct repeated shift/scale/rotate on child parts.
    """

    def __init__(
        self,
        body_rig: BodyRig,
        config: IdleActionConfig | None = None,
        with_sound: bool = True,
    ) -> None:
        if not isinstance(body_rig, BodyRig):
            raise TypeError(
                f"body_rig must be BodyRig, got {type(body_rig).__name__}"
            )

        self.body_rig = body_rig
        self.config = config or IdleActionConfig()
        self.with_sound = bool(with_sound)

        self.elapsed_time = 0.0
        self.is_active = True

        self.breath_cycle = 0.0
        self.current_breath_offset = 0.0
        self.current_sway = 0.0

        self.current_head_tilt = 0.0
        self.current_head_drift = zero_vector()

        self.current_balance_shift = zero_vector()
        self.micro_noise = zero_vector()

        self.left_foot_settle = 0.0
        self.right_foot_settle = 0.0

        self.idle_sound_timer = 0.0

    def update(
        self,
        delta_time: float,
    ) -> None:
        """
        Advance idle state.
        """
        if not self.is_active:
            return

        delta_time = float(delta_time)

        if delta_time <= 0:
            return

        self.elapsed_time += delta_time
        self.idle_sound_timer += delta_time

        self._update_breathing(delta_time)
        self._update_sway(delta_time)
        self._update_head_motion(delta_time)
        self._update_balance(delta_time)
        self._update_micro_motion(delta_time)
        self._update_feet(delta_time)
        self._update_body_rig_state()
        self._update_idle_audio()

    def _update_breathing(
        self,
        delta_time: float,
    ) -> None:
        self.breath_cycle += delta_time * self.config.breathing_speed

        target = (
            np.sin(self.breath_cycle)
            * self.config.breathing_strength
        )

        self.current_breath_offset = damp(
            self.current_breath_offset,
            target,
            8.0,
            delta_time,
        )

    def _update_sway(
        self,
        delta_time: float,
    ) -> None:
        target = (
            np.sin(self.elapsed_time * self.config.sway_speed)
            * self.config.sway_strength
        )

        self.current_sway = damp(
            self.current_sway,
            target,
            6.0,
            delta_time,
        )

    def _update_head_motion(
        self,
        delta_time: float,
    ) -> None:
        tilt_target = (
            np.sin(self.elapsed_time * 0.8)
            * self.config.head_tilt_strength
        )

        self.current_head_tilt = damp(
            self.current_head_tilt,
            tilt_target,
            5.0,
            delta_time,
        )

        drift_target = point(
            np.sin(self.elapsed_time * 0.4)
            * self.config.head_drift_strength,
            np.cos(self.elapsed_time * 0.5)
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

    def _update_balance(
        self,
        delta_time: float,
    ) -> None:
        target = point(
            np.sin(self.elapsed_time * 0.6)
            * self.config.balance_shift_strength,
            0.0,
            0.0,
        )

        self.current_balance_shift = damp_vector(
            self.current_balance_shift,
            target,
            self.config.stabilization_speed,
            delta_time,
        )

    def _update_micro_motion(
        self,
        delta_time: float,
    ) -> None:
        target = point(
            np.sin(self.elapsed_time * self.config.micro_motion_speed)
            * self.config.micro_motion_strength,
            np.cos(
                self.elapsed_time
                * self.config.micro_motion_speed
                * 1.37
            )
            * self.config.micro_motion_strength,
            0.0,
        )

        self.micro_noise = damp_vector(
            self.micro_noise,
            target,
            8.0,
            delta_time,
        )

    def _update_feet(
        self,
        delta_time: float,
    ) -> None:
        settle = (
            np.sin(self.elapsed_time * 1.8)
            * self.config.foot_settle_strength
        )

        self.left_foot_settle = settle
        self.right_foot_settle = -settle

        leg_rig = self.body_rig.get_leg_rig()

        if leg_rig is None:
            return

        left_foot = leg_rig.get_left_foot()
        right_foot = leg_rig.get_right_foot()

        if left_foot is not None:
            left_foot.set_rotation(self.left_foot_settle)

        if right_foot is not None:
            right_foot.set_rotation(self.right_foot_settle)

    def _update_body_rig_state(
        self,
    ) -> None:
        """
        Store idle values on BodyRig.

        No direct repeated child shift/scale is applied here.
        """
        idle_offset = (
            point(
                self.current_sway,
                self.current_breath_offset,
                0.0,
            )
            + self.micro_noise
        )

        self.body_rig.balance_offset = idle_offset
        self.body_rig.center_of_mass = self.current_balance_shift

        self.body_rig.body_bounce = self.current_breath_offset
        self.body_rig.body_sway = self.current_sway
        self.body_rig.body_tilt = self.current_head_tilt

        self.body_rig.idle_offset = idle_offset
        self.body_rig.idle_head_drift = self.current_head_drift
        self.body_rig.idle_head_tilt = self.current_head_tilt

    def _update_idle_audio(
        self,
    ) -> None:
        if not self.with_sound:
            return

        if not self.config.enable_audio:
            return

        if self.idle_sound_timer < self.config.idle_sound_interval:
            return

        if maybe_play_sound is None or play_look_sound is None:
            return

        maybe_play_sound(
            self.with_sound,
            play_look_sound,
            volume=self.config.idle_sound_volume,
        )

        self.idle_sound_timer = 0.0

    def start(self) -> None:
        self.is_active = True

    def stop(self) -> None:
        self.is_active = False

    def toggle(self) -> None:
        self.is_active = not self.is_active

    def enable_sound(self) -> None:
        self.with_sound = True

    def disable_sound(self) -> None:
        self.with_sound = False

    def active(self) -> bool:
        return bool(self.is_active)

    def get_breath_cycle(self) -> float:
        return float(self.breath_cycle)

    def get_elapsed_time(self) -> float:
        return float(self.elapsed_time)

    def reset(self) -> None:
        self.elapsed_time = 0.0
        self.breath_cycle = 0.0

        self.current_breath_offset = 0.0
        self.current_sway = 0.0

        self.current_head_tilt = 0.0
        self.current_head_drift = zero_vector()

        self.current_balance_shift = zero_vector()
        self.micro_noise = zero_vector()

        self.left_foot_settle = 0.0
        self.right_foot_settle = 0.0

        self.idle_sound_timer = 0.0

        self._update_body_rig_state()

    def debug_print(self) -> None:
        print("========== IDLE ACTION ==========")
        print("Elapsed Time:", self.elapsed_time)
        print("Breath Offset:", self.current_breath_offset)
        print("Current Sway:", self.current_sway)
        print("Head Tilt:", self.current_head_tilt)
        print("Sound Enabled:", self.with_sound)
        print("=================================")

    def __repr__(self) -> str:
        return (
            "IdleAction("
            f"active={self.is_active}, "
            f"time={round(self.elapsed_time, 3)}"
            ")"
        )


def build_idle_action(
    body_rig: BodyRig,
    config: IdleActionConfig | None = None,
    with_sound: bool = True,
) -> IdleAction:
    """
    Create idle action for BodyRig.
    """
    return IdleAction(
        body_rig=body_rig,
        config=config,
        with_sound=with_sound,
    )


__all__ = [
    "IdleActionConfig",
    "IdleAction",
    "build_idle_action",
]