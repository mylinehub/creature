import sys
import subprocess
import os

BASE = os.path.dirname(__file__)

SCENES = {
    "test": {
        "boot": ("scenes/tests/test_boot_scene.py", "TestBootScene"),
        "body": ("scenes/tests/test_body_scene.py", "TestBodyScene"),
        "face": ("scenes/tests/test_face_scene.py", "TestFaceScene"),
        "hat": ("scenes/tests/test_hat_scene.py", "TestHatScene"),
        "limbs": ("scenes/tests/test_limbs_scene.py", "TestLimbsScene"),
        "pose": ("scenes/tests/test_pose_scene.py", "TestPoseScene"),
        "actions": ("scenes/tests/test_actions_scene.py", "TestActionsScene"),
        "props": ("scenes/tests/test_props_scene.py", "TestPropsScene"),
    },

    "character": {
        "intro": ("scenes/character/mascot_intro_scene.py", "MascotIntroScene"),
        "wave": ("scenes/character/mascot_wave_scene.py", "MascotWaveScene"),
        "walk": ("scenes/character/mascot_walk_scene.py", "MascotWalkScene"),
        "point": ("scenes/character/mascot_point_scene.py", "MascotPointScene"),
        "teach": ("scenes/character/mascot_teach_scene.py", "MascotTeachScene"),
    },

    "lesson": {
        "vectors": ("scenes/lessons/vectors_intro_scene.py", "VectorsIntroScene"),
        "coordinates": ("scenes/lessons/coordinates_intro_scene.py", "CoordinatesIntroScene"),
        "matrix": ("scenes/lessons/matrix_intro_scene.py", "MatrixIntroScene"),
    },
}


def print_help():
    print("\nUsage:")
    print("  creature run <category> <scene>\n")

    print("Categories and scenes:\n")

    for category, scenes in SCENES.items():
        print(f"  {category}:")
        for scene_name in scenes:
            print(f"    - {scene_name}")
        print()

    print("Examples:")
    print("  creature run test pose")
    print("  creature run lesson vectors")
    print("  creature run character wave\n")


def main():
    if len(sys.argv) < 2:
        print_help()
        return

    if sys.argv[1] != "run":
        print_help()
        return

    if len(sys.argv) < 4:
        print("Missing arguments.\n")
        print_help()
        return

    category = sys.argv[2]
    scene = sys.argv[3]

    if category not in SCENES:
        print(f"\n❌ Unknown category: {category}\n")
        print_help()
        return

    if scene not in SCENES[category]:
        print(f"\n❌ Unknown scene: {scene}\n")
        print_help()
        return

    file_path, class_name = SCENES[category][scene]

    full_path = os.path.join(BASE, file_path)

    print(f"\n▶ Running: {category}/{scene}")
    print(f"   File: {file_path}")
    print(f"   Scene: {class_name}\n")

    subprocess.run(["manimgl", full_path, class_name])