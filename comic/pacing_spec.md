# Pacing Heuristics (Phase 2A — The Director)

## Overview
Phase 2A is the most creatively complex step in the pipeline. The Director agent must decide how many panels each narrative beat gets, what layout template to use, and how beats group into pages. This document defines the heuristics and constraints that guide those decisions, transforming them from "the AI decides" into a structured, reproducible system.

## Core Concept: Beat Weight
Every beat extracted in Phase 1 is assigned a **weight** value (1–5) based on its narrative function. The weight determines how much visual real estate the beat receives.

| Weight | Label | Description | Typical Layout |
|---|---|---|---|
| **1** | Transition | Scene-setting filler, time passing, travel. | 1 panel in a shared strip |
| **2** | Dialogue | Character conversation, exposition. | 2–3 panel strip |
| **3** | Action | Physical movement, fights, chases. | 3-panel strip or 2×2 grid |
| **4** | Climax | Major turning point, revelation, emotional peak. | Full splash page |
| **5** | Splash | Establishing shot, title-worthy moment, "jaw-drop" visual. | Full splash page (oversized) |

### Weight Assignment Rules
The Writer agent (Phase 1) assigns weights during beat extraction using these heuristics:

1. **Dialogue density**: If the beat contains ≥3 dialogue exchanges → weight ≥ 2 (give it panels for the back-and-forth).
2. **Action verbs**: If the beat contains high-energy verbs (frapper, courir, exploser, hurler, s'effondrer) → weight ≥ 3.
3. **Scene transition**: If the beat introduces a new location or significant time jump → weight ≥ 2 (needs an establishing shot).
4. **Emotional payload**: If the beat contains a character revelation, death, or first appearance → weight ≥ 4.
5. **Chapter opening/closing**: First and last beats of a chapter get a +1 weight bonus (bookend the reader).

---

## Page Budget
Before layout begins, the Director calculates a **page budget** for the chapter:

```
target_pages = ceil(total_beats / beats_per_page_average)
```

| Chapter Type | Beats per Page (avg) | Typical Page Count |
|---|---|---|
| Dialogue-heavy (e.g., Log #1) | 4–6 | 6–8 pages |
| Action-heavy (e.g., Log #5) | 2–4 | 8–12 pages |
| Mixed | 3–5 | 7–10 pages |

The Director can exceed the budget for action sequences but should avoid bloating dialogue scenes beyond their narrative weight.

---

## Layout Selection Algorithm

Once beats are weighted, the Director groups them into pages using a **bin-packing** approach:

### Step 1: Calculate Panel Slots per Page
Each `layout_type` from `layout_definitions_spec.md` has a fixed panel capacity:

| Layout Type | Panel Slots | Total Weight Capacity |
|---|---|---|
| `single_splash` | 1 | 4–5 (one heavy beat) |
| `2_panel_strip` | 2 | 2–3 |
| `3_panel_strip` | 3 | 3–5 |
| `2x2_grid` | 4 | 4–6 |
| `full_page_9_grid` | 9 | 6–10 |

### Step 2: Group Beats into Pages
Process beats sequentially (they are already in narrative order):

1. **Weight 4–5 beats** → Automatically get a `single_splash` page. No other beats share their page.
2. **Weight 3 beats** → Start a new `3_panel_strip` or `2x2_grid`. Fill remaining slots with adjacent weight 1–2 beats.
3. **Weight 2 beats** → Group into `2_panel_strip` or `3_panel_strip` blocks. Prioritize grouping dialogue exchanges into the same strip for visual flow.
4. **Weight 1 beats** → Fill remaining slots in existing pages. Never give a weight-1 beat its own page.

### Step 3: Scene Boundary Enforcement
**A page must never mix two different scenes** (different `scene_id` from `beats.json`). If grouping would cross a scene boundary, start a new page even if the current one has empty slots. This prevents visual whiplash from suddenly changing location mid-page.

### Step 4: Pacing Rhythm
To avoid visual monotony, the Director enforces variety:
- Never place 3+ consecutive `3_panel_strip` pages in a row — insert a `2_panel_strip` or `2x2_grid` to break the pattern.
- After a `single_splash`, the next page should be dense (grid or multi-strip) to create a visual contrast.
- End each scene on a natural breakpoint — the last page of a scene should not feel like it ran out of space.

---

## Beat Expansion: One Beat → Multiple Panels
Some beats expand to fill multiple panels within their layout:

| Beat Type | Panel Expansion |
|---|---|
| Single action | 1 panel |
| Action sequence ("draws sword and charges") | 2–3 panels (Setup → Action → Impact) |
| Dialogue exchange (2 speakers) | 2 panels (speaker A → speaker B), or 3 panels (A → B → reaction) |
| Dialogue exchange (3+ speakers) | 1 panel per speaker |
| Emotional reaction | 1 close-up panel |
| Environmental establishing | 1 wide-shot panel |

When expanding, each sub-panel inherits the parent beat's characters and location but gets its own `sdxl_prompt` and camera angle.

---

## The `layout_plan.json` Schema Addition

The Phase 2A output extends `beats.json` with layout metadata:

```json
{
  "chapter_id": "ch_01",
  "page_budget": 8,
  "pages": [
    {
      "page_id": "page_01",
      "scene_id": "s_01",
      "layout_type": "single_splash",
      "beats_covered": ["b_01"],
      "panels": [
        {
          "panel_id": "p_01",
          "beat_ref": "b_01",
          "action": "Wide establishing shot of Bayeux II at sunset, towering identical concrete buildings stretching to the horizon, AR advertisements floating in the sky.",
          "camera": "establishing_shot",
          "active_characters": [],
          "location_id": "bayeux_ii"
        }
      ]
    },
    {
      "page_id": "page_02",
      "scene_id": "s_01",
      "layout_type": "3_panel_strip",
      "beats_covered": ["b_02", "b_03"],
      "panels": [
        {
          "panel_id": "p_02",
          "beat_ref": "b_02",
          "action": "Aymeric floating in the gel-filled work pod, eyes closed, surrounded by virtual Japanese temple scenery.",
          "camera": "medium_shot",
          "active_characters": ["aymeric_bator"],
          "location_id": "complexe_argos"
        },
        {
          "panel_id": "p_03",
          "beat_ref": "b_02",
          "action": "The pod opens like a jewel box, gel dripping, Aymeric climbing out.",
          "camera": "wide_shot",
          "active_characters": ["aymeric_bator"],
          "location_id": "complexe_argos"
        },
        {
          "panel_id": "p_04",
          "beat_ref": "b_03",
          "action": "Close-up of Aymeric's face under the shower spray, IM notification windows floating around his head.",
          "camera": "close_up",
          "active_characters": ["aymeric_bator"],
          "location_id": "complexe_argos"
        }
      ]
    }
  ]
}
```

## Dialogue Assignment
Dialogue is assigned at the panel level, not the beat level. During Phase 2A, the Director decides which lines of dialogue (extracted from the prose) go with which panel:

- **Rule**: A panel should carry **at most 2 dialogue bubbles**. More than 2 makes the panel cluttered and forces the Webtoon overlay into tiny text.
- **Exception**: A `single_splash` page can carry up to 3–4 bubbles if they are short (≤10 words each).
- Narration boxes (inner monologue, which is pervasive in this book) count toward the bubble limit.
