"""
Body M construction for mathlab-mylinehub-creature.

This file creates the base M-shaped body of the mascot.

Version 1 approach:
- Use a clean, geometric "M" built from strokes (Line objects)
- Keep it readable and adjustable
- Use config for sizes and colors
- Return a grouped VGroup so other parts can attach easily

Later we can upgrade to:
- curved / stylized M
- SVG-based M
- thicker filled shapes

But first we build a strong geometric base.
"""

from __future__ import annotations

from manimlib import Line, VGroup

from config.colors import CREATURE_BODY_STROKE
from config.defaults import BODY_NAME
from config.defaults import DEBUG_MODE
from config.defaults import LOG_CREATURE_BUILD
from config.sizes import BODY_M_HEIGHT
from config.sizes import BODY_M_STROKE_WIDTH
from config.sizes import BODY_M_WIDTH
from core.geometry import point
from core.logger import get_logger
from core.naming import creature_part_name

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
    Ensure a positive numeric value and return it as float.
    """
    value = _validate_numeric(name, value)
    if value <= 0:
        raise ValueError(f"{name} must be > 0, got {value}")
    return value


def _coerce_center(center: tuple[float, float, float] | None) -> tuple[float, float, float]:
    """
    Normalize an optional center tuple.
    """
    if center is None:
        return (0.0, 0.0, 0.0)

    if not isinstance(center, (tuple, list)) or len(center) != 3:
        raise TypeError("center must be None or a 3-item tuple/list")

    return (
        float(center[0]),
        float(center[1]),
        float(center[2]),
    )


def _build_m_points(
    width: float,
    height: float,
    center: tuple[float, float, float],
) -> dict[str, object]:
    """
    Build the key points used to construct the M body.

    The shape is a clean, symmetric geometric M with:
    - two outer vertical legs
    - two upper-to-inner diagonals
    - one inner valley connection
    """
    cx, cy, cz = center

    half_w = width / 2.0
    half_h = height / 2.0

    # Outer boundary points
    p_bottom_left = point(cx - half_w, cy - half_h, cz)
    p_top_left = point(cx - half_w, cy + half_h, cz)

    p_top_right = point(cx + half_w, cy + half_h, cz)
    p_bottom_right = point(cx + half_w, cy - half_h, cz)

    # Inner top shoulders of the M.
    # These control how wide the center valley is.
    inner_shoulder_x = half_w * 0.32
    inner_shoulder_y = cy + half_h * 0.18

    # Valley point controls the central dip of the M.
    valley_y = cy - half_h * 0.28

    p_inner_top_left = point(cx - inner_shoulder_x, inner_shoulder_y, cz)
    p_inner_valley = point(cx, valley_y, cz)
    p_inner_top_right = point(cx + inner_shoulder_x, inner_shoulder_y, cz)

    return {
        "half_width": half_w,
        "half_height": half_h,
        "bottom_left": p_bottom_left,
        "top_left": p_top_left,
        "inner_top_left": p_inner_top_left,
        "inner_valley": p_inner_valley,
        "inner_top_right": p_inner_top_right,
        "top_right": p_top_right,
        "bottom_right": p_bottom_right,
    }


def _style_line(line: Line, stroke_color: str, stroke_width: float) -> Line:
    """
    Apply consistent styling to one M-body stroke segment.
    """
    line.set_stroke(
        color=stroke_color,
        width=stroke_width,
    )
    return line


# ============================================================
# Public builder
# ============================================================

def build_body_m(
    *,
    width: float = BODY_M_WIDTH,
    height: float = BODY_M_HEIGHT,
    stroke_width: float = BODY_M_STROKE_WIDTH,
    stroke_color: str = CREATURE_BODY_STROKE,
    center: tuple[float, float, float] | None = None,
    scale_factor: float = 1.0,
    assign_subpart_names: bool = True,
) -> VGroup:
    """
    Build the M-shaped body.

    Parameters:
        width:
            Base width of the M body bounding zone.

        height:
            Base height of the M body bounding zone.

        stroke_width:
            Stroke width used for each line segment.

        stroke_color:
            Color of the body strokes.

        center:
            Optional center position for constructing the M.

        scale_factor:
            Optional uniform scale multiplier applied after construction.

        assign_subpart_names:
            If True, assign stable names to the main VGroup and segment lines.

    Returns:
        VGroup containing all stroke segments of the M.
    """
    width = _validate_positive("width", width)
    height = _validate_positive("height", height)
    stroke_width = _validate_positive("stroke_width", stroke_width)
    scale_factor = _validate_positive("scale_factor", scale_factor)
    center = _coerce_center(center)

    if LOG_CREATURE_BUILD:
        logger.info(
            "Building M body | width=%.3f height=%.3f stroke_width=%.3f scale_factor=%.3f center=%s",
            width,
            height,
            stroke_width,
            scale_factor,
            center,
        )

    # --------------------------------------------------------
    # Define key points of the M
    # --------------------------------------------------------
    points = _build_m_points(
        width=width,
        height=height,
        center=center,
    )

    p_bottom_left = points["bottom_left"]
    p_top_left = points["top_left"]
    p_inner_top_left = points["inner_top_left"]
    p_inner_valley = points["inner_valley"]
    p_inner_top_right = points["inner_top_right"]
    p_top_right = points["top_right"]
    p_bottom_right = points["bottom_right"]

    # --------------------------------------------------------
    # Create line segments
    # --------------------------------------------------------
    #
    # Structure:
    #
    #   top_left ----\      /---- top_right
    #                 \    /
    #           inner_top_left  inner_top_right
    #                    \    /
    #                     \  /
    #                    valley
    #
    # with outer vertical legs on both sides.

    left_leg = Line(p_bottom_left, p_top_left)
    left_inner_diag = Line(p_top_left, p_inner_valley)
    right_inner_diag = Line(p_inner_valley, p_top_right)
    right_leg = Line(p_top_right, p_bottom_right)

    # Optional shoulder accents to make the M silhouette read more clearly.
    # These are short connectors that slightly strengthen the top inner shape.
    left_shoulder = Line(p_top_left, p_inner_top_left)
    right_shoulder = Line(p_inner_top_right, p_top_right)

    segments = [
        left_leg,
        left_shoulder,
        left_inner_diag,
        right_inner_diag,
        right_shoulder,
        right_leg,
    ]

    # --------------------------------------------------------
    # Apply styling
    # --------------------------------------------------------
    for segment in segments:
        _style_line(
            segment,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
        )

    # --------------------------------------------------------
    # Group everything
    # --------------------------------------------------------
    body = VGroup(*segments)

    # --------------------------------------------------------
    # Optional scaling
    # --------------------------------------------------------
    if scale_factor != 1.0:
        body.scale(scale_factor)

    # --------------------------------------------------------
    # Optional stable naming
    # --------------------------------------------------------
    if assign_subpart_names:
        body.name = creature_part_name(BODY_NAME)

        left_leg.name = "body_m_left_leg"
        left_shoulder.name = "body_m_left_shoulder"
        left_inner_diag.name = "body_m_left_inner_diag"
        right_inner_diag.name = "body_m_right_inner_diag"
        right_shoulder.name = "body_m_right_shoulder"
        right_leg.name = "body_m_right_leg"

    # --------------------------------------------------------
    # Debug metadata
    # --------------------------------------------------------
    #
    # These attributes are lightweight and useful later for:
    # - anchor debugging
    # - test scenes
    # - rigging experiments
    # - visual verification
    body.body_width = width
    body.body_height = height
    body.body_stroke_width = stroke_width
    body.body_center = center
    body.body_points = points

    if DEBUG_MODE:
        logger.debug(
            "M body points prepared | top_left=%s valley=%s top_right=%s",
            p_top_left,
            p_inner_valley,
            p_top_right,
        )

    if LOG_CREATURE_BUILD:
        logger.info("M body created successfully")

    return body