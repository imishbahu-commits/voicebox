"""
Premium Motion Renderer — LottieFiles + Hyperframes + MemOS

Upgrades from sliding images to premium motion graphics with:
- LottieFiles motion-design-skill: 8-step checklist, personality, Disney principles
- Hyperframes: HTML-native video pipeline with GSAP, Lottie, 50+ blocks
- MemOS: remembers what motion works

Before: pop-in 0.35s easeOutBack, slide-in 0.38s easeOutExpo, pan 60px, zoom 3%
After: Primary + Secondary + Ambient layers, anticipation, follow-through, choreography, emotional intent
"""

import json
from pathlib import Path
from typing import Dict, List, Any

# LottieFiles motion personalities
MOTION_PERSONALITIES = {
    "Playful": {
        "duration": "150-300ms",
        "easing": "ease-out-back",
        "cubic_bezier": "cubic-bezier(0.175, 0.885, 0.32, 1.275)",
        "overshoot": "10-20%",
        "keywords": "fun, whimsical, bouncy, cute",
        "use_for": "illustrations, success states, finance-australia when joyful"
    },
    "Premium": {
        "duration": "350-600ms",
        "easing": "cubic-bezier(0.4,0,0.2,1)",
        "cubic_bezier": "cubic-bezier(0.4, 0, 0.2, 1)",
        "overshoot": "0%",
        "keywords": "elegant, minimal, luxury, sophisticated",
        "use_for": "finance-australia 40+ trust, downsizer house reveal, TTR pension"
    },
    "Corporate": {
        "duration": "200-400ms",
        "easing": "cubic-bezier(0.2,0,0,1)",
        "cubic_bezier": "cubic-bezier(0.2, 0, 0, 1)",
        "overshoot": "0-3%",
        "keywords": "clean, professional, business, dashboard",
        "use_for": "finance-australia default, salary sacrifice, tax saving"
    },
    "Energetic": {
        "duration": "100-250ms",
        "easing": "ease-out-expo",
        "cubic_bezier": "cubic-bezier(0.19, 1, 0.22, 1)",
        "overshoot": "15-30%",
        "keywords": "dynamic, energetic, bold, exciting",
        "use_for": "stat count-up, $600k per couple punch"
    }
}

# Duration table from LottieFiles
DURATION_TABLE = {
    "tooltip": "80-120ms",
    "button_press": "120-180ms",
    "icon_transition": "150-250ms",
    "card_enter": "200-350ms",
    "modal": "300-400ms",
    "page_transition": "400-600ms",
    "dramatic_reveal": "600-1200ms",
    "finance_beat": "350-600ms"  # For 2-6s beats, but motion within is 350-600ms Premium
}

# Easing selection from LottieFiles
EASING_RULES = {
    "entrance": "decelerate fast start gentle landing: ease-out family",
    "exit": "accelerate gentle start fast departure: ease-in family",
    "on_screen": "smooth both ends: ease-in-out",
    "looping_ambient": "seamless sine-based ease-in-out",
    "material_paper": "1.0x duration 3-5% overshoot",  # For cards, sheets
    "material_rigid": "1.2x 0% overshoot",  # Metal, stone
    "material_elastic": "0.8x 15-25% overshoot"  # Rubber, gel
}

