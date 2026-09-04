# Prompt Engineering Guide

## Overview
This guide defines the conventions, patterns, and vocabulary for crafting Stable Diffusion XL prompts throughout the comic pipeline. Consistency in prompt structure is critical — it ensures that the LoRA and IP-Adapter behave predictably, and that the visual style remains uniform across hundreds of panels.

---

## Prompt Architecture

Every SDXL prompt follows this structure:

```
[Style Prefix], [Environment Description], [Character Description(s)], [Action], [Camera/Composition], [Quality Suffix]
```

### 1. Style Prefix (Constant)
The style prefix triggers the comic-style LoRA and sets the visual tone. It is the same for every panel in the project and is configured at the project level, not per-panel.

**Default:**
```
comic book style, graphic novel, bold ink lines, cel-shaded coloring
```

**Alternatives (depending on LoRA):**
- Western gritty: `western comic book, heavy crosshatching, dark gritty tones`
- Manga-leaning: `manga style, screentone shading, dynamic lineart`
- Bande dessinée: `european comic, franco-belgian style, clean precise linework, watercolor coloring`

### 2. Environment Description (From Vault — Echo Rule)
Pulled verbatim from the location's `environmental_description` field in the Vault JSON. Wrapped in emphasis brackets to signal importance to the model.

```
(A dim, smoky medieval tavern made of rotting wood, illuminated by green glowing candles:1.1)
```

**Weight**: `1.0–1.2`. Keep it moderate — the environment should frame the character, not overwhelm the composition.

### 3. Character Description(s) (From Vault — Echo Rule)
Pulled from the character's `physical_description` field. The Echo Rule mandates that this text is **always** injected, even when IP-Adapter is also active.

```
(A mixed-race young man in his mid-20s with short curly black hair, grey left arm, silver scars, wearing plain grey clothing:1.2)
```

**Weight**: `1.2–1.4` for the primary character, `1.0–1.1` for secondary characters in the same panel.

**Multiple characters**: List them sequentially, separated by commas. The primary character (usually the POV character) gets higher weight.

### 4. Action (From Beat)
The specific visual action for this panel, written in present participle or descriptive form:

```
slamming a gold coin onto a wooden table, aggressive expression
```

**Rules:**
- Use **visual** verbs. Avoid internal/emotional states that can't be drawn (e.g., ~~"feeling anxious"~~ → `"clenching fists, sweat on brow"`).
- Keep to one primary action per panel. Two simultaneous actions confuse the model.
- Include facial expression cues when relevant (`smirking`, `wide-eyed in shock`, `grinning`).

### 5. Camera/Composition (From Layout Plan)
Describes the virtual camera position. Uses the vocabulary from `camera_vocabulary_spec.md`:

```
medium shot, low angle, dramatic lighting
```

### 6. Quality Suffix (Constant)
Appended to every prompt for output quality:

```
masterpiece, best quality, highly detailed, sharp focus
```

---

## Complete Prompt Example

```
comic book style, graphic novel, bold ink lines, cel-shaded coloring,
(A vast open-plan office filled with identical work pods, cold fluorescent lighting, sterile grey walls, AR advertisements floating in the air:1.1),
(A mixed-race young man in his mid-20s with short curly black hair, grey left arm, silver scars, wearing plain grey clothing:1.2) climbing out of a gel-filled work pod, dripping translucent liquid, squinting under bright lights,
medium shot, slight low angle,
masterpiece, best quality, highly detailed, sharp focus
```

---

## Negative Prompt Library

### Standard Panel (Default)
Used for every comic panel unless overridden:
```
photorealistic, 3d render, photograph, deformed, bad anatomy, bad hands, extra fingers, missing fingers, extra limbs, fused fingers, long neck, mutated, disfigured, blurry, low quality, watermark, text, speech bubbles, signature, logo, censored, nsfw
```

### Character Exploration (Design Phase)
More permissive to allow creative variation:
```
photorealistic, 3d render, deformed, bad anatomy, bad hands, extra fingers, blurry, low quality, watermark, text
```

### Face Extract (FaceID Portrait)
Strict — needs a clean, usable reference:
```
full body, background scenery, text, blurry, deformed face, asymmetric eyes, bad proportions, multiple people, cropped, lowres
```

### Body Extract (Body Anchor)
```
close-up, portrait, background scenery, sitting, cropped, multiple people, blurry, deformed, bad anatomy, bad proportions
```

---

## Emphasis Weight Guidelines

SDXL uses `(text:weight)` syntax to increase/decrease attention to specific tokens.

| Weight Range | Use Case | Example |
|---|---|---|
| `0.8–0.9` | Subtle background details | `(distant city lights:0.8)` |
| `1.0` | Normal emphasis (default) | `wooden table` |
| `1.1–1.2` | Important scene elements | `(dim smoky tavern:1.1)` |
| `1.2–1.4` | Primary character features | `(curly black hair, grey arm:1.3)` |
| `1.5+` | **Avoid** — causes artifacts | — |

**Rule of thumb**: Never go above `1.4` for any single token group. If the model isn't respecting a feature at `1.3`, the problem is usually in the prompt structure, not the weight.

---

## IP-Adapter Weight Guidelines

IP-Adapter weights control how strongly the reference image influences the output. These are separate from prompt emphasis weights.

| Adapter Type | Recommended Weight | Purpose |
|---|---|---|
| IP-Adapter Plus (body) | `0.75–0.90` | Outfit, silhouette, body proportions |
| IP-Adapter FaceID | `0.80–0.95` | Facial structure lock |
| IP-Adapter (location vibe) | `0.25–0.40` | Color palette, atmosphere. **Keep low** to avoid overriding characters. |

**Conflict resolution**: When body and face adapters disagree with the text prompt, the adapters usually win. This is by design — the Echo Rule text acts as a "safety net" for when the adapter influence is insufficient, not as the primary driver.

---

## Mood-to-Prompt Mapping
The chapter frontmatter includes a `mood` array. These translate to lighting and atmospheric keywords:

| Mood (French) | Prompt Keywords |
|---|---|
| `banal` | `flat office lighting, mundane atmosphere, muted colors` |
| `désinvolte` | `warm casual lighting, relaxed posture, soft shadows` |
| `tension montante` | `dramatic shadows, desaturated colors, harsh angular lighting` |
| `panique` | `chaotic motion blur, red emergency lighting, dutch angle` |
| `horreur` | `deep shadows, cold blue-green tint, fog, unsettling atmosphere` |
| `combat` | `dynamic lighting, motion lines, impact effects, high contrast` |
| `mélancolie` | `soft diffused light, muted blue tones, rain, isolated framing` |

---

## Special Case: Inner Monologue Panels
This book is narrated entirely in first person with constant inner monologue. In traditional comics, this is rendered as **narration boxes** (rectangular captions), not speech bubbles. Panels that are pure internal thought may not need a complex action scene — sometimes a close-up on the character's face or a POV shot (what the character sees) is sufficient.

**Prompt pattern for thought panels:**
```
..., extreme close-up of face, introspective expression, looking slightly off-camera, shallow depth of field, ...
```

## Special Case: IM (Instant Message) Conversations
The book heavily features virtual IM exchanges rendered as in-world AR elements. These should be treated as **overlay elements in the Webtoon HTML**, not burned into the Stable Diffusion image. The SDXL prompt should show the character *interacting with* the IM (looking at invisible floating UI, typing gesture) but the actual message text is handled by Phase 5.

**Prompt pattern for IM panels:**
```
..., looking at floating holographic interface, fingers swiping at invisible AR display, soft blue glow on face from holographic light, ...
```
