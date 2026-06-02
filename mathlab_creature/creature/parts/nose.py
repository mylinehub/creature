"""
Nose construction for mathlab-mylinehub-creature.

This file builds the creature nose.

Architecture rule:
- nose is a visual face part
- nose does not animate itself
- nose does not move independently
- face_rig.py may later control expressions
- body_m.py will attach nose to the face hierarchy
- audio is not handled here

Connection chain:

    Body
        |
        Face
            |
            Nose
"""

from __future__ import annotations

from typing import Iterable
from typing import Optional

import numpy as np

from manimlib import RoundedRectangle

from mathlab_creature.config.colors import NOSE_FILL
from mathlab_creature.config.colors import NOSE_STROKE
from mathlab_creature.config.defaults import DEBUG_MODE
from mathlab_creature.config.defaults import LOG_CREATURE_BUILD
from mathlab_creature.config.defaults import NOSE_NAME
from mathlab_creature.config.sizes import NOSE_HEIGHT
from mathlab_creature.config.sizes import NOSE_STROKE_WIDTH
from mathlab_creature.config.sizes import NOSE_WIDTH

from mathlab_creature.core.anchors import get_nose_center
from mathlab_creature.core.geometry import as_vec3
from mathlab_creature.core.geometry import point
from mathlab_creature.core.geometry import zero_point
from mathlab_creature.core.logger import get_logger
from mathlab_creature.core.naming import creature_part_name


logger = get_logger(__name__)


Vector3 = np.ndarray
Vec3Like = np.ndarray | Iterable[float]


def _validate_numeric(
    name: str,
    value: float | int,
) -> float:
    if not isinstance(value, (int, float)):
        raise TypeError(
            f"{name} must be numeric, got {type(value).__name__}"
        )
    return float(value)


def _validate_positive(
    name: str,
    value: float | int,
) -> float:
    value = _validate_numeric(name, value)

    if value <= 0:
        raise ValueError(
            f"{name} must be > 0, got {value}"
        )

    return value


def _validate_non_negative(
    name: str,
    value: float | int,
) -> float:
    value = _validate_numeric(name, value)

    if value < 0:
        raise ValueError(
            f"{name} must be >= 0, got {value}"
        )

    return value


def _coerce_point3(
    value: Optional[Vec3Like],
    name: str = "value",
) -> Vector3:
    if value is None:
        return zero_point()

    return as_vec3(
        value,
        name=name,
    )


def build_nose_shape(
    *,
    width: float = NOSE_WIDTH,
    height: float = NOSE_HEIGHT,
    stroke_width: float = NOSE_STROKE_WIDTH,
    fill_color: str = NOSE_FILL,
    stroke_color: str = NOSE_STROKE,
    corner_radius_ratio: float = 0.30,
) -> RoundedRectangle:
    """
    Build raw nose shape.

    Version 1 uses a rounded rectangle.
    """

    width = _validate_positive(
        "width",
        width,
    )

    height = _validate_positive(
        "height",
        height,
    )

    stroke_width = _validate_non_negative(
        "stroke_width",
        stroke_width,
    )

    corner_radius_ratio = _validate_non_negative(
        "corner_radius_ratio",
        corner_radius_ratio,
    )

    corner_radius = (
        min(width, height)
        * corner_radius_ratio
    )

    nose = RoundedRectangle(
        width=width,
        height=height,
        corner_radius=corner_radius,
    )

    nose.set_fill(
        fill_color,
        opacity=1.0,
    )

    nose.set_stroke(
        stroke_color,
        width=stroke_width,
    )

    nose.nose_width = width
    nose.nose_height = height
    nose.nose_corner_radius = corner_radius

    return nose


def build_nose_at(
    position: Optional[Vec3Like] = None,
    *,
    width: float = NOSE_WIDTH,
    height: float = NOSE_HEIGHT,
    stroke_width: float = NOSE_STROKE_WIDTH,
    fill_color: str = NOSE_FILL,
    stroke_color: str = NOSE_STROKE,
    corner_radius_ratio: float = 0.30,
    nose_name: str = "nose",
) -> RoundedRectangle:
    """
    Build nose at an explicit position.
    """

    nose_center = _coerce_point3(
        position,
        "position",
    )

    nose = build_nose_shape(
        width=width,
        height=height,
        stroke_width=stroke_width,
        fill_color=fill_color,
        stroke_color=stroke_color,
        corner_radius_ratio=corner_radius_ratio,
    )

    nose.move_to(
        nose_center,
    )

    nose.name = nose_name

    nose.nose_center = nose_center
    nose.nose_width = width
    nose.nose_height = height
    nose.nose_stroke_width = stroke_width
    nose.nose_corner_radius_ratio = corner_radius_ratio

    nose.is_creature_nose = True

    if DEBUG_MODE:
        logger.debug(
            "Nose placed | center=%s width=%.3f height=%.3f",
            nose_center,
            width,
            height,
        )

    return nose


def build_nose(
    body_center: Optional[Vec3Like] = None,
    *,
    position: Optional[Vec3Like] = None,
    width: float = NOSE_WIDTH,
    height: float = NOSE_HEIGHT,
    stroke_width: float = NOSE_STROKE_WIDTH,
    fill_color: str = NOSE_FILL,
    stroke_color: str = NOSE_STROKE,
    corner_radius_ratio: float = 0.30,
) -> RoundedRectangle:
    """
    Build creature nose.

    If position is supplied,
    it overrides anchor placement.
    """

    if LOG_CREATURE_BUILD:
        logger.info(
            "Building nose"
        )

    nose_center = (
        _coerce_point3(
            position,
            "position",
        )
        if position is not None
        else get_nose_center(
            body_center,
        )
    )

    nose = build_nose_at(
        position=nose_center,
        width=width,
        height=height,
        stroke_width=stroke_width,
        fill_color=fill_color,
        stroke_color=stroke_color,
        corner_radius_ratio=corner_radius_ratio,
        nose_name=creature_part_name(
            NOSE_NAME,
        ),
    )

    if LOG_CREATURE_BUILD:
        logger.info(
            "Nose created successfully"
        )

    return nose


def get_nose_center_point(
    nose: RoundedRectangle,
) -> Vector3:
    """
    Return stored nose center.
    """

    if hasattr(
        nose,
        "nose_center",
    ):
        return as_vec3(
            nose.nose_center,
            name="nose.nose_center",
        )

    return as_vec3(
        nose.get_center(),
        name="nose.get_center()",
    )


def set_nose_center_metadata(
    nose: RoundedRectangle,
    center: Vec3Like,
) -> None:
    """
    Update nose metadata.

    Does not move the object.
    """

    center_vec = as_vec3(
        center,
        name="center",
    )

    nose.nose_center = center_vec


__all__ = [
    "Vector3",
    "Vec3Like",
    "build_nose_shape",
    "build_nose_at",
    "build_nose",
    "get_nose_center_point",
    "set_nose_center_metadata",
]