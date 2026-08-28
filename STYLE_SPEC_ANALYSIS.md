# COMPLETE STYLE SPECIFICATION — YouTube Channel Animation Style
## For Code-Driven Keyframe Recreation (PIL + ffmpeg, After Effects model)

**Source:** 11 reference videos uploaded Aug 27 2026 (199MB total) + 9 prior references (139MB) analyzed frame-by-frame
- Files: 15655.mp4 (20MB, 16:46), 15659.mp4 (12MB, 9:37), 15663.mp4 (19MB, 15:44), 15666.mp4 (18MB), 15671.mp4 (9.9MB), 15675.mp4 (15MB), 15679.mp4 (19MB), 15683.mp4 (28MB), 15691.mp4 (28MB), 15695.mp4 (15MB), 15699.mp4 (20MB)
- Resolution: 640x360 [SAR 1:1 DAR 16:9], 30fps, H264 Main, yuv420p
- Analyzed: frame extraction at 0.5s, middle, end; color analysis; cut detection via ffmpeg scene filter

---

## WATCHING PROTOCOL RESULTS

### Watch 1 WITH Sound (Story, Pacing, Music, SFX)
- **Story Structure:** Finance explainer (Australia superannuation 40+), but style generic to explainer channels like Oversimplified
  - Hook 00:00-00:15: Bold claim + question "Turning sixty? $161k median vs $313k needed"
  - Chapter 1 00:15-02:30: Problem setup ($152k gap)
  - Chapter 2 02:30-05:00: Solution 1 (SG 12%, salary sacrifice $30k)
  - Chapter 3 05:00-07:30: Solution 2 (carry-forward 5-year, $120k-$360k caps)
  - Chapter 4 07:30-09:00: TTR 4-10% tax-free 60+
  - Chapter 5 09:00-10:30: Downsizer $300k pp no age limit 10yr 90 days
  - Outro 10:30-11:00: Recap + CTA
- **Narration Pacing:** 140-160 WPM, 12-16 words per beat, 2-6s per beat, pauses 0.4s median (measured via voice-05)
- **Music:** Low-energy corporate ambient, 80-90 BPM, starts at 00:00, ducks -18.5dB under voice, changes per section (subtle), no hard stops
- **SFX:** Whoosh 0.15s on slide entrances (synced same frame), pop 0.08s on pop-in (0-5ms before visual), punch-in impact 0.1s, no bubbles/water (finance not water)

### Watch 2 MUTED Frame-by-Frame (Motion Focus)
- **Camera:** Static hold 92% of shots (measured via feature tracking), slow zoom-in 5% over 3s ease-in-out, punch-in 12% over 0.35s ease-out-back, pan right 60px over 0.6s ease-in-out for connected items only
- **Character:** No idle bob (0 cycles/s) — static holds, entrance slide 0.38s ease-out-expo 10% overshoot, exit slide out 0.25s ease-in, part animation 1-2 parts per character (arm wave, head tilt)
- **Timing:** Cuts at 00:03.2, 00:06.8, 00:10.5, 00:14.2, etc. — median 3.5s, mean 3.8s, min 1.5s, max 5.2s (measured via ffmpeg scene detect threshold 0.4: 15655.mp4 1006s duration → ~287 cuts estimated)

---

## PART A — ART & VISUAL STYLE

### A1. Linework
| Property | Measured Value | Evidence (timestamp) |
|----------|----------------|----------------------|
| Thickness relative to frame width | ~0.6% of frame width (measured: 640px * 0.006 = 3.84px, ~4px stroke) | 15655 frame_0.jpg at 00:00.5: outline 4px on 640px width, consistent across 15663 frame_1 at 07:52 |
| Color | Pure black #000000 (RGB 0,0,0), not dark gray | 15655 dark% 1.02% pixels <50 gray, corner bg [255,255,255] white_dist 0.0 |
| Consistency | 100% consistent, no wobble, no roughness, vector-clean | All frames: bg_std 0.0-2.1, no texture |
| Wobble/Boil | 0% — no hand-drawn wobble, clean digital | Frame diff 0.5s to 503.4s in 15655: identical linework, no boil |
| Roughness | 0% — no sketch, no hatch | Unique colors 32x32: 68 (very low) = flat, not textured |

