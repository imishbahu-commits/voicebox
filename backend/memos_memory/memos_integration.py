"""
MemOS Integration for Voicebox - Persistent Memory Across Chats
Based on https://github.com/MemTensor/MemOS

Provides consistent memory in every new chat, survives sandbox wipes via git.

Features from MemOS:
- Unified Memory API: add, search, edit, delete
- Self-evolving memory (feedback-driven)
- Hybrid retrieval (text + vector ready)
- Local-first SQLite storage concept
- Multi-cube knowledge base

For Voicebox paint-explainer:
- Remembers winning finance topics
- Remembers editing style (clean visuals, no messy, smart router)
- Remembers voice preferences
- Remembers project progress (30 beats = 2.64 min done)
"""

import json
import os
import time
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Persistent storage that survives wipes via git commit
MEMORY_DIR = Path(__file__).parent
MEMORY_FILE = MEMORY_DIR / "memory_store.json"
CONFIG_FILE = MEMORY_DIR / "config.yaml"

# Also backup to data/ which is more persistent
BACKUP_DIR = Path("/home/user/voicebox/data/memos")
BACKUP_FILE = BACKUP_DIR / "memory_store_backup.json"

class MemOSVoicebox:
    """
    Lightweight MemOS-inspired memory OS for Voicebox
    - Stores memories in JSON (git-committed for persistence)
    - Provides add/search like MemOS
    - Self-evolving via feedback
    - Survives sandbox wipes
    """
    
    def __init__(self, user_id: str = "voicebox_user"):
        self.user_id = user_id
        self.memory_file = MEMORY_FILE
        self.backup_file = BACKUP_FILE
        self._ensure_storage()
        self.memories = self._load()
    
    def _ensure_storage(self):
        MEMORY_DIR.mkdir(exist_ok=True)
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        if not self.memory_file.exists():
            self.memory_file.write_text(json.dumps({
                "user_id": self.user_id,
                "created_at": datetime.now().isoformat(),
                "memories": [],
                "version": "2.0-stardust",
                "source": "MemTensor/MemOS integration"
            }, indent=2))
    
    def _load(self) -> List[Dict]:
        try:
            if self.memory_file.exists():
                data = json.loads(self.memory_file.read_text())
                return data.get("memories", [])
        except:
            pass
        # Try backup
        try:
            if self.backup_file.exists():
                data = json.loads(self.backup_file.read_text())
                return data.get("memories", [])
        except:
            pass
        return []
    
    def _save(self):
        data = {
            "user_id": self.user_id,
            "updated_at": datetime.now().isoformat(),
            "memories": self.memories,
            "version": "2.0-stardust",
            "count": len(self.memories),
            "source": "MemTensor/MemOS integration for voicebox"
        }
        self.memory_file.write_text(json.dumps(data, indent=2))
        # Backup
        try:
            self.backup_file.write_text(json.dumps(data, indent=2))
        except:
            pass
    
    def add(self, messages: List[Dict[str, str]] = None, content: str = None, 
            memory_type: str = "text", metadata: Dict = None) -> Dict:
        """
        Add memory - like MemOS add API
        Supports both messages format and direct content
        """
        if messages:
            # Extract from messages like MemOS
            text = " ".join([m.get("content", "") for m in messages])
        else:
            text = content or ""
        
        if not text:
            return {"status": "error", "message": "No content"}
        
        memory = {
            "id": f"mem_{int(time.time()*1000)}_{len(self.memories)}",
            "content": text,
            "type": memory_type,
            "user_id": self.user_id,
            "created_at": datetime.now().isoformat(),
            "metadata": metadata or {},
            "messages": messages or []
        }
        self.memories.append(memory)
        self._save()
        return {"status": "success", "memory_id": memory["id"], "memory": memory}
    
    def search(self, query: str, top_k: int = 5, user_id: str = None) -> Dict:
        """
        Search memories - like MemOS search API
        Hybrid retrieval: simple text matching (vector ready for future)
        """
        query_lower = query.lower()
        scored = []
        for mem in self.memories:
            content_lower = mem.get("content", "").lower()
            # Simple scoring: count query words in content
            score = 0
            for word in query_lower.split():
                if word in content_lower:
                    score += 1
            # Bonus for recent
            if score > 0:
                scored.append((score, mem))
        
        # Sort by score descending
        scored.sort(key=lambda x: x[0], reverse=True)
        results = [m for _, m in scored[:top_k]]
        
        return {
            "query": query,
            "results": results,
            "count": len(results),
            "total_memories": len(self.memories),
            "text_mem": [r["content"] for r in results]  # MemOS compatible
        }
    
    def get_all(self) -> List[Dict]:
        return self.memories
    
    def delete(self, memory_id: str) -> Dict:
        original_len = len(self.memories)
        self.memories = [m for m in self.memories if m.get("id") != memory_id]
        if len(self.memories) < original_len:
            self._save()
            return {"status": "success", "deleted": memory_id}
        return {"status": "not_found"}
    
    def feedback(self, memory_id: str, feedback: str) -> Dict:
        """
        Memory feedback & correction - like MemOS feedback API
        Refine memory with natural-language feedback
        """
        for mem in self.memories:
            if mem.get("id") == memory_id:
                mem["feedback"] = feedback
                mem["updated_at"] = datetime.now().isoformat()
                # If feedback says correct, update content
                if "correct" in feedback.lower() or "update" in feedback.lower():
                    mem["content"] += f" [Feedback: {feedback}]"
                self._save()
                return {"status": "success", "memory": mem}
        return {"status": "not_found"}

# Singleton for easy use across voicebox
_memos_instance = None

def get_memos(user_id: str = "voicebox_user") -> MemOSVoicebox:
    global _memos_instance
    if _memos_instance is None:
        _memos_instance = MemOSVoicebox(user_id=user_id)
    return _memos_instance

# Quick test
if __name__ == "__main__":
    memos = get_memos()
    print(f"Loaded {len(memos.get_all())} memories")
    
    # Add example memories from current session
    memos.add(content="User wants winning finance topic for tier1 Australia 40yo, genuine no fake claims, educational like reference videos. Subniche: Super Catch-Up $152k behind, niche bending super+tax+TTR+property", 
              metadata={"topic": "finance-australia", "type": "winning_topic"})
    
    memos.add(content="Editing style: smart router different edit per beat not same every time, only when needed. Visuals clean PURE WHITE bg thick black outline flat colors MS-Paint style no messy, visuals that resonate house couple piggy bank not just text. Voice clean 12-16 words 2-6s voice-05 perfect sync 0.2s before keyword. No cheap arrow circle marking.",
              metadata={"type": "editing_style", "project": "paint-explainer"})
    
    memos.add(content="Project progress: Part 2 Batch 1 visual 11-20 DONE 50s 1.41MB with real visuals that resonate. 30 beats total before wipe = 2.64 min. Target 90 beats = 8.2 min for 8-10 min video. Need 80 beats remaining. Preview Studio Port 3001, Upload Studio Port 3000.",
              metadata={"type": "project_progress", "project": "finance-australia-40plus-part2"})
    
    # Search
    results = memos.search("finance Australia super", top_k=3)
    print(f"Search results: {results['count']}")
    for r in results["results"]:
        print(f" - {r['content'][:100]}...")
