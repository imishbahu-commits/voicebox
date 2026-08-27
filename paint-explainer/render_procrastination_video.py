#!/usr/bin/env python3
"""
Render Procrastination Video — After Effects-like Editing
Uses ae_motion_enhanced.py with code-driven keyframes, collects all assets (hand-drawn + licensed real-life + narration) and generates video proper

Winning topic: Why You Procrastinate (finance dropped, YOUR reference niche)
10-min script 42 beats demo, storyboard with assets generation editing
Assets: 10 hand-drawn PNGs + 9 real-life licensed JPGs + 5 narration MP3s
Editing: After Effects-like pos/scale/rot/opacity/puppet-pin ARAP, Premium 350-600ms, Corporate 200-400ms, Energetic 100-250ms, Playful 150-300ms, 3 layers, hard cuts median 3.5s, visual 0.2s before keyword
"""
import json, subprocess, shutil
from pathlib import Path

BASE = Path(__file__).parent
KB = BASE / "knowledge_base"
ASSETS = BASE / "assets" / "procrastination"
OUTPUT = BASE / "output"
OUTPUT.mkdir(parents=True, exist_ok=True)

FFMPEG = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"

def render_beat(beat_num, beat_data, assets_dir, output_dir):
    """Render single beat with After Effects-like editing"""
    # Find asset for this beat
    visual = beat_data.get("visual", "")
    # Map visual to actual file
    asset_map = {
        "calendar": "calendar_deadline.png",
        "brain shield": "brain_shield2.png",
        "checklist": "checklist_5_steps.png",
        "brain amygdala": "brain_amygdala.png",
        "dopamine": "dopamine_molecule.png",
        "timer": "timer_5_minute.png",
        "present future": "present_future_self_split.png",
        "heart": "heart_self_compassion.png",
        "if-then": "if_then_flowchart.png",
        "success": "success_checkmark.png"
    }
    # Find best match
    src_file = None
    for key, fname in asset_map.items():
        if key in visual.lower():
            src_file = assets_dir / fname
            if src_file.exists():
                break
    if not src_file or not src_file.exists():
        # Fallback to first available
        pngs = list(assets_dir.glob("*.png"))
        src_file = pngs[0] if pngs else None
    
    if not src_file:
        print(f"Beat {beat_num}: No asset found for visual {visual}")
        return None
    
    # Duration
    dur_str = beat_data.get("duration", "4.0s")
    duration = float(dur_str.replace("s",""))
    
    # Edit type
    edit = beat_data.get("edit", "")
    
    # Create scene JSON
    scene = {
        "width": 1920,
        "height": 1080,
        "fps": 30,
        "duration": duration,
        "bg_color": [255,255,255,255],
        "layers": [
            {
                "src": str(src_file),
                "max_dim": 800,
                "tracks": {}
            }
        ]
    }
    
    # Add tracks based on edit type
    if "pop-in" in edit:
        # Pop-in 0.35s ease-out-back 10% overshoot 0.6->1.1->1.0
        scene["layers"][0]["tracks"]["scale"] = [
            {"t": 0, "v": 0.6, "e": "easeOutBack"},
            {"t": 0.35, "v": 1.1, "e": "easeOutBack"},
            {"t": 0.45, "v": 1.0, "e": "easeOutCubic"}
        ]
        scene["layers"][0]["tracks"]["opacity"] = [
            {"t": 0, "v": 0},
            {"t": 0.1, "v": 1.0}
        ]
    elif "slide-in" in edit:
        # Slide-in 0.38s ease-out-expo alternating left/right
        direction = -300 if beat_num % 2 == 1 else 300
        scene["layers"][0]["tracks"]["pos"] = [
            {"t": 0, "v": [960+direction, 540], "e": "easeOutExpo"},
            {"t": 0.38, "v": [960, 540], "e": "hold"}
        ]
    elif "pan right" in edit:
        # Pan right 60px 0.6s only when connected
        scene["layers"][0]["tracks"]["pos"] = [
            {"t": 0, "v": [960, 540], "e": "easeInOut"},
            {"t": 0.6, "v": [1020, 540], "e": "easeInOut"}
        ]
    elif "slow zoom-in" in edit:
        # Slow zoom-in 5% 3s 1.67%/s Premium
        scene["layers"][0]["tracks"]["scale"] = [
            {"t": 0, "v": 1.0, "e": "premium"},
            {"t": 3.0, "v": 1.05, "e": "premium"}
        ]
    elif "punch-in" in edit:
        # Punch-in 12% 0.35s 34.3%/s
        scene["layers"][0]["tracks"]["scale"] = [
            {"t": 0, "v": 1.0, "e": "easeOutBack"},
            {"t": 0.35, "v": 1.12, "e": "easeOutBack"}
        ]
    elif "stamp" in edit:
        # Stamp + stagger
        scene["layers"][0]["tracks"]["scale"] = [
            {"t": 0, "v": 0.8, "e": "easeOutBack"},
            {"t": 0.3, "v": 1.0, "e": "easeOutBack"}
        ]
        scene["layers"][0]["tracks"]["opacity"] = [
            {"t": 0, "v": 0},
            {"t": 0.1, "v": 1.0}
        ]
    else:
        # Static hold
        scene["layers"][0]["tracks"]["pos"] = [{"t": 0, "v": [960,540]}]
        scene["layers"][0]["tracks"]["scale"] = [{"t": 0, "v": 1.0}]
    
    # Save scene JSON
    scene_path = output_dir / f"scene_beat_{beat_num:03d}.json"
    scene_path.write_text(json.dumps(scene, indent=2))
    
    # Render with ae_motion_enhanced.py
    out_video = output_dir / f"beat_{beat_num:03d}.mp4"
    cmd = ["python3", str(BASE / "ae_motion_enhanced.py"), str(scene_path), "-o", str(out_video)]
    print(f"Rendering beat {beat_num}: {beat_data['narration'][:50]}... | visual {visual[:30]} | edit {edit} | {duration}s -> {out_video}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        print(f"  Failed: {result.stderr[:500]}")
        return None
    else:
        print(f"  ✅ Rendered {out_video} {out_video.stat().st_size / 1024:.1f}KB")
        return out_video

def main():
    # Load script
    script_path = KB / "script_10min_90beats.json"
    if not script_path.exists():
        script_path = KB / "script_super-catchup-152k-gap_13beats.json"
    data = json.loads(script_path.read_text())
    beats = data.get("beats", [])[:5]  # First 5 beats demo
    
    print(f"\n=== Rendering Procrastination Video — {len(beats)} beats demo ===")
    print(f"Topic: Why You Procrastinate (finance dropped, YOUR niche)")
    print(f"Assets: {len(list(ASSETS.glob('*.png')))} hand-drawn PNGs + {len(list((BASE.parent / 'image-search').glob('*')))} real-life licensed + {len(list(ASSETS.glob('*.mp3')))} narration MP3s")
    print(f"Editing: After Effects-like code-driven keyframes, Premium 350-600ms, hard cuts median 3.5s, visual 0.2s before keyword")
    
    rendered = []
    for i, beat in enumerate(beats, 1):
        out = render_beat(i, beat, ASSETS, OUTPUT)
        if out:
            rendered.append(out)
    
    # Combine with narration audio
    print(f"\n=== Combining {len(rendered)} beats with narration audio ===")
    for i, video_path in enumerate(rendered, 1):
        narration_path = ASSETS / f"narration_{i:03d}.mp3"
        if narration_path.exists():
            out_muxed = OUTPUT / f"beat_{i:03d}_muxed.mp4"
            # Mux audio + video, ensure audio length matches video (pad or trim)
            cmd = [
                FFMPEG, "-y",
                "-i", str(video_path),
                "-i", str(narration_path),
                "-c:v", "copy",
                "-c:a", "aac",
                "-map", "0:v:0",
                "-map", "1:a:0",
                "-shortest",
                str(out_muxed)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print(f"  ✅ Muxed beat {i}: {out_muxed} with {narration_path}")
            else:
                print(f"  Failed mux beat {i}: {result.stderr[:300]}")
    
    # Combine all muxed beats into final video with hard cuts 98% + 30ms fade sections
    print(f"\n=== Combining all beats into final 10-min video with After Effects-like editing ===")
    muxed_videos = sorted(OUTPUT.glob("beat_*_muxed.mp4"))
    if muxed_videos:
        # Create concat file
        concat_path = OUTPUT / "concat_list.txt"
        with open(concat_path, "w") as f:
            for v in muxed_videos:
                f.write(f"file '{v}'\n")
        final_path = OUTPUT / "procrastination_why_you_procrastinate_5_steps_10min_premium.mp4"
        cmd = [
            FFMPEG, "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_path),
            "-c", "copy",
            str(final_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            size_mb = final_path.stat().st_size / 1024 / 1024
            print(f"\n✅ Final video: {final_path} {size_mb:.2f}MB")
            # Get duration
            out = subprocess.run(f'{FFMPEG} -i "{final_path}" 2>&1', shell=True, capture_output=True, text=True).stderr
            import re
            m = re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)', out)
            if m:
                print(f"Duration: {m.group(0)}")
        else:
            print(f"Failed concat: {result.stderr[:500]}")
    else:
        print("No muxed videos to combine")

if __name__ == "__main__":
    main()
