# MCP Server Specification (`comic-mcp`)

## Overview
`comic-mcp` is a local Python MCP server that exposes discrete, stateless tools to the AI Orchestrator. It acts as the sole bridge between the high-level reasoning layer (Gemini) and the local compute hardware (Ollama, ComfyUI, ImageMagick). The server itself performs **zero creative reasoning** — it translates structured JSON instructions into subprocess calls and API requests, then returns deterministic results.

## Design Principles
1. **Stateless Per-Call**: Each tool invocation is self-contained. The server does not maintain session state between calls. All context (file paths, vault references, layout instructions) is passed explicitly in the tool parameters.
2. **Explicit File Paths**: Every tool that produces or consumes files uses absolute paths. No implicit "current directory" assumptions.
3. **Blocking Execution**: Tools block until their underlying operation completes (image generated, file written). The orchestrator does not need to poll for results.
4. **Structured Errors**: On failure, tools return a structured error object (`{ "error": "<code>", "message": "<detail>" }`) rather than crashing the MCP session.

---

## Tool Definitions

### 1. `ollama_generate_panel`
Sends a structured prompt to the local Ollama instance to translate a narrative beat into a strict ComfyUI JSON payload.

**Parameters:**
| Param | Type | Required | Description |
|---|---|---|---|
| `beat_text` | `string` | ✅ | The isolated narrative action for this panel (e.g., "The Warrior slams a gold coin onto the table"). |
| `characters` | `array<CharacterVaultEntry>` | ✅ | Extracted vault entries for characters in this panel (includes `physical_description`, `core_tags`, `assets`). |
| `location` | `LocationVaultEntry` | ✅ | Extracted vault entry for the scene location. |
| `camera` | `string` | ✅ | Camera shot type from the camera vocabulary (e.g., `medium_shot`, `low_angle`). |
| `style_prefix` | `string` | ❌ | Style LoRA trigger words to prepend (defaults to project-level config). |
| `model` | `string` | ❌ | Ollama model override (defaults to `llama3`). |

**Returns:**
```json
{
  "panel_payload": {
    "sdxl_prompt": "...",
    "negative_prompt": "...",
    "ip_adapter_nodes": [...],
    "controlnet_nodes": [...],
    "seed": 42,
    "steps": 30,
    "cfg_scale": 7.0
  }
}
```

**Errors:**
- `OLLAMA_UNREACHABLE` — Cannot connect to Ollama at configured host.
- `OLLAMA_INVALID_JSON` — Model returned malformed JSON (retry with stricter system prompt).
- `OLLAMA_TIMEOUT` — Generation exceeded timeout threshold (default: 120s).

---

### 2. `comfy_generate_image`
Fires a complete ComfyUI workflow payload to the local ComfyUI API and waits for the rendered image.

**Parameters:**
| Param | Type | Required | Description |
|---|---|---|---|
| `workflow_template` | `string` | ✅ | Name of the base workflow template to use (e.g., `base_panel`, `exploration`, `face_extract`, `body_extract`). |
| `prompt_overrides` | `object` | ✅ | Key-value patches to apply to the workflow template (SDXL prompt, negative prompt, IP-Adapter image paths, ControlNet maps, seed, etc.). |
| `output_path` | `string` | ✅ | Absolute path where the generated image should be saved. |
| `extract_faces` | `boolean` | ❌ | If `true`, run the YOLO face detection node post-render and return bounding boxes. Defaults to `false`. |
| `batch_size` | `integer` | ❌ | Number of variations to generate (default: `1`). Used during Exploration Phase. |
| `moodboard_images` | `MoodboardConfig` | ❌ | Optional moodboard references for the exploration workflow. See below. |

**`MoodboardConfig` Object:**
| Field | Type | Required | Description |
|---|---|---|---|
| `style_image` | `string` | ❌ | Absolute path to art style reference image. Patches `{{MOODBOARD_STYLE_IMAGE}}`. |
| `style_weight` | `float` | ❌ | IP-Adapter weight for style reference (default: `0.35`, range: `0.20–0.50`). |
| `ref_image` | `string` | ❌ | Absolute path to character/environment look reference. Patches `{{MOODBOARD_REF_IMAGE}}`. |
| `ref_weight` | `float` | ❌ | IP-Adapter weight for look reference (default: `0.40`, range: `0.20–0.60`). |

When `moodboard_images` is provided, the MCP server enables the corresponding IP-Adapter bypass switches in the `exploration.json` template. When omitted (or when individual fields are `null`), those branches remain bypassed.

**Returns:**
```json
{
  "images": ["/output/chapter_05/raw_panels/p_01.png"],
  "face_bounding_boxes": [
    {
      "entity_guess": "warrior_01",
      "x_min": 400, "y_min": 300,
      "x_max": 550, "y_max": 450,
      "confidence": 0.92
    }
  ],
  "generation_time_ms": 14200,
  "seed_used": 42
}
```

**Errors:**
- `COMFY_UNREACHABLE` — Cannot connect to ComfyUI API at configured host:port.
- `COMFY_QUEUE_FULL` — ComfyUI queue is saturated; retry after delay.
- `COMFY_WORKFLOW_ERROR` — ComfyUI returned a node execution error (includes node ID and error message).
- `COMFY_OOM` — VRAM out-of-memory during generation.
- `COMFY_TIMEOUT` — Generation exceeded timeout threshold (default: 300s).

