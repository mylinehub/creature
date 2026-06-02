"""
Visibility controller for mathlab-mylinehub-creature.

Controls visibility for one connected creature.

Architecture rule:
- visibility_controller.py never manipulates body parts
- visibility_controller.py works through BodyRig
- BodyRig owns creature root/group visibility
- preserves creature transform state
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np

from mathlab_creature.core.kinematics import damp
from mathlab_creature.core.kinematics import clamp
from mathlab_creature.creature.rigs.body_rig import BodyRig


class VisibilityMode(str, Enum):
    VISIBLE = "visible"
    HIDDEN = "hidden"
    FADING_IN = "fading_in"
    FADING_OUT = "fading_out"


@dataclass
class VisibilityControllerConfig:
    fade_speed: float = 8.0

    minimum_visible_opacity: float = 0.01

    hidden_opacity: float = 0.0
    visible_opacity: float = 1.0

    preserve_transform_state: bool = True

    enable_cinematic_fade: bool = True


class VisibilityController:
    """
    Controls creature visibility through BodyRig.
    """

    def __init__(
        self,
        body_rig: BodyRig,
        config: VisibilityControllerConfig | None = None,
    ) -> None:
        if not isinstance(body_rig, BodyRig):
            raise TypeError(
                f"body_rig must be BodyRig, got {type(body_rig).__name__}"
            )

        self.body_rig = body_rig
        self.config = config or VisibilityControllerConfig()

        self.mode = VisibilityMode.VISIBLE

        self.current_opacity = 1.0
        self.target_opacity = 1.0

        self.visible = True

        self.saved_position = np.array(
            self.body_rig.current_position,
            dtype=float,
        )

        self.saved_rotation = float(
            self.body_rig.current_rotation
        )

        self.saved_scale = float(
            self.body_rig.current_scale
        )

    def update(
        self,
        delta_time: float,
    ) -> None:
        if not self.config.enable_cinematic_fade:
            return

        delta_time = float(delta_time)

        if delta_time <= 0:
            return

        self.current_opacity = damp(
            self.current_opacity,
            self.target_opacity,
            self.config.fade_speed,
            delta_time,
        )

        self.current_opacity = clamp(
            self.current_opacity,
            0.0,
            1.0,
        )

        self.body_rig.set_opacity(
            self.current_opacity,
        )

        if abs(
            self.current_opacity
            - self.target_opacity
        ) <= 0.001:

            if (
                self.target_opacity
                <= self.config.minimum_visible_opacity
            ):
                self.mode = VisibilityMode.HIDDEN
                self.visible = False

            else:
                self.mode = VisibilityMode.VISIBLE
                self.visible = True

    def show(
        self,
        animated: bool = True,
    ) -> None:
        self.visible = True

        if animated:
            self.mode = VisibilityMode.FADING_IN
            self.target_opacity = (
                self.config.visible_opacity
            )

        else:
            self.current_opacity = (
                self.config.visible_opacity
            )

            self.target_opacity = (
                self.config.visible_opacity
            )

            self.mode = VisibilityMode.VISIBLE

            self.body_rig.set_opacity(
                self.current_opacity,
            )

    def hide(
        self,
        animated: bool = True,
    ) -> None:
        self._save_state()

        if animated:
            self.mode = VisibilityMode.FADING_OUT

            self.target_opacity = (
                self.config.hidden_opacity
            )

        else:
            self.current_opacity = (
                self.config.hidden_opacity
            )

            self.target_opacity = (
                self.config.hidden_opacity
            )

            self.visible = False
            self.mode = VisibilityMode.HIDDEN

            self.body_rig.set_opacity(
                self.current_opacity,
            )

    def toggle_visibility(
        self,
        animated: bool = True,
    ) -> None:
        if self.visible:
            self.hide(animated=animated)
        else:
            self.show(animated=animated)

    def _save_state(
        self,
    ) -> None:
        if not self.config.preserve_transform_state:
            return

        self.saved_position = np.array(
            self.body_rig.current_position,
            dtype=float,
        )

        self.saved_rotation = float(
            self.body_rig.current_rotation
        )

        self.saved_scale = float(
            self.body_rig.current_scale
        )

    def restore_state(
        self,
    ) -> None:
        if not self.config.preserve_transform_state:
            return

        self.body_rig.teleport(
            self.saved_position,
        )

        self.body_rig.rotate_to(
            self.saved_rotation,
        )

        self.body_rig.set_creature_scale(
            self.saved_scale,
        )

    def appear_at(
        self,
        position,
    ) -> None:
        self.body_rig.teleport(
            np.array(
                position,
                dtype=float,
            )
        )

        self.show(animated=False)

    def disappear(
        self,
        animated: bool = True,
    ) -> None:
        self.hide(animated=animated)

    def fade_to(
        self,
        opacity: float,
    ) -> None:
        opacity = clamp(
            float(opacity),
            0.0,
            1.0,
        )

        self.target_opacity = opacity

        if (
            opacity
            <= self.config.minimum_visible_opacity
        ):
            self.mode = VisibilityMode.FADING_OUT
        else:
            self.mode = VisibilityMode.FADING_IN

    def hidden_teleport(
        self,
        position,
    ) -> None:
        was_visible = self.visible

        self.hide(animated=False)

        self.body_rig.teleport(
            np.array(
                position,
                dtype=float,
            )
        )

        if was_visible:
            self.show(animated=False)

    def is_visible(
        self,
    ) -> bool:
        return bool(self.visible)

    def is_hidden(
        self,
    ) -> bool:
        return (
            self.mode
            == VisibilityMode.HIDDEN
        )

    def fading(
        self,
    ) -> bool:
        return (
            self.mode
            in (
                VisibilityMode.FADING_IN,
                VisibilityMode.FADING_OUT,
            )
        )

    def get_opacity(
        self,
    ) -> float:
        return float(self.current_opacity)

    def get_mode(
        self,
    ) -> VisibilityMode:
        return self.mode

    def reset(
        self,
    ) -> None:
        self.current_opacity = 1.0
        self.target_opacity = 1.0

        self.visible = True
        self.mode = VisibilityMode.VISIBLE

        self.body_rig.set_opacity(1.0)

    def debug_print(
        self,
    ) -> None:
        print("====== VISIBILITY CONTROLLER ======")
        print("Mode:", self.mode)
        print("Visible:", self.visible)
        print("Current Opacity:", self.current_opacity)
        print("Target Opacity:", self.target_opacity)
        print("===================================")

    def __repr__(
        self,
    ) -> str:
        return (
            f"VisibilityController("
            f"mode={self.mode!r}, "
            f"opacity={round(self.current_opacity, 3)}"
            f")"
        )


def build_visibility_controller(
    body_rig: BodyRig,
    config: VisibilityControllerConfig | None = None,
) -> VisibilityController:
    return VisibilityController(
        body_rig=body_rig,
        config=config,
    )


__all__ = [
    "VisibilityMode",
    "VisibilityControllerConfig",
    "VisibilityController",
    "build_visibility_controller",
]