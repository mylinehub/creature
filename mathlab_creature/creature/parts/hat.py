"""
Hat construction for mathlab-mylinehub-creature.

This file builds the creature's triangular hat and places it using
body/head anchor helpers.

Version 1 goals:
- keep the hat simple and iconic
- use a clean triangular silhouette
- optionally include a small brim
- keep all styling controlled by config
- keep placement controlled by anchors

This file only builds the hat object.
It does not animate hat motion yet.
"""

from __future__ import annotations

from manimlib import Polygon, RoundedRectangle, VGroup

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
from mathlab_creature.core.geometry import point
from mathlab_creature.core.layout import place_below
from mathlab_creature.core.logger import get_logger
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


def _validate_positive(name: str, value: float | int) -> float:
    """
    Ensure a positive numeric value.
    """
    value = _validate_numeric(name, value)
    if value <= 0:
        raise ValueError(f"{name} must be > 0, got {value}")
    return value


def _validate_non_negative(name: str, value: float | int) -> float:
    """
    Ensure a non-negative numeric value.
    """
    value = _validate_numeric(name, value)
    if value < 0:
        raise ValueError(f"{name} must be >= 0, got {value}")
    return value


# ============================================================
# Internal builders
# ============================================================

def _build_hat_triangle(
    *,
    width: float = HAT_WIDTH,
    height: float = HAT_HEIGHT,
    fill_color: str = CREATURE_HAT_FILL,
    stroke_color: str = CREATURE_HAT_STROKE,
    stroke_width: float = 2.0,
) -> Polygon:
    """
    Build the main triangular hat shape.

    The triangle is created around the origin first, then moved later
    to the correct anchor position.
    """
    width = _validate_positive("width", width)
    height = _validate_positive("height", height)
    stroke_width = _validate_non_negative("stroke_width", stroke_width)

    half_w = width / 2.0

    top_point = point(0.0, height, 0.0)
    left_base = point(-half_w, 0.0, 0.0)
    right_base = point(half_w, 0.0, 0.0)

    triangle = Polygon(
        left_base,
        top_point,
        right_base,
    )
    triangle.set_fill(fill_color, opacity=1.0)
    triangle.set_stroke(stroke_color, width=stroke_width)

    return triangle


def _build_hat_brim(
    *,
    width: float = HAT_BRIM_WIDTH,
    height: float = HAT_BRIM_HEIGHT,
    fill_color: str = CREATURE_HAT_FILL,
    stroke_color: str = CREATURE_HAT_STROKE,
    stroke_width: float = 2.0,
    corner_radius_ratio: float = 0.45,
) -> RoundedRectangle:
    """
    Build a small brim under the triangular hat.

    This gives the hat a slightly more character-like silhouette without
    making it too complex.
    """
    width = _validate_positive("width", width)
    height = _validate_positive("height", height)
    stroke_width = _validate_non_negative("stroke_width", stroke_width)
    corner_radius_ratio = _validate_non_negative("corner_radius_ratio", corner_radius_ratio)

    brim = RoundedRectangle(
        width=width,
        height=height,
        corner_radius=height * corner_radius_ratio,
    )
    brim.set_fill(fill_color, opacity=1.0)
    brim.set_stroke(stroke_color, width=stroke_width)

    return brim


# ============================================================
# Public builder
# ============================================================

def build_hat(
    body_center=None,
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
    assign_name: bool = True,
) -> VGroup:
    """
    Build the creature hat and place it above the body.

    Args:
        body_center:
            Optional body center point. If omitted, origin-based anchors are used.

        hat_width:
            Width of the triangular hat.

        hat_height:
            Height of the triangular hat.

        brim_width:
            Width of the brim.

        brim_height:
            Height of the brim.

        fill_color:
            Fill color for the hat parts.

        stroke_color:
            Stroke color for the hat parts.

        stroke_width:
            Stroke width for the hat parts.

        include_brim:
            If True, include the brim under the main triangle.

        brim_offset_ratio:
            How far below the base anchor the brim sits, relative to brim height.

        assign_name:
            If True, assign stable names to the group and subparts.

    Returns:
        VGroup containing:
        - triangular hat
        - optional brim
    """
    hat_width = _validate_positive("hat_width", hat_width)
    hat_height = _validate_positive("hat_height", hat_height)
    brim_width = _validate_positive("brim_width", brim_width)
    brim_height = _validate_positive("brim_height", brim_height)
    stroke_width = _validate_non_negative("stroke_width", stroke_width)
    brim_offset_ratio = _validate_non_negative("brim_offset_ratio", brim_offset_ratio)

    if LOG_CREATURE_BUILD:
        logger.info(
            "Building hat | hat_width=%.3f hat_height=%.3f brim_width=%.3f brim_height=%.3f include_brim=%s",
            hat_width,
            hat_height,
            brim_width,
            brim_height,
            include_brim,
        )

    hat_base_center = get_hat_base_center(body_center)

    triangle = _build_hat_triangle(
        width=hat_width,
        height=hat_height,
        fill_color=fill_color,
        stroke_color=stroke_color,
        stroke_width=stroke_width,
    )

    # The triangle is built with its base centered on y=0.
    # Move it so that its base aligns with the hat base anchor.
    triangle.move_to(
        point(
            hat_base_center[0],
            hat_base_center[1] + hat_height / 2.0,
            hat_base_center[2],
        )
    )

    parts = [triangle]

    brim = None
    if include_brim:
        brim = _build_hat_brim(
            width=brim_width,
            height=brim_height,
            fill_color=fill_color,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
        )
        brim.move_to(place_below(hat_base_center, brim_height * brim_offset_ratio))
        parts.append(brim)

    hat = VGroup(*parts)

    if assign_name:
        hat.name = creature_part_name(HAT_NAME)
        triangle.name = "creature_hat_triangle"
        if brim is not None:
            brim.name = "creature_hat_brim"

    # Lightweight metadata for later rigging / motion
    hat.hat_base_center = hat_base_center
    hat.hat_width = hat_width
    hat.hat_height = hat_height
    hat.brim_width = brim_width
    hat.brim_height = brim_height
    hat.include_brim = include_brim
    hat.triangle = triangle
    hat.brim = brim

    if DEBUG_MODE:
        logger.debug(
            "Hat placed | base_center=%s hat_width=%.3f hat_height=%.3f",
            hat_base_center,
            hat_width,
            hat_height,
        )

    if LOG_CREATURE_BUILD:
        logger.info("Hat created successfully")

    return hat