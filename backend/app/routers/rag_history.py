from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.rag_history_manager import RagHistoryManager
from app.utils.response import ResponseWrapper as R

router = APIRouter()


def _history() -> RagHistoryManager:
    # Scope history storage by (active dify_profile + active app scheme).
    return RagHistoryManager()


class RagStatePayload(BaseModel):
    user_id: Optional[str] = None
    current_conversation_id: Optional[str] = None
    conversations: list[dict[str, Any]] = Field(default_factory=list)


class RagConversationPatch(BaseModel):
    title: Optional[str] = None
    difyConversationId: Optional[str] = None
    dify_conversation_id: Optional[str] = None


class RagMessagePayload(BaseModel):
    id: str
    role: str
    content: str
    createdAt: Optional[str] = None
    resources: Optional[list[Any]] = None


@router.get("/rag/state")
def get_rag_state():
    return R.success(_history().get_state())


@router.post("/rag/state")
def set_rag_state(data: RagStatePayload):
    return R.success(_history().replace_state(data.model_dump()))


@router.put("/rag/current/{conversation_id}")
def set_rag_current(conversation_id: str):
    return R.success(_history().set_current_conversation(conversation_id))


@router.put("/rag/conversations/{conversation_id}")
def upsert_conversation(conversation_id: str, patch: RagConversationPatch):
    try:
        conv = _history().upsert_conversation(conversation_id, patch.model_dump(exclude_none=True))
        return R.success(conv)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/rag/conversations/{conversation_id}/messages")
def append_message(conversation_id: str, msg: RagMessagePayload):
    try:
        conv = _history().append_message(conversation_id, msg.model_dump(exclude_none=True))
        return R.success(conv)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.delete("/rag/conversations/{conversation_id}")
def delete_conversation(conversation_id: str):
    return R.success(_history().delete_conversation(conversation_id))


@router.delete("/rag/conversations")
def clear_conversations():
    return R.success(_history().clear())
