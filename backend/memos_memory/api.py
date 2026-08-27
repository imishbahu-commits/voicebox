"""
MemOS API for Voicebox Backend
Provides REST API for persistent memory

Endpoints:
- POST /api/memos/add - Add memory
- POST /api/memos/search - Search memories
- GET /api/memos/all - Get all memories
- GET /api/memos/viewer - Viewer dashboard data
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# Import with fallback
try:
    from .memos_integration import get_memos
    from .plugin import memos_plugin
except ImportError:
    # Fallback for direct import
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from memos_integration import get_memos
    memos_plugin = get_memos()

router = APIRouter(prefix="/api/memos", tags=["memos"])

class AddMemoryRequest(BaseModel):
    content: Optional[str] = None
    messages: Optional[List[Dict[str, str]]] = None
    memory_type: str = "text"
    metadata: Optional[Dict[str, Any]] = None
    user_id: str = "voicebox_user"

class SearchMemoryRequest(BaseModel):
    query: str
    top_k: int = 5
    user_id: str = "voicebox_user"

@router.post("/add")
async def add_memory(request: AddMemoryRequest):
    """Add memory - like MemOS Cloud API /product/add"""
    try:
        memos = get_memos(user_id=request.user_id)
        result = memos.add(
            messages=request.messages,
            content=request.content,
            memory_type=request.memory_type,
            metadata=request.metadata
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search")
async def search_memory(request: SearchMemoryRequest):
    """Search memories - like MemOS search"""
    try:
        memos = get_memos(user_id=request.user_id)
        result = memos.search(query=request.query, top_k=request.top_k)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/all")
async def get_all_memories(user_id: str = "voicebox_user"):
    """Get all memories"""
    try:
        memos = get_memos(user_id=user_id)
        memories = memos.get_all()
        return {
            "user_id": user_id,
            "count": len(memories),
            "memories": memories
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/viewer")
async def viewer_data(user_id: str = "voicebox_user"):
    """Viewer dashboard - like memos-local-plugin/viewer/"""
    try:
        memos = get_memos(user_id=user_id)
        memories = memos.get_all()
        return {
            "total_memories": len(memories),
            "memories": memories[-20:],
            "user_id": user_id,
            "version": "2.0-stardust",
            "source": "https://github.com/MemTensor/MemOS",
            "storage": "json (git-committed) + backup"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{memory_id}")
async def delete_memory(memory_id: str, user_id: str = "voicebox_user"):
    """Delete memory"""
    try:
        memos = get_memos(user_id=user_id)
        result = memos.delete(memory_id=memory_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