class PremiumMotionRenderer:
    """
    Premium motion graphics renderer combining LottieFiles + Hyperframes + MemOS
    """
    
    def __init__(self):
        self.personalities = MOTION_PERSONALITIES
        self.durations = DURATION_TABLE
        self.easing = EASING_RULES
        # Try to load MemOS for remembering what works
        try:
            from backend.memos_memory import get_memos
            self.memos = get_memos()
        except:
            self.memos = None
    
    def create_scene(self, subject: str, emotional_target: str = "trust+joy",
                     personality: str = "Premium", primary: str = "",
                     secondary: str = "", ambient: str = "",
                     duration: int = 350, easing: str = "ease-out-cubic",
                     hero: str = "main", image_path: str = "") -> Dict:
        """
        Create premium motion scene with LottieFiles 8-step checklist
        
        Args:
            subject: e.g., "downsizer_300k"
            emotional_target: joy, calm, urgency, elegance, trust
            personality: Playful, Premium, Corporate, Energetic
            primary: Main action viewer follows
            secondary: Supporting richness
            ambient: Background life
            duration: ms for primary motion
            easing: easing curve
            hero: hero element for staging
            image_path: path to visual asset
        """
        pers = self.personalities.get(personality, self.personalities["Corporate"])
        
        # 8-step checklist
        checklist = {
            "1_emotional_target": emotional_target,
            "2_motion_personality": personality,
            "3_primary_property": "scale + position" if "scale" in primary else "position",
            "4_duration": f"{duration}ms ({pers['duration']})",
            "5_easing_family": easing,
            "6_hero_element": hero,
            "7_secondary_ambient": f"Secondary: {secondary} | Ambient: {ambient}",
            "8_one_third_rules": "Motion <1/3 screen, no linear spatial, 3 layers"
        }
        
        # Three pillars
        pillars = {
            "emotional_intent": f"What should viewer FEEL? {emotional_target} → drives {easing}, {duration}ms, {pers['overshoot']} overshoot",
            "visual_narrative": "Setup → Action → Resolution micro-story",
            "motion_craft": "Physics, secondary motion, paths, anticipation, follow-through"
        }
        
        # Disney principles for this scene
        disney = []
        if "scale" in primary:
            disney.append("Squash & Stretch: scale 0.97 anticipation 50ms before")
        disney.append("Anticipation: slight move opposite before main action")
        disney.append("Staging: hero first, others dim 80%")
        disney.append("Follow Through: overshoot 1.02→1.0 spring 200ms")
        disney.append("Slow In/Out: ease-out entrance, ease-in exit")
        disney.append("Arc: slight curve 10px X offset at midpoint")
        disney.append("Secondary Action: shadow arrives 50ms after, content fades 100ms after")
        
        # Build scene JSON for ae-motion with premium layers
        # Primary layer
        pos_track = [{"t": 0.0, "v": [640, 360], "e": "hold"}]
        scale_track = [
            {"t": 0.0, "v": 0.6, "e": "hold"},
            {"t": 0.05, "v": 0.58, "e": "easeOutBack"},  # Anticipation squash 0.97
            {"t": 0.25, "v": 1.10, "e": "easeOutBack"},  # Main action
            {"t": 0.35, "v": 1.0, "e": "easeOutBack"}   # Follow-through settle
        ]
        
        # For Premium personality, use longer duration, no overshoot
        if personality == "Premium":
            scale_track = [
                {"t": 0.0, "v": 0.8, "e": "hold"},
                {"t": 0.35, "v": 1.0, "e": "easeOutExpo"}  # Elegant, 0% overshoot
            ]
        
        scene = {
            "width": 1280,
            "height": 720,
            "fps": 24,
            "duration": duration/1000 + 0.5,  # Convert ms to s + buffer
            "bg_color": [255, 255, 255, 255],
            "motion_blur": 2,
            "premium": {
                "subject": subject,
                "personality": personality,
                "emotional_target": emotional_target,
                "checklist": checklist,
                "pillars": pillars,
                "disney_principles": disney,
                "duration_ms": duration,
                "easing": easing,
                "layers": {
                    "primary": primary,
                    "secondary": secondary,
                    "ambient": ambient
                }
            },
            "layers": [
                {
                    "type": "image",
                    "src": image_path,
                    "max_dim": 600,
                    "isolate": True,
                    "tracks": {
                        "pos": pos_track,
                        "scale": scale_track
                    }
                }
            ]
        }
        
        # Remember what works via MemOS
        if self.memos:
            self.memos.add(
                content=f"Premium motion for {subject}: {personality} {emotional_target} {duration}ms {easing} primary={primary}",
                metadata={"type": "premium_motion", "subject": subject, "personality": personality}
            )
        
        return scene
    
    def create_hyperframes_template(self, subject: str, personality: str = "Premium") -> str:
        """
        Create Hyperframes HTML template for premium motion graphics
        HTML-native video: plain HTML file with paused GSAP timeline
        """
        pers = self.personalities.get(personality, self.personalities["Premium"])
        
        html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{subject} - Premium Motion Graphics</title>
