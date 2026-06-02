"""
Body M construction for mathlab-mylinehub-creature.

This file builds the connected visible creature body.

Architecture rule:
- body_m.py is the main visible assembly part
- it builds the M-shaped body
- it attaches face parts
- it attaches hat
- it attaches arms with hands
- it attaches legs with feet
- body_m.py does not animate parts directly
- rigs/actions/controllers will animate later
- audio is not handled here

Connection chain:

    BodyM
        |
        Hat
        |
        Face
            |
            Eyes
            Nose
            Mouth
        |
        Arms
            |
            Hands
        |
        Legs
            |
            Knees
            Ankles
            Feet
"""

from __future__ import annotations

from typing import Iterable
from typing import Optional

import numpy as np

from manimlib import Line
from manimlib import VGroup

from mathlab_creature.config.colors import CREATURE_BODY_STROKE
from mathlab_creature.config.defaults import BODY_NAME
from mathlab_creature.config.defaults import DEBUG_MODE
from mathlab_creature.config.defaults import LOG_CREATURE_BUILD
from mathlab_creature.config.sizes import BODY_M_HEIGHT
from mathlab_creature.config.sizes import BODY_M_STROKE_WIDTH
from mathlab_creature.config.sizes import BODY_M_WIDTH

from mathlab_creature.core.anchors import get_full_anchor_map
from mathlab_creature.core.geometry import as_vec3
from mathlab_creature.core.geometry import point
from mathlab_creature.core.geometry import zero_point
from mathlab_creature.core.logger import get_logger
from mathlab_creature.core.naming import creature_part_name
from mathlab_creature.core.transforms import TransformNode
from mathlab_creature.core.transforms import create_transform_node

from mathlab_creature.creature.parts.arms import build_arms
from mathlab_creature.creature.parts.eyes import build_eyes
from mathlab_creature.creature.parts.hat import build_hat
from mathlab_creature.creature.parts.legs import build_legs
from mathlab_creature.creature.parts.mouth import build_mouth
from mathlab_creature.creature.parts.nose import build_nose


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


def _build_m_points(
    width: float,
    height: float,
    center: Vec3Like,
) -> dict[str, Vector3 | float]:
    """
    Build key points for geometric M body.
    """

    center_vec = _coerce_point3(
        center,
        "center",
    )

    cx = center_vec[0]
    cy = center_vec[1]
    cz = center_vec[2]

    half_width = width / 2.0
    half_height = height / 2.0

    bottom_left = point(
        cx - half_width,
        cy - half_height,
        cz,
    )
    top_left = point(
        cx - half_width,
        cy + half_height,
        cz,
    )
    top_right = point(
        cx + half_width,
        cy + half_height,
        cz,
    )
    bottom_right = point(
        cx + half_width,
        cy - half_height,
        cz,
    )

    inner_shoulder_x = half_width * 0.32
    inner_shoulder_y = cy + half_height * 0.18
    valley_y = cy - half_height * 0.28

    inner_top_left = point(
        cx - inner_shoulder_x,
        inner_shoulder_y,
        cz,
    )
    inner_valley = point(
        cx,
        valley_y,
        cz,
    )
    inner_top_right = point(
        cx + inner_shoulder_x,
        inner_shoulder_y,
        cz,
    )

    return {
        "half_width": half_width,
        "half_height": half_height,
        "bottom_left": bottom_left,
        "top_left": top_left,
        "inner_top_left": inner_top_left,
        "inner_valley": inner_valley,
        "inner_top_right": inner_top_right,
        "top_right": top_right,
        "bottom_right": bottom_right,
    }


def _style_line(
    line: Line,
    *,
    stroke_color: str,
    stroke_width: float,
) -> Line:
    """
    Apply body line style.
    """

    line.set_stroke(
        color=stroke_color,
        width=stroke_width,
    )

    return line


