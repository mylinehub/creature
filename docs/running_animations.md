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

This file is meant to be the practical “how to run things” reference for the whole project.

---

## 2. Basic Command

All scenes run using this format:

```bash
manimgl <file_path> <SceneClass>
```

Example:

```bash
manimgl scenes/tests/test_pose_scene.py TestPoseScene
```

---

## 3. Common Output Variants

### 3.1 Preview in window

```bash
manimgl scenes/tests/test_pose_scene.py TestPoseScene
```

This opens the interactive preview window.

---

### 3.2 Write video file

```bash
manimgl scenes/tests/test_pose_scene.py TestPoseScene -w
```

This renders and writes the output video.

---

### 3.3 Save final still frame

```bash
manimgl scenes/tests/test_pose_scene.py TestPoseScene -s
```

This saves only a final image frame.

---

### 3.4 Open output after render

```bash
manimgl scenes/tests/test_pose_scene.py TestPoseScene -o
```

This opens output after rendering.

---

## 4. First Quick Run

If you only want to test that the whole project pipeline is alive, start with:

```bash
manimgl scenes/tests/test_boot_scene.py TestBootScene
```

| Item | Meaning |
|------|---------|
| File | `scenes/tests/test_boot_scene.py` |
| Scene | `TestBootScene` |
| Goal | Verify project boots correctly |

---

## 5. Run the Main Master Scene

To run the full orchestrated project demo:

```bash
manimgl render_scene.py MasterRenderScene
```

To write video:

```bash
manimgl render_scene.py MasterRenderScene -w
```

| Item | Meaning |
|------|---------|
| File | `render_scene.py` |
| Scene | `MasterRenderScene` |
| Goal | Run the complete integrated demo |

---

## 6. Test Scenes

These are development validation scenes.

They are the first place to test if something is broken.

---

### 6.1 Boot Test

```bash
manimgl scenes/tests/test_boot_scene.py TestBootScene
```

```bash
manimgl scenes/tests/test_boot_scene.py TestBootScene -w
```

| Check | What to verify |
|-------|----------------|
| Manim boot | project starts |
| Text rendering | visible |
| Logging | scene starts cleanly |

---

### 6.2 Body Test

```bash
manimgl scenes/tests/test_body_scene.py TestBodyScene
```

```bash
manimgl scenes/tests/test_body_scene.py TestBodyScene -w
```

| Check | What to verify |
|-------|----------------|
| Body shape | M looks correct |
| Face alignment | eyes, nose, mouth align |
| Hat | placed properly |

---

### 6.3 Face Test

```bash
manimgl scenes/tests/test_face_scene.py TestFaceScene
```

```bash
manimgl scenes/tests/test_face_scene.py TestFaceScene -w
```

| Check | What to verify |
|-------|----------------|
| Eye spacing | balanced |
| Nose placement | centered |
| Mouth placement | readable |
| Face composition | clear |

---

### 6.4 Hat Test

```bash
manimgl scenes/tests/test_hat_scene.py TestHatScene
```

```bash
manimgl scenes/tests/test_hat_scene.py TestHatScene -w
```

| Check | What to verify |
|-------|----------------|
| Hat size | not too large/small |
| Hat position | sits above body properly |
| Silhouette | readable |

---

### 6.5 Limbs Test

```bash
manimgl scenes/tests/test_limbs_scene.py TestLimbsScene
```

```bash
manimgl scenes/tests/test_limbs_scene.py TestLimbsScene -w
```

| Check | What to verify |
|-------|----------------|
| Arms | attach properly |
| Hands | align to arms |
| Legs | attach properly |
| Feet | align to legs |
| Full silhouette | balanced |

---

### 6.6 Pose Test

```bash
manimgl scenes/tests/test_pose_scene.py TestPoseScene
```

```bash
manimgl scenes/tests/test_pose_scene.py TestPoseScene -w
```

| Check | What to verify |
|-------|----------------|
| Neutral pose | stable |
| Happy pose | cheerful |
| Teacher pose | presentational |
| Pointing pose | readable |
| Thinking pose | distinct |

---

