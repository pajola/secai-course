"""v0 - Naked Nora: no controls at all."""
from fastapi import FastAPI
from pydantic import BaseModel

from nora import llm, rag
from nora.config import SYSTEM_PROMPT

app = FastAPI(title="Nora v0 - naked")


class ChatIn(BaseModel):
    message: str


@app.post("/chat")
def chat(req: ChatIn):
    docs = rag.retrieve(req.message)
    context = "\n\n".join(d["text"] for d in docs)
    prompt = f"Context:\n{context}\n\nQuestion: {req.message}"
    answer = llm.chat(SYSTEM_PROMPT, prompt)
    return {"answer": answer, "sources": [d["source"] for d in docs]}