def build_body_m_shape(
    *,
    width: float = BODY_M_WIDTH,
    height: float = BODY_M_HEIGHT,
    stroke_width: float = BODY_M_STROKE_WIDTH,
    stroke_color: str = CREATURE_BODY_STROKE,
    center: Optional[Vec3Like] = None,
    scale_factor: float = 1.0,
    assign_subpart_names: bool = True,
) -> VGroup:
    """
    Build only the M-shaped body strokes.

    This does not attach eyes, hat, arms, legs, or other parts.
    """

    width = _validate_positive(
        "width",
        width,
    )
    height = _validate_positive(
        "height",
        height,
    )
    stroke_width = _validate_positive(
        "stroke_width",
        stroke_width,
    )
    scale_factor = _validate_positive(
        "scale_factor",
        scale_factor,
    )

    center_vec = _coerce_point3(
        center,
        "center",
    )

    points = _build_m_points(
        width=width,
        height=height,
        center=center_vec,
    )

    bottom_left = points["bottom_left"]
    top_left = points["top_left"]
    inner_top_left = points["inner_top_left"]
    inner_valley = points["inner_valley"]
    inner_top_right = points["inner_top_right"]
    top_right = points["top_right"]
    bottom_right = points["bottom_right"]

    left_leg = Line(
        bottom_left,
        top_left,
    )
    left_shoulder = Line(
        top_left,
        inner_top_left,
    )
    left_inner_diag = Line(
        top_left,
        inner_valley,
    )
    right_inner_diag = Line(
        inner_valley,
        top_right,
    )
    right_shoulder = Line(
        inner_top_right,
        top_right,
    )
    right_leg = Line(
        top_right,
        bottom_right,
    )

    segments = [
        left_leg,
        left_shoulder,
        left_inner_diag,
        right_inner_diag,
        right_shoulder,
        right_leg,
    ]

    for segment in segments:
        _style_line(
            segment,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
        )

    body_shape = VGroup(
        *segments,
    )

    if scale_factor != 1.0:
        body_shape.scale(
            scale_factor,
        )

    if assign_subpart_names:
        body_shape.name = creature_part_name(
            BODY_NAME,
        )

        left_leg.name = "body_m_left_leg"
        left_shoulder.name = "body_m_left_shoulder"
        left_inner_diag.name = "body_m_left_inner_diag"
        right_inner_diag.name = "body_m_right_inner_diag"
        right_shoulder.name = "body_m_right_shoulder"
        right_leg.name = "body_m_right_leg"

    body_shape.body_width = width
    body_shape.body_height = height
    body_shape.body_stroke_width = stroke_width
    body_shape.body_center = center_vec
    body_shape.body_points = points
    body_shape.is_body_m_shape = True

    return body_shape


