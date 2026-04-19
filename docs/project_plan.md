# 🧠 MathLab MYLINEHUB Creature — Project Plan

## 📦 Project Name

mathlab-mylinehub-creature

---

# 1. 🚀 Vision

Build a programmable teaching mascot system using ManimGL that:

* Explains mathematics visually
* Behaves like a human instructor (gesture, timing, attention)
* Combines:

  * Character (expression, motion)
  * Math visuals (vectors, matrices, graphs)
* Scales into:

  * Full Linear Algebra / ML teaching pipeline
  * Video lesson generation system

This is NOT animation.
This is a **Visual Teaching Engine**.

---

# 2. 🧩 Core Philosophy

We build in strict layered architecture:

Math Concepts
→ Visual Objects (Props)
→ Creature (Rig + Parts)
→ Actions & Poses
→ Scene Logic
→ Rendered Output

---

## 🔑 Golden Rules

| Rule          | Description                                |
| ------------- | ------------------------------------------ |
| Separation    | Creature, Props, Scenes must not mix logic |
| Reusability   | Every component must be reusable           |
| No Hardcoding | Scenes assemble, not define                |
| Config Driven | Sizes, colors, timings centralized         |
| Rig First     | All animation must go through rig          |

---

# 3. 🏗️ Architecture Overview

## System Flow

config → core → creature(parts → rigs → poses → actions) → props → scenes → render

---

# 4. 📁 Folder Structure

mathlab-mylinehub-creature/

* config/
* core/
* creature/

  * parts/
  * rigs/
  * poses/
  * actions/
* props/
* scenes/

  * test/
  * mascot/
  * lessons/
* engine/ (future)
* math/ (future)
* docs/

---

# 5. ⚙️ Configuration Layer

| File              | Purpose             |
| ----------------- | ------------------- |
| colors.py         | all color constants |
| sizes.py          | geometry sizing     |
| timings.py        | animation timing    |
| defaults.py       | scene defaults      |
| logging_config.py | logging             |

---

# 6. 🧍 Creature System

## Parts

* body_m.py → M structure
* eyes.py → eyes + pupils
* nose.py → center detail
* mouth.py → arc expression
* hat.py → triangle + brim
* arms.py → limbs
* hands.py → tips
* legs.py → lower body
* feet.py → base

---

## Rig System (CORE)

Structure:

rig = {
body,
face,
arms,
legs,
group
}

---

# 7. 🎭 Poses

| Pose     | Description  |
| -------- | ------------ |
| neutral  | default      |
| happy    | raised arms  |
| teacher  | presentation |
| pointing | extended arm |
| thinking | reflective   |

---

# 8. ⚡ Actions

| Action | Description     |
| ------ | --------------- |
| blink  | eye squash      |
| look   | pupil move      |
| wave   | arm oscillation |
| point  | arm extension   |
| hop    | squash + jump   |
| walk   | stepping        |

---

# 9. 📦 Props

| Prop          | Use               |
| ------------- | ----------------- |
| pointer_stick | teaching          |
| math_board    | explanation       |
| formula_card  | focus             |
| axis_plane    | coordinate system |

---

# 10. 🎬 Scene Types

## Test Scenes

* debug parts
* debug rigs
* debug actions

## Mascot Scenes

* intro
* wave
* walk
* point

## Lesson Scenes

* vectors
* coordinates
* matrix

---

# 11. 🔗 Relationships

parts → rigs → poses → actions → scenes
props → scenes

---

# 12. 📐 Rendering Flow

1. Scene runs
2. Rig builds
3. Props load
4. Animations run
5. Frames render

---

# 13. 📚 Libraries Used

## ManimGL

* animation engine
* rendering
* transformations

## NumPy

* vector math
* coordinate calculations

## Python Std

* logging
* math
* os

---

# 14. 🧠 Teaching Model

Introduce → Visualize → Highlight → Reinforce

Example:

Vector → Arrow → Point → Hold

---

# 15. 🔄 Execution Flow

Scene Start
→ Build Rig
→ Fade In
→ Blink
→ Show Concept
→ Point
→ Hold

---

# 16. 🚀 Future Roadmap

## Engine Layer

engine/lesson_flow.py

## Math Layer

math/vector.py
math/matrix.py

## Behavior Layer

behavior/reaction.py

---

# 17. ⚠️ Constraints

| Rule          | Reason               |
| ------------- | -------------------- |
| No hardcoding | maintain flexibility |
| Use rig only  | consistency          |
| Config first  | scalability          |

---

# 18. 🧠 Current Status

| System     | Status  |
| ---------- | ------- |
| Creature   | Done    |
| Rig        | Done    |
| Poses      | Done    |
| Actions    | Done    |
| Props      | Done    |
| Lessons    | Basic   |
| Engine     | Pending |
| Math Layer | Pending |

---

# 19. 🎯 Final Identity

A modular math teaching engine with character intelligence.

---

END OF DOCUMENT
