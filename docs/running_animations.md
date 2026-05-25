# File: RUN_TESTS.md

# mathlab-mylinehub-creature
# FINAL TEST + RENDER RUN ORDER

IMPORTANT:
Activate local environment first.

```bash
source .venv/bin/activate
```

Verify:

```bash
which python
```

Expected:

```text
.../.venv/bin/python
```

---

# ABOUT render_scene.py

YES.

```text
render_scene.py
```

is ALSO a test.

But it is a:

```text
FINAL CINEMATIC INTEGRATION TEST
```

Meaning:

- all systems together
- all actions together
- all props together
- all audio together
- all timing together
- final storytelling flow

So:

```text
test_* files
```

=
isolated validation

BUT:

```text
render_scene.py
```

=
FULL SYSTEM VALIDATION

It is basically:

```text
FINAL MASTER TEST
```

---

# WHY WE CREATED MANY TEST FILES

Because production systems need:

- isolated debugging
- isolated validation
- faster testing
- sound-only testing
- walk-only testing
- action-only testing

If one thing breaks:
- easier to locate
- easier to debug
- easier to tune

This is GOOD architecture.

---

# HOW TEST FILES WORK

Each file tests ONE area.

Example:

```text
test_audio_scene.py
```

tests:
- audio boot
- pyo
- playback

---

```text
test_walk_audio_scene.py
```

tests:
- footsteps
- timing
- left/right rhythm

---

```text
test_sound_toggle_scene.py
```

tests:
- with_sound=True
- with_sound=False

---

```text
test_master_audio_scene.py
```

tests:
- FULL cinematic audio flow

---

# IMPORTANT

You do NOT run all tests every time.

Usually:

## during development

run only:

```bash
manimgl mathlab_creature/scenes/tests/test_walk_audio_scene.py TestWalkAudioScene
```

OR:

```bash
manimgl mathlab_creature/scenes/tests/test_audio_scene.py TestAudioScene
```

---

## before commit / validation

run:

```bash
manimgl mathlab_creature/scenes/tests/test_master_audio_scene.py TestMasterAudioScene
```

---

## final production validation

run:

```bash
manimgl render_scene.py MasterRenderScene
```

---

# FINAL RUN ORDER

Run IN THIS ORDER.

---

# 1. VERIFY PYO

```bash
python -c "from pyo import *; s=Server().boot(); print('PYO OK')"
```

---

# 2. VERIFY PACKAGE

```bash
python -c "import mathlab_creature; print('PACKAGE OK')"
```

---

# 3. AUDIO BOOT TEST

FILE:
test_audio_scene.py

Command:

```bash
manimgl mathlab_creature/scenes/tests/test_audio_scene.py TestAudioScene
```

Purpose:
- verify audio boots
- verify no crashes
- verify procedural playback

---

# 4. SOUND TOGGLE TEST

FILE:
test_sound_toggle_scene.py

Command:

```bash
manimgl mathlab_creature/scenes/tests/test_sound_toggle_scene.py TestSoundToggleScene
```

Purpose:
- verify with_sound=True
- verify with_sound=False
- verify silent mode safe

IMPORTANT:
Animation should remain IDENTICAL.
Only sound changes.

---

# 5. WALK AUDIO TEST

FILE:
test_walk_audio_scene.py

Command:

```bash
manimgl mathlab_creature/scenes/tests/test_walk_audio_scene.py TestWalkAudioScene
```

Purpose:
- verify footsteps
- verify timing
- verify left/right alternation
- verify mascot walk feel

---

# 6. PROCEDURAL AUDIO TEST

FILE:
test_procedural_audio_scene.py

Command:

```bash
manimgl mathlab_creature/scenes/tests/test_procedural_audio_scene.py TestProceduralAudioScene
```

Purpose:
- verify synthesis
- verify envelopes
- verify timing
- verify layering

---

# 7. ACTIONS TEST

FILE:
test_actions_scene.py

Command:

```bash
manimgl mathlab_creature/scenes/tests/test_actions_scene.py TestActionsScene
```

Purpose:
- verify walk
- verify blink
- verify wave
- verify hop
- verify point
- verify look
- verify integration

---

# 8. WALK CYCLE TEST

FILE:
test_walk_cycle_scene.py

Command:

```bash
manimgl mathlab_creature/scenes/tests/test_walk_cycle_scene.py TestWalkCycleScene
```

Purpose:
- verify gait
- verify bounce
- verify sway
- verify cinematic locomotion

---

# 9. BALANCE TEST

FILE:
test_balance_scene.py

Command:

```bash
manimgl mathlab_creature/scenes/tests/test_balance_scene.py TestBalanceScene
```

---

# 10. ROTATION TEST

FILE:
test_rotation_scene.py

Command:

```bash
manimgl mathlab_creature/scenes/tests/test_rotation_scene.py TestRotationScene
```

---

# 11. LEG KINEMATICS TEST

FILE:
test_leg_kinematics_scene.py

Command:

```bash
manimgl mathlab_creature/scenes/tests/test_leg_kinematics_scene.py TestLegKinematicsScene
```

---

# 12. INTERACTIVE CONTROLLER TEST

FILE:
test_interactive_controller_scene.py

Command:

```bash
manimgl mathlab_creature/scenes/tests/test_interactive_controller_scene.py TestInteractiveControllerScene
```

---

# 13. MASTER AUDIO DEMO

FILE:
test_master_audio_scene.py

THIS IS THE MAIN AUDIO VALIDATION.

Command:

```bash
manimgl mathlab_creature/scenes/tests/test_master_audio_scene.py TestMasterAudioScene
```

Purpose:
- cinematic audio
- mascot storytelling
- layered procedural sound
- integrated audio flow
- educational rhythm

---

# 14. FINAL MASTER RENDER

FILE:
render_scene.py

THIS IS THE FINAL FULL SYSTEM TEST.

Command:

```bash
manimgl render_scene.py MasterRenderScene
```

Purpose:
- final cinematic validation
- full storytelling
- all systems together
- all actions together
- all props together
- all audio together

---

# 15. WRITE VIDEO OUTPUT

Example:

```bash
manimgl render_scene.py MasterRenderScene -w
```

---

# 16. OPEN AFTER RENDER

Example:

```bash
manimgl render_scene.py MasterRenderScene -o
```

---

# 17. SAVE FINAL FRAME

Example:

```bash
manimgl render_scene.py MasterRenderScene -s
```

---

# MOST IMPORTANT TESTS

RUN THESE FIRST:

```bash
manimgl mathlab_creature/scenes/tests/test_audio_scene.py TestAudioScene
```

```bash
manimgl mathlab_creature/scenes/tests/test_sound_toggle_scene.py TestSoundToggleScene
```

```bash
manimgl mathlab_creature/scenes/tests/test_walk_audio_scene.py TestWalkAudioScene
```

```bash
manimgl mathlab_creature/scenes/tests/test_master_audio_scene.py TestMasterAudioScene
```

```bash
manimgl render_scene.py MasterRenderScene
```