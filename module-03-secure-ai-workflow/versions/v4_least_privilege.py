"""v4 - + Least privilege at retrieval (data -> retriever): users search only what their groups may read."""
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

from nora import llm, rag
from nora.config import SYSTEM_PROMPT_HARDENED
from nora.firewall import THRESHOLD, injection_score
from nora.gateway import authenticate, check_limits

app = FastAPI(title="Nora v4 - least privilege")


class ChatIn(BaseModel):
    message: str


@app.post("/chat")
def chat(req: ChatIn, user: dict = Depends(authenticate)):
    check_limits(user, req.message, scope="v4")

    score = injection_score(req.message)
    if score > THRESHOLD:
        raise HTTPException(400, detail={"blocked_by": "prompt_firewall", "score": round(score, 3)})

    # NEW: filter by the user's groups at query time.
    # The model never sees what the user is not entitled to - no prompt can leak it.
    docs = rag.retrieve(req.message, where={"classification": {"$in": user["groups"]}})
    docs = [d for d in docs if injection_score(d["text"]) <= THRESHOLD]
    context = "\n".join(f'<document source="{d["source"]}">\n{d["text"]}\n</document>' for d in docs)
    prompt = f"{context}\n\nQuestion: {req.message}"
    answer = llm.chat(SYSTEM_PROMPT_HARDENED, prompt)
    return {"answer": answer, "sources": [d["source"] for d in docs]}
