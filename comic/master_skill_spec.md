# Master Skill: Chapter to Comic Generator

## Overview
This document defines the "Master Skill" (the core AI Orchestrator loop) responsible for converting a raw markdown chapter into a fully assembled, multi-page comic. The Master Skill acts as the central conductor, delegating tasks to specific LLM models (cloud or local) and local MCP tools while strictly enforcing context isolation and visual continuity.

## Execution Constraints
To prevent LLM hallucination and context degradation, the Master Skill must adhere to these strict operational constraints:
1. **Strict Handoffs**: The pipeline is linear. A phase cannot begin until the previous phase has written its deterministic output artifact (e.g., `beats.json`, `panels.json`) to the disk.
2. **Context Isolation**: When processing Phase 2B (Panel Prompts), the AI must *never* be fed the entire chapter text. It must only be fed the isolated action description for that specific panel and the required Vault metadata.
3. **Continuity First**: The Master Skill must cross-reference all identified characters and locations against the Continuity Vault before rendering begins.

---

## The Pipeline Execution Flow

### Phase 1: The Writer (Beat Extraction)
- **Actor**: High-Context Cloud LLM (Gemini).
- **Task**: Read the raw `chapter.md`. Break the narrative into discrete scenes. For each scene, extract the core visual actions (beats).
- **Constraint**: Must identify the active Location and the active Characters for each beat.
- **Output**: Writes `beats.json` to the workspace.

### Phase 2: The Storyboarder (Layout & Prompts)
This phase translates the narrative beats into machine-readable ComfyUI payloads.

#### Phase 2A: The High-Level Director
- **Actor**: High-Context Cloud LLM (Gemini).
- **Task**: Determine pacing. Decide if a beat requires a 9-panel page, a 3-panel strip, or a splash page. 
- **Output**: Updates the working JSON with panel grids and IDs.

#### Phase 2B: The Low-Level Implementer
- **Actor**: Local LLM via `ask_ollama` MCP (or Cloud LLM if preferred).
- **Task**: Iterate over every panel ID. Translate the narrative action into a strict Stable Diffusion prompt (`sdxl_prompt`) and define camera angles.
- **Output**: Writes the final `panels.json` payload array.

### Phase 3: The Illustrator (Rendering)
- **Actor**: The `comfy_generate_image` MCP Tool (Headless).
- **Task**: Iterate through `panels.json`. For each panel, fire the payload to the local ComfyUI API on `192.168.1.10:8188`. Wait for the image generation to complete.
- **Output**: Saves raw `.png` files to `/output/chapter_X/raw_panels/`. Updates the JSON with local file paths.

### Phase 4: The Publisher (Assembly)
- **Actor**: The `magick_assemble` MCP Tool (Headless).
- **Task**: Group the raw panels into strips and pages based on the layout instructions from Phase 2A. Apply black gutters and borders using ImageMagick subprocesses.
- **Output**: Saves the final `/output/chapter_X/pages/page_01.png`.

### Phase 5: The Webtoon Typesetter (Dialogue Overlay)
- **Actor**: The `generate_webtoon_html` MCP Tool (or native Orchestrator logic).
- **Task**: Read the `panels.json` to extract `dialogue` objects and `face_bounding_boxes` (supplied by ComfyUI YOLO nodes). Calculate empty spatial coordinates to prevent dialogue from covering character faces, and generate an `index.html` web application.
- **Output**: Saves `/output/chapter_X/index.html` which loads the assembled pages as backgrounds and uses CSS absolute positioning to dynamically overlay speech bubbles.

---

## Continuity & Context Protocols
During Phase 2, the Master Skill must strictly enforce the following protocols to ensure the low-level rendering engines have unambiguous data.

### 1. The "Echo Rule" Prompt Injection
The rendering engine cannot rely on IP-Adapter images alone. The Master Skill must enforce the "Echo Rule".
- **Mechanism**: The Storyboarder must pull the `description` field from `/vault/characters/warrior.json` and automatically prefix it to the panel's action prompt.
- Example: `"[Comic Style], (A rugged man with a facial scar, wearing asymmetrical leather armor:1.2) swinging a sword."`

