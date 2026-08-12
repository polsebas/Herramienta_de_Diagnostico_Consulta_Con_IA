# Proyecto archivado — agosto 2026

**Estado:** archivado / sin desarrollo activo  
**Fecha de decisión:** 2026-08-12  
**Último desarrollo relevante:** septiembre 2025

## Por qué lo cerramos

Este repo nació cuando los agentes de desarrollo y los asistentes con contexto de repo eran mucho más limitados. La apuesta — RAG + subagentes + human-in-the-loop + paquetes de tareas para Cursor — tenía sentido como experimento.

En 2026, herramientas como **Cursor** (y agentes similares) cubren la mayor parte de ese valor con prompts y contexto nativo del repositorio. Seguir este código como producto sería competir con plataformas que ya entregan ejecución, UX y velocidad de iteración que un side project no puede sostener.

Cerramos a propósito, no por olvido.

## Alcance honesto de lo construido

Lo que hay es sobre todo un **prototipo / spike**:

- Andamiaje útil alrededor de specs, aprobaciones HITL, formas de retrieval, endpoints FastAPI y cableado de Agent UI
- Muchos caminos caen a **simulación / fallback** si faltan Milvus, ML o un cliente LLM
- `agno` aparecía en dependencias, pero el “team” es un coordinator propio con roles placeholder
- La documentación y el roadmap describían metas enterprise y métricas que eran **aspiracionales**, no evidencia de producción

Las afirmaciones viejas de “100% completo” o ROI enterprise en docs históricas quedan como **narrativa obsoleta**, no como verdad actual.

## Qué valió la pena aprender

1. **Wedge antes que plataforma** — “informe → roadmap editable → tasks Cursor aprobadas con auditoría” es una idea más nítida que “RAG enterprise”.
2. **La simulación esconde el fallo** — fallbacks que inventan retrieval/LLM hacen pasar demos y frenan el producto.
3. **Docs ≠ terminado** — medir progreso por PRs mergeados y auditorías de “el archivo existe” no es un E2E usable.
4. **Timing de mercado** — un spike útil puede quedar viejo; archivar es un resultado válido.

## Qué se podría reusar (en otro lado)

Si extraés algo a un kit chico, preferí estas ideas antes que migrar el monorepo entero:

| Idea | Dónde vivía | Nota |
|------|-------------|------|
| Contratos de tarea (goal, risk, format, acceptance) | `app/spec_layer.py`, `app/specs/` | Quedate con el schema; tirate el ML classifier |
| Aprobación humana + audit trail | `app/human_loop.py`, `logs/audit.jsonl` | Quedate con el modelo; no arrastres Slack/enterprise a medias |
| Templates markdown para tasks de Cursor | `app/cursor_tasks/`, ejemplos en docs | Sirve como formato de packs/prompts |
| Preflight “needs configuration” | `app/analysis/preflight.py` | Patrón simple de UX |

**No** portes Milvus/BM25 simulado, `advanced_contracts`, ni los roles Agno placeholder tal cual.

## Cómo archivar en GitHub

Después de mergear este cierre a `main`:

1. Repo **Settings → General → Danger Zone → Archive this repository**
2. Opcional: descripción `ARCHIVED — spike 2025; ver CIERRE.md`

## Soporte

No hay features, fixes ni roadmap previstos. Issues y PRs nuevos deberían cerrarse como fuera de alcance de un proyecto archivado.

English version: [ARCHIVE.md](ARCHIVE.md)
