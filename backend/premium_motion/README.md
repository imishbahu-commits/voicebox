# Premium Motion Graphics — LottieFiles + Hyperframes + MemOS

> Connected repos:
> - https://github.com/LottieFiles/motion-design-skill (1.4k stars, MIT)
> - https://github.com/heygen-com/hyperframes (open-source HTML-to-video)
> - https://github.com/aaronpie/hyperframes-kit (12 finished projects)
> - https://github.com/MemTensor/MemOS (persistent memory)

This module upgrades paint-explainer from **sliding images** to **premium motion graphics** with professional timing, easing, choreography, and HTML-native video pipeline.

## Why Only Sliding Images Before?

Previous ae-motion.py only did:
- pop-in 0.35s easeOutBack
- slide-in 0.38s easeOutExpo
- pan right 60px
- slow-zoom 3-5%

**Flat animation = missing layers** (from LottieFiles skill):
- Primary only, no secondary, no ambient
- No Disney principles (anticipation, follow-through, squash/stretch)
- No motion personality (Playful, Premium, Corporate, Energetic)
- No choreography (hero first, 1/3 rule, stagger)

## What Premium Motion Graphics Adds

### From LottieFiles motion-design-skill:

**8-Step Checklist Before Any Animation:**
1. Emotional target? — joy, calm, urgency, elegance
2. Motion Personality? — Playful (150-300ms ease-out-back 10-20% overshoot), Premium (350-600ms cubic-bezier 0.4,0,0.2,1 0% overshoot), Corporate (200-400ms 0-3%), Energetic (100-250ms ease-out-expo 15-30%)
3. Primary property? — position, scale, rotation, opacity
4. Duration? — tooltip 80-120ms, button 120-180ms, card 200-350ms, modal 300-400ms, page 400-600ms, dramatic 600-1200ms
5. Easing family? — entrance=decelerate ease-out, exit=accelerate ease-in, on-screen=ease-in-out, looping=sine
6. Hero element? — staging principles
7. Secondary + ambient layers? — richness
8. 1/3 rules? — motion distance, simultaneous elements

**Three Pillars (CRITICAL):**
- Emotional Intent: What should viewer FEEL? → drives easing, timing, amplitude
- Visual Narrative: Micro-story Setup → Action → Resolution
- Motion Craft: Physics, secondary motion, paths

**Three Motion Layers:**
- Primary: Main action viewer follows
- Secondary: Supporting richness (shadows, icons shifting 2px)
- Ambient: Background life (gradients, subtle pulses)

**Disney's 12 Principles Adapted for UI:**
- Squash & Stretch, Anticipation, Staging, Straight Ahead, Follow Through, Slow In/Out, Arc, Secondary Action, Timing, Exaggeration, Solid Drawing, Appeal

**Common Patterns:**
- Button Press (Playful): Anticipation scale 0.97 50ms, Squash [1.04,0.96] 100ms, Follow through 1.02→1.0 spring 200ms, Secondary shadow shrinks
- Card Entrance (Premium): Start 20px below opacity 0, Path slight curve 10px X offset, Easing ease-out-cubic, Shadow arrives 50ms after, Content fades 100ms after, Other cards dim 80%
- Success State: Scale pop ease-out-back, Checkmark draws in, Particle burst, Green fill, 300-400ms
- Error Shake: Position ±10-15px 2-3 times, ease-in-out, Red tint, 300-400ms, No overshoot

### From Hyperframes:

**HTML-Native Video Pipeline:**
- Write HTML, render video — plain HTML file with paused GSAP timeline on window.__timelines
- Supports: CSS, GSAP, Lottie, Three.js, Anime.js, WAAPI, shaders
- 50+ blocks: data-chart, caption-*, logo-outro, us-map, etc.
- CLI: `npx hyperframes init`, `preview`, `lint`, `check`, `render`
- Skills: /motion-graphics (short design-led, motion-is-message, <10s, no narration), /general-video (longer narrated)

**12 Finished Projects in hyperframes-kit:**
- Short-form vertical 9:16: may-shorts-19 (TikTok talking-head + MG + karaoke captions, most polish), may-shorts-18
- Product promos: clickup-demo (60s SaaS, heavy registry-block), linear-promo-30s, hyperframes-sizzle, first-agent-promo (32s)
- Educational: aisoc-lesson-5-1 (face-cam + MG), golden-ratio-demo, claude-edit-intro