### 2. The Temporary NPC Protocol
Chapters often introduce "Random NPCs" that appear across multiple panels but do not exist in the permanent Continuity Vault.
1. **Detection (Phase 1)**: If the Writer finds an unknown entity (e.g., `tavern_keeper`), it creates a temporary profile in memory.
2. **On-the-Fly Generation**: Before Phase 3 begins, the Master Skill pauses and fires a direct request to ComfyUI to generate a single "Base Portrait" for the `tavern_keeper`.
3. **Temporary Vault**: This portrait is saved to `/vault/temporary/chapter_X/tavern_keeper.jpg`.
4. **Enforced Continuity**: When generating the comic panels, the IP-Adapter uses that temporary image, keeping the NPC consistent throughout the chapter.

### 3. Explicit File Paths in Payloads
To ensure zero ambiguity, the final `panels.json` must map explicit absolute file paths for the IP-Adapter and ControlNet nodes so ComfyUI knows exactly what to load.

---

## Error Handling & Review Gates

### Retry Budget
Each phase has a defined retry budget before escalating to human review:

| Phase | Max Retries | Retry Strategy |
|---|---|---|
| Phase 1 (Writer) | 2 | Re-prompt with stricter extraction instructions. |
| Phase 2A (Director) | 2 | Re-prompt with layout constraint reminders. |
| Phase 2B (Implementer) | 3 per panel | Re-prompt with tighter JSON schema enforcement. On 3rd failure, flag panel for manual prompt writing. |
| Phase 3 (Illustrator) | 3 per panel | Re-render with different seed. On VRAM OOM, reduce resolution to 768×768 and retry once. |
| Phase 4 (Publisher) | 1 | Assembly errors are deterministic — if ImageMagick fails, it's a bug, not a retry situation. |
| Phase 5 (Typesetter) | 1 | Same as Phase 4. |

### Review Gates
The pipeline supports two modes: **fully autonomous** and **supervised**.

**Supervised Mode** (recommended for initial chapters):
1. **Gate after Phase 1**: The orchestrator presents `beats.json` summary to the user. User confirms the scene breakdown and character casting before proceeding.
2. **Gate after Phase 2A**: The orchestrator presents the layout plan (page count, layout types). User can adjust pacing (e.g., "make this beat a splash page instead").
3. **Gate after Phase 3**: A contact sheet (grid of all raw panels) is assembled and shown to the user. User can flag individual panels for re-render before assembly.
4. **No gate after Phase 4/5**: Assembly and typesetting are deterministic — if the inputs are good, the outputs are good.

**Autonomous Mode** (for batch processing once the pipeline is tuned):
- All gates are skipped. The pipeline runs end-to-end without pausing.
- A quality report is generated at the end listing any panels that required retries or hit edge cases.

### Specific Failure Scenarios

| Failure | Detection | Recovery |
|---|---|---|
| **Ollama returns malformed JSON** | JSON parse fails in `ollama_generate_panel` | Retry with a stricter system prompt that includes a JSON schema example. Max 3 retries. |
| **ComfyUI VRAM OOM** | `COMFY_OOM` error from MCP tool | Reduce resolution to 768×768, disable ControlNet (keep IP-Adapter), retry once. |
| **Bad composition** (character cut off, wrong angle) | Human review gate (supervised mode) or automated YOLO check (if no faces detected when expected) | Re-render with different seed (up to 3 seeds). If still failing, adjust the prompt (remove conflicting terms). |
| **YOLO detects zero faces** | `face_bounding_boxes` is empty | If dialogue exists for this panel, fall back to placing bubbles in the top-left quadrant (safe default). Log a warning. |
| **Character not in Vault** | `VAULT_NOT_FOUND` during Phase 2 casting | Trigger the Temporary NPC Protocol. If it's a known character that simply hasn't been through the Exploration Phase yet, halt and alert the user. |
| **ComfyUI queue timeout** | `COMFY_TIMEOUT` after 300s | Cancel the stuck prompt, clear the queue, retry once with a simpler prompt (remove ControlNet). |
