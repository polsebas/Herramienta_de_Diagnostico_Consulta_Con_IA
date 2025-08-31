from __future__ import annotations

from typing import Any, Dict, List, Optional, Protocol


class AgentRole(Protocol):
    """
    Contrato mínimo para roles de agentes bajo coordinación.
    """

    name: str

    async def act(self, context: Dict[str, Any]) -> Dict[str, Any]:
        ...

    async def respond(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        ...

    async def handoff(self) -> Optional[str]:
        ...


class TeamCoordinator:
    """
    Orquestador central en modo Coordinate.

    - Mantiene la lista de roles activos
    - Define protocolo de turnos y handoffs
    - Emite eventos para UI (placeholder)
    """

    def __init__(self, roles: Optional[List[AgentRole]] = None) -> None:
        self.roles: List[AgentRole] = roles or []

    def register_role(self, role: AgentRole) -> None:
        # Logging simple para trazabilidad inicial
        role_name = getattr(role, "name", role.__class__.__name__)
        print(f"[TeamCoordinator] Registrando rol: {role_name}")
        self.roles.append(role)

    async def coordinate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        state: Dict[str, Any] = {"context": context, "steps": []}
        for role in self.roles:
            step_in = state["context"]
            print(f"[TeamCoordinator] Ejecutando act() de {getattr(role, 'name', role.__class__.__name__)}")
            output = await role.act(step_in)
            state["steps"].append(
                {"role": getattr(role, "name", role.__class__.__name__), "output": output}
            )
            handoff_target = await role.handoff()
            if handoff_target is not None:
                state["handoff"] = handoff_target
        return state


