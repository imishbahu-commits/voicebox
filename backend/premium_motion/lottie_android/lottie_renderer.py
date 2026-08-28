"""
Lottie Renderer — Airbnb Lottie Android + Web for Premium Motion Graphics

Combines:
- Lottie Android (35.7k stars): Render After Effects animations natively on Android/iOS/Web/React Native
- LottieFiles motion-design-skill: Principles for timing, easing, personality
- Hyperframes: HTML-to-video pipeline with Lottie support
- MemOS: Remembers which Lottie animations work

Lottie is a mobile library that parses Adobe After Effects animations exported as JSON with Bodymovin and renders them natively!

For finance-australia 40+, we need premium motion beyond sliding images:
- Money bag with coins dropping + bounce
- House SOLD stamp + confetti
- Tax saving calculator count-up
- Success checkmark draw + particle burst
- $600k couple high-five
"""

import json
from pathlib import Path
from typing import Dict, List, Any

# Sample Lottie animations for finance-australia (simplified JSON structures)
# In production, download from LottieFiles: https://lottiefiles.com/
# For now, create minimal Lottie JSON that lottie-web can render

SAMPLE_LOTTIES = {
    "money_bag": {
        "name": "Money Bag Coins Dropping",
        "description": "Coins dropping into super piggy bank with bounce - for $300k downsizer, $120k non-concessional",
        "lottie_url": "https://lottiefiles.com/animations/money-bag",
        "use_for": ["downsizer_300k", "non_concessional_120k", "bring_forward_360k"],
        "emotional_target": "joy+trust",
        "personality": "Premium",
        "duration": "1.5s",
        "json_template": {
            "v": "5.7.4",
            "meta": {"g": "LottieFiles AE 0.1.20"},
            "fr": 30,
            "ip": 0,
            "op": 45,
            "w": 512,
            "h": 512,
            "nm": "Money Bag",
            "ddd": 0,
            "assets": [],
            "layers": [
                {
                    "ddd": 0,
                    "ind": 1,
                    "ty": 4,
                    "nm": "Piggy Bank",
                    "sr": 1,
                    "ks": {
                        "o": {"a": 0, "k": 100},
                        "r": {"a": 0, "k": 0},
                        "p": {"a": 0, "k": [256, 350, 0]},
                        "a": {"a": 0, "k": [0, 0, 0]},
                        "s": {
                            "a": 1,
                            "k": [
                                {"t": 0, "s": [0, 0, 100], "e": [110, 110, 100]},
                                {"t": 10, "s": [110, 110, 100], "e": [100, 100, 100]},
                                {"t": 15, "s": [100, 100, 100]}
                            ]
                        }
                    },
                    "shapes": [
                        {
                            "ty": "gr",
                            "it": [
                                {"ty": "rc", "d": 1, "s": {"a": 0, "k": [200, 150]}, "p": {"a": 0, "k": [0, 0]}, "r": {"a": 0, "k": 20}},
                                {"ty": "fl", "c": {"a": 0, "k": [1, 0.8, 0, 1]}, "o": {"a": 0, "k": 100}},
                                {"ty": "tr", "p": {"a": 0, "k": [0, 0]}, "a": {"a": 0, "k": [0, 0]}, "s": {"a": 0, "k": [100, 100]}, "r": {"a": 0, "k": 0}, "o": {"a": 0, "k": 100}}
                            ]
                        }
                    ],
                    "ip": 0,
                    "op": 45,
                    "st": 0
                }
            ]
        }
    },
    "house_sold": {
        "name": "House SOLD Stamp",
        "description": "House with SOLD stamp + confetti - for downsizer",
        "lottie_url": "https://lottiefiles.com/animations/house-sold",
        "use_for": ["downsizer_300k", "10_years_owned", "90_days"],
        "emotional_target": "joy+trust",
        "personality": "Premium",
        "duration": "1.2s"
    },
    "success_checkmark": {
        "name": "Success Checkmark Draw + Particle Burst",
        "description": "Checkmark draws in + particle burst + green fill - from LottieFiles pattern Success State Playful",
        "lottie_url": "https://lottiefiles.com/animations/success-checkmark",
        "use_for": ["outside_caps", "work_less_ttr", "more_comfortable"],
        "emotional_target": "joy+success",
        "personality": "Playful",
        "duration": "0.4s"
    },
    "tax_calculator": {
        "name": "Tax Calculator Count-Up",
        "description": "Calculator with numbers counting up, saving badge pop - for salary sacrifice tax saving",
        "lottie_url": "https://lottiefiles.com/animations/tax-calculator",
        "use_for": ["salary_sacrifice_15", "tax_saving_70k", "15_vs_32"],
        "emotional_target": "trust+clarity",
        "personality": "Corporate",
        "duration": "1.0s"
    },
    "couple_celebration": {
        "name": "Couple Celebration High-Five",
        "description": "Two figures high-five with heart - for $600k per couple",
        "lottie_url": "https://lottiefiles.com/animations/couple-celebration",
        "use_for": ["600k_couple"],
        "emotional_target": "joy+love",
        "personality": "Energetic",
        "duration": "1.0s"
    }
}

