# Webtoon Overlay System (Dialogue & Text)

This document defines how the pipeline handles speech bubbles and dialogue using a non-destructive, HTML-based Webtoon approach.

## The Strategy
Instead of permanently burning text into the image pixels, the final output of the comic pipeline is an `index.html` web app. The clean, assembled comic strips act as the background layer, while speech bubbles are rendered as dynamic CSS/SVG elements floated over the top. 

This allows for real-time typo correction, instantaneous translation, and dynamic resizing of text without ever needing to re-render the heavy Stable Diffusion images.

---

## Spatial Awareness (How to avoid covering faces)

If we overlay CSS bubbles blindly, they will inevitably cover the characters' faces. We must extract "director-level" spatial data from ComfyUI.

### ComfyUI Bounding Box Extraction
To achieve this, we append a **Computer Vision Node** (such as YOLOv8-Face or MediaPipe) to the very end of the ComfyUI workflow on the remote server.

1. **The Render**: Stable Diffusion finishes generating the 1024x1024 panel.
2. **The Scan**: Before saving, ComfyUI passes the pixels through the YOLO node.
3. **The Extraction**: The node detects where the faces/bodies are and outputs their X/Y coordinates.
4. **The Handoff**: The `comfy_generate_image` MCP tool returns the image file path AND the spatial JSON data back to the Orchestrator.

### The Dynamic Layout Algorithm
During Phase 4 (Assembly), instead of just gluing images together, the Publisher script runs a simple mathematical algorithm:
1. Read the `face_bounding_boxes` array for the panel.
2. Calculate the required width/height for the dialogue bubble based on the text length.
3. Search the upper quadrant of the 1024x1024 grid for the largest block of empty space that **does not intersect** with any face bounding boxes.
4. Inject those specific `top: 150px; left: 45px;` CSS coordinates into the final HTML output.

---

## The Data Schema Addition

To support this Webtoon overlay, the `panels.json` schema is expanded to track dialogue and spatial data:

```json
{
  "panel_id": "p_01",
  "image_path": "/output/chapter_05/raw_panels/p_01.png",
  "comfy_metadata": {
    "face_bounding_boxes": [
      {
        "entity_guess": "warrior_01",
        "x_min": 400, "y_min": 300, 
        "x_max": 550, "y_max": 450
      }
    ]
  },
  "dialogue": [
    {
      "speaker": "warrior_01",
      "text": "Take the gold.",
      "type": "speech" // Alternatives: "thought", "narration", "shout"
    }
  ]
}
```
