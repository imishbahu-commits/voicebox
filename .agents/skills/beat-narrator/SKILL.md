---
name: beat-narrator
description: Generate high-quality beat-by-beat text-to-speech narration for YouTube explainer videos in the FoodCode / Paint Explainer style — every beat 12-16 words, 2.0-6.0 s of real audio, with a measured cut list (beat marks) aligned to each beat's visual. Use when the user wants narration for a video script, per-beat voiceover audio, a cut list / EDL, or wants beats validated against the 12-16 word and 2-6 second rules.
---

# Beat Narrator — FoodCode-style TTS with measured beat marks

Voicebox is the TTS engine. This skill is the layer that makes a script
*cuttable*: it forces every narration beat into the measured FoodCode / Paint
Explainer window, synthesises one audio file per beat, and derives the cut list
from the audio that actually came out.

## The two hard rules

| Rule | Value | Why |
|---|---|---|
| Words per beat | **12–16** | The FoodCode/Paint Explainer reference cadence. Under 12 the cut stutters; over 16 the beat needs its own image anyway. |
| Seconds per beat | **2.0–6.0** (median 3.6) | Measured cut interval from the reference video (`skills/references/paint-explainer-autopsy.md`). |

Derived: **1 beat = 1 image = 1 audio file = 1 cut.** Never stretch a beat to
save an image. A long sentence becomes two beats, each with its own visual.

## Pipeline

```bash
# 1. Split raw narration into compliant beats (writes beats.json)
python3 narration/beat_narrator.py split script.txt -o projects/myvid

# 2. Fill in the visual field for every beat, then validate
python3 narration/beat_narrator.py check projects/myvid/beats.json --rows

# 3. Synthesise one file per beat
python3 narration/beat_narrator.py synth projects/myvid/beats.json --backend arena
python3 narration/beat_narrator.py synth projects/myvid/beats.json \
    --backend voicebox --profile <profile-id> --base http://127.0.0.1:17493

# 4. Measure the real audio and emit the cut list
python3 narration/beat_narrator.py marks projects/myvid/beats.json
```

Step 4 writes three artefacts into the project directory:

- `beat_marks.json` — start/end/duration/frames per beat + the visual and
  narration attached to each mark. This is the source of truth for the edit.
- `beat_marks.csv` — same rows, spreadsheet-friendly.
- `beat_marks.edl` — CMX3600 EDL for Premiere / Resolve / Final Cut.

## Beat schema

```json
{
  "id": 16,
  "part": 2,
  "narration": "That sensation is not acidity. It is an enzyme called bromelain digesting you.",
  "scene": "A bromelain enzyme shape cutting into a tongue with tiny scissors",
  "label": "BROMELAIN",
  "transition": "cut"
}
```

- `narration` — the spoken line. 12–16 words.
- `scene` — what is **on screen**, never an emotion. "a bromelain enzyme shape
  cutting into a tongue", never "epic reveal". Forbidden: cinematic, moody,
  painterly, film grain, dark palettes, shadows, gradients, photorealism.
- `label` — short on-screen caption in caps.
- `transition` — `cut` | `revealing` | `disappearing` | `switching`.

## TTS backends

**`--backend arena`** (default) — writes `audio/tts_manifest.json` plus one
`audio/beatNN.txt` per beat, which the agent feeds to its `generate_speech`
tool. Use this when Voicebox's local engines are not installed: they need
several GB of model weights and ideally a GPU. Cap is **10 clips per turn**;
resume with `--limit N` and keep going next turn.

**`--backend voicebox`** — drives the Voicebox REST API directly
(`POST /generate` → poll `/generate/{id}/status` → `GET /audio/{id}`).
Requires a running server and a voice profile id. Engines: `qwen`,
`qwen_custom_voice`, `luxtts`, `chatterbox`, `chatterbox_turbo`, `tada`,
`kokoro`.

## Voice direction (FoodCode)

Calm, clinical, confident science narrator — not a hype man. Second person
"you". Short declarative sentences, fragments for emphasis, repetition as a
device ("100 times. 100 times."). Specific numbers, named compounds, named
journals. Never slang, never jokes.

## Self-check before the audio leaves this skill

- [ ] `check` reports 0 issues (all beats 12–16 words, all have a visual)
- [ ] Every beat's measured duration is inside 2.0–6.0 s
- [ ] Median beat duration is ≈ 3.6 s
- [ ] `beat_marks.json` exists and total duration matches the target length
- [ ] No beat shares an image with another beat
