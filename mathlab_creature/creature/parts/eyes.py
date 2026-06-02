"""
Eye construction for mathlab-mylinehub-creature.

This file builds the creature's eye parts:
- left eye white
- right eye white
- left pupil
- right pupil
- pupil highlights

Architecture rule:
- eyes are visual parts only
- eyes do not animate themselves
- eyes do not move independently in scene code
- pupils may move locally inside the eye group
- blink/look actions will control eyes later
- audio is not handled here

Connection chain:

    Body / Head / FaceRig
        |
        Eyes
            |
            Eye white
            Pupil
            Highlight
"""

from __future__ import annotations

from typing import Iterable
from typing import Optional

import numpy as np

from manimlib import Circle
from manimlib import VGroup

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
from mathlab_creature.core.geometry import as_vec3
from mathlab_creature.core.geometry import clamp
from mathlab_creature.core.geometry import point
from mathlab_creature.core.geometry import zero_point
from mathlab_creature.core.logger import get_logger
from mathlab_creature.core.naming import creature_pair_part_names
from mathlab_creature.core.naming import creature_part_name


logger = get_logger(__name__)


Vector3 = np.ndarray
Vec3Like = np.ndarray | Iterable[float]


def _validate_numeric(name: str, value: float | int) -> float:
    if not isinstance(value, (int, float)):
        raise TypeError(
            f"{name} must be numeric, got {type(value).__name__}"
        )
    return float(value)


def _validate_positive(name: str, value: float | int) -> float:
    value = _validate_numeric(name, value)
    if value <= 0:
        raise ValueError(f"{name} must be > 0, got {value}")
    return value


def _validate_non_negative(name: str, value: float | int) -> float:
    value = _validate_numeric(name, value)
    if value < 0:
        raise ValueError(f"{name} must be >= 0, got {value}")
    return value


def _coerce_point3(
    value: Optional[Vec3Like],
    name: str = "value",
) -> Vector3:
    if value is None:
        return zero_point()

    return as_vec3(value, name=name)


def _offset_point(
    base_point: Vec3Like,
    dx: float,
    dy: float,
    dz: float = 0.0,
) -> Vector3:
    base = _coerce_point3(base_point, "base_point")

    return point(
        base[0] + _validate_numeric("dx", dx),
        base[1] + _validate_numeric("dy", dy),
        base[2] + _validate_numeric("dz", dz),
    )


def _coerce_pupil_offset(
    pupil_offset: Optional[Vec3Like] = None,
) -> Vector3:
    """
    Normalize and clamp optional pupil offset.
    """
    if pupil_offset is None:
        return zero_point()

    offset_vec = _coerce_point3(
        pupil_offset,
        "pupil_offset",
    )

    clamped_x = clamp(
        offset_vec[0],
        -PUPIL_MAX_OFFSET,
        PUPIL_MAX_OFFSET,
    )
    clamped_y = clamp(
        offset_vec[1],
        -PUPIL_MAX_OFFSET,
        PUPIL_MAX_OFFSET,
    )

    return point(
        clamped_x,
        clamped_y,
        offset_vec[2],
    )


