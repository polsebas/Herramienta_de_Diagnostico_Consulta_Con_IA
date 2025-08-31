from __future__ import annotations

from typing import Any, Dict


class RoadmapAgent:
    name = "RoadmapAgent"

    async def act(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Placeholder: sintetiza un plan de trabajo
        plan = [
            {"id": "R2-1", "task": "Migrar subagentes a roles"},
            {"id": "R3-1", "task": "Implementar coordinate_flow"},
        ]
        return {"plan": plan, "inputs_seen": list(context.keys())}

    async def respond(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {"ack": True, "planned_items": len(input_data.get("plan", []))}

    async def handoff(self) -> str | None:
        return "CursorTaskAgent"


