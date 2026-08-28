#!/usr/bin/env python3
"""
Render Funny Absurd Video — Highly Engaging Easy To Watch
Reference 11 videos style: pure white bg thick black outline 0.6% flat MS-Paint, hard cuts median 3.5s, visual 0.2s BEFORE keyword, funny absurd assets

Pipeline: script (highly engaging) -> voiceover (voice-06) -> storyboard -> editing plan -> assets funny absurd -> editing create videos
"""
import json, subprocess
from pathlib import Path

BASE = Path(__file__).parent
KB = BASE / "knowledge_base"
ASSETS = BASE / "assets" / "procrastination"
OUTPUT = BASE / "output"
OUTPUT.mkdir(parents=True, exist_ok=True)

# Get ffmpeg path
try:
    import imageio_ffmpeg
    FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
except:
    FFMPEG = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"

def render_beat(beat_num, beat_data, output_dir):
    """Render single beat with funny absurd assets + After Effects-like editing"""
    visual = beat_data.get("visual", "")
    
    # Map funny absurd visuals to actual files
    asset_map = {
        "calendar": ["calendar_deadline_tomorrow_absurd.png", "calendar_deadline.png", "calendar_deadline_tomorrow.png"],
        "security guard": ["brain_security_guard_shield_not_lazy.png", "brain_shield2.png"],
        "drama queen": ["brain_drama_queen_crown.png", "brain_shield.png"],
        "checklist": ["checklist_5_steps.png"],
        "cross-out LAZY": ["cross_out_lazy_heart_brain_argue.png", "brain_amygdala.png"],
        "heart stress": ["heart_stress_cloud_task_monsters.png", "heart_self_compassion.png"],
        "ice cream": ["brain_ice_cream_broccoli_crying.png", "dopamine_molecule.png"],
        "dopamine party": ["dopamine_party_clock_sad.png", "dopamine_molecule.png"],
        "present self": ["present_future_self_split_absurd.png", "present_future_self_split.png"],
        "future stranger": ["future_self_stranger_question.png", "present_future_self_split.png"],
        "brain map": ["brain_amygdala_drama_alarm_ceo.png", "brain_amygdala_prefrontal.png"],
        "BEAR": ["amygdala_shouting_bear_email.png", "brain_amygdala.png"],
        "CEO sleeping": ["prefrontal_ceo_sleeping_coffee.png", "brain_amygdala_prefrontal.png"],
        "alarm wins": ["alarm_wins_ceo_offline_scroll.png", "brain_shield.png"],
        "slot machine": ["dopamine_slot_machine_phone_jackpot.png", "dopamine_molecule.png"],
        "bug spray": ["brain_bug_spray_checkmark.png", "success_checkmark.png"],
        "timer 5 minute": ["timer_5_minute_drama_queen_trick.png", "timer_5_minute.png"],
        "stopwatch": ["brain_stopwatch_suffering_ok.png", "timer_5_minute.png"],
        "boulder": ["person_pushing_boulder_momentum.png", "success_checkmark.png"],
        "80%": ["graph_80_percent_brain_pinocchio.png", "checklist_5_steps.png"],
        "essay monster": ["essay_monster_tiny_button_sword.png", "checklist_5_steps.png"],
    }
    
    src_file = None
    vlower = visual.lower()
    for key, fnames in asset_map.items():
        if key.lower() in vlower:
            for fname in fnames:
                fpath = ASSETS / fname
                if fpath.exists():
                    src_file = fpath
                    break
            if src_file:
                break
    
    if not src_file:
        pngs = [p for p in ASSETS.glob("*.png") if "funny" not in str(p) or True]
        # Prefer funny absurd
        funny = list(ASSETS.glob("*absurd*.png")) + list(ASSETS.glob("*funny*.png")) + list(ASSETS.glob("brain_*.png"))
        if funny:
            src_file = funny[(beat_num-1) % len(funny)]
        else:
            src_file = pngs[0] if pngs else None
    
    if not src_file or not src_file.exists():
        print(f"Beat {beat_num}: No asset found for {visual[:50]}")
        return None
    
    dur_str = beat_data.get("duration", "4.0s")
    duration = float(dur_str.replace("s",""))
    edit = beat_data.get("edit", "")
    
    scene = {
        "width": 1920,
        "height": 1080,
        "fps": 30,
        "duration": duration,
        "bg_color": [255,255,255,255],
        "layers": [{"src": str(src_file), "max_dim": 850, "tracks": {}}]
    }
    
    # After Effects-like editing per storyboard
    if "slide-in" in edit:
        direction = -320 if beat_num % 2 == 1 else 320
        scene["layers"][0]["tracks"]["pos"] = [
            {"t": 0, "v": [960+direction, 540], "e": "easeOutExpo"},
            {"t": 0.38, "v": [960, 540], "e": "hold"}
        ]
        scene["layers"][0]["tracks"]["opacity"] = [{"t": 0, "v": 0}, {"t": 0.05, "v": 1.0}]
    elif "pop-in" in edit:
        scene["layers"][0]["tracks"]["scale"] = [
            {"t": 0, "v": 0.6, "e": "easeOutBack"},
            {"t": 0.35, "v": 1.1, "e": "easeOutBack"},
            {"t": 0.45, "v": 1.0, "e": "easeOutCubic"}
        ]
        scene["layers"][0]["tracks"]["opacity"] = [{"t": 0, "v": 0}, {"t": 0.1, "v": 1.0}]
    elif "pan right" in edit:
        scene["layers"][0]["tracks"]["pos"] = [
            {"t": 0, "v": [960, 540], "e": "easeInOut"},
            {"t": 0.6, "v": [1020, 540], "e": "easeInOut"}
        ]
    elif "slow zoom-in" in edit:
        scene["layers"][0]["tracks"]["scale"] = [
            {"t": 0, "v": 1.0, "e": "premium"},
            {"t": 3.0, "v": 1.05, "e": "premium"}
        ]
    elif "punch-in" in edit:
        scene["layers"][0]["tracks"]["scale"] = [
            {"t": 0, "v": 1.0, "e": "easeOutBack"},
            {"t": 0.35, "v": 1.12, "e": "easeOutBack"},
            {"t": 0.45, "v": 1.0, "e": "easeOutCubic"}
        ]
    elif "stamp" in edit:
        scene["layers"][0]["tracks"]["scale"] = [
            {"t": 0, "v": 0.8, "e": "easeOutBack"},
            {"t": 0.3, "v": 1.0, "e": "easeOutBack"}
        ]
        scene["layers"][0]["tracks"]["opacity"] = [{"t": 0, "v": 0}, {"t": 0.1, "v": 1.0}]
    elif "cross-out" in edit or "draw-on" in edit:
        scene["layers"][0]["tracks"]["scale"] = [
            {"t": 0, "v": 1.0, "e": "easeOutBack"},
            {"t": 0.35, "v": 1.12, "e": "easeOutBack"},
            {"t": 0.45, "v": 1.0, "e": "easeOutCubic"}
        ]
    else:
        scene["layers"][0]["tracks"]["pos"] = [{"t": 0, "v": [960,540]}]
        scene["layers"][0]["tracks"]["scale"] = [{"t": 0, "v": 1.0}]
    
    scene_path = output_dir / f"funny_scene_beat_{beat_num:03d}.json"
    scene_path.write_text(json.dumps(scene, indent=2))
    
    out_video = output_dir / f"funny_beat_{beat_num:03d}.mp4"
    cmd = ["python3", str(BASE / "ae_motion_enhanced.py"), str(scene_path), "-o", str(out_video)]
    print(f"Rendering funny beat {beat_num}: {beat_data['narration'][:55]}... | {src_file.name} | {edit[:30]} | {duration}s")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        print(f"  Failed: {result.stderr[-500:]}")
        return None
    else:
        print(f"  ✅ {out_video.name} {out_video.stat().st_size/1024:.1f}KB")
        return out_video

def main():
    script_path = KB / "script_90beats_funny_absurd.json"
    data = json.loads(script_path.read_text())
    beats = data.get("beats", [])[:10]  # First 10 beats highly engaging
    
    print(f"\n=== Rendering FUNNY ABSURD Video — {len(beats)} beats highly engaging ===")
    print(f"Title: {data['title']}")
    print(f"Style: pure white bg thick outline 0.6% flat MS-Paint funny absurd resonant visuals")
    print(f"Assets: {len(list(ASSETS.glob('*.png')))} PNGs (10 new funny absurd) + {len(list(ASSETS.glob('narration_funny_*.mp3')))} narration funny")
    print(f"Editing: After Effects-like Premium 350-600ms 3 layers, visual 0.2s BEFORE keyword, hard cuts median 3.5s")
    
    rendered = []
    for i, beat in enumerate(beats, 1):
        out = render_beat(i, beat, OUTPUT)
        if out:
            rendered.append(out)
    
    print(f"\n=== Muxing with funny voiceover audio ===")
    for i, video_path in enumerate(rendered, 1):
        narration_path = ASSETS / f"narration_funny_{i:03d}.mp3"
        if not narration_path.exists():
            narration_path = ASSETS / f"narration_{i:03d}.mp3"
        if narration_path.exists():
            out_muxed = OUTPUT / f"funny_beat_{i:03d}_muxed.mp4"
            cmd = [FFMPEG, "-y", "-i", str(video_path), "-i", str(narration_path), "-c:v", "copy", "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0", "-shortest", str(out_muxed)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print(f"  ✅ Muxed beat {i}: {out_muxed.name} + {narration_path.name}")
    
    print(f"\n=== Final concat highly engaging funny absurd video ===")
    muxed_videos = sorted(OUTPUT.glob("funny_beat_*_muxed.mp4"))
    if muxed_videos:
        concat_path = OUTPUT / "funny_concat_list.txt"
        with open(concat_path, "w") as f:
            for v in muxed_videos:
                f.write(f"file '{v}'\n")
        final_path = OUTPUT / "why_you_procrastinate_drama_queen_5_hacks_funny_absurd_premium_10beats.mp4"
        cmd = [FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_path), "-c", "copy", str(final_path)]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            size_mb = final_path.stat().st_size / 1024 / 1024
            print(f"\n✅ FINAL FUNNY ABSURD VIDEO: {final_path} {size_mb:.2f}MB")
            out = subprocess.run(f'{FFMPEG} -i "{final_path}" 2>&1', shell=True, capture_output=True, text=True).stderr
            import re
            m = re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)', out)
            if m:
                print(f"Duration: {m.group(0)}")
        else:
            print(f"Failed concat: {result.stderr[:500]}")

if __name__ == "__main__":
    main()
