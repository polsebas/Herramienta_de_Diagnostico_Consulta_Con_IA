from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List


def scan_repository(source_path: str) -> Dict[str, Any]:
    """Escanea rápidamente la estructura del repositorio.

    Nota: Implementación mínima (sin dependencias externas). Versión ampliada en PR-S2.
    """
    root = Path(source_path)
    if not root.exists() or not root.is_dir():
        raise ValueError("Ruta de repositorio inválida")

    file_count = 0
    extensions: Dict[str, int] = {}
    docs_detected: List[str] = []

    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            file_count += 1
            ext = Path(name).suffix.lower() or ""
            extensions[ext] = extensions.get(ext, 0) + 1
            # Heurística docs
            if name.lower() in {"readme.md", "readme"}:
                docs_detected.append(str(Path(dirpath) / name))
            if Path(dirpath).name.lower() == "docs":
                docs_detected.append(str(Path(dirpath)))

    # Lenguajes (heurística por extensión)
    lang_map = {
        ".py": "python",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".js": "javascript",
        ".java": "java",
        ".go": "go",
        ".rs": "rust",
    }
    languages: Dict[str, int] = {}
    for ext, count in extensions.items():
        lang = lang_map.get(ext)
        if lang:
            languages[lang] = languages.get(lang, 0) + count

    return {
        "root": str(root.resolve()),
        "file_count": file_count,
        "extensions": extensions,
        "languages": languages,
        "docs_detected": sorted(set(docs_detected)),
    }