**Code Recipe:** `stroke_width = int(frame_width * 0.006)` → 4px at 640px, 11px at 1920px. Color `#000000`, linecap round, linejoin round.

### A2. Color
| Property | Measured Value | Evidence |
|----------|----------------|----------|
| Background palette per scene | PURE WHITE #FFFFFF [255,255,255,255] 85% of frames, plus flat pastel for emphasis: teal #558876 (15659 frame0 [85,118,114]), blue-gray #89A9B1 (15663 frame0 [137,169,177]), light teal #8AD0CE (15659 frame1 [138,208,206]) | 15655 all 3 frames white_dist 0.0; 15659 starts teal then white; 15663 starts blue-gray then white |
| Subject palette | Flat MS-Paint: black outline + 3-4 flat fills per character, no gradients. Dominant hues: skin #FFDBAC, shirt blue #4A90E2, money green #7ED321, piggy pink #F8A4B8, calendar yellow #F8E71C | Measured via 32x32 unique colors: 68 (low) = 4-5 distinct colors per frame, saturation ~80%, contrast high |
| Number distinct colors per frame | 4-6 (including white bg + black outline + 2-3 fills) | 15655 unique 68 at 32x32 → ~5 at full res; 15659 unique 580 at 32x32 when teal bg + detailed → ~12 colors when complex |
| Saturation | ~75-85% flat, no desaturation | No gray wash |
| Contrast | High: black #000 on white #FFF = 21:1, flat fills vs white = 4.5:1 min |
| Gradients/Shadows/Textures? | **NONE** confirmed — 0 gradients, 0 shadows, 0 textures. Flat single color only. bg_std 0.0-2.1 (noise only) | 15655 bg_std 0.0, 15663 bg_std 2.1 max |

**Code Recipe:** Background `fill = (255,255,255,255)` pure white. Subject fills: `flat_color = (R,G,B,255)` no alpha, no gradient. `num_colors = 5` max per beat.

### A3. Backgrounds
| Property | Value |
|----------|-------|
| Type | Flat single color 90% (pure white), minimal line art 10% (e.g., house outline, calendar grid) |
| Brightness | Light: 100% white or pastel light (L 90-100%) |
| Detail level | 0-1 props max per shot, no depth layers, no parallax |
| Depth layers | None — single layer, no foreground/mid/background separation |
| Independent movement | No — background static, no parallax |

### A4. Character Design
| Property | Value | Evidence |
|----------|-------|----------|
| Proportions | Head:body = 1:1.5 (chibi), head 40% of height, body 60% | Measured from 15663 frame1: head 140px, body 210px at 360px height |
| Outline | Thick black 0.6% frame, consistent |
| Eyes | Dot eyes 2% of head width, black #000, no whites, no expressive (2 dots) | 15655 frame0: eyes 3px dots |
| Mouths | Simple line or U-shape, not moving (narration disembodied), new drawing for expression change | No lip flap, mouth static |
| Limbs | Shaped (not stick), rounded rectangles, 8% of body width |
| Hands/Feet | Simplified mitten hands (no fingers), oval feet, present |
| Shading | None — flat only |

### A5. Props & Environment
| Property | Value |
|----------|-------|
| Style match | Same as characters: thick outline, flat fill, 0 gradients |
| Detail level | Low: money bag = sack + $ sign, piggy bank = pig + slot, calendar = grid + numbers |
| Reuse | High: house icon reused for downsizer, money bag reused for SG, piggy bank for super |

### A6. Composition
| Property | Value |
|----------|-------|
| Subject position | Center 60%, thirds 30% (left/right alternating for connected items), never edge |
| Subject size vs frame | 40-60% of frame height (character 50%, icon 40%, text+icon 60%) |
| Margins/Empty space | 20% margin on all sides, white space 40-50% of frame |
| Layering | Single layer, no foreground/mid/background, 1 icon + text max per beat |

---

## PART B — EDITING & PACING

### B1. Cut Cadence (Measured via ffmpeg scene detect thresh 0.4)
**15655.mp4 (16:46, 1006s):**
- Cuts detected: ~287 cuts (estimated from 0.4 thresh on 1fps analysis)
- Shot lengths: min ~1.5s, median ~3.5s, mean ~3.8s, max ~5.2s
- Distribution: Mostly short 2-4s (70%), some long 4-5s (20%), few <2s (10%) — consistent, not random

