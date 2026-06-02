"""
Hat construction for mathlab-mylinehub-creature.

This file builds the creature hat.

Architecture rule:
- hat is a visual body/head part
- hat does not animate itself
- hat does not move independently
- body_m.py attaches the hat
- future body_rig.py may animate hat motion
- audio is not handled here

Connection chain:

    Body
        |
        Hat
            |
            Triangle
            Brim
"""

from __future__ import annotations

from typing import Iterable
from typing import Optional

import numpy as np

from manimlib import Polygon
from manimlib import RoundedRectangle
from manimlib import VGroup

from mathlab_creature.config.colors import CREATURE_HAT_FILL
from mathlab_creature.config.colors import CREATURE_HAT_STROKE
from mathlab_creature.config.defaults import DEBUG_MODE
from mathlab_creature.config.defaults import HAT_NAME
from mathlab_creature.config.defaults import LOG_CREATURE_BUILD
from mathlab_creature.config.sizes import HAT_BRIM_HEIGHT
from mathlab_creature.config.sizes import HAT_BRIM_WIDTH
from mathlab_creature.config.sizes import HAT_HEIGHT
from mathlab_creature.config.sizes import HAT_WIDTH

from mathlab_creature.core.anchors import get_hat_base_center
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


def build_hat_triangle(
    *,
    width: float = HAT_WIDTH,
    height: float = HAT_HEIGHT,
    fill_color: str = CREATURE_HAT_FILL,
    stroke_color: str = CREATURE_HAT_STROKE,
    stroke_width: float = 2.0,
) -> Polygon:
    """
    Build raw triangular hat.
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

    half_width = width / 2.0

    triangle = Polygon(
        point(-half_width, 0.0, 0.0),
        point(0.0, height, 0.0),
        point(half_width, 0.0, 0.0),
    )

    triangle.set_fill(
        fill_color,
        opacity=1.0,
    )

    triangle.set_stroke(
        stroke_color,
        width=stroke_width,
    )

    return triangle


def build_hat_brim(
    *,
    width: float = HAT_BRIM_WIDTH,
    height: float = HAT_BRIM_HEIGHT,
    fill_color: str = CREATURE_HAT_FILL,
    stroke_color: str = CREATURE_HAT_STROKE,
    stroke_width: float = 2.0,
    corner_radius_ratio: float = 0.45,
) -> RoundedRectangle:
    """
    Build raw hat brim.
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

    brim = RoundedRectangle(
        width=width,
        height=height,
        corner_radius=height * corner_radius_ratio,
    )

    brim.set_fill(
        fill_color,
        opacity=1.0,
    )

    brim.set_stroke(
        stroke_color,
        width=stroke_width,
    )

    return brim


def build_hat_at(
    position: Optional[Vec3Like] = None,
    *,
    hat_width: float = HAT_WIDTH,
    hat_height: float = HAT_HEIGHT,
    brim_width: float = HAT_BRIM_WIDTH,
    brim_height: float = HAT_BRIM_HEIGHT,
    fill_color: str = CREATURE_HAT_FILL,
    stroke_color: str = CREATURE_HAT_STROKE,
    stroke_width: float = 2.0,
    include_brim: bool = True,
    brim_offset_ratio: float = 0.35,
    hat_name: str = "hat",
) -> VGroup:
    """
    Build hat at explicit position.
    """

    hat_base_center = _coerce_point3(
        position,
        "position",
    )

    triangle = build_hat_triangle(
        width=hat_width,
        height=hat_height,
        fill_color=fill_color,
        stroke_color=stroke_color,
        stroke_width=stroke_width,
    )

    triangle.move_to(
        point(
            hat_base_center[0],
            hat_base_center[1] + (hat_height / 2.0),
            hat_base_center[2],
        )
    )

    parts = [triangle]

    brim = None

    if include_brim:
        brim = build_hat_brim(
            width=brim_width,
            height=brim_height,
            fill_color=fill_color,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
        )

        brim.move_to(
            point(
                hat_base_center[0],
                hat_base_center[1]
                - (brim_height * brim_offset_ratio),
                hat_base_center[2],
            )
        )

        parts.append(brim)

    hat = VGroup(*parts)

    hat.name = hat_name

    hat.triangle = triangle
    hat.brim = brim

    hat.hat_base_center = hat_base_center

    hat.hat_width = hat_width
    hat.hat_height = hat_height

    hat.brim_width = brim_width
    hat.brim_height = brim_height

    hat.include_brim = include_brim

    hat.is_creature_hat = True

    return hat


def build_hat(
    body_center: Optional[Vec3Like] = None,
    *,
    position: Optional[Vec3Like] = None,
    hat_width: float = HAT_WIDTH,
    hat_height: float = HAT_HEIGHT,
    brim_width: float = HAT_BRIM_WIDTH,
    brim_height: float = HAT_BRIM_HEIGHT,
    fill_color: str = CREATURE_HAT_FILL,
    stroke_color: str = CREATURE_HAT_STROKE,
    stroke_width: float = 2.0,
    include_brim: bool = True,
    brim_offset_ratio: float = 0.35,
) -> VGroup:
    """
    Build creature hat.

    If position is supplied,
    it overrides anchor placement.
    """

    if LOG_CREATURE_BUILD:
        logger.info(
            "Building hat"
        )

    hat_base_center = (
        _coerce_point3(
            position,
            "position",
        )
        if position is not None
        else get_hat_base_center(
            body_center,
        )
    )

    hat = build_hat_at(
        position=hat_base_center,
        hat_width=hat_width,
        hat_height=hat_height,
        brim_width=brim_width,
        brim_height=brim_height,
        fill_color=fill_color,
        stroke_color=stroke_color,
        stroke_width=stroke_width,
        include_brim=include_brim,
        brim_offset_ratio=brim_offset_ratio,
        hat_name=creature_part_name(
            HAT_NAME,
        ),
    )

    if DEBUG_MODE:
        logger.debug(
            "Hat placed | base_center=%s",
            hat_base_center,
        )

    if LOG_CREATURE_BUILD:
        logger.info(
            "Hat created successfully"
        )

    return hat


def get_hat_base_point(
    hat: VGroup,
) -> Vector3:
    """
    Return stored hat base center.
    """

    if hasattr(
        hat,
        "hat_base_center",
    ):
        return as_vec3(
            hat.hat_base_center,
            name="hat.hat_base_center",
        )

    return as_vec3(
        hat.get_center(),
        name="hat.get_center()",
    )


def set_hat_base_metadata(
    hat: VGroup,
    center: Vec3Like,
) -> None:
    """
    Update hat metadata.

    Does not move the object.
    """

    center_vec = as_vec3(
        center,
        name="center",
    )

    hat.hat_base_center = center_vec


__all__ = [
    "Vector3",
    "Vec3Like",
    "build_hat_triangle",
    "build_hat_brim",
    "build_hat_at",
    "build_hat",
    "get_hat_base_point",
    "set_hat_base_metadata",
]