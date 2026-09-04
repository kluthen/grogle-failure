# ComfyUI Workflow Templates

## Overview
The `comic-mcp` server does not generate ComfyUI workflows from scratch. It maintains a library of **pre-built workflow `.json` templates** stored in a local `workflows/` directory. At runtime, the server loads the appropriate template, patches placeholder values with the orchestrator's parameters, and submits the patched JSON to the ComfyUI API.

This approach eliminates the risk of LLM-generated workflow errors and ensures every rendering call uses a validated, tested node graph.

## Template Patching Convention
All templates use double-brace placeholders for values that the MCP server patches at runtime:
- `{{SDXL_PROMPT}}` — Positive prompt string
- `{{NEGATIVE_PROMPT}}` — Negative prompt string
- `{{SEED}}` — Random seed (integer)
- `{{STEPS}}` — Sampling steps (integer, default 30)
- `{{CFG_SCALE}}` — CFG guidance scale (float, default 7.0)
- `{{IP_ADAPTER_IMAGE_1}}` — Absolute path to IP-Adapter reference image (slot 1)
- `{{IP_ADAPTER_WEIGHT_1}}` — IP-Adapter influence weight (float, slot 1)
- `{{IP_ADAPTER_IMAGE_2}}` — Second IP-Adapter slot (optional)
- `{{IP_ADAPTER_WEIGHT_2}}` — Second IP-Adapter weight (optional)
- `{{CONTROLNET_IMAGE}}` — Absolute path to ControlNet input image
- `{{CONTROLNET_WEIGHT}}` — ControlNet influence weight (float)
- `{{OUTPUT_PREFIX}}` — Output filename prefix
- `{{WIDTH}}` / `{{HEIGHT}}` — Output resolution (default 1024×1024)
- `{{MOODBOARD_STYLE_IMAGE}}` — Absolute path to art style moodboard reference (exploration only)
- `{{MOODBOARD_STYLE_WEIGHT}}` — Style reference IP-Adapter weight (float, 0.30–0.45)
- `{{MOODBOARD_REF_IMAGE}}` — Absolute path to character/environment look reference (exploration only)
- `{{MOODBOARD_REF_WEIGHT}}` — Look reference IP-Adapter weight (float, 0.30–0.60)

---

## Required Templates

### 1. `base_panel.json` — Standard Comic Panel Rendering
The core template used during **Phase 3 (Illustrator)** for every panel in the comic.

**Node Graph:**
```
SDXL Checkpoint Loader
    → CLIP Text Encode (Positive: {{SDXL_PROMPT}})
    → CLIP Text Encode (Negative: {{NEGATIVE_PROMPT}})
    → KSampler (seed, steps, cfg)
    → VAE Decode
    → [Branch A] IP-Adapter Plus ({{IP_ADAPTER_IMAGE_1}}, weight)
    → [Branch B] IP-Adapter FaceID ({{IP_ADAPTER_IMAGE_2}}, weight) [optional]
    → [Branch C] ControlNet Union ({{CONTROLNET_IMAGE}}, weight) [optional]
    → LoRA Loader (comic style LoRA, weight 0.6–0.8)
    → YOLO Face Detector [conditional: only if extract_faces=true]
    → Save Image ({{OUTPUT_PREFIX}})
```

**Key Design Decisions:**
- IP-Adapter Plus is wired for **body/outfit continuity** (slot 1). IP-Adapter FaceID is wired for **facial structure lock** (slot 2). Both are optional — the MCP server only patches slots that have data.
- The LoRA loader uses a fixed comic-style LoRA at a moderate weight. The specific LoRA file is configured at the project level, not per-panel.
- The YOLO face detector node is connected via a bypass switch. The MCP server toggles it on/off based on the `extract_faces` parameter.
- Output resolution defaults to **1024×1024** (square panels). This can be overridden for splash pages.

---

### 2. `exploration.json` — Character/Location Design Exploration
Used during the **Exploration Phase** for generating design variations. Supports optional moodboard seeding via bypassable IP-Adapter slots.

**Node Graph:**
```
SDXL Checkpoint Loader
    → CLIP Text Encode (Positive: {{SDXL_PROMPT}})
    → CLIP Text Encode (Negative: {{NEGATIVE_PROMPT}})
    → KSampler (seed, steps, cfg)
    → VAE Decode
    → LoRA Loader (comic style LoRA)
    → [Branch A] IP-Adapter Plus ({{MOODBOARD_STYLE_IMAGE}}, {{MOODBOARD_STYLE_WEIGHT}}) [bypassable]
    → [Branch B] IP-Adapter Plus/FaceID ({{MOODBOARD_REF_IMAGE}}, {{MOODBOARD_REF_WEIGHT}}) [bypassable]
    → Save Image ({{OUTPUT_PREFIX}})
```

**Key Design Decisions:**
- **Branch A (Style)** captures art style and color palette from a moodboard reference. Weight range: `0.30–0.45`. Bypassed when no moodboard is provided.
- **Branch B (Reference)** captures a specific look — a character's face/body or an environment's architecture. Uses IP-Adapter Plus for environments, FaceID for character face references. Weight range: `0.30–0.60`. Bypassed when no reference image is provided.
- Both branches use **bypass switches** (not removal). The nodes are always present in the workflow; the MCP server toggles them on/off. This avoids needing separate templates for "with moodboard" vs. "without moodboard".
- Higher step count recommended (40+) for quality during the design iteration loop.
- Supports `batch_size > 1` for generating multiple variations in a single pass.
- When the Style Anchor is locked (see `exploration_phase_spec.md` Phase 0), Branch A automatically loads `/vault/style/project_style.jpg` at the weight specified in `style.json`.

---

### 3. `face_extract.json` — FaceID Portrait Generation
Used during the **Exploration Phase → Asset Lock (Path A, Step 1)** to generate a standardized FaceID portrait.

**Node Graph:**
```
SDXL Checkpoint Loader
    → CLIP Text Encode (Positive: "portrait photo, {{SDXL_PROMPT}}, neutral background, flat studio lighting, tight facial crop, looking at viewer")
    → CLIP Text Encode (Negative: "full body, background scenery, text, blurry")
    → KSampler
    → VAE Decode
    → LoRA Loader (comic style LoRA)
    → Save Image → {{OUTPUT_PREFIX}}_face.jpg
```

**Key Design Decisions:**
- The positive prompt is **force-prefixed** with portrait-specific terms that the orchestrator cannot override.
- Resolution is locked to **512×512** (sufficient for FaceID reference, saves VRAM).

---

### 4. `body_extract.json` — Body Anchor Generation
Used during the **Exploration Phase → Asset Lock (Path A, Step 2)** to generate a full-body standing pose.

**Node Graph:**
```
SDXL Checkpoint Loader
    → CLIP Text Encode (Positive: "full body standing pose, {{SDXL_PROMPT}}, neutral white background, T-pose, front view")
    → CLIP Text Encode (Negative: "close-up, background scenery, sitting, cropped")
    → KSampler
    → VAE Decode
    → LoRA Loader (comic style LoRA)
    → Save Image → {{OUTPUT_PREFIX}}_body.jpg
```

---

### 5. `depth_extract.json` — Location Geometry Extraction
Used during the **Exploration Phase → Asset Lock (Path B, Step 2)** to extract a ControlNet depth map from an approved location vibe image.

**Node Graph:**
```
Load Image ({{INPUT_IMAGE}})
    → Zoe Depth Preprocessor (from comfyui_controlnet_aux)
    → Save Image → {{OUTPUT_PREFIX}}_depth.png
```

**Note:** This template does **not** run Stable Diffusion. It is purely a computer vision pipeline that extracts geometric data from an existing image.

---

### 6. `npc_portrait.json` — Temporary NPC Base Portrait
Used during the **Temporary NPC Protocol** (pre-Phase 3) to generate a quick one-shot portrait for an unnamed NPC.

**Node Graph:** Identical to `face_extract.json`, but with:
- Output path pointing to `/vault/temporary/chapter_X/`.
- A second run through `body_extract.json` for the body anchor.

This can be implemented as two sequential calls to `face_extract.json` and `body_extract.json` rather than a separate template, at the orchestrator's discretion.

---

## Template Storage & Versioning
```
comic/
└── workflows/
    ├── base_panel.json
    ├── exploration.json        # includes bypassable moodboard IP-Adapter slots
    ├── face_extract.json
    ├── body_extract.json
    ├── depth_extract.json
    └── npc_portrait.json       # optional shorthand
```

The Vault gains two new directories for moodboard and style assets:
```
/vault/
├── characters/
├── locations/
├── temporary/
├── moodboard/                  # user-provided reference images
│   ├── style/
│   ├── characters/
│   ├── environments/
│   └── palette/
└── style/                      # locked project-wide style anchor
    ├── project_style.jpg
    └── style.json
```

Templates are versioned alongside the rest of the `comic/` spec directory. Changes to templates should be tested against the remote ComfyUI instance before being committed — a malformed workflow JSON will cause `COMFY_WORKFLOW_ERROR` at runtime.

## Future Templates
As the pipeline evolves, additional templates may be needed:
- **`upscale.json`** — For post-render upscaling (e.g., 1024→2048 or 4096 for print).
- **`inpaint.json`** — For targeted corrections on specific panel regions without full re-render.
- **`pose_extract.json`** — OpenPose extraction from reference images for forced character posing.
