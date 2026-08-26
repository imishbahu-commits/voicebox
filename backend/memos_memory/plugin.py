"""
MemOS Plugin for Voicebox - OpenClaw / Hermes compatible
Based on https://github.com/MemTensor/MemOS/apps/memos-local-plugin

This plugin provides persistent memory for Voicebox across chats,
surviving sandbox wipes via git-committed storage.

Installation (like MemOS local plugin):
- For OpenClaw: openclaw plugins install @memtensor/memos-local-plugin
- For Voicebox: This file is auto-loaded

Usage in Voicebox backend:
    from backend.memos_memory.plugin import memos_plugin
    
    # Before each chat - recall memories
    memories = memos_plugin.recall(query="finance Australia")
    
    # After each chat - save new memories
    memos_plugin.remember(messages=[...])
"""

import json
from pathlib import Path
from typing import List, Dict, Any
from .memos_integration import get_memos

class MemOSPlugin:
    """
    MemOS Plugin compatible with OpenClaw/Hermes plugin API
    Provides persistent memory across chats
    """
    
    def __init__(self, user_id: str = "voicebox_user"):
        self.memos = get_memos(user_id=user_id)
        self.name = "memos-local-plugin"
        self.version = "2.0-stardust"
        self.enabled = True
    
    def recall(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Recall memories before each agent run
        Like MemOS Cloud Plugin: recalls memories from MemOS Cloud before each agent run
        """
        result = self.memos.search(query=query, top_k=top_k)
        return result.get("results", [])
    
    def remember(self, messages: List[Dict[str, str]] = None, content: str = None, 
                 metadata: Dict = None) -> Dict:
        """
        Save new messages back after the run ends
        Like MemOS Cloud Plugin: saves new messages back after the run ends
        """
        return self.memos.add(messages=messages, content=content, metadata=metadata)
    
    def search(self, query: str, top_k: int = 5) -> Dict:
        """Search API like MemOS Cloud API"""
        return self.memos.search(query=query, top_k=top_k)
    
    def add(self, messages: List[Dict] = None, content: str = None, **kwargs) -> Dict:
        """Add API like MemOS Cloud API"""
        return self.memos.add(messages=messages, content=content, metadata=kwargs.get("metadata"))
    
    def get_config(self) -> Dict:
        """Get plugin config"""
        config_path = Path(__file__).parent / "config.yaml"
        if config_path.exists():
            import yaml
            try:
                return yaml.safe_load(config_path.read_text())
            except:
                return {"version": self.version, "enabled": self.enabled}
        return {"version": self.version, "enabled": self.enabled}
    
    def viewer_data(self) -> Dict:
        """Data for Memory Viewer dashboard - like memos-local-plugin/viewer/"""
        memories = self.memos.get_all()
        return {
            "total_memories": len(memories),
            "memories": memories[-20:],  # Last 20
            "user_id": self.memos.user_id,
            "version": self.version,
            "storage": "json (git-committed) + backup"
        }

# Singleton plugin instance - auto-loaded
memos_plugin = MemOSPlugin()

# For OpenClaw/Hermes plugin compatibility
def initialize(config: Dict = None) -> MemOSPlugin:
    """Initialize plugin - called by agent runtime"""
    user_id = config.get("user_id", "voicebox_user") if config else "voicebox_user"
    global memos_plugin
    memos_plugin = MemOSPlugin(user_id=user_id)
    return memos_plugin

def get_memory_for_query(query: str, top_k: int = 5) -> str:
    """
    Helper for voicebox to inject memory into prompts
    Returns formatted memory context
    """
    results = memos_plugin.recall(query=query, top_k=top_k)
    if not results:
        return ""
    
    context = "\n".join([f"- {r.get('content', '')}" for r in results])
    return f"\n[Relevant Memories from MemOS]:\n{context}\n"

# Example usage for voicebox paint-explainer
if __name__ == "__main__":
    plugin = MemOSPlugin()
    
    print("=== MemOS Plugin for Voicebox ===")
    print(f"Version: {plugin.version}")
    print(f"Total memories: {len(plugin.memos.get_all())}")
    
    # Simulate recall before chat
    print("\n--- Recall before chat: 'finance Australia' ---")
    memories = plugin.recall("finance Australia", top_k=3)
    for m in memories:
        print(f"  - {m['content'][:80]}...")
    
    # Simulate remember after chat
    print("\n--- Remember after chat ---")
    result = plugin.remember(
        content="User confirmed visuals that resonate work better than text-only. House, couple, piggy bank visuals increase engagement.",
        metadata={"type": "feedback", "project": "finance-australia"}
    )
    print(f"  Saved: {result['memory_id']}")
    
    print(f"\nTotal memories now: {len(plugin.memos.get_all())}")
