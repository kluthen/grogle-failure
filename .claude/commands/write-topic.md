---
name: write-topic
description: Write or rewrite a world/ topic file that meets all quality requirements
triggers:
  - "write topic"
  - "create topic"
  - "new topic"
  - "topic for"
  - "add topic"
role: inquisitive
---

## Task: Write a World Topic

Follow these steps strictly and in order. A topic that skips any requirement will be
incomplete for the pre-processor injection system and for the worldbuilding database.

### Step 1 — Check for duplicates

Call `list_topics` filtered by the relevant kind. Then call `get_topic` for any entry
whose name or aliases overlap with the entity you are about to write. If a duplicate or
close overlap exists, prefer `update_topic` over creating a new file.

### Step 2 — Gather what you know

If you are working from a chapter or an existing draft, read the source material now.
List the entity's known attributes, relationships, and any names it goes by in the text.

### Step 3 — Determine the frontmatter fields

Every topic **must** have all of the following fields populated before it can be written:

#### `name` (required)
The single canonical name of the entity. This is what the database indexes and what
`get_topic` resolves against. Choose the most complete and unambiguous form:
- Character: full name or primary title if the name is unknown ("The Warden of Gates")
- Location: official name plus any meaningful qualifier ("108 Waterfall Valley Floor")
- Faction, item, concept: the term used by in-world characters

#### `kind` (required)
One of: `character`, `location`, `item`, `faction`, `concept`, `creature`, `species`, `event`, `note`, `arc`.

#### `aliases` (required when any alternate name exists)
A list of every alternate name, abbreviation, nickname, or shorthand the entity is
referred to by in the text. These feed the pre-processor's entity resolution —
if a name is not listed here it will not be matched automatically.

Examples:
```yaml
aliases: [108WFV, The Waterfall, Waterfall Haven]
aliases: [K, Captain Karima, The Iron Captain]
aliases: [WFV, Waterfall Floor]
```

If the entity has no known alternate names, omit the field entirely rather than
providing an empty list.

#### `summary` (required)
A single sentence, no more. Written so that a reader with no prior knowledge of
this story understands the entity immediately. Rules:
- No pronouns at the start ("She is…" → "Karima is…")
- No "this is about…" or "a topic covering…"
- No conjunctions connecting two separate facts — if you need "and", split it or pick the more important fact
- Written in present tense for living entities, past tense for historical ones

This sentence is injected verbatim into the agent's context on every query that
mentions the entity. Make it count.

#### `since_chapter` / `until_chapter` (optional)
Set `since_chapter` to the chapter number where the entity first appears. Set
`until_chapter` only when the entity definitively exits the narrative.

### Step 4 — Write the body

The body must be structured with `##` section headers. No free-form prose before
the first `##` header. Choose sections appropriate to the entity kind:

**Character:**
`## Description`, `## History`, `## Abilities`, `## Relationships`, `## Role`, `## Voice & Behavior`, `## POV Writing Style`

**Location:**
`## Geography`, `## Population`, `## Points of Interest`, `## Hazards`, `## History`

**Faction:**
`## Overview`, `## Structure`, `## Goals`, `## Relations`

**Item:**
`## Description`, `## Properties`, `## History`, `## Current Location`

**Concept:**
`## Definition`, `## Mechanics`, `## Known Examples`, `## Limitations`

**Creature / Species:**
`## Appearance`, `## Behavior`, `## Habitat`, `## Diet`, `## Threat Level`

**Event:**
`## Summary`, `## Participants`, `## Consequences`, `## History`

**Important Style Constraints (For Continuity):**
- **`## Voice & Behavior` (Characters):** You must detail their speech patterns (vocabulary, idioms, sentence length), physical tics, and typical reactions under stress. This governs how they speak and act in generated scenes.
- **`## POV Writing Style` (Characters):** You must define the narrator's voice when this character is the POV. Specify their sensory focus (what they notice first), internal monologue structure, and narrative tone (e.g., cynical, analytical).

You do not need to populate every section if the information is not yet established.
An empty section header with a single-line placeholder is fine:
```markdown
## Hazards
_Not yet established._
```

This preserves the structure for future updates and keeps the section skeleton
complete for context injection.

### Step 5 — Call `create_topic` or `update_topic`

Pass all gathered fields. Do not submit without a `summary`. Do not submit without
at least the section skeleton in `body`.

After the write, the tool re-indexes the file automatically — you do not need to
call any index command.

### Step 6 — Confirm to the writer

Report what was written:
- Canonical name and kind
- Aliases registered
- Summary sentence used
- Sections created
- File path

---

### Constraints

- `summary` is never optional. If you do not have enough information to write one,
  ask the writer before proceeding.
- `aliases` must include abbreviations the writer uses in conversation
  (e.g. "108WFV", "The Path"). These are matching keys, not decorative.
- Top-level section headers must use `##`. The pre-processor extracts the section
  skeleton by scanning for `##` lines only — `###` and deeper are ignored by the
  extractor but are valid and encouraged for internal organisation within a section.
- `book/` is permanently read-only. Topic files live in `world/` only.
- If the adjacency check surfaces a DUPLICATE match, stop and report it to the writer
  rather than overriding.
- **Language**: The YAML frontmatter keys (`name`, `kind`, `summary`, etc.) and the restricted `kind` values (e.g., `character`, `location`) MUST be in English. The actual content—including all `##` section headers and body text—must be written in the user's preferred language.
