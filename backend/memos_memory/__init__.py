"""
MemOS Integration for Voicebox
https://github.com/MemTensor/MemOS

Provides persistent memory across chats, survives sandbox wipes.

Quick Start:
    from backend.memos_memory import memos_plugin, get_memos
    
    # Recall before chat
    memories = memos_plugin.recall("finance Australia")
    
    # Remember after chat
    memos_plugin.remember(content="New insight...")

For full MemOS (requires ollama, qdrant, neo4j):
    pip install MemoryOS
    from memos.configs.mem_os import MOSConfig
    from memos.mem_os.main import MOS
"""

from .memos_integration import MemOSVoicebox, get_memos
from .plugin import MemOSPlugin, memos_plugin, get_memory_for_query, initialize

__all__ = [
    "MemOSVoicebox",
    "get_memos", 
    "MemOSPlugin",
    "memos_plugin",
    "get_memory_for_query",
    "initialize"
]

__version__ = "2.0-stardust"
__source__ = "https://github.com/MemTensor/MemOS"
