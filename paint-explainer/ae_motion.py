#!/usr/bin/env python3
import json, os, sys, math, subprocess
from pathlib import Path
from PIL import Image
import numpy as np

def ease_out_back(t):
    c1=1.70158
    c3=c1+1
    return 1 + c3*pow(t-1,3) + c1*pow(t-1,2)

def ease_out_expo(t):
    return 1 if t==1 else 1-pow(2,-10*t)

def ease_in_out(t):
    return t*t*(3-2*t) if t<1 else 1

def interp(v0,v1,t,ease):
    if ease=="hold":
        return v0
    if ease=="easeOutBack":
        tt=ease_out_back(t)
    elif ease=="easeOutExpo":
        tt=ease_out_expo(t)
    elif ease=="easeInOut":
        tt=ease_in_out(t)
    else:
        tt=t
    if isinstance(v0,(list,tuple)):
        return [v0[i]+(v1[i]-v0[i])*tt for i in range(len(v0))]
    else:
        return v0+(v1-v0)*tt

def get_track_value(track, time):
    if not track:
        return None
    # find surrounding keyframes
    prev=None
    nxt=None
    for kf in track:
        if kf["t"]<=time:
            prev=kf
        else:
            nxt=kf
            break
    if prev is None:
        return track[0]["v"]
    if nxt is None:
        return prev["v"]
    # interpolate
    dt=nxt["t"]-prev["t"]
    if dt<=0:
        return prev["v"]
    t=(time-prev["t"])/dt
    return interp(prev["v"], nxt["v"], t, nxt.get("e","hold"))

def render_scene(scene_path, out_path):
    data=json.loads(Path(scene_path).read_text())
    W=data.get("width",1280)
    H=data.get("height",720)
    fps=data.get("fps",24)
    dur=data.get("duration",3.0)
    bg=data.get("bg_color",[255,255,255,255])
    layers=data.get("layers",[])
    motion_blur=data.get("motion_blur",1)
    
    frames=int(dur*fps)
    tmp_dir=Path(out_path).parent / f"tmp_{Path(out_path).stem}"
    tmp_dir.mkdir(exist_ok=True)
    
    # preload images
    layer_imgs=[]
    for lyr in layers:
        src=lyr.get("src")
        max_dim=lyr.get("max_dim",600)
        try:
            img=Image.open(src).convert("RGBA")
            # isolate and resize
            w,h=img.size
            scale_factor=max_dim/max(w,h) if max(w,h)>max_dim else 1.0
            nw=int(w*scale_factor)
            nh=int(h*scale_factor)
            img=img.resize((nw,nh), Image.LANCZOS)
            layer_imgs.append(img)
        except Exception as e:
            print(f"Failed load {src}: {e}")
            layer_imgs.append(None)
    
    # render frames
    for f in range(frames):
        t=f/fps
        canvas=Image.new("RGBA",(W,H), tuple(bg))
        for idx, lyr in enumerate(layers):
            img=layer_imgs[idx]
            if img is None:
                continue
            tracks=lyr.get("tracks",{})
            pos_track=tracks.get("pos")
            scale_track=tracks.get("scale")
            pos=get_track_value(pos_track, t) if pos_track else [W//2,H//2]
            scale=get_track_value(scale_track, t) if scale_track else 1.0
            if isinstance(scale,(list,tuple)):
                scale=scale[0]
            # apply scale
            iw,ih=img.size
            nw=int(iw*scale)
            nh=int(ih*scale)
            if nw<=0 or nh<=0:
                continue
            scaled=img.resize((nw,nh), Image.LANCZOS)
            # position
            x=int(pos[0]-nw//2)
            y=int(pos[1]-nh//2)
            canvas.alpha_composite(scaled, (x,y))
        # save frame
        frame_path=tmp_dir / f"frame_{f:05d}.png"
        canvas.convert("RGB").save(frame_path)
        if f%24==0:
            print(f"Frame {f}/{frames} t={t:.2f}s")
    
    # encode with ffmpeg
    ffmpeg="/usr/local/bin/ffmpeg"
    cmd=[ffmpeg,"-y","-framerate",str(fps),"-i",str(tmp_dir/"frame_%05d.png"),"-c:v","libx264","-pix_fmt","yuv420p","-vf","format=yuv420p",str(out_path)]
    subprocess.run(cmd, capture_output=True)
    # cleanup
    import shutil
    shutil.rmtree(tmp_dir, ignore_errors=True)
    print(f"wrote {out_path}")

if __name__=="__main__":
    if len(sys.argv)<2:
        print("Usage: ae_motion.py scene.json -o out.mp4")
        sys.exit(1)
    scene=sys.argv[1]
    out="out.mp4"
    if "-o" in sys.argv:
        idx=sys.argv.index("-o")
        if idx+1<len(sys.argv):
            out=sys.argv[idx+1]
    render_scene(scene,out)
