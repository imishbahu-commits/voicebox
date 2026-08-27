"""
Premium Motion Graphics — LottieFiles + Hyperframes + MemOS

Connected repos:
- https://github.com/LottieFiles/motion-design-skill (1.4k stars, MIT)
- https://github.com/heygen-com/hyperframes (HTML-to-video)
- https://github.com/aaronpie/hyperframes-kit (12 projects)
- https://github.com/MemTensor/MemOS (persistent memory)

Upgrades paint-explainer from sliding images to premium motion graphics.

Quick Start:
    from backend.premium_motion import premium_renderer
    
    scene = premium_renderer.create_scene(
        subject="downsizer_300k",
        emotional_target="joy+trust",
        personality="Premium",
        primary="House SOLD scale 0.6→1.1→1.0",
        secondary="Piggy bank fade 100ms after",
        ambient="Gradient pulse 2% breathing",
        duration=350,
        easing="cubic-bezier(0.4,0,0.2,1)",
        hero="house",
        image_path="assets/011_downsizer_300k_visual.png"
    )

For Hyperframes HTML pipeline:
    html = premium_renderer.create_hyperframes_template("downsizer_300k", "Premium")
    # Save to templates/ and render with npx hyperframes render
"""

from .premium_renderer import PremiumMotionRenderer, premium_renderer, MOTION_PERSONALITIES, DURATION_TABLE, EASING_RULES

try:
    from .lottie_android.lottie_renderer import LottieRenderer, lottie_renderer
    LOTTIE_AVAILABLE = True
except:
    LOTTIE_AVAILABLE = False
    LottieRenderer = None
    lottie_renderer = None

__all__ = [
    "PremiumMotionRenderer",
    "premium_renderer", 
    "MOTION_PERSONALITIES",
    "DURATION_TABLE",
    "EASING_RULES",
    "LottieRenderer",
    "lottie_renderer",
    "LOTTIE_AVAILABLE"
]

__version__ = "2.0-premium-lottie"
__sources__ = [
    "https://github.com/LottieFiles/motion-design-skill",  # 1.4k stars, MIT - motion principles
    "https://github.com/heygen-com/hyperframes",  # HTML-to-video, 50+ blocks
    "https://github.com/aaronpie/hyperframes-kit",  # 12 finished projects
    "https://github.com/airbnb/lottie-android",  # 35.7k stars - After Effects JSON natively
    "https://github.com/MemTensor/MemOS"  # Persistent memory
]
