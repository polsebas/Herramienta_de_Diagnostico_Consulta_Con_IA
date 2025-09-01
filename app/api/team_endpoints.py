from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from uuid import uuid4
from time import time

from fastapi import FastAPI, HTTPException, Query
from fastapi import WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse
from pydantic import BaseModel, Field

from agents.team.TeamCoordinator import TeamCoordinator
from agents.workflow.coordinate_flow import run_coordinate_flow


logger = logging.getLogger("team")
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Agno Team Coordinator API")

# CORS para Agent UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
EVENT_SUBSCRIBERS: Dict[str, List[WebSocket]] = {"team": []}


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
        "created_at": int(time()),
        "title": f"Team session {session_id[:8]}",
    }

    return SessionCreateResponse(session_id=session_id, status="initialized")


@app.get("/api/team/status", response_model=SessionStatusResponse)
async def get_team_status(session_id: str = Query(..., description="Identificador de la sesión")) -> SessionStatusResponse:
    session = SESSIONS.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    return SessionStatusResponse(session_id=session_id, status=session["status"], steps=session.get("steps", []))


class RunRequest(BaseModel):
    session_id: str
    context_override: Optional[Dict[str, Any]] = Field(default=None, description="Contexto para sobrescribir/merge")


@app.post("/api/team/run", response_model=SessionStatusResponse)
async def run_team_flow(payload: RunRequest) -> SessionStatusResponse:
    session = SESSIONS.get(payload.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")

    # Preparar contexto
    context = dict(session.get("context", {}))
    if payload.context_override:
        context.update(payload.context_override)

    SESSIONS[payload.session_id]["status"] = "running"

    # Ejecutar flujo coordinate
    result = await run_coordinate_flow(context)
    steps = result.get("steps", [])
    status = result.get("status", "completed")

    SESSIONS[payload.session_id]["steps"] = steps
    SESSIONS[payload.session_id]["status"] = status

    return SessionStatusResponse(session_id=payload.session_id, status=status, steps=steps)

# --- Agent UI Adapter: Playground-compatible endpoints ---

@app.get("/v1/playground/status")
async def playground_status() -> Dict[str, Any]:
    return {"status": "ok", "sessions": len(SESSIONS)}


@app.get("/v1/playground/teams")
async def playground_teams() -> List[Dict[str, Any]]:
    # Un único team descriptor mínimo
    return [
        {
            "team_id": "team_default",
            "name": "Agno Team",
            "description": "Coordinated multi-agent team",
            "model": {"provider": "custom"},
            "storage": False,
        }
    ]


@app.get("/v1/playground/teams/{team_id}/sessions")
async def playground_team_sessions(team_id: str) -> List[Dict[str, Any]]:
    # Mapear nuestras SESSIONS a SessionEntry esperado por Agent UI
    entries: List[Dict[str, Any]] = []
    for sid, s in SESSIONS.items():
        entries.append(
            {
                "session_id": sid,
                "title": s.get("title", sid[:8]),
                "created_at": s.get("created_at", int(time())),
            }
        )
    return entries


@app.get("/v1/playground/teams/{team_id}/sessions/{session_id}")
async def playground_team_session(team_id: str, session_id: str) -> Dict[str, Any]:
    s = SESSIONS.get(session_id)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    # Transformar a estructura esperada
    runs = [
        {
            "message": {
                "role": "user",
                "content": "Run coordinate flow",
                "created_at": s.get("created_at", int(time())),
            },
            "response": {
                "content": str(s.get("steps", [])),
                "created_at": int(time()),
            },
        }
    ] if s.get("steps") else []
    return {
        "session_id": session_id,
        "team_id": team_id,
        "user_id": None,
        "memory": {"runs": runs},
        "team_data": {},
    }


@app.post("/v1/playground/teams/{team_id}/runs")
async def playground_team_run(team_id: str, request: Request):
    """Endpoint de ejecución con streaming compatible con Agent UI.
    Soporta FormData o JSON. Emite objetos JSON concatenados (sin delimitadores) para parsing incremental.
    """
    created_ts = int(time())

    # Leer payload flexible (FormData o JSON)
    try:
        content_type = request.headers.get("content-type", "")
        if content_type.startswith("application/json"):
            payload = await request.json()
        else:
            form = await request.form()
            payload = {k: form.get(k) for k in form.keys()}
    except Exception:
        payload = {}

    session_id = (payload.get("session_id") or "").strip()
    # Crear sesión si no existe
    if not session_id or session_id not in SESSIONS:
        session_id = str(uuid4())
        SESSIONS[session_id] = {
            "coordinator": TeamCoordinator(roles=[]),
            "status": "initialized",
            "context": {},
            "steps": [],
            "created_at": created_ts,
            "title": f"Team session {session_id[:8]}",
        }

    async def event_stream():
        # RunStarted
        started = {
            "event": "TeamRunStarted",
            "session_id": session_id,
            "created_at": created_ts,
        }
        yield json_dump(started)

        # Ejecutar flujo y streamear pasos
        result = await run_coordinate_flow(SESSIONS[session_id].get("context", {}))
        steps = result.get("steps", [])
        SESSIONS[session_id]["steps"] = steps
        SESSIONS[session_id]["status"] = result.get("status", "completed")

        # Emitir contenido por cada step
        for step in steps:
            content_obj = {
                "event": "TeamRunResponseContent",
                "session_id": session_id,
                "created_at": int(time()),
                "content_type": "text/plain",
                "content": f"{step.get('role')}: {step.get('output')}",
            }
            yield json_dump(content_obj)

        # RunCompleted
        completed = {
            "event": "TeamRunCompleted",
            "session_id": session_id,
            "created_at": int(time()),
        }
        yield json_dump(completed)

    return StreamingResponse(event_stream(), media_type="application/json")


def json_dump(obj: Dict[str, Any]) -> str:
    import json

    return json.dumps(obj, ensure_ascii=False)


async def publish_event(channel: str, event: Dict[str, Any]) -> None:
    # Persistir en audit.jsonl
    try:
        import json, os
        os.makedirs("logs", exist_ok=True)
        with open("logs/audit.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps({"channel": channel, **event}) + "\n")
    except Exception as e:
        logger.error("Error escribiendo audit log: %s", e)

    # Emitir a suscriptores WebSocket
    stale: List[WebSocket] = []
    for ws in EVENT_SUBSCRIBERS.get(channel, []):
        try:
            await ws.send_json(event)
        except Exception:
            stale.append(ws)
    for ws in stale:
        try:
            EVENT_SUBSCRIBERS[channel].remove(ws)
        except ValueError:
            pass


@app.websocket("/ws/team/events")
async def team_events_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    EVENT_SUBSCRIBERS.setdefault("team", []).append(websocket)
    try:
        while True:
            # Mantener viva la conexión; ignoramos mensajes entrantes
            await websocket.receive_text()
    except WebSocketDisconnect:
        try:
            EVENT_SUBSCRIBERS["team"].remove(websocket)
        except ValueError:
            pass

