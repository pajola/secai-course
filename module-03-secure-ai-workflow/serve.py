"""All Nora versions in one server:  uv run uvicorn serve:app --port 8000
Each version answers at /vN/chat (e.g. /v0/chat, /v4/chat)."""
from fastapi import FastAPI

from versions import (v0_naked, v1_gateway, v2_firewall, v3_chunk_scan,
                      v4_least_privilege, v5_redaction, v6_audit)

app = FastAPI(title="Nora - all versions")
for version in (v0_naked, v1_gateway, v2_firewall, v3_chunk_scan,
                v4_least_privilege, v5_redaction, v6_audit):
    app.mount("/" + version.__name__.split(".")[-1].split("_")[0], version.app)
