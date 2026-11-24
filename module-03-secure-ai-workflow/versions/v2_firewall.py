"""v2 - + Prompt firewall (user -> model boundary): Llama Prompt Guard 2 on the user's input."""
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

from nora import llm, rag
from nora.config import SYSTEM_PROMPT
from nora.firewall import THRESHOLD, injection_score  # NEW
from nora.gateway import authenticate, check_limits

app = FastAPI(title="Nora v2 - prompt firewall")


class ChatIn(BaseModel):
    message: str


@app.post("/chat")
def chat(req: ChatIn, user: dict = Depends(authenticate)):
    check_limits(user, req.message, scope="v2")

    score = injection_score(req.message)  # NEW: does the input try to override instructions?
    if score > THRESHOLD:
        raise HTTPException(400, detail={"blocked_by": "prompt_firewall", "score": round(score, 3)})

    docs = rag.retrieve(req.message)
    context = "\n\n".join(d["text"] for d in docs)
    prompt = f"Context:\n{context}\n\nQuestion: {req.message}"
    answer = llm.chat(SYSTEM_PROMPT, prompt)
    return {"answer": answer, "sources": [d["source"] for d in docs]}
