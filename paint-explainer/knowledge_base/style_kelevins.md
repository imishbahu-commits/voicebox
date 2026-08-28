# Kelevins — style breakdown (evidence-based)

Target: `youtube.com/@kelevins` → channel **“Kelevin / Kelevins”**, Canada, joined **Nov 2023**, ~**265k subs**
(count read off a transcript mirror on 2026-08-28), long-form history/curiosity list essays.

**Honesty box.** Nothing here is frame analysis. This sandbox cannot play YouTube: `youtube.com` / `i.ytimg.com` /
`googleapis.com` all fail from `curl` (HTTP 000), the watch page 401s `fetch_page`, RSS 404s, Invidious hosts are
down/blocked, and `image_search` for his thumbnails returns only Canva/PosterMyWall lookalikes (one result tagged as
his, `GSgKNx44Hes`, is actually an *InternetCity* video). What is **verified** below comes from two readable sources:
his video pages/descriptions/chapter lists (search-indexed mirrors) and, since this pass, the **full English
transcript** of one video. Voice timbre, grade, music and shot motion stay **⚠️ inferred** — they are *style choices*
in my renderer, not measured replicas.

## Evidence

| # | Observation | Source | Status |
| --- | --- | --- | --- |
| 1 | `The Craziest Cults From Every Time Period` — description: “These are the craziest cults from every time period in history. / Let me know down below if you’ve got any other crazy cults which you want to know about! / Timestamps as always for you guys, Love you all!” | his video page (`Bf35BeERBjs`), 2025-12-14 | ✅ verbatim |
| 2 | Chapters: `00:00 The Thuggee · 02:34 Nizari Ismailis · 04:34 Anabaptists · 07:26 Heavenly Kingdom · 10:35 KKK · 13:17 Movement Of Restoration` → 6 entries, 15:30–16:00 | same video | ✅ verbatim + arithmetic |
| 3 | `The Worst Punishment From Every Time Period` (`6BjnqataM_I`) — description is **only** the sponsor code line | his video page | ✅ verbatim |
| 4 | **Full transcript** of `Historical Myths That Turned Out To Be Real` (`tJLOLp_6klg`, 2026-08-25): ~2,900 words, **9 entries**, no published chapters | `youtubetotranscript.com/transcript?v=<id>` | ✅ verbatim (not stored in git — see Rights) |
| 5 | Runtime of the myths video, per-entry seconds | — | ⚠️ unknown; duration never returned by any reachable endpoint |
| 6 | VO timbre, delivery speed, joke density, music, SFX, colour grade, motion, thumbnail layout | — | ⚠️ **not observed** |

## The entry machine — VERIFIED from the transcript

Every one of the 9 entries runs the same 6-beat loop (~320 words, ≈100–115 s of speech):

1. **The myth**, stated the way believers state it, in 1–2 sentences. (`“A sword in a stone. … You pull it out, you rule.”`)
2. **Dismissal beat, phrased as a question:** “Obviously fake, right?” / “Obviously nonsense.”
3. **The turn:** “Well, Italy has a real one.” / “Except in 2011, archaeologists…”
4. **Receipts.** Named place, named year, a number: `1180 and 1185`, `2001`, `132 AD`, `1545`, `33 days`, `4,000 km`,
   `about 170`. He never says “studies show”.
5. **The deflation.** One clause that makes the miracle mundane: “It wasn’t glamorous. It was basically just the
   parking lot.” / “and it was as boring as a ruler.”
6. **One flat punchline, then hard cut:** “Sick.” / “Course it is.” / “Zero skeletons. Clean getaway.” / “RIP, bro.”

Recurring devices, all present in that single transcript (so they are structure, not luck):

- **Lie-then-retract**: “An earthquake had just hit the capital. I’m lying, nothing hit the capital.”
- **Audible self-correction kept in the cut**: “Was Pompeii before that? No, I think it was after. Actually, I think
  Pompeii was later on.”
- **Flatter-then-insult**: “As my more intelligent viewers have already realized, that is not possible.”
- **Rigged quiz**: “wild guess which state has the most sunken ships? That’s right, Colorado. Yeah, it’s obviously Florida.”
- **Look-at-this prompting** (proves he cuts to an object, not to b-roll scenery): “Look at this thing.” / “Can you see it?”
- **One mid-roll subscribe bait tied to the content, none at the top**: “You’ll have a better chance of pulling it out
  if you subscribe. Just saying.”
- **Running gag, used ~2× per video**: “Seems to be a recurring theme on this channel.”
- **Sign-off is one line**: “Anyway, if you like this video, you’ll like this one even more. Subscribe.”

**Corollary for listicles:** entry count scales with subformat — 9 myth/reality pairs in ~2,900 words vs 6 eras in a
15:30 runtime. Cold open inside entry 1, no intro, no summary section, in both.

## Grammar that stays (format rules)

