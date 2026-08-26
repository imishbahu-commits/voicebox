# Premium Motion Graphics V2 — LottieFiles + Hyperframes + Lottie Android + MemOS

> Connected repos for premium motion beyond sliding images:
> - https://github.com/LottieFiles/motion-design-skill (1.4k stars, MIT) — Motion principles
> - https://github.com/heygen-com/hyperframes (HTML-to-video, 50+ blocks, GSAP/Lottie/Three.js)
> - https://github.com/aaronpie/hyperframes-kit (12 finished projects: may-shorts-19 TikTok + MG + karaoke)
> - https://github.com/airbnb/lottie-android (35.7k stars) — Render After Effects JSON natively on Android/iOS/Web/React Native
> - https://github.com/MemTensor/MemOS (11k stars) — Persistent memory across chats

## Problem: Only Sliding Images Before

**Old ae-motion.py:**
- pop-in 0.35s easeOutBack, slide-in 0.38s easeOutExpo, pan right 60px, slow-zoom 3%
- 92% static hold, flat animation = missing layers
- Same edit every time, no Disney principles, no personality, no choreography
- Text-only images like "$300k per person" — doesn't resonate

**User feedback:** "Why in the video have only text I want visuals so that's people's can really resonated" + "many we need to explain something not only by sliding images but also with premium motion graphics"

## Solution: Premium Motion Graphics with 4 Repos

### 1. LottieFiles Motion-Design-Skill (Principles)

**8-Step Checklist Before Any Animation:**
1. Emotional target? — joy, calm, urgency, elegance, trust+joy for 40+ Aussies
2. Motion Personality? — Playful 150-300ms ease-out-back 10-20% fun whimsical bouncy cute, Premium 350-600ms cubic-bezier(0.4,0,0.2,1) 0% elegant minimal luxury sophisticated, Corporate 200-400ms cubic-bezier(0.2,0,0,1) 0-3% clean professional business dashboard, Energetic 100-250ms ease-out-expo 15-30% dynamic bold exciting
3. Primary property? — position, scale, rotation, opacity
4. Duration? — tooltip 80-120ms, button 120-180ms, icon 150-250ms, card 200-350ms, modal 300-400ms, page 400-600ms, dramatic 600-1200ms, finance beat 350-600ms Premium
5. Easing family? — entrance decelerate ease-out, exit accelerate ease-in, on-screen ease-in-out, looping sine
6. Hero element? — staging principles
7. Secondary + ambient layers? — richness
8. 1/3 rules? — motion <1/3 screen, stagger <500ms

**Three Pillars:**
- Emotional Intent: What should viewer FEEL? → drives easing, timing, amplitude
- Visual Narrative: Setup → Action → Resolution micro-story
- Motion Craft: Physics, secondary motion, paths

**Three Motion Layers:**
- Primary: Main action viewer follows (house scale 0.6→1.1→1.0)
- Secondary: Supporting richness (shadow arrives 50ms after, piggy bank fades 100ms after, icon shifts 2px)
- Ambient: Background life (gradient pulse 2% breathing loop sine ease-in-out 2s)

**Disney's 12 Principles:**
- Squash & Stretch (scale 0.97 anticipation 50ms), Anticipation, Staging (hero first dim others 80%), Follow Through (overshoot 1.02→1.0 spring 200ms), Slow In/Out, Arc (10px X curve), Secondary Action (shadow 50ms after), Timing, Exaggeration, Solid Drawing, Appeal

**Patterns:**
- Card Entrance Premium: Start 20px below opacity 0, Path curve 10px X, Easing ease-out-cubic, Shadow 50ms after, Content fades 100ms after, Other cards dim 80%
- Success State Playful: Scale pop ease-out-back, Checkmark draws in, Particle burst, Green fill, 300-400ms
- Error Shake Corporate: Position ±10-15px 2-3 times, ease-in-out, Red tint, 300-400ms, No overshoot

