# File: mathlab_creature/creature/actions/walk_action.py

"""
mathlab_creature/creature/actions/walk_action.py

Production-grade procedural walk system
with cinematic procedural audio integration.

Core Responsibilities
---------------------
- real gait cycle
- stride timing
- body bounce
- foot timing
- realistic walking
- procedural locomotion
- movement blending
- synchronized stepping
- procedural audio timing
- alternating left/right stepping feel

Design Goals
------------
- production-ready
- cinematic movement
- realistic weight
- smooth timing
- future AI-ready
- future IK-ready
- future 3D-ready
- soft mascot movement
- educational motion rhythm
- subtle procedural sound

Audio Goals
-----------
- soft
- cartoony
- educational mascot style
- not heavy realistic boots
- alive but not annoying
- subtle and expressive
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from manimlib import AnimationGroup

from mathlab_creature.core.transforms import (
    vec3,
)

from mathlab_creature.core.kinematics import (
    clamp,
    ease_in_out,
    smootherstep,
    solve_body_bounce,
    solve_body_sway,
    solve_leg_step_arc,
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

from mathlab_creature.creature.rigs.body_rig import (
    BodyRig,
)

logger = get_logger(__name__)


# =========================================================
# CONFIG
# =========================================================

@dataclass
class WalkActionConfig:
    """
    Tunable procedural gait settings.
    """

    stride_length: float = 0.75

    step_height: float = 0.3

    walk_speed: float = 1.0

    gait_frequency: float = 2.0

    body_bounce_strength: float = 0.08

    body_sway_strength: float = 0.05

    body_tilt_strength: float = 0.12

    foot_lift_threshold: float = 0.52

    arm_swing_strength: float = 0.35

    step_smoothing: float = 0.85

    movement_damping: float = 0.92

    foot_rotation_strength: float = 0.28

    root_motion_strength: float = 1.0

    # -----------------------------------------------------
    # AUDIO SETTINGS
    # -----------------------------------------------------

    enable_audio: bool = True

    footstep_volume: float = 1.0

    footstep_cooldown: float = 0.22

    left_step_pitch_offset: float = -6.0

    right_step_pitch_offset: float = 6.0


# =========================================================
# WALK ACTION
# =========================================================

class WalkAction:
    """
    Production-grade procedural walk controller.

    Features:
    - procedural gait
    - synchronized stepping
    - body balance
    - foot timing
    - cinematic movement
    - procedural audio support
    """

    def __init__(
        self,
        body_rig: BodyRig,
        config: WalkActionConfig | None = None,
        with_sound: bool = True,
    ):
        self.body_rig = body_rig

        self.config = config or WalkActionConfig()

        self.with_sound = with_sound

        # -------------------------------------------------
        # INTERNAL STATE
        # -------------------------------------------------

        self.walk_cycle = 0.0

        self.walk_direction = vec3(0.0, 1.0, 0.0)

        self.current_speed = 0.0

        self.target_speed = 0.0

        self.is_active = False

        self.left_phase = 0.0
        self.right_phase = 0.5

        # -------------------------------------------------
        # FOOT STATES
        # -------------------------------------------------

        self.left_foot_planted = True
        self.right_foot_planted = True

        # -------------------------------------------------
        # AUDIO STATE
        # -------------------------------------------------

        self.left_step_triggered = False
        self.right_step_triggered = False

        self.footstep_timer = 0.0

    # =====================================================
    # START / STOP
    # =====================================================

    def start(
        self,
        direction,
        speed: float = 1.0,
    ):
        """
        Activate procedural walking.
        """

        direction = np.array(
            direction,
            dtype=float,
        )

        magnitude = np.linalg.norm(direction)

        if magnitude <= 1e-5:
            return

        direction /= magnitude

        self.walk_direction = direction

        self.target_speed = speed

        self.is_active = True

    def stop(self):
        """
        Gracefully stop walking.
        """

        self.target_speed = 0.0

        self.is_active = False

    # =====================================================
    # UPDATE
    # =====================================================

    def update(
        self,
        delta_time: float,
    ):
        """
        Main procedural walk update.
        """

        # -------------------------------------------------
        # SPEED BLENDING
        # -------------------------------------------------

        self.current_speed += (
            self.target_speed
            - self.current_speed
        ) * (
            1.0 - self.config.movement_damping
        )

        if self.current_speed <= 1e-4:
            return

        # -------------------------------------------------
        # FOOTSTEP TIMER
        # -------------------------------------------------

        self.footstep_timer += delta_time

        # -------------------------------------------------
        # GAIT CYCLE
        # -------------------------------------------------

        self.walk_cycle += (
            delta_time
            * self.config.gait_frequency
            * self.current_speed
        )

        # -------------------------------------------------
        # STEP PHASES
        # -------------------------------------------------

        self.left_phase = (
            np.sin(
                self.walk_cycle * np.pi
            )
            * 0.5
            + 0.5
        )

        self.right_phase = (
            np.sin(
                (self.walk_cycle + 1.0)
                * np.pi
            )
            * 0.5
            + 0.5
        )

        # -------------------------------------------------
        # BODY MOTION
        # -------------------------------------------------

        self._update_body_motion()

        # -------------------------------------------------
        # FOOT SOLVING
        # -------------------------------------------------

        self._update_left_leg()

        self._update_right_leg()

        # -------------------------------------------------
        # AUDIO
        # -------------------------------------------------

        self._update_footstep_audio()

        # -------------------------------------------------
        # ROOT MOTION
        # -------------------------------------------------

        self._apply_root_motion(
            delta_time
        )

    # =====================================================
    # BODY MOTION
    # =====================================================

    def _update_body_motion(self):
        """
        Procedural body movement.
        """

        bounce = solve_body_bounce(
            self.walk_cycle,
            self.config.body_bounce_strength,
        )

        sway = solve_body_sway(
            self.walk_cycle,
            self.config.body_sway_strength,
        )

        tilt = (
            self.walk_direction[0]
            * self.config.body_tilt_strength
        )

        self.body_rig.body.shift(
            vec3(
                sway,
                bounce,
                0.0,
            )
        )

        self.body_rig.body.rotate(
            tilt,
            about_point=vec3(),
        )

    # =====================================================
    # LEFT LEG
    # =====================================================

    def _update_left_leg(self):
        """
        Solve left procedural step.
        """

        self._solve_leg(
            leg_rig=self.body_rig.left_leg_rig,
            phase=self.left_phase,
            side_multiplier=-1.0,
        )

    # =====================================================
    # RIGHT LEG
    # =====================================================

    def _update_right_leg(self):
        """
        Solve right procedural step.
        """

        self._solve_leg(
            leg_rig=self.body_rig.right_leg_rig,
            phase=self.right_phase,
            side_multiplier=1.0,
        )

    # =====================================================
    # LEG SOLVER
    # =====================================================

    def _solve_leg(
        self,
        leg_rig,
        phase: float,
        side_multiplier: float,
    ):
        """
        Procedural gait solver.
        """

        phase = smootherstep(phase)

        stride = (
            self.walk_direction
            * self.config.stride_length
            * (phase - 0.5)
        )

        side_offset = vec3(
            side_multiplier * 0.18,
            0.0,
            0.0,
        )

        foot_target = solve_leg_step_arc(
            start=-stride + side_offset,
            end=stride + side_offset,
            step_height=self.config.step_height,
            t=phase,
        )

        leg_rig.solve_leg_ik(
            foot_target
        )

        self._update_foot_contact(
            leg_rig,
            phase,
        )

        foot_rotation = (
            np.sin(phase * np.pi)
            * self.config.foot_rotation_strength
        )

        leg_rig.foot.set_rotation(
            foot_rotation
        )

    # =====================================================
    # FOOT CONTACT
    # =====================================================

    def _update_foot_contact(
        self,
        leg_rig,
        phase: float,
    ):
        """
        Procedural planted/lifted timing.
        """

        if (
            phase
            > self.config.foot_lift_threshold
        ):
            leg_rig.foot.set_lifted()

            leg_rig.ankle_joint.set_lifted()

        else:
            leg_rig.foot.set_planted()

            leg_rig.ankle_joint.set_planted()

    # =====================================================
    # AUDIO TIMING
    # =====================================================

    def _update_footstep_audio(self):
        """
        Procedural footstep sound timing.

        Features:
        - alternating left/right feel
        - soft mascot timing
        - subtle educational rhythm
        - cinematic pacing
        """

        if not self.with_sound:
            return

        if not self.config.enable_audio:
            return

        if (
            self.footstep_timer
            < self.config.footstep_cooldown
        ):
            return

        # -------------------------------------------------
        # LEFT STEP
        # -------------------------------------------------

        if (
            self.left_phase
            > self.config.foot_lift_threshold
            and not self.left_step_triggered
        ):

            maybe_play_sound(
                self.with_sound,
                play_walk_step,
                frequency=104
                + self.config.left_step_pitch_offset,
                volume=self.config.footstep_volume,
            )

            self.left_step_triggered = True

            self.right_step_triggered = False

            self.footstep_timer = 0.0

        # -------------------------------------------------
        # RIGHT STEP
        # -------------------------------------------------

        if (
            self.right_phase
            > self.config.foot_lift_threshold
            and not self.right_step_triggered
        ):

            maybe_play_sound(
                self.with_sound,
                play_walk_step,
                frequency=112
                + self.config.right_step_pitch_offset,
                volume=self.config.footstep_volume,
            )

            self.right_step_triggered = True

            self.left_step_triggered = False

            self.footstep_timer = 0.0

    # =====================================================
    # ROOT MOTION
    # =====================================================

    def _apply_root_motion(
        self,
        delta_time: float,
    ):
        """
        Move creature root.
        """

        movement = (
            self.walk_direction
            * self.current_speed
            * self.config.walk_speed
            * delta_time
            * self.config.root_motion_strength
        )

        self.body_rig.current_position += movement

        self.body_rig.move_to(
            self.body_rig.current_position
        )

    # =====================================================
    # SPEED
    # =====================================================

    def set_speed(
        self,
        speed: float,
    ):
        self.target_speed = max(
            0.0,
            speed,
        )

    # =====================================================
    # DIRECTION
    # =====================================================

    def set_direction(
        self,
        direction,
    ):
        direction = np.array(
            direction,
            dtype=float,
        )

        magnitude = np.linalg.norm(direction)

        if magnitude <= 1e-5:
            return

        self.walk_direction = (
            direction / magnitude
        )

    # =====================================================
    # AUDIO CONTROL
    # =====================================================

    def enable_sound(self):
        """
        Enable walk audio.
        """

        self.with_sound = True

    def disable_sound(self):
        """
        Disable walk audio.
        """

        self.with_sound = False

    # =====================================================
    # STATE
    # =====================================================

    def is_walking(self):
        return (
            self.current_speed > 1e-4
        )

    def get_walk_cycle(self):
        return self.walk_cycle

    def get_speed(self):
        return self.current_speed

    # =====================================================
    # RESET
    # =====================================================

    def reset(self):
        """
        Reset procedural gait state.
        """

        self.walk_cycle = 0.0

        self.current_speed = 0.0

        self.target_speed = 0.0

        self.left_phase = 0.0

        self.right_phase = 0.5

        self.left_step_triggered = False

        self.right_step_triggered = False

        self.footstep_timer = 0.0

        self.body_rig.reset_pose()

    # =====================================================
    # DEBUG
    # =====================================================

    def debug_print(self):
        print("========== WALK ACTION ==========")
        print("Cycle:", self.walk_cycle)
        print("Speed:", self.current_speed)
        print("Direction:", self.walk_direction)
        print("Left Phase:", self.left_phase)
        print("Right Phase:", self.right_phase)
        print("Sound Enabled:", self.with_sound)
        print("=================================")


# =========================================================
# FACTORY HELPERS
# =========================================================

def build_walk_action(
    body_rig: BodyRig,
    config: WalkActionConfig | None = None,
    with_sound: bool = True,
) -> WalkAction:
    """
    Create production-grade procedural walk action.
    """

    return WalkAction(
        body_rig=body_rig,
        config=config,
        with_sound=with_sound,
    )


# =========================================================
# MANIM COMPATIBILITY
# =========================================================

def build_walk_animation(
    body_rig: BodyRig,
    cycles: int = 2,
    with_sound: bool = True,
):
    """
    Backward-compatible placeholder.

    Future:
    integrate directly with Manim Animation.

    Args:
        body_rig:
            Creature body rig.

        cycles:
            Walk cycle count.

        with_sound:
            Enables/disables procedural walk audio.
    """

    logger.debug(
        "Building walk animation | cycles=%s | with_sound=%s",
        cycles,
        with_sound,
    )

    return AnimationGroup()