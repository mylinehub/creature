# File: mathlab_creature/creature/rigs/face_rig.py

"""
Face rig helpers for mathlab-mylinehub-creature.

FIXED VERSION
-------------
- added transform-node compatibility
- added get_transform_node()
- fixed broken tuple syntax
- compatible with body_rig.py
- preserves all existing functionality
"""

from __future__ import annotations

from manimlib import VGroup

from mathlab_creature.config.defaults import (
    DEBUG_MODE,
    LOG_CREATURE_BUILD,
)

from mathlab_creature.creature.parts.eyes import (
    build_eyes,
)

from mathlab_creature.creature.parts.mouth import (
    build_mouth,
)

from mathlab_creature.creature.parts.nose import (
    build_nose,
)

from mathlab_creature.core.transforms import (
    create_transform_node,
)

from mathlab_creature.core.logger import (
    get_logger,
)

logger = get_logger(__name__)


# ============================================================
# INTERNAL CONSTANTS
# ============================================================

_FACE_EYES_INDEX = 0
_FACE_NOSE_INDEX = 1
_FACE_MOUTH_INDEX = 2

_FACE_MIN_PART_COUNT = 3


# ============================================================
# INTERNAL HELPERS
# ============================================================

def _validate_face_group(
    face_group: VGroup,
    *,
    require_full: bool = True,
) -> None:

    if not isinstance(face_group, VGroup):

        raise TypeError(
            f"face_group must be a VGroup, "
            f"got {type(face_group).__name__}"
        )

    if (
        require_full
        and len(face_group) < _FACE_MIN_PART_COUNT
    ):

        raise ValueError(
            f"face_group must contain at least "
            f"{_FACE_MIN_PART_COUNT} parts, "
            f"got {len(face_group)}"
        )


def _build_face_parts(
    body_center=None,
) -> tuple[object, object, object]:

    eyes = build_eyes(body_center)

    nose = build_nose(body_center)

    mouth = build_mouth(body_center)

    return eyes, nose, mouth


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

    if assign_name:
        face_group.name = "creature_face"

    # --------------------------------------------------------
    # TRANSFORM NODE
    # --------------------------------------------------------

    face_group.transform_node = (
        create_transform_node(
            name="face_rig",
            mobject=face_group,
        )
    )

    face_group.get_transform_node = (
        lambda: face_group.transform_node
    )

    # --------------------------------------------------------
    # METADATA
    # --------------------------------------------------------

    face_group.eyes = eyes

    face_group.nose = nose

    face_group.mouth = mouth

    face_group.body_center = body_center

    face_group.face_part_order = (
        "eyes",
        "nose",
        "mouth",
    )

    return face_group


def _refresh_face_group_metadata(
    face_group: VGroup,
    *,
    body_center=None,
) -> VGroup:

    _validate_face_group(
        face_group,
        require_full=True,
    )

    face_group.eyes = face_group[
        _FACE_EYES_INDEX
    ]

    face_group.nose = face_group[
        _FACE_NOSE_INDEX
    ]

    face_group.mouth = face_group[
        _FACE_MOUTH_INDEX
    ]

    if body_center is not None:
        face_group.body_center = body_center

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


# ============================================================
# FACE BUILDERS
# ============================================================

def build_face_group(
    body_center=None,
) -> VGroup:

    if LOG_CREATURE_BUILD:
        logger.info("Building face group")

    eyes, nose, mouth = (
        _build_face_parts(
            body_center
        )
    )

    face_group = (
        _build_face_group_from_parts(
            eyes,
            nose,
            mouth,
            body_center=body_center,
        )
    )

    if DEBUG_MODE:

        logger.debug(
            "Face group built | eyes=%s nose=%s mouth=%s",
            getattr(
                eyes,
                "name",
                "eyes",
            ),
            getattr(
                nose,
                "name",
                "nose",
            ),
            getattr(
                mouth,
                "name",
                "mouth",
            ),
        )

    if LOG_CREATURE_BUILD:

        logger.info(
            "Face group created successfully"
        )

    return face_group


