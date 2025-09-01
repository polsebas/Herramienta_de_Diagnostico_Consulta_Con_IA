from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional


def generate_main_report(
    overview: Dict[str, Any],
    history: Optional[Dict[str, Any]] = None,
    output_dir: str = str(Path(__file__).resolve().parents[2] / "reports"),
) -> str:
    """Genera un main_report.md mínimo combinando overview + history.

    Retorna la ruta del archivo generado.
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    target = out / "main_report.md"

    lines = ["# Informe Principal (Preliminar)", ""]
    lines.append("## Overview")
    lines.append(f"Archivos: {overview.get('file_count', 0)}")
    lines.append(f"Lenguajes: {', '.join(sorted(overview.get('languages', {}).keys()))}")
    lines.append("")
    if history:
        lines.append("## Historia (resumen)")
        lines.append(str({k: history.get(k) for k in list(history.keys())[:5]}))
        lines.append("")

    target.write_text("\n".join(lines), encoding="utf-8")
    return str(target.resolve())

