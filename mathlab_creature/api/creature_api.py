"""
Public creature API.

This is the only public construction entry point.

External usage:

    from mathlab_creature import build_creature

    creature = build_creature()
"""

from __future__ import annotations

from typing import Optional

from mathlab_creature.creature.root.creature_root import CreatureRoot


def build_creature(
    *,
    position=None,
    with_sound: bool = True,
    debug_enabled: Optional[bool] = None,
) -> CreatureRoot:
    """
    Build one complete connected creature.

    Returns:
        CreatureRoot

    Public rule:
        Outside code should use only this function.
    """
    return CreatureRoot(
        position=position,
        with_sound=with_sound,
        debug_enabled=debug_enabled,
    )


__all__ = [
    "build_creature",
]