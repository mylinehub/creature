"""
Face rig for mathlab-mylinehub-creature.

This file controls already-built face parts.

Architecture rule:
- face_rig.py does not create disconnected floating parts
- face_rig.py can build fallback face parts if needed
- face_rig.py controls eyes, pupils, nose, and mouth metadata
- face_rig.py does not animate directly
- blink_action.py and look_action.py will call this rig later
- audio is not handled here

Connection chain:

    Action
        |
        FaceRig
            |
            Eyes
            Nose
            Mouth
"""

from __future__ import annotations

from typing import Optional

from manimlib import VGroup

from mathlab_creature.config.defaults import DEBUG_MODE
from mathlab_creature.config.defaults import LOG_CREATURE_BUILD

from mathlab_creature.core.logger import get_logger
from mathlab_creature.core.transforms import TransformNode
from mathlab_creature.core.transforms import create_transform_node

from mathlab_creature.creature.parts.eyes import build_eyes
from mathlab_creature.creature.parts.eyes import reset_eyes_pupils
from mathlab_creature.creature.parts.eyes import set_eyes_pupil_offset
from mathlab_creature.creature.parts.mouth import build_mouth
from mathlab_creature.creature.parts.mouth import set_mouth_smile_amount
from mathlab_creature.creature.parts.nose import build_nose


logger = get_logger(__name__)


_FACE_EYES_INDEX = 0
_FACE_NOSE_INDEX = 1
_FACE_MOUTH_INDEX = 2
_FACE_MIN_PART_COUNT = 3


def _validate_face_group(
    face_group: VGroup,
    *,
    require_full: bool = True,
) -> None:
    if not isinstance(face_group, VGroup):
        raise TypeError(
            f"face_group must be VGroup, got {type(face_group).__name__}"
        )

    if require_full and len(face_group) < _FACE_MIN_PART_COUNT:
        raise ValueError(
            f"face_group must contain at least {_FACE_MIN_PART_COUNT} parts, "
            f"got {len(face_group)}"
        )


def _build_face_parts(
    body_center=None,
):
    eyes = build_eyes(
        body_center=body_center,
    )
    nose = build_nose(
        body_center=body_center,
    )
    mouth = build_mouth(
        body_center=body_center,
    )

    return eyes, nose, mouth


def _attach_face_metadata(
    face_group: VGroup,
    *,
    eyes,
    nose,
    mouth,
    body_center=None,
    name: str = "creature_face",
) -> VGroup:
    face_group.name = name

    face_group.eyes = eyes
    face_group.nose = nose
    face_group.mouth = mouth

    face_group.body_center = body_center
    face_group.face_part_order = (
        "eyes",
        "nose",
        "mouth",
    )

    face_group.transform_node = create_transform_node(
        name="face_rig",
        mobject=face_group,
    )

    face_group.get_transform_node = lambda: face_group.transform_node

    face_group.is_creature_face_rig = True

    return face_group


def _build_face_group_from_parts(
    eyes,
    nose,
    mouth,
    *,
    body_center=None,
    assign_name: bool = True,
) -> VGroup:
    face_group = VGroup(
        eyes,
        nose,
        mouth,
    )

    return _attach_face_metadata(
        face_group,
        eyes=eyes,
        nose=nose,
        mouth=mouth,
        body_center=body_center,
        name="creature_face" if assign_name else "face_rig",
    )


def _refresh_face_group_metadata(
    face_group: VGroup,
    *,
    body_center=None,
) -> VGroup:
    _validate_face_group(
        face_group,
        require_full=True,
    )

    eyes = face_group[_FACE_EYES_INDEX]
    nose = face_group[_FACE_NOSE_INDEX]
    mouth = face_group[_FACE_MOUTH_INDEX]

    if not hasattr(face_group, "transform_node"):
        face_group.transform_node = create_transform_node(
            name="face_rig",
            mobject=face_group,
        )
        face_group.get_transform_node = lambda: face_group.transform_node

    face_group.eyes = eyes
    face_group.nose = nose
    face_group.mouth = mouth

    if body_center is not None:
        face_group.body_center = body_center

    face_group.face_part_order = (
        "eyes",
        "nose",
        "mouth",
    )
    face_group.is_creature_face_rig = True

    return face_group


def _replace_face_part(
    face_group: VGroup,
    index: int,
    new_part,
    *,
    body_center=None,
    log_label: str = "face part",
) -> VGroup:
    _validate_face_group(
        face_group,
        require_full=True,
    )

    face_group.submobjects[index] = new_part

    _refresh_face_group_metadata(
        face_group,
        body_center=body_center,
    )

    if LOG_CREATURE_BUILD:
        logger.info(
            "%s rebuilt successfully",
            log_label,
        )

    return face_group