1. **No intro, no title card.** Chapter 1 is entry 1 at `00:00`; the hook is a concrete detail, not a promise.
2. **Chapter title = the entry’s proper noun**, 1–3 words, Capitalised (`The Thuggee`, `KKK`) — a name, not a summary.
3. **Title grammar:** `The <superlative> <plural> From Every Time Period` / `<X> in Human History` /
   `How you would <verb> on every <noun>`. Title Case, **no numbers, no ALL-CAPS, no emoji, no colon**; 33–45 chars.
   The clickbait is the *scope*, not an exclamation.
4. **One joke per fact, never two.** State the horror flatly, add one deadpan clause, move on. No meme inserts.
5. **Second person, present tense, physical**, short declaratives, ~155 wpm (⚠️ derived from the beat budget, not measured).
6. **Description = 3 lines + timestamps**, sometimes sponsor code only (evidence #3).
7. **One sponsor read, after the middle entries**, one joke maximum, then back in. Never before entry 1.
8. **The last entry drops the comedy** and says the real thing in 2–3 sentences, then a soft CTA. That pivot is what
   makes the earlier jokes read as wit instead of sneering.

## Sound / picture (⚠️ inferred, chosen — not copied)

Deadpan monotone, no shouty promo VO, no laugh track. Single low drone (55 / 82.4 / 110 Hz stack) + filtered
brown-noise swell under everything, music ducked to 0.55 while he talks, one soft wood tick per cut, no risers
inside entries. Colour: navy `#0f1726` fields + gold `#e8be60` for the one word that matters + bone `#f5f6f8` text.
Thumbnails: one hero object, dead-centred, flat field, ≤4 words, one word in gold, one red arrow at the flaw
(mockups in `thumb_a_kelevins_style.png` / `thumb_b_kelevins_style.png` — a starting point, not a match).

## Rendering — built, run, measured

Two tools, both in this repo:

| Tool | Role |
| --- | --- |
| `kelevins_build.py` | beat list → script JSON + Markdown + chapter list + description at 155 wpm |
| `../kelevins_render.py` | `beats.json` + recorded narration + key art → encoded MP4 (audio drives the timeline) |

```bash
python3 paint-explainer/kelevins_render.py \
  --beats tmp/vid/beats.json --audio-dir tmp/vid/audio --art-dir tmp/vid \
  --out tmp/vid/sunstone.mp4
```

Each beat = `{"narration": "...", "art": "art_1_longship.png", "title": "01 · THE MYTH"}` plus `n01.wav`, `n02.wav`…
(VOICEBOX-01-style: one line of speech per beat, TTS-able verbatim). Caption chunk timings come from the *measured*
duration of each wav, so the edit can never drift from the VO.

Measured on the first run — Sunstone segment, 5 beats, 24 kHz mono VO, 1376×768 art:

| Check | Result |
| --- | --- |
| Container | `1280x720` H.264 High + AAC mono, 30 fps, **1:04**, 5.2 MB |
| Encode wall clock | 51 s (≈1.2× realtime on 2 vCPU) |
| Loudness | mean **-16.5 dB**, max **-0.5 dB** (hot, no clipping) |
| Motion | zoom 1.045 → 1.22, smoothstep, drift direction alternates per beat |
| Captions | 5–7 word UPPERCASE chunks; previous line kept dimmed above the current one |
| Overlays | `NN / NN` chapter chip + beat title top-left, gold progress bar bottom |
| ffmpeg | `imageio-ffmpeg` wheel (static, libx264 + aac) — `ffmpeg` is absent from the base image |

v1 gaps, stated plainly: one artwork per beat is fewer cuts than a human editor would use; the bottom gradient is
heavier than his; caption timing is chunk-level, not word-level (no forced aligner installed here); the music is a
synthesised stand-in because there is no licensed bed in this repo. Fidelity ladder, cheapest first: 2–3 shots per
beat → real record-collection bed → word-level timing via forced alignment → record VO in a real voice instead of TTS.

## Rights (read before publishing)

- Transcript text is evidence for **structure only**. It is deliberately **not committed** here, and no line of his
  writing is reused in any script or caption — `kelevins_build.py` / `kelevins_render.py` carry zero transcript text.
- Facts are cited from primary sources (`Mary Rose`, sunk **1545**, Icelandic sources, 2011 Rennes polarisation
  test) and must be checked by a human before upload; a myth-busting video lives or dies on its dates.
- Music/SFX here are synthesised, so they are clear to use. **Do not** sample his audio or drop in copyrighted
  movie/game footage, which is what this style is usually built from.
- Thumbnails were generated, not fetched, because his real ones were unreachable from this sandbox.

## Build it again (checklist)

1. Pick a title from the grammar rules; write **6–9 entries**, one per claim you have receipts for.
2. Per entry, produce exactly six beats in the order above. Target ~320 words / ~110 s.
3. For each beat: write one narration line → generate the VO file → generate one key-art frame in the palette.
4. `kelevins_render.py` → QC by extracting frames (`ffmpeg -ss <t> -frames:v 1`) and `volumedetect`. I can read the
   stills, not the video, so still-frame + loudness checks are the loop.
5. End on the one-line subscribe. Do not explain the joke twice.
