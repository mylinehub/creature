Focus on `config/sizes.py`, this file gives all your answers.

---

# 1. First: how this project is built

From the zip, the structure is basically this:

```python
mathlab_creature/
    config/
        colors.py
        defaults.py
        logging_config.py
        sizes.py
        timings.py

    core/
        anchors.py
        geometry.py
        layout.py
        motion.py
        naming.py

    creature/
        myline_m_creature.py
        parts/
            body_m.py
            eyes.py
            nose.py
            mouth.py
            hat.py
            arms.py
            legs.py
            feet.py
        rigs/
            ...
        poses/
            ...
        actions/
            ...
```

So the design idea is:

* `config/sizes.py` = numeric truth
* `core/geometry.py` = math helpers like point, midpoint, direction
* `core/anchors.py` = “where should parts go?”
* `creature/parts/*.py` = “what shape should each part be?”
* `creature/myline_m_creature.py` = “assemble all parts into one mascot”

That means `sizes.py` is not doing drawing directly.

It is doing something more important:

> It defines the **geometric grammar** of the creature.

That is, it decides:

* how big the body is
* where the face sits inside the body
* how far apart the eyes are
* how large the pupil is compared to the eye
* how far below the eyes the nose sits
* where the mouth goes
* where arms and legs attach

So `sizes.py` is the **dimension language** of the whole mascot.

---

# 2. The most important mental model

Think like this:

The mascot is not “drawn manually”.

It is **constructed from coordinate relationships**.

You can imagine the pipeline as:

```python
sizes.py  ->  anchors.py  ->  parts/*.py  ->  myline_m_creature.py
numbers      positions        shapes          full character
```

So if one number changes in `sizes.py`, many later placements change automatically.

Example:

* if `BODY_M_HEIGHT` changes
* then face zone top changes
* then face zone center changes
* then eye anchor changes
* then nose anchor changes
* then mouth anchor changes

So a single size value can move many parts.

That is why we must understand the math deeply.

---

# 3. Let us bring `sizes.py` into memory properly

Here is the core structure of the file, grouped in simple form:

```python
# Base creature scale
CREATURE_BASE_HEIGHT = 4.8
CREATURE_BASE_WIDTH = 3.6
CREATURE_SCALE = 1.0

# Body M sizing
BODY_M_WIDTH = 3.6
BODY_M_HEIGHT = 4.2
BODY_M_STROKE_WIDTH = 18
BODY_M_CORNER_RADIUS = 0.12
BODY_FACE_ZONE_TOP_RATIO = 0.24
BODY_FACE_ZONE_HEIGHT_RATIO = 0.22

# Eye sizing
EYE_RADIUS = 0.22
EYE_WIDTH = 0.42
EYE_HEIGHT = 0.52
EYE_STROKE_WIDTH = 2
PUPIL_RADIUS = 0.08
PUPIL_MAX_OFFSET = 0.07
EYE_GAP = 0.42

# Nose sizing
NOSE_WIDTH = 0.14
NOSE_HEIGHT = 0.20
NOSE_STROKE_WIDTH = 2

# Mouth sizing
MOUTH_WIDTH = 0.48
MOUTH_HEIGHT = 0.18
MOUTH_STROKE_WIDTH = 4
SMILE_ARC_ANGLE = 1.8
NEUTRAL_MOUTH_WIDTH = 0.30

# Hat sizing
HAT_WIDTH = 1.25
HAT_HEIGHT = 0.72
HAT_BRIM_WIDTH = 1.05
HAT_BRIM_HEIGHT = 0.08
HAT_OFFSET_ABOVE_HEAD = 0.12

# Arm sizing
ARM_LENGTH = 1.15
ARM_STROKE_WIDTH = 10
ARM_SHOULDER_OFFSET_X = 1.05
ARM_SHOULDER_OFFSET_Y = 0.10
HAND_RADIUS = 0.11

# Leg sizing
LEG_LENGTH = 1.15
LEG_STROKE_WIDTH = 10
LEG_HIP_OFFSET_X = 0.62
LEG_HIP_OFFSET_Y = 1.88
FOOT_WIDTH = 0.30
FOOT_HEIGHT = 0.10
```

And then some values are **derived**:

```python
BODY_M_HALF_WIDTH = BODY_M_WIDTH / 2
BODY_M_HALF_HEIGHT = BODY_M_HEIGHT / 2

FACE_ZONE_TOP_Y = BODY_M_HEIGHT * (0.5 - BODY_FACE_ZONE_TOP_RATIO)
FACE_ZONE_HEIGHT = BODY_M_HEIGHT * BODY_FACE_ZONE_HEIGHT_RATIO
FACE_ZONE_BOTTOM_Y = FACE_ZONE_TOP_Y - FACE_ZONE_HEIGHT
FACE_ZONE_CENTER_Y = (FACE_ZONE_TOP_Y + FACE_ZONE_BOTTOM_Y) / 2

EYE_PAIR_WIDTH = (2 * EYE_WIDTH) + EYE_GAP
EYE_CENTER_TO_CENTER = EYE_WIDTH + EYE_GAP

LEFT_EYE_OFFSET_X = -(EYE_CENTER_TO_CENTER / 2)
RIGHT_EYE_OFFSET_X = EYE_CENTER_TO_CENTER / 2

NOSE_CENTER_Y = FACE_ZONE_CENTER_Y - 0.05
MOUTH_CENTER_Y = NOSE_CENTER_Y - 0.34
```

This last part is very important.

Some constants are **primitive**.
Some constants are **computed from other constants**.

That is exactly how a good geometric system should be built.

---

# 4. Before body/eye math: understand the validation functions

At the top of `sizes.py`, the file has helper checks like:

```python
def _validate_positive(name, value):
    ...
def _validate_non_negative(name, value):
    ...
def _validate_ratio(name, value):
    ...
```

This may look boring, but mathematically it matters a lot.

## 4.1 Positive

If something is a true size, it must be:

```python
value > 0
```

Examples:

* width
* height
* radius
* stroke width
* length

Because negative size is meaningless in this design layer.

## 4.2 Non-negative

Some things may be zero, but not negative.

Examples:

* offset
* corner radius
* spacing buffer

So:

```python
value >= 0
```

## 4.3 Ratio in [0, 1]

A ratio means “part of a whole”.

So:

```python
0 <= ratio <= 1
```

For example:

```python
BODY_FACE_ZONE_TOP_RATIO = 0.24
BODY_FACE_ZONE_HEIGHT_RATIO = 0.22
```

These are fractions of body height.

That means these are not absolute coordinates.
They are **relative proportions**.

This is powerful because proportions scale better than hardcoded locations.

---

# 5. Category 1 — Base creature scale

Code:

```python
CREATURE_BASE_HEIGHT = 4.8
CREATURE_BASE_WIDTH = 3.6
CREATURE_SCALE = 1.0
```

---

## 5.1 Plain English meaning

These are the broad envelope numbers.

They tell us the intended overall footprint of the creature.

* base height ≈ overall vertical size target
* base width ≈ overall width target
* scale = multiplier for enlarging or shrinking everything uniformly

So these are not detailed facial numbers.
These are “whole creature” numbers.

---

## 5.2 Mathematical meaning

If the creature is scaled uniformly by factor `s`, then every linear dimension becomes:

```python
new_size = s × old_size
```

So if:

```python
CREATURE_SCALE = 1.5
```

then:

* width multiplies by 1.5
* height multiplies by 1.5
* eye size multiplies by 1.5
* arm length multiplies by 1.5
* pupil radius multiplies by 1.5

That is uniform similarity scaling.

This preserves shape ratios.

---

## 5.3 Why this matters

This is how you keep a mascot looking like the same mascot at different sizes.

If you manually changed body but forgot eye size, the design would break.

Uniform scaling preserves:

* proportion
* symmetry
* visual identity

So even this simple scale constant is part of the math system.

---

# 6. Category 2 — Body M sizing

Code:

```python
BODY_M_WIDTH = 3.6
BODY_M_HEIGHT = 4.2
BODY_M_STROKE_WIDTH = 18
BODY_M_CORNER_RADIUS = 0.12
BODY_FACE_ZONE_TOP_RATIO = 0.24
BODY_FACE_ZONE_HEIGHT_RATIO = 0.22
```

Let us go very slowly.

---

## 6.1 `BODY_M_WIDTH = 3.6`

### English meaning

This is how wide the body’s main bounding region is.

The M body is centered around some center point `(cx, cy)`.

So width says how far left and right the body extends.

### Math meaning

If width is `W = 3.6`, then half-width is:

```python
W / 2 = 1.8
```

So body x-range becomes:

```python
x ∈ [cx - 1.8, cx + 1.8]
```

If center is origin `(0,0)`, then:

```python
x ∈ [-1.8, 1.8]
```

### Why useful

This lets every left-right placement be measured relative to body center.

For example:

* shoulders can be placed inside this width
* face zone can be centered within this width
* eye anchors can stay visually balanced

### Visual effect

A width of `3.6` gives the mascot a stable, readable front shape.
If too narrow, the M becomes cramped.
If too wide, the face may feel too small inside it.

---

## 6.2 `BODY_M_HEIGHT = 4.2`

