# Exploratory Skill: Casting & Set Design

## Overview
This document defines the "Exploratory Skill", a dedicated, interactive workflow used to design and "lock in" visual assets for the comic. This skill must be executed *before* the Master Skill can process a chapter. The AI orchestrator drives a collaborative, iterative loop with the user until a design is approved, and then autonomously generates the strict technical assets required for the Continuity Vault.

## The Execution Flow

### Phase 0: Moodboard Seeding (Optional)
Before generating anything, the user can provide visual references to establish the artistic direction. This seeds the entire exploration session with a consistent visual tone.

#### What the User Provides
A folder of reference images — any combination of:
- **Art style references**: Pages from existing comics, concept art, illustrations (e.g., Moebius, Enki Bilal, manga panels).
- **Color/atmosphere references**: Movie stills, photographs, paintings that capture the desired mood.
- **Character look references**: Photos of real people, other character designs — for facial structure, body type, clothing style.
- **Environment references**: Architectural photos, game screenshots, urban photography.

The user drops these images into a local moodboard directory:
```
/vault/moodboard/
├── style/          # Art style references (comic pages, illustrations)
├── characters/     # Face/body look references (photos, character art)
├── environments/   # Location atmosphere references (photos, stills)
└── palette/        # Color palette / mood references (any image)
```

#### How the Orchestrator Uses Moodboard Images
The orchestrator selects the most relevant images from the moodboard based on what is being designed:

| Designing... | Moodboard Source | IP-Adapter Slot | Weight |
|---|---|---|---|
| A character | `moodboard/style/` + `moodboard/characters/` | IP-Adapter Plus (style) + IP-Adapter FaceID (look) | `0.30–0.45` (style) / `0.40–0.60` (look) |
| A location | `moodboard/style/` + `moodboard/environments/` | IP-Adapter Plus (style) + IP-Adapter Plus (environment) | `0.30–0.45` (style) / `0.30–0.50` (environment) |
| General style test | `moodboard/style/` + `moodboard/palette/` | IP-Adapter Plus | `0.35–0.50` |

**Key constraint**: Moodboard IP-Adapter weights are kept **deliberately low** (0.3–0.5). The goal is to capture the *vibe* — color palette, line quality, lighting mood — without copying the source image content. The text prompt remains the primary creative driver.

#### The Style Anchor (Project-Level Asset)
Once the user is satisfied with the overall art style, the orchestrator saves the most effective moodboard configuration as a **Style Anchor** — a project-wide reference that influences all subsequent generation:

- **`/vault/style/project_style.jpg`**: The single best style reference image (or a composite created by generating an image that captures the approved vibe).
- **`/vault/style/style.json`**: Metadata storing the approved style prefix, recommended IP-Adapter weight, and LoRA configuration.

```json
{
  "style_id": "project_default",
  "style_prefix": "comic book style, graphic novel, bold ink lines, cel-shaded coloring",
  "style_anchor_path": "/vault/style/project_style.jpg",
  "style_adapter_weight": 0.35,
  "lora": {
    "name": "Western_Graphic_Novel_XL",
    "weight": 0.7
  },
  "negative_base": "photorealistic, 3d render, photograph, deformed, bad anatomy"
}
```

This Style Anchor is then automatically injected into every subsequent generation — both in the Exploration Phase (for character/location design) and in Phase 3 (for comic panel rendering). It ensures that every image produced shares the same visual DNA.

---

### Phase 1: The Design Iteration Loop
The orchestrator acts as a concept artist, taking high-level direction from the user.
1. **Initial Request**: The user provides a rough concept (e.g., "Design a Goblin Boss, scarred, heavy armor").
2. **Generation**: The orchestrator formulates a detailed ComfyUI prompt and uses the `comfy_generate_image` MCP tool to render a batch of variations. If a moodboard was provided in Phase 0, the Style Anchor and any relevant character/environment references are fed into IP-Adapter alongside the prompt.
3. **Feedback**: The user reviews the images and provides critique (e.g., "Image 2 is close, but make the armor darker and the tusks longer").
4. **Moodboard Adjustment**: The user can also adjust the visual references mid-loop:
   - "Use this new reference image instead" → orchestrator swaps the IP-Adapter source.
   - "Increase the style influence" → orchestrator raises the IP-Adapter weight.
   - "Ignore the moodboard for this one, go pure prompt" → orchestrator bypasses IP-Adapter entirely.
5. **Refinement**: The orchestrator adjusts the prompt (and optionally the reference images) and rerenders. This loop continues until the user explicitly approves a final design.

---

### Phase 2: The Asset Lock (Commit)
Once the user approves a design, the orchestrator *automatically* transitions to Phase 2. It takes the approved prompt and autonomously generates the specific, standardized files required by the IP-Adapter and ControlNet nodes.

#### Path A: Character Asset Lock
If the entity is a character or creature, the orchestrator must generate and save the following three files:
1. **The FaceID Portrait (`{name}_face.jpg`)**:
   - *Constraint*: The orchestrator modifies the prompt to force a tight facial crop and flat lighting against a neutral white/gray background.
   - *Purpose*: Used by IP-Adapter FaceID to strictly lock the facial structure.
   - *Save Path*: `/vault/characters/{name}_face.jpg`
2. **The Body Anchor (`{name}_body.jpg`)**:
   - *Constraint*: The orchestrator modifies the prompt to force a full-body standing pose against a neutral background.
   - *Purpose*: Used by IP-Adapter Plus to lock clothing, armor, and silhouette.
   - *Save Path*: `/vault/characters/{name}_body.jpg`
3. **The Metadata (`{name}.json`)**:
   - *Constraint*: The orchestrator writes a JSON file storing the final, optimized physical text description.
   - *Save Path*: `/vault/characters/{name}.json`

#### Path B: Location Asset Lock
If the entity is an environment or set, the orchestrator must generate the following files:
1. **The Vibe Anchor (`{name}_vibe.jpg`)**:
   - *Constraint*: The approved concept art image from Phase 1 is saved directly.
   - *Purpose*: Used by standard IP-Adapter (at a low weight, ~0.3) to ensure consistent lighting, color palettes, and textures across panels without overriding characters.
   - *Save Path*: `/vault/locations/{name}_vibe.jpg`
2. **The Geometry Anchor (Optional) (`{name}_depth.png`)**:
   - *Constraint*: If the user specifies the room geometry must remain rigid (e.g., a specific tavern layout), the orchestrator triggers the `comfyui_controlnet_aux` preprocessors to extract a mathematical depth map from the Vibe Anchor.
   - *Purpose*: Fed into ControlNet Depth during comic generation to rigidly lock walls, tables, and pillars into the exact same position in every panel.
   - *Save Path*: `/vault/locations/{name}_depth.png`
3. **The Metadata (`{name}.json`)**:
   - *Constraint*: The orchestrator writes a JSON file storing the environmental text description.
   - *Save Path*: `/vault/locations/{name}.json`
