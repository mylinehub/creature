# 🎬 mathlab-mylinehub-creature

A modular **ManimGL-based animation system** to build and control a reusable MYLINEHUB mascot — designed for **education, storytelling, and telecom/AI training visuals**.

---

# 🧠 What this project really is

This is **not just a character**.

It is a **layered animation architecture** where:

```
Parts → Rig → Pose → Action → Scene
```

Each layer adds more intelligence and reuse.

---

# 🎯 Core Goals

* Build a **reusable animated mascot system**
* Keep **clean separation of concerns**
* Enable **fast scene creation**
* Make animations **consistent + scalable**
* Support **teaching visuals (math, telecom, AI)**

---

# 🧩 System Architecture

## 🔷 High-level flow

```
[ config ] → [ parts ] → [ rigs ] → [ poses ] → [ actions ] → [ scenes ]
```

| Layer   | Responsibility                |
| ------- | ----------------------------- |
| config  | Colors, sizes, defaults       |
| parts   | Raw shapes (eyes, body, hat…) |
| rigs    | Attach + control parts        |
| poses   | Static expressions            |
| actions | Motion (blink, wave, walk)    |
| scenes  | Final animation output        |

---

# 🏗️ Folder Structure (Explained)

```
config/
core/
creature/
props/
scenes/
docs/
assets/
```

---

## ⚙️ config/

Defines **visual rules**

| File        | Purpose                     |
| ----------- | --------------------------- |
| colors.py   | All colors used globally    |
| sizes.py    | Dimensions & proportions    |
| defaults.py | Default positions & scaling |

👉 This ensures **no hardcoding inside parts**

---

## 🧠 core/

Reusable low-level helpers

| File        | Purpose           |
| ----------- | ----------------- |
| geometry.py | Shape math        |
| anchors.py  | Alignment points  |
| layout.py   | Position helpers  |
| motion.py   | Animation helpers |
| naming.py   | Consistent naming |

👉 This is your **engine layer**

---

## 🧍 creature/

Main character system

### 🔹 parts/

Smallest visual units

| Part      | Meaning           |
| --------- | ----------------- |
| body_m.py | M-shaped body     |
| eyes.py   | Eye system        |
| nose.py   | Nose              |
| mouth.py  | Expressions       |
| hat.py    | Identity/branding |
| arms.py   | Movement          |
| legs.py   | Movement          |

👉 These are **dumb objects** (no intelligence)

---

### 🔹 rigs/

Control systems

| Rig         | Role                    |
| ----------- | ----------------------- |
| face_rig.py | Controls eyes, mouth    |
| arm_rig.py  | Controls arms           |
| leg_rig.py  | Controls walking        |
| body_rig.py | Whole-body coordination |

👉 Rigs = **connect + control parts**

---

### 🔹 poses/

Static states

| Pose             | Example  |
| ---------------- | -------- |
| neutral_pose.py  | Default  |
| happy_pose.py    | Smile    |
| thinking_pose.py | Thinking |
| teacher_pose.py  | Teaching |

👉 Pose = **"freeze frame" of character**

---

### 🔹 actions/

Time-based animations

| Action          | Meaning          |
| --------------- | ---------------- |
| blink_action.py | Eye blink        |
| wave_action.py  | Hand wave        |
| walk_action.py  | Movement         |
| point_action.py | Teaching gesture |

👉 Action = **Pose + Motion over time**

---

## 🧪 scenes/

Final output

### 🔹 tests/

Used for development

| Scene                 | Purpose         |
| --------------------- | --------------- |
| test_body_scene.py    | Check body      |
| test_face_scene.py    | Check face      |
| test_actions_scene.py | Check animation |

---

### 🎭 character/

Story-level scenes

* mascot_intro_scene.py
* mascot_wave_scene.py
* mascot_teach_scene.py

👉 These combine **multiple actions**

---

### 📘 lessons/

Educational scenes

* vectors_intro_scene.py
* matrix_intro_scene.py

👉 This is where **real teaching happens**

---

## 🧰 props/

External objects

| Prop             | Usage              |
| ---------------- | ------------------ |
| pointer_stick.py | Teaching           |
| math_board.py    | Explanations       |
| formula_card.py  | Visual math        |
| axis_plane.py    | Coordinate systems |

---

## 📂 assets/

* svg → vector graphics
* refs → design references

---

## 📚 docs/

Design thinking

* project_plan.md
* animation_notes.md
* creature_design_notes.md

---

# 🧬 How Everything Connects

```
body + eyes + mouth → face_rig
face_rig + arms → body_rig
body_rig → pose
pose + motion → action
action → scene
```

---

# 🧪 Example Build Flow

### Step 1 — Create parts

```python
eyes = Eyes()
body = BodyM()
```

### Step 2 — Attach rig

```python
rig = FaceRig(eyes, mouth)
```

### Step 3 — Apply pose

```python
pose = HappyPose(rig)
```

### Step 4 — Animate

```python
self.play(WaveAction(rig))
```

---

# ⚡ Why this architecture matters

Without this:

❌ everything becomes hardcoded
❌ animations become unmanageable
❌ reuse becomes impossible

With this:

✅ modular
✅ scalable
✅ production-ready
✅ clean mental model

---

# 🚀 Future Expansion

* Physics-based motion
* Lip-sync system
* Emotion engine
* Scene templates
* Multi-character interaction

---

# 🧑‍💻 How to run

```bash
manimgl scenes/tests/test_body_scene.py TestBodyScene
```

---

# 🎯 Philosophy

> Build once. Animate infinitely.

This system is designed so that:

* one character → many scenes
* one action → many contexts
* one system → infinite reuse

---

# 🔥 Final Insight

This is not just animation.

This is:

* **visual storytelling engine**
* **teaching system**
* **brand identity layer**