### English meaning

This is how tall the M body is.

### Math meaning

If height is `H = 4.2`, then half-height is:

```python
H / 2 = 2.1
```

So body y-range is:

```python
y ∈ [cy - 2.1, cy + 2.1]
```

If center is at origin:

```python
y ∈ [-2.1, 2.1]
```

### Why useful

Now the body has a vertical frame.
That frame becomes the reference for:

* top of body
* bottom of body
* face zone location
* hat placement
* hip placement

### Visual effect

Since height `4.2` is larger than width `3.6`, the mascot is slightly taller than wide.

Ratio:

```python
BODY_M_HEIGHT / BODY_M_WIDTH = 4.2 / 3.6 = 1.1667
```

So the body is about **16.7% taller than wide**.

That is good because it avoids:

* square, blocky look
* overly flat look

This helps the mascot feel upright and character-like.

---

## 6.3 `BODY_M_STROKE_WIDTH = 18`

### English meaning

The M body is drawn as thick line segments, not as a thin pen line.

This number controls that thickness.

### Math meaning

This is not position geometry.
It is **render thickness geometry**.

But it still matters mathematically because the visible body occupies more area than just the centerline.

A line segment with stroke width `t` behaves visually like a band around the line.

So the perceived body thickness is related to `t`.

### Why useful

If stroke is too thin:

* mascot feels weak
* body outline is not dominant
* face may overpower the body

If stroke is too thick:

* inner spaces collapse visually
* M shape becomes muddy

So this number balances identity and readability.

### Visual effect

Compared to face part stroke widths like `2` or `4`, body stroke `18` is much larger.

This creates clear hierarchy:

* body = main structure
* face = delicate internal detail

That is a very good design principle.

---

## 6.4 `BODY_M_CORNER_RADIUS = 0.12`

### English meaning

This says how soft corners may become if rounded construction is used.

### Math meaning

This is a local smoothing radius.

A larger corner radius means more curvature replacing sharp angle.

### Why useful

Characters often look friendlier with slight softness.

Perfectly sharp geometry can look too mechanical.

Even if not used strongly yet, this number is preparing for future shape refinement.

---

## 6.5 `BODY_FACE_ZONE_TOP_RATIO = 0.24`

### English meaning

This tells us where the face region starts, measured relative to total body height.

It means:

> the top of the face zone is some distance below the body top

### Math meaning

Distance down from top is:

```python
BODY_M_HEIGHT × BODY_FACE_ZONE_TOP_RATIO
= 4.2 × 0.24
= 1.008
```

Body top is at:

```python
+ BODY_M_HEIGHT/2 = +2.1
```

So face zone top is:

```python
2.1 - 1.008 = 1.092
```

That matches the file’s formula:

```python
FACE_ZONE_TOP_Y = BODY_M_HEIGHT * (0.5 - BODY_FACE_ZONE_TOP_RATIO)
```

because:

```python
4.2 × (0.5 - 0.24)
= 4.2 × 0.26
= 1.092
```

### Why useful

This means the face is not placed at the very top of the body.
It is brought down a bit.

That is good because:

* hat needs space above
* top of M should still visually read as “M”
* face should sit in a comfortable upper-middle region

### Visual effect

If the face goes too high, it feels pasted onto the top edge.
If too low, the character feels sleepy or empty at the top.

So `0.24` is a proportion choice for balance.

---

## 6.6 `BODY_FACE_ZONE_HEIGHT_RATIO = 0.22`

### English meaning

This controls how tall the face zone is relative to body height.

### Math meaning

Face zone height:

```python
FACE_ZONE_HEIGHT = BODY_M_HEIGHT × BODY_FACE_ZONE_HEIGHT_RATIO
= 4.2 × 0.22
= 0.924
```

So the face region vertically spans about `0.924` units.

Then:

```python
FACE_ZONE_BOTTOM_Y = FACE_ZONE_TOP_Y - FACE_ZONE_HEIGHT
= 1.092 - 0.924
= 0.168
```

And center:

```python
FACE_ZONE_CENTER_Y = (1.092 + 0.168)/2 = 0.63
```

So the face zone center is around:

```python
y = 0.63
```

### Why useful

This creates a **container region** for facial features.

That means the face is not floating freely.
It lives inside a bounded design zone.

This is exactly the right way to build a rigged character.

### Visual effect

A face zone that is too tall makes the face too stretched and sparse.
A face zone that is too short makes eyes, nose, mouth overly compressed.

`0.22` means the face zone is only about 22% of the body height, which keeps the facial area compact and readable.

---

# 7. Derived body values — very important

Code:

```python
BODY_M_HALF_WIDTH = BODY_M_WIDTH / 2
BODY_M_HALF_HEIGHT = BODY_M_HEIGHT / 2

FACE_ZONE_TOP_Y = BODY_M_HEIGHT * (0.5 - BODY_FACE_ZONE_TOP_RATIO)
FACE_ZONE_HEIGHT = BODY_M_HEIGHT * BODY_FACE_ZONE_HEIGHT_RATIO
FACE_ZONE_BOTTOM_Y = FACE_ZONE_TOP_Y - FACE_ZONE_HEIGHT
FACE_ZONE_CENTER_Y = (FACE_ZONE_TOP_Y + FACE_ZONE_BOTTOM_Y) / 2
```

This is excellent design.

Why?

Because this converts raw numbers into **usable geometry**.

Instead of repeatedly recalculating from width and height everywhere else, the file gives direct derived values.

That reduces mistakes.

---

## 7.1 Final computed body-face numbers

Using your file values:

```python
BODY_M_WIDTH = 3.6
BODY_M_HEIGHT = 4.2
BODY_FACE_ZONE_TOP_RATIO = 0.24
BODY_FACE_ZONE_HEIGHT_RATIO = 0.22
```

we get:

```python
BODY_M_HALF_WIDTH  = 1.8
BODY_M_HALF_HEIGHT = 2.1

FACE_ZONE_TOP_Y    = 1.092
FACE_ZONE_HEIGHT   = 0.924
FACE_ZONE_BOTTOM_Y = 0.168
FACE_ZONE_CENTER_Y = 0.63
```

That means:

* body top is at `2.1`
* face zone starts at `1.092`
* face zone ends at `0.168`
* face zone center is `0.63`

This tells us where the facial system lives.

---

# 8. Category 3 — Eye sizing

Now we come to the most important part for your current study.

Code:

```python
EYE_RADIUS = 0.22
EYE_WIDTH = 0.42
EYE_HEIGHT = 0.52
EYE_STROKE_WIDTH = 2

PUPIL_RADIUS = 0.08
PUPIL_MAX_OFFSET = 0.07

EYE_GAP = 0.42
```

And the eye-building file uses:

```python
eye = Circle()
eye.set_width(EYE_WIDTH)
eye.set_height(EYE_HEIGHT)
```

This is very important.

---

## 8.1 First subtle point: eye is not really staying a perfect circle visually

You stored:

```python
EYE_RADIUS = 0.22
```

but the actual eye white is built as:

```python
Circle()
    .set_width(0.42)
    .set_height(0.52)
```

So after scaling, it becomes an **ellipse-like eye**, not a perfect circle.

That means:

* horizontal semi-axis is about `0.42 / 2 = 0.21`
* vertical semi-axis is about `0.52 / 2 = 0.26`

So the visible eye is a vertically stretched shape.

This is one reason it looks expressive and not too robotic.

So already we must separate:

* conceptual radius constant
* actual rendered width/height

This is a very good beginner observation.

---

## 8.2 `EYE_WIDTH = 0.42`

### English meaning

This is the full horizontal size of one eye white.

### Math meaning

Horizontal semi-width:

```python
a = EYE_WIDTH / 2 = 0.21
```

If you model the eye as an ellipse centered at `(x0, y0)`, then:

```python
((x - x0)^2 / a^2) + ((y - y0)^2 / b^2) <= 1
```

with:

```python
a = 0.21
b = EYE_HEIGHT/2 = 0.26
```

### Why useful

The eye needs enough horizontal room to contain the pupil and slight gaze movement.

If the width were too small:

* pupil would dominate
* gaze shifts would be cramped
* eye would look pinched

### Visual effect

Width `0.42` is modest, not huge.
It keeps the eyes friendly and compact.

---

## 8.3 `EYE_HEIGHT = 0.52`

### English meaning

This is the full vertical size of the eye.

### Math meaning

Vertical semi-height:

```python
b = 0.52 / 2 = 0.26
```

So the eye is taller than it is wide:

```python
EYE_HEIGHT / EYE_WIDTH = 0.52 / 0.42 ≈ 1.238
```

So height is about **23.8% greater than width**.

### Why useful

This gives a more alive, open, character-like eye.

A perfectly round or horizontally stretched eye would feel different:

* round = neutral/simple
* wide horizontal = sleepy/cartoony sideways
* taller vertical = alert and cute

### Visual effect

This is one of the biggest reasons the eye likely feels expressive.

---

## 8.4 `EYE_RADIUS = 0.22`

### English meaning

This is a conceptual radius number for eye scale.

### Important observation

In current code, the white eye is not created using:

```python
Circle(radius=EYE_RADIUS)
```

Instead it is created by width and height.