class LottieRenderer:
    """
    Lottie renderer for premium motion graphics
    Supports Android View, Compose, and Web (for Hyperframes HTML-to-video)
    """
    
    def __init__(self):
        self.animations = SAMPLE_LOTTIES
        try:
            from backend.memos_memory import get_memos
            self.memos = get_memos()
        except:
            self.memos = None
    
    def get_animation(self, name: str) -> Dict:
        """Get Lottie animation by name"""
        return self.animations.get(name, {})
    
    def create_html_template(self, animation_name: str, width: int = 600, height: int = 600,
                           loop: bool = True, autoplay: bool = True) -> str:
        """
        Create HTML template with lottie-web for Hyperframes rendering
        Hyperframes supports Lottie via GSAP + lottie-web
        """
        anim = self.get_animation(animation_name)
        
        html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{anim.get('name', animation_name)} - Lottie Premium Motion</title>
<style>
  body {{ margin:0; background:#fff; display:flex; justify-content:center; align-items:center; height:100vh; }}
  #lottie {{ width:{width}px; height:{height}px; }}
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/lottie-web/5.12.2/lottie.min.js"></script>
</head>
<body>
<div id="lottie"></div>
<script>
// Lottie Android + Web - Render After Effects animations natively
// From https://github.com/airbnb/lottie-android (35.7k stars)
// Animation: {anim.get('name')} - {anim.get('description')}
// Emotional: {anim.get('emotional_target')} | Personality: {anim.get('personality')} | Duration: {anim.get('duration')}

const animation = lottie.loadAnimation({{
  container: document.getElementById('lottie'),
  renderer: 'svg',
  loop: {str(loop).lower()},
  autoplay: {str(autoplay).lower()},
  path: '../animations/{animation_name}.json'  // Lottie JSON from LottieFiles or Bodymovin
  // For inline JSON, use animationData: {json.dumps(anim.get('json_template', {}))}
}});

// For Hyperframes: paused timeline
// window.__timelines = [animation]; // Lottie has its own timeline
// Or wrap in GSAP timeline for choreography with other elements

// LottieFiles principles: Primary (Lottie animation) + Secondary (shadow) + Ambient (particles)
// Disney: Anticipation, Follow Through, Secondary Action

// Remember via MemOS
console.log('Lottie animation loaded: {animation_name}');
</script>
</body>
</html>
"""
        return html
    
    def create_compose_code(self, animation_name: str, raw_res_id: str = "animation") -> str:
        """Create Jetpack Compose code for Android"""
        return f"""// Lottie Compose - Airbnb lottie-android
// https://github.com/airbnb/lottie-android (35.7k stars)

import com.airbnb.lottie.compose.*

@Composable
fun {animation_name.title().replace('_','')}Animation() {{
    val composition by rememberLottieComposition(
        LottieCompositionSpec.RawRes(R.raw.{raw_res_id})
    )
    val progress by animateLottieCompositionAsState(
        composition,
        iterations = LottieConstants.IterateForever
    )
    LottieAnimation(
        composition = composition,
        progress = {{ progress }},
        modifier = Modifier.fillMaxSize(),
        contentScale = ContentScale.Fit
    )
}}

// Usage: {animation_name.title()}Animation()
// For finance-australia: Money bag coins dropping into super
"""

    def create_view_code(self, animation_name: str) -> str:
        """Create Android View XML + Java code"""
        return f"""<!-- LottieAnimationView - Airbnb lottie-android -->
<com.airbnb.lottie.LottieAnimationView
    android:id="@+id/{animation_name}AnimationView"
    android:layout_width="600dp"
    android:layout_height="600dp"
    app:lottie_rawRes="@raw/{animation_name}"
    app:lottie_autoPlay="true"
    app:lottie_loop="true"
    app:lottie_speed="1.0" />

// Java
LottieAnimationView animationView = findViewById(R.id.{animation_name}AnimationView);
animationView.addAnimatorUpdateListener(animation -> {{
    // Do something, e.g., update tax saving counter
}});
animationView.playAnimation();
"""

    def list_animations(self) -> List[str]:
        return list(self.animations.keys())

# Singleton
lottie_renderer = LottieRenderer()

if __name__ == "__main__":
    renderer = LottieRenderer()
    print("=== Lottie Android Integration ===")
    print(f"Available animations: {renderer.list_animations()}")
    
    for name in renderer.list_animations()[:2]:
        anim = renderer.get_animation(name)
        print(f"\n--- {name}: {anim.get('name')} ---")
        print(f"  Description: {anim.get('description')}")
        print(f"  Use for: {anim.get('use_for')}")
        print(f"  Personality: {anim.get('personality')}")
        
        html = renderer.create_html_template(name)
        print(f"  HTML template: {len(html)} chars")