### 2. Hyperframes (HTML-to-Video Pipeline)

**HTML-Native Video:**
- Write HTML, render video — plain HTML file with paused GSAP timeline on window.__timelines
- Supports: CSS, GSAP, Lottie, Three.js, Anime.js, WAAPI, shaders
- 50+ blocks: data-chart (for $152k gap visualization), caption-*, logo-outro, us-map, world-map
- CLI: `npx hyperframes init`, `preview` http://localhost:3002, `lint` HTML structure, `check` headless Chrome runtime, `render -q high -o ./renders/video.mp4`

**12 Projects in hyperframes-kit:**
- Short-form vertical 9:16: may-shorts-19 (TikTok talking-head + motion graphics + karaoke captions, most polish, /short-form-video skill written around it), may-shorts-18
- Product promos: clickup-demo (60s SaaS heavy registry-block x-post ui-3d-reveal, 5 versions), linear-promo-30s (30s Linear-style Infinite Payments), hyperframes-sizzle, first-agent-promo (32s Your First AI Agent, React-via-Babel)
- Educational: aisoc-lesson-5-1 (full lesson face-cam + MG, transcribe→word-synced MG→sections), golden-ratio-demo, claude-edit-intro

**Skills:**
- /motion-graphics: short design-led, motion-is-message, <10s, no narration, kinetic-type, stat count-up, charts, logo sting, lower-thirds, maps, webpage, news, tweet, asset-fusion
- /general-video: longer narrated multi-scene

### 3. Lottie Android (After Effects JSON Natively)

**Repo:** https://github.com/airbnb/lottie-android (35.7k stars, 5.4k forks, 1,669 commits)

**What it is:**
Lottie is a mobile library for Android and iOS that parses Adobe After Effects animations exported as JSON with Bodymovin and renders them natively on mobile! For the first time, designers can create and ship beautiful animations without an engineer painstakingly recreating it by hand.

**Download:**
```groovy
// Gradle - only supported build config
dependencies {
  implementation 'com.airbnb.android:lottie:$lottieVersion'  // Latest badge: maven-badges.herokuapp.com/maven-central/com.airbnb.android/lottie
}
// Lottie-Compose for Jetpack Compose
implementation 'com.airbnb.android:lottie-compose:6.x.x'
```

**Usage Android View:**
```xml
<com.airbnb.lottie.LottieAnimationView
  android:id="@+id/animationView"
  android:layout_width="wrap_content"
  android:layout_height="wrap_content"
  app:lottie_rawRes="@raw/animation"
  app:lottie_autoPlay="true"
  app:lottie_loop="true" />
```
```java
LottieAnimationView animationView = findViewById(R.id.animationView);
animationView.playAnimation();
```

**Usage Jetpack Compose:**
```kotlin
val composition by rememberLottieComposition(LottieCompositionSpec.RawRes(R.raw.animation))
val progress by animateLottieCompositionAsState(composition, iterations = LottieConstants.IterateForever)
LottieAnimation(composition, progress, Modifier.fillMaxSize())
```

**Usage Web (for Hyperframes HTML-to-video):**
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/lottie-web/5.12.2/lottie.min.js"></script>
<div id="lottie"></div>
<script>
  lottie.loadAnimation({
    container: document.getElementById('lottie'),
    renderer: 'svg',
    loop: true,
    autoplay: true,
    path: 'animations/money-bag.json'  // JSON from LottieFiles or Bodymovin
  });
