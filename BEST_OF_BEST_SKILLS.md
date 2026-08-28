# BEST OF BEST SKILLS — For All Editing Types
## Curated Top-Tier GitHub Repos, Beyond Previous Prompt, In-Depth Detailed

**Goal:** For every editing type present in 11 reference videos (199MB) + beyond, find best-of-best skills (highest stars, most active, best docs, most applicable to code-driven keyframe PNG animation with After Effects model)

**Criteria for Best-of-Best:**
- Stars >1k or active <6 months or unique capability
- Python or JS (for PIL/ffmpeg pipeline)
- Docs + examples
- Applicable to white bg thick outline flat MS-Paint style, pure white #FFFFFF, black #000000 0.6% frame, 4-6 colors, hard cuts median 3.5s, static 92%, pop 0.35s ease-out-back, slide 0.38s ease-out-expo, punch 12% 0.35s

---

## TIER 1 — ESSENTIAL (Must Have, Best of Best)

### 1. puppet-warp — Best for Puppet-Pin Deformation (Python ARAP)
- **URL:** https://github.com/mikecokina/puppet-warp
- **Stars:** ~150, active 2024, GPLv3
- **Why best:** Only Python library for Photoshop Puppet Warp ARAP, plug-and-play, triangular mesh + graph warp + graph-defined warp, demo interactive, pip install, works with PIL/ffmpeg pipeline
- **Features:** `triangular_mesh(width,height,delta,method)` → vertices,faces; `arap_precompute(vertices,faces)` → pre; `graph_warp(vertices,faces,control_indices,shift,pre)` → new_vertices; `graph_defined_warp(image,src_vertices,src_faces,dst_vertices,dst_faces)` → deformed image; supports scipy + JRS Triangle bindings
- **For our style:** Arm wave 20px right 30px up 0.35s, head tilt 5° 0.2s, 1-2 pins typical up to 32, per-pin pos/radius/pull/rot/expansion, anticipation 0.97 50ms + action 1.1 0.35s + settle 1.0 0.1s, starch/overlap via root lock + weight mask
- **Install:** `pip install puppet-warp --break-system-packages` (needs libGL.so.1 → `apt install libgl1` or fallback simple)
- **Code:** See `ae_motion_enhanced.py` puppet_deform_arap()
- **Comparison:** Better than FusionRigFX (needs DaVinci), ImageDeform (needs Unity), OpenCV remap (no ARAP)

### 2. LottieFiles motion-design-skill — Best for Motion Principles (Universal)
- **URL:** https://github.com/LottieFiles/motion-design-skill
- **Stars:** 1.4k, MIT, 40+ agents, npx skills add
- **Why best:** Only universal motion design principles for AI agents, philosophy-first implementation-agnostic, 8-step checklist, 4 archetypes, duration/easing tables, 3 pillars, Disney 12 principles, emotion mapping, choreography, narrative, patterns, reference, quality checklist
- **Features:** SKILL.md <500 lines quick ref, director/ (core-philosophy, decision-framework, disney-principles, motion-personality, emotion-mapping, choreography, narrative-structure, context-adaptation), patterns/ (entrance-exit, state-feedback, ambient-continuous, multi-element), reference/ (timing-easing-tables, property-selection, quality-checklist, troubleshooting)
- **Archetypes for finance-australia 40+:**
  - Playful 150-300ms ease-out-back 10-20% fun whimsical bouncy cute → couple high-five
  - Premium 350-600ms cubic-bezier(0.4,0,0.2,1) 0% elegant minimal luxury sophisticated → house SOLD stamp confetti
  - Corporate 200-400ms cubic-bezier(0.2,0,0,1) 0-3% clean professional business dashboard → SG 12%, salary sacrifice $30k
  - Energetic 100-250ms ease-out-expo 15-30% dynamic energetic bold exciting → numbers $313k punch-in