def build_eye_white(
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
    width = _validate_positive("width", width)
    height = _validate_positive("height", height)
    stroke_width = _validate_non_negative("stroke_width", stroke_width)

    eye = Circle()
    eye.set_width(width)
    eye.set_height(height)
    eye.set_fill(fill_color, opacity=1.0)
    eye.set_stroke(stroke_color, width=stroke_width)

    eye.eye_width = width
    eye.eye_height = height

    return eye


def build_pupil(
    *,
    radius: float = PUPIL_RADIUS,
    fill_color: str = PUPIL_FILL,
) -> Circle:
    """
    Build one pupil.
    """
    radius = _validate_positive("radius", radius)

    pupil = Circle(radius=radius)
    pupil.set_fill(fill_color, opacity=1.0)
    pupil.set_stroke(fill_color, width=0)

    pupil.pupil_radius = radius

    return pupil


def build_pupil_highlight(
    *,
    pupil_radius: float = PUPIL_RADIUS,
    fill_color: str = PUPIL_HIGHLIGHT,
) -> Circle:
    """
    Build small pupil highlight.
    """
    pupil_radius = _validate_positive("pupil_radius", pupil_radius)

    highlight = Circle(radius=pupil_radius * 0.28)
    highlight.set_fill(fill_color, opacity=1.0)
    highlight.set_stroke(fill_color, width=0)

    return highlight


def build_eye_at(
    center: Optional[Vec3Like] = None,
    *,
    eye_name: str = "eye",
    pupil_offset: Optional[Vec3Like] = None,
    eye_width: float = EYE_WIDTH,
    eye_height: float = EYE_HEIGHT,
    eye_stroke_width: float = EYE_STROKE_WIDTH,
    pupil_radius: float = PUPIL_RADIUS,
) -> VGroup:
    """
    Build one complete eye group at a supplied center.

    Structure:
    - eye white
    - pupil
    - highlight
    """
    center_point = _coerce_point3(center, "center")
    pupil_offset_vec = _coerce_pupil_offset(pupil_offset)

    eye_white = build_eye_white(
        width=eye_width,
        height=eye_height,
        stroke_width=eye_stroke_width,
    )
    pupil = build_pupil(
        radius=pupil_radius,
    )
    highlight = build_pupil_highlight(
        pupil_radius=pupil_radius,
    )

    eye_white.move_to(center_point)

    pupil_center = _offset_point(
        center_point,
        pupil_offset_vec[0],
        pupil_offset_vec[1],
        pupil_offset_vec[2],
    )
    pupil.move_to(pupil_center)

    highlight.move_to(
        _offset_point(
            pupil_center,
            -(pupil_radius * 0.28),
            pupil_radius * 0.28,
            0.0,
        )
    )

    eye_group = VGroup(
        eye_white,
        pupil,
        highlight,
    )

    eye_group.name = eye_name
    eye_white.name = f"{eye_name}_white"
    pupil.name = f"{eye_name}_pupil"
    highlight.name = f"{eye_name}_highlight"

    eye_group.eye_white = eye_white
    eye_group.pupil = pupil
    eye_group.highlight = highlight

    eye_group.eye_center = center_point
    eye_group.pupil_center = pupil_center
    eye_group.pupil_offset = pupil_offset_vec

    eye_group.eye_width = eye_width
    eye_group.eye_height = eye_height
    eye_group.pupil_radius = pupil_radius

    eye_group.is_creature_eye = True

    if DEBUG_MODE:
        logger.debug(
            "Built eye group | name=%s center=%s pupil_offset=%s",
            eye_name,
            center_point,
            pupil_offset_vec,
        )

    return eye_group


def set_eye_pupil_offset(
    eye_group: VGroup,
    pupil_offset: Optional[Vec3Like] = None,
) -> None:
    """
    Move pupil locally inside an existing eye group.

    This is used later by look_action.py / face_rig.py.
    """
    offset_vec = _coerce_pupil_offset(pupil_offset)

    if not hasattr(eye_group, "eye_center"):
        raise AttributeError("eye_group must have eye_center metadata")

    if not hasattr(eye_group, "pupil"):
        raise AttributeError("eye_group must have pupil metadata")

    if not hasattr(eye_group, "highlight"):
        raise AttributeError("eye_group must have highlight metadata")

    pupil_radius = getattr(
        eye_group,
        "pupil_radius",
        PUPIL_RADIUS,
    )

    pupil_center = _offset_point(
        eye_group.eye_center,
        offset_vec[0],
        offset_vec[1],
        offset_vec[2],
    )

    eye_group.pupil.move_to(pupil_center)
    eye_group.highlight.move_to(
        _offset_point(
            pupil_center,
            -(pupil_radius * 0.28),
            pupil_radius * 0.28,
            0.0,
        )
    )

    eye_group.pupil_center = pupil_center
    eye_group.pupil_offset = offset_vec


def reset_eye_pupil(
    eye_group: VGroup,
) -> None:
    """
    Reset pupil to eye center.
    """
    set_eye_pupil_offset(
        eye_group,
        zero_point(),
    )


def build_left_eye(
    body_center: Optional[Vec3Like] = None,
    *,
    position: Optional[Vec3Like] = None,
    pupil_offset: Optional[Vec3Like] = None,
) -> VGroup:
    """
    Build left eye group.

    If position is supplied, it is used directly.
    Otherwise anchor helper decides position from body_center.
    """
    if LOG_CREATURE_BUILD:
        logger.info("Building left eye")

    left_eye_center = (
        _coerce_point3(position, "position")
        if position is not None
        else get_left_eye_center(body_center)
    )

    eye = build_eye_at(
        center=left_eye_center,
        eye_name=creature_part_name(LEFT_EYE_NAME),
        pupil_offset=pupil_offset,
    )

    eye.side = "left"

    return eye


def build_right_eye(
    body_center: Optional[Vec3Like] = None,
    *,
    position: Optional[Vec3Like] = None,
    pupil_offset: Optional[Vec3Like] = None,
) -> VGroup:
    """
    Build right eye group.

    If position is supplied, it is used directly.
    Otherwise anchor helper decides position from body_center.
    """
    if LOG_CREATURE_BUILD:
        logger.info("Building right eye")

    right_eye_center = (
        _coerce_point3(position, "position")
        if position is not None
        else get_right_eye_center(body_center)
    )

    eye = build_eye_at(
        center=right_eye_center,
        eye_name=creature_part_name(RIGHT_EYE_NAME),
        pupil_offset=pupil_offset,
    )

    eye.side = "right"

    return eye


def build_eyes(
    body_center: Optional[Vec3Like] = None,
    *,
    left_position: Optional[Vec3Like] = None,
    right_position: Optional[Vec3Like] = None,
    left_pupil_offset: Optional[Vec3Like] = None,
    right_pupil_offset: Optional[Vec3Like] = None,
    assign_group_name: bool = True,
) -> VGroup:
    """
    Build both eyes together.

    Returns:
        VGroup(left_eye, right_eye)
    """
    if LOG_CREATURE_BUILD:
        logger.info("Building both eyes")

    left_eye = build_left_eye(
        body_center=body_center,
        position=left_position,
        pupil_offset=left_pupil_offset,
    )

    right_eye = build_right_eye(
        body_center=body_center,
        position=right_position,
        pupil_offset=right_pupil_offset,
    )

    eyes = VGroup(
        left_eye,
        right_eye,
    )

    if assign_group_name:
        left_name, right_name = creature_pair_part_names("eye")
        eyes.name = "creature_eyes"
        eyes.left_eye_name = left_name
        eyes.right_eye_name = right_name

    eyes.left_eye = left_eye
    eyes.right_eye = right_eye
    eyes.body_center = body_center
    eyes.is_creature_eyes_group = True

    if LOG_CREATURE_BUILD:
        logger.info("Eyes created successfully")

    return eyes


def set_eyes_pupil_offset(
    eyes: VGroup,
    left_offset: Optional[Vec3Like] = None,
    right_offset: Optional[Vec3Like] = None,
) -> None:
    """
    Move both pupils locally.

    Used later by look_action.py / face_rig.py.
    """
    if not hasattr(eyes, "left_eye") or not hasattr(eyes, "right_eye"):
        raise AttributeError("eyes group must have left_eye and right_eye metadata")

    set_eye_pupil_offset(
        eyes.left_eye,
        left_offset,
    )
    set_eye_pupil_offset(
        eyes.right_eye,
        right_offset,
    )


def reset_eyes_pupils(
    eyes: VGroup,
) -> None:
    """
    Reset both pupils to center.
    """
    set_eyes_pupil_offset(
        eyes,
        zero_point(),
        zero_point(),
    )


__all__ = [
    "Vector3",
    "Vec3Like",
    "build_eye_white",
    "build_pupil",
    "build_pupil_highlight",
    "build_eye_at",
    "set_eye_pupil_offset",
    "reset_eye_pupil",
    "build_left_eye",
    "build_right_eye",
    "build_eyes",
    "set_eyes_pupil_offset",
    "reset_eyes_pupils",
]