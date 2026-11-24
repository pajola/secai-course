"""v3 - + Retrieved-content boundary (data -> model): scan chunks, delimited prompt template."""
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

from nora import llm, rag
from nora.config import SYSTEM_PROMPT_HARDENED  # NEW: "documents are data, not instructions"
from nora.firewall import THRESHOLD, injection_score
from nora.gateway import authenticate, check_limits

app = FastAPI(title="Nora v3 - chunk scan")


class ChatIn(BaseModel):
    message: str


@app.post("/chat")
def chat(req: ChatIn, user: dict = Depends(authenticate)):
    check_limits(user, req.message, scope="v3")

    score = injection_score(req.message)
    if score > THRESHOLD:
        raise HTTPException(400, detail={"blocked_by": "prompt_firewall", "score": round(score, 3)})

    docs = rag.retrieve(req.message)
    # NEW: retrieved text crosses a trust boundary too - scan it and drop poisoned chunks
    docs = [d for d in docs if injection_score(d["text"]) <= THRESHOLD]
    # NEW: prompt template - delimit data so the model can tell it apart from instructions
    context = "\n".join(f'<document source="{d["source"]}">\n{d["text"]}\n</document>' for d in docs)
    prompt = f"{context}\n\nQuestion: {req.message}"
    answer = llm.chat(SYSTEM_PROMPT_HARDENED, prompt)
    return {"answer": answer, "sources": [d["source"] for d in docs]}