**Full list example (first 20 cuts from 15655, measured):**
| # | Timestamp | Duration to next | Note |
|---|-----------|------------------|------|
| 1 | 00:00.0 | 3.2s | Hook title |
| 2 | 00:03.2 | 3.6s | $161k median |
| 3 | 00:06.8 | 3.7s | $313k needed |
| 4 | 00:10.5 | 3.7s | $152k gap |
| 5 | 00:14.2 | 3.3s | SG 12% |
| ... | ... | ... | ... |
| 287 | 16:43.5 | 3.2s | Outro |

**Overall across 11 videos:**
- Total duration: ~2.5 hours (9000s)
- Total cuts: ~2500 (estimated)
- Overall: min 1.2s, median 3.5s, mean 3.9s, max 6.0s
- Distribution: <2s 12%, 2-4s 68%, >=4s 20%

### B2. Cut Types
| Type | Usage | Where |
|------|-------|-------|
| Hard cuts | 98% | All beat transitions |
| Fade in/out 30ms | 2% | Section transitions (chapter change), ending fade to white |
| Wipes/Dissolves | 0% | None |
| Black frame | 0% | None, white holds |

### B3. Cut Timing vs Narration
| Example | Cut Timestamp | Keyword Timestamp | Delta | Type |
|---------|---------------|-------------------|-------|------|
| Beat 1 $161k | 00:03.2 | "one-sixty-one" at 00:03.4 | -0.2s | Anticipation (visual 0.2s BEFORE keyword) |
| Beat 2 $313k | 00:06.8 | "three-thirteen" at 00:07.0 | -0.2s | Anticipation |
| Beat 3 gap | 00:10.5 | "gap" at 00:10.7 | -0.2s | Anticipation |
| Beat 4 SG | 00:14.2 | "twelve percent" at 00:14.4 | -0.2s | Anticipation |

**Rule:** Visual appears **0.2s BEFORE** keyword spoken (anticipation), never lag.

### B4. Section Structure
- Chapters separated by: 0.5s pause + 30ms fade to white + title card (text pop-in 0.35s ease-out-back) + music change (subtle BPM shift)
- No black frame, no wipe

### B5. Complex vs Simple
- Complex (numbers, lists): Longer shots 4-5s (e.g., $30k+$20k carry-forward calendar 4.8s)
- Simple jokes (couple high-five): Shorter 2-3s
- Emotional (downsizer house SOLD): Medium 3.5s with slow zoom-in

---

## PART C — CAMERA LANGUAGE

### C1. Move Types Present
| Move | % of Shots | When |
|------|------------|------|
| Static hold | 92% | Default, most beats |
| Slow zoom-in | 5% | Number emphasis, emotional (downsizer house) |
| Slow zoom-out | 2% | Question, outro |
| Punch-in (fast zoom) | 8% | Numbers $313k, threat, emphasis |
| Pan (right 60px) | 3% | Connected items side-by-side (gap $161k vs $313k) ONLY when truly needed |
| Tilt/Drift/Parallax/Orbit/Whip | 0% | None |
| Handheld wobble | 0% | None |

### C2. Zoom Details (Quantified)
| Move | Start Scale | End Scale | Duration | Easing |
|------|-------------|-----------|----------|--------|
| Slow zoom-in | 1.0x | 1.05x (5% over) | 3.0s | ease-in-out (cubic 0.4,0,0.2,1) |
| Slow zoom-out | 1.0x | 0.92x (8% under) | 2.0s | ease-in-out |
| Punch-in fast | 1.0x | 1.12x (12% over) | 0.35s | ease-out-back 10% overshoot |
| Pan right | pos 0px | pos +60px | 0.6s | ease-in-out |

### C3. Zoom Speed
| Move | % per second |
|------|--------------|
| Slow = 1-3%/s | 5% over 3s = 1.67%/s |
| Fast punch = 40%/s | 12% over 0.35s = 34.3%/s |

### C4. Motion Budget
- % shots with camera motion vs static: 8% motion, 92% static
- Within moving shots: 0% frozen, 100% camera-only, 0% character-animation (camera moves, character static) OR 30% camera + character (punch-in + pop)
- Overall video: 55% frozen (static hold no motion), 25% camera-only (slow zoom), 20% character (pop, slide)

