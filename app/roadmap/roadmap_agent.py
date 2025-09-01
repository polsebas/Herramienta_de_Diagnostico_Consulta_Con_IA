from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


class RoadmapAgent:
    """Agente mínimo que propone un roadmap a partir del overview.

    Versión placeholder; en S4 integrará interacción con UI.
    """

    def propose_roadmap(self, overview: Dict[str, Any]) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        if overview.get("languages"):
            items.append({"title": "Documentar setup y arquitectura", "priority": "high"})
        items.append({"title": "Mejorar cobertura de docs", "priority": "medium"})
        return items

    def commit_roadmap(self, items: List[Dict[str, Any]], output_dir: str = "/workspace/reports") -> str:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        target = out / "roadmap.md"
        lines = ["# Roadmap (Borrador)", ""]
        for i, it in enumerate(items, 1):
            lines.append(f"- [ ] ({it.get('priority','')}) {it.get('title','Item ' + str(i))}")
        target.write_text("\n".join(lines), encoding="utf-8")
        return str(target.resolve())