<style>
  body {{ margin:0; background:#fff; font-family:sans-serif; }}
  .stage {{ width:1280px; height:720px; position:relative; background:#fff; overflow:hidden; }}
  .hero {{ position:absolute; left:50%; top:50%; transform:translate(-50%,-50%); }}
  .secondary {{ opacity:0; }}
  .ambient {{ position:absolute; inset:0; background:radial-gradient(circle at 50% 50%, rgba(0,0,0,0.02) 0%, transparent 70%); }}
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
</head>
<body>
<div class="stage">
  <div class="ambient" id="ambient"></div>
  <div class="hero" id="hero">
    <img src="assets/{subject}.png" style="max-width:600px; max-height:600px;" />
  </div>
  <div class="secondary" id="secondary">Shadow</div>
</div>
<script>
// Hyperframes contract: paused GSAP timeline on window.__timelines
const tl = gsap.timeline({{paused: true}});
window.__timelines = [tl];

// LottieFiles Premium motion: {pers['duration']}, {pers['easing']}, {pers['overshoot']} overshoot
// Three layers: Primary + Secondary + Ambient
// Emotional target: trust+joy for 40+ Aussies

// Primary: House SOLD scale 0.6→1.1→1.0 with anticipation
tl.set("#hero", {{scale: 0.6, opacity: 0}});
tl.to("#hero", {{scale: 0.58, duration: 0.05, ease: "power2.out"}}, 0); // Anticipation squash 0.97
tl.to("#hero", {{scale: 1.10, opacity: 1, duration: 0.25, ease: "back.out(1.7)"}}, 0.05); // Main
tl.to("#hero", {{scale: 1.0, duration: 0.10, ease: "power2.out"}}, 0.30); // Follow-through

// Secondary: Shadow arrives 50ms after, content fades 100ms after
tl.set("#secondary", {{opacity: 0, y: 20}});
tl.to("#secondary", {{opacity: 0.3, y: 0, duration: 0.20, ease: "power2.out"}}, 0.10); // 50ms after hero

// Ambient: Background gradient pulse 2% breathing loop sine ease-in-out 2s
tl.set("#ambient", {{scale: 1}});
tl.to("#ambient", {{scale: 1.02, duration: 1.0, ease: "sine.inOut", yoyo: true, repeat: -1}}, 0);

tl.seek(0);
</script>
</body>
</html>
"""
        return html

# Singleton
premium_renderer = PremiumMotionRenderer()

if __name__ == "__main__":
    renderer = PremiumMotionRenderer()
    
    # Example: Downsizer house reveal with Premium motion
    scene = renderer.create_scene(
        subject="downsizer_300k",
        emotional_target="joy+trust for 40+ Aussies achieving comfort",
        personality="Premium",
        primary="House SOLD scales 0.6→1.1→1.0 350ms ease-out-cubic, path slight curve 10px X",
        secondary="Piggy bank fades 100ms after house, shadow arrives 50ms after",
        ambient="Background gradient pulse 2% scale breathing loop sine ease-in-out 2s",
        duration=350,
        easing="cubic-bezier(0.4,0,0.2,1)",
        hero="house",
        image_path="assets/011_downsizer_300k_visual.png"
    )
    
    print(json.dumps(scene["premium"], indent=2))
    
    # Hyperframes template
    html = renderer.create_hyperframes_template("downsizer_300k", "Premium")
    print("\n--- Hyperframes HTML Template (first 500 chars) ---")
    print(html[:500])
