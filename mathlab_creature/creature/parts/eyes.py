"""
Eye construction for mathlab-mylinehub-creature.

This file builds the creature's eye parts:
- left eye white
- right eye white
- left pupil
- right pupil

Version 1 goals:
- keep eyes simple and expressive
- keep placement driven by anchor helpers
- return grouped parts cleanly
- make later blinking / looking easy

This file only builds the eye objects.
It does not animate blinking or gaze yet.
"""

from __future__ import annotations

import numpy as np
from manimlib import Circle, VGroup

from mathlab_creature.config.colors import EYE_STROKE
from mathlab_creature.config.colors import EYE_WHITE
from mathlab_creature.config.colors import PUPIL_FILL
from mathlab_creature.config.colors import PUPIL_HIGHLIGHT
from mathlab_creature.config.defaults import DEBUG_MODE
from mathlab_creature.config.defaults import LEFT_EYE_NAME
from mathlab_creature.config.defaults import LOG_CREATURE_BUILD
from mathlab_creature.config.defaults import RIGHT_EYE_NAME
from mathlab_creature.config.sizes import EYE_HEIGHT
from mathlab_creature.config.sizes import EYE_STROKE_WIDTH
from mathlab_creature.config.sizes import EYE_WIDTH
from mathlab_creature.config.sizes import PUPIL_MAX_OFFSET
from mathlab_creature.config.sizes import PUPIL_RADIUS

from mathlab_creature.core.anchors import get_left_eye_center
from mathlab_creature.core.anchors import get_right_eye_center
from mathlab_creature.core.geometry import point
from mathlab_creature.core.logger import get_logger
from mathlab_creature.core.naming import creature_pair_part_names
from mathlab_creature.core.naming import creature_part_name

logger = get_logger(__name__)


# ============================================================
# Internal helpers
# ============================================================

def _validate_numeric(name: str, value: float | int) -> float:
    """
    Ensure a numeric value and return it as float.
    """
    if not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be numeric, got {type(value).__name__}")
    return float(value)


def _validate_non_negative(name: str, value: float | int) -> float:
    """
    Ensure a non-negative numeric value.
    """
    value = _validate_numeric(name, value)
    if value < 0:
        raise ValueError(f"{name} must be >= 0, got {value}")
    return value


def _coerce_point3(value, name: str = "value") -> np.ndarray:
    """
    Normalize a point-like input into a 3D numpy point.

    Accepted:
    - numpy array of shape (3,)
    - tuple/list of length 3
    """
    if isinstance(value, np.ndarray):
        if value.shape != (3,):
            raise ValueError(f"{name} must have shape (3,), got {value.shape}")
        return value.astype(float)

    if isinstance(value, (tuple, list)):
        if len(value) != 3:
            raise ValueError(f"{name} must contain exactly 3 values, got {len(value)}")
        return point(value[0], value[1], value[2])

    raise TypeError(f"{name} must be a numpy.ndarray or 3-item tuple/list")


def _offset_point(base_point: np.ndarray, dx: float, dy: float, dz: float = 0.0) -> np.ndarray:
    """
    Return a new point offset from a base point.
    """
    return point(
        base_point[0] + dx,
        base_point[1] + dy,
        base_point[2] + dz,
    )


def _coerce_pupil_offset(
    pupil_offset: tuple[float, float, float] | list[float] | np.ndarray | None = None,
) -> np.ndarray:
    """
    Normalize an optional pupil offset.

    This is kept internal so later gaze logic can reuse it.
    """
    if pupil_offset is None:
        return point(0.0, 0.0, 0.0)

    offset_vec = _coerce_point3(pupil_offset, "pupil_offset")

    # Clamp x/y to safe range so pupil does not drift too far outside the eye.
    clamped_x = max(-PUPIL_MAX_OFFSET, min(PUPIL_MAX_OFFSET, offset_vec[0]))
    clamped_y = max(-PUPIL_MAX_OFFSET, min(PUPIL_MAX_OFFSET, offset_vec[1]))

    return point(clamped_x, clamped_y, offset_vec[2])


# ============================================================
# Internal builders
# ============================================================

def _build_eye_white(
    *,
    width: float = EYE_WIDTH,
    height: float = EYE_HEIGHT,
    stroke_width: float = EYE_STROKE_WIDTH,
    fill_color: str = EYE_WHITE,
    stroke_color: str = EYE_STROKE,
) -> Circle:
    """
    Build one eye white.
    """
    width = _validate_non_negative("width", width)
    height = _validate_non_negative("height", height)
    stroke_width = _validate_non_negative("stroke_width", stroke_width)

    eye = Circle()
    eye.set_width(width)
    eye.set_height(height)
    eye.set_fill(fill_color, opacity=1.0)
    eye.set_stroke(stroke_color, width=stroke_width)
    return eye


def _build_pupil(
    *,
    radius: float = PUPIL_RADIUS,
    fill_color: str = PUPIL_FILL,
) -> Circle:
    """
    Build one pupil.
    """
    radius = _validate_non_negative("radius", radius)

    pupil = Circle(radius=radius)
    pupil.set_fill(fill_color, opacity=1.0)
    pupil.set_stroke(fill_color, width=0)
    return pupil