class FaceRig:
    """
    Controller wrapper for face parts.

    Controls:
    - pupil look offsets
    - pupil reset
    - smile metadata
    - face rebuild helpers
    """

    def __init__(
        self,
        face_group: Optional[VGroup] = None,
        *,
        eyes=None,
        nose=None,
        mouth=None,
        body_center=None,
    ) -> None:
        if face_group is None:
            if eyes is None:
                eyes = build_eyes(
                    body_center=body_center,
                )

            if nose is None:
                nose = build_nose(
                    body_center=body_center,
                )

            if mouth is None:
                mouth = build_mouth(
                    body_center=body_center,
                )

            face_group = _build_face_group_from_parts(
                eyes,
                nose,
                mouth,
                body_center=body_center,
            )
        else:
            _refresh_face_group_metadata(
                face_group,
                body_center=body_center,
            )

        self.group = face_group
        self.eyes = face_group.eyes
        self.nose = face_group.nose
        self.mouth = face_group.mouth
        self.body_center = getattr(
            face_group,
            "body_center",
            body_center,
        )

        self.transform_node = face_group.transform_node

    def get_group(self) -> VGroup:
        return self.group

    def get_transform_node(self) -> TransformNode:
        return self.transform_node

    def get_eyes(self):
        return self.eyes

    def get_nose(self):
        return self.nose

    def get_mouth(self):
        return self.mouth

    def look(
        self,
        left_offset=None,
        right_offset=None,
    ) -> None:
        """
        Move pupils locally inside eyes.

        Used later by look_action.py.
        """
        set_eyes_pupil_offset(
            self.eyes,
            left_offset,
            right_offset,
        )

    def reset_look(self) -> None:
        """
        Reset both pupils to eye centers.
        """
        reset_eyes_pupils(
            self.eyes,
        )

    def set_smile(
        self,
        arc_angle: float,
    ) -> None:
        """
        Store smile state on mouth.

        Actual expression replacement/animation can be added later.
        """
        set_mouth_smile_amount(
            self.mouth,
            arc_angle,
        )

    def rebuild_eyes(self) -> VGroup:
        self.group = rebuild_eyes(
            self.group,
            body_center=self.body_center,
        )
        self.eyes = self.group.eyes
        return self.group

    def rebuild_nose(self) -> VGroup:
        self.group = rebuild_nose(
            self.group,
            body_center=self.body_center,
        )
        self.nose = self.group.nose
        return self.group

    def rebuild_mouth(self) -> VGroup:
        self.group = rebuild_mouth(
            self.group,
            body_center=self.body_center,
        )
        self.mouth = self.group.mouth
        return self.group

    def rebuild_face(self) -> VGroup:
        self.group = rebuild_face(
            self.group,
            body_center=self.body_center,
        )
        self.eyes = self.group.eyes
        self.nose = self.group.nose
        self.mouth = self.group.mouth
        return self.group

    def debug_print(self) -> None:
        print("========== FACE RIG DEBUG ==========")
        print("Body Center:", self.body_center)
        print("Eyes:", getattr(self.eyes, "name", "eyes"))
        print("Nose:", getattr(self.nose, "name", "nose"))
        print("Mouth:", getattr(self.mouth, "name", "mouth"))
        print("====================================")


def build_face_group(
    body_center=None,
) -> VGroup:
    """
    Build face group only.
    """
    if LOG_CREATURE_BUILD:
        logger.info("Building face group")

    eyes, nose, mouth = _build_face_parts(
        body_center=body_center,
    )

    face_group = _build_face_group_from_parts(
        eyes,
        nose,
        mouth,
        body_center=body_center,
    )

    if DEBUG_MODE:
        logger.debug(
            "Face group built | eyes=%s nose=%s mouth=%s",
            getattr(eyes, "name", "eyes"),
            getattr(nose, "name", "nose"),
            getattr(mouth, "name", "mouth"),
        )

    if LOG_CREATURE_BUILD:
        logger.info("Face group created successfully")

    return face_group


