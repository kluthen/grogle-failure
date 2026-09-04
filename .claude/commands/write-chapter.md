# Skill: Write Chapter

This skill provides the structure and guidelines for writing or outlining a chapter in Watson.

## Chapter Frontmatter

Every chapter file must start with a standardized YAML frontmatter block. This structured data is crucial for querying the timeline, anchoring the setting, and tracking narrative progression.

Use the following frontmatter template for a chapter:

```yaml
---
chapter_id: 001
chapter_name: "Human readable name of the chapter"
pov: ["Character Name"] # Or "Third Person"
location: ["Location Name"]
date: "12 01 1029 10:31" # In book time (can be obscure like 'in the evening', 'the following day', or specific)
presence: ["Main Character in presence", "Another Character"]
mood: ["mood", "another mood"] # Most prevalent moods through the chapter
description: "One-liner of the objective of this chapter"
arcs: ["Arc Beat Name"] # May have one or more such beats being fulfilled
notes: "Any internal notes for the author about the chapter's execution"
---
```

### Frontmatter Field Explanations

- **`chapter_id`**: Numeric ordered value (e.g., 001, 002...) to ensure correct chronological sorting.
- **`chapter_name`**: A human-readable title or name for the chapter.
- **`pov`**: Dictates the primary perspective (e.g., a specific character or "third person"). If it's a specific character, ensure you follow their `POV Writing Style` from their topic file.
- **`location`**: The main setting(s) where the chapter takes place.
- **`date`**: Mostly helps to anchor the setting. It can be a specific timestamp or a relative expression.
- **`presence`**: A list of the main characters present in the chapter.
- **`mood`**: The most prevalent atmosphere or emotional tones throughout the chapter.
- **`description`**: A concise one-liner summarizing the primary objective or event of the chapter.
- **`arcs`**: Links the chapter to the broader narrative by specifying which Arc Beats are being fulfilled or advanced.
- **`notes`**: Optional area for author notes, open questions, or reminders.

## Writing Guidelines

When writing the chapter body, always refer to the Global Style (`world/style.md`) and the respective characters' `Voice & Behavior` and `POV Writing Style` defined in their topic files. Maintain continuity by verifying facts, character traits, and current locations against the graph database using Watson's tools.