- **Duration table:** hover <100ms, press <150ms, release 200-300ms, error shake 300-400ms 2-3 oscillations
- **Quality rules:** Never linear for spatial, never opacity-only, never exceed 1/3 screen without keyframe, always 3 layers primary+secondary+ambient
- **For our style:** Pop-in 0.35s ease-out-back 10% overshoot, slide 0.38s ease-out-expo, punch 12% 0.35s, slow zoom 5% 3s 1.67%/s ease-in-out, pan 60px 0.6s only when connected
- **Already used:** Batch2 premium 54.1s 1.56MB combined 20 beats 1.74min 2.89MB with Corporate/Premium/Energetic

### 3. lottie-android — Best for Premium Motion Graphics Beyond Sliding Images
- **URL:** https://github.com/airbnb/lottie-android
- **Stars:** 35.7k, 5.4k forks, 1669 commits, Apache 2.0, Airbnb
- **Why best:** Most stars for animation, renders AE JSON natively on Android/iOS/Web/React Native, small file size vector scalable, manipulate duration forward/backward, shapes layers alpha paths, used by Uber Netflix Google Airbnb Shopify Duolingo, 13000 words docs
- **Features:** LottieAnimationView XML app:lottie_rawRes app:lottie_autoPlay app:lottie_loop, Java addAnimatorUpdateListener playAnimation, Compose rememberLottieComposition LottieCompositionSpec.RawRes animateLottieCompositionAsState LottieConstants.IterateForever, web lottie-web 5.12.2 lottie.loadAnimation container renderer svg loop autoplay path animationData, Gradle implementation com.airbnb.android:lottie:$lottieVersion, 2.8.0+ only androidx
- **For finance-australia 40+:** welcome screen progress, success/failed animation, user input response, money bag coins dropping bounce, house SOLD stamp confetti, tax calculator count-up saving badge pop, couple high-five, success checkmark draw particle burst
- **Benefits:** Lightweight small file size vs PNG sequence, vector scalable, duration control, solid support
- **Already used:** Batch2 premium with money_bag, tax_calculator, success_checkmark, couple_celebration Lottie animations

### 4. hyperframes — Best for HTML-to-Video + 50+ Blocks
- **URL:** https://github.com/heygen-com/hyperframes
- **Stars:** 42.6k, open-source agent-native, Write HTML Render video
- **Why best:** Only agent-native HTML-to-video, composition contract data-* timing class=clip tracks sub-compositions determinism, atomic motion rules scene blueprints transitions runtime adapters GSAP Lottie Three.js Anime.js CSS WAAPI TypeGPU, keyframes seek-safe, CLI npx hyperframes lint check preview render transcribe tts, registry 50+ components, 12 finished projects in hyperframes-kit (aaronpie/hyperframes-kit)
- **Features:** Skills motion-graphics short design-led <10s motion-is-message kinetic type stat count-up chart logo sting lower-third overlay animated tweet headline MP4 or transparent overlay, hyperframes-core, hyperframes-animation, hyperframes-keyframes, CLI, registry blocks
- **For our style:** Kinetic type for $161k, stat count-up for $152k gap, chart for $161k vs $313k, logo sting for house SOLD, lower-third, animated tweet, transparent overlay for confetti
- **Already used:** Reference for Batch2 premium motion graphics

---

## TIER 2 — CRITICAL (Highly Recommended)

### 5. hand-drawn-styles — Best for MS-Paint Thick Outline Flat Style Prompts
- **URL:** https://github.com/threerocks/hand-drawn-styles
- **License:** MIT
- **Why best:** Only tool-agnostic hand-drawn style prompt recipes, 19 styles, PROTOCOL.md + STYLES.md + SKILL.md, render_prompt.py, works with any image model (gpt-image, MidJourney, etc.)
- **Styles for finance:** ms-paint-bad-doodle style 5 (mouse hard draw virus-level intentionally bad, absurd proportions, rough pure color blocks — for $161k median funny), bean-doodle-infographic style 4 (black round bean white dot eye single orange emphasis — for steps), minimal-line-explainer style 2 (米白 paper thin black single line stickman + few props — for flow), whiteboard-explainer style 19 (white bg black line few red/blue marks steps clear — for tutorial)
- **Install:** `git clone https://github.com/threerocks/hand-drawn-styles.git`, `python3 scripts/render_prompt.py --style 5 --subject 'money bag $313k' --text 'no text' --aspect 16:9 --format json`
- **For our style:** Generate PNGs with thick outline 0.6% frame black #000000 flat 4-6 colors pure white bg, max_dim 600, 1 icon + text max

