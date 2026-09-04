# Camera & Transition Vocabulary

## Overview
Standardized vocabulary for the Storyboarder (Phase 2) to describe camera positions, angles, and panel transitions. Using a fixed enum ensures consistency — the Director, the prompt engineer, and the SDXL keywords all align.

---

## Shot Types

| Enum Value | Description | SDXL Keywords | Use |
|---|---|---|---|
| `extreme_close_up` | Eyes, mouth, a hand gripping something. | `extreme close-up, macro detail, shallow depth of field` | Emotional intensity, details |
| `close_up` | Head and shoulders. | `close-up portrait, head and shoulders, bokeh background` | Dialogue, reactions, monologue |
| `medium_close_up` | Chest and up. | `medium close-up, upper body, chest up` | Conversation with gestures |
| `medium_shot` | Waist-up. Default comic shot. | `medium shot, waist up, half body` | General action and dialogue |
| `medium_wide_shot` | Knees-up. | `medium wide shot, three-quarter body` | Character in environment |
| `wide_shot` | Full body, environment shown. | `wide shot, full body, environmental context` | Action, spatial relationships |
| `extreme_wide_shot` | Character small in vast environment. | `extreme wide shot, vast landscape, tiny figure, panoramic` | Scale, isolation |
| `establishing_shot` | Pure environment, no character focus. | `establishing shot, cityscape, architectural, no people` | Scene openers |

---

## Camera Angles

| Enum Value | Description | SDXL Keywords | Use |
|---|---|---|---|
| `eye_level` | Neutral, at character's eye height. | `eye level, straight on` | Standard dialogue |
| `low_angle` | Looking up. Makes subject imposing. | `low angle, looking up, imposing` | Power, threat, heroic |
| `high_angle` | Looking down. Makes subject vulnerable. | `high angle, looking down, diminished` | Vulnerability, defeat |
| `dutch_angle` | Tilted frame. Visual tension. | `dutch angle, tilted frame, canted angle` | Panic, disorientation |
| `bird_eye` | Directly overhead. | `bird's eye view, top-down, directly overhead` | Tactical layout views |
| `over_the_shoulder` | Behind one character, looking at another. | `over the shoulder, OTS shot` | Two-person dialogue |
| `pov` | What the character sees. | `first person POV, subjective camera` | AR/IM interfaces |

---

## Panel Transitions

| Enum Value | Description | Layout Implication |
|---|---|---|
| `moment_to_moment` | Tiny time progression, same action. | Same strip, adjacent panels. |
| `action_to_action` | Same scene, different action. Most common. | Same strip or page. |
| `subject_to_subject` | Same scene, camera shifts to different character. | Same strip. Dialogue reactions. |
| `scene_to_scene` | New location or time skip. | **Page break** + establishing shot. |
| `aspect_to_aspect` | Same moment, different environmental aspect. | Same page. Mood montage. |

---

## Composition Modifiers

| Modifier | SDXL Keywords | Purpose |
|---|---|---|
| `dramatic_lighting` | `dramatic lighting, chiaroscuro, strong shadows, rim light` | Tension |
| `silhouette` | `silhouette, backlit, dark figure against bright background` | Mystery, reveals |
| `motion_blur` | `motion blur, speed lines, dynamic movement` | Fast action |
| `depth_of_field` | `shallow depth of field, bokeh, blurred background` | Focus isolation |
| `rain` | `rain, wet surfaces, reflections on ground, water droplets` | Dystopian atmosphere |
| `ar_glow` | `holographic interface glow, blue light on face, floating UI` | AR overlay interaction |

---

## Usage in `layout_plan.json`

Format: `{shot_type}` or `{shot_type}, {angle}` or `{shot_type}, {angle}, {modifier}`.

```json
{
  "panel_id": "p_01",
  "camera": "establishing_shot"
},
{
  "panel_id": "p_02",
  "camera": "medium_shot, low_angle"
},
{
  "panel_id": "p_03",
  "camera": "extreme_close_up, eye_level, dramatic_lighting"
},
{
  "panel_id": "p_04",
  "camera": "pov, eye_level, ar_glow"
}
```

Phase 2B reads the `camera` field and maps it to SDXL keywords from the tables above.