### 6.7 Actions Test

```bash
manimgl scenes/tests/test_actions_scene.py TestActionsScene
```

```bash
manimgl scenes/tests/test_actions_scene.py TestActionsScene -w
```

| Check | What to verify |
|-------|----------------|
| Blink | fast and readable |
| Look | pupils move correctly |
| Wave | right arm reads clearly |
| Point | direction is strong |
| Hop | body motion works |
| Walk | stepping is readable |

---

### 6.8 Props Test

```bash
manimgl scenes/tests/test_props_scene.py TestPropsScene
```

```bash
manimgl scenes/tests/test_props_scene.py TestPropsScene -w
```

| Check | What to verify |
|-------|----------------|
| Pointer stick | visible and scaled well |
| Math board | readable |
| Formula card | readable |
| Axis plane | grid + axes look correct |

---

## 7. Character Scenes

These are presentation scenes for the mascot.

---

### 7.1 Mascot Intro Scene

```bash
manimgl scenes/character/mascot_intro_scene.py MascotIntroScene
```

```bash
manimgl scenes/character/mascot_intro_scene.py MascotIntroScene -w
```

| Check | What to verify |
|-------|----------------|
| Intro feel | friendly |
| Blink | natural |
| Look around | readable |
| Hop | small and clean |

---

### 7.2 Mascot Wave Scene

```bash
manimgl scenes/character/mascot_wave_scene.py MascotWaveScene
```

```bash
manimgl scenes/character/mascot_wave_scene.py MascotWaveScene -w
```

| Check | What to verify |
|-------|----------------|
| Greeting feel | friendly |
| Wave action | clear |
| Arm readability | strong |

---

### 7.3 Mascot Walk Scene

```bash
manimgl scenes/character/mascot_walk_scene.py MascotWalkScene
```

```bash
manimgl scenes/character/mascot_walk_scene.py MascotWalkScene -w
```

| Check | What to verify |
|-------|----------------|
| Entry movement | readable |
| Step rhythm | alternating |
| Travel direction | clear |

---

### 7.4 Mascot Point Scene

```bash
manimgl scenes/character/mascot_point_scene.py MascotPointScene
```

```bash
manimgl scenes/character/mascot_point_scene.py MascotPointScene -w
```

| Check | What to verify |
|-------|----------------|
| Point direction | right side emphasis |
| Hold pose | readable |
| Target label | clear |

---

### 7.5 Mascot Teach Scene

```bash
manimgl scenes/character/mascot_teach_scene.py MascotTeachScene
```

```bash
manimgl scenes/character/mascot_teach_scene.py MascotTeachScene -w
```

| Check | What to verify |
|-------|----------------|
| Board placement | correct |
| Pointer visibility | clear |
| Teaching silhouette | readable |

---

## 8. Lesson Scenes

These are the first math-teaching scenes.

---

### 8.1 Vectors Intro Scene

```bash
manimgl scenes/lessons/vectors_intro_scene.py VectorsIntroScene
```

```bash
manimgl scenes/lessons/vectors_intro_scene.py VectorsIntroScene -w
```

| Check | What to verify |
|-------|----------------|
| Axis plane | visible |
| Vector idea | readable |
| Mascot pointing | aligned with concept |

---

### 8.2 Coordinates Intro Scene

```bash
manimgl scenes/lessons/coordinates_intro_scene.py CoordinatesIntroScene
```

```bash
manimgl scenes/lessons/coordinates_intro_scene.py CoordinatesIntroScene -w
```

| Check | What to verify |
|-------|----------------|
| Point location | correct |
| Projection lines | readable |
| Coordinate label | clear |

---

### 8.3 Matrix Intro Scene

```bash
manimgl scenes/lessons/matrix_intro_scene.py MatrixIntroScene
```

```bash
manimgl scenes/lessons/matrix_intro_scene.py MatrixIntroScene -w
```

| Check | What to verify |
|-------|----------------|
| Formula card | readable |
| Matrix text | visible |
| Layout | balanced |

---

## 9. Full Recommended Run Order

If you want to test the whole project progressively, run in this order:

### Step 1 — boot