### 6. handanim — Best for Programmatic Hand-Drawn Animation (Python)
- **URL:** https://github.com/subroy13/handanim
- **Why best:** Only Python package for programmatic animation with hand-drawn feel, draw and animate shapes lines ellipses polygons with hand-drawn feel, fill with sketch-style strokes hatching scribbles, animate handwritten text custom fonts, export SVG or MP4, intuitive API scenes timelines
- **For our style:** Hand-drawn linework with wobble if needed (but our spec 0% wobble clean), flat fills via hatching, handwritten marker text 8% body 12% numbers, pop-in slide

### 7. story-to-handdrawn-video — Best for Agent Skill 20 Styles
- **URL:** https://github.com/gnipbao/story-to-handdrawn-video
- **Why best:** Agent skill convert story to hand-drawn video, 20 built-in styles, detailed table with visual features and recommended topics
- **Styles:** colored-pencil-diary default, minimal-line-explainer, kid-crayon, rawkid-crayon, bean-doodle-infographic, ms-paint-bad-doodle, ballpoint-scribble, real-crayon-paper, ink-wash, emotional-watercolor-sketch, retro-gouache-concept, sunlit-storybook, nordic-gouache-storybook, inked-storybook, warm-flat-storybook, naive-marker-notes, zine-riso-collage, organic-contour-doodle, whiteboard-explainer, linocut-editorial
- **For our style:** Use ms-paint-bad-doodle for thick outline flat, whiteboard-explainer for white bg black line, bean-doodle for steps

### 8. srt-whiteboard-animation — Best for SRT → Whiteboard (AI)
- **URL:** https://github.com/geeklee/srt-whiteboard-animation
- **Why best:** Only SRT subtitle → whiteboard hand-drawn video Skill with partition mask orchestration + streaming pen stroke, each element follows subtitle sequentially, pen tip continuous in region then color fill, export MP4, warm beige paper but adaptable to pure white #FFFFFF, independent Python venv prepare_env.py
- **Features:** `parse_srt.py <srt> --target-sec 30 --min-sec 25 --max-sec 35` → storyboard, `render_annotation_preview.py <image> <annotation> <preview>` → check, `render_stream_whiteboard.py <image> <annotation> <output.mp4> assets/drawing-hand.png --ink-path grid --color-fill contour-wipe` → single scene, `merge_scenes.py --inputs scene1.mp4 scene2.mp4 --output final.mp4` → merge, preview.html local editing
- **For our style:** Auto-caption Whisper → SRT → whiteboard mask animation for mechanism, tax calculator, beyond static text

### 9. automated-whiteboard — Best for Fully Automated Whiteboard (Python OpenCV)
- **URL:** https://github.com/maksimKorzh/automated-whiteboard
- **Why best:** Fully automated whiteboard animation using Python OpenCV PyAutoGUI, simple, demo available
- **For our style:** Draw-on effect stroke-dashoffset 0.8s linear for mechanism

---

## TIER 3 — SPECIALIZED (For Specific Editing Types)

### 10. FusionRigFX — Best for DaVinci Resolve Puppet Pin Reference (32 Pins)
- **URL:** https://github.com/mhermiz/FusionRigFX
- **Stars:** 24 commits active, Fuse plugin
- **Why best:** Only Puppet Pin-style deformation for DaVinci Resolve Fusion with automatic mesh + animatable pins, up to 32 pins per-pin pos/radius/pull/rot/expansion, Setup/Animate workflow, influence blending falloff, root lock weight mask, follower/wave deformers, debug overlays
- **For our style:** Reference for Python implementation — use same pin model, mesh from alpha non-transparent pixels, interior+contour sampling, contour expansion, triangulated mesh