So `EYE_RADIUS` is not the final visible eye boundary in the strict rendered sense.

### Then why keep it?

Because it still gives a reference scale.

Look:

```python
EYE_WIDTH / 2 = 0.21
EYE_RADIUS = 0.22
EYE_HEIGHT / 2 = 0.26
```

So `0.22` sits near the horizontal half-size and below the vertical half-size.

That means it acts like an approximate “typical eye size” constant.

This can be useful conceptually when designing pupil ratios.

### Deep design thought

This often happens in graphics systems:

* one constant gives an intuitive base scale
* more exact rendering uses width and height separately

So the system still has mathematical meaning even if one constant is not the exact final equation radius.

---

## 8.5 `PUPIL_RADIUS = 0.08`

### English meaning

This is the size of the dark inner circle.

### Math meaning

Pupil diameter:

```python
2r = 0.16
```

Ratio to eye width:

```python
0.08 / 0.21 ≈ 0.381
```

if compared to horizontal semi-axis.

Ratio to conceptual eye radius `0.22`:

```python
0.08 / 0.22 ≈ 0.364
```

So pupil radius is about **36% of eye radius scale**.

### Why useful

This is a strong but not oversized pupil.

If pupil too small:

* eyes feel empty
* gaze becomes hard to read
* character loses warmth

If pupil too large:

* eyes become heavy
* white space disappears
* highlight becomes crowded

### Visual effect

A pupil around one-third of eye scale is a common sweet spot for readable cartoon eyes.

---

## 8.6 `PUPIL_MAX_OFFSET = 0.07`

This is the one you already started studying, and yes, this is central.

### English meaning

This tells how far the pupil center may move away from eye center.

If eye center is `C` and pupil center is `P`, then:

```python
P = C + d
```

where:

```python
‖d‖ <= safe_limit
```

Current file uses component-wise clamp, but conceptually it is still a bounded offset idea.

### Your earlier bounded-disk idea

You wrote:

```python
‖P - C‖ ≤ R - r
```

That is the correct geometric safety idea for a circular eye.

Let us compare with current numbers.

If we use conceptual eye radius:

```python
R = 0.22
r = 0.08
R - r = 0.14
```

Current offset is:

```python
0.07
```

So:

```python
0.07 < 0.14
```

That means the allowed pupil shift is only about half of the absolute circular maximum.

### Safety margin

Margin left:

```python
0.14 - 0.07 = 0.07
```

So the same amount as allowed movement still remains as spare safety.

That is a large buffer.

### Why this is visually good

Even if a pupil could physically go farther and still technically remain inside, that does not mean it should.

When a pupil gets too close to the eye boundary:

* the eye feels strained
* it looks startled or unnatural
* the face becomes unstable during repeated animation
* tiny rendering differences become more visible

So the designer intentionally uses:

> not maximum mathematically possible motion
> but smaller aesthetically safe motion

That is excellent design.

---

## 8.7 Very important subtle issue: current clamping is square-style, not perfect circular/elliptic clamp

In `eyes.py`:

```python
clamped_x = max(-PUPIL_MAX_OFFSET, min(PUPIL_MAX_OFFSET, offset_vec[0]))
clamped_y = max(-PUPIL_MAX_OFFSET, min(PUPIL_MAX_OFFSET, offset_vec[1]))
```

This means x and y are clamped independently.

So allowed offsets form something like:

```python
|dx| <= 0.07
|dy| <= 0.07
```

That is a square box in offset space, not a circle.

So the exact allowed region is:

```python
[-0.07, 0.07] × [-0.07, 0.07]
```

not:

```python
dx^2 + dy^2 <= 0.07^2
```

This matters.

### Why?

At diagonal offset `(0.07, 0.07)`, the distance from center is:

```python
sqrt(0.07^2 + 0.07^2)
= 0.07 * sqrt(2)
≈ 0.099
```

So diagonal moves are effectively farther than horizontal-only moves.

### Is that bad?

Not necessarily yet, because the safety margin is still large.

But mathematically:

* current implementation = square-clamped motion
* ideal eye-ball constraint = disk or ellipse-clamped motion

This is a wonderful thing to notice while studying.

---

## 8.8 `EYE_GAP = 0.42`

### English meaning

This is the horizontal spacing between the two eye centers.

Actually in anchors, left eye is placed at `-EYE_GAP/2`, right at `+EYE_GAP/2`.

So center-to-center distance is:

```python
0.42
```

### Math meaning

Left eye center x:

```python
-0.21
```

Right eye center x:

```python
+0.21
```

if body center is origin.

Distance:

```python
0.42
```

### Compare with eye width

Eye width is also `0.42`.

