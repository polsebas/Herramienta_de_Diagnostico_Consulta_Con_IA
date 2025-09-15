from __future__ import annotations

from typing import Any, Dict, List

from app.config.system_selector import get_system_config
from app.analysis.repo_scanner import scan_repository
from app.analysis.doc_upgrader import detect_docs


def run_preflight() -> Dict[str, Any]:
    """Verifica configuración y estado mínimo del proyecto.

    Retorna un dict con:
      - configured: bool
      - missing: List[str]
      - source_exists: bool | None
      - docs_exists: bool | None
      - overview: Dict | None
      - docs_info: Dict | None
      - ready_for_analysis: bool
    """
    cfg = get_system_config() or {}
    source_folder = cfg.get("source_folder")
    docs_folder = cfg.get("docs_folder")

    missing: List[str] = []
    source_exists = None
    docs_exists = None

    if not source_folder:
        missing.append("source_folder")
    if not docs_folder:
        missing.append("docs_folder")

    if source_folder:
        try:
            import os
            source_exists = os.path.isdir(source_folder)
            if not source_exists and "source_folder" not in missing:
                missing.append("source_folder")
        except Exception:
            source_exists = False
            if "source_folder" not in missing:
                missing.append("source_folder")

    if docs_folder:
        try:
            import os
            docs_exists = os.path.isdir(docs_folder)
            if not docs_exists and "docs_folder" not in missing:
                missing.append("docs_folder")
        except Exception:
            docs_exists = False
            if "docs_folder" not in missing:
                missing.append("docs_folder")

    configured = len(missing) == 0

    overview = None
    docs_info = None
    if source_folder and source_exists:
        try:
            overview = scan_repository(source_folder)
        except Exception:
            overview = None
        try:
            docs_info = detect_docs(source_folder, docs_folder)
        except Exception:
            docs_info = None

    ready_for_analysis = bool(configured and source_exists)

    return {
        "configured": configured,
        "missing": missing,
        "source_exists": source_exists,
        "docs_exists": docs_exists,
        "overview": overview,
        "docs_info": docs_info,
        "ready_for_analysis": ready_for_analysis,
    }


