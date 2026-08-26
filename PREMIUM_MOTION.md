# Premium Motion Graphics — LottieFiles + Hyperframes + MemOS

> Connected:
> - https://github.com/LottieFiles/motion-design-skill (1.4k stars, MIT) — Universal motion design principles
> - https://github.com/heygen-com/hyperframes (open-source HTML-to-video, 50+ blocks)
> - https://github.com/aaronpie/hyperframes-kit (12 finished projects)
> - https://github.com/MemTensor/MemOS (persistent memory)

**Problem:** Before only sliding images (pop-in 0.35s, slide-in 0.38s, pan 60px, zoom 3%) — flat animation = missing layers.

**Solution:** Premium motion graphics with LottieFiles 8-step checklist + Hyperframes HTML pipeline + MemOS memory.

## LottieFiles Motion-Design-Skill

**Install:**
```bash
npx skills add LottieFiles/motion-design-skill
```

**What's included:**
- `SKILL.md` — 8-step checklist, motion personality archetypes, duration/easing tables
- `director/` — Three pillars, Disney 12 principles, emotion mapping, choreography, narrative structure
- `patterns/` — Entrance/exit, state-feedback, ambient, multi-element
- `reference/` — Timing/easing tables, property selection, quality checklist, troubleshooting

**8-Step Checklist Before Any Animation:**
1. Emotional target? — joy, calm, urgency, elegance, trust
2. Motion Personality? — Playful (150-300ms ease-out-back 10-20% overshoot fun whimsical bouncy cute), Premium (350-600ms cubic-bezier(0.4,0,0.2,1) 0% elegant minimal luxury sophisticated), Corporate (200-400ms cubic-bezier(0.2,0,0,1) 0-3% clean professional business dashboard), Energetic (100-250ms ease-out-expo 15-30% dynamic energetic bold exciting)
3. Primary property? — position, scale, rotation, opacity
4. Duration? — tooltip 80-120ms, button 120-180ms, icon 150-250ms, card 200-350ms, modal 300-400ms, page 400-600ms, dramatic 600-1200ms, finance beat 350-600ms Premium
5. Easing family? — entrance=decelerate ease-out, exit=accelerate ease-in, on-screen=ease-in-out, looping=sine
6. Hero element? — staging principles
7. Secondary + ambient layers? — richness
8. 1/3 rules? — motion <1/3 screen without keyframe, simultaneous elements <500ms stagger

**Three Pillars (CRITICAL):**
- Emotional Intent: What should viewer FEEL? → drives easing, timing, amplitude
- Visual Narrative: Setup → Action → Resolution micro-story
- Motion Craft: Physics, secondary motion, paths, believability

**Three Motion Layers (flat = missing layers):**
- Primary: Main action viewer follows
- Secondary: Supporting richness (shadows 50ms after, icons shift 2px, content fades 100ms after)
- Ambient: Background life (gradient pulse 2% breathing loop sine ease-in-out 2s)

**Disney's 12 Principles Adapted for UI:**
- Squash & Stretch, Anticipation, Staging, Straight Ahead, Follow Through, Slow In/Out, Arc, Secondary Action, Timing, Exaggeration, Solid Drawing, Appeal

**Common Patterns:**
- Button Press Playful: Anticipation scale 0.97 50ms ease-out, Squash [1.04,0.96] 100ms ease-in, Follow through 1.02→1.0 spring 200ms, Secondary shadow shrinks, icon shifts down 2px
- Card Entrance Premium: Start 20px below opacity 0, Path slight curve 10px X offset midpoint, Easing ease-out-cubic, Shadow arrives 50ms after card, Content fades 100ms after, Other cards dim 80%
- Success State Playful: Scale pop ease-out-back, Checkmark draws in, Particle burst, Green fill, 300-400ms
- Error Shake Corporate: Position ±10-15px 2-3 times horizontal, ease-in-out, Red tint, 300-400ms, No overshoot firm

## Hyperframes

**Install:**
```bash
npm install -g hyperframes
npx hyperframes init videos/my-project --example=blank
npx hyperframes preview  # http://localhost:3002
npx hyperframes lint     # HTML structure check
npx hyperframes check    # Headless Chrome runtime errors
npx hyperframes render . -q high -o ./renders/video.mp4
```

