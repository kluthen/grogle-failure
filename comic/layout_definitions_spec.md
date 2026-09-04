# Layout Definitions (Phase 4 Assembly)

This document defines the strict enum values for `layout_type` used in the `panels.json` schema. It dictates exactly how the `magick_assemble` MCP tool must translate those strings into underlying ImageMagick subprocess commands.

## Core Assembly Logic
ImageMagick uses two primary flags to glue images, which form the basis of our comic grids:
- **`+append`**: Glues images side-by-side (Horizontally).
- **`-append`**: Glues images top-to-bottom (Vertically).
- **Gutters**: Before any gluing happens, the MCP tool must run `magick {image} -bordercolor black -border 15x15 {output}` on every raw panel to create the traditional black comic borders (gutters).

*(Assumption: All raw ComfyUI panel outputs are 1024x1024 squares)*

---

## Supported Layout Types

### 1. `"single_splash"`
Used for massive, high-impact establishing shots or critical action beats.
- **Expected Panels**: 1
- **Assembly Logic**: No gluing required. Just add a thick outer border.
- **Subprocess**: 
  `magick p_01.png -bordercolor black -border 30x30 final_splash.png`

### 2. `"2_panel_strip"`
A wide, cinematic aspect ratio showing a quick sequence or a back-and-forth dialogue.
- **Expected Panels**: 2
- **Assembly Logic**: Add gutters to individual panels, then glue horizontally.
- **Subprocess**:
  `magick p_01_bordered.png p_02_bordered.png +append final_strip.png`

### 3. `"3_panel_strip"`
The standard comic strip format. Great for action sequences (Setup -> Action -> Result).
- **Expected Panels**: 3
- **Assembly Logic**: Add gutters to individual panels, then glue horizontally.
- **Subprocess**:
  `magick p_01_bordered.png p_02_bordered.png p_03_bordered.png +append final_strip.png`

### 4. `"2x2_grid"`
A dense block of information, often used for fast-paced dialogue or simultaneous events.
- **Expected Panels**: 4
- **Assembly Logic**: Create two `2_panel_strip` blocks horizontally, then glue them vertically.
- **Subprocess**:
  1. `magick p_01_b.png p_02_b.png +append row_1.png`
  2. `magick p_03_b.png p_04_b.png +append row_2.png`
  3. `magick row_1.png row_2.png -append final_grid.png`

### 5. `"full_page_9_grid"`
A massive, complete comic page layout.
- **Expected Panels**: 9
- **Assembly Logic**: Creates three `3_panel_strip` blocks, then glues them vertically.
- **Subprocess**:
  1. `magick p_01 p_02 p_03 +append row_1.png`
  2. `magick p_04 p_05 p_06 +append row_2.png`
  3. `magick p_07 p_08 p_09 +append row_3.png`
  4. `magick row_1.png row_2.png row_3.png -append final_page.png`
