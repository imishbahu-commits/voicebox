# MemOS Integration for Voicebox — Persistent Memory Across Chats

> Connected: https://github.com/MemTensor/MemOS
> Plugin: Self-evolving memory OS for LLM & AI Agents

This integration provides **consistent memory in every new chat**, surviving sandbox wipes via git-committed storage — inspired by MemTensor/MemOS 2.0 Stardust.

## What is MemOS?

**MemOS** is a Memory Operating System for LLMs and AI agents that unifies **store / retrieve / manage** for long-term memory, enabling context-aware and personalized interactions.

**Key Features from MemOS:**
- **Unified Memory API**: add, retrieve, edit, delete — structured as graph, inspectable
- **Multi-Modal Memory**: text, images, tool traces, personas
- **Multi-Cube Knowledge Base**: Manage multiple knowledge bases as composable cubes
- **Asynchronous Ingestion via MemScheduler**: Millisecond-level latency
- **Memory Feedback & Correction**: Refine memory with natural-language feedback
- **Hybrid Retrieval**: FTS5 + vector search
- **Local-first**: 100% on-device SQLite option

**Performance:**
- LoCoMo: 88.83, LongMemEval: 89.20, PersonaMem v2: 40.58
- OpenClaw task completion: 36.63% → 50.87% with MemOS
- 35.24% token savings

## Installation Options (from MemOS README)

### Option 1: Cloud API (Hosted) — Easiest
```bash
# Get API key from https://memos.openmem.net/
# Then:
from memos import MemOSClient
client = MemOSClient(api_key="mpg-your-key")
client.add(messages=[...])
```

### Option 2: Self-Host
```bash
git clone https://github.com/MemTensor/MemOS.git
cd MemOS
cp docker/.env.example .env
cd docker
docker compose up  # Starts MemOS API + Neo4j + Qdrant at localhost:8000
```

### Option 3: MemOS Cloud Plugin for OpenClaw (Zero Ops)
```bash
openclaw plugins install @memtensor/memos-cloud-openclaw-plugin@latest
openclaw gateway restart
# Recalls memories before each agent run, saves after
```

### Option 4: Local Plugin for OpenClaw/Hermes/DeepSeek Harness (100% Local)
```bash
# macOS/Linux
curl -fsSL https://raw.githubusercontent.com/MemTensor/MemOS/main/apps/memos-local-plugin/install.sh | bash

# Windows
irm https://raw.githubusercontent.com/MemTensor/MemOS/main/apps/memos-local-plugin/install.ps1 -OutFile "$env:TEMP\memos-install.ps1"; powershell -ExecutionPolicy Bypass -File "$env:TEMP\memos-install.ps1"
```

## Our Integration for Voicebox (This Repo)

We implemented a **lightweight MemOS-inspired plugin** that works in this sandbox and **survives wipes via git commit**.

### Architecture

```
backend/memos_memory/
├── memos_integration.py  # Core MemOS-like API (add/search/feedback)
├── plugin.py             # OpenClaw/Hermes compatible plugin
├── api.py                # FastAPI router /api/memos/*
├── config.yaml           # Config
├── memory_store.json     # Git-committed memory store (survives wipes!)
└── __init__.py

data/memos/
└── memory_store_backup.json  # Backup
```

### Why Git-Committed Storage?

Sandbox wipes (like Aug 26 20:35 UTC) delete:
- `paint-explainer/` folder
- `output/*.mp4`
- `projects/*`
- `data/reference_videos/`

**Only committed files survive.** So `memory_store.json` is committed to git and survives.

### Usage in Voicebox

#### Python API
```python
from backend.memos_memory import memos_plugin, get_memos

# Recall before chat (like MemOS Cloud Plugin)
memories = memos_plugin.recall(query="finance Australia 40+", top_k=5)
# Returns: [{"content": "User wants winning finance topic...", ...}]

# Inject into prompt
from backend.memos_memory import get_memory_for_query
context = get_memory_for_query("finance Australia")
# Use context in LLM prompt

# Remember after chat (like MemOS Cloud Plugin saves after run)
memos_plugin.remember(
    content="User confirmed visuals that resonate work better",
    metadata={"type": "feedback", "project": "finance-australia"}
)

# Direct API like MemOS
memos = get_memos()
memos.add(content="New insight...", metadata={"topic": "editing"})
results = memos.search("editing style", top_k=3)
print(results["text_mem"])  # MemOS compatible
```

#### REST API (FastAPI)
```bash
# Add memory
curl -X POST http://localhost:8000/api/memos/add \
  -H "Content-Type: application/json" \
  -d '{"content": "Winning topic: Super Catch-Up $152k behind", "metadata": {"topic": "finance"}}'

# Search
curl -X POST http://localhost:8000/api/memos/search \
  -H "Content-Type: application/json" \
  -d '{"query": "finance Australia", "top_k": 5}'

# Get all
curl http://localhost:8000/api/memos/all

# Viewer dashboard (like memos-local-plugin/viewer/)
curl http://localhost:8000/api/memos/viewer
```

### Current Memories (Persisted)

As of Aug 26 20:53, we have 3 memories committed:

1. **Winning finance topic**: Tier1 Australia 40yo, genuine, educational, subniche Super Catch-Up $152k behind, niche bending super+tax+TTR+property
2. **Editing style**: Smart router different edit per beat, clean visuals PURE WHITE bg thick black outline flat MS-Paint style no messy visuals that resonate house couple piggy bank, voice clean 12-16 words 2-6s voice-05 perfect sync 0.2s before keyword, no cheap arrow circle
3. **Project progress**: Part 2 Batch 1 visual 11-20 DONE 50s 1.41MB with real visuals, 30 beats before wipe = 2.64 min, target 90 beats = 8.2 min, need 80 beats remaining

### For Future Chats

Every new chat will:

1. **Load** `backend/memos_memory/memory_store.json` (git-committed)
2. **Recall** relevant memories via `memos_plugin.recall(query)`
3. **Inject** into context so agent remembers:
   - Your editing style (clean visuals, no messy, smart router)
   - Winning topics (Australia super $152k gap)
   - Project progress (Batch 1 done, 80 beats remaining)
   - Voice preferences (voice-05)
   - Preview Studio Port 3001, Upload Studio Port 3000
4. **Save** new insights after chat via `remember()`
5. **Commit** to git to survive next wipe

### Upgrade to Full MemOS

When you have infrastructure (Ollama, Qdrant, Neo4j):

```python
# pip install MemoryOS
from memos.configs.mem_os import MOSConfig
from memos.mem_os.main import MOS

config = MOSConfig.from_json_file("backend/memos_memory/config.yaml")
memory = MOS(config)
memory.add(messages=[...], user_id="voicebox_user")
results = memory.search(query="finance", user_id="voicebox_user")
```

Full MemOS gives:
- Vector embeddings (nomic-embed-text)
- Graph DB (Neo4j)
- 35.24% token savings
- DeepSeek Harness support

### For Paint-Explainer Project

The finance-australia 40+ project benefits from persistent memory:

- **Before wipe**: 30 beats = 2.64 min done, editing style, winning topic
- **After wipe**: Memory recalls all that, so new chat continues Batch 4 without re-explaining
- **Visuals that resonate**: Memory stores that house/couple/piggy bank visuals work better than text-only

### Links

- MemOS Repo: https://github.com/MemTensor/MemOS
- Docs: https://memos-docs.openmem.net/home/overview/
- Cloud Plugin: https://github.com/MemTensor/MemOS-Cloud-OpenClaw-Plugin
- Local Plugin: https://github.com/MemTensor/MemOS/tree/main/apps/memos-local-plugin
- Viewer: apps/memos-local-plugin/viewer/
- Benchmarks: https://github.com/MemTensor/OmniMemEval

---

**Status**: ✅ Connected — `backend/memos_memory/` committed, API `/api/memos/*` wired, memory_store.json survives wipes via git.
