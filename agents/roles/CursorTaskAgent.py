from __future__ import annotations

from typing import Any, Dict


class CursorTaskAgent:
    name = "CursorTaskAgent"

    async def act(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Placeholder: emite paquetes de tareas para Cursor
        tasks = [
            {"file": "app/api/team_endpoints.py", "action": "add-tests"},
            {"file": "agents/team/TeamCoordinator.py", "action": "add-ui-events"},
        ]
        return {"cursor_tasks": tasks}

    async def respond(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {"ack": True, "tasks": input_data.get("cursor_tasks", [])}

    async def handoff(self) -> str | None:
        return None


