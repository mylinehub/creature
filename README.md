# 🎬 mathlab-mylinehub-creature

A reusable ManimGL creature system for educational animation, storytelling, mathematics visualization, telecom demonstrations, and AI teaching content.

The purpose of this project is not to build a generic animation framework.

The purpose is to build:

- one connected creature
- one reusable architecture
- one public API
- one believable movement system
- one reusable audio system
- one educational mascot platform

---

# Philosophy

The creature must behave like:

```text
ONE ROOT
ONE BODY
ONE SKELETON
ONE ORGANISM
```

Not:

```text
many disconnected objects
```

Every body part belongs to a single hierarchy.

Nothing floats independently.

Nothing moves independently.

Everything is connected.

---

# Public API

Only one import is considered public.

```python
from mathlab_creature import build_creature
```

Everything else is internal.

External code should never directly import:

```python
Eyes
Nose
Mouth
Arm
Leg
Hand
Foot
FaceRig
ArmRig
LegRig
BodyRig
```

These are implementation details.

---

# High Level Architecture

The creature is organized around a connected hierarchy.

```text
CreatureRoot
    │
    ▼
BodyCore
    │
    ▼
Spine
    │
    ├── Head
    │     ├── Eyes
    │     ├── Nose
    │     └── Mouth
    │
    ├── Left Shoulder
    │      └── Left Arm
    │
    ├── Right Shoulder
    │      └── Right Arm
    │
    └── Pelvis
           ├── Left Leg
           └── Right Leg
```

Every object has exactly one parent.

Movement propagates downward.

---

# Audio Architecture

Audio is a separate subsystem.

Audio is NOT part of the creature hierarchy.

```text
Project
├── Creature System
└── Audio System
```

Audio may be used by:

- scenes
- actions
- narration
- procedural sound
- teaching demonstrations

The creature must still function without audio.

Audio is optional.

---

# Project Structure

```text
mathlab_creature/

├── api/
├── config/
├── core/
│   └── audio/
├── creature/
└── scenes/
```

---

# api/

Public interface.

```text
creature_api.py
```

Provides:

```python
build_creature()
```

This is the only supported public entry point.

---

# config/

Visual and behavioral constants.

```text
colors.py
sizes.py
defaults.py
timings.py
logging_config.py
```

Contains:

- colors
- dimensions
- proportions
- timing constants
- logging settings

No hardcoded values should exist inside creature parts.

---

# core/

Reusable low-level utilities.

```text
geometry.py
anchors.py
layout.py
motion.py
transforms.py
kinematics.py
debug_draw.py
input_controller.py
logger.py
naming.py
```

Purpose:

- geometry helpers
- transform math
- local/world coordinate systems
- naming
- debugging
- utility functions

---

# core/audio/

Audio subsystem.

```text
audio_config.py
audio_server.py
helpers.py
procedural.py
sound_registry.py
timing.py
```

Purpose:

- procedural sounds
- sound effects
- future narration
- future voice support
- educational audio demonstrations

This subsystem remains independent from creature hierarchy.

---

# creature/

Contains the creature implementation.

Not intended for external use.

---

# creature/root/

Contains root systems.

```text
creature_root.py
skeleton.py
body_core.py
```

Responsibilities:

- root ownership
- hierarchy ownership
- center of mass
- breathing
- sway
- balance
- body coordination

---

# creature/parts/

Contains body components.

```text
head
eyes
nose
mouth
arms
hands
legs
feet
joints
```

Body parts are NOT independent objects.

They are connected pieces of a single creature.

---

# creature/rigs/

Internal control layers.

```text
body_rig.py
face_rig.py
arm_rig.py
leg_rig.py
```

Used only during creature construction and coordination.

Not intended for external use.

---

# creature/actions/

Animation behaviors.

```text
idle_action.py
blink_action.py
look_action.py
walk_action.py
step_action.py
turn_action.py
wave_action.py
point_action.py
hop_action.py
```

Actions operate on the connected creature.

Actions never directly manipulate disconnected body parts.

---

# creature/controllers/

```text
movement_controller.py
rotation_controller.py
visibility_controller.py
camera_controller.py
```

Responsibilities:

- movement
- rotation
- visibility
- camera coordination

All global movement must originate from CreatureRoot.

---

# scenes/

Contains example scenes.

Current primary development scene:

```text
test_creature_scene.py
```

Purpose:

- verify build_creature()
- verify hierarchy
- verify movement
- verify actions
- verify transforms

This is the primary validation scene during development.

---

# Movement Rules

Global movement belongs only to:

```text
CreatureRoot
```

Never:

```text
Eye
Hand
Leg
Foot
Nose
Mouth
```

Example:

Bad:

```python
eye.shift(...)
hand.rotate(...)
leg.move_to(...)
```

Good:

```python
creature.move(...)
```

---

# Transform Rules

Each object owns:

```text
Local Transform
```

relative to its parent.

World position is derived from:

```text
Parent World Transform
+
Local Transform
```

Child objects never directly control world space.

---

# Body Rules

Eyes remain attached to head.

Nose remains attached to face.

Mouth remains attached to face.

Hands remain attached to arms.

Feet remain attached to legs.

Nothing floats.

Nothing detaches.

Everything remains connected.

---

# Development Goal

The creature should feel:

- connected
- grounded
- stable
- reusable
- educational
- believable

Not:

- over-engineered
- disconnected
- chaotic
- unnecessarily complex

---

# Dependencies

```text
manimgl
numpy
pyo
```

---

# Running

Render the primary creature validation scene.

```bash
manimgl scenes/tests/test_creature_scene.py TestCreatureScene
```

---

# Core Principle

```text
ONE ROOT
ONE BODY
ONE SKELETON
ONE ORGANISM
```

Everything else derives from that.