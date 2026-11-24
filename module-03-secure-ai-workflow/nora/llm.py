import ollama

from nora.config import CHAT_MODEL


def chat(system: str, user: str) -> str:
    response = ollama.chat(
        model=CHAT_MODEL,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        options={"temperature": 0, "num_predict": 256},
    )
    return response["message"]["content"]