def _build_pupil_highlight(
    *,
    pupil_radius: float = PUPIL_RADIUS,
    fill_color: str = PUPIL_HIGHLIGHT,
) -> Circle:
    """
    Small highlight on the pupil to keep the eyes lively.
    """
    pupil_radius = _validate_non_negative("pupil_radius", pupil_radius)

    highlight = Circle(radius=pupil_radius * 0.28)
    highlight.set_fill(fill_color, opacity=1.0)
    highlight.set_stroke(fill_color, width=0)
    return highlight


def _build_single_eye_group(
    center_point,
    *,
    eye_name: str = "eye",
    pupil_offset=None,
    eye_width: float = EYE_WIDTH,
    eye_height: float = EYE_HEIGHT,
    eye_stroke_width: float = EYE_STROKE_WIDTH,
    pupil_radius: float = PUPIL_RADIUS,
) -> VGroup:
    """
    Build a single complete eye group at a given center point.

    Structure:
    - eye white
    - pupil
    - highlight
    """
    center_point = _coerce_point3(center_point, "center_point")
    pupil_offset = _coerce_pupil_offset(pupil_offset)

    eye_white = _build_eye_white(
        width=eye_width,
        height=eye_height,
        stroke_width=eye_stroke_width,
    )
    pupil = _build_pupil(radius=pupil_radius)
    highlight = _build_pupil_highlight(pupil_radius=pupil_radius)

    eye_white.move_to(center_point)

    pupil_center = _offset_point(
        center_point,
        pupil_offset[0],
        pupil_offset[1],
        pupil_offset[2],
    )
    pupil.move_to(pupil_center)

    # Slight top-left highlight offset for a more lively feel.
    highlight.move_to(
        _offset_point(
            pupil_center,
            -(pupil_radius * 0.28),
            pupil_radius * 0.28,
            0.0,
        )
    )

    eye_group = VGroup(eye_white, pupil, highlight)

    # Stable naming for easier debugging and later rigging.
    eye_group.name = eye_name
    eye_white.name = f"{eye_name}_white"
    pupil.name = f"{eye_name}_pupil"
    highlight.name = f"{eye_name}_highlight"

    # Lightweight metadata for later blink/look systems.
    eye_group.eye_center = center_point
    eye_group.pupil_center = pupil_center
    eye_group.pupil_offset = pupil_offset
    eye_group.eye_width = eye_width
    eye_group.eye_height = eye_height
    eye_group.pupil_radius = pupil_radius

    if DEBUG_MODE:
        logger.debug(
            "Built eye group | name=%s center=%s pupil_offset=%s",
            eye_name,
            center_point,
            pupil_offset,
        )

    return eye_group


# ============================================================
# Public builders
# ============================================================

def build_left_eye(
    body_center=None,
    *,
    pupil_offset=None,
) -> VGroup:
    """
    Build left eye group.
    """
    if LOG_CREATURE_BUILD:
        logger.info("Building left eye")

    left_eye_center = get_left_eye_center(body_center)
    return _build_single_eye_group(
        left_eye_center,
        eye_name=creature_part_name(LEFT_EYE_NAME),
        pupil_offset=pupil_offset,
    )


def build_right_eye(
    body_center=None,
    *,
    pupil_offset=None,
) -> VGroup:
    """
    Build right eye group.
    """
    if LOG_CREATURE_BUILD:
        logger.info("Building right eye")

    right_eye_center = get_right_eye_center(body_center)
    return _build_single_eye_group(
        right_eye_center,
        eye_name=creature_part_name(RIGHT_EYE_NAME),
        pupil_offset=pupil_offset,
    )


def build_eyes(
    body_center=None,
    *,
    left_pupil_offset=None,
    right_pupil_offset=None,
    assign_group_name: bool = True,
) -> VGroup:
    """
    Build both eyes together.

    Parameters:
        body_center:
            Optional body-center reference passed through anchor helpers.

        left_pupil_offset:
            Optional offset for the left pupil relative to eye center.

        right_pupil_offset:
            Optional offset for the right pupil relative to eye center.

        assign_group_name:
            If True, assign a stable name to the returned eye-pair group.

    Returns:
        VGroup(left_eye, right_eye)
    """
    if LOG_CREATURE_BUILD:
        logger.info("Building both eyes")

    left_eye = build_left_eye(
        body_center=body_center,
        pupil_offset=left_pupil_offset,
    )
    right_eye = build_right_eye(
        body_center=body_center,
        pupil_offset=right_pupil_offset,
    )

    eyes = VGroup(left_eye, right_eye)

    if assign_group_name:
        left_name, right_name = creature_pair_part_names("eye")
        eyes.name = "creature_eyes"
        eyes.left_eye_name = left_name
        eyes.right_eye_name = right_name

    # Lightweight metadata
    eyes.left_eye = left_eye
    eyes.right_eye = right_eye
    eyes.body_center = body_center

    if LOG_CREATURE_BUILD:
        logger.info("Eyes created successfully")

    return eyes