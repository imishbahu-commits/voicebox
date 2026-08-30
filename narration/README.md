# Beat narration (FoodCode / Paint Explainer style)

Voicebox generates the voice. `beat_narrator.py` makes the script **cuttable**:
it forces every narration beat into the measured FoodCode window, synthesises
one audio file per beat, and derives the cut list from the audio that actually
came out — not from an estimate.

## The two hard rules

| Rule | Value | Why |
|---|---|---|
| Words per beat | **12–16** | The FoodCode cadence. Under 12 the cut stutters; over 16 the beat needs its own image anyway. |
| Seconds per beat | **2.0–6.0**, median **3.6** | Measured cut interval from the Paint Explainer reference video. |

Derived rule: **1 beat = 1 image = 1 audio file = 1 cut.** A long sentence
becomes two beats, each with its own visual. Never stretch a beat to save an
image.

## Install

No dependencies — standard library only.

```bash
python3 narration/beat_narrator.py --help
```

Optional, for accurate audio measurement: `ffprobe` or `ffmpeg` on `PATH`
(a stdlib MP3/WAV reader is used as a fallback).

## Pipeline

```bash
# 1. split raw narration into 12-16 word beats  -> beats.json
python3 narration/beat_narrator.py split script.txt -o projects/myvid

# 2. fill in the visual for each beat, then validate
python3 narration/beat_narrator.py check projects/myvid/beats.json --rows

# 3. synthesise one audio file per beat
python3 narration/beat_narrator.py synth projects/myvid/beats.json --backend arena
python3 narration/beat_narrator.py synth projects/myvid/beats.json \
    --backend voicebox --profile <profile-id> --base http://127.0.0.1:17493

# 3b. retime any beat that fell outside 2-6 s (pitch preserved)
python3 narration/beat_narrator.py fit projects/myvid/beats.json --dry-run
python3 narration/beat_narrator.py fit projects/myvid/beats.json --target-wps 2.7

# 4. measure the real audio and emit the cut list
python3 narration/beat_narrator.py marks projects/myvid/beats.json

# 4b. optimise the generated PNGs before they pile up (~55% smaller)
.tools/venv/bin/python narration/optimize_images.py projects/myvid/images

# 5. cut the beats into a real video
python3 narration/render_video.py projects/myvid --part 1
```

`beats.txt` in the `NN|narration` form (used by the foodcode projects) is read
directly by `split`.

## Pace: the one real tension

12–16 words inside a 2–6 s beat implies a delivery rate of **2.7–6.0 words/sec**.
Most natural TTS reads land at ~2.3 wps, so a 14-word beat arrives at ~6 s and
needs retiming. `fit` does this with ffmpeg's `atempo`, which changes tempo
without touching pitch — the same move an editor makes when a read runs long.

| `--target-wps` | 12 w | 14 w | 16 w | typical stretch |
|---|---|---|---|---|
| **2.7** (default-friendly) | 4.4 s | 5.2 s | 5.9 s | ~1.2× |
| 3.89 (reference median) | 3.1 s | 3.6 s | 4.1 s | ~1.7× |
| **3.6** (tomato/8-min) | 3.3 s | 3.9 s | 4.4 s | ~1.55× |

2.7 is the slowest rate that still keeps a 16-word beat under 6 s, so it is the
gentlest option. Use 3.89 when you want the measured 3.6 s median cadence and
accept a faster, more urgent read. `fit --dry-run` shows the change before any
audio is touched, and the untouched read is always kept in `audio/original/`.

## Output artefacts

| File | Purpose |
|---|---|
| `beats.json` | the script: narration + visual + label + transition per beat |
| `audio/beatNN.mp3` | one TTS clip per beat |
| `audio/tts_manifest.json` | per-beat texts for the `arena` backend |
| `beat_marks.json` | **the cut list**: start/end/duration/frames + visual per mark |
| `beat_marks.csv` | same rows, spreadsheet friendly |
| `beat_marks.edl` | CMX3600 EDL for Premiere / Resolve / Final Cut |

| `video/partNN.mp4` | rendered cut (gitignored — regenerate, don't commit) |
| `video/partNN_contact.jpg` | 10-up contact sheet of that part |

`beat_marks.json` is the source of truth for the edit — every mark carries its
`visual`, so the picture is cut to the narration rather than guessed.

## Render

`render_video.py` turns finished beats into an MP4. One beat = one image +
one voice clip = one cut, and the cut points are read from `beat_marks.json`,
so picture and voice cannot drift.

```bash
python3 narration/render_video.py projects/myvid --part 1     # one part
python3 narration/render_video.py projects/myvid --beats 1-20 # explicit range
python3 narration/render_video.py projects/myvid --motion hold # no camera move
```

What it does per beat:

1. Pillow fits the generated image onto a 1920x1080 canvas — never squashed,
   matted in a pale cream that matches the doodle white (`--pad` to change).
2. ffmpeg holds it, pushes in, or pulls out, following the measured FoodCode
   mix (60% still / 40% slow move, `--motion` to override). Pitch and tempo of
   the voice are untouched.
3. The beat's own audio is muxed into that segment, so sync is structural.
4. Segments are joined with `-c copy` — no re-encode, no accumulated drift.

Needs Pillow and ffmpeg. Use the repo's own tool venv, which survives
environment resets: `.tools/venv/bin/python narration/render_video.py ...`
(the script re-execs into it automatically if Pillow is missing).

Beats without audio or an image are skipped and reported, so you can render a
part the moment those 10 beats are done instead of waiting for all 145.

## TTS backends

**`arena`** (default) — writes `audio/tts_manifest.json` plus `audio/beatNN.txt`
per beat for the agent's `generate_speech` tool. Use when Voicebox's local
engines are not installed (they need several GB of weights and ideally a GPU).
Cap is **10 clips per turn**; resume by re-running with `--limit N`.

**`voicebox`** — drives the Voicebox REST API directly:
`POST /generate` → poll `/generate/{id}/status` → `GET /audio/{id}`.
Needs a running server (`bun run dev:server`, default port 17493) and a voice
profile id. Engines: `qwen`, `qwen_custom_voice`, `luxtts`, `chatterbox`,
`chatterbox_turbo`, `tada`, `kokoro`.

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

- `narration` — the spoken line, 12–16 words.
- `scene` — what is **on screen**, never an emotion. Write "a bromelain enzyme
  shape cutting into a tongue", never "epic reveal". Forbidden: cinematic,
  moody, painterly, film grain, dark palettes, shadows, gradients, photorealism.
- `label` — short on-screen caption, caps.
- `transition` — `cut` | `revealing` | `disappearing` | `switching`.

## Voice direction (FoodCode)

Calm, clinical, confident science narrator — not a hype man. Second person
"you". Short declarative sentences. Fragments for emphasis. Repetition as a
device ("100 times. 100 times."). Specific numbers, named compounds, named
journals, years. No slang, no jokes.

## Worked example

`projects/foodcode-pineapple/` — 60 beats, 60/60 inside 12–16 words, median
3.34 s, every beat carrying its own visual.

```bash
python3 narration/beat_narrator.py check projects/foodcode-pineapple/beats.json
# beats            60
# words            total 782  min 12  max 16  mean 13.0
# in 12-16 words    60/60
# OK — every beat is 12-16 words, 2-6 s, and has a visual.
```