**What it is:**
- Open-source HTML-to-video rendering: write HTML, render video
- Plain HTML file with paused GSAP timeline on window.__timelines
- Supports: CSS, GSAP, Lottie, Three.js, Anime.js, WAAPI, shaders
- 50+ blocks: data-chart, caption-*, logo-outro, us-map, world-map, etc.
- Skills: /motion-graphics (short design-led, motion-is-message, <10s, no narration, kinetic-type, stat count-up, charts, logo sting, lower-thirds, maps), /general-video (longer narrated)

**12 Projects in hyperframes-kit:**
- Short-form vertical 9:16: may-shorts-19 (TikTok talking-head + MG + karaoke captions, most polish, /short-form-video skill written around it), may-shorts-18
- Product promos: clickup-demo (60s SaaS heavy registry-block x-post ui-3d-reveal, 5 render versions), linear-promo-30s (30s Linear-style Infinite Payments aesthetic), hyperframes-sizzle (Hyperframes × Claude Code), first-agent-promo (32s Your First AI Agent, React-via-Babel counter-example)
- Educational: aisoc-lesson-5-1 (full lesson face-cam + MG, transcribe→word-synced MG→sections), golden-ratio-demo (proportion), claude-edit-intro (promo intro minimal brand)

**Composition Contract:**
- data-* timing attributes, class="clip", tracks, sub-compositions, variables, deterministic
- Framework-owned media playback, seek-safe keyframes

## Combined Premium for Finance-Australia 40+

**Before (sliding images only):**
```python
# ae-motion old
pos = [{"t":0.0, "v":[640,360], "e":"hold"}]
scale = [{"t":0.0, "v":0.6, "e":"hold"}, {"t":0.25, "v":1.10, "e":"easeOutBack"}, {"t":0.35, "v":1.0, "e":"easeOutBack"}]
# Flat, primary only, no secondary, no ambient, same edit every time
```

**After (premium motion graphics):**
```python
from backend.premium_motion import premium_renderer

scene = premium_renderer.create_scene(
    subject="downsizer_300k",
    emotional_target="joy+trust for 40+ Aussies achieving comfort",
    personality="Premium",  # 350-600ms, cubic-bezier(0.4,0,0.2,1), 0% overshoot, elegant
    primary="House SOLD scales 0.6→1.1→1.0 350ms ease-out-cubic, path slight curve 10px X offset",
    secondary="Piggy bank fades 100ms after house, shadow arrives 50ms after, $300k text badge",
    ambient="Background gradient pulse 2% scale breathing loop sine ease-in-out 2s",
    duration=350,
    easing="cubic-bezier(0.4,0,0.2,1)",
    hero="house",
    image_path="assets/011_downsizer_300k_visual.png"
)

# Premium includes:
# - 8-step checklist: emotional target joy+trust, personality Premium, primary scale+position, duration 350ms, easing cubic-bezier, hero house, secondary+ambient, 1/3 rules
# - Three pillars: Emotional Intent trust → easing, Visual Narrative house→super, Motion Craft anticipation follow-through
# - Three layers: Primary house scale, Secondary piggy bank fade + shadow, Ambient gradient pulse
# - Disney: Squash & Stretch anticipation 0.97 50ms, Anticipation opposite move, Staging hero first dim others 80%, Follow Through 1.02→1.0 spring 200ms, Slow In/Out, Arc 10px curve, Secondary Action shadow 50ms after
```

**For $600k per couple (Energetic personality for punch):**
```
Emotional: Joy + excitement couple achieving together
Personality: Energetic (100-250ms, ease-out-expo, 15-30% overshoot, dynamic bold exciting)
Primary: Two stick figures couple + $600k text pop 0.5→1.15→1.0 250ms ease-out-back 15% overshoot
Secondary: Two piggy banks stagger 80ms, house behind fades 100ms after
Ambient: Confetti particle burst subtle
Duration: 250ms entrance (Energetic), total 400ms with follow-through
```

**For Salary Sacrifice Flow (Corporate personality):**
```
Emotional: Trust + clarity for tax saving
Personality: Corporate (200-400ms, cubic-bezier(0.2,0,0,1), 0-3% overshoot, clean professional)
Primary: Salary card enters -300→center 0.38s ease-out, arrow draws in 0.30s, super card enters 300→center 0.38s stagger 80ms
Secondary: 15% vs 32.5% comparison badge pops
Ambient: Gradient sweep 90deg transparent→2%→transparent 1.5s sine
Choreography: Hero salary first, then arrow, then super (spatial consistency same direction)
```

## Files in This Integration

