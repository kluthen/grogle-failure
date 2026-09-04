# AI Comic Generation Architecture

## Overview
A multi-agent, pipeline-driven architecture designed to convert long-form prose (chapters/logs) into comic pages. The system is designed to minimize LLM context bloat, ensure strict visual continuity, and orchestrate local compute (Ollama, ComfyUI, ImageMagick) via a dedicated MCP server.

## Core Components

### 1. The MCP Server (`comic-mcp`)
A local Python-based MCP server providing discrete tools to the orchestrating agent:
- `ollama_generate_panel`: Generates ComfyUI JSON payloads per panel using local LLMs.
- `comfy_generate_image`: Triggers image generation via the local ComfyUI API (RTX 3060).
- `magick_assemble`: Stitches images together using ImageMagick subprocesses.

### 2. The Continuity Vault
A local database storing visual anchors to ensure consistency across panels.
- **`/vault/characters/`**: Character sheets (JSON) defining physical traits and mapping to IP-Adapter reference images.
- **`/vault/locations/`**: Location sheets defining lighting, environmental aesthetics, and optional ControlNet depth maps.
- **Continuity State Tracker**: An active memory of current conditions (e.g., "Warrior's sword is broken", "Time is night").

---

## The Pipeline (The Master Skill)

### Phase 1: The Writer (Native Orchestrator)
- **Input**: Raw chapter prose (`.md`).
- **Action**: The main agent (Gemini) reads the chapter, understands the narrative flow, and extracts key visual moments.
- **Output**: `beats.json` (An array of narrative scenes and key visual bullet points).

### Phase 2: The Storyboarder (Multi-Tiered)
To handle the complexity of pacing and layout without context degradation, Phase 2 is split into two specialized tiers:

#### Phase 2A: The High-Level Director
- **Input**: `beats.json` and the Continuity Vault.
- **Action**: Determines comic pacing (e.g., assigning action to a full splash page, dialogue to a 3-panel strip). Scans the text to "cast" the scene, identifying which entities from the Vault are present.
- **Output**: `layout_plan.json` (Defines pages, panels, active characters, and locations).

#### Phase 2B: The Low-Level Implementers
- **Input**: Specific panel data from `layout_plan.json` + specific character/location sheets.
- **Action**: Spawns a micro-agent (or isolated Ollama call) for *each individual panel*. Context is surgically restricted to the specific action required for that one square.
- **Output**: `panels.json` (Array of strict ComfyUI payloads, including SDXL prompts, negative prompts, and IP-Adapter mappings).

### Phase 3: The Illustrator (Rendering)
- **Input**: `panels.json`.
- **Action**: Iterates over the JSON, firing requests to the `comfy_generate_image` MCP tool without requiring further LLM reasoning.
- **Output**: A directory of raw panel images (e.g., `panel_01.png`, `panel_02.png`).

### Phase 4: The Publisher (Assembly)
- **Input**: Raw panel images.
- **Action**: Invokes the `magick_assemble` MCP tool to stitch strips horizontally and pages vertically, applying gutters and borders.
- **Output**: Final comic pages ready for reading.