#### ComfyUI Connection Model
The server connects to ComfyUI via its **WebSocket API** (`ws://{host}:{port}/ws`):
1. **Prompt Submission**: POST the workflow JSON to `/prompt`.
2. **Progress Tracking**: Listen on the WebSocket for `progress`, `executing`, and `executed` messages.
3. **Image Retrieval**: On completion, fetch the output image from `/view` or read it directly from ComfyUI's output directory (preferred for local setups — avoids base64 overhead).
4. **Timeout**: If no `executed` message arrives within the timeout window, the server cancels the prompt via `/queue` DELETE and returns `COMFY_TIMEOUT`.

#### Workflow Template Patching
The server does **not** generate ComfyUI workflows from scratch. It maintains a set of pre-built workflow `.json` templates (see `comfyui_workflows_spec.md`) and patches them at runtime:
1. Load the template JSON.
2. Walk the node graph and replace placeholder values with `prompt_overrides` (e.g., `{{SDXL_PROMPT}}` → actual prompt string, `{{IP_ADAPTER_IMAGE}}` → absolute file path).
3. Inject a random seed if none is specified.
4. Submit the patched workflow.

---

### 3. `magick_assemble`
Stitches multiple panel images into comic strips and pages using ImageMagick subprocesses.

**Parameters:**
| Param | Type | Required | Description |
|---|---|---|---|
| `layout_type` | `string` | ✅ | Layout enum value from `layout_definitions_spec.md` (e.g., `3_panel_strip`, `2x2_grid`, `full_page_9_grid`). |
| `panel_paths` | `array<string>` | ✅ | Ordered array of absolute paths to raw panel images. Count must match `layout_type` expectations. |
| `output_path` | `string` | ✅ | Absolute path for the assembled output image. |
| `gutter_width` | `integer` | ❌ | Border/gutter width in pixels (default: `15`). |
| `gutter_color` | `string` | ❌ | Gutter color (default: `black`). |

**Returns:**
```json
{
  "assembled_image": "/output/chapter_05/pages/page_01.png",
  "dimensions": { "width": 3174, "height": 1054 }
}
```

**Errors:**
- `MAGICK_NOT_FOUND` — ImageMagick binary not found in system PATH.
- `MAGICK_INPUT_MISSING` — One or more input panel paths do not exist.
- `MAGICK_PANEL_COUNT_MISMATCH` — Number of panels does not match `layout_type` requirement.
- `MAGICK_SUBPROCESS_FAIL` — ImageMagick returned a non-zero exit code (includes stderr).

---

### 4. `generate_webtoon_html`
Generates the final Webtoon HTML viewer with CSS-positioned speech bubbles overlaid on assembled comic pages.

**Parameters:**
| Param | Type | Required | Description |
|---|---|---|---|
| `pages` | `array<PageData>` | ✅ | Array of page objects, each containing `image_path`, `panels` (with `dialogue` and `face_bounding_boxes`), and `layout_type`. |
| `output_dir` | `string` | ✅ | Directory where `index.html` and assets will be written. |
| `language` | `string` | ❌ | Dialogue language code (default: `fr`). Affects font selection and text direction. |
| `theme` | `string` | ❌ | Visual theme for bubbles: `classic_white`, `manga_black`, `modern_flat` (default: `classic_white`). |

**Returns:**
```json
{
  "html_path": "/output/chapter_05/index.html",
  "page_count": 4,
  "bubble_count": 23
}
```

**Errors:**
- `WEBTOON_NO_PAGES` — Empty pages array provided.
- `WEBTOON_IMAGE_MISSING` — Referenced page image does not exist.

---

### 5. `vault_query`
Queries the Continuity Vault to retrieve character or location metadata by entity ID.

**Parameters:**
| Param | Type | Required | Description |
|---|---|---|---|
| `entity_id` | `string` | ✅ | The vault entity ID (e.g., `warrior_01`, `tavern_interior`). |
| `include_temporary` | `boolean` | ❌ | If `true`, also search `/vault/temporary/` (default: `false`). |

**Returns:** The full JSON vault entry for the entity.

**Errors:**
- `VAULT_NOT_FOUND` — No entity with this ID exists in the Vault.

---

### 6. `vault_commit`
Writes or updates a vault entry (character or location JSON + associated image assets).

**Parameters:**
| Param | Type | Required | Description |
|---|---|---|---|
| `entity` | `VaultEntry` | ✅ | Full vault entry object (character or location schema). |
| `assets` | `object<string, string>` | ❌ | Map of asset key → source image path to copy into the vault directory. |
| `temporary` | `boolean` | ❌ | If `true`, save to `/vault/temporary/` instead of the permanent vault. |

**Returns:**
```json
{
  "entity_id": "warrior_01",
  "vault_path": "/vault/characters/warrior_01.json",
  "assets_written": ["warrior_01_face.jpg", "warrior_01_body.jpg"]
}
```

---

## Server Configuration
The server reads its configuration from a `comic-mcp.toml` file:

```toml
[comfyui]
host = "192.168.1.10"
port = 8188
timeout_seconds = 300

[ollama]
host = "192.168.1.10"
port = 11434
default_model = "llama3"
timeout_seconds = 120

[vault]
root = "/vault"
temporary_prefix = "temporary"

[workflows]
templates_dir = "./workflows"

[imagemagick]
binary = "magick"
default_gutter = 15
default_gutter_color = "black"
```

## Server Startup
```bash
# Install
pip install comic-mcp

# Run (stdio transport for IDE integration)
comic-mcp serve

# Run with explicit config
comic-mcp serve --config /path/to/comic-mcp.toml
```
