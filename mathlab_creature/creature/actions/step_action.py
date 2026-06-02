"""
Step action for mathlab-mylinehub-creature.

This file controls a single procedural step.

Architecture rule:
- step_action.py does not build legs
- step_action.py does not create joints
- step_action.py works through LegRig
- LegRig controls connected leg systems
- audio is optional and safely ignored if audio modules are unavailable

Connection chain:

    StepAction
        |
        LegRig
            |
            Left Leg / Right Leg
                |
                Knee
                Ankle
                Foot
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from mathlab_creature.core.geometry import as_vec3
from mathlab_creature.core.geometry import zero_vector
from mathlab_creature.core.kinematics import clamp
from mathlab_creature.core.kinematics import smootherstep
from mathlab_creature.core.logger import get_logger
from mathlab_creature.creature.rigs.leg_rig import LegRig


logger = get_logger(__name__)


try:
    from mathlab_creature.core.audio.helpers import maybe_play_sound
    from mathlab_creature.core.audio.procedural import play_walk_step
except Exception:
    maybe_play_sound = None
    play_walk_step = None


@dataclass
class StepActionConfig:
    step_height: float = 0.32
    step_duration: float = 0.45

    stride_length: float = 0.75

    foot_rotation_strength: float = 0.28
    body_shift_strength: float = 0.06

    foot_lift_threshold: float = 0.52
    easing_strength: float = 1.0

    enable_audio: bool = True
    step_sound_volume: float = 1.0
    step_sound_frequency: float = 110.0
    step_sound_trigger_phase: float = 0.56


class StepAction:
    """
    Single reusable procedural step.

    Used by:
    - WalkAction
    - TurnAction
    - HopAction
    - Balance recovery
    """

    def __init__(
        self,
        leg_rig: LegRig,
        config: StepActionConfig | None = None,
        with_sound: bool = True,
    ) -> None:
        if not isinstance(leg_rig, LegRig):
            raise TypeError(
                f"leg_rig must be LegRig, got {type(leg_rig).__name__}"
            )

        self.leg_rig = leg_rig
        self.config = config or StepActionConfig()
        self.with_sound = bool(with_sound)

        self.elapsed_time = 0.0
        self.progress = 0.0

        self.is_active = False
        self.is_finished = False

        self.start_position = zero_vector()
        self.target_position = zero_vector()
        self.current_position = zero_vector()

        self.walk_direction = zero_vector()
        self.walk_direction[1] = 1.0

        self.step_side = "left"

        self.foot_rotation = 0.0
        self.step_sound_triggered = False

    def start(
        self,
        start_position,
        target_position,
        walk_direction,
        *,
        side: str = "left",
    ) -> None:
        self.start_position = as_vec3(
            start_position,
            name="start_position",
        )

        self.target_position = as_vec3(
            target_position,
            name="target_position",
        )

        self.walk_direction = as_vec3(
            walk_direction,
            name="walk_direction",
        )

        magnitude = np.linalg.norm(
            self.walk_direction,
        )

        if magnitude > 1e-8:
            self.walk_direction = (
                self.walk_direction / magnitude
            )

        self.step_side = (
            str(side)
            .strip()
            .lower()
        )

        self.elapsed_time = 0.0
        self.progress = 0.0

        self.is_active = True
        self.is_finished = False

        self.step_sound_triggered = False

    def update(
        self,
        delta_time: float,
    ) -> None:
        if not self.is_active:
            return

        self.elapsed_time += float(delta_time)

        raw_progress = (
            self.elapsed_time
            / self.config.step_duration
        )

        self.progress = clamp(
            raw_progress,
            0.0,
            1.0,
        )

        smooth_progress = smootherstep(
            self.progress,
        )

        self.current_position = (
            self.start_position
            + (
                self.target_position
                - self.start_position
            )
            * smooth_progress
        )

        self._update_leg_state(
            smooth_progress,
        )

        self._update_audio(
            smooth_progress,
        )

        if self.progress >= 1.0:
            self.finish()

    def _update_leg_state(
        self,
        progress: float,
    ) -> None:
        """
        Update LegRig state.

        LegRig owns:
        - knee state
        - ankle state
        - foot state
        """

        phase = clamp(
            progress,
            0.0,
            1.0,
        )

        if phase > self.config.foot_lift_threshold:
            self.leg_rig.set_feet_lifted()
        else:
            self.leg_rig.set_feet_planted()

    def _update_audio(
        self,
        progress: float,
    ) -> None:
        if not self.with_sound:
            return

        if not self.config.enable_audio:
            return

        if self.step_sound_triggered:
            return

        if maybe_play_sound is None:
            return

        if play_walk_step is None:
            return

        if (
            progress
            < self.config.step_sound_trigger_phase
        ):
            return

        maybe_play_sound(
            self.with_sound,
            play_walk_step,
            frequency=self.config.step_sound_frequency,
            volume=self.config.step_sound_volume,
        )

        self.step_sound_triggered = True

    def finish(
        self,
    ) -> None:
        self.is_active = False
        self.is_finished = True

        self.leg_rig.set_feet_planted()

    def cancel(
        self,
    ) -> None:
        self.is_active = False
        self.is_finished = True

        self.leg_rig.set_feet_planted()

    def enable_sound(
        self,
    ) -> None:
        self.with_sound = True

    def disable_sound(
        self,
    ) -> None:
        self.with_sound = False

    def active(
        self,
    ) -> bool:
        return bool(
            self.is_active,
        )

    def finished(
        self,
    ) -> bool:
        return bool(
            self.is_finished,
        )

    def get_progress(
        self,
    ) -> float:
        return float(
            self.progress,
        )

    def get_current_position(
        self,
    ):
        return np.array(
            self.current_position,
            dtype=float,
        )

    def reset(
        self,
    ) -> None:
        self.elapsed_time = 0.0
        self.progress = 0.0

        self.is_active = False
        self.is_finished = False

        self.current_position = zero_vector()

        self.step_sound_triggered = False

    def debug_print(
        self,
    ) -> None:
        print("========== STEP ACTION ==========")
        print("Progress:", self.progress)
        print("Elapsed:", self.elapsed_time)
        print("Active:", self.is_active)
        print("Finished:", self.is_finished)
        print("Current Position:", self.current_position)
        print("Step Side:", self.step_side)
        print("Sound Enabled:", self.with_sound)
        print("=================================")

    def __repr__(
        self,
    ) -> str:
        return (
            "StepAction("
            f"progress={round(self.progress, 3)}, "
            f"active={self.is_active}"
            ")"
        )


def build_step_action(
    leg_rig: LegRig,
    config: StepActionConfig | None = None,
    with_sound: bool = True,
) -> StepAction:
    return StepAction(
        leg_rig=leg_rig,
        config=config,
        with_sound=with_sound,
    )


__all__ = [
    "StepActionConfig",
    "StepAction",
    "build_step_action",
]