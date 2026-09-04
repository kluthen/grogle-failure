# World-to-Vault Bridge

## Problem
The project already contains rich narrative metadata for **22 characters** (in `world/characters/`) and **10 locations** (in `world/locations/`), written as markdown files with YAML frontmatter. The comic pipeline's Continuity Vault expects a completely different format: flat JSON files with specific fields (`entity_id`, `physical_description`, `assets`).

Without a bridge, every character and location would need to be manually re-described — duplicating work and introducing inconsistencies between the narrative source-of-truth and the visual pipeline.

## Solution
A conversion layer that reads `world/` markdown files and produces Vault-ready JSON skeletons. The conversion is **semi-automated**: structural fields are mapped deterministically, while the `physical_description` (which must be SDXL-optimized) requires a one-time LLM pass or manual edit.

---

## Field Mapping

### Characters: `world/characters/{name}.md` → `/vault/characters/{entity_id}.json`

| World Field | Vault Field | Conversion Rule |
|---|---|---|
| `name` (frontmatter) | `name` | Direct copy |
| `name` (lowercased, spaces→underscores) | `entity_id` | `"Aymeric Bator"` → `"aymeric_bator"` |
| — | `type` | Always `"character"` |
| `## Description` section | `physical_description` | **Requires LLM extraction.** The world description mixes physical traits with backstory. The bridge must extract only visual/physical attributes and rewrite them as SDXL-friendly descriptors. |
| — | `core_tags` | **Derived from `physical_description`.** Comma-separated keywords for quick prompt injection (e.g., `"male, mixed-race, curly hair, grey arm, silver scars"`). |
| — | `assets.face_anchor` | Path placeholder. Populated after the Exploration Phase generates the FaceID portrait. Initially `null`. |
| — | `assets.body_anchor` | Path placeholder. Populated after the Exploration Phase generates the body anchor. Initially `null`. |

### Locations: `world/locations/{name}.md` → `/vault/locations/{entity_id}.json`

| World Field | Vault Field | Conversion Rule |
|---|---|---|
| `name` (frontmatter) | `name` | Direct copy |
| `name` (lowercased, spaces→underscores) | `entity_id` | `"Le Bunker"` → `"le_bunker"` |
| — | `type` | Always `"location"` |
| `## Description` + `## Points of Interest` | `environmental_description` | **Requires LLM extraction.** Merge the Description and POI sections, then rewrite as SDXL-friendly environmental descriptors focusing on visual elements (lighting, materials, atmosphere). |
| — | `assets.vibe_anchor` | Path placeholder. Initially `null`. |
| — | `assets.depth_map` | Path placeholder. Initially `null`. |

---

## Conversion Example

### Input: `world/characters/aymeric_bator.md`

**Frontmatter:**
```yaml
name: Aymeric Bator
aliases: [Aymeric, Aym, A. Bator]
```

**Description Section (raw):**
> Narrateur de l'histoire. Métis (mère martiniquaise dont il a hérité des cheveux crépus), 25 ans, en bas de l'échelle sociale. Employé d'un centre d'appel d'Argos Corporation où il suit des scripts toute la journée. Cynique, fataliste, porté sur l'humour vulgaire, mais fondamentalement loyal. Pseudonyme réseau : A. Bator. Après ses transformations, son bras gauche prend une teinte grisâtre et son corps se couvre de cicatrices argentées.

### Output: `/vault/characters/aymeric_bator.json`

```json
{
  "entity_id": "aymeric_bator",
  "type": "character",
  "name": "Aymeric Bator",
  "physical_description": "A mixed-race young man in his mid-20s with short curly black hair, wearing plain grey recycled cotton clothing. His left arm has an unnatural greyish tint, and faint silver scars trace lines across his exposed skin. Lean build, tired eyes, slightly defiant posture.",
  "core_tags": "male, mixed-race, curly black hair, grey left arm, silver scars, plain grey clothing, young adult",
  "assets": {
    "face_anchor": null,
    "body_anchor": null
  }
}
```

**Note:** The `physical_description` has been rewritten from narrative French to SDXL-optimized English. This is the step that requires either:
1. An LLM pass (send the French description + chapter context → ask for SDXL-ready English visual description), or
2. Manual writing by the author.

---

## Conversion Workflow

### Step 1: Generate JSON Skeletons (Automated)
A script reads every `.md` file in `world/characters/` and `world/locations/`, extracts the frontmatter and description sections, and writes skeleton `.json` files to `/vault/` with `physical_description` set to the raw French text and `assets` set to `null`.

### Step 2: LLM Description Rewrite (Semi-Automated)
For each skeleton, the orchestrator (or a batch script using Ollama) rewrites the `physical_description` from narrative French into SDXL-optimized English visual descriptors. The author reviews and approves each rewrite.

### Step 3: Visual Asset Generation (Exploration Phase)
Once descriptions are approved, the Exploration Phase (`exploration_phase_spec.md`) is run for each major character and location. The generated FaceID portraits, body anchors, and vibe images are saved, and the `assets` paths in the JSON are updated via the `vault_commit` MCP tool.

### Step 4: Linking
The vault JSON files reference `world/` entities by matching `entity_id`. The chapter frontmatter field `presence` already lists character names — the orchestrator resolves these to vault entries during Phase 1 (Writer) by matching against the `name` or `aliases` fields from the world files.

---

## Chapter Frontmatter Integration
The existing chapter frontmatter provides valuable signals for Phase 1:

```yaml
chapter_id: 001
chapter_name: "La Mise à Jour"
pov: ["Aymeric Bator"]
location: ["Complexe Argos - Bayeux II", "Rues de Bayeux II", "Commissariat de Bayeux II"]
presence: ["Aymeric Bator", "Alex"]
mood: ["banal", "désinvolte", "tension montante"]
```

| Frontmatter Field | Comic Pipeline Use |
|---|---|
| `pov` | Determines the primary camera subject for panels. |
| `location` | Maps to vault location entries. If a location has no vault entry, it gets a temporary description. |
| `presence` | Pre-casts the scene — the orchestrator loads these vault entries before entering Phase 2. |
| `mood` | Influences color grading, lighting direction, and atmospheric keywords in the SDXL prompt. |
| `chapter_id` | Used for output directory naming (`/output/chapter_001/`). |

---

## Alias Resolution
Characters in prose are referenced by various names (e.g., "Alex", "Fara", "le lieutenant"). The vault bridge must maintain an alias lookup table derived from the `aliases` frontmatter field in `world/characters/`:

```json
{
  "Aymeric": "aymeric_bator",
  "Aym": "aymeric_bator",
  "A. Bator": "aymeric_bator",
  "Fara": "fara_nakach",
  "Lieutenant": "fara_nakach",
  "Le lieutenant": "fara_nakach"
}
```

This table is used by the Writer agent (Phase 1) to resolve character mentions in the prose to vault `entity_id` values when populating the `active_characters` array in `beats.json`.
