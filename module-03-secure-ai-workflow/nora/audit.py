"""Audit trail: one JSON line per request - who, what, which control decided, and why.
The prompt itself is redacted before it is written: logs must not become a PII store."""
from pathlib import Path

import structlog

from nora.sanitize import redact

Path("logs").mkdir(exist_ok=True)
log_file = open("logs/audit.jsonl", "a", buffering=1)

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.WriteLoggerFactory(file=log_file),
)
audit = structlog.get_logger()


def record(user: str, message: str, decision: str, **fields) -> None:
    prompt, _ = redact(message)  # redact first, then cut: a cut could split an IBAN and hide it from the detector
    audit.info("chat_request", user=user, decision=decision, prompt=prompt[:300], **fields)