# ============================================================
# COMPATIBILITY FACTORY
# ============================================================

def build_face_rig(
    eyes=None,
    mouth=None,
    nose=None,
    body_center=None,
):

    if LOG_CREATURE_BUILD:
        logger.info("Building face rig")

    # --------------------------------------------------------
    # AUTO BUILD FALLBACKS
    # --------------------------------------------------------

    if eyes is None:
        eyes = build_eyes(body_center)

    if nose is None:
        nose = build_nose(body_center)

    if mouth is None:
        mouth = build_mouth(body_center)

    face_group = (
        _build_face_group_from_parts(
            eyes,
            nose,
            mouth,
            body_center=body_center,
        )
    )

    if LOG_CREATURE_BUILD:

        logger.info(
            "Face rig created successfully"
        )

    return face_group


# ============================================================
# FACE RIG MAP
# ============================================================

def build_face_rig_map(
    body_center=None,
) -> dict[str, object]:

    if LOG_CREATURE_BUILD:
        logger.info("Building face rig map")

    eyes, nose, mouth = (
        _build_face_parts(
            body_center
        )
    )

    group = (
        _build_face_group_from_parts(
            eyes,
            nose,
            mouth,
            body_center=body_center,
        )
    )

    rig_map = {
        "eyes": eyes,
        "nose": nose,
        "mouth": mouth,
        "group": group,
        "body_center": body_center,
    }

    if LOG_CREATURE_BUILD:

        logger.info(
            "Face rig map created successfully"
        )

    return rig_map


# ============================================================
# REBUILD HELPERS
# ============================================================

def rebuild_mouth(
    face_group: VGroup,
    body_center=None,
) -> VGroup:

    if LOG_CREATURE_BUILD:

        logger.info(
            "Rebuilding mouth inside face group"
        )

    _validate_face_group(
        face_group,
        require_full=True,
    )

    new_mouth = build_mouth(
        body_center
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

        logger.info(
            "Rebuilding eyes inside face group"
        )

    _validate_face_group(
        face_group,
        require_full=True,
    )

    new_eyes = build_eyes(
        body_center
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

        logger.info(
            "Rebuilding nose inside face group"
        )

    _validate_face_group(
        face_group,
        require_full=True,
    )

    new_nose = build_nose(
        body_center
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

        logger.info(
            "Rebuilding full face group"
        )

    _validate_face_group(
        face_group,
        require_full=True,
    )

    (
        new_eyes,
        new_nose,
        new_mouth,
    ) = _build_face_parts(
        body_center
    )

    face_group.submobjects[
        _FACE_EYES_INDEX
    ] = new_eyes

    face_group.submobjects[
        _FACE_NOSE_INDEX
    ] = new_nose

    face_group.submobjects[
        _FACE_MOUTH_INDEX
    ] = new_mouth

    _refresh_face_group_metadata(
        face_group,
        body_center=body_center,
    )

    if LOG_CREATURE_BUILD:

        logger.info(
            "Full face group rebuilt successfully"
        )

    return face_group


# ============================================================
# ACCESS HELPERS
# ============================================================

def get_eyes(
    face_group: VGroup,
):

    _validate_face_group(
        face_group,
        require_full=True,
    )

    return face_group[
        _FACE_EYES_INDEX
    ]


def get_nose(
    face_group: VGroup,
):

    _validate_face_group(
        face_group,
        require_full=True,
    )

    return face_group[
        _FACE_NOSE_INDEX
    ]


def get_mouth(
    face_group: VGroup,
):

    _validate_face_group(
        face_group,
        require_full=True,
    )

    return face_group[
        _FACE_MOUTH_INDEX
    ]


def get_face_parts(
    face_group: VGroup,
) -> tuple[object, object, object]:

    _validate_face_group(
        face_group,
        require_full=True,
    )

    return (
        face_group[
            _FACE_EYES_INDEX
        ],
        face_group[
            _FACE_NOSE_INDEX
        ],
        face_group[
            _FACE_MOUTH_INDEX
        ],
    )