"""v6 - + Audit trail (all boundaries): one JSON line per request, prompts redacted before logging."""
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
from pydantic import BaseModel

from nora import llm, rag
from nora.audit import record  # NEW
from nora.config import SYSTEM_PROMPT_HARDENED
from nora.firewall import THRESHOLD, injection_score
from nora.gateway import authenticate, check_limits
from nora.sanitize import redact

app = FastAPI(title="Nora v6 - audit trail")


class ChatIn(BaseModel):
    message: str


@app.post("/chat")
def chat(req: ChatIn, request: Request, user: dict = Depends(authenticate)):
    request.state.user, request.state.message = user["name"], req.message
    check_limits(user, req.message, scope="v6")

    score = injection_score(req.message)
    if score > THRESHOLD:
        raise HTTPException(400, detail={"blocked_by": "prompt_firewall", "score": round(score, 3)})

    # Least privilege at retrieval: the user only searches documents their groups may read.
    # The model never sees what the user is not entitled to - no prompt can leak it.
    docs = rag.retrieve(req.message, where={"classification": {"$in": user["groups"]}})
    # Retrieved text crosses a trust boundary too: scan it and drop poisoned chunks
    dropped = [d["source"] for d in docs if injection_score(d["text"]) > THRESHOLD]
    docs = [d for d in docs if d["source"] not in dropped]
    # Prompt template: delimit data so the model can tell it apart from instructions
    context = "\n".join(f'<document source="{d["source"]}">\n{d["text"]}\n</document>' for d in docs)
    prompt = f"{context}\n\nQuestion: {req.message}"
    answer = llm.chat(SYSTEM_PROMPT_HARDENED, prompt)

    # Model -> user boundary: redact sensitive data before it leaves the system
    answer, redacted = redact(answer)
    sources = [d["source"] for d in docs]
    record(user["name"], req.message, "allow", firewall_score=round(score, 3),
           sources=sources, dropped_chunks=dropped, redacted=redacted)
    return {"answer": answer, "sources": sources, "redacted": redacted}


@app.exception_handler(HTTPException)
async def audit_blocked(request: Request, exc: HTTPException):
    """Every blocked request is logged too - blocks are the most interesting events."""
    record(getattr(request.state, "user", "anonymous"), getattr(request.state, "message", ""),
           "block", **(exc.detail if isinstance(exc.detail, dict) else {"blocked_by": str(exc.detail)}))
    return await http_exception_handler(request, exc)
