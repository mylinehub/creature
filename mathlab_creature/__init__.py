"""
mathlab_creature

Public package interface.

Only build_creature() is intended to be imported
by external projects.

Example:

    from mathlab_creature import build_creature

Everything else should remain internal to the
package implementation.
"""

from mathlab_creature.api.creature_api import (
    build_creature,
)

__all__ = [
    "build_creature",
]