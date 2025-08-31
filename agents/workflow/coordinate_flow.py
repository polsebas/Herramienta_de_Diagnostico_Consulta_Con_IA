from __future__ import annotations

from typing import Any, Dict, List

from agents.roles import AnalyzerAgent, DocGenAgent, RoadmapAgent, CursorTaskAgent
from agents.team.TeamCoordinator import TeamCoordinator
from app.human_loop import HumanLoopManager


async def run_coordinate_flow(initial_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Flujo de orquestación completo (Coordinate):
    1) Analyzer -> 2) DocGen -> 3) Roadmap -> 4) CursorTask
    Incluye pause points human-in-the-loop cuando se detectan áreas críticas.
    """
    coordinator = TeamCoordinator(
        roles=[AnalyzerAgent(), DocGenAgent(), RoadmapAgent(), CursorTaskAgent()]
    )
    human = HumanLoopManager()

    # Pause point ejemplo: si el contexto declara cambios críticos
    critical_paths: List[str] = initial_context.get("critical_paths", [])
    if critical_paths:
        approval_id = await human.request_approval(
            action_type="coordinate_flow_critical_paths",
            description="Se detectaron rutas críticas, solicitar aprobación para continuar",
            payload={"paths": critical_paths},
            requester="TeamCoordinator",
        )
        approved = await human.wait_for_approval(approval_id, timeout_seconds=5)
        if not approved:
            return {
                "status": "halted",
                "reason": "approval_rejected_or_timeout",
                "approval_id": approval_id,
            }

    async def on_event(event: Dict[str, Any]) -> None:
        # Hook para emitir eventos desde el flujo hacia la UI
        try:
            # Lazy import para evitar dependencia cíclica
            from app.api.team_endpoints import publish_event

            await publish_event("team", {"source": "coordinate_flow", **event})
        except Exception:
            # Evitar romper el flujo por errores de notificación
            pass

    result = await coordinator.coordinate(initial_context, on_event=on_event)
    result["status"] = "completed"
    return result