So this is interesting:

```python
EYE_GAP = EYE_WIDTH
```

That means center-to-center distance equals one eye width.

Now think carefully.

Each eye half-width is `0.21`.

So the inner edge of left eye is at `-0.21 + 0.21 = 0`
and the inner edge of right eye is at `+0.21 - 0.21 = 0`

That means if modeled purely by the ellipse widths and centered this way, the eyes almost meet at the middle.

This is a strong, tightly grouped eye design.

### Why useful

It creates a very unified face.

The eyes do not feel too far apart.

It also keeps the eye-midpoint exactly centered for nose placement.

### Visual effect

Close eye spacing usually gives:

* cuteness
* focus
* compact face identity

Too much spacing would make the face look empty or flat.

---

# 9. Derived eye values

Code:

```python
EYE_PAIR_WIDTH = (2 * EYE_WIDTH) + EYE_GAP
EYE_CENTER_TO_CENTER = EYE_WIDTH + EYE_GAP

LEFT_EYE_OFFSET_X = -(EYE_CENTER_TO_CENTER / 2)
RIGHT_EYE_OFFSET_X = EYE_CENTER_TO_CENTER / 2
```

Now this part is a little interesting.

In `anchors.py`, actual eye center is based on `EYE_GAP / 2`, not on `EYE_CENTER_TO_CENTER / 2`.

So this tells us the file is mixing two ideas:

* one idea for total eye-pair footprint
* another idea for actual anchor placement

This is not wrong, but it is something to understand carefully.

## 9.1 `EYE_PAIR_WIDTH`

With current values:

```python
EYE_PAIR_WIDTH = 2(0.42) + 0.42 = 1.26
```

This means the full left-eye + middle gap + right-eye span is `1.26`.

That is useful for layout reasoning.

## 9.2 `EYE_CENTER_TO_CENTER`

```python
EYE_CENTER_TO_CENTER = 0.42 + 0.42 = 0.84
```

This looks more like a “one eye width plus one gap” model.

But anchors currently place eyes at ±0.21, meaning actual center-to-center in anchors is `0.42`.

So here I would say:

> This constant appears more like a planning/layout helper than the actual active anchor distance used by current eye placement.

That is a healthy reading.

---

# 10. Category 4 — Nose sizing

Code:

```python
NOSE_WIDTH = 0.14
NOSE_HEIGHT = 0.20
NOSE_STROKE_WIDTH = 2
```

And nose shape is a rounded rectangle.

---

## 10.1 Plain English

The nose is intentionally small and simple.

It is not the dominant facial feature.

It should connect the eye region and mouth region without stealing attention.

---

## 10.2 Math ratios

Compare with eye dimensions:

```python
NOSE_WIDTH / EYE_WIDTH  = 0.14 / 0.42 = 1/3 ≈ 0.333
NOSE_HEIGHT / EYE_HEIGHT = 0.20 / 0.52 ≈ 0.385
```

So nose is roughly one-third of eye width and about 38% of eye height.

That is a nice subordinate proportion.

---

## 10.3 Why this works

A nose is usually a separator, not a headline feature, in this mascot style.

Too large:

* face becomes heavy in the center
* mascot looks clumsy
* mouth feels crowded

Too small:

* center structure disappears
* face may feel unfinished

This size keeps the hierarchy:

* eyes first
* mouth second
* nose third

That is usually good.

---

## 10.4 Nose placement math

In anchors:

```python
nose_center = eye_midpoint - (NOSE_HEIGHT * 1.4) in y
```

Since:

```python
NOSE_HEIGHT = 0.20
```

vertical drop is:

```python
0.20 × 1.4 = 0.28
```

So the nose sits `0.28` below the eye midpoint.

That is proportional placement.

Very nice.

It means if nose height changes, placement also adapts.

---

# 11. Category 5 — Mouth sizing

Code:

```python
MOUTH_WIDTH = 0.48
MOUTH_HEIGHT = 0.18
MOUTH_STROKE_WIDTH = 4
SMILE_ARC_ANGLE = 1.8
NEUTRAL_MOUTH_WIDTH = 0.30
```

---

## 11.1 `MOUTH_WIDTH = 0.48`

### English meaning

This is how wide the smile arc stretches.

### Math meaning

Compare with nose width:

```python
0.48 / 0.14 ≈ 3.43
```

So mouth is over three times wider than nose.

Compare with one eye width:

```python
0.48 / 0.42 ≈ 1.14
```

So mouth is slightly wider than a single eye.

That is good because the mouth should read clearly, but not become too dominant.

---

## 11.2 `MOUTH_HEIGHT = 0.18`

### English meaning

This controls how tall the mouth arc is.

