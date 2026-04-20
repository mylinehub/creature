"""
Main creature assembly for mathlab-mylinehub-creature.

This file builds the full MYLINEHUB M mascot by combining:

- body (M shape)
- eyes
- nose
- mouth
- hat

Version 1 goals:
- clean assembly
- no hardcoded positioning
- all parts aligned via anchors
- return a single grouped object
- easy to scale / move later

This is the first "complete character".
"""

from __future__ import annotations

import numpy as np
from manimlib import VGroup

from mathlab_creature.creature.parts.body_m import build_body_m
from mathlab_creature.creature.parts.eyes import build_eyes
from mathlab_creature.creature.parts.hat import build_hat
from mathlab_creature.creature.parts.mouth import build_mouth
from mathlab_creature.creature.parts.nose import build_nose

from mathlab_creature.config.defaults import CREATURE_NAME
from mathlab_creature.config.defaults import DEBUG_MODE
from mathlab_creature.config.defaults import DEFAULT_CREATURE_SCALE
from mathlab_creature.config.defaults import LOG_CREATURE_BUILD
from mathlab_creature.core.geometry import point
from mathlab_creature.core.logger import get_logger
from mathlab_creature.core.naming import clean_name

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


def _validate_positive(name: str, value: float | int) -> float:
    """
    Ensure a positive numeric value.
    """
    value = _validate_numeric(name, value)
    if value <= 0:
        raise ValueError(f"{name} must be > 0, got {value}")
    return value


def _coerce_body_center(body_center=None) -> np.ndarray:
    """
    Normalize body_center into a clean 3D point.

    Accepted:
    - None
    - numpy.ndarray with shape (3,)
    - tuple/list with 3 numeric values
    """
    if body_center is None:
        return point(0.0, 0.0, 0.0)

    if isinstance(body_center, np.ndarray):
        if body_center.shape != (3,):
            raise ValueError(f"body_center must have shape (3,), got {body_center.shape}")
        return body_center.astype(float)

    if isinstance(body_center, (tuple, list)):
        if len(body_center) != 3:
            raise ValueError(
                f"body_center must contain exactly 3 values, got {len(body_center)}"
            )
        return point(body_center[0], body_center[1], body_center[2])

    raise TypeError(
        "body_center must be None, a numpy.ndarray of shape (3,), "
        "or a 3-item tuple/list"
    )


# ============================================================
# Main builder
# ============================================================

def build_myline_m_creature(
    body_center=None,
    *,
    scale_factor: float = DEFAULT_CREATURE_SCALE,
    include_body: bool = True,
    include_eyes: bool = True,
    include_nose: bool = True,
    include_mouth: bool = True,
    include_hat: bool = True,
    assign_name: bool = True,
) -> VGroup:
    """
    Build the complete MYLINEHUB M creature.

    Args:
        body_center:
            Optional center point for the creature.
            Default is origin.

        scale_factor:
            Uniform scale applied after assembly.

        include_body:
            If True, include the M body.

        include_eyes:
            If True, include both eyes.

        include_nose:
            If True, include the nose.

        include_mouth:
            If True, include the mouth.

        include_hat:
            If True, include the hat.

        assign_name:
            If True, assign a stable name to the final creature group.

    Returns:
        VGroup containing the assembled creature.
    """
    scale_factor = _validate_positive("scale_factor", scale_factor)
    body_center = _coerce_body_center(body_center)

    if LOG_CREATURE_BUILD:
        logger.info(
            "Starting creature assembly | center=%s scale_factor=%.3f body=%s eyes=%s nose=%s mouth=%s hat=%s",
            body_center,
            scale_factor,
            include_body,
            include_eyes,
            include_nose,
            include_mouth,
            include_hat,
        )

    parts: list = []

    # --------------------------------------------------------
    # Build base body
    # --------------------------------------------------------
    body = None
    if include_body:
        body = build_body_m(
            center=(body_center[0], body_center[1], body_center[2]),
        )
        parts.append(body)

        if LOG_CREATURE_BUILD:
            logger.info("Body built")

    # --------------------------------------------------------
    # Build face components
    # --------------------------------------------------------
    eyes = None
    nose = None
    mouth = None

    if include_eyes:
        eyes = build_eyes(body_center=body_center)
        parts.append(eyes)

    if include_nose:
        nose = build_nose(body_center=body_center)
        parts.append(nose)

    if include_mouth:
        mouth = build_mouth(body_center=body_center)
        parts.append(mouth)

    if LOG_CREATURE_BUILD and (include_eyes or include_nose or include_mouth):
        logger.info("Face components built")

    # --------------------------------------------------------
    # Build hat
    # --------------------------------------------------------
    hat = None
    if include_hat:
        hat = build_hat(body_center=body_center)
        parts.append(hat)

        if LOG_CREATURE_BUILD:
            logger.info("Hat built")

    # --------------------------------------------------------
    # Assemble creature
    # --------------------------------------------------------
    creature = VGroup(*parts)

    # --------------------------------------------------------
    # Apply default scale
    # --------------------------------------------------------
    if scale_factor != 1.0:
        creature.scale(scale_factor)

    # --------------------------------------------------------
    # Stable naming
    # --------------------------------------------------------
    if assign_name:
        creature.name = clean_name(CREATURE_NAME)

    # --------------------------------------------------------
    # Lightweight metadata
    # --------------------------------------------------------
    creature.creature_name = CREATURE_NAME
    creature.body_center = body_center
    creature.scale_factor = scale_factor

    creature.body = body
    creature.eyes = eyes
    creature.nose = nose
    creature.mouth = mouth
    creature.hat = hat

    creature.include_body = include_body
    creature.include_eyes = include_eyes
    creature.include_nose = include_nose
    creature.include_mouth = include_mouth
    creature.include_hat = include_hat

    if DEBUG_MODE:
        logger.debug(
            "Creature metadata | parts=%d center=%s scale_factor=%.3f",
            len(parts),
            body_center,
            scale_factor,
        )

    if LOG_CREATURE_BUILD:
        logger.info("Creature assembly completed")

    return creature