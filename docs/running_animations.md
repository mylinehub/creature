# Running Animations Guide  
mathlab-mylinehub-creature

---

## 1. Purpose

This guide explains:

- how to run any scene
- how to run one specific scene
- how to run test scenes one by one
- how to run character scenes
- how to run lesson scenes
- how to render video output
- how to troubleshoot common issues

This file is the **single source of truth** for running this project.

---

## 2. IMPORTANT (New Structure)

The project is now a **Python package**:

```

mathlab_creature/

```

So ALL scene paths must use:

```

mathlab_creature/scenes/...

````

---

## 3. Basic Command

```bash
manimgl <file_path> <SceneClass>
````

---

## 4. Correct Usage (VERY IMPORTANT)

### ❌ OLD (WILL FAIL)

```bash
manimgl scenes/tests/test_pose_scene.py TestPoseScene
```

### ✅ NEW (CORRECT)

```bash
manimgl mathlab_creature/scenes/tests/test_pose_scene.py TestPoseScene
```

---

## 5. Output Variants

### Preview

```bash
manimgl mathlab_creature/scenes/tests/test_pose_scene.py TestPoseScene
```

---

### Write video

```bash
manimgl mathlab_creature/scenes/tests/test_pose_scene.py TestPoseScene -w
```

---

### Save final frame

```bash
manimgl mathlab_creature/scenes/tests/test_pose_scene.py TestPoseScene -s
```

---

### Open after render

```bash
manimgl mathlab_creature/scenes/tests/test_pose_scene.py TestPoseScene -o
```

---

## 6. First Quick Run (Sanity Check)

```bash
manimgl mathlab_creature/scenes/tests/test_boot_scene.py TestBootScene
```

---

## 7. Master Scene

```bash
manimgl mathlab_creature/render_scene.py MasterRenderScene
```

---

## 8. Test Scenes

---

### Boot

```bash
manimgl mathlab_creature/scenes/tests/test_boot_scene.py TestBootScene
```

---

### Body

```bash
manimgl mathlab_creature/scenes/tests/test_body_scene.py TestBodyScene
```

---

### Face

```bash
manimgl mathlab_creature/scenes/tests/test_face_scene.py TestFaceScene
```

---

### Hat

```bash
manimgl mathlab_creature/scenes/tests/test_hat_scene.py TestHatScene
```

---

### Limbs

```bash
manimgl mathlab_creature/scenes/tests/test_limbs_scene.py TestLimbsScene
```

---

### Pose

```bash
manimgl mathlab_creature/scenes/tests/test_pose_scene.py TestPoseScene
```

---

### Actions

```bash
manimgl mathlab_creature/scenes/tests/test_actions_scene.py TestActionsScene
```

---

### Props

```bash
manimgl mathlab_creature/scenes/tests/test_props_scene.py TestPropsScene
```

---

## 9. Character Scenes

---

### Intro

```bash
manimgl mathlab_creature/scenes/character/mascot_intro_scene.py MascotIntroScene
```

---

### Wave

```bash
manimgl mathlab_creature/scenes/character/mascot_wave_scene.py MascotWaveScene
```

---

### Walk

```bash
manimgl mathlab_creature/scenes/character/mascot_walk_scene.py MascotWalkScene
```

---

### Point

```bash
manimgl mathlab_creature/scenes/character/mascot_point_scene.py MascotPointScene
```

---

### Teach

```bash
manimgl mathlab_creature/scenes/character/mascot_teach_scene.py MascotTeachScene
```

---

## 10. Lesson Scenes

---

### Vectors

```bash
manimgl mathlab_creature/scenes/lessons/vectors_intro_scene.py VectorsIntroScene
```

---

### Coordinates

```bash
manimgl mathlab_creature/scenes/lessons/coordinates_intro_scene.py CoordinatesIntroScene
```

---

### Matrix

```bash
manimgl mathlab_creature/scenes/lessons/matrix_intro_scene.py MatrixIntroScene
```

---

## 11. Recommended Run Order

```bash
manimgl mathlab_creature/scenes/tests/test_boot_scene.py TestBootScene
manimgl mathlab_creature/scenes/tests/test_body_scene.py TestBodyScene
manimgl mathlab_creature/scenes/tests/test_face_scene.py TestFaceScene
manimgl mathlab_creature/scenes/tests/test_hat_scene.py TestHatScene
manimgl mathlab_creature/scenes/tests/test_limbs_scene.py TestLimbsScene
manimgl mathlab_creature/scenes/tests/test_pose_scene.py TestPoseScene
manimgl mathlab_creature/scenes/tests/test_actions_scene.py TestActionsScene
manimgl mathlab_creature/scenes/tests/test_props_scene.py TestPropsScene
manimgl mathlab_creature/scenes/character/mascot_intro_scene.py MascotIntroScene
manimgl mathlab_creature/scenes/character/mascot_wave_scene.py MascotWaveScene
manimgl mathlab_creature/scenes/character/mascot_walk_scene.py MascotWalkScene
manimgl mathlab_creature/scenes/character/mascot_point_scene.py MascotPointScene
manimgl mathlab_creature/scenes/character/mascot_teach_scene.py MascotTeachScene
manimgl mathlab_creature/scenes/lessons/coordinates_intro_scene.py CoordinatesIntroScene
manimgl mathlab_creature/scenes/lessons/vectors_intro_scene.py VectorsIntroScene
manimgl mathlab_creature/scenes/lessons/matrix_intro_scene.py MatrixIntroScene
manimgl mathlab_creature/render_scene.py MasterRenderScene
```

---

## 12. If Something Fails

### Step 1

```bash
manimgl mathlab_creature/scenes/tests/test_boot_scene.py TestBootScene
```

---

### Step 2

```bash
python -c "import mathlab_creature"
```

---

### Step 3

```bash
pip install -e .
```

---

## 13. Most Common Mistake

❌ Using old path:

```bash
manimgl scenes/...
```

✅ Correct:

```bash
manimgl mathlab_creature/scenes/...
```

---

## 14. Final Note

This project is now:

* a **Python package**
* a **reusable animation engine**
* a **teaching system**

Always use the **package path**.

---

## 15. Your Quick Command

```bash
manimgl mathlab_creature/scenes/tests/test_pose_scene.py TestPoseScene
```

---

````
