from __future__ import annotations

import re
from pathlib import Path
from typing import List


def generate_cursor_tasks(roadmap_md_path: str, output_dir: str = "/workspace/cursor_tasks") -> List[str]:
    """Convierte roadmap.md en tareas .md mínimas para Cursor.

    Heurística: cada item de lista genera un T####-*.md.
    """
    roadmap = Path(roadmap_md_path)
    if not roadmap.exists():
        raise FileNotFoundError("roadmap.md no encontrado")
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    titles: List[str] = []
    for line in roadmap.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^- \[ \] \((.*?)\) (.+)$", line.strip())
        if m:
            titles.append(m.group(2))

    created: List[str] = []
    for idx, title in enumerate(titles, 1):
        tid = f"T-{idx:04d}"
        target = out / f"{tid}-{re.sub(r'[^a-zA-Z0-9_-]+', '-', title)[:40]}.md"
        content = (
            f"---\n"
            f"id: {tid}\n"
            f"title: \"{title}\"\n"
            f"risk: low\n"
            f"inputs:\n  - reports/main_report.md\n  - reports/roadmap.md\n"
            f"acceptance:\n  - [ ] Ejecuta en CI\n  - [ ] Validado por usuario\n"
            f"---\n\nDescripción: Generado automáticamente desde roadmap.\n"
        )
        target.write_text(content, encoding="utf-8")
        created.append(str(target.resolve()))

    return created

