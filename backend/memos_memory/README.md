# MemOS Integration for Voicebox - Persistent Memory Across Chats

This integrates MemTensor/MemOS concepts for consistent memory in every new chat.

## Why MemOS?

MemOS (Memory Operating System) provides:
- Unified Memory API: add, retrieve, edit, delete
- Self-evolving memory
- Hybrid retrieval (FTS5 + vector)
- Local-first storage (SQLite) - 100% on-device
- Survives sandbox wipes via git-committed storage

## Architecture

- `memory_store.json` - committed to git, survives wipes
- `memos_integration.py` - wrapper with add/search
- `config.yaml` - local config

## For Voicebox:

Voicebox is AI voice studio - persistent memory means:
- Remember user's voice preferences
- Remember past projects (finance-australia 40+)
- Remember editing style (clean visuals, no messy, smart router)
- Remember winning topics
- Consistent across new chats