```bash
manimgl scenes/tests/test_boot_scene.py TestBootScene
```

### Step 2 — body

```bash
manimgl scenes/tests/test_body_scene.py TestBodyScene
```

### Step 3 — face

```bash
manimgl scenes/tests/test_face_scene.py TestFaceScene
```

### Step 4 — hat

```bash
manimgl scenes/tests/test_hat_scene.py TestHatScene
```

### Step 5 — limbs

```bash
manimgl scenes/tests/test_limbs_scene.py TestLimbsScene
```

### Step 6 — poses

```bash
manimgl scenes/tests/test_pose_scene.py TestPoseScene
```

### Step 7 — actions

```bash
manimgl scenes/tests/test_actions_scene.py TestActionsScene
```

### Step 8 — props

```bash
manimgl scenes/tests/test_props_scene.py TestPropsScene
```

### Step 9 — character intro

```bash
manimgl scenes/character/mascot_intro_scene.py MascotIntroScene
```

### Step 10 — character wave

```bash
manimgl scenes/character/mascot_wave_scene.py MascotWaveScene
```

### Step 11 — character walk

```bash
manimgl scenes/character/mascot_walk_scene.py MascotWalkScene
```

### Step 12 — character point

```bash
manimgl scenes/character/mascot_point_scene.py MascotPointScene
```

### Step 13 — character teach

```bash
manimgl scenes/character/mascot_teach_scene.py MascotTeachScene
```

### Step 14 — coordinates lesson

```bash
manimgl scenes/lessons/coordinates_intro_scene.py CoordinatesIntroScene
```

### Step 15 — vectors lesson

```bash
manimgl scenes/lessons/vectors_intro_scene.py VectorsIntroScene
```

### Step 16 — matrix lesson

```bash
manimgl scenes/lessons/matrix_intro_scene.py MatrixIntroScene
```

### Step 17 — master render

```bash
manimgl render_scene.py MasterRenderScene
```

---

## 10. Running Multiple Scenes One by One

There is no single built-in “run all files automatically” command in our project structure yet.

So for now, run them one by one in terminal in the order above.

If later you want, we can create a helper runner script that:

- lists scenes
- lets you pick one
- lets you run all tests
- lets you run only lessons
- lets you run only character scenes

That would go into `render_scene.py` or a separate `run_all.py`.

---

## 11. If a Scene Fails

Use this order to debug:

### 11.1 Boot scene first

If this fails:

- project setup problem
- Manim install problem
- environment problem

### 11.2 Then body scene

If this fails:

- basic creature import/build problem

### 11.3 Then props scene

If this fails:

- prop config mismatch
- prop builder issue

### 11.4 Then actions scene

If this fails:

- rig/action mismatch
- animation logic issue

---

## 12. Common Problems to Check

| Problem | Likely reason |
|---------|---------------|
| Import error | bad file name / missing symbol |
| Config constant missing | file using old constant name |
| Hand not following arm well | action logic needs refinement |
| Pointer not attached perfectly | prop not dynamically linked yet |
| Walk feels stiff | version 1 walk cycle is simple |

---

## 13. Recommended During Development

When creating or editing a file, test in this pattern:

1. related test scene
2. related character scene
3. related lesson scene
4. master render

This catches issues early.

---

## 14. Best Practical Commands Summary

### Fast sanity check

```bash
manimgl scenes/tests/test_boot_scene.py TestBootScene
```

### First real creature check

```bash
manimgl scenes/tests/test_body_scene.py TestBodyScene
```

### Full action check

```bash
manimgl scenes/tests/test_actions_scene.py TestActionsScene
```

### Full prop check

```bash
manimgl scenes/tests/test_props_scene.py TestPropsScene
```

### First teaching check

```bash
manimgl scenes/character/mascot_teach_scene.py MascotTeachScene
```

### Full demo

```bash
manimgl render_scene.py MasterRenderScene
```

---

## 15. Final Note

Always test progressively.

Do NOT jump straight to the master scene after every edit.

Better flow:

- small test
- focused scene
- full scene
- master render

That keeps debugging fast and controlled.