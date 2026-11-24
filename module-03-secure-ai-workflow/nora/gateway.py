"""Boundary 1: user -> gateway. Who are you, how often, how much?"""
import tiktoken
from fastapi import Header, HTTPException
from limits import parse, storage, strategies

# In production: an identity provider. Here: API keys mapped to users and their groups.
USERS = {
    "key-giulia": {"name": "giulia", "groups": ["public", "staff", "hr"]},
    "key-marco": {"name": "marco", "groups": ["public", "staff", "customer"]},
    "key-loadtest": {"name": "loadtest", "groups": ["public"]},
}

RATE = parse("10/minute")
limiter = strategies.MovingWindowRateLimiter(storage.MemoryStorage())

MAX_PROMPT_TOKENS = 1000
encoder = tiktoken.get_encoding("cl100k_base")  # approximation of the model's tokenizer


def authenticate(x_api_key: str | None = Header(default=None)) -> dict:
    user = USERS.get(x_api_key or "")
    if user is None:
        raise HTTPException(401, detail={"blocked_by": "authentication"})
    return user


def check_limits(user: dict, message: str, scope: str = "nora") -> None:
    if not limiter.hit(RATE, scope, user["name"]):
        raise HTTPException(429, detail={"blocked_by": "rate_limit"})
    if len(encoder.encode(message)) > MAX_PROMPT_TOKENS:
        raise HTTPException(413, detail={"blocked_by": "token_limit"})