**Composition Contract:**
- data-* timing attributes, class="clip", tracks, sub-compositions, variables, deterministic
- Validation: `npx hyperframes lint` (HTML structure), `npx hyperframes check` (headless Chrome runtime errors)

### Combined with MemOS:

MemOS remembers:
- Which motion personality works for finance-australia 40+ (Corporate + Premium?)
- Which easing curves resonate
- Which visual patterns (house, couple, piggy bank) + motion
- Project progress

## For Finance-Australia 40+ Project

**Before (sliding images):**
- Image pops or slides, static hold 92%
- Flat, no secondary, no ambient
- Same edit every time

**After (premium motion graphics):**
- **Primary**: House with SOLD sign scales 0.6→1.10→1.0 easeOutBack 10% overshoot 350ms (Premium personality)
- **Secondary**: Shadow arrives 50ms after house, piggy bank fades in 100ms after
- **Ambient**: Subtle gradient pulse in background, 2% scale breathing
- **Anticipation**: Before $300k appears, house slightly squashes 0.97 50ms
- **Follow-through**: After landing, overshoots 1.02 then settles
- **Choreography**: Hero house first, then couple, then $600k text with stagger 80ms
- **Emotion**: Joy + trust for 40+ Aussies, so Premium easing cubic-bezier(0.4,0,0.2,1), duration 350-600ms, 0% overshoot for elegance

**Example for Downsizer $300k:**
```
Emotional target: Joy + trust (40+ Aussies achieving comfort)
Motion Personality: Premium (350-600ms, cubic-bezier(0.4,0,0.2,1), 0% overshoot, elegant minimal luxury)
Primary: House SOLD scales 0.6→1.1→1.0 350ms ease-out-cubic, path slight curve 10px X
Secondary: Piggy bank fades 100ms after house, shadow arrives 50ms after
Ambient: Background gradient pulse 2% scale breathing loop sine ease-in-out 2s
Duration: 350ms entrance (Premium), 400ms total with follow-through
Easing: Entrance decelerate ease-out, material Paper 1.0x 3-5% overshoot
Hero: House first, then text $300k per person
1/3 Rule: House moves <1/3 screen, no linear spatial movement
```

## Files

```
backend/premium_motion/
├── README.md (this)
├── lottie_skill/           # LottieFiles motion-design-skill
│   ├── SKILL.md            # 8-step checklist, personality, duration/easing tables
│   ├── director/           # Three pillars, Disney principles, emotion mapping
│   ├── patterns/           # Entrance/exit, state-feedback, ambient, multi-element
│   └── reference/          # Timing/easing tables, property selection, quality checklist
├── hyperframes/            # Hyperframes motion-graphics skill
│   ├── SKILL.md            # Short design-led motion graphic workflow
│   ├── agents/             # Director, Builder
│   ├── categories/         # kinetic-type, stat, charts, logo-reveal, lower-thirds, maps, webpage, news, tweet, asset-fusion
│   └── references/         # Motion vocabulary, builder contract
├── templates/              # Premium templates for finance-australia
│   ├── downsizer_house_reveal.html  # House SOLD → super with Premium motion
│   ├── salary_sacrifice_flow.html   # Salary → super flow with Corporate
│   └── ttr_pension_combo.html       # TTR + salary combo with choreography
├── premium_renderer.py     # Combines LottieFiles + Hyperframes + MemOS
└── __init__.py
```

## Usage

```python
from backend.premium_motion import premium_renderer

# Before: sliding image
# scene = {pos: [640,360], scale: 0.6→1.1→1.0 pop 0.35s}

# After: premium motion graphics with LottieFiles principles
scene = premium_renderer.create_scene(
    subject="downsizer_300k",
    emotional_target="joy+trust",
    personality="Premium",  # 350-600ms, cubic-bezier(0.4,0,0.2,1)
    primary="house SOLD scale 0.6→1.1→1.0",
    secondary="piggy bank fade 100ms after + shadow 50ms after",
    ambient="gradient pulse 2% breathing loop",
    duration=350,  # ms
    easing="ease-out-cubic",
    hero="house",
    image_path="assets/011_downsizer_300k_visual.png"
)

# Render with Hyperframes HTML pipeline (future)
# npx hyperframes render templates/downsizer_house_reveal.html
```

## Next Steps

1. Install Hyperframes: `npm install -g hyperframes` or `npx hyperframes`
2. Use templates for finance-australia 40+ with premium motion
3. MemOS remembers which motion works
4. Preview Studio shows premium vs sliding comparison
