# 📁 File Responsibilities

MathLab MYLINEHUB Creature

---

# 1. 🧠 Purpose of this Document

This document defines:

* what each folder is responsible for
* what each file should contain
* what each file MUST NOT do

This prevents:

* code duplication
* architectural confusion
* tight coupling
* future breakage

---

# 2. 🔑 Golden Rule

**One file = One responsibility**

If a file starts doing multiple unrelated things → **split it immediately**

---

# 3. 🏗️ Folder Responsibilities

---

## 3.1 `config/`

### Purpose

Global constants and tuning

### Contains

* colors
* sizes
* timings
* defaults

### Allowed

* constants only

### Not Allowed

* geometry logic
* animation logic
* scene logic

---

## 3.2 `core/`

### Purpose

Low-level reusable utilities

### Contains

* geometry helpers
* anchor system
* layout helpers
* logging
* naming

### Allowed

* pure helper functions
* reusable utilities

### Not Allowed

* building creature parts
* animation
* scene creation

---

## 3.3 `creature/parts/`

### Purpose

Build raw visual components

### Contains

* body (M)
* eyes
* nose
* mouth
* hat
* arms
* hands
* legs
* feet

### Allowed

* return Manim objects (Line, Circle, VGroup)

### Not Allowed

* animation
* scene logic
* rig logic

---

## 3.4 `creature/rigs/`

### Purpose

Organize parts into structured systems

### Contains

* face rig
* arm rig
* leg rig
* body rig

### Allowed

* grouping parts
* structured dictionaries
* component linking

### Not Allowed

* animation
* scene logic

---

## 3.5 `creature/poses/`

### Purpose

Define static character states

### Contains

* neutral pose
* happy pose
* teacher pose
* pointing pose
* thinking pose

### Allowed

* modifying positions/angles

### Not Allowed

* animation
* building parts
* scene logic

---

## 3.6 `creature/actions/`

### Purpose

Define animations

### Contains

* blink
* look
* wave
* point
* hop
* walk

### Allowed

* return animations (AnimationGroup, ApplyMethod)

### Not Allowed

* building parts
* scene logic
* rebuilding rigs

---

## 3.7 `props/`

### Purpose

Build teaching objects

### Contains

* pointer stick
* math board
* formula card
* axis plane

### Allowed

* return VGroup objects

### Not Allowed

* attaching to creature automatically
* animation logic
* scene logic

---

## 3.8 `scenes/`

### Purpose

Execution layer

---

### 3.8.1 `scenes/tests/`

**Purpose**

* debugging
* validation

---

### 3.8.2 `scenes/character/`

**Purpose**

* showcase mascot

---

### 3.8.3 `scenes/lessons/`

**Purpose**

* teaching content

---

# 4. 📄 File-Level Responsibilities

---

## Example: body_m.py

| Must            | Must NOT     |
| --------------- | ------------ |
| build M shape   | animate      |
| return geometry | attach limbs |

---

## Example: arm_rig.py

| Must             | Must NOT     |
| ---------------- | ------------ |
| organize arms    | animate      |
| expose structure | create scene |

---

## Example: wave_action.py

| Must             | Must NOT   |
| ---------------- | ---------- |
| return animation | call Scene |
| animate arm      | build arm  |

---

## Example: mascot_wave_scene.py

| Must             | Must NOT         |
| ---------------- | ---------------- |
| orchestrate flow | define animation |
| call actions     | build parts      |

---

# 5. 🔗 Dependency Direction (CRITICAL)

## Allowed Flow

````
config
   ↓
core
   ↓
parts
   ↓
rigs
   ↓
poses
   ↓
actions
   ↓
props
   ↓
scenes
``` id="depflow01"

---

## ❌ Forbidden Directions

| From | Cannot Import |
|-----|--------------|
| parts | rigs / scenes |
| rigs | scenes |
| actions | scenes |
| props | creature |
| config | anything |

---

## Rule

**Higher layers can depend on lower layers only**

Never reverse.

---

# 6. 🧠 Dependency Table

| Layer | Can Use |
|------|--------|
| config | nothing |
| core | config |
| parts | core + config |
| rigs | parts |
| poses | rigs |
| actions | rigs + config |
| props | core + config |
| scenes | everything |

---

# 7. ⚠️ Anti-Patterns (STRICTLY FORBIDDEN)

---

## ❌ 1. Scene Logic Inside Actions

Wrong:
```python
self.play(...)
````

Correct:

```python
return AnimationGroup(...)
```

---

## ❌ 2. Building Parts Inside Actions

Wrong:

```python
arm = build_arm()
```

Correct:

```python
arm = rig["arms"]["left_arm"]
```

---

## ❌ 3. Hardcoding Coordinates in Parts

Wrong:

```python
eye.move_to([1, 2, 0])
```

Correct:

```python
eye.move_to(anchor)
```

---

## ❌ 4. Props Attaching Themselves

Props must NEVER do:

```python
attach_to_hand()
```

Scene decides that.

---

# 8. 🧩 Integration Rules

---

## Scene = Orchestrator Only

Scene should:

* build rig
* build props
* call actions
* control timing

Scene should NOT:

* define behavior
* build internals

---

## Rig = Access Layer

Rig provides:

```python
rig["arms"]["right_hand"]
rig["face"]["eyes"]
```

---

## Actions = Reusable Motion

Action must:

* work on any rig
* not assume scene

---

# 9. 🧪 Testing Philosophy

Each layer must be testable independently:

| Layer   | Test Scene         |
| ------- | ------------------ |
| parts   | test_body_scene    |
| rigs    | test_pose_scene    |
| actions | test_actions_scene |
| props   | test_props_scene   |

---

# 10. 📊 Flow of Execution

````
Scene
  ↓
Rig built
  ↓
Props built
  ↓
Actions applied
  ↓
Rendering
``` id="execflow01"

---

# 11. 🚀 Scalability Rules

To scale system:

- never mix layers  
- always reuse rig  
- keep actions independent  
- keep props stateless  

---

# 12. 🎯 Final Principle

This system is not scripts.

It is a:

**Layered, reusable animation architecture**

---

END OF DOCUMENT
````
