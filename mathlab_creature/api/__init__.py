"""
Public API package for mathlab-mylinehub-creature.

Only stable public entry point:

    from mathlab_creature import build_creature
"""

from mathlab_creature.api.creature_api import build_creature

__all__ = [
    "build_creature",
]