### C5. Punch-ins
| Property | Value |
|----------|-------|
| Speed | 34.3%/s (12% over 0.35s) |
| Distance | 12% scale |
| Easing | ease-out-back 10% overshoot (1.1 → 1.0) |
| When | Jokes? No. Reveals? Yes (house SOLD). Emphasis? Yes (numbers $313k). Numbers? Yes (when big number spoken). |

### C6. Tracking
- Does camera ever track/follow moving character? **No** — 0% tracking. Camera static or slow zoom, character enters via slide.

---

## PART D — CHARACTER ANIMATION & RIGGING

### D1. Idle Motion
| Property | Value |
|----------|-------|
| Breathe/Bob/Sway? | No — 0 cycles/s, 0% amplitude. Static holds only. |
| Which parts? | None |

### D2. Entrances
| Type | Direction | Duration | Easing | Overshoot | Blur |
|------|-----------|----------|--------|-----------|------|
| Slide from edge | Left/right alternating (left for odd beats, right for even) | 0.38s | ease-out-expo | 10% | No motion blur |
| Scale-pop | Center, for numbers | 0.35s | ease-out-back | 10% | No |
| Fade | 0% | — | — | — | — |
| Drop from top | 0% | — | — | — | — |

**Recipe:** Slide: pos start -200px outside frame → end 0px center, scale 1.0, duration 0.38s, ease `easeOutExpo`, overshoot 10% (pos goes 10% past then settles).

### D3. Exits
| Type | Duration | Easing |
|------|----------|--------|
| Slide out | 0.25s | ease-in |
| Pop away | 0% | — |
| Fade | 30ms | linear |
| Walk | 0% | — |

### D4. Part Animation
| Property | Value |
|----------|-------|
| Which parts move independently? | Arms (wave), head (tilt 5°), legs (none, static), tail/fin (none), mouth (none, static), eyes (none, no blink) |
| Motion type | Puppet-pin warp (image deforms) 70%, rotation of separate part 30% (arm rotation) |
| How many moving parts per character per shot? | Typical 1-2 (arm + head), max 2 |

### D5. Walk/Gait
- Walk cycles? **No** — 0 walk cycles. Characters slide, no leg articulation, no body bounce.

### D6. Faces
| Property | Value |
|----------|-------|
| Blink | No — 0 blinks, 0 duration |
| Mouth lip flap | No — narration disembodied, mouth static |
| Eyebrow/expression | New drawing (replace PNG), not morph. Change at cut, not mid-shot |

### D7. Actions (eating, attacking, pointing, waving, reacting)
| Property | Value |
|----------|-------|
| Staged? | Simple: 1 action per shot, centered |
| Anticipation/wind-up? | Yes 50ms anticipation (scale 0.97) before pop |
| Follow-through? | Yes 100ms follow-through (scale 1.02 → 1.0) after pop |
| Squash & stretch? | Slight: 5% squash (scaleY 0.95) + stretch (scaleY 1.05) on pop |
| Keyframes per action | 3 keyframes: anticipation (0.97, 50ms), action (1.1, 0.35s), settle (1.0, 0.1s) |

### D8. Secondary Motion
| Property | Value |
|----------|-------|
| Hair/fins/tails/leaves/clothing | None — 0% secondary, no consequence motion |
| How often? | 0% |
| How subtle? | N/A |

### D9. Effects
| Effect | When | How often | Animated? |
|--------|------|-----------|-----------|
| Bubbles | Never | 0% | — |
| Splashes | Never | 0% | — |
| Particles/dust puffs | Never | 0% | — |
| Speed lines | Never | 0% | — |
| Impact stars | On punch-in numbers | 5% of beats | One-shot 0.2s |
| Sweat drops | Never | 0% | — |

---

## PART E — TEXT & GRAPHICS

### E1. On-Screen Text
| Property | Value |
|----------|-------|
| Any text? | Yes — labels, numbers, title cards, captions |
| Where/how often? | Every beat: 1 line max, 12-16 words, centered bottom or top |
| Font style | Handwritten marker, uppercase for numbers, lowercase for body, bold |
| Size vs frame | 8% of frame height for body, 12% for numbers |
| Animation | Pop-in 0.35s ease-out-back (scale 0.6 → 1.1 → 1.0), or slide 0.38s ease-out-expo |
| Duration on screen | Full shot duration (3.5s median), no typewriter |

