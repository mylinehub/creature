"""
Mouth construction for mathlab-mylinehub-creature.

This file builds the creature mouth.

Architecture rule:
- mouth is a visual face part
- mouth does not animate itself
- mouth does not move independently
- face_rig.py may later control expressions
- body_m.py will attach mouth to the face hierarchy
- audio is not handled here

Connection chain:

    Body
        |
        Face
            |
            Mouth
"""

from __future__ import annotations

from typing import Iterable
from typing import Optional

import numpy as np

from manimlib import Arc

from mathlab_creature.config.colors import MOUTH_COLOR
from mathlab_creature.config.defaults import DEBUG_MODE
from mathlab_creature.config.defaults import LOG_CREATURE_BUILD
from mathlab_creature.config.defaults import MOUTH_NAME
from mathlab_creature.config.sizes import MOUTH_HEIGHT
from mathlab_creature.config.sizes import MOUTH_STROKE_WIDTH
from mathlab_creature.config.sizes import MOUTH_WIDTH
from mathlab_creature.config.sizes import SMILE_ARC_ANGLE

from mathlab_creature.core.anchors import get_mouth_center
from mathlab_creature.core.geometry import as_vec3
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


def build_mouth_shape(
    *,
    width: float = MOUTH_WIDTH,
    height: float = MOUTH_HEIGHT,
    stroke_width: float = MOUTH_STROKE_WIDTH,
    stroke_color: str = MOUTH_COLOR,
    arc_angle: float = SMILE_ARC_ANGLE,
) -> Arc:
    """
    Build raw mouth shape.

    Version 1 uses a friendly smile arc.
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

    arc_angle = _validate_positive(
        "arc_angle",
        arc_angle,
    )

    mouth = Arc(
        angle=arc_angle,
    )

    mouth.set_width(width)
    mouth.set_height(height)

    mouth.set_stroke(
        stroke_color,
        width=stroke_width,
    )

    mouth.mouth_width = width
    mouth.mouth_height = height
    mouth.mouth_arc_angle = arc_angle

    return mouth


def build_mouth_at(
    position: Optional[Vec3Like] = None,
    *,
    width: float = MOUTH_WIDTH,
    height: float = MOUTH_HEIGHT,
    stroke_width: float = MOUTH_STROKE_WIDTH,
    stroke_color: str = MOUTH_COLOR,
    arc_angle: float = SMILE_ARC_ANGLE,
    mouth_name: str = "mouth",
) -> Arc:
    """
    Build mouth at explicit position.
    """

    mouth_center = _coerce_point3(
        position,
        "position",
    )

    mouth = build_mouth_shape(
        width=width,
        height=height,
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        arc_angle=arc_angle,
    )

    mouth.move_to(
        mouth_center,
    )

    mouth.name = mouth_name

    mouth.mouth_center = mouth_center
    mouth.mouth_width = width
    mouth.mouth_height = height
    mouth.mouth_stroke_width = stroke_width
    mouth.mouth_arc_angle = arc_angle

    mouth.is_creature_mouth = True

    if DEBUG_MODE:
        logger.debug(
            "Mouth placed | center=%s width=%.3f height=%.3f arc_angle=%.3f",
            mouth_center,
            width,
            height,
            arc_angle,
        )

    return mouth


def build_mouth(
    body_center: Optional[Vec3Like] = None,
    *,
    position: Optional[Vec3Like] = None,
    width: float = MOUTH_WIDTH,
    height: float = MOUTH_HEIGHT,
    stroke_width: float = MOUTH_STROKE_WIDTH,
    stroke_color: str = MOUTH_COLOR,
    arc_angle: float = SMILE_ARC_ANGLE,
) -> Arc:
    """
    Build creature mouth.

    If position is supplied,
    it overrides anchor placement.
    """

    if LOG_CREATURE_BUILD:
        logger.info(
            "Building mouth"
        )

    mouth_center = (
        _coerce_point3(
            position,
            "position",
        )
        if position is not None
        else get_mouth_center(
            body_center,
        )
    )

    mouth = build_mouth_at(
        position=mouth_center,
        width=width,
        height=height,
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        arc_angle=arc_angle,
        mouth_name=creature_part_name(
            MOUTH_NAME,
        ),
    )

    if LOG_CREATURE_BUILD:
        logger.info(
            "Mouth created successfully"
        )

    return mouth


def get_mouth_center_point(
    mouth: Arc,
) -> Vector3:
    """
    Return stored mouth center.
    """

    if hasattr(
        mouth,
        "mouth_center",
    ):
        return as_vec3(
            mouth.mouth_center,
            name="mouth.mouth_center",
        )

    return as_vec3(
        mouth.get_center(),
        name="mouth.get_center()",
    )


def set_mouth_center_metadata(
    mouth: Arc,
    center: Vec3Like,
) -> None:
    """
    Update mouth metadata.

    Does not move the object.
    """

    center_vec = as_vec3(
        center,
        name="center",
    )

    mouth.mouth_center = center_vec


def set_mouth_smile_amount(
    mouth: Arc,
    arc_angle: float,
) -> None:
    """
    Store future smile state.

    Actual expression animation
    will later be handled by face_rig.py.
    """

    mouth.mouth_arc_angle = float(
        arc_angle,
    )


__all__ = [
    "Vector3",
    "Vec3Like",
    "build_mouth_shape",
    "build_mouth_at",
    "build_mouth",
    "get_mouth_center_point",
    "set_mouth_center_metadata",
    "set_mouth_smile_amount",
]