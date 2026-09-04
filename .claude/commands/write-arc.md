---
name: write-arc
description: Write or rewrite an arc master file and optionally flesh out individual beat files
triggers:
  - "write arc"
  - "create arc"
  - "new arc"
  - "arc for"
  - "add arc"
  - "flesh out arc"
  - "write beat"
  - "flesh out beat"
role: inquisitive
---

## Task: Write an Arc Topic File

Arc topic files live at `world/arcs/<slug>/arc_<slug>.md`. Each arc also has an
optional set of beat files at `world/arcs/<slug>/beat_<slug>.md`. The arc master
file is the planning document for the whole arc; beat files give depth to individual
spine points without bloating the master.

Follow these steps strictly and in order.

### Step 1 — Check for an existing arc

Call `list_topics(kind="arc")` to see what arc files already exist. Then call
`search_graph(type="arc", query=<name>)` to check the graph row. If either returns
a match, use `get_topic` to read the existing file before deciding whether to create
or update.

If the arc exists as a graph row but has no topic file, skip to Step 3.

### Step 2 — Gather what you know

Read the relevant chapters or drafts if the arc is already in progress. List:
- The inciting event and the arc's endpoint (resolved or still open)
- Which characters are the drivers vs the affected parties
- What changes in the world by the time the arc closes
- Any beats the writer has already named or described

### Step 3 — Determine the frontmatter fields

#### `name` (required)
The arc's canonical title. Choose a form that is unambiguous and stable — it will
be used as the folder slug and as the resolution key in `search_graph`. Avoid
names that duplicate a character or location name.

#### `kind` (required)
Always `arc` for the master file.

#### `aliases` (required when the arc is referred to by shorthand)
Any abbreviation or nickname the writer uses in conversation. These feed the
pre-processor's entity resolution so that the arc context is injected automatically
when the writer mentions the arc by name.

#### `summary` (required)
A single sentence describing what the arc is about at the narrative level — not a
plot summary, but what the arc *means*. Rules:
- No pronouns at the start
- No conjunctions connecting two separate facts
- Present tense for open arcs, past tense for resolved ones

Examples:
```
Takeo's arc of reclaiming agency after years of enforced helplessness.
The guild's slow collapse under the weight of its own corrupt hierarchy.
```

### Step 4 — Write the arc body

Use the following sections. Omit a section only if no information is established
yet — prefer a placeholder over a missing header.

#### `## Overview`
Two to four sentences. What triggers the arc, what conflict sustains it, what
resolves (or fails to resolve) it. Written for a reader who knows the world but
has not read the story.

#### `## Themes`
Bullet list. The abstract concerns the arc dramatises — not plot beats, but the
questions the arc poses to the reader. Examples: *loyalty vs survival*, *the cost
of completionism*, *what it means to rebuild identity*.

#### `## Stakes`
What is at risk if the arc fails or is abandoned — for each major character and
for the world. Be concrete: not "Takeo might fail" but "Takeo loses his only
framework for self-worth and reverts to passive dependency".

#### `## Character Goals`
One subsection per character involved. For each: what they want (surface goal),
what they need (underlying need), and what they fear losing. Keep to the beats
of this arc, not the character's entire arc.

#### `## Beat Outline`
An ordered list of the arc's spine points with their current status. Format:
```markdown
1. **Opening** — Takeo discovers the sealed dungeon exists (`planned`)
2. **Milestone** — First failed attempt; party fractures (`planned`)
3. **Climax** — Solo run, Completionist seal activates under pressure (`planned`)
4. **Resolution** — Seal acknowledged; Takeo redefines what completion means (`planned`)
```
Status values: `planned`, `written`, `skipped`. When a beat has a topic file,
add the path inline: `[beat file](world/arcs/slug/beat_slug.md)`.

#### `## Open Questions`
Bullet list of unresolved decisions: plot branches, character choices not yet
made, world-state ambiguities that this arc depends on. This section is the
writer's scratchpad — it is not injected into the agent's context during writing.

### Step 5 — Call `arc_describe` (REPL) or `upsert_arc` (MCP)

Pass all frontmatter fields and the full body. The tool creates both the graph row
and the topic file atomically, then re-indexes. You do not need to call `create_topic`
separately.

If the arc already exists and you are enriching it, pass the updated body. The tool
preserves the existing graph row status and ordinal.

### Step 6 — Decide which beats need a file

A beat needs its own file when:
- It requires more than two sentences of staging context
- Multiple characters have conflicting goals that need tracking
- The writer will be drafting it in a dedicated session

A beat does NOT need a file when:
- It is a transitional milestone the writer can derive from the arc master
- It is already marked `written`

For each beat that needs a file, proceed to Step 7. Otherwise skip to Step 8.

### Step 7 — Write beat files (repeat per beat)

Beat files live at `world/arcs/<arc_slug>/beat_<beat_slug>.md`.

**Frontmatter:**
```yaml
---
bucket: world
kind: beat
name: <Beat Name>
arc: <arc_slug>
summary: <one sentence — what happens and why it matters>
---
```

The `arc:` field is mandatory. It is the back-reference used by the agent to
fetch the arc master file when a beat file alone is insufficient.

**Body sections:**

#### `## What Must Happen`
The non-negotiable narrative requirement: what concrete event occurs, what state
changes as a result. If this beat were cut, what would the reader lose?

#### `## Character Positions`
Where each involved character stands emotionally and physically at beat entry.
What they want from this scene. What they are willing to do.

#### `## Reader Experience`
What the reader should feel and understand by the end of this beat. What question
gets answered? What new question opens?

#### `## World State Changes`
Bullet list of facts that are different after this beat: relationships, knowledge,
physical state, political situation. These inform continuity checking.

#### `## Notes`
Staging ideas, alternative approaches, open micro-questions. Not injected into
the agent's writing context.

Call `beat_add` or `upsert_arc_beat` with the beat body to create the file. The
tool will echo the path back — confirm it matches the Beat Outline entry in the
arc master file and update that entry if needed.

### Step 8 — Confirm to the writer

Report:
- Arc canonical name and status
- Summary sentence used
- Sections created in the master file
- Beat files created (if any) with their paths
- Any open questions surfaced during writing that the writer should resolve

---

### Constraints

- `summary` is never optional for the master file. If you cannot write one from
  the available information, ask the writer before proceeding.
- Do not use `create_topic` for arc or beat files — use the arc tools, which keep
  the graph row and the topic file in sync.
- Beat files reference the arc master via the `arc:` frontmatter field. Never
  omit this field on a beat file.
- During writing sessions, load the beat file first. Load the arc master only when
  the beat file does not provide enough context. Never load both in full if the beat
  file covers the need.
- `book/` is permanently read-only. Arc and beat files live in `world/arcs/` only.