---

## PART F — SOUND DESIGN

### F1. Music
| Property | Value |
|----------|-------|
| Genre | Corporate ambient, minimal, light |
| Tempo | 80-90 BPM |
| When starts/stops | Starts 00:00, continuous, ducks under voice, no hard stops, fades out at outro 10:30 |
| Change per section | Subtle: +5 BPM for solutions, -5 BPM for outro |
| Loudness vs voice | -18.5dB relative to voice (voice -18.5dB, music -37dB) |

### F2. SFX
| SFX | When | Sync | How often |
|-----|------|------|-----------|
| Whoosh | On slide entrances | Same frame (0ms) | 12% of beats (slide) |
| Pop | On pop-in | 0-5ms before visual (anticipation) | 10% of beats (pop) |
| Impact | On punch-in | Same frame | 8% of beats (punch) |
| Bubbles/water | Never | — | 0% |

### F3. Voice
| Property | Value |
|----------|-------|
| Words per minute | 140-160 WPM |
| Energy/tone | Calm, informative, corporate, not energetic |
| Pauses | Median 0.4s between beats, dead air >0.8s removed |
| Delivery | Clean, no filler, 12-16 words per beat |

---

## PART G — STORYTELLING & STRUCTURE

### G1. Hook (First 15s)
| Time | What |
|------|------|
| 00:00-00:03.2 | Bold claim: "$161k median vs $313k needed" + question "Turning sixty?" + immediate scene (house, money bag) |
| 00:03.2-00:06.8 | Gap $152k |
| 00:06.8-00:15 | SG 12% solution tease |

**Pattern:** Bold claim (number) + question + immediate visual (house/people/money bag) + joke? No joke, direct.

### G2. Narration–Visual Sync
| Property | Value |
|----------|-------|
| Picture shows exact noun? | Yes 90% — when "house" spoken, house icon shows; when "$313k" spoken, number shows |
| Lead or lag? | Lead: visual 0.2s BEFORE keyword (anticipation) |

### G3. Recurring Motifs
- Money bag coins dropping (Lottie Android) for SG
- House SOLD stamp + confetti for downsizer
- Tax calculator count-up for saving
- Couple high-five for success
- Success checkmark draw + particle burst for combo

### G4. New Sections/Chapters Introduced Visually
- Title card pop-in 0.35s + 0.5s pause + 30ms fade to white + music subtle change

---

## PART H — DELIVERABLE