class BodyM(VGroup):
    """
    Connected visible creature body assembly.

    Contains:
    - M body shape
    - hat
    - eyes
    - nose
    - mouth
    - arms with hands
    - legs with feet
    """

    def __init__(
        self,
        *,
        center: Optional[Vec3Like] = None,
        width: float = BODY_M_WIDTH,
        height: float = BODY_M_HEIGHT,
        stroke_width: float = BODY_M_STROKE_WIDTH,
        stroke_color: str = CREATURE_BODY_STROKE,
        scale_factor: float = 1.0,
        include_hat: bool = True,
        include_face: bool = True,
        include_arms: bool = True,
        include_legs: bool = True,
        include_hands: bool = True,
        include_feet: bool = True,
        debug_enabled: Optional[bool] = None,
        name: str = "body_m",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.body_center = _coerce_point3(
            center,
            "center",
        )

        self.body_width = _validate_positive(
            "width",
            width,
        )
        self.body_height = _validate_positive(
            "height",
            height,
        )
        self.body_stroke_width = _validate_positive(
            "stroke_width",
            stroke_width,
        )
        self.stroke_color = stroke_color
        self.scale_factor = _validate_positive(
            "scale_factor",
            scale_factor,
        )

        self.include_hat = bool(include_hat)
        self.include_face = bool(include_face)
        self.include_arms = bool(include_arms)
        self.include_legs = bool(include_legs)
        self.include_hands = bool(include_hands)
        self.include_feet = bool(include_feet)
        self.debug_enabled = DEBUG_MODE if debug_enabled is None else bool(debug_enabled)

        self.body_name = str(name)

        self.transform_node = create_transform_node(
            name=self.body_name,
            mobject=self,
        )

        self._build_body_shape()
        self._build_attached_parts()
        self._assemble()
        self._register_metadata()

        self.name = creature_part_name(
            BODY_NAME,
        )
        self.is_creature_body_m = True

    def _build_body_shape(self) -> None:
        """
        Build main M body shape.
        """

        self.body_shape = build_body_m_shape(
            width=self.body_width,
            height=self.body_height,
            stroke_width=self.body_stroke_width,
            stroke_color=self.stroke_color,
            center=self.body_center,
            scale_factor=self.scale_factor,
            assign_subpart_names=True,
        )

    def _build_attached_parts(self) -> None:
        """
        Build all optional attached body parts.
        """

        self.hat = None
        self.eyes = None
        self.nose = None
        self.mouth = None
        self.arms = None
        self.legs = None

        if self.include_hat:
            self.hat = build_hat(
                body_center=self.body_center,
            )

        if self.include_face:
            self.eyes = build_eyes(
                body_center=self.body_center,
            )
            self.nose = build_nose(
                body_center=self.body_center,
            )
            self.mouth = build_mouth(
                body_center=self.body_center,
            )

        if self.include_arms:
            self.arms = build_arms(
                body_center=self.body_center,
                include_hands=self.include_hands,
            )

        if self.include_legs:
            self.legs = build_legs(
                body_center=self.body_center,
                include_feet=self.include_feet,
                debug_enabled=self.debug_enabled,
            )

    def _assemble(self) -> None:
        """
        Add all parts to one connected VGroup.
        """

        parts = [
            self.body_shape,
        ]

        if self.legs is not None:
            parts.append(
                self.legs,
            )

        if self.arms is not None:
            parts.append(
                self.arms,
            )

        if self.hat is not None:
            parts.append(
                self.hat,
            )

        if self.eyes is not None:
            parts.append(
                self.eyes,
            )

        if self.nose is not None:
            parts.append(
                self.nose,
            )

        if self.mouth is not None:
            parts.append(
                self.mouth,
            )

        self.add(
            *parts,
        )

    def _register_metadata(self) -> None:
        """
        Register anchor and part metadata.
        """

        self.anchor_map = get_full_anchor_map(
            self.body_center,
        )

        self.transform_node.set_center_point(
            self.body_center,
        )
        self.transform_node.set_root_pivot(
            self.body_center,
        )

        self.parts = {
            "body_shape": self.body_shape,
            "hat": self.hat,
            "eyes": self.eyes,
            "nose": self.nose,
            "mouth": self.mouth,
            "arms": self.arms,
            "legs": self.legs,
        }

        self.face_parts = VGroup()

        if self.eyes is not None:
            self.face_parts.add(
                self.eyes,
            )

        if self.nose is not None:
            self.face_parts.add(
                self.nose,
            )

        if self.mouth is not None:
            self.face_parts.add(
                self.mouth,
            )

        self.face_parts.name = "creature_face_parts"

        self.left_arm = getattr(
            self.arms,
            "left_arm",
            None,
        )
        self.right_arm = getattr(
            self.arms,
            "right_arm",
            None,
        )
        self.left_hand = getattr(
            self.arms,
            "left_hand",
            None,
        )
        self.right_hand = getattr(
            self.arms,
            "right_hand",
            None,
        )

        self.left_leg = getattr(
            self.legs,
            "left_leg",
            None,
        )
        self.right_leg = getattr(
            self.legs,
            "right_leg",
            None,
        )
        self.left_foot = getattr(
            self.legs,
            "left_foot",
            None,
        )
        self.right_foot = getattr(
            self.legs,
            "right_foot",
            None,
        )

    def get_transform_node(self) -> TransformNode:
        return self.transform_node

    def get_body_shape(self) -> VGroup:
        return self.body_shape

    def get_hat(self):
        return self.hat

    def get_eyes(self):
        return self.eyes

    def get_nose(self):
        return self.nose

    def get_mouth(self):
        return self.mouth

    def get_arms(self):
        return self.arms

    def get_legs(self):
        return self.legs

    def get_anchor_map(self) -> dict[str, Vector3]:
        return dict(
            self.anchor_map,
        )

    def get_part(
        self,
        name: str,
    ):
        return self.parts.get(
            name,
        )

    def debug_print(self) -> None:
        print("========== BODY M DEBUG ==========")
        print("Name:", self.body_name)
        print("Center:", self.body_center)
        print("Width:", self.body_width)
        print("Height:", self.body_height)
        print("Has Hat:", self.hat is not None)
        print("Has Face:", self.eyes is not None or self.nose is not None or self.mouth is not None)
        print("Has Arms:", self.arms is not None)
        print("Has Legs:", self.legs is not None)
        print("Parts:", list(self.parts.keys()))
        print("==================================")


def build_body_m(
    *,
    width: float = BODY_M_WIDTH,
    height: float = BODY_M_HEIGHT,
    stroke_width: float = BODY_M_STROKE_WIDTH,
    stroke_color: str = CREATURE_BODY_STROKE,
    center: Optional[Vec3Like] = None,
    scale_factor: float = 1.0,
    include_hat: bool = True,
    include_face: bool = True,
    include_arms: bool = True,
    include_legs: bool = True,
    include_hands: bool = True,
    include_feet: bool = True,
    debug_enabled: Optional[bool] = None,
) -> BodyM:
    """
    Build complete connected BodyM creature body.
    """

    if LOG_CREATURE_BUILD:
        logger.info(
            "Building connected BodyM"
        )

    body = BodyM(
        center=center,
        width=width,
        height=height,
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        scale_factor=scale_factor,
        include_hat=include_hat,
        include_face=include_face,
        include_arms=include_arms,
        include_legs=include_legs,
        include_hands=include_hands,
        include_feet=include_feet,
        debug_enabled=debug_enabled,
        name="body_m",
    )

    if DEBUG_MODE:
        logger.debug(
            "BodyM created | center=%s width=%.3f height=%.3f",
            body.body_center,
            width,
            height,
        )

    if LOG_CREATURE_BUILD:
        logger.info(
            "Connected BodyM created successfully"
        )

    return body


def build_body_m_only(
    *,
    width: float = BODY_M_WIDTH,
    height: float = BODY_M_HEIGHT,
    stroke_width: float = BODY_M_STROKE_WIDTH,
    stroke_color: str = CREATURE_BODY_STROKE,
    center: Optional[Vec3Like] = None,
    scale_factor: float = 1.0,
) -> VGroup:
    """
    Build only the M body shape.

    Useful for isolated body tests.
    """

    return build_body_m_shape(
        width=width,
        height=height,
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        center=center,
        scale_factor=scale_factor,
    )


__all__ = [
    "Vector3",
    "Vec3Like",
    "BodyM",
    "build_body_m_shape",
    "build_body_m",
    "build_body_m_only",
]