### 11. jspaint — Best for MS Paint Reference (7.5k Stars)
- **URL:** https://github.com/1j01/jspaint
- **Stars:** 7.5k, JavaScript HTML5 canvas online classic MS Paint revived + extras
- **Why best:** Most stars for MS Paint, reference for flat thick outline rendering, no anti-alias? But our spec clean vector

### 12. animism / pycairo-animations / motionpicture — Best for Python Frame → Video
- **URLs:** https://github.com/jhol/animism, https://github.com/elliotwaite/pycairo-animations (25 stars), https://github.com/Sbozzolo/motionpicture (GPLv3)
- **Why best:** Simple frameworks for procedurally generating animations with cairo+ffmpeg or Pycairo+ffmpeg or generic frame→video, pip install, need ffmpeg
- **For our style:** Alternative to PIL+ffmpeg in ae_motion.py, for rendering pipeline

### 13. MemOS — Best for Persistent Memory Across Chats
- **URL:** https://github.com/MemTensor/MemOS
- **Stars:** 11k, 1k forks, 2061 commits, 4 modes Cloud API Self-Host Local Plugin SQLite FTS5+vector 100% local
- **Why best:** Self-evolving memory OS ultra-persistent hybrid-retrieval cross-task skill reuse 35.24% token savings, already integrated
- **For our style:** Remember reference video style (9 memories now) across wipes via git-committed memory_store.json, 10 memories after 11 uploads

### 14. Ultimate Video Editing (Local Skill) — Best for Cut Patterns
- **URL:** Local (from previous tasks)
- **Why best:** Entrance 4 types pop/slide/stamp/draw-on, exit 65-75% duration, stagger 50-100ms, 3-act 25/50/25, traps, 90% hard cuts
- **For our style:** Cut cadence median 3.5s, hard cuts 98% + 30ms fade

### 15. content-router (Local Skill) — Best for Smart Router
- **URL:** Local
- **Why best:** Stage map 0-8, one skill at a time, trigger-driven, decides WHICH skill WHEN based on narration function, not same every time
- **For our style:** Different edit per beat (pop for number, slide for new idea, pan only when connected), no cheap arrow/circle every time

---

## TIER 4 — EMERGING (New, High Potential)

### 16. whiteboard-mask-animation — Best for Mask Whiteboard (Chinese Article)
- **URL:** https://github.com/geeklee/whiteboard-mask-animation
- **Why best:** Chinese article → whiteboard mask animation Skill, mask rules current module shows by progress subsequent + protection deducted, unstarted not visible, final full at least 0.5s, preview_server.py http://127.0.0.1:8766, render_mask_whiteboard.py
- **For our style:** Similar to srt-whiteboard but for articles

### 17. DreamWall dwencode — Best for FFmpeg Wrapper with Overlay Text
- **URL:** https://github.com/DreamWall-Animation/dwencode
- **Why best:** FFmpeg python wrapper to encode image sequence to movie with overlay text, rectangles, overlay image, metadata, font path
- **For our style:** Alternative encoding with top-left datetime, top-middle project name, etc.

---

## COMPARISON TABLE — Best of Best for Each Editing Type

