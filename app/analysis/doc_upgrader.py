from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional


def detect_docs(source_path: str, user_docs_path: Optional[str] = None) -> Dict[str, Any]:
    """Detecta documentación existente en el repo y en la carpeta de usuario.

    Implementación mínima para PR-S2; será extendida en S3.
    """
    repo = Path(source_path)
    user_docs = Path(user_docs_path) if user_docs_path else None

    found: List[str] = []
    if repo.exists():
        for candidate in [repo / "README.md", repo / "readme.md", repo / "README"]:
            if candidate.exists():
                found.append(str(candidate.resolve()))
        docs_dir = repo / "docs"
        if docs_dir.exists() and docs_dir.is_dir():
            found.append(str(docs_dir.resolve()))

    if user_docs and user_docs.exists():
        found.append(str(user_docs.resolve()))

    return {"existing_docs": sorted(set(found))}

