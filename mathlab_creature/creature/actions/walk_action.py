"""
Walk action for mathlab-mylinehub-creature.

This file controls walking state for one connected creature.

Architecture rule:
- walk_action.py does not build creature parts
- walk_action.py does not move legs, feet, or body parts independently
- walk_action.py works through BodyRig and LegRig
- BodyRig moves the one creature root
- LegRig controls connected legs/feet
- audio is optional and safely ignored if audio modules are unavailable
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from manimlib import AnimationGroup

from mathlab_creature.core.geometry import as_vec3
from mathlab_creature.core.geometry import normalize
from mathlab_creature.core.geometry import zero_vector
from mathlab_creature.core.kinematics import smootherstep
from mathlab_creature.core.logger import get_logger
from mathlab_creature.creature.rigs.body_rig import BodyRig


logger = get_logger(__name__)


try:
    from mathlab_creature.core.audio.helpers import maybe_play_sound
    from mathlab_creature.core.audio.procedural import play_walk_step
except Exception:
    maybe_play_sound = None
    play_walk_step = None


@dataclass
class WalkActionConfig:
    stride_length: float = 0.75
    step_height: float = 0.30

    walk_speed: float = 1.0
    gait_frequency: float = 2.0

    body_bounce_strength: float = 0.08
    body_sway_strength: float = 0.05
    body_tilt_strength: float = 0.12

    foot_lift_threshold: float = 0.52
    foot_rotation_strength: float = 0.28

    movement_damping: float = 0.92
    root_motion_strength: float = 1.0

    enable_audio: bool = True
    footstep_volume: float = 1.0
    footstep_cooldown: float = 0.22

    left_step_pitch_offset: float = -6.0
    right_step_pitch_offset: float = 6.0


class WalkAction:
    """
    Procedural walk controller.

    It updates BodyRig root movement and LegRig gait state.
    """

    def __init__(
        self,
        body_rig: BodyRig,
        config: WalkActionConfig | None = None,
        with_sound: bool = True,
    ) -> None:
        if not isinstance(body_rig, BodyRig):
            raise TypeError(
                f"body_rig must be BodyRig, got {type(body_rig).__name__}"
            )

        self.body_rig = body_rig
        self.config = config or WalkActionConfig()
        self.with_sound = bool(with_sound)

        self.walk_cycle = 0.0
        self.walk_direction = zero_vector()
        self.walk_direction[1] = 1.0

        self.current_speed = 0.0
        self.target_speed = 0.0
        self.is_active = False

        self.left_phase = 0.0
        self.right_phase = 0.5

        self.left_step_triggered = False
        self.right_step_triggered = False
        self.footstep_timer = 0.0

    def start(
        self,
        direction,
        speed: float = 1.0,
    ) -> None:
        direction_vec = normalize(
            as_vec3(
                direction,
                name="direction",
            )
        )

        if np.linalg.norm(direction_vec) <= 1e-8:
            return

        self.walk_direction = direction_vec
        self.target_speed = max(0.0, float(speed))
        self.is_active = True

    def stop(self) -> None:
        self.target_speed = 0.0
        self.is_active = False

    def update(
        self,
        delta_time: float,
    ) -> None:
        delta_time = float(delta_time)

        if delta_time <= 0:
            return

        self.current_speed += (
            self.target_speed - self.current_speed
        ) * (
            1.0 - self.config.movement_damping
        )

        if self.current_speed <= 1e-4:
            self.current_speed = 0.0
            return

        self.footstep_timer += delta_time

        self.walk_cycle += (
            delta_time
            * self.config.gait_frequency
            * self.current_speed
        )

        self.left_phase = smootherstep(
            np.sin(self.walk_cycle * np.pi) * 0.5 + 0.5
        )
        self.right_phase = smootherstep(
            np.sin((self.walk_cycle + 1.0) * np.pi) * 0.5 + 0.5
        )

        self._update_leg_rig(delta_time)
        self._update_body_rig(delta_time)
        self._update_footstep_audio()

    def _update_leg_rig(
        self,
        delta_time: float,
    ) -> None:
        leg_rig = self.body_rig.get_leg_rig()

        if leg_rig is None:
            return

        leg_rig.move_in_direction(
            self.walk_direction,
            self.current_speed,
            delta_time,
        )

        leg_rig.update_step_pose(
            left_phase=0.0,
            right_phase=1.0,
        )

    def _update_body_rig(
        self,
        delta_time: float,
    ) -> None:
        movement_speed = (
            self.current_speed
            * self.config.walk_speed
            * self.config.root_motion_strength
        )

        self.body_rig.move(
            self.walk_direction,
            movement_speed,
            delta_time,
        )

    def _update_footstep_audio(self) -> None:
        if not self.with_sound:
            return

        if not self.config.enable_audio:
            return

        if self.footstep_timer < self.config.footstep_cooldown:
            return

        if maybe_play_sound is None or play_walk_step is None:
            return

        if (
            self.left_phase > self.config.foot_lift_threshold
            and not self.left_step_triggered
        ):
            maybe_play_sound(
                self.with_sound,
                play_walk_step,
                frequency=104 + self.config.left_step_pitch_offset,
                volume=self.config.footstep_volume,
            )

            self.left_step_triggered = True
            self.right_step_triggered = False
            self.footstep_timer = 0.0
            return

        if (
            self.right_phase > self.config.foot_lift_threshold
            and not self.right_step_triggered
        ):
            maybe_play_sound(
                self.with_sound,
                play_walk_step,
                frequency=112 + self.config.right_step_pitch_offset,
                volume=self.config.footstep_volume,
            )

            self.right_step_triggered = True
            self.left_step_triggered = False
            self.footstep_timer = 0.0

    def set_speed(
        self,
        speed: float,
    ) -> None:
        self.target_speed = max(
            0.0,
            float(speed),
        )

        self.is_active = self.target_speed > 0.0

    def set_direction(
        self,
        direction,
    ) -> None:
        direction_vec = normalize(
            as_vec3(
                direction,
                name="direction",
            )
        )

        if np.linalg.norm(direction_vec) <= 1e-8:
            return

        self.walk_direction = direction_vec

    def enable_sound(self) -> None:
        self.with_sound = True

    def disable_sound(self) -> None:
        self.with_sound = False

    def is_walking(self) -> bool:
        return self.current_speed > 1e-4

    def get_walk_cycle(self) -> float:
        return float(self.walk_cycle)

    def get_speed(self) -> float:
        return float(self.current_speed)

    def reset(self) -> None:
        self.walk_cycle = 0.0

        self.current_speed = 0.0
        self.target_speed = 0.0
        self.is_active = False

        self.left_phase = 0.0
        self.right_phase = 0.5

        self.left_step_triggered = False
        self.right_step_triggered = False
        self.footstep_timer = 0.0

        self.body_rig.reset_pose()

    def debug_print(self) -> None:
        print("========== WALK ACTION ==========")
        print("Cycle:", self.walk_cycle)
        print("Speed:", self.current_speed)
        print("Direction:", self.walk_direction)
        print("Left Phase:", self.left_phase)
        print("Right Phase:", self.right_phase)
        print("Sound Enabled:", self.with_sound)
        print("=================================")


def build_walk_action(
    body_rig: BodyRig,
    config: WalkActionConfig | None = None,
    with_sound: bool = True,
) -> WalkAction:
    return WalkAction(
        body_rig=body_rig,
        config=config,
        with_sound=with_sound,
    )


def build_walk_animation(
    body_rig: BodyRig,
    cycles: int = 2,
    with_sound: bool = True,
):
    """
    Backward-compatible placeholder for Manim Animation usage.
    """
    logger.debug(
        "Building walk animation | cycles=%s | with_sound=%s",
        cycles,
        with_sound,
    )

    return AnimationGroup()


__all__ = [
    "WalkActionConfig",
    "WalkAction",
    "build_walk_action",
    "build_walk_animation",
]