```
backend/premium_motion/
├── README.md (this)
├── __init__.py
├── premium_renderer.py          # Combines LottieFiles + Hyperframes + MemOS
├── lottie_skill/                # LottieFiles motion-design-skill (1.4k stars)
│   ├── SKILL.md                 # 8-step checklist, personality, duration/easing
│   ├── director/                # Three pillars, Disney principles, emotion mapping
│   │   ├── core-philosophy.md
│   │   ├── disney-principles.md
│   │   ├── motion-personality.md
│   │   ├── choreography.md
│   │   └── ...
│   ├── patterns/                # Entrance/exit, state-feedback, ambient, multi-element
│   └── reference/               # Timing/easing tables, property selection, quality checklist
├── hyperframes/                 # Hyperframes motion-graphics skill
│   ├── SKILL.md                 # Short design-led motion graphic workflow
│   ├── agents/                  # Director, Builder
│   ├── categories/              # kinetic-type, stat, charts, logo-reveal, lower-thirds, maps, webpage, news, tweet, asset-fusion
│   ├── references/              # Motion vocabulary, builder contract
│   └── ...
└── templates/                   # Premium HTML templates for finance-australia
    ├── downsizer_house_reveal.html  # House SOLD → super Premium motion with GSAP
    └── salary_sacrifice_flow.html   # Salary → super flow Corporate

backend/memos_memory/            # MemOS persistent memory (already connected)
├── memory_store.json            # Git-committed, survives wipes, 4 memories
└── ...
```

## Usage for Paint-Explainer

**Old way (sliding images):**
```bash
# Generate 10 text images, render with ae-motion pop/slide
python3 ae_motion.py scenes/scene_011.json -o output/scene_011.mp4
```

**New way (premium motion graphics):**
```python
# 1. Use premium renderer with LottieFiles principles
from backend.premium_motion import premium_renderer
scene = premium_renderer.create_scene(
    subject="downsizer_300k",
    personality="Premium",
    emotional_target="joy+trust",
    primary="House scale 0.6→1.1→1.0 350ms",
    secondary="Piggy bank fade 100ms after",
    ambient="Gradient pulse 2% breathing"
)
# Save scene JSON and render with ae-motion (now has anticipation, follow-through, 3 layers)

# 2. For HTML-native premium (future)
html = premium_renderer.create_hyperframes_template("downsizer_300k", "Premium")
# Save to templates/ and:
# npx hyperframes preview  # http://localhost:3002
# npx hyperframes render . -q high -o ./renders/downsizer.mp4
# Supports transparent overlay: --format webm/mov

# 3. MemOS remembers what works
from backend.memos_memory import memos_plugin
memos_plugin.remember(content="Premium motion Premium personality 350ms works for 40+ Aussies trust")
```

## For Finance-Australia 8-10 Min Video

**Batch 1 Visual (11-20) DONE with premium motion:**
- 011 downsizer $300k: Premium 350ms cubic-bezier(0.4,0,0.2,1) 0% overshoot, house with SOLD, piggy bank secondary, gradient ambient, anticipation 0.97 50ms, follow-through 1.02→1.0
- 012 10 years: Corporate 200-400ms, house + calendar, slide-in left
- 013 90 days: Corporate, calendar 90 days + clock, slide-in right
- 014 $600k couple: Energetic 100-250ms ease-out-expo 15-30% overshoot for punch, two stick figures couple, 2 piggy banks stagger 80ms
- etc.

**Next batches will use:**
- Salary sacrifice flow: Corporate personality with flow animation (salary -300→center, arrow draws, super 300→center)
- TTR pension: Premium with slow-zoom focus
- Stat count-up: Energetic with Apple money-count block from Hyperframes
- Chart: data-chart block from Hyperframes for $152k gap

## Installation for Full Premium

```bash
# LottieFiles skill (already copied)
npx skills add LottieFiles/motion-design-skill

# Hyperframes
npm install -g hyperframes
npx hyperframes doctor
npx hyperframes init videos/finance-australia --example=blank

# MemOS (already connected)
# See MEMOS_INTEGRATION.md
```

## Links

- LottieFiles: https://github.com/LottieFiles/motion-design-skill
- Hyperframes: https://github.com/heygen-com/hyperframes
- Hyperframes Kit: https://github.com/aaronpie/hyperframes-kit (12 projects)
- MemOS: https://github.com/MemTensor/MemOS
- Docs: https://hyperframes.heygen.com/introduction, https://memos-docs.openmem.net/
```

**Status:** ✅ Connected — LottieFiles (1.4k stars) + Hyperframes (HTML-to-video, 50+ blocks) + MemOS (persistent memory) for premium motion graphics beyond sliding images.