### Compare with width

```python
0.18 / 0.48 = 0.375
```

So mouth is much wider than tall.

That is exactly what a calm smile should be.

A smile is usually a shallow curve, not a tall oval.

---

## 11.3 `SMILE_ARC_ANGLE = 1.8`

### English meaning

This controls smile curvature.

Larger angle means stronger arc segment.

### Math meaning

This is in radians.

Since:

```python
π ≈ 3.1416
```

then:

```python
1.8 rad ≈ 103.1°
```

So the mouth uses an arc of about 103 degrees.

That gives a readable gentle smile.

Not flat, not exaggerated.

---

## 11.4 Mouth placement

Anchor logic:

```python
mouth_center = nose_center - (MOUTH_HEIGHT * 2.1) in y
```

Since:

```python
MOUTH_HEIGHT = 0.18
```

drop is:

```python
0.18 × 2.1 = 0.378
```

So mouth is placed about `0.378` below nose center.

Again, beautiful design idea:

placement depends on actual part size.

That is exactly how proportional rigs should work.

---

# 12. Category 6 — Hat sizing

Code:

```python
HAT_WIDTH = 1.25
HAT_HEIGHT = 0.72
HAT_BRIM_WIDTH = 1.05
HAT_BRIM_HEIGHT = 0.08
HAT_OFFSET_ABOVE_HEAD = 0.12
```

---

## 12.1 Why these matter mathematically

Hat is not just decoration.

It changes silhouette.

Silhouette is one of the strongest identity signals for characters.

So these hat numbers are silhouette geometry.

---

## 12.2 Width relative to body

```python
1.25 / 3.6 ≈ 0.347
```

So hat width is about 35% of body width.

That means it is clearly visible, but it does not cover the whole body.

That is good.

---

## 12.3 Offset above head

```python
HAT_OFFSET_ABOVE_HEAD = 0.12
```

This adds a little breathing room above the body top.

Without offset, the hat would feel glued directly to the body.

With a small offset:

* top silhouette becomes cleaner
* hat feels like a worn object
* crowding is reduced

Tiny numbers matter a lot in character design.

---

# 13. Category 7 — Arm sizing

Code:

```python
ARM_LENGTH = 1.15
ARM_STROKE_WIDTH = 10
ARM_SHOULDER_OFFSET_X = 1.05
ARM_SHOULDER_OFFSET_Y = 0.10
HAND_RADIUS = 0.11
```

You asked to connect to future constraint thinking too, so let’s do it.

---

## 13.1 Shoulder anchor

Arm anchor is placed at:

```python
(center_x ± 1.05, center_y + 0.10)
```

That means arms begin slightly above body center and significantly to left/right.

This is good because the shoulders should be lateral attachments.

---

## 13.2 Arm length

Compare with body height:

```python
1.15 / 4.2 ≈ 0.274
```

So each arm is about 27% of body height.

That is a moderate length.

Not too stubby, not too human-realistic long.

---

## 13.3 Constraint idea

Later when arms rotate, the shoulder becomes a pivot.

Then the arm endpoint lies on a circle:

```python
(x - x_s)^2 + (y - y_s)^2 = L^2
```

where `L = ARM_LENGTH`.

So already this constant is setting up a future rotation geometry system.

This is exactly the kind of connection you wanted.

---

# 14. Category 8 — Leg sizing

Code:

```python
LEG_LENGTH = 1.15
LEG_STROKE_WIDTH = 10
LEG_HIP_OFFSET_X = 0.62
LEG_HIP_OFFSET_Y = 1.88
FOOT_WIDTH = 0.30
FOOT_HEIGHT = 0.10
```

---

## 14.1 Hip placement

Leg anchor is:

```python
(center_x ± 0.62, center_y - 1.88)
```

Since body half-height is `2.1`, bottom is at `-2.1`.

So leg anchor y at `-1.88` is near the lower region of the body.

That makes sense physically.

The legs should emerge close to the bottom.

---

## 14.2 Leg length

Same as arm length:

```python
1.15
```

This symmetry is intentional-looking.

It makes the character feel unified and simple.

---

## 14.3 Future constraint idea

A leg rotating at hip also forms a circle of reachable endpoints:

```python
(x - x_h)^2 + (y - y_h)^2 = LEG_LENGTH^2
```

If later you restrict angle, then it becomes a circular arc sector.

So yes — even leg length is already a future motion-space parameter.

---

# 15. Now let us connect everything back to the eye math deeply

You wanted deeper reasoning behind chosen eye values and ratios.

So let us summarize eye proportions properly.

Given:

```python
EYE_WIDTH = 0.42
EYE_HEIGHT = 0.52
PUPIL_RADIUS = 0.08
PUPIL_MAX_OFFSET = 0.07
EYE_GAP = 0.42
```

---

## 15.1 Eye shape ratio

```python
EYE_HEIGHT / EYE_WIDTH = 1.238
```

So the eye is taller than wide.

Interpretation:

* more open
* more alert
* more lively

---

## 15.2 Pupil-to-eye ratio

Using eye width half-axis `0.21`:

```python
PUPIL_RADIUS / (EYE_WIDTH/2) = 0.08 / 0.21 ≈ 0.381
```

Using conceptual eye radius `0.22`:

```python
0.08 / 0.22 ≈ 0.364
```

Interpretation:

* pupil big enough to read emotion
* small enough to preserve eye white
* good for highlights

---

## 15.3 Pupil motion vs safe circular limit

Using conceptual circle:

```python
R = 0.22
r = 0.08
max theoretical offset = R - r = 0.14
actual configured offset = 0.07
```

Ratio:

```python
0.07 / 0.14 = 0.5
```

So actual motion uses only 50% of the conceptual maximum.

Interpretation:

* high safety margin
* no edge crowding
* better visual calmness
* robust against animation noise

---

## 15.4 Eye spacing

```python
EYE_GAP = 0.42 = EYE_WIDTH
```

Interpretation:

* eyes are compactly grouped
* face remains centered and cohesive
* midpoint is stable for nose and mouth placement

---

# 16. One very important conceptual upgrade for you

When studying these constants, think in 3 layers:

## Layer 1 — raw number

Example:

```python
PUPIL_MAX_OFFSET = 0.07
```

## Layer 2 — mathematical meaning

Example:

```python
|dx| <= 0.07
|dy| <= 0.07
```

or conceptually:

```python
‖P - C‖ bounded
```

## Layer 3 — visual meaning

Example:

* pupil can look around a little
* not too much
* keeps face stable
* avoids unnatural edge touching

This 3-layer reading method will help you read the whole project faster.

---

# 17. What `sizes.py` really is, in one line

`sizes.py` is a file of **design constraints encoded as numbers**.

Not decoration.

Not arbitrary defaults.

It is:

* proportion system
* placement system
* safety system
* future rigging system

---

# 18. The strongest beginner summary

If I explain like to a kid, but clearly:

* the body gives the big box
* inside the body there is a face zone
* inside the face zone the eyes sit
* below the eyes the nose sits
* below the nose the mouth sits
* the pupil is allowed to move, but only a little
* all of this is controlled by ratios and offsets
* so the creature is really a small geometry machine

That is the correct understanding.

---

# 19. Best mental formulas from this file

Keep these in memory:

## Body frame

```python
half_width = W / 2
half_height = H / 2
```

## Face zone

```python
face_top = H(0.5 - top_ratio)
face_height = H(height_ratio)
face_bottom = face_top - face_height
face_center = (face_top + face_bottom)/2
```

## Eye ellipse

```python
((x - x0)^2 / a^2) + ((y - y0)^2 / b^2) <= 1
a = EYE_WIDTH / 2
b = EYE_HEIGHT / 2
```

## Pupil placement

```python
P = C + d
```

## Safe pupil motion idea

```python
‖P - C‖ <= R - r
```

## Proportional placement

```python
nose_y = eye_mid_y - k1 * nose_height
mouth_y = nose_y - k2 * mouth_height
```

This is excellent rig-thinking.

---

# 20. Where the file is especially strong

The strongest things in this system are:

* body-to-face proportions use ratios
* derived constants are precomputed
* nose and mouth placement depend on part sizes
* pupil movement has safety clamping
* everything is anchored from body center

That is solid design.

---

# 21. Where the system is slightly inconsistent, but educational

These are not “bad”, just useful study points:

## 21.1 `EYE_RADIUS` vs actual ellipse

The eye is not rendered directly from `EYE_RADIUS`, but from width and height.

So radius is more conceptual than literal.

## 21.2 square clamping vs circular/elliptic clamping

The pupil offset is clamped independently in x and y.

So motion region is box-like, not truly disk-like.

## 21.3 `EYE_CENTER_TO_CENTER` in `sizes.py` vs actual anchors

The derived eye-center formula and the actual anchor placement are not fully using the same spacing logic.

These are good things to notice because they help you read code like an engineer, not just a memorizer.

---

# 22. What we should do next

The best next step is this:

I should now take `sizes.py` again and rewrite it for you as a **component-by-component study sheet**, in this exact order:

1. body frame
2. face zone
3. eyes
4. nose
5. mouth
6. hat
7. arms
8. legs
9. final derived map of the whole creature