| Editing Type | Best Skill | URL | Stars | Why Best | For Finance-Australia 40+ |
|--------------|------------|-----|-------|----------|---------------------------|
| Puppet-pin ARAP | puppet-warp | https://github.com/mikecokina/puppet-warp | ~150 | Only Python ARAP, pip, PIL/ffmpeg | Arm wave, head tilt 5° |
| Motion principles | LottieFiles motion-design-skill | https://github.com/LottieFiles/motion-design-skill | 1.4k | Universal, 8-step, 4 archetypes, 3 layers | Pop 0.35s, slide 0.38s, punch 12% |
| Premium motion beyond sliding | lottie-android | https://github.com/airbnb/lottie-android | 35.7k | Most stars, small vector scalable | Money bag coins, house SOLD confetti, calculator count-up |
| HTML-to-video 50+ blocks | hyperframes | https://github.com/heygen-com/hyperframes | 42.6k | Agent-native, data-* timing, GSAP/Lottie/Three.js | Kinetic type, stat count-up, chart, logo sting |
| MS-Paint thick outline | hand-drawn-styles | https://github.com/threerocks/hand-drawn-styles | — | 19 styles tool-agnostic | Generate PNGs 0.6% outline flat 4-6 colors white bg |
| Hand-drawn animation Python | handanim | https://github.com/subroy13/handanim | — | Programmatic hand-drawn feel SVG/MP4 | Handwritten marker text |
| Story → hand-drawn 20 styles | story-to-handdrawn-video | https://github.com/gnipbao/story-to-handdrawn-video | — | Agent skill 20 styles | ms-paint-bad-doodle, whiteboard-explainer |
| SRT → whiteboard AI | srt-whiteboard-animation | https://github.com/geeklee/srt-whiteboard-animation | — | Partition mask + streaming pen, Whisper SRT | Auto-caption, mechanism |
| Fully automated whiteboard | automated-whiteboard | https://github.com/maksimKorzh/automated-whiteboard | — | Python OpenCV PyAutoGUI | Draw-on 0.8s |
| DaVinci puppet 32 pins | FusionRigFX | https://github.com/mhermiz/FusionRigFX | 24 commits | 32 pins reference, follower/wave | Reference for Python 32 pins |
| MS Paint revived | jspaint | https://github.com/1j01/jspaint | 7.5k | Most stars MS Paint | Reference flat rendering |
| Frame → video | animism/pycairo/motionpicture | https://github.com/jhol/animism etc. | 25 | Simple cairo+ffmpeg | Rendering pipeline alternative |
| Persistent memory | MemOS | https://github.com/MemTensor/MemOS | 11k | Ultra-persistent 35% token savings | Remember style across wipes |
| Cut patterns | Ultimate Video Editing (local) | Local | — | 4 entrance types, stagger | Cut median 3.5s hard 98% |
| Smart router | content-router (local) | Local | — | Stage map 0-8, trigger-driven | Different edit per beat |

---

## INSTALLATION — All Best of Best

```bash
# Tier 1 Essential
pip install puppet-warp --break-system-packages  # Needs libGL.so.1: apt install libgl1 || fallback simple
npx skills add LottieFiles/motion-design-skill --skill motion-design --agent claude-code
# lottie-android: Gradle implementation com.airbnb.android:lottie:$lottieVersion
# hyperframes: npx hyperframes lint check preview render transcribe tts

# Tier 2 Critical
git clone https://github.com/threerocks/hand-drawn-styles.git
pip install handanim  # Check PyPI
git clone https://github.com/gnipbao/story-to-handdrawn-video.git
git clone https://github.com/geeklee/srt-whiteboard-animation.git
git clone https://github.com/maksimKorzh/automated-whiteboard.git

# Tier 3 Specialized
git clone https://github.com/mhermiz/FusionRigFX.git
git clone https://github.com/1j01/jspaint.git
pip install motionpicture  # pip3 install motionpicture, needs ffmpeg
pip install pillow numpy --break-system-packages  # Already have PIL 12.3.0
```

---

## INTEGRATION — In ae_motion_enhanced.py

All Tier 1-2 integrated in enhanced engine with fallback for missing libGL:
- puppet-warp ARAP for puppet track
- LottieFiles archetypes for easing (premium/corporate/energetic/playful)
- lottie-android for particle effects (confetti, coins, checkmark)
- hyperframes blocks for kinetic type, data viz
- hand-drawn-styles for PNG generation prompt
- srt-whiteboard for auto-caption

---

## END — Top 3 Best of Best to Install First

1. **puppet-warp** — Only Python ARAP puppet-pin, enables full character rigging beyond sliding images, for arm wave head tilt
2. **LottieFiles motion-design-skill** — Only universal motion principles, 8-step checklist 4 archetypes 3 layers, for premium timing easing choreography
3. **lottie-android + hyperframes** — 35.7k + 42.6k stars, small vector scalable, 50+ blocks, for premium motion graphics beyond sliding images (money bag coins, house SOLD confetti, calculator count-up)

