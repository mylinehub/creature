"""
Command line interface for mathlab-mylinehub-creature.

Current architecture rule:

    One connected creature.
    One public build_creature() API.
    One primary validation scene.

The CLI should not expose old deleted scene groups such as:

    test_boot_scene
    test_face_scene
    mascot_intro_scene
    vectors_intro_scene

Those belonged to the older multi-scene prototype architecture.
"""

from __future__ import annotations

import os
import subprocess
import sys
from typing import Dict, Tuple


PACKAGE_DIR = os.path.dirname(__file__)
PROJECT_DIR = os.path.dirname(PACKAGE_DIR)


SceneTarget = Tuple[str, str]


SCENES: Dict[str, Dict[str, SceneTarget]] = {
    "test": {
        "creature": (
            "scenes/tests/test_creature_scene.py",
            "TestCreatureScene",
        ),
    },
}


def print_help() -> None:
    print()
    print("Usage:")
    print("  creature run test creature")
    print()
    print("Available scenes:")
    print()

    for category, scenes in SCENES.items():
        print(f"  {category}:")
        for scene_name in scenes:
            print(f"    - {scene_name}")
        print()

    print("Examples:")
    print("  creature run test creature")
    print()


def run_scene(category: str, scene: str) -> int:
    if category not in SCENES:
        print(f"\n❌ Unknown category: {category}\n")
        print_help()
        return 1

    if scene not in SCENES[category]:
        print(f"\n❌ Unknown scene: {scene}\n")
        print_help()
        return 1

    relative_file_path, class_name = SCENES[category][scene]
    full_path = os.path.join(PROJECT_DIR, relative_file_path)

    if not os.path.exists(full_path):
        print()
        print("❌ Scene file does not exist.")
        print(f"   Expected: {full_path}")
        print()
        print("Create this file first:")
        print(f"   {relative_file_path}")
        print()
        return 1

    print()
    print(f"▶ Running: {category}/{scene}")
    print(f"   File: {relative_file_path}")
    print(f"   Scene: {class_name}")
    print()

    completed = subprocess.run(
        [
            "manimgl",
            full_path,
            class_name,
        ],
        check=False,
    )

    return completed.returncode


def main() -> int:
    if len(sys.argv) < 2:
        print_help()
        return 0

    command = sys.argv[1]

    if command in {"help", "-h", "--help"}:
        print_help()
        return 0

    if command != "run":
        print(f"\n❌ Unknown command: {command}\n")
        print_help()
        return 1

    if len(sys.argv) < 4:
        print("\n❌ Missing arguments.\n")
        print_help()
        return 1

    category = sys.argv[2]
    scene = sys.argv[3]

    return run_scene(
        category=category,
        scene=scene,
    )


if __name__ == "__main__":
    raise SystemExit(main())