"""
mathlab_creature/creature/controllers/visibility_controller.py

Production-grade creature visibility controller.

Core Responsibilities
---------------------
- gayab/show system
- opacity state
- preserve transform state
- visibility transitions
- cinematic appearing/disappearing
- hidden-state management

Design Goals
------------
- production-ready
- hierarchy-safe
- animation-safe
- state-preserving
- future multiplayer-ready
- cinematic-ready
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np

from mathlab_creature.core.kinematics import (
    damp,
    clamp,
)

from mathlab_creature.creature.rigs.body_rig import (
    BodyRig,
)


# =========================================================
# ENUMS
# =========================================================

class VisibilityMode(str, Enum):
    """
    Visibility states.
    """

    VISIBLE = "visible"

    HIDDEN = "hidden"

    FADING_IN = "fading_in"

    FADING_OUT = "fading_out"


# =========================================================
# CONFIG
# =========================================================

@dataclass
class VisibilityControllerConfig:
    """
    Tunable visibility settings.
    """

    fade_speed: float = 8.0

    minimum_visible_opacity: float = 0.01

    hidden_opacity: float = 0.0

    visible_opacity: float = 1.0

    preserve_collision_state: bool = True

    preserve_transform_state: bool = True

    enable_cinematic_fade: bool = True


# =========================================================
# VISIBILITY CONTROLLER
# =========================================================

class VisibilityController:
    """
    Production-grade visibility controller.

    Features:
    - smooth fading
    - instant hide/show
    - state preservation
    - cinematic transitions
    - transform-safe visibility
    """

    def __init__(
        self,
        body_rig: BodyRig,
        config: VisibilityControllerConfig | None = None,
    ):
        self.body_rig = body_rig

        self.config = (
            config
            or VisibilityControllerConfig()
        )

        # -------------------------------------------------
        # VISIBILITY STATE
        # -------------------------------------------------

        self.mode = VisibilityMode.VISIBLE

        self.current_opacity = 1.0

        self.target_opacity = 1.0

        self.visible = True

        # -------------------------------------------------
        # PRESERVED STATE
        # -------------------------------------------------

        self.saved_position = (
            self.body_rig.current_position.copy()
        )

        self.saved_rotation = (
            self.body_rig.current_rotation
        )

        self.saved_scale = (
            self.body_rig.current_scale.copy()
        )

    # =====================================================
    # UPDATE
    # =====================================================

    def update(
        self,
        delta_time: float,
    ):
        """
        Update cinematic fading.
        """

        if (
            not self.config.enable_cinematic_fade
        ):
            return

        # -------------------------------------------------
        # OPACITY BLEND
        # -------------------------------------------------

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

        # -------------------------------------------------
        # APPLY
        # -------------------------------------------------

        self.body_rig.set_opacity(
            self.current_opacity
        )

        # -------------------------------------------------
        # STATE
        # -------------------------------------------------

        if (
            abs(
                self.current_opacity
                - self.target_opacity
            )
            <= 0.001
        ):
            if (
                self.target_opacity
                <= self.config.minimum_visible_opacity
            ):
                self.mode = (
                    VisibilityMode.HIDDEN
                )

                self.visible = False

            else:
                self.mode = (
                    VisibilityMode.VISIBLE
                )

                self.visible = True

    # =====================================================
    # SHOW
    # =====================================================

    def show(
        self,
        animated: bool = True,
    ):
        """
        Restore visibility.
        """

        self.visible = True

        if animated:
            self.mode = (
                VisibilityMode.FADING_IN
            )

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

            self.mode = (
                VisibilityMode.VISIBLE
            )

            self.body_rig.set_opacity(
                self.current_opacity
            )

    # =====================================================
    # HIDE
    # =====================================================

    def hide(
        self,
        animated: bool = True,
    ):
        """
        Hide while preserving state.
        """

        self._save_state()

        if animated:
            self.mode = (
                VisibilityMode.FADING_OUT
            )

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

            self.mode = (
                VisibilityMode.HIDDEN
            )

            self.visible = False

            self.body_rig.set_opacity(
                self.current_opacity
            )

    # =====================================================
    # TOGGLE
    # =====================================================

    def toggle_visibility(
        self,
        animated: bool = True,
    ):
        """
        Toggle visibility state.
        """

        if self.visible:
            self.hide(
                animated=animated
            )

        else:
            self.show(
                animated=animated
            )

    # =====================================================
    # SAVE STATE
    # =====================================================

    def _save_state(self):
        """
        Preserve transform state before hiding.
        """

        if (
            not self.config.preserve_transform_state
        ):
            return

        self.saved_position = (
            self.body_rig.current_position.copy()
        )

        self.saved_rotation = (
            self.body_rig.current_rotation
        )

        self.saved_scale = (
            self.body_rig.current_scale.copy()
        )

    # =====================================================
    # RESTORE STATE
    # =====================================================

    def restore_state(self):
        """
        Restore preserved transforms.
        """

        if (
            not self.config.preserve_transform_state
        ):
            return

        self.body_rig.teleport(
            self.saved_position
        )

        self.body_rig.rotate_to(
            self.saved_rotation
        )

        self.body_rig.set_creature_scale(
            self.saved_scale[0]
        )

    # =====================================================
    # INSTANT APPEAR
    # =====================================================

    def appear_at(
        self,
        position,
    ):
        """
        Appear instantly at world position.
        """

        position = np.array(
            position,
            dtype=float,
        )

        self.body_rig.teleport(
            position
        )

        self.show(
            animated=False
        )

    # =====================================================
    # DISAPPEAR
    # =====================================================

    def disappear(
        self,
        animated: bool = True,
    ):
        """
        Cinematic vanish.
        """

        self.hide(
            animated=animated
        )

    # =====================================================
    # FADE
    # =====================================================

    def fade_to(
        self,
        opacity: float,
    ):
        """
        Fade to arbitrary opacity.
        """

        opacity = clamp(
            opacity,
            0.0,
            1.0,
        )

        self.target_opacity = opacity

        if opacity <= (
            self.config.minimum_visible_opacity
        ):
            self.mode = (
                VisibilityMode.FADING_OUT
            )

        else:
            self.mode = (
                VisibilityMode.FADING_IN
            )

    # =====================================================
    # TELEPORT HIDDEN
    # =====================================================

    def hidden_teleport(
        self,
        position,
    ):
        """
        Move creature while invisible.
        """

        was_visible = self.visible

        self.hide(
            animated=False
        )

        self.body_rig.teleport(
            position
        )

        if was_visible:
            self.show(
                animated=False
            )

    # =====================================================
    # STATE
    # =====================================================

    def is_visible(self):
        return self.visible

    def is_hidden(self):
        return (
            self.mode
            == VisibilityMode.HIDDEN
        )

    def fading(self):
        return (
            self.mode
            in (
                VisibilityMode.FADING_IN,
                VisibilityMode.FADING_OUT,
            )
        )

    def get_opacity(self):
        return self.current_opacity

    def get_mode(self):
        return self.mode

    # =====================================================
    # RESET
    # =====================================================

    def reset(self):
        """
        Reset visibility state.
        """

        self.current_opacity = 1.0

        self.target_opacity = 1.0

        self.visible = True

        self.mode = VisibilityMode.VISIBLE

        self.body_rig.set_opacity(
            1.0
        )

    # =====================================================
    # DEBUG
    # =====================================================

    def debug_print(self):
        print("====== VISIBILITY CONTROLLER ======")
        print("Mode:", self.mode)
        print("Visible:", self.visible)
        print("Current Opacity:", self.current_opacity)
        print("Target Opacity:", self.target_opacity)
        print("===================================")

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self):
        return (
            f"VisibilityController("
            f"mode='{self.mode}', "
            f"opacity={round(self.current_opacity, 3)}"
            f")"
        )


# =========================================================
# FACTORY HELPERS
# =========================================================

def build_visibility_controller(
    body_rig: BodyRig,
    config: VisibilityControllerConfig | None = None,
) -> VisibilityController:
    """
    Create production-grade visibility controller.
    """

    return VisibilityController(
        body_rig=body_rig,
        config=config,
    )