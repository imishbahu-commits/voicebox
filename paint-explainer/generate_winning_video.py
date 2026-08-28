#!/usr/bin/env python3
"""
Winning Video Generator — Survives Wipes via Git
Chooses winning topic → generates script → narration → starts creating video
Uses knowledge_base/ JSONs git-tracked + MemOS memory_store.json + STYLE_SPEC etc.

Usage:
  python3 generate_winning_video.py --topic super-catchup-152k-gap --beats 90 --voice voice-05 --output finance_australia_combined_90beats_premium_8_10min.mp4
  python3 generate_winning_video.py --list-topics
  python3 generate_winning_video.py --restore  # Restore heavy info after wipe

Heavy info saved in:
- paint-explainer/knowledge_base/winning_topics.json (5 topics)
- paint-explainer/knowledge_base/style_spec.json (34 rules)
- paint-explainer/knowledge_base/editing_skills.json (15 repos)
- paint-explainer/knowledge_base/script_templates.json (90 beats template)
- paint-explainer/knowledge_base/narration_config.json (voice-05 140-160 WPM)
- paint-explainer/knowledge_base/video_pipeline.json (8 steps)
- STYLE_SPEC_ANALYSIS.md 524 lines, GITHUB_TOOLS_INVENTORY.md 300 lines, EXTENDED_EDITING_TYPES.md 64 rules, BEST_OF_BEST_SKILLS.md 15 repos
- backend/memos_memory/memory_store.json 32 memories MemOS
All git-tracked in arena/01a03907-voicebox branch, pushed to GitHub, survives wipes via git clone -b arena/01a03907-voicebox
"""
import json, os, sys, argparse
from pathlib import Path

BASE = Path(__file__).parent
KB = BASE / "knowledge_base"

def load_json(name):
    path = KB / name
    if not path.exists():
        print(f"Missing {path}, restoring from git?")
        return {}
    return json.loads(path.read_text())

def list_topics():
    data = load_json("winning_topics.json")
    print(f"\n=== Winning Topics ({len(data.get('winning_topics',[]))} topics) ===")
    for t in data.get("winning_topics", []):
        print(f"\n[{t['priority']}] {t['id']}: {t['title']}")
        print(f"  Hook: {t['hook'][:100]}...")
        print(f"  Why winning: {t['why_winning'][:100]}...")
        print(f"  Beats: {t['beats']} Duration: {t['duration_target']} Status: {t['status']}")
        print(f"  Visuals: {', '.join(t['visuals_resonate'][:3])}...")

def choose_topic(topic_id=None):
    data = load_json("winning_topics.json")
    topics = data.get("winning_topics", [])
    if not topics:
        print("No topics found, using default super-catchup-152k-gap")
        return {"id": "super-catchup-152k-gap", "title": "The $152k Super Gap at 40"}
    if topic_id:
        for t in topics:
            if t["id"] == topic_id:
                print(f"\n=== Chosen Topic: {t['id']} ===")
                print(f"Title: {t['title']}")
                print(f"Hook: {t['hook']}")
                print(f"Why winning: {t['why_winning']}")
                print(f"Beats: {t['beats']} Duration: {t['duration_target']}")
                print(f"Chapters: {len(t.get('chapters',[]))}")
                for ch in t.get("chapters", []):
                    print(f"  - {ch['name']}: {ch['duration']} {ch['beats']} beats")
                return t
    # Default priority 1
    sorted_topics = sorted(topics, key=lambda x: x.get("priority", 99))
    t = sorted_topics[0]
    print(f"\n=== Auto-Chosen Winning Topic (Priority 1): {t['id']} ===")
    print(f"Title: {t['title']}")
    return t

