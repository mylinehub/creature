# File: mathlab_creature/creature/actions/step_action.py

"""
mathlab_creature/creature/actions/step_action.py

Production-grade reusable procedural step system
with cinematic procedural audio integration.

Core Responsibilities
---------------------
- reusable single step
- procedural foot arc
- foot placement
- step timing
- weight shifting
- planted/lifted transitions
- cinematic stepping
- procedural audio timing
- soft educational footstep feel

Design Goals
------------
- reusable
- animation-safe
- procedural-ready
- future IK-ready
- future AI-ready
- cinematic-quality movement
- soft mascot movement
- educational motion rhythm

Audio Goals
-----------
- soft
- cartoony
- subtle
- expressive
- educational mascot feel
- not realistic heavy boots
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from mathlab_creature.core.transforms import (
    vec3,
)

from mathlab_creature.core.kinematics import (
    solve_leg_step_arc,
    smootherstep,
    clamp,
)

from mathlab_creature.core.logger import (
    get_logger,
)

from mathlab_creature.core.audio.helpers import (
    maybe_play_sound,
)

from mathlab_creature.core.audio.procedural import (
    play_walk_step,
)

from mathlab_creature.creature.rigs.leg_rig import (
    LegRig,
)

logger = get_logger(__name__)


# =========================================================
# CONFIG
# =========================================================

@dataclass
class StepActionConfig:
    """
    Tunable single-step settings.
    """

    step_height: float = 0.32

    step_duration: float = 0.45

    stride_length: float = 0.75

    foot_rotation_strength: float = 0.28

    body_shift_strength: float = 0.06

    foot_lift_threshold: float = 0.52

    easing_strength: float = 1.0

    # -----------------------------------------------------
    # AUDIO SETTINGS
    # -----------------------------------------------------

    enable_audio: bool = True

    step_sound_volume: float = 1.0

    step_sound_frequency: float = 110.0

    step_sound_trigger_phase: float = 0.56


# =========================================================
# STEP ACTION
# =========================================================

class StepAction:
    """
    Reusable procedural single-step controller.

    Features:
    - single foot step
    - procedural foot arc
    - cinematic timing
    - planted/lifted state
    - reusable movement primitive
    - procedural audio support

    Used by:
    - walk cycles
    - turning
    - balancing
    - procedural locomotion
    """

    def __init__(
        self,
        leg_rig: LegRig,
        config: StepActionConfig | None = None,
        with_sound: bool = True,
    ):
        self.leg_rig = leg_rig

        self.config = config or StepActionConfig()

        self.with_sound = with_sound

        # -------------------------------------------------
        # INTERNAL STATE
        # -------------------------------------------------

        self.elapsed_time = 0.0

        self.progress = 0.0

        self.is_active = False

        self.is_finished = False

        # -------------------------------------------------
        # STEP DATA
        # -------------------------------------------------

        self.start_position = vec3()

        self.target_position = vec3()

        self.current_position = vec3()

        self.walk_direction = vec3(
            0.0,
            1.0,
            0.0,
        )

        self.step_side = "left"

        self.foot_rotation = 0.0

        # -------------------------------------------------
        # AUDIO STATE
        # -------------------------------------------------

        self.step_sound_triggered = False

    # =====================================================
    # START
    # =====================================================

    def start(
        self,
        start_position,
        target_position,
        walk_direction,
    ):
        """
        Begin procedural step.
        """

        self.start_position = np.array(
            start_position,
            dtype=float,
        )

        self.target_position = np.array(
            target_position,
            dtype=float,
        )

        self.walk_direction = np.array(
            walk_direction,
            dtype=float,
        )

        magnitude = np.linalg.norm(
            self.walk_direction
        )

        if magnitude > 1e-5:
            self.walk_direction /= magnitude

        self.elapsed_time = 0.0

        self.progress = 0.0

        self.is_active = True

        self.is_finished = False

        self.step_sound_triggered = False

    # =====================================================
    # UPDATE
    # =====================================================

    def update(
        self,
        delta_time: float,
    ):
        """
        Advance procedural step.
        """

        if not self.is_active:
            return

        # -------------------------------------------------
        # TIME
        # -------------------------------------------------

        self.elapsed_time += delta_time

        raw_progress = (
            self.elapsed_time
            / self.config.step_duration
        )

        self.progress = clamp(
            raw_progress,
            0.0,
            1.0,
        )

        # -------------------------------------------------
        # EASING
        # -------------------------------------------------

        smooth_progress = smootherstep(
            self.progress
        )

        # -------------------------------------------------
        # FOOT ARC
        # -------------------------------------------------

        self.current_position = (
            solve_leg_step_arc(
                start=self.start_position,
                end=self.target_position,
                step_height=self.config.step_height,
                t=smooth_progress,
            )
        )

        # -------------------------------------------------
        # LEG IK
        # -------------------------------------------------

        self.leg_rig.solve_leg_ik(
            self.current_position
        )

        # -------------------------------------------------
        # FOOT STATE
        # -------------------------------------------------

        self._update_foot_state(
            smooth_progress
        )

        # -------------------------------------------------
        # FOOT ROTATION
        # -------------------------------------------------

        self._update_foot_rotation(
            smooth_progress
        )

        # -------------------------------------------------
        # BODY SHIFT
        # -------------------------------------------------

        self._update_body_shift(
            smooth_progress
        )

        # -------------------------------------------------
        # STEP AUDIO
        # -------------------------------------------------

        self._update_step_audio(
            smooth_progress
        )

        # -------------------------------------------------
        # FINISH
        # -------------------------------------------------

        if self.progress >= 1.0:
            self.finish()

    # =====================================================
    # FOOT STATE
    # =====================================================

    def _update_foot_state(
        self,
        progress: float,
    ):
        """
        Handle planted/lifted timing.
        """

        if (
            progress
            > self.config.foot_lift_threshold
        ):
            self.leg_rig.foot.set_lifted()

            self.leg_rig.ankle_joint.set_lifted()

        else:
            self.leg_rig.foot.set_planted()

            self.leg_rig.ankle_joint.set_planted()

    # =====================================================
    # FOOT ROTATION
    # =====================================================

    def _update_foot_rotation(
        self,
        progress: float,
    ):
        """
        Add cinematic foot articulation.
        """

        self.foot_rotation = (
            np.sin(progress * np.pi)
            * self.config.foot_rotation_strength
        )

        self.leg_rig.foot.set_rotation(
            self.foot_rotation
        )

        self.leg_rig.ankle_joint.set_ankle_angle(
            self.foot_rotation
        )

    # =====================================================
    # BODY SHIFT
    # =====================================================

    def _update_body_shift(
        self,
        progress: float,
    ):
        """
        Procedural balance shift.
        """

        shift = (
            np.sin(progress * np.pi)
            * self.config.body_shift_strength
        )

        self.leg_rig.hip_joint.shift_center_of_mass(
            vec3(
                shift,
                0.0,
                0.0,
            )
        )

    # =====================================================
    # STEP AUDIO
    # =====================================================

    def _update_step_audio(
        self,
        progress: float,
    ):
        """
        Procedural step sound timing.

        Goals:
        - soft mascot rhythm
        - educational feel
        - subtle cinematic support
        """

        if not self.with_sound:
            return

        if not self.config.enable_audio:
            return

        if self.step_sound_triggered:
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

    # =====================================================
    # FINISH
    # =====================================================

    def finish(self):
        """
        End procedural step.
        """

        self.is_active = False

        self.is_finished = True

        self.leg_rig.foot.set_planted()

        self.leg_rig.ankle_joint.set_planted()

    # =====================================================
    # INTERRUPT
    # =====================================================

    def cancel(self):
        """
        Abort current step.
        """

        self.is_active = False

        self.is_finished = True

    # =====================================================
    # AUDIO CONTROL
    # =====================================================

    def enable_sound(self):
        """
        Enable procedural step audio.
        """

        self.with_sound = True

    def disable_sound(self):
        """
        Disable procedural step audio.
        """

        self.with_sound = False

    # =====================================================
    # STATE
    # =====================================================

    def active(self):
        return self.is_active

    def finished(self):
        return self.is_finished

    def get_progress(self):
        return self.progress

    def get_current_position(self):
        return np.array(
            self.current_position
        )

    # =====================================================
    # RESET
    # =====================================================

    def reset(self):
        """
        Reset internal state.
        """

        self.elapsed_time = 0.0

        self.progress = 0.0

        self.is_active = False

        self.is_finished = False

        self.current_position = vec3()

        self.step_sound_triggered = False

    # =====================================================
    # DEBUG
    # =====================================================

    def debug_print(self):
        print("========== STEP ACTION ==========")
        print("Progress:", self.progress)
        print("Elapsed:", self.elapsed_time)
        print("Active:", self.is_active)
        print("Finished:", self.is_finished)
        print("Current Position:", self.current_position)
        print("Sound Enabled:", self.with_sound)
        print("=================================")

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self):
        return (
            f"StepAction("
            f"progress={round(self.progress, 3)}, "
            f"active={self.is_active}"
            f")"
        )


# =========================================================
# FACTORY HELPERS
# =========================================================

def build_step_action(
    leg_rig: LegRig,
    config: StepActionConfig | None = None,
    with_sound: bool = True,
) -> StepAction:
    """
    Create production-grade procedural step.
    """

    return StepAction(
        leg_rig=leg_rig,
        config=config,
        with_sound=with_sound,
    )