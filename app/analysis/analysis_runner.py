from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from app.config.system_selector import get_system_config
from app.analysis.repo_scanner import scan_repository
from app.analysis.doc_upgrader import detect_docs


def run_system_analysis() -> Dict[str, Any]:
    """Ejecuta el análisis mínimo del sistema.

    Genera `reports/system_overview.md` y retorna un resumen.
    """
    cfg = get_system_config() or {}
    source = cfg.get("source_folder")
    docs = cfg.get("docs_folder")
    if not source:
        raise ValueError("source_folder no configurado")

    overview = scan_repository(source)
    docs_info = detect_docs(source, docs)

    out_dir = Path(__file__).resolve().parents[2] / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "system_overview.md"

    lines = [
        "# System Overview",
        "",
        f"Root: {overview.get('root','')}\n",
        f"Files: {overview.get('file_count',0)}\n",
        f"Languages: {', '.join(sorted(overview.get('languages',{}).keys()))}\n",
        "## Detected Docs",
    ]
    for p in docs_info.get("existing_docs", []):
        lines.append(f"- {p}")

    target.write_text("\n".join(lines), encoding="utf-8")

    summary = {
        "overview": overview,
        "docs_info": docs_info,
        "artifacts": {"system_overview": str(target.resolve())},
    }
    (out_dir / "system_overview.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


