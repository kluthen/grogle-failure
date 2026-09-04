# Autonomous AI Comic Generation

## Goal
The goal of this project is to build an autonomous, agent-driven pipeline that converts long-form prose (chapters or draft logs) into visually consistent, fully assembled comic book pages. 

By leveraging local LLMs, the ComfyUI API, and ImageMagick, this system aims to solve the two biggest hurdles in AI comic generation: **Context Bloat** (LLMs failing to maintain complex schema logic over long prompts) and **Visual Continuity** (characters changing appearance between panels).

## Core Principles
1. **Context Isolation**: The pipeline is broken into discrete phases (Writer, Storyboarder, Illustrator). No single agent is ever burdened with reading the entire chapter *and* writing the rendering code at the same time.
2. **Strict Continuity**: The system relies on a local "Continuity Vault" containing locked character designs and location aesthetics. These are fed directly into ComfyUI's IP-Adapter and ControlNet nodes to violently enforce visual consistency across all panels.
3. **MCP Orchestration**: The high-level reasoning (the AI Orchestrator) is decoupled from the hardware execution. The agent communicates with the local GPU (Ollama/ComfyUI) via a standardized Python MCP server (`comic-mcp`).

## Documentation Directory
The architectural specifications and agent protocols for building this pipeline are detailed in the following documents:

### Architecture & Pipeline
- [architecture_plan.md](./architecture_plan.md)
  *The high-level blueprint of the 5-phase pipeline, explaining how the components and tools interact.*

- [master_skill_spec.md](./master_skill_spec.md)
  *The strict operational protocol for the orchestrator, detailing execution flow, the "Echo Rule" for IP-Adapter prompts, the temporary NPC protocol, and error handling/retry logic.*

- [pacing_spec.md](./pacing_spec.md)
  *Heuristics for Phase 2A: beat weighting, page budget calculation, layout selection algorithm, and beat-to-panel expansion rules.*

### Data & Schemas
- [data_schema_spec.md](./data_schema_spec.md)
  *The strict JSON data structures for the Continuity Vault, pipeline handoffs (`beats.json`, `panels.json`), and the extended dialogue schema (speech, narration, IM, SFX).*

- [vault_bridge_spec.md](./vault_bridge_spec.md)
  *How existing `world/` character and location markdown files map to the Vault's JSON format, including alias resolution and chapter frontmatter integration.*

### MCP Server & ComfyUI
- [mcp_server_spec.md](./mcp_server_spec.md)
  *The technical blueprint for the `comic-mcp` Python server: tool signatures, ComfyUI WebSocket connection model, Ollama integration, and error codes.*

- [comfyui_workflows_spec.md](./comfyui_workflows_spec.md)
  *Specification for the pre-built ComfyUI workflow templates (base panel, exploration, face/body extraction, depth mapping) that the MCP server patches at runtime.*

- [remote_server_requirements.md](./remote_server_requirements.md)
  *The technical hardware and software requirements (Ollama, ComfyUI, custom nodes) needed on the local GPU compute node.*

### Creative & Visual
- [exploration_phase_spec.md](./exploration_phase_spec.md)
  *The "Step 0" interactive workflow for collaboratively designing characters and sets, and autonomously locking those assets into the Continuity Vault.*

- [prompt_guide.md](./prompt_guide.md)
  *Prompt engineering conventions: standard prompt architecture, negative prompt libraries, IP-Adapter weight guidelines, mood-to-prompt mapping, and special cases for inner monologue and IM panels.*

- [camera_vocabulary_spec.md](./camera_vocabulary_spec.md)
  *Standardized enum of shot types, camera angles, panel transitions, and composition modifiers with their SDXL keyword mappings.*

### Output & Assembly
- [layout_definitions_spec.md](./layout_definitions_spec.md)
  *The strict enum values for `layout_type` and their ImageMagick assembly commands.*

- [webtoon_overlay_spec.md](./webtoon_overlay_spec.md)
  *How the pipeline handles speech bubbles and dialogue using a non-destructive HTML-based Webtoon approach with YOLO-driven spatial awareness.*

- [output_spec.md](./output_spec.md)
  *Deliverable formats (Webtoon HTML and print-ready pages), resolution strategy, directory structure, versioning, and SFX/narration handling.*

