# Remote Server Requirements (192.168.1.10)

To support the AI Comic Generation Pipeline, the remote server acting as the compute node must be configured with the following software, models, and network access.

## 1. Local LLM Server (Ollama)
Ollama handles the "Low-Level Implementer" tasks (Phase 2B) for translating narrative beats into strict JSON ComfyUI prompts.
- **Software**: [Ollama](https://ollama.com/)
- **Network Configuration**: Must be configured to accept external connections from your orchestration machine. Set the environment variable `OLLAMA_HOST=0.0.0.0` before starting the service.
- **Recommended Models**: You need a model capable of strict JSON adherence that fits your hardware.
  - `ollama pull llama3` (8B) or `ollama pull mistral`

## 2. Image Generation Backend (ComfyUI)
ComfyUI acts as the headless rendering engine driven by the MCP server.
- **Software**: ComfyUI. **Crucial:** It must be started with the `--listen` flag (e.g., `python main.py --listen 0.0.0.0`) so the API is accessible over the network on port 8188.
- **Core Checkpoints (`/models/checkpoints/`)**:
  - Juggernaut XL (v9/v10) or Z-Image Turbo (Optimized for 12GB VRAM limits).
- **LoRAs (`/models/loras/`)**:
  - A dedicated Comic/Graphic Novel style LoRA (e.g., Western_Graphic_Novel_XL or Manga_Screentone).

### Essential ComfyUI Custom Nodes
Install these via the ComfyUI Manager to support the required workflows:
- **ComfyUI IP-Adapter Plus**: The core tool for character continuity.
  - *Pre-requisites*: Download IP-Adapter FaceID and Plus models (place in `models/ipadapter/`) and CLIP Vision models (place in `models/clip_vision/`).
- **ComfyUI ControlNet Union-ProMax**: The 2026 standard for multi-control (depth, pose, lineart) in a single VRAM-friendly node.
- **ComfyUI-Inspire-Pack** & **ComfyUI-Impact-Pack**: Essential utility node collections.
- **comfyui_controlnet_aux**: Contains the depth map preprocessors (like Zoe-Depth) required to extract geometry from location images during the Exploration Phase.
- **ComfyUI-Ultralytics-YOLO** (or **Impact-Pack Face Detectors**): Required to extract face bounding boxes at the end of the image generation. This spatial JSON data is critical for the Phase 5 Webtoon Overlay to prevent speech bubbles from covering faces.

## 3. Image Assembly Tooling
The remote server (or whichever machine is running the `magick_assemble` MCP tool) needs the binaries to perform the image stitching.
- **Software**: [ImageMagick](https://imagemagick.org/)
- **Installation (Linux)**: `sudo apt-get install imagemagick`
- **Verification**: Ensure the `magick` (or `montage`/`convert`) command is globally available in the system PATH.

## 4. Continuity Vault Access
Because ComfyUI needs to load reference images into its IP-Adapter and ControlNet nodes, it must have file-system access to the entire Continuity Vault.
- The master `/vault/` directory (including `/vault/characters/`, `/vault/locations/`, and `/vault/temporary/`) must be located on the remote server, or mounted as a shared network drive so the ComfyUI API payloads can successfully reference the image paths.
