# File: mathlab_creature/creature/controllers/camera_controller.py

"""
mathlab_creature/creature/controllers/camera_controller.py

Production-grade cinematic camera controller
for creature-focused animation systems.

Core Responsibilities
---------------------
- follow creature
- orbit camera
- zoom control
- cinematic shots
- framing
- tracking
- smoothing
- procedural camera motion

IMPORTANT:
This version is FIXED for ManimGL v1.7.2

Previous issue:
----------------
MovingCameraScene does NOT exist in installed manimgl package.

This file now:
- removes incompatible imports
- works with current ManimGL
- keeps architecture intact
- keeps cinematic system intact
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np

from manimlib import Scene

from mathlab_creature.core.transforms import (
    vec3,
)

from mathlab_creature.core.kinematics import (
    damp_vector,
    damp,
    clamp,
)

from mathlab_creature.creature.rigs.body_rig import (
    BodyRig,
)


# =========================================================
# ENUMS
# =========================================================

class CameraMode(str, Enum):

    STATIC = "static"

    FOLLOW = "follow"

    ORBIT = "orbit"

    LOOK_AT = "look_at"

    CINEMATIC = "cinematic"

    LOCKED = "locked"


# =========================================================
# CONFIG
# =========================================================

@dataclass
class CameraControllerConfig:

    follow_smoothing: float = 6.0

    zoom_smoothing: float = 5.0

    orbit_speed: float = 0.8

    default_zoom: float = 1.0

    minimum_zoom: float = 0.3

    maximum_zoom: float = 4.0

    follow_offset_x: float = 0.0

    follow_offset_y: float = 1.2

    follow_offset_z: float = 0.0

    orbit_radius: float = 4.0

    orbit_height: float = 1.5

    cinematic_drift_strength: float = 0.08

    predictive_follow_strength: float = 0.25


# =========================================================
# CAMERA CONTROLLER
# =========================================================

class CameraController:
    """
    Production-grade cinematic camera system.
    """

    def __init__(
        self,
        scene: Scene,
        body_rig: BodyRig,
        config: CameraControllerConfig | None = None,
    ):
        self.scene = scene

        self.body_rig = body_rig

        self.config = (
            config
            or CameraControllerConfig()
        )

        # -------------------------------------------------
        # MODE
        # -------------------------------------------------

        self.mode = CameraMode.FOLLOW

        # -------------------------------------------------
        # POSITION
        # -------------------------------------------------

        self.current_position = vec3()

        self.target_position = vec3()

        self.current_zoom = (
            self.config.default_zoom
        )

        self.target_zoom = (
            self.config.default_zoom
        )

        # -------------------------------------------------
        # ORBIT
        # -------------------------------------------------

        self.orbit_angle = 0.0

        self.orbit_target = vec3()

        # -------------------------------------------------
        # LOOK TARGET
        # -------------------------------------------------

        self.look_target = vec3()

        # -------------------------------------------------
        # CINEMATIC
        # -------------------------------------------------

        self.cinematic_time = 0.0

        self.cinematic_drift = vec3()

    # =====================================================
    # UPDATE
    # =====================================================

    def update(
        self,
        delta_time: float,
    ):

        self.cinematic_time += delta_time

        # -------------------------------------------------
        # MODES
        # -------------------------------------------------

        if self.mode == CameraMode.FOLLOW:

            self._update_follow(
                delta_time
            )

        elif self.mode == CameraMode.ORBIT:

            self._update_orbit(
                delta_time
            )

        elif self.mode == CameraMode.LOOK_AT:

            self._update_look_at(
                delta_time
            )

        elif self.mode == CameraMode.CINEMATIC:

            self._update_cinematic(
                delta_time
            )

        # -------------------------------------------------
        # ZOOM
        # -------------------------------------------------

        self._update_zoom(
            delta_time
        )

        # -------------------------------------------------
        # APPLY
        # -------------------------------------------------

        self._apply_camera()

    # =====================================================
    # FOLLOW
    # =====================================================

    def follow_creature(self):

        self.mode = CameraMode.FOLLOW

    def _update_follow(
        self,
        delta_time: float,
    ):

        creature_position = (
            self.body_rig.current_position
        )

        velocity = (
            self.body_rig.current_velocity
        )

        predictive_offset = (
            velocity
            * self.config.predictive_follow_strength
        )

        offset = vec3(
            self.config.follow_offset_x,
            self.config.follow_offset_y,
            self.config.follow_offset_z,
        )

        self.target_position = (
            creature_position
            + offset
            + predictive_offset
        )

        self.current_position = damp_vector(
            self.current_position,
            self.target_position,
            self.config.follow_smoothing,
            delta_time,
        )

    # =====================================================
    # ORBIT
    # =====================================================

    def orbit_creature(
        self,
        radius: float | None = None,
    ):

        self.mode = CameraMode.ORBIT

        if radius is not None:
            self.config.orbit_radius = radius

    def _update_orbit(
        self,
        delta_time: float,
    ):

        self.orbit_angle += (
            delta_time
            * self.config.orbit_speed
        )

        target = (
            self.body_rig.current_position
        )

        x = (
            np.cos(self.orbit_angle)
            * self.config.orbit_radius
        )

        y = (
            np.sin(self.orbit_angle)
            * self.config.orbit_radius
        )

        self.target_position = (
            target
            + vec3(
                x,
                y
                + self.config.orbit_height,
                0.0,
            )
        )

        self.current_position = damp_vector(
            self.current_position,
            self.target_position,
            self.config.follow_smoothing,
            delta_time,
        )

    # =====================================================
    # LOOK AT
    # =====================================================

    def look_at(
        self,
        world_position,
    ):

        self.look_target = np.array(
            world_position,
            dtype=float,
        )

        self.mode = CameraMode.LOOK_AT

    def _update_look_at(
        self,
        delta_time: float,
    ):

        self.target_position = (
            self.look_target
        )

        self.current_position = damp_vector(
            self.current_position,
            self.target_position,
            self.config.follow_smoothing,
            delta_time,
        )

    # =====================================================
    # CINEMATIC
    # =====================================================

    def cinematic_mode(self):

        self.mode = CameraMode.CINEMATIC

    def _update_cinematic(
        self,
        delta_time: float,
    ):

        creature_position = (
            self.body_rig.current_position
        )

        drift = vec3(
            np.sin(
                self.cinematic_time * 0.35
            )
            * self.config.cinematic_drift_strength,

            np.cos(
                self.cinematic_time * 0.28
            )
            * self.config.cinematic_drift_strength,

            0.0,
        )

        offset = vec3(
            self.config.follow_offset_x,
            self.config.follow_offset_y,
            self.config.follow_offset_z,
        )

        self.target_position = (
            creature_position
            + offset
            + drift
        )

        self.current_position = damp_vector(
            self.current_position,
            self.target_position,
            self.config.follow_smoothing,
            delta_time,
        )

    # =====================================================
    # ZOOM
    # =====================================================

    def set_zoom(
        self,
        zoom_value: float,
    ):

        self.target_zoom = clamp(
            zoom_value,
            self.config.minimum_zoom,
            self.config.maximum_zoom,
        )

    def zoom_in(
        self,
        amount: float = 0.1,
    ):

        self.set_zoom(
            self.target_zoom - amount
        )

    def zoom_out(
        self,
        amount: float = 0.1,
    ):

        self.set_zoom(
            self.target_zoom + amount
        )

    def _update_zoom(
        self,
        delta_time: float,
    ):

        self.current_zoom = damp(
            self.current_zoom,
            self.target_zoom,
            self.config.zoom_smoothing,
            delta_time,
        )

    # =====================================================
    # APPLY CAMERA
    # =====================================================

    def _apply_camera(self):
        """
        Push transforms into ManimGL camera.
        """

        # -------------------------------------------------
        # SAFETY
        # -------------------------------------------------

        if not hasattr(
            self.scene,
            "camera",
        ):
            return

        if not hasattr(
            self.scene.camera,
            "frame",
        ):
            return

        frame = self.scene.camera.frame

        # -------------------------------------------------
        # POSITION
        # -------------------------------------------------

        frame.move_to(
            self.current_position
        )

        # -------------------------------------------------
        # ZOOM
        # -------------------------------------------------

        frame.set_width(
            14 * self.current_zoom
        )

    # =====================================================
    # SHOTS
    # =====================================================

    def wide_shot(self):

        self.set_zoom(1.8)

    def medium_shot(self):

        self.set_zoom(1.0)

    def close_up(self):

        self.set_zoom(0.55)

    # =====================================================
    # LOCK
    # =====================================================

    def lock_camera(self):

        self.mode = CameraMode.LOCKED

    def unlock_camera(self):

        self.mode = CameraMode.FOLLOW

    # =====================================================
    # STATE
    # =====================================================

    def get_mode(self):

        return self.mode

    def get_zoom(self):

        return self.current_zoom

    def get_position(self):

        return np.array(
            self.current_position
        )

    # =====================================================
    # RESET
    # =====================================================

    def reset(self):

        self.current_position = vec3()

        self.target_position = vec3()

        self.current_zoom = (
            self.config.default_zoom
        )

        self.target_zoom = (
            self.config.default_zoom
        )

        self.orbit_angle = 0.0

        self.mode = CameraMode.FOLLOW

    # =====================================================
    # DEBUG
    # =====================================================

    def debug_print(self):

        print(
            "========= CAMERA CONTROLLER ========="
        )

        print(
            "Mode:",
            self.mode,
        )

        print(
            "Position:",
            self.current_position,
        )

        print(
            "Zoom:",
            self.current_zoom,
        )

        print(
            "Orbit Angle:",
            self.orbit_angle,
        )

        print(
            "====================================="
        )

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self):

        return (
            f"CameraController("
            f"mode='{self.mode}', "
            f"zoom={round(self.current_zoom, 3)}"
            f")"
        )


# =========================================================
# FACTORY HELPERS
# =========================================================

def build_camera_controller(
    scene: Scene,
    body_rig: BodyRig,
    config: CameraControllerConfig | None = None,
) -> CameraController:
    """
    Create production-grade cinematic camera controller.
    """

    return CameraController(
        scene=scene,
        body_rig=body_rig,
        config=config,
    )