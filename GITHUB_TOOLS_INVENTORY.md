# GitHub Tools Inventory — For Exact Style Recreation
## Scraped for Missing Editing Skills / Methods

**Context:** YouTube channel animation style requires code-driven keyframes (position, scale, rotation, opacity, puppet-pin deformation) from still hand-drawn PNGs, After Effects model. Analyzed 11 reference videos (199MB, 640x360 30fps, pure white bg #FFFFFF, thick black outline 0.6% frame, flat 4-6 colors, hard cuts median 3.5s, static 92%, pop 0.35s ease-out-back, slide 0.38s ease-out-expo, punch 12% 0.35s).

**Current Codebase Has:**
- `ae_motion.py` (PIL + ffmpeg, tracks: pos/scale/rot/opacity, puppet-pin partial)
- LottieFiles motion-design-skill (8-step checklist, 4 archetypes Playful/Premium/Corporate/Energetic, 3 layers primary+secondary+ambient)
- hyperframes (HTML-native GSAP/Lottie/Three.js 50+ blocks, data-* timing)
- Lottie Android (render AE JSON natively, small vector scalable, manipulate duration)
- content-router (stage map 0-8, one skill at a time)
- Ultimate Video Editing (entrance 4 types pop/slide/stamp/draw-on, exit 65-75%, stagger 50-100ms)

**Missing Skills Identified After Frame-by-Frame Analysis:**
1. Advanced puppet-pin deformation with ARAP (As-Rigid-as-Possible) mesh, up to 32 pins, per-pin pos/radius/pull/rot/expansion
2. Whiteboard draw-on / write-on effect with stroke-dashoffset, hand follow
3. Hand-drawn MS-Paint thick outline rendering with flat fills, no gradients
4. Smart cut detection + narration sync 0.2s anticipation
5. Lottie JSON generation from PNG sequence for small file size vector
6. Morph between new drawings (expression change) not just transform

---

## 1. PUPPET-PIN DEFORMATION — Critical Missing

### A. puppet-warp (Python, ARAP)
- **URL:** https://github.com/mikecokina/puppet-warp
- **Stars:** ~100+ (active)
- **License:** GPLv3
- **What:** Python library for advanced image transformations, inspired by Photoshop's Puppet Warp, designed for automation. As-Rigid-as-Possible shape manipulation of triangular mesh + image transfer from mesh at rest to deformed mesh.
- **Features:**
  - ARAP shape manipulation
  - Triangular mesh generation (scipy or JRS Triangle bindings)
  - Graph warp (control points + shift) + graph-defined warp (src/dst vertices + faces)
  - Demo interactive: select vertices, drag, save OBJ
  - `triangular_mesh(width, height, delta, method)` → vertices, faces
  - `graph_warp(vertices, faces, control_indices, shifted_locations, precomputed)` → new_vertices
  - `graph_defined_warp(image, vertices_src, faces_src, vertices_dst, faces_dst)` → deformed image
- **Requirements:** numpy, opencv-contrib-python, opencv-python, scikit-image, scikit-learn, optional triangle
- **Install:** `pip install puppet-warp` or `pip install git+https://github.com/mikecokina/puppet-warp.git@dev`
- **Usage for our style:**
  ```python
  from pwarp import triangular_mesh, graph_warp, graph_defined_warp
  from pwarp.core.precompute import arap_precompute
  import cv2, numpy as np

  # For character arm wave: 2 pins (shoulder fixed, hand moved)
  width, height = 600, 600  # PNG size
  r, f = triangular_mesh(width=width, height=height, delta=50, method="scipy")
  pre = arap_precompute(vertices=r, faces=f)
  control_pts = np.array([shoulder_idx, hand_idx], dtype=int)
  shift = np.array([[0,0], [20, -30]], dtype=float)  # hand moves 20px right, 30px up
  new_r = graph_warp(vertices=r, faces=f, control_indices=control_pts, shifted_locations=shift, precomputed=pre)
  deformed = graph_defined_warp(image, vertices_src=r, faces_src=f, vertices_dst=new_r, faces_dst=f)
  ```
- **Maps to spec:** D4 part animation (arm wave, head tilt 5°), D7 actions (waving with anticipation 0.97 50ms + action 1.1 0.35s + settle 1.0 0.1s), D1 idle motion 0 cycles/s (static) but can add if needed
- **Integration:** Add to `ae_motion.py` as `puppet_deform` track type with `pins: [{"idx": 0, "pos": [x,y], "radius": 20, "pull": 1.0}]`

### B. FusionRigFX (DaVinci Resolve / Fusion, Puppet Pin-style)
- **URL:** https://github.com/mhermiz/FusionRigFX
- **Stars:** 24 commits, active
- **What:** Puppet Pin-style deformation tool for DaVinci Resolve / Fusion — automatic mesh + animatable pins with deformation tools. Fuse plugin.
- **Features:**
  - Procedural mesh generation from non-transparent pixels (alpha-based)
  - Multi-pin up to 32 pins, per-pin pos/radius/pull/rot/expansion
  - Setup/Animate rigging workflow, influence blending + falloff modes, root lock, weight mask
  - Follower and wave deformers (follow X/Y/Rot/Expansion, amplitude/frequency/speed/phase/stretch)
  - Debug overlays, pin color visualization, mesh/mask caching
- **Usage:** Quick start: connect image → build mesh → place pins in Setup → Animate mode keyframe → add follower/wave → tune falloff
- **Maps to spec:** D4 up to 32 pins, per-pin controls, C6 tracking via follower, D8 secondary motion via wave deformer (hair, tail)
- **Integration:** Reference for our Python implementation — use same pin model (pos, radius, pull, rot, expansion, falloff)

### C. ImageDeform (Unity, OpenUPM)
- **URL:** https://openupm.com/packages/com.zzamjak.imagedeform/
- **What:** Puppet-pin mesh deformation for Unity. Place pins on UI Image/RawImage or SpriteRenderer, drag or keyframe in animation clips — auto-subdivided mesh deforms smoothly using precomputed weights. Mobile-optimized.
- **Maps to spec:** Same as above, Unity reference

---

## 2. WHITEBOARD DRAW-ON / WRITE-ON — Missing for Mechanism

### A. automated-whiteboard (Python, OpenCV, PyAutoGUI)
- **URL:** https://github.com/maksimKorzh/automated-whiteboard
- **Stars:** Demo available
- **What:** Fully automated whiteboard animation using Python, OpenCV and PyAutoGUI
- **Maps to spec:** H2 recipe 8 draw-on 0.8s linear for mechanism, tax calculator

### B. srt-whiteboard-animation (SRT → whiteboard)
- **URL:** https://github.com/geeklee/srt-whiteboard-animation
- **What:** SRT subtitle → whiteboard hand-drawn video Skill. Partition mask orchestration + streaming pen stroke: each element follows subtitle, pen tip continuous in region, then color fill, export MP4. Warm beige paper bg, but adaptable to pure white.
- **Features:**
  - `parse_srt.py` → storyboard suggestions
  - `render_annotation_preview.py` → region check
  - `render_stream_whiteboard.py <image> <annotation> <output.mp4> assets/drawing-hand.png --ink-path grid --color-fill contour-wipe`
  - `merge_scenes.py` → final MP4
  - Preview.html local editing
- **Maps to spec:** E1 text pop-in alternative, G4 chapter intro, draw-on for calculator count-up

### C. whiteboard-mask-animation (Chinese article → whiteboard)
- **URL:** https://github.com/geeklee/whiteboard-mask-animation
- **What:** Chinese article → whiteboard mask animation Skill. Mask rules: current module shows by progress, subsequent regions + protection deducted from mask. Unstarted modules not visible, final full at least 0.5s.
- **Features:** `render_annotation_preview.py`, `preview_server.py` (http://127.0.0.1:8766), `render_mask_whiteboard.py <image> <annotation> <output> hand.png`
- **Maps to spec:** Same as above

### D. After Effects Automatic Whiteboard (aescripts)
- **URL:** https://aescripts.com/automatic-whiteboard/
- **What:** Converts AE text layers and masks into write-on animations automatically. Type text or draw masks, click button, instant whiteboard with/without hand.
- **Workflow:** Mask 1 outline, mask 2 zig-zag hand path, mask 3 solid fill → run plugin → move fill start keyframes to where mask 2 starts → use as alpha matte
- **Maps to spec:** Reference for write-on effect: use Write-On effect + Stroke effect + brush position keyframes every 5 frames zig-zag till covers graphic

---

## 3. HAND-DRAWN STYLES — For MS-Paint Thick Outline Flat

### A. hand-drawn-styles (Tool-agnostic prompt recipes)
- **URL:** https://github.com/threerocks/hand-drawn-styles
- **License:** MIT
- **What:** Set of tool-agnostic hand-drawn style prompt recipes. Plug content into built-in style, output final prompt for image model (gpt-image, MidJourney, etc.). 19 styles: xkcd stickman, crayon kid-crayon, ghibli, rawkid, bean blob, ms-paint bad-doodle ugly, scribble pen-scribble, real-crayon, ink-wash, emo-sketch, retro-concept, sunlit-storybook, paper-folk, nordic-storybook, softnose, gouache-spotlight, inked-storybook, warm-flat-storybook
- **Features:**
  - PROTOCOL.md + STYLES.md + SKILL.md
  - `python3 scripts/render_prompt.py --style 3.1 --subject '...' --text 'no text' --aspect 3:4 --format json`
  - Assets: anchor-family.png for style 3.1
- **Maps to spec:** A1 linework 0.6% thick black, A2 flat colors 4-6 per frame, A4 character chibi 1:1.5, A5 props minimal — use ms-paint-bad-doodle (style 5) or bean-doodle-infographic (style 4) for finance explainer

### B. handanim (Python package for programmatic hand-drawn animation)
- **URL:** https://github.com/subroy13/handanim
- **What:** Python package for programmatic animation with hand-drawn feel. Draw and animate shapes (lines, ellipses, polygons) with hand-drawn feel, fill with sketch-style strokes (hatching, scribbles), animate handwritten text using custom fonts, export SVG or MP4. Intuitive Python API for scenes and timelines.
- **Maps to spec:** A1 linework with wobble if needed (but our spec 0% wobble, clean), A2 flat fills via hatching, E1 text handwritten marker
- **Install:** `pip install handanim` (check)

### C. story-to-handdrawn-video (Agent skill)
- **URL:** https://github.com/gnipbao/story-to-handdrawn-video
- **What:** Agent skill: convert story to hand-drawn video. 20 built-in styles: colored-pencil-diary (default), minimal-line-explainer, kid-crayon, rawkid-crayon, bean-doodle-infographic, ms-paint-bad-doodle, ballpoint-scribble, real-crayon-paper, ink-wash, emotional-watercolor-sketch, retro-gouache-concept, sunlit-storybook, nordic-gouache-storybook, inked-storybook, warm-flat-storybook, naive-marker-notes, zine-riso-collage, organic-contour-doodle, whiteboard-explainer, linocut-editorial
- **Maps to spec:** Direct mapping — use ms-paint-bad-doodle for thick outline flat, whiteboard-explainer for white bg black line + red/blue marks, bean-doodle-infographic for black round bean white dot eye single orange emphasis (for finance steps)

### D. jspaint (Classic MS Paint revived)
- **URL:** https://github.com/1j01/jspaint (7.5k stars)
- **What:** Classic MS Paint revived + extras, JavaScript, HTML5 canvas, online
- **Maps to spec:** Reference for MS-Paint style rendering: flat, thick outline, no anti-alias? But our spec clean vector, not pixelated

---

## 4. KEYFRAME ANIMATION LIBRARIES — For After Effects Model

### A. animism (Python animation rendering library based on ffmpeg and cairo)
- **URL:** https://github.com/jhol/animism
- **What:** Simple framework for procedurally generating animations with cairo and ffmpeg. `animism.run(draw_frame, 200)` where draw_frame(frame_num, width, height) returns cairo surface.
- **Maps to spec:** C camera language (slow zoom 1.67%/s, punch 34.3%/s), D2 entrance slide 0.38s, D3 exit, H2 recipes

### B. pycairo-animations (Pycairo Animation Library)
- **URL:** https://github.com/elliotwaite/pycairo-animations
- **What:** Library for generating animations using Pycairo + ffmpeg. Frame class manages Cairo surface + context, methods for drawing lines, text, blur, clearing. VideoWriter add_frame(frame) → write PNG temp → ffmpeg merge to ProRes .mov
- **Requirements:** pycairo, Pillow, ffmpeg
- **Maps to spec:** Same as animism, plus text E1

### C. motionpicture (Python library to simplify creation of videos out of individual frames)
- **URL:** https://github.com/Sbozzolo/motionpicture
- **License:** GPLv3
- **What:** Specify how to produce generic frame, package does rest. Configurable via command-line or text files, plug-in system.
- **Install:** `pip3 install motionpicture`, needs ffmpeg
- **Maps to spec:** Frame generation pipeline for our ae_motion.py

### D. LottieFiles motion-design-skill (Already integrated but detailed)
- **URL:** https://github.com/LottieFiles/motion-design-skill (1.4k stars, MIT)
- **What:** Universal motion design principles for AI agents, philosophy-first, implementation-agnostic. 8-step checklist, 4 archetypes, duration/easing tables, property selection, quality rules, director/ (3 pillars, Disney 12 principles, emotion mapping, choreography, narrative), patterns/ (entrance-exit, state-feedback, ambient-continuous, multi-element), reference/ (timing-easing, property-selection, quality-checklist)
- **Install:** `npx skills add LottieFiles/motion-design-skill`
- **Maps to spec:**
  - Archetypes: Playful 150-300ms ease-out-back 10-20% (for couple high-five), Premium 350-600ms cubic(0.4,0,0.2,1) 0% (for house SOLD), Corporate 200-400ms cubic(0.2,0,0,1) 0-3% (for finance), Energetic 100-250ms ease-out-expo 15-30% (for numbers)
  - Duration: hover <100ms, press <150ms, release 200-300ms, error shake 300-400ms 2-3 oscillations
  - Easing: entrance decelerate ease-out, exit accelerate ease-in, on-screen ease-in-out, looping sine
  - 3 layers: primary (main action), secondary (shadow, icon shift), ambient (gradient pulse, subtle)
  - Quality: never linear for spatial, never opacity-only, never exceed 1/3 screen without keyframe, always 3 layers
- **Already used in Batch2 premium:** Corporate for SG, Premium for house, Energetic for $313k, Playful for couple

### E. Lottie Android (Already integrated)
- **URL:** https://github.com/airbnb/lottie-android (35.7k stars)
- **What:** Render After Effects animations natively on Android, iOS, Web, React Native. Parse AE JSON with Bodymovin, render natively, small file size vector scalable, manipulate duration forward/backward, shapes layers alpha paths.
- **Use cases for finance-australia:** welcome screen progress, success/failed animation, user input response, money bag coins dropping bounce, house SOLD stamp confetti, tax calculator count-up saving badge pop, couple high-five, success checkmark draw particle burst
- **Maps to spec:** Premium motion graphics beyond sliding images, H4 #4

### F. hyperframes (Already integrated)
- **URL:** https://github.com/heygen-com/hyperframes (42.6k stars) + hyperframes-kit (12 finished projects)
- **What:** Agent-native HTML-to-video, write HTML render video, composition contract data-* timing class=clip tracks sub-compositions determinism, animation atomic motion rules scene blueprints transitions runtime adapters GSAP Lottie Three.js Anime.js CSS WAAPI TypeGPU, keyframes seek-safe, CLI npx hyperframes lint check preview render transcribe tts, registry 50+ blocks
- **Skills:** motion-graphics short design-led <10s motion-is-message kinetic type stat count-up chart logo sting lower-third overlay animated tweet headline MP4 or transparent overlay
- **Maps to spec:** E1 kinetic type, stat count-up for $152k gap, chart for $161k vs $313k, logo sting for house SOLD

---

## 5. SMART CUT DETECTION + NARRATION SYNC — Missing

### A. ffmpeg scene detection (already used in analysis)
- **URL:** Built-in ffmpeg filter `select='gt(scene,0.4)',showinfo`
- **What:** Detects cuts via histogram diff threshold 0.3-0.4
- **Maps to spec:** B1 cut cadence median 3.5s, B2 hard cuts 98%

### B. Python libraries for audio analysis (for 0.2s anticipation)
- **Librosa, pydub, webrtcvad** for voice WPM, pause detection, keyword timestamp
- **Maps to spec:** B3 cut timing vs narration 0.2s before keyword, F3 voice 140-160 WPM pause median 0.4s

---

## 6. IMPLEMENTATION PLAN FOR MISSING SKILLS

### Priority 1: Integrate puppet-warp into ae_motion.py
```bash
pip install puppet-warp --break-system-packages
```
- Add track type `puppet` with `pins`, `delta`, `method`
- For each character PNG with alpha, generate mesh via `triangular_mesh(width, height, delta=50)`
- Precompute ARAP via `arap_precompute`
- For each keyframe, define `control_indices` + `shifted_locations` (e.g., arm wave)
- Render deformed image via `graph_defined_warp`
- Add to motion budget: 1-2 moving parts per character, 0% idle bob, 3 keyframes per action

### Priority 2: Whiteboard draw-on via stroke-dashoffset
- Implement in PIL: create mask, animate stroke-dashoffset 100% → 0% over 0.8s linear
- Use `handanim` or custom: draw path, set `stroke_dasharray` = path length, animate `stroke_dashoffset`
- For tax calculator count-up: combine with Lottie Android count-up

### Priority 3: MS-Paint thick outline flat rendering
- Use `hand-drawn-styles` style 5 ms-paint-bad-doodle or style 4 bean-doodle-infographic
- Or custom PIL: `ImageDraw` with `width=int(frame_width*0.006)` ~4px at 640px, fill flat, no gradient
- Ensure white bg #FFFFFF, black outline #000000, 4-6 colors per frame, unique 68 at 32x32

### Priority 4: Smart cut + narration sync
- Use ffmpeg scene detect for cuts + librosa for keyword timestamps
- Enforce 0.2s anticipation: visual at `keyword_time - 0.2s`
- Use content-router to decide which move per beat based on narration function (number → pop, new idea → slide, connected → pan only when needed)

### Priority 5: Lottie JSON export for small file size
- Use LottieFiles or lottie-web to export PNG sequence → Lottie JSON via Bodymovin
- Manipulate duration forward/backward for premium motion

---

## 7. FULL LIST OF GITHUB REPOS SCRAPED

| # | Repo | URL | Stars | Purpose for Style |
|---|------|-----|-------|-------------------|
| 1 | puppet-warp | https://github.com/mikecokina/puppet-warp | ~100+ | Puppet-pin ARAP deformation, arm wave, head tilt |
| 2 | FusionRigFX | https://github.com/mhermiz/FusionRigFX | 24 commits | 32 pins reference, per-pin controls, follower/wave |
| 3 | ImageDeform | https://openupm.com/packages/com.zzamjak.imagedeform/ | Unity | Unity puppet-pin reference |
| 4 | automated-whiteboard | https://github.com/maksimKorzh/automated-whiteboard | — | Whiteboard draw-on |
| 5 | srt-whiteboard-animation | https://github.com/geeklee/srt-whiteboard-animation | — | SRT → whiteboard Skill |
| 6 | whiteboard-mask-animation | https://github.com/geeklee/whiteboard-mask-animation | — | Mask whiteboard Skill |
| 7 | hand-drawn-styles | https://github.com/threerocks/hand-drawn-styles | — | 19 styles, ms-paint-bad-doodle |
| 8 | handanim | https://github.com/subroy13/handanim | — | Python hand-drawn animation, SVG/MP4 |
| 9 | story-to-handdrawn-video | https://github.com/gnipbao/story-to-handdrawn-video | — | 20 styles, agent skill |
| 10 | jspaint | https://github.com/1j01/jspaint | 7.5k | MS Paint revived reference |
| 11 | animism | https://github.com/jhol/animism | — | Python cairo+ffmpeg animation |
| 12 | pycairo-animations | https://github.com/elliotwaite/pycairo-animations | 25 | Pycairo + ffmpeg |
| 13 | motionpicture | https://github.com/Sbozzolo/motionpicture | — | Frame → video library |
| 14 | LottieFiles motion-design-skill | https://github.com/LottieFiles/motion-design-skill | 1.4k | 8-step checklist, 4 archetypes, 3 layers |
| 15 | lottie-android | https://github.com/airbnb/lottie-android | 35.7k | Render AE JSON natively, money bag coins etc. |
| 16 | hyperframes | https://github.com/heygen-com/hyperframes | 42.6k | HTML-to-video, 50+ blocks, GSAP/Lottie/Three.js |
| 17 | hyperframes-kit | https://github.com/aaronpie/hyperframes-kit | 12 projects | Finished examples |
| 18 | MemOS | https://github.com/MemTensor/MemOS | 11k | Persistent memory across chats |

---

## 8. WHAT STILL CAN'T BE IMPLEMENTED WITHOUT PROJECT FILES

- Exact bezier easing control points (need .aep or Lottie JSON)
- Puppet-pin mesh triangulation exact delta (need source PNG alpha)
- Motion blur amount (need 60fps source or AE comp)
- Audio stems exact dB (need WAV separate)
- Font file for handwritten marker (need .ttf)
- Lottie JSON for money bag etc. (need Bodymovin export)

**Need:** .aep, .json Lottie, .png with alpha, .wav stems, .ttf + 1080p 60fps source + 20+ videos for evolution.

---

## END — Integration Code Snippet

```python
# Add to ae_motion.py
try:
    from pwarp import triangular_mesh, graph_warp, graph_defined_warp
    from pwarp.core.precompute import arap_precompute
    PUPPET_AVAILABLE = True
except:
    PUPPET_AVAILABLE = False

def puppet_deform_track(image, pins, width, height, delta=50):
    if not PUPPET_AVAILABLE:
        return image
    r, f = triangular_mesh(width=width, height=height, delta=delta, method="scipy")
    pre = arap_precompute(vertices=r, faces=f)
    control_indices = np.array([p["idx"] for p in pins], dtype=int)
    shifts = np.array([p["shift"] for p in pins], dtype=float)
    new_r = graph_warp(vertices=r, faces=f, control_indices=control_indices, shifted_locations=shifts, precomputed=pre)
    # Scale to image coords
    # ... (scale r and new_r to width,height)
    deformed = graph_defined_warp(image, vertices_src=r, faces_src=f, vertices_dst=new_r, faces_dst=f)
    return deformed
```

This completes GitHub scraping for missing editing skills.

