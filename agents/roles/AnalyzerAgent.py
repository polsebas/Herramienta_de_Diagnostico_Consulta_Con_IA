from __future__ import annotations

from typing import Any, Dict


class AnalyzerAgent:
    name = "AnalyzerAgent"

    async def act(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Placeholder: extrae insights básicos del contexto
        return {"insights": ["repo_scanned", "dependencies_ok"], "context_size": len(str(context))}

    async def respond(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {"ack": True, "received": list(input_data.keys())}

    async def handoff(self) -> str | None:
        return "DocGenAgent"