def build_face_rig(
    eyes=None,
    mouth=None,
    nose=None,
    body_center=None,
) -> FaceRig:
    """
    Build FaceRig wrapper.

    Existing parts may be passed from BodyM.
    If missing, they are built automatically.
    """
    if LOG_CREATURE_BUILD:
        logger.info("Building face rig")

    rig = FaceRig(
        eyes=eyes,
        nose=nose,
        mouth=mouth,
        body_center=body_center,
    )

    if LOG_CREATURE_BUILD:
        logger.info("Face rig created successfully")

    return rig


def build_face_rig_group(
    eyes=None,
    mouth=None,
    nose=None,
    body_center=None,
) -> VGroup:
    """
    Compatibility helper returning only VGroup.
    """
    return build_face_rig(
        eyes=eyes,
        mouth=mouth,
        nose=nose,
        body_center=body_center,
    ).get_group()


def build_face_rig_map(
    body_center=None,
) -> dict[str, object]:
    """
    Build face rig and return map.
    """
    if LOG_CREATURE_BUILD:
        logger.info("Building face rig map")

    rig = build_face_rig(
        body_center=body_center,
    )

    group = rig.get_group()

    rig_map = {
        "rig": rig,
        "eyes": rig.get_eyes(),
        "nose": rig.get_nose(),
        "mouth": rig.get_mouth(),
        "group": group,
        "body_center": body_center,
    }

    if LOG_CREATURE_BUILD:
        logger.info("Face rig map created successfully")

    return rig_map


def rebuild_mouth(
    face_group: VGroup,
    body_center=None,
) -> VGroup:
    if LOG_CREATURE_BUILD:
        logger.info("Rebuilding mouth inside face group")

    new_mouth = build_mouth(
        body_center=body_center,
    )

    return _replace_face_part(
        face_group,
        _FACE_MOUTH_INDEX,
        new_mouth,
        body_center=body_center,
        log_label="Mouth",
    )


def rebuild_eyes(
    face_group: VGroup,
    body_center=None,
) -> VGroup:
    if LOG_CREATURE_BUILD:
        logger.info("Rebuilding eyes inside face group")

    new_eyes = build_eyes(
        body_center=body_center,
    )

    return _replace_face_part(
        face_group,
        _FACE_EYES_INDEX,
        new_eyes,
        body_center=body_center,
        log_label="Eyes",
    )


def rebuild_nose(
    face_group: VGroup,
    body_center=None,
) -> VGroup:
    if LOG_CREATURE_BUILD:
        logger.info("Rebuilding nose inside face group")

    new_nose = build_nose(
        body_center=body_center,
    )

    return _replace_face_part(
        face_group,
        _FACE_NOSE_INDEX,
        new_nose,
        body_center=body_center,
        log_label="Nose",
    )


def rebuild_face(
    face_group: VGroup,
    body_center=None,
) -> VGroup:
    if LOG_CREATURE_BUILD:
        logger.info("Rebuilding full face group")

    _validate_face_group(
        face_group,
        require_full=True,
    )

    new_eyes, new_nose, new_mouth = _build_face_parts(
        body_center=body_center,
    )

    face_group.submobjects[_FACE_EYES_INDEX] = new_eyes
    face_group.submobjects[_FACE_NOSE_INDEX] = new_nose
    face_group.submobjects[_FACE_MOUTH_INDEX] = new_mouth

    _refresh_face_group_metadata(
        face_group,
        body_center=body_center,
    )

    if LOG_CREATURE_BUILD:
        logger.info("Full face group rebuilt successfully")

    return face_group


def get_eyes(
    face_group: VGroup,
):
    _validate_face_group(
        face_group,
        require_full=True,
    )

    return face_group[_FACE_EYES_INDEX]


def get_nose(
    face_group: VGroup,
):
    _validate_face_group(
        face_group,
        require_full=True,
    )

    return face_group[_FACE_NOSE_INDEX]


def get_mouth(
    face_group: VGroup,
):
    _validate_face_group(
        face_group,
        require_full=True,
    )

    return face_group[_FACE_MOUTH_INDEX]


def get_face_parts(
    face_group: VGroup,
) -> tuple[object, object, object]:
    _validate_face_group(
        face_group,
        require_full=True,
    )

    return (
        face_group[_FACE_EYES_INDEX],
        face_group[_FACE_NOSE_INDEX],
        face_group[_FACE_MOUTH_INDEX],
    )


__all__ = [
    "FaceRig",
    "build_face_group",
    "build_face_rig",
    "build_face_rig_group",
    "build_face_rig_map",
    "rebuild_mouth",
    "rebuild_eyes",
    "rebuild_nose",
    "rebuild_face",
    "get_eyes",
    "get_nose",
    "get_mouth",
    "get_face_parts",
]