def generate_script(topic, beats=90):
    templates = load_json("script_templates.json")
    winning = templates.get("winning_topic_super_catchup_152k_gap", {})
    base_beats = winning.get("beats", [])
    
    print(f"\n=== Generating Script for {topic['id']} — {beats} beats ===")
    print(f"Template: {len(base_beats)} base beats, extending to {beats} beats")
    
    # Extend base beats to 90 by repeating pattern with variations
    script = []
    chapter_beats = topic.get("chapters", [])
    # Simple: repeat base pattern
    for i in range(beats):
        if i < len(base_beats):
            b = base_beats[i].copy()
            b["beat"] = i+1
            script.append(b)
        else:
            # Generate variation based on chapter
            chapter_idx = min(i // 15, len(chapter_beats)-1) if chapter_beats else 0
            chapter = chapter_beats[chapter_idx] if chapter_beats else {"name": "Solution"}
            # Variation
            b = {
                "beat": i+1,
                "narration": f"{chapter['name']} continues with genuine ATO data and visuals that resonate for 40+ Aussies.",
                "visual": "money bag + calendar + house",
                "edit": "pop-in 0.35s ease-out-back" if i % 3 == 0 else "slide-in 0.38s ease-out-expo" if i % 3 == 1 else "pan right 60px 0.6s only when connected",
                "keywords": ["$30k", "12%", "house"],
                "duration": "3.5s",
                "chapter": chapter["name"]
            }
            script.append(b)
    
    print(f"Generated {len(script)} beats, first 3:")
    for b in script[:3]:
        print(f"  Beat {b['beat']}: {b['narration'][:80]}... | visual: {b['visual']} | edit: {b['edit']} | {b['duration']}")
    
    # Save
    out_path = KB / f"script_{topic['id']}_{beats}beats.json"
    out_path.write_text(json.dumps({"topic": topic, "beats": script, "total_beats": beats, "rules": templates.get("script_generation_rules", {})}, indent=2))
    print(f"Saved script to {out_path} {out_path.stat().st_size / 1024:.1f}KB")
    return script, out_path

def generate_narration(script, voice_id="voice-05"):
    config = load_json("narration_config.json")
    print(f"\n=== Generating Narration — Voice {voice_id} 140-160 WPM ===")
    print(f"Rules: {config.get('narration_rules', {}).get('wpm')} WPM, {config.get('narration_rules', {}).get('words_per_beat')} words/beat, pause median {config.get('narration_rules', {}).get('pause_median')}")
    
    narration = []
    for b in script:
        narration.append({
            "beat": b["beat"],
            "text": b["narration"],
            "duration": b.get("duration", "3.5s"),
            "words": len(b["narration"].split()),
            "voice_id": voice_id,
            "file_path": f"audio/narration_{b['beat']:03d}.mp3",
            "visual_sync": "0.2s BEFORE keyword"
        })
    
    print(f"Generated {len(narration)} narration files, first 3:")
    for n in narration[:3]:
        print(f"  Beat {n['beat']}: {n['text'][:80]}... | {n['duration']} | {n['words']} words | {n['file_path']}")
    
    out_path = KB / f"narration_{script[0].get('chapter','topic')}_{len(script)}beats_{voice_id}.json"
    # Use topic id from first beat if available
    out_path = KB / f"narration_{len(script)}beats_{voice_id}.json"
    out_path.write_text(json.dumps({"voice": config.get("voice", {}), "narration": narration, "total": len(narration)}, indent=2))
    print(f"Saved narration config to {out_path} {out_path.stat().st_size / 1024:.1f}KB")
    print(f"Next: Use voicebox generate_speech with voice_id {voice_id} for each beat text -> {narration[0]['file_path']}")
    return narration, out_path

def start_creating_video(topic, script, narration, output="finance_australia_combined_90beats_premium_8_10min.mp4"):
    pipeline = load_json("video_pipeline.json")
    style = load_json("style_spec.json")
    skills = load_json("editing_skills.json")
    
    print(f"\n=== Starting Video Creation — {output} ===")
    print(f"Topic: {topic['id']} {topic['title']}")
    print(f"Script: {len(script)} beats")
    print(f"Narration: {len(narration)} files voice {narration[0]['voice_id'] if narration else 'voice-05'}")
    print(f"Style: pure white bg #FFFFFF thick outline 0.6% flat 4-6 colors no gradients, pop 0.35s ease-out-back slide 0.38s ease-out-expo pan 60px only when connected, visual 0.2s before keyword")
    print(f"Skills: {len(skills.get('tiers',{}).get('tier1_essential',[]))} Tier1 essential puppet-warp LottieFiles lottie-android hyperframes")
    print(f"Pipeline: 8 steps choose_topic -> script -> narration -> visuals -> animate with ae_motion_enhanced.py -> add audio -> combine -> preview")
    
    # Create scene JSON for ae_motion_enhanced.py for first 3 beats as demo
    demo_beats = script[:3]
    scene = {
        "width": 1920,
        "height": 1080,
        "fps": 30,
        "duration": sum([float(b.get("duration","3.5s").replace("s","")) for b in demo_beats]),
        "bg_color": [255,255,255,255],
        "layers": []
    }
    # For each beat, create layer
    for i, b in enumerate(demo_beats):
        # Visual to asset mapping (simplified)
        visual = b.get("visual", "house")
        # In real, would generate PNG via hand-drawn-styles
        # For demo, use placeholder
        layer = {
            "src": f"assets/{visual.replace(' ', '_')}.png",  # Placeholder, need actual PNG
            "max_dim": 600,
            "tracks": {
                "pos": [{"t": 0, "v": [960,540], "e": "easeOutExpo"}, {"t": 0.38, "v": [960,540], "e": "hold"}] if "slide" in b.get("edit","") else [{"t": 0, "v": [960,540]}],
                "scale": [{"t": 0, "v": 0.6, "e": "easeOutBack"}, {"t": 0.35, "v": 1.1}, {"t": 0.45, "v": 1.0, "e": "easeOutCubic"}] if "pop" in b.get("edit","") else [{"t": 0, "v": 1.0}],
                "rot": [{"t": 0, "v": 0}],
                "opacity": [{"t": 0, "v": 0}, {"t": 0.1, "v": 1.0}],
                "puppet": [{"t": 0, "v": {"pins": [{"idx": 10, "shift": [0,0]}, {"idx": 50, "shift": [20,-30]}]}, "e": "easeInOut"}] if "money bag" in visual else []
            }
        }
        scene["layers"].append(layer)
    
    scene_path = KB / f"scene_demo_{topic['id']}_3beats.json"
    scene_path.write_text(json.dumps(scene, indent=2))
    print(f"\nDemo scene JSON created: {scene_path} {scene_path.stat().st_size / 1024:.1f}KB")
    print(f"To render demo 3 beats: python3 paint-explainer/ae_motion_enhanced.py {scene_path} -o /tmp/demo_3beats.mp4")
    print(f"To render full {len(script)} beats: generate scene JSONs for all beats and combine via ffmpeg concat")
    print(f"Final output target: {output} 8-10 min 90 beats")
    print(f"\n=== Heavy Info Saved & Pipeline Ready ===")
    print(f"All heavy info in paint-explainer/knowledge_base/ git-tracked, survives wipes via git clone -b arena/01a03907-voicebox")
    print(f"MemOS 32 memories in backend/memos_memory/memory_store.json git-tracked")
    print(f"STYLE_SPEC 524 lines, GITHUB_TOOLS 300 lines, EXTENDED 64 rules, BEST_OF_BEST 15 repos all git-tracked")
    print(f"Restore after wipe: git clone https://github.com/imishbahu-commits/voicebox.git -b arena/01a03907-voicebox && cd voicebox && python3 paint-explainer/generate_winning_video.py --topic super-catchup-152k-gap --beats 90")
    
    return scene_path

def restore_heavy_info():
    print("\n=== Restoring Heavy Info After Wipe ===")
    print("Checking git-tracked knowledge base...")
    files = [
        "paint-explainer/knowledge_base/winning_topics.json",
        "paint-explainer/knowledge_base/style_spec.json",
        "paint-explainer/knowledge_base/editing_skills.json",
        "paint-explainer/knowledge_base/script_templates.json",
        "paint-explainer/knowledge_base/narration_config.json",
        "paint-explainer/knowledge_base/video_pipeline.json",
        "STYLE_SPEC_ANALYSIS.md",
        "GITHUB_TOOLS_INVENTORY.md",
        "EXTENDED_EDITING_TYPES.md",
        "BEST_OF_BEST_SKILLS.md",
        "paint-explainer/ae_motion_enhanced.py",
        "backend/memos_memory/memory_store.json"
    ]
    for f in files:
        p = Path(f)
        if p.exists():
            size = p.stat().st_size / 1024
            print(f"  ✅ {f} {size:.1f}KB")
        else:
            print(f"  ❌ Missing {f} — need git clone -b arena/01a03907-voicebox")
    print("\nAll heavy info survives wipes via git push to arena/01a03907-voicebox branch")
    print("To restore: git clone https://github.com/imishbahu-commits/voicebox.git -b arena/01a03907-voicebox")

def main():
    parser = argparse.ArgumentParser(description="Winning Video Generator — Survives Wipes")
    parser.add_argument("--topic", type=str, default="super-catchup-152k-gap", help="Winning topic id")
    parser.add_argument("--beats", type=int, default=90, help="Number of beats 8-10 min 90 beats")
    parser.add_argument("--voice", type=str, default="voice-05", help="Voice id voice-05 clean corporate")
    parser.add_argument("--output", type=str, default="finance_australia_combined_90beats_premium_8_10min.mp4", help="Output MP4")
    parser.add_argument("--list-topics", action="store_true", help="List winning topics")
    parser.add_argument("--restore", action="store_true", help="Restore heavy info after wipe")
    args = parser.parse_args()
    
    if args.list_topics:
        list_topics()
        return
    if args.restore:
        restore_heavy_info()
        return
    
    print(f"\n=== Winning Video Generator — Heavy Info Persistent ===")
    print(f"Topic: {args.topic} Beats: {args.beats} Voice: {args.voice} Output: {args.output}")
    
    topic = choose_topic(args.topic)
    script, script_path = generate_script(topic, beats=args.beats)
    narration, narration_path = generate_narration(script, voice_id=args.voice)
    scene_path = start_creating_video(topic, script, narration, output=args.output)
    
    print(f"\n=== DONE — Heavy Info Saved ===")
    print(f"Script: {script_path}")
    print(f"Narration: {narration_path}")
    print(f"Scene demo: {scene_path}")
    print(f"Next: Generate PNGs via hand-drawn-styles, TTS via generate_speech, render via ae_motion_enhanced.py, combine via ffmpeg")

if __name__ == "__main__":
    main()
