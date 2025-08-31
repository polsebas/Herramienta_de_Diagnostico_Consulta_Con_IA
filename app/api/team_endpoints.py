from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from agents.team.TeamCoordinator import TeamCoordinator


logger = logging.getLogger("team")
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Agno Team Coordinator API")


class SessionCreateRequest(BaseModel):
    roles: Optional[List[str]] = Field(default_factory=list, description="Lista de roles por nombre")
    context: Dict[str, Any] = Field(default_factory=dict, description="Contexto inicial opcional")


class SessionCreateResponse(BaseModel):
    session_id: str
    status: str


class SessionStatusResponse(BaseModel):
    session_id: str
    status: str
    steps: List[Dict[str, Any]] = Field(default_factory=list)


# Estado en memoria (placeholder). Para PR-R3 se migrará a storage adecuado.
SESSIONS: Dict[str, Dict[str, Any]] = {}


@app.post("/api/team/session", response_model=SessionCreateResponse)
async def create_team_session(payload: SessionCreateRequest) -> SessionCreateResponse:
    session_id = str(uuid4())
    coordinator = TeamCoordinator(roles=[])

    # Placeholder: loggear roles declarativos hasta migrar a instancias reales
    for role_name in payload.roles:
        logger.info("Asignando rol declarado a la sesión %s: %s", session_id, role_name)

    SESSIONS[session_id] = {
        "coordinator": coordinator,
        "status": "initialized",
        "context": payload.context,
        "steps": [],
    }

    return SessionCreateResponse(session_id=session_id, status="initialized")


@app.get("/api/team/status", response_model=SessionStatusResponse)
async def get_team_status(session_id: str = Query(..., description="Identificador de la sesión")) -> SessionStatusResponse:
    session = SESSIONS.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    return SessionStatusResponse(session_id=session_id, status=session["status"], steps=session.get("steps", []))