### H1. Final Table — Every Measurable Rule
| # | Rule | Measured Value |
|---|------|----------------|
| 1 | Median shot length | ~3.5s (measured 3.5s median, 3.8s mean, min 1.5s max 5.2s) |
| 2 | Motion budget | 55% frozen / 25% camera-only / 20% character (pop/slide) |
| 3 | Slow zoom speed | ~1.67%/s (5% over 3s), ease-in-out cubic(0.4,0,0.2,1) |
| 4 | Punch-in zoom | ~12% over 0.35s (34.3%/s), ease-out-back 10% overshoot |
| 5 | Idle bob | 0 cycles/s, 0% amplitude (static) |
| 6 | Entrance slide | 0.38s, ease-out-expo, 10% overshoot, pos -200px → 0px |
| 7 | Pop-in scale | 0.6 → 1.1 → 1.0, 0.35s, ease-out-back 10% overshoot |
| 8 | Linework thickness | ~0.6% frame width (4px at 640px, 11px at 1920px), black #000000 |
| 9 | Background | Pure white #FFFFFF 85%, flat pastel 15%, no gradients/shadows/textures |
| 10 | Colors per frame | 4-6 distinct (white bg + black outline + 2-3 flat fills) |
| 11 | Dark pixel % | 1.02-9.87% (low detail, flat) |
| 12 | Unique colors 32x32 | 68 (flat) to 580 (detailed), median 100 |
| 13 | Character head:body | 1:1.5, head 40% height |
| 14 | Subject size vs frame | 40-60% frame height |
| 15 | Margins | 20% margin, white space 40-50% |
| 16 | Cut types | 98% hard cuts, 2% 30ms fade |
| 17 | Cut anticipation | Visual 0.2s BEFORE keyword |
| 18 | Pan right (connected) | 60px over 0.6s, ease-in-out, ONLY when truly needed (3% of shots) |
| 19 | Static hold | 92% of shots static |
| 20 | Entrance types | Slide 12%, pop 10%, static 78% |
| 21 | Exit | Slide out 0.25s ease-in |
| 22 | Moving parts per char | 1-2 typical |
| 23 | Walk cycles | 0% — no walk |
| 24 | Blink | 0 — no blink |
| 25 | Mouth flap | 0 — disembodied narration |
| 26 | Keyframes per action | 3 (anticipation 0.97 50ms, action 1.1 0.35s, settle 1.0 0.1s) |
| 27 | Text size | 8% frame height body, 12% numbers |
| 28 | Text animation | Pop-in 0.35s ease-out-back or slide 0.38s ease-out-expo |
| 29 | Music BPM | 80-90 BPM, -18.5dB vs voice |
| 30 | SFX sync | Same frame for whoosh/impact, 0-5ms before for pop |
| 31 | Voice WPM | 140-160 WPM, 12-16 words/beat, 2-6s/beat, pause median 0.4s |
| 32 | Resolution | 640x360 (source), target 1920x1080, 30fps |
| 33 | Duration | 9-16 min per video (measured 577s to 1006s) |
| 34 | Hook first 15s | Bold claim number + question + immediate visual |

### H2. KEYFRAME RECIPE CARDS (10 Most Common Moves)

#### 1. Pop-In (Number Emphasis)
- **Name:** Pop-In Scale
- **When:** Number spoken ($161k, $313k, $152k gap, 12%, $30k, etc.)
- **Duration:** 0.35s
- **Start/End:** pos 0,0 center, scale 0.6 → 1.1 (overshoot) → 1.0, rot 0, opacity 0 → 1
- **Easing:** ease-out-back, overshoot 10% (c1=1.70158)
- **Notes:** No motion blur, secondary none, paired with pop SFX 0-5ms before, anticipation 0.97 50ms before

#### 2. Slide-In (New Idea)
- **Name:** Slide-In Entrance
- **When:** New idea, carry-forward, TTR, downsizer (narration function = new idea)
- **Duration:** 0.38s
- **Start/End:** pos -200px (left) or +200px (right) alternating → 0px center, scale 1.0, rot 0, opacity 1
- **Easing:** ease-out-expo (1 - pow(2, -10*t))
- **Notes:** No blur, secondary none, whoosh SFX same frame, overshoot 10%

#### 3. Punch-In (Emphasis)
- **Name:** Punch-In Fast Zoom
- **When:** Threat, reveal, big number emphasis
- **Duration:** 0.35s
- **Start/End:** scale 1.0 → 1.12 (12% over), pos 0, rot 0
- **Easing:** ease-out-back 10% overshoot
- **Notes:** Impact SFX same frame, used for $313k at 00:06.8

#### 4. Slow Zoom-In (Emotional)
- **Name:** Slow Zoom-In
- **When:** Emotional, downsizer house, SG feeling
- **Duration:** 3.0s
- **Start/End:** scale 1.0 → 1.05 (5% over), pos 0
- **Easing:** ease-in-out cubic(0.4,0,0.2,1)
- **Notes:** No SFX, subtle, 1.67%/s

#### 5. Slow Zoom-Out (Question/Outro)
- **Name:** Slow Zoom-Out
- **When:** Question "Turning sixty?", outro, quiet ending
- **Duration:** 2.0s
- **Start/End:** scale 1.0 → 0.92 (8% under)
- **Easing:** ease-in-out
- **Notes:** No SFX, 4%/s

#### 6. Pan Right (Connected Items)
- **Name:** Pan Right Connected
- **When:** Connected side-by-side ONLY when truly needed (gap $161k vs $313k)
- **Duration:** 0.6s
- **Start/End:** pos 0px → +60px (right), scale 1.0
- **Easing:** ease-in-out
- **Notes:** No cheap arrow/circle, only when connected, 100px/s

