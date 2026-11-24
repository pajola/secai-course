"""v1 - + Gateway (user -> gateway boundary): authentication, rate limit, token limit."""
from fastapi import Depends, FastAPI
from pydantic import BaseModel

from nora import llm, rag
from nora.config import SYSTEM_PROMPT
from nora.gateway import authenticate, check_limits  # NEW

app = FastAPI(title="Nora v1 - gateway")


class ChatIn(BaseModel):
    message: str


@app.post("/chat")
def chat(req: ChatIn, user: dict = Depends(authenticate)):  # NEW: who are you?
    check_limits(user, req.message, scope="v1")  # NEW: how often, how much?

    docs = rag.retrieve(req.message)
    context = "\n\n".join(d["text"] for d in docs)
    prompt = f"Context:\n{context}\n\nQuestion: {req.message}"
    answer = llm.chat(SYSTEM_PROMPT, prompt)
    return {"answer": answer, "sources": [d["source"] for d in docs]}
