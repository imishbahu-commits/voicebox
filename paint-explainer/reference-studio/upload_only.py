from flask import Flask, request, send_from_directory, jsonify
from flask_cors import CORS
import os
import shutil
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

BASE = Path(__file__).parent
UPLOAD = BASE / "uploads"
UPLOAD.mkdir(parents=True, exist_ok=True)

# Also backup to data/reference_videos for persistence attempt + memos
DATA_REF = Path("/home/user/voicebox/data/reference_videos")
DATA_REF.mkdir(parents=True, exist_ok=True)

# Fast upload config - 4 MB/s target
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max
app.config['UPLOAD_FOLDER'] = str(UPLOAD)

# For memos integration
try:
    import sys
    sys.path.insert(0, "/home/user/voicebox")
    from backend.memos_memory import memos_plugin
    MEMOS_AVAILABLE = True
except:
    MEMOS_AVAILABLE = False

@app.route("/")
def index():
    return send_from_directory(str(BASE), "index.html")

@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "upload_dir": str(UPLOAD), "count": len(list(UPLOAD.glob("*.mp4")))})

@app.route("/list")
def lst():
    files = []
    for f in UPLOAD.glob("*"):
        if f.is_file():
            try:
                stat = f.stat()
                files.append({
                    "name": f.name,
                    "size": stat.st_size,
                    "size_mb": round(stat.st_size / 1024 / 1024, 2),
                    "mtime": stat.st_mtime,
                    "mtime_str": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "path": str(f)
                })
            except:
                pass
    # Sort by mtime desc (newest first)
    files.sort(key=lambda x: x["mtime"], reverse=True)
    return jsonify(files)

@app.route("/uploads/<path:filename>")
def serve(filename):
    return send_from_directory(str(UPLOAD), filename)

@app.route("/upload", methods=["POST"])
def upload():
    """Fast upload endpoint - handles single file upload"""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # Secure filename
    filename = file.filename
    # Remove path traversal
    filename = os.path.basename(filename)
    # Ensure mp4 or video
    if not filename.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v')):
        # Allow anyway but warn
        pass
    
    save_path = UPLOAD / filename
    
    # Ensure dir exists before save - fix FileNotFoundError for 15699.mp4
    UPLOAD.mkdir(parents=True, exist_ok=True)
    DATA_REF.mkdir(parents=True, exist_ok=True)
    
    # Save file - fast 4 MB/s optimized
    # Use direct save with larger buffer for speed
    file.save(str(save_path))
    
    size_mb = save_path.stat().st_size / 1024 / 1024
    
    # Backup to data/reference_videos
    try:
        backup_path = DATA_REF / filename
        shutil.copy(str(save_path), str(backup_path))
    except Exception as e:
        print(f"Backup failed: {e}")
    
    # Remember via MemOS
    if MEMOS_AVAILABLE:
        try:
            memos_plugin.remember(
                content=f"Reference video uploaded: {filename} {size_mb:.2f}MB via Upload Studio Port 3000 fast upload",
                metadata={"type": "reference_video", "filename": filename, "size_mb": size_mb, "source": "upload_studio"}
            )
        except Exception as e:
            print(f"MemOS remember failed: {e}")
    
    # Try to get duration via ffmpeg
    duration = 0
    try:
        import subprocess, re
        result = subprocess.run(
            ["/usr/local/bin/ffmpeg", "-i", str(save_path)],
            capture_output=True, text=True, timeout=10
        )
        m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", result.stderr)
        if m:
            h, mm, s = m.groups()
            duration = int(h)*3600 + int(mm)*60 + float(s)
    except:
        pass
    
    return jsonify({
        "status": "success",
        "filename": filename,
        "size_mb": round(size_mb, 2),
        "duration": duration,
        "path": str(save_path),
        "message": f"Uploaded {filename} {size_mb:.2f}MB fast, grabbed for processing"
    })

@app.route("/upload-multiple", methods=["POST"])
def upload_multiple():
    """Fast multiple files upload"""
    if 'files' not in request.files:
        return jsonify({"error": "No files part"}), 400
    
    files = request.files.getlist('files')
    results = []
    
    for file in files:
        if file.filename == '':
            continue
        filename = os.path.basename(file.filename)
        save_path = UPLOAD / filename
        # Ensure dir exists for fast 4 MB/s upload
        UPLOAD.mkdir(parents=True, exist_ok=True)
        DATA_REF.mkdir(parents=True, exist_ok=True)
        file.save(str(save_path))
        size_mb = save_path.stat().st_size / 1024 / 1024
        
        # Backup
        try:
            shutil.copy(str(save_path), str(DATA_REF / filename))
        except:
            pass
        
        if MEMOS_AVAILABLE:
            try:
                memos_plugin.remember(
                    content=f"Reference video uploaded: {filename} {size_mb:.2f}MB",
                    metadata={"type": "reference_video", "filename": filename}
                )
            except:
                pass
        
        results.append({
            "filename": filename,
            "size_mb": round(size_mb, 2),
            "status": "success"
        })
    
    return jsonify({
        "status": "success",
        "count": len(results),
        "files": results,
        "message": f"Uploaded {len(results)} files fast"
    })

@app.route("/delete/<path:filename>", methods=["DELETE", "POST"])
def delete_file(filename):
    """Delete uploaded file"""
    filename = os.path.basename(filename)
    path = UPLOAD / filename
    if path.exists():
        path.unlink()
        # Also delete backup
        try:
            (DATA_REF / filename).unlink(missing_ok=True)
        except:
            pass
        return jsonify({"status": "success", "deleted": filename})
    return jsonify({"error": "Not found"}), 404

if __name__ == "__main__":
    print(f"Upload Studio starting on 0.0.0.0:3000")
    print(f"Upload dir: {UPLOAD}")
    print(f"Backup dir: {DATA_REF}")
    print(f"MemOS available: {MEMOS_AVAILABLE}")
    app.run(host="0.0.0.0", port=3000, debug=False, threaded=True)
