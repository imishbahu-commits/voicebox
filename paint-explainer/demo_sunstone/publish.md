# Sunstone demo — publish sheet

Rendered by `paint-explainer/kelevins_render.py` from 5 recorded narration clips
(`audio/n01.wav` … `n05.wav`, one line of speech per beat) and 5 flat-vector key-art
frames (`art/*.png`).

| Measured | Value |
| --- | --- |
| Output | `paint-explainer/demo_sunstone/sunstone.mp4` |
| Container | H.264 High + AAC mono, 1280×720, 30 fps |
| Duration | 1:07.53 (2,026 frames, audio-driven timeline) |
| Size | 5.4 MB |
| Loudness | mean −16.4 dB, max −0.2 dB |
| Encode time | ~54 s wall clock on 2 vCPU (≈1.2× realtime) |
| Chapters | `sunstone.edl.json` (written from measured clip durations) |

This is **one entry**, not an episode — his uploads run 6–9 entries of ~100–115 s each
(verified: 9 entries, ~2,900 words, in `Historical Myths That Turned Out To Be Real`).
Use it to judge the look, caption cadence and VO before a full script gets rendered.

## Title (his grammar: the scope is the clickbait — no numbers, no emoji, no colon)

`Historical Myths That Turned Out To Be Real — Viking Sunstone (demo cut)`

## Description (his 3-lines + timestamps format)

```
A myth about Vikings finding the sun through fog with one crystal, and the receipts that made it real.
Let me know down below if you've got any other myths you want checked!
Timestamps as always for you guys, Love you all!

0:00 The myth
0:13 The receipts
0:29 The date
0:44 How it works
1:00 The punchline
```

## Narration as recorded (verbatim — `voice-00`, for re-voicing in a human voice)

**01 · THE MYTH** — A Viking sunstone. That is the textbook example of a myth. One
crystal, and a ship finds the sun through three days of fog. Obviously nonsense.

**02 · THE RECEIPTS** — Except there was a real one. Henry the Eighth lost a warship,
the Mary Rose, in 1545. It was found in 1971, and inside the wreck, archaeologists
catalogued a cloudy green crystal, sitting next to navigation dividers and a lead line.

**03 · THE DATE** — That is a sunstone, or the closest thing to one anyone has ever
held. So the legend is not a legend, it is an inventory list. The instrument that let
ships leave the coastline was real, and it was as boring as a ruler.

**04 · HOW IT WORKS** — The myth was that it was magic. The reality is that it was
polarisation. The crystal splits the light into two images. You line the two images up,
and the sun tells you where it is, even when the sun is gone.

**05 · THE PUNCHLINE** — Boats have crossed oceans with a ruler and a clear opinion
ever since. Sick.

## What was already fixed in this pass

Two claims in the first recording were wrong and were re-voiced, not patched over:

1. the wreck is in the **Solent off Portsmouth**, not "off the coast of France";
2. the sunstone-vs-Columbus comparison was inverted — 1492 to 1545 is **half** a
   century, not "a century and a half", so the line was replaced with shipboard
   inventory instead of a bad date comparison.

## Check before upload (a myth-busting video dies on its dates)

- The **crystal + elongated "sunstone" reported from the Mary Rose** and exactly what it
  was catalogued beside — the "dividers and lead line" pairing is the load-bearing
  detail. Use the Mary Rose Trust archive / the excavation report, not a news roundup.
- The **polarisation-navigation lab tests** (the ~1° accuracy figure): confirm group,
  year (reported 2011) and the precise claim before citing them on screen.
- The **Icelandic sólarsteinn** literary reference if it stays in the description
  (which saga, which date).
- Frames in `qc_*.png` are the QC method: extract `ffmpeg -ss <t> -frames:v 1` and read
  the stills, plus `volumedetect`. The audio stream is checked numerically; nobody here
  can watch the picture and the edit together, so skim the MP4 once yourself.

## Re-render

```bash
python3 paint-explainer/kelevins_render.py \
  --beats paint-explainer/demo_sunstone/beats.json \
  --audio-dir paint-explainer/demo_sunstone/audio \
  --art-dir paint-explainer/demo_sunstone/art \
  --out paint-explainer/demo_sunstone/sunstone.mp4
```

Needs `imageio-ffmpeg`, `Pillow`, `numpy` (all pip-installable; the wheel ships a static
ffmpeg since `ffmpeg` is absent from this image). Caption chunk size: `--min-words` /
`--max-words` (5 / 7 default). Pacing levers: more beats per entry, 2–3 shots per beat,
longer pauses via `pre_gap` / `post_gap` in the script.