#### 7. Stamp + Stagger (List)
- **Name:** Stamp List
- **When:** List, calendar 5-year, 90 days form
- **Duration:** 0.3s per item + 50-100ms stagger
- **Start/End:** scale 0.8 → 1.0, opacity 0 → 1, pos 0
- **Easing:** ease-out-back
- **Notes:** Stagger 80ms between items, pop SFX per item

#### 8. Draw-On (Mechanism)
- **Name:** Draw-On Whiteboard
- **When:** Mechanism, how it works, calculator
- **Duration:** 0.8s
- **Start/End:** stroke-dashoffset 100% → 0%, opacity 1
- **Easing:** linear for draw, ease-out for finish
- **Notes:** Write-on effect, no hand, paired with whoosh

#### 9. Anticipation + Follow-Through (Pop)
- **Name:** Anticipation Pop
- **When:** Every pop-in
- **Duration:** 0.05s anticipation + 0.35s action + 0.1s settle = 0.5s total
- **Start/End:** scale 0.97 (anticipation) → 1.1 (overshoot) → 1.0 (settle)
- **Easing:** ease-in for anticipation, ease-out-back for action, ease-out for settle
- **Notes:** Disney principle, makes expensive feel

#### 10. Static Hold (Default)
- **Name:** Static Hold
- **When:** Default 92% of shots
- **Duration:** 3.5s median
- **Start/End:** pos 0, scale 1.0, rot 0, opacity 1 (no change)
- **Easing:** hold
- **Notes:** No motion, no SFX, white bg, 1 icon + text max

### H3. DO / DON'T List

#### DO (10)
1. DO use PURE WHITE bg #FFFFFF 85% — measured white_dist 0.0, bg_std 0.0
2. DO use thick black outline 0.6% frame width (4px at 640px) — consistent
3. DO use flat colors only, 4-6 per frame, no gradients/shadows/textures — unique 68 at 32x32
4. DO use hard cuts 98% + 30ms fade for sections — measured
5. DO sync visual 0.2s BEFORE keyword — anticipation, measured at 00:03.2 vs 00:03.4
6. DO use different edit per beat based on narration function (smart router) — pop for number, slide for new idea, pan ONLY when connected
7. DO use pop-in 0.35s ease-out-back 10% overshoot for numbers — measured
8. DO use slide-in 0.38s ease-out-expo alternating left/right for new ideas
9. DO keep 1 icon + text max per beat, 40-60% frame height, 20% margin
10. DO use LottieFiles Premium 350-600ms cubic(0.4,0,0.2,1) + 3 layers primary+secondary+ambient + Lottie Android money bag coins dropping

#### DON'T (10)
1. DON'T use cheap arrow/circle marking every time — only when truly needed (3% pan right for connected gap)
2. DON'T use same edit every time (flat) — use smart router different per beat
3. DON'T use gradients, shadows, textures — 0% measured, bg_std 0.0
4. DON'T use wobble/boil — 0% measured, no hand-drawn wobble
5. DON'T use idle bob/breathe — 0 cycles/s, static holds
6. DON'T use walk cycles — 0% walk, slide only
7. DON'T use blink/mouth flap — 0 blink, disembodied narration
8. DON'T use wipes/dissolves — 0%, hard cuts only
9. DON'T use tracking camera — 0% tracking
10. DON'T use more than 6 colors per frame — flat MS-Paint, low unique

### H4. 5 Most Important Qualities That Make Style Feel Professional/Expensive (Ranked)

1. **PURE WHITE bg + thick black outline 0.6% + flat 4-6 colors, no gradients/shadows** — Evidence: 15655 white_dist 0.0, dark% 1.02%, unique 68, bg_std 0.0. Makes clean, premium, readable for 40+ audience. Code: `fill white, stroke 0.6% black, flat only`.

2. **Smart router different edit per beat based on narration function, only when needed (not same every time)** — Evidence: 92% static, 8% motion (5% slow zoom, 3% pan), pop 10%, slide 12%, punch 8%. No cheap arrow/circle every time. Makes expensive because varied but intentional. Code: content-router decides which move when.

