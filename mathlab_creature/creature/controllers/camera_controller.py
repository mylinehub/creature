"""
Camera controller for mathlab-mylinehub-creature.

Controls camera framing for one connected creature.

Architecture rule:
- camera_controller.py does not move creature parts
- camera_controller.py reads BodyRig state only
- camera_controller.py controls ManimGL camera frame only
- compatible with ManimGL camera.frame when available
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np

from manimlib import Scene

from mathlab_creature.core.geometry import as_vec3
from mathlab_creature.core.geometry import point
from mathlab_creature.core.geometry import zero_vector
from mathlab_creature.core.kinematics import clamp
from mathlab_creature.core.kinematics import damp
from mathlab_creature.core.kinematics import damp_vector
from mathlab_creature.creature.rigs.body_rig import BodyRig


class CameraMode(str, Enum):
    STATIC = "static"
    FOLLOW = "follow"
    ORBIT = "orbit"
    LOOK_AT = "look_at"
    CINEMATIC = "cinematic"
    LOCKED = "locked"


@dataclass
class CameraControllerConfig:
    follow_smoothing: float = 6.0
    zoom_smoothing: float = 5.0

    orbit_speed: float = 0.8
    orbit_radius: float = 4.0
    orbit_height: float = 1.5

    default_zoom: float = 1.0
    minimum_zoom: float = 0.3
    maximum_zoom: float = 4.0

    follow_offset_x: float = 0.0
    follow_offset_y: float = 1.2
    follow_offset_z: float = 0.0

    cinematic_drift_strength: float = 0.08
    predictive_follow_strength: float = 0.25

    base_frame_width: float = 14.0


class CameraController:
    """
    Cinematic camera controller.
    """

    def __init__(
        self,
        scene: Scene,
        body_rig: BodyRig,
        config: CameraControllerConfig | None = None,
    ) -> None:
        if not isinstance(body_rig, BodyRig):
            raise TypeError(
                f"body_rig must be BodyRig, got {type(body_rig).__name__}"
            )

        self.scene = scene
        self.body_rig = body_rig
        self.config = config or CameraControllerConfig()

        self.mode = CameraMode.FOLLOW

        self.current_position = zero_vector()
        self.target_position = zero_vector()

        self.current_zoom = self.config.default_zoom
        self.target_zoom = self.config.default_zoom

        self.orbit_angle = 0.0
        self.look_target = zero_vector()

        self.cinematic_time = 0.0

    def update(
        self,
        delta_time: float,
    ) -> None:
        delta_time = float(delta_time)

        if delta_time <= 0:
            return

        if self.mode == CameraMode.LOCKED:
            return

        self.cinematic_time += delta_time

        if self.mode == CameraMode.FOLLOW:
            self._update_follow(delta_time)

        elif self.mode == CameraMode.ORBIT:
            self._update_orbit(delta_time)

        elif self.mode == CameraMode.LOOK_AT:
            self._update_look_at(delta_time)

        elif self.mode == CameraMode.CINEMATIC:
            self._update_cinematic(delta_time)

        self._update_zoom(delta_time)
        self._apply_camera()

    def _follow_offset(
        self,
    ):
        return point(
            self.config.follow_offset_x,
            self.config.follow_offset_y,
            self.config.follow_offset_z,
        )

    def follow_creature(
        self,
    ) -> None:
        self.mode = CameraMode.FOLLOW

    def _update_follow(
        self,
        delta_time: float,
    ) -> None:
        creature_position = as_vec3(
            self.body_rig.current_position,
            name="body_rig.current_position",
        )

        velocity = as_vec3(
            self.body_rig.current_velocity,
            name="body_rig.current_velocity",
        )

        predictive_offset = (
            velocity
            * self.config.predictive_follow_strength
        )

        self.target_position = (
            creature_position
            + self._follow_offset()
            + predictive_offset
        )

        self.current_position = damp_vector(
            self.current_position,
            self.target_position,
            self.config.follow_smoothing,
            delta_time,
        )

    def orbit_creature(
        self,
        radius: float | None = None,
    ) -> None:
        self.mode = CameraMode.ORBIT

        if radius is not None:
            self.config.orbit_radius = max(
                0.0,
                float(radius),
            )

    def _update_orbit(
        self,
        delta_time: float,
    ) -> None:
        self.orbit_angle += (
            delta_time
            * self.config.orbit_speed
        )

        target = as_vec3(
            self.body_rig.current_position,
            name="body_rig.current_position",
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
            + point(
                x,
                y + self.config.orbit_height,
                0.0,
            )
        )

        self.current_position = damp_vector(
            self.current_position,
            self.target_position,
            self.config.follow_smoothing,
            delta_time,
        )

    def look_at(
        self,
        world_position,
    ) -> None:
        self.look_target = as_vec3(
            world_position,
            name="world_position",
        )

        self.mode = CameraMode.LOOK_AT

    def _update_look_at(
        self,
        delta_time: float,
    ) -> None:
        self.target_position = self.look_target

        self.current_position = damp_vector(
            self.current_position,
            self.target_position,
            self.config.follow_smoothing,
            delta_time,
        )

    def cinematic_mode(
        self,
    ) -> None:
        self.mode = CameraMode.CINEMATIC

    def _update_cinematic(
        self,
        delta_time: float,
    ) -> None:
        creature_position = as_vec3(
            self.body_rig.current_position,
            name="body_rig.current_position",
        )

        drift = point(
            np.sin(self.cinematic_time * 0.35)
            * self.config.cinematic_drift_strength,
            np.cos(self.cinematic_time * 0.28)
            * self.config.cinematic_drift_strength,
            0.0,
        )

        self.target_position = (
            creature_position
            + self._follow_offset()
            + drift
        )

        self.current_position = damp_vector(
            self.current_position,
            self.target_position,
            self.config.follow_smoothing,
            delta_time,
        )

    def set_zoom(
        self,
        zoom_value: float,
    ) -> None:
        self.target_zoom = clamp(
            float(zoom_value),
            self.config.minimum_zoom,
            self.config.maximum_zoom,
        )

    def zoom_in(
        self,
        amount: float = 0.1,
    ) -> None:
        self.set_zoom(
            self.target_zoom - float(amount),
        )

    def zoom_out(
        self,
        amount: float = 0.1,
    ) -> None:
        self.set_zoom(
            self.target_zoom + float(amount),
        )

    def _update_zoom(
        self,
        delta_time: float,
    ) -> None:
        self.current_zoom = damp(
            self.current_zoom,
            self.target_zoom,
            self.config.zoom_smoothing,
            delta_time,
        )

    def _apply_camera(
        self,
    ) -> None:
        """
        Push transforms into ManimGL camera when available.
        """
        if not hasattr(self.scene, "camera"):
            return

        if not hasattr(self.scene.camera, "frame"):
            return

        frame = self.scene.camera.frame

        frame.move_to(
            self.current_position,
        )

        frame.set_width(
            self.config.base_frame_width
            * self.current_zoom
        )

    def wide_shot(
        self,
    ) -> None:
        self.set_zoom(1.8)

    def medium_shot(
        self,
    ) -> None:
        self.set_zoom(1.0)

    def close_up(
        self,
    ) -> None:
        self.set_zoom(0.55)

    def lock_camera(
        self,
    ) -> None:
        self.mode = CameraMode.LOCKED

    def unlock_camera(
        self,
    ) -> None:
        self.mode = CameraMode.FOLLOW

    def static_camera(
        self,
    ) -> None:
        self.mode = CameraMode.STATIC

    def get_mode(
        self,
    ) -> CameraMode:
        return self.mode

    def get_zoom(
        self,
    ) -> float:
        return float(self.current_zoom)

    def get_position(
        self,
    ):
        return np.array(
            self.current_position,
            dtype=float,
        )

    def reset(
        self,
    ) -> None:
        self.current_position = zero_vector()
        self.target_position = zero_vector()

        self.current_zoom = self.config.default_zoom
        self.target_zoom = self.config.default_zoom

        self.orbit_angle = 0.0
        self.look_target = zero_vector()
        self.cinematic_time = 0.0

        self.mode = CameraMode.FOLLOW

    def debug_print(
        self,
    ) -> None:
        print("========= CAMERA CONTROLLER =========")
        print("Mode:", self.mode)
        print("Position:", self.current_position)
        print("Zoom:", self.current_zoom)
        print("Orbit Angle:", self.orbit_angle)
        print("=====================================")

    def __repr__(
        self,
    ) -> str:
        return (
            f"CameraController("
            f"mode={self.mode!r}, "
            f"zoom={round(self.current_zoom, 3)}"
            f")"
        )


def build_camera_controller(
    scene: Scene,
    body_rig: BodyRig,
    config: CameraControllerConfig | None = None,
) -> CameraController:
    return CameraController(
        scene=scene,
        body_rig=body_rig,
        config=config,
    )


__all__ = [
    "CameraMode",
    "CameraControllerConfig",
    "CameraController",
    "build_camera_controller",
]