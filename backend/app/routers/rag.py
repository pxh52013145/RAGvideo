from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.dify_client import DifyChatClient, DifyConfig, DifyError
from app.services.rag_service import build_library_answer_from_resources
from app.utils.response import ResponseWrapper as R

router = APIRouter()


class RagChatRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None
    user: Optional[str] = None


@router.post("/rag/chat")
def rag_chat(data: RagChatRequest):
    cfg = DifyConfig.from_env()
    client = DifyChatClient(cfg)
    try:
        resp = client.chat(
            query=data.query,
            conversation_id=data.conversation_id,
            user=data.user,
            response_mode="blocking",
        )
    except DifyError as exc:
        return R.error(msg=str(exc), code=500)
    finally:
        client.close()

    metadata = resp.get("metadata") if isinstance(resp, dict) else {}
    resources = metadata.get("retriever_resources") if isinstance(metadata, dict) else []

    answer = resp.get("answer")
    # For "knowledge base inventory" style questions, produce a deterministic answer based on retrieval resources.
    override = build_library_answer_from_resources(query=data.query, resources=resources)
    if override:
        answer = override

    return R.success(
        {
            "answer": answer,
            "conversation_id": resp.get("conversation_id"),
            "message_id": resp.get("message_id"),
            "task_id": resp.get("task_id"),
            "retriever_resources": resources or [],
            "raw": resp,
        }
    )

