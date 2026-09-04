# Output Specification

## Overview
This document defines the deliverable formats, resolution strategy, and directory structure for the comic pipeline's outputs.

---

## Output Formats

The pipeline produces **two** distinct output formats from the same rendering pass:

### 1. Webtoon (Web — Primary)
An interactive HTML viewer optimized for vertical scrolling on screens.

- **Deliverable**: A self-contained folder (`/output/chapter_XXX/webtoon/`) containing `index.html`, image assets, and embedded CSS/JS.
- **Text Handling**: Speech bubbles, narration boxes, and IM messages are CSS-positioned overlays (non-destructive). Text can be corrected, resized, or translated without re-rendering images.
- **Image Format**: WebP (lossy, quality 85) for fast web loading.
- **Resolution**: Native render resolution (1024px per panel side).
- **Language**: Configurable per build. Default `fr`, with `en` as alternate. The HTML supports a language toggle if both are provided.

### 2. Print-Ready Pages (Static — Secondary)
Traditional comic pages with text permanently composited into the image, suitable for PDF export or physical printing.

- **Deliverable**: A folder of high-resolution PNG files (`/output/chapter_XXX/print/page_01.png`, etc.).
- **Text Handling**: Speech bubbles, narration boxes, and IM messages are rendered directly onto the image using ImageMagick text compositing. This is a **destructive, one-way** operation.
- **Image Format**: PNG (lossless).
- **Resolution**: Upscaled (see Resolution Strategy below).
- **Language**: Baked at build time. Separate builds for FR and EN.

---

## Resolution Strategy

| Stage | Resolution | Format | Purpose |
|---|---|---|---|
| Raw panel (ComfyUI output) | 1024×1024 | PNG | Base render. Optimized for 12GB VRAM (RTX 3060). |
| Assembled strip/page (web) | Native (e.g., 3174×1054 for 3-panel strip) | WebP | No upscale needed for screen viewing. |
| Assembled strip/page (print) | 2× upscale (e.g., 6348×2108) | PNG | Upscaled via a dedicated `upscale.json` ComfyUI workflow or Real-ESRGAN CLI. |
| Final print page (300 DPI) | Target: ~2480×3508 (A4 at 300 DPI) | PNG/TIFF | Requires layout adjustment — see Print Layout below. |

### Print Layout Considerations
The web layout (horizontal strips stacked vertically) is designed for infinite scroll. For print, strips must be grouped onto fixed-dimension pages (A4, US Letter, or custom). The `magick_assemble` tool handles this in a secondary pass:
1. Take the assembled strips for a chapter.
2. Stack them vertically onto a fixed-height canvas with margins.
3. If a strip doesn't fit on the current page, start a new page.
4. Add page numbers and optional headers/footers.

---

## Directory Structure

```
/output/
└── chapter_001/
    ├── raw_panels/              # Phase 3 output
    │   ├── p_01.png
    │   ├── p_02.png
    │   └── ...
    ├── assembled/               # Phase 4 output (strips and pages)
    │   ├── page_01.png
    │   ├── page_02.png
    │   └── ...
    ├── webtoon/                 # Phase 5 output (web viewer)
    │   ├── index.html
    │   ├── assets/
    │   │   ├── page_01.webp
    │   │   └── ...
    │   └── style.css
    ├── print/                   # Optional print export
    │   ├── page_01_300dpi.png
    │   └── ...
    ├── beats.json               # Phase 1 artifact
    ├── layout_plan.json         # Phase 2A artifact
    └── panels.json              # Phase 2B artifact
```

---

## Versioning

Each pipeline run is **non-destructive by default**:
- First run writes to `/output/chapter_001/`.
- Subsequent runs write to `/output/chapter_001_v2/`, `_v3/`, etc.
- The orchestrator can force overwrite with an explicit `--overwrite` flag.

**Selective re-render**: Individual panels can be re-rendered without rebuilding the entire chapter. The orchestrator updates the specific panel in `raw_panels/`, then re-runs Phase 4 (Assembly) and Phase 5 (Webtoon) which are fast operations.

---

## Sound Effects (SFX)

Visual sound effects (`BOOM`, `CRACK`, `WHOOSH`) are handled differently from dialogue:

- **In the SDXL prompt**: The action description should include the implied visual effect (e.g., `"impact shockwave, debris flying"`) but **not** the text itself.
- **In the Webtoon overlay**: SFX text is rendered as a special CSS class with large, stylized fonts, rotation, and color. The `dialogue` schema supports a `"type": "sfx"` value for this purpose.
- **In print output**: SFX text is composited with a bold, angled font at the coordinates specified by the overlay algorithm.

---

## Narration Boxes (Inner Monologue)

Given that this book is entirely first-person narration, the pipeline must handle **narration boxes** as a first-class element:

- Narration boxes use `"type": "narration"` in the dialogue schema.
- In the Webtoon overlay, they render as **rectangular boxes** with a distinct background color (semi-transparent dark), positioned at the top or bottom of the panel.
- They are **not** tailed to a character (unlike speech bubbles).
- Maximum ~30 words per box. Longer monologues split across multiple panels.