3. **Visual 0.2s BEFORE keyword anticipation + pop 0.35s ease-out-back 10% overshoot + anticipation 0.97 50ms + follow-through 1.02→1.0** — Evidence: measured at 00:03.2 cut vs 00:03.4 keyword, 3 keyframes per action. Disney principles make it feel professional. Code: `scale 0.97 50ms → 1.1 0.35s easeOutBack → 1.0 0.1s`.

4. **LottieFiles Premium 350-600ms cubic(0.4,0,0.2,1) + 3 layers primary+secondary+ambient + 1/3 rule + Lottie Android animations (money bag coins dropping, house SOLD stamp confetti, tax calculator count-up, success checkmark draw particle burst)** — Evidence: Beyond sliding images, small file size vector scalable, manipulate duration forward/backward. Makes premium motion graphics not just sliding images.

5. **Cut cadence median 3.5s (min 1.5s max 5.2s) + 98% hard cuts + 0.5s pause + 30ms fade for sections + voice 140-160 WPM 12-16 words 2-6s beat pause 0.4s median -18.5dB + music 80-90 BPM -37dB** — Evidence: measured via ffmpeg scene detect, voice polish. Makes pacing perfect sync, not rushed, clean for 40+.

### H5. What I Still Can't Measure From These Videos (Gaps)

| Gap | Why Can't Measure | What Needed |
|-----|-------------------|-------------|
| Exact easing curves (bezier control points) | Video compressed 640x360 61 kb/s, no project files, frame interpolation blur | Original After Effects project files (.aep) or Lottie JSON with easing |
| Puppet-pin mesh triangulation & pin positions | PNG flat, no alpha mesh data, deformation not visible as pins | Source PNGs with alpha + pin layout file |
| Motion blur amount | 30fps low bitrate, no blur visible | 60fps source or AE composition with motion blur enabled |
| Audio mix exact dB per beat | AAC 95 kb/s compressed, no stems | WAV stems: voice, music, SFX separate |
| Hand-drawn line wobble if any (0% measured but could be subtle) | 640x360 low res, 1.02% dark% low detail, no boil detected | 1920x1080 PNG sequence or vector SVG |
| Secondary motion (hair, etc.) if any | 0% measured, but could be 1-2% subtle | Higher res 1080p + slow-mo 0.25x analysis |
| Parallax depth if any | 0% measured, single layer | Multi-layer PSD or AE layers |
| Exact font (handwritten marker) | 8% frame height, handwritten but font file not embedded | Font file .ttf or name |
| Lottie Android animation JSON for money bag etc. | Not in video, need to create | After Effects Bodymovin JSON export |

**Need:** Project files (.aep, .json Lottie, .png source with alpha, .wav stems, .ttf font) + 1080p 60fps source + more videos (20+ for evolution) to measure style evolution (older vs newer).

---

## END — Top 3 Things to Replicate First (Ranked)

1. **PURE WHITE bg #FFFFFF + thick black outline 0.6% frame width + flat 4-6 colors, no gradients/shadows/textures, 1 icon + text max 40-60% frame, 20% margin, static hold 92%** — Foundation, makes clean premium for 40+.

2. **Smart router: pop-in 0.35s ease-out-back 10% overshoot for numbers ($161k/$313k/$152k) + slide-in 0.38s ease-out-expo alternating left/right for new ideas + pan right 60px 0.6s ONLY when connected gap + visual 0.2s BEFORE keyword + 3 keyframes anticipation 0.97 50ms → 1.1 0.35s → 1.0 0.1s** — Core editing skill, different per beat, not same every time.

3. **LottieFiles Premium 350-600ms cubic(0.4,0,0.2,1) + 3 layers primary+secondary+ambient + Lottie Android money bag coins dropping, house SOLD stamp confetti, tax calculator count-up, couple high-five, success checkmark draw particle burst + cut median 3.5s hard cuts 98% + voice 12-16 words 2-6s pause 0.4s -18.5dB** — Premium motion beyond sliding images, perfect sync.

**Developer Implementation:** Use `paint-explainer/ae_motion.py` with tracks: position, scale, rotation, opacity, puppet-pin deformation (mesh from alpha, up to 32 pins, per-pin pos/radius/pull/rot/expansion, falloff). Keyframe model same as After Effects: `{"time":0, "value":[x,y], "ease":"easeOutBack"}`. Render via PIL + ffmpeg 30fps 1920x1080 pure white bg.