</script>
```

**Why Lottie for Finance-Australia 40+ Beyond Sliding Images:**

| Need | Old Sliding Image | New Lottie Premium Motion |
|------|-------------------|---------------------------|
| Money bag $300k | Text "$300k per person" | **Coins dropping into super piggy bank with bounce** — Lottie JSON with squash & stretch, anticipation, follow-through, small file size, vector scalable |
| House SOLD | Text "10 years owned" | **House with SOLD stamp + confetti particle burst** — Lottie stamp animation + confetti |
| Tax saving $12k | Text "saves $12k tax" | **Calculator count-up numbers + saving badge pop + green fill** — Lottie count-up + success pattern |
| $600k couple | Text "$600k per couple" | **Two figures high-five with heart + two piggy banks** — Lottie celebration |
| Success | Text "Outside caps" | **Checkmark draws in + particle burst** — LottieFiles Success State Playful pattern 300-400ms |
| Mistakes | Text "Must give form" | **Error shake ±10-15px 2-3 times + red tint** — LottieFiles Error Shake Corporate |

**Lottie Benefits:**
- Small file size, vector, efficient, load from JSON API
- Manipulate programmatically: duration, forward/backward
- Solid support: shapes, layers, alpha, transparency, paths, patterns
- Used by Uber, Netflix, Google, Airbnb, Shopify, Duolingo
- Cross-platform: Android, iOS, Web, React Native, Windows

**Sample Lotties for Finance-Australia:**
- money_bag: Coins dropping into super piggy bank with bounce — for $300k downsizer, $120k non-concessional, $360k bring-forward — Premium 1.5s joy+trust
- house_sold: House SOLD stamp + confetti — for downsizer 10 years, 90 days — Premium 1.2s
- success_checkmark: Checkmark draw + particle burst + green fill — from LottieFiles Success State Playful — for outside caps, work less TTR — Playful 0.4s joy+success
- tax_calculator: Calculator count-up + saving badge pop — for salary sacrifice 15% vs 32.5% — Corporate 1.0s trust+clarity
- couple_celebration: Two figures high-five with heart — for $600k per couple — Energetic 1.0s joy+love

### 4. MemOS (Persistent Memory)

**Repo:** https://github.com/MemTensor/MemOS (11k stars, 2.0 Stardust)

- Remembers which motion personality works for 40+ Aussies (Premium 350ms trust)
- Remembers which Lottie animations resonate (money bag, house SOLD)
- Remembers project progress (10 beats visual DONE 50s, 3 beats premium demo 12.8s DONE)
- Survives sandbox wipes via git-committed `memory_store.json`
- 9 memories now, API `/api/memos/*`

## Combined Premium for Finance-Australia

**Example: Downsizer $300k with ALL 4 repos:**

```
1. MemOS recalls: User wants winning finance topic $152k gap, editing style clean visuals that resonate, previous Batch 1 visual DONE 50s with house/couple/piggy bank

2. LottieFiles principles:
   Emotional target: Joy + Trust for 40+ Aussies achieving comfort
   Personality: Premium (350-600ms, cubic-bezier(0.4,0,0.2,1), 0% overshoot, elegant minimal luxury)
   Duration: 350ms entrance Premium
   Easing: Entrance decelerate ease-out-cubic
   Hero: House
   Checklist: 8-step, 3 pillars, 3 layers, Disney principles, 1/3 rules

3. Hyperframes pipeline:
   HTML template: stage 1280x720, hero house, secondary piggy bank, ambient gradient pulse
   GSAP timeline: paused on window.__timelines, anticipation 0.97 50ms, main 1.10 250ms back.out, follow-through 1.0 100ms power2.out, secondary shadow 50ms after, ambient breathing loop sine.inOut 2s
   Validation: npx hyperframes lint + check
   Render: npx hyperframes render -q high -o ./renders/downsizer.mp4 or transparent overlay --format webm

4. Lottie Android premium motion beyond sliding:
   Primary: House SOLD Lottie animation (stamp + bounce) - JSON from LottieFiles or Bodymovin
   Secondary: Money bag coins dropping Lottie (coins fall into piggy bank with squash & stretch)
   Ambient: Confetti Lottie particle burst
   Code: lottie.loadAnimation({container: #lottie, renderer: 'svg', path: 'animations/house_sold.json'})
   Benefits: Small file size, vector scalable, manipulate duration forward/backward, solid support shapes layers alpha paths

5. MemOS remembers:
   After render, remember: Premium motion Premium personality 350ms cubic-bezier with house SOLD Lottie + money bag Lottie works for 40+ Aussies trust+joy, 50s visual DONE
   Next chat recalls automatically, continues Batch 2 without re-explaining
```

**For Salary Sacrifice Flow:**
```
MemOS: Recall salary sacrifice 15% vs 32.5% tax saving
LottieFiles: Corporate personality 200-400ms cubic-bezier(0.2,0,0,1) 0-3% clean professional, emotional trust+clarity, duration 380ms
Hyperframes: HTML template stage with salary card -300→center ease-out, arrow draws scaleX 0→1, super card 300→center back.out, gradient sweep ambient, choreography hero salary first then arrow then super spatial consistency
Lottie: Tax calculator count-up Lottie (numbers counting) + saving badge pop Lottie (success pattern)
```

## Files

```
backend/premium_motion/
├── README.md (LottieFiles + Hyperframes + MemOS)
├── PREMIUM_MOTION_V2.md (this, adds Lottie Android)
├── __init__.py (exports premium_renderer + lottie_renderer)
├── premium_renderer.py (LottieFiles 8-step checklist, 3 pillars, 3 layers, Disney principles, Hyperframes HTML template)
├── lottie_skill/ (LottieFiles motion-design-skill 1.4k stars)
│   ├── SKILL.md
│   ├── director/ (core-philosophy, disney-principles, motion-personality, choreography, emotion-mapping, narrative-structure)
│   ├── patterns/ (entrance-exit, state-feedback, ambient-continuous, multi-element)
│   └── reference/ (timing-easing-tables, property-selection, quality-checklist, troubleshooting)
├── hyperframes/ (heygen-com/hyperframes motion-graphics skill)
│   ├── SKILL.md (short design-led motion graphic workflow)
│   ├── categories/ (kinetic-type, stat, charts, logo-reveal, lower-thirds, maps, webpage, news, tweet, asset-fusion)
│   └── ...
├── lottie_android/ (airbnb/lottie-android 35.7k stars)
│   ├── README.md
│   ├── lottie_renderer.py (money_bag, house_sold, success_checkmark, tax_calculator, couple_celebration with HTML/Compose/View code)
│   ├── animations/ (Lottie JSON files from LottieFiles or Bodymovin)
│   └── templates/
└── templates/ (premium HTML templates)
    ├── downsizer_house_reveal.html (Premium 350ms with GSAP anticipation follow-through 3 layers)
    └── salary_sacrifice_flow.html (Corporate flow with arrow)

backend/memos_memory/ (MemOS persistent memory)
├── memory_store.json (9 memories, git-committed, survives wipes)
└── ...
```

## Usage

```python
# Old: sliding images only
from paint_explainer.ae_motion import render
render(scene_011.json)  # pop 0.35s, slide 0.38s, flat

# New: premium motion with LottieFiles + Hyperframes + Lottie Android + MemOS
from backend.premium_motion import premium_renderer, lottie_renderer
from backend.memos_memory import memos_plugin

# 1. MemOS recall what works
memories = memos_plugin.recall("finance Australia downsizer")
# → Premium motion 350ms with house visuals resonates

# 2. LottieFiles principles for premium motion
scene = premium_renderer.create_scene(
    subject="downsizer_300k",
    emotional_target="joy+trust",
    personality="Premium",  # 350-600ms, cubic-bezier(0.4,0,0.2,1)
    primary="House SOLD scale 0.6→1.1→1.0 350ms ease-out-cubic with anticipation 0.97 50ms follow-through 1.02→1.0",
    secondary="Piggy bank coins dropping Lottie fades 100ms after, shadow 50ms after",
    ambient="Confetti Lottie particle burst + gradient pulse 2% breathing loop",
    duration=350,
    easing="cubic-bezier(0.4,0,0.2,1)",
    hero="house",
    image_path="assets/011_downsizer_300k_visual.png"
)

# 3. Lottie Android for After Effects JSON animations beyond sliding
lottie_html = lottie_renderer.create_html_template("money_bag", width=600, height=600)
# Save to animations/money_bag.json from LottieFiles
# Use in Hyperframes HTML template with lottie-web

# 4. Hyperframes HTML-to-video pipeline
html = premium_renderer.create_hyperframes_template("downsizer_300k", "Premium")
# Save to templates/ and:
# npx hyperframes preview  # http://localhost:3002
# npx hyperframes render . -q high -o ./renders/downsizer.mp4
# Transparent overlay: --format webm/mov for lower-thirds

# 5. MemOS remember what works
memos_plugin.remember(content="Premium motion with house SOLD Lottie + money bag Lottie works for 40+ Aussies", metadata={"type": "premium_motion", "personality": "Premium"})
```

## Installation

```bash
# LottieFiles skill (already copied to backend/premium_motion/lottie_skill/)
npx skills add LottieFiles/motion-design-skill

# Hyperframes
npm install -g hyperframes
npx hyperframes doctor
npx hyperframes init videos/finance-australia --example=blank

# Lottie Android (for Android projects)
# build.gradle:
implementation 'com.airbnb.android:lottie:$lottieVersion'
implementation 'com.airbnb.android:lottie-compose:6.x.x'

# Lottie Web (for Hyperframes HTML-to-video)
# In HTML: <script src="https://cdnjs.cloudflare.com/ajax/libs/lottie-web/5.12.2/lottie.min.js"></script>
# lottie.loadAnimation({container, renderer:'svg', path:'animations/money-bag.json'})

# MemOS (already connected, 9 memories)
# See MEMOS_INTEGRATION.md
# pip install MemoryOS or docker compose up for full version
```

## For Finance-Australia 8-10 Min Video

**Current progress:**
- Batch 1 Visual (11-20) DONE 50s 1.41MB with real visuals that resonate (house, couple, piggy bank) — Corporate/Playful pop/slide
- Premium Demo (11-13) DONE 12.8s 0.34MB with LottieFiles Premium personality 350ms cubic-bezier anticipation 0.97 50ms follow-through 1.02→1.0 secondary shadow 50ms after ambient gradient pulse

**Next with premium motion (LottieFiles + Hyperframes + Lottie Android):**
- Batch 2 (21-30): Ann $90k $50k unused with Premium motion + Lottie money bag coins dropping + tax calculator count-up Lottie
- Batch 3 (31-40): Work test 40hrs with Corporate + Lottie success checkmark draw + particle burst
- Batch 4 (41-50): Property $800k with Premium + Lottie house SOLD stamp + confetti
- Batch 5 (51-60): ATO averages gap $152k with Hyperframes data-chart block + Lottie stat count-up
- etc.

All with 3 layers (primary Lottie animation + secondary shadow/badge + ambient particles/gradient), not just sliding images.

## Links

- LottieFiles motion-design-skill: https://github.com/LottieFiles/motion-design-skill (1.4k stars, MIT)
- Hyperframes: https://github.com/heygen-com/hyperframes (HTML-to-video, 50+ blocks)
- Hyperframes Kit: https://github.com/aaronpie/hyperframes-kit (12 projects)
- Lottie Android: https://github.com/airbnb/lottie-android (35.7k stars, 5.4k forks) — https://airbnb.io/lottie/
- LottieFiles: https://lottiefiles.com/ (free/premium animations)
- Lottie Web: https://github.com/airbnb/lottie-web (Bodymovin)
- MemOS: https://github.com/MemTensor/MemOS (11k stars, persistent memory)
- Docs: https://hyperframes.heygen.com/introduction, https://memos-docs.openmem.net/, https://airbnb.io/lottie/
```

**Status:** ✅ Connected — LottieFiles (principles) + Hyperframes (HTML-to-video pipeline) + Lottie Android (After Effects JSON natively) + MemOS (memory) for premium motion graphics beyond sliding images.
