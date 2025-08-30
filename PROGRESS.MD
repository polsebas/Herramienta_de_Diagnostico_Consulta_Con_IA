# Progress Report – Herramienta de Diagnóstico y Consulta con IA
**Versión:** 2025-08-30  
**Propósito:** Documento vivo para guiar la evolución del proyecto desde un RAG simple hacia un **agente semi-autónomo administrador de proyectos** con *human-in-the-loop*, trazabilidad y flujos asincrónicos (inspirados en HumanLayer y prácticas de Context Engineering).

---

## 1) Análisis de la respuesta anterior y reflexión

### 1.1 Robustez: definición aplicada
En este proyecto, **robustez** significa:
- **Confiabilidad**: respuestas estables ante cambios en el repo/formato.
- **Control humano**: puntos de aprobación para acciones sensibles.
- **Escalabilidad**: agentes trabajando en background y orquestación de subtareas.
- **Auditabilidad**: trazabilidad completa de decisiones y dependencias.

**Caso real (falta de auditabilidad):**  
Si el agente propone un plan para un issue sin registrar por qué eligió ciertas tareas (fuentes, métricas y reglas), el equipo:
- No podrá reproducir la decisión ni entender supuestos.
- Perderá confianza y-> rechazará la automatización.
- La falta de registros dificultará revertir cambios o auditar fallos (p. ej. si un test no cubrió un caso crítico).

### 1.2 Human-in-the-Loop y Human-as-Tool: cómo decidir "puntos críticos"
Estrategia práctica:
- **Reglas predefinidas (primer nivel):**
  - Si PR/issue afecta rutas o carpetas sensibles: `/auth/`, `/payments/`, `/migrations/`, `/infra/`.
  - Si el diff incluye cambios en DB schemas o permisos, pausar.
  - Si etiqueta = `high-priority` o `security`, pausar.
- **Reglas dinámicas (segundo nivel):**
  - Scoring por riesgo: combina heurísticas (nº archivos, tests tocados, cobertura) y ML (clasificador de riesgo basado en históricos).
  - Si score_riesgo > threshold → trigger human-in-loop.

### 1.3 Automatización de subtareas (Cursor background agents)
Diseño de opciones configurables:
- **Modo conservador:** Genera *draft PRs* y artefactos (tests, docs) pero **espera confirmación** humana antes de publicar/remotear.
- **Modo asistido (semi-autónomo):** Crea drafts y, con aprobación humana por notificación (Slack/GitHub comment), empuja branch.
- **Modo productivo (NO recomendado sin políticas):** autopush/merge en áreas seguras (boilerplate, docs), con auditoría automática.

Por defecto, implementaremos **modo conservador** y permitiremos configuración por repo/team.

### 1.4 Priorización de riesgos
Prioridad inicial (más crítico → menos crítico):
1. **Pérdida de trazabilidad / auditabilidad** — crítico: sin logs y links a fuentes las decisiones son irreproducibles.  
2. **Decisiones prematuras (merge / cambios sensibles)** — alto: puede introducir regresiones o fallos en producción.  
3. **Generación de propuestas irrelevantes ("ruido")** — medio: reduce confianza y desperdicia tiempo humano.  

La mitigación prioriza trazabilidad y gates humanos en cambios sensibles antes que la completa automatización.

---

## 2) Análisis del repositorio HumanLayer (lecciones clave a aplicar)

### 2.1 Fortalezas relevantes
- **Human-in-the-loop**: flujos de aprobaciones asincrónicas (Slack, email) para evitar acciones sin supervisión.
- **Workflows asincrónicos**: agentes que trabajan en background y notifican al humano en puntos de decisión.
- **Modularidad para herramientas externas**: fácil integración con APIs (GitHub, Slack, etc.).
- **Ejemplos y plantillas**: usan scripts de ejemplo que sirven como blueprint (p. ej. lead_gen_assistant.py).

### 2.2 Cómo adaptar al proyecto
- Añadir hooks de notificación y aprobación (Slack/GitHub comments) antes de ejecutar acciones sensibles.
- Orquestar flujos: Agent principal → subagentes (retrieval, analysis, plan, execution) → notificar/human-approval → background worker (Cursor) ejecuta subtareas seguras.
- Indexar metadata de PRs/issues en Milvus y usar RAG para respuestas/contexto.

---

## 3) Integración práctica: diseño y snippets

### 3.1 Indexar PRs / Issues en Milvus (concepto)
- Metadata a indexar por item:
  - `id`, `type` (pr/issue), `repo`, `title`, `body`, `files[]`, `author`, `labels[]`, `created_at`, `updated_at`, `embedding`, `raw_text`

**Pseudocódigo:**
```python
from github import Github

def index_pr_metadata(milvus_client, repo_name, pr_number, embed_fn):
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    text = pr.title + "\n\n" + pr.body
    files = [f.filename for f in pr.get_files()]
    vector = embed_fn(text)
    item = {
      "id": f"pr:{repo_name}:{pr_number}",
      "type": "pr",
      "repo": repo_name,
      "title": pr.title,
      "body": pr.body,
      "files": files,
      "created_at": int(pr.created_at.timestamp()),
      "embedding": vector,
      "raw_text": text
    }
    milvus_client.insert([item])
3.2 Check de acción crítica (inspirado HumanLayer)
async def check_critical_action(plan: dict, files_affected: list) -> bool:
    # reglas rápidas
    critical_paths = ["/auth/", "/payments/", "/migrations/", "/infra/"]
    if any(any(p in f for p in critical_paths) for f in files_affected):
        await notify_slack("Plan propuesto afecta código crítico. Aprobar?", plan)
        return await wait_for_human_approval()  # espera respuesta humana
    return True

3.3 Notificación y espera (ejemplo Slack)
import aiohttp
async def notify_slack(message: str, payload: dict):
    async with aiohttp.ClientSession() as session:
        await session.post(SLACK_WEBHOOK_URL, json={"text": message, "attachments": [payload]})

async def wait_for_human_approval(timeout_hours=24):
    # Implementar webhook listener o polling sobre Slack/GitHub comment
    # Retorna True/False
    ...

3.4 Human-as-tool: consulta puntual

Agente genera una question card y la envía (Slack/GitHub), espera respuesta y la incorpora al plan.

4) Propuesta de flujo (Research → Plan → Implement) con HumanLayer ideas

Research

Recuperar contexto del repo + PR/issue desde Milvus y GitHub.

Rerank y seleccionar 3–5 chunks relevantes.

Plan

Generar contrato (spec-first): objetivos, pasos, riesgos, outputs esperados.

Analizar archivos afectados y calcular riesgo.

Si riesgo > threshold → trigger human-in-loop (notificación y pausa).

Implement

Con aprobación: lanzar background agents en Cursor para tareas seguras:

crear draft PR con cambios boilerplate,

generar tests unitarios/e2e preliminares,

agregar documentación de cambios.

Registrar cada acción en el progress.md y en logs (audit trail).

Verify

Subagente de verificación (self-check) corre checklist: citas, supuestos, pruebas creadas.

Si falla, reabrir revisión humana.

5) Plan de implementación (semanal) y métricas (cuantificables)
Semana 1 — Infra y indexación

Tareas

Configurar GitHub API token y pruebas de fetch.

Implementar index_issues/prs (inserción en Milvus con metadata).

Añadir embedding pipeline para PR/issue.

Entregables

Script scripts/index_github.py.

Pruebas de carga: indexar 50 PRs/issues.

Métricas

% issues/PRs correctamente indexados (meta 100%).

Semana 2 — Human-in-the-Loop y Notificaciones

Tareas

Implementar check_critical_action.

Integrar Slack webhook (o GitHub comment) para notificaciones.

Implementar listener mínimo para respuestas humanas (webhook o polling).

Entregables

app/notify/slack.py

app/human_loop.py

Métricas

% de planes que requieren intervención humana (meta <20% para tareas rutinarias).

Tiempo promedio de respuesta humana (meta <1h).

Semana 3 — Cursor integration y background tasks

Tareas

Integrar mecanismo para delegar subtareas a Cursor-like agents (o worker async local).

Crear flows para generar draft PRs, tests y docs.

Añadir compactación de contexto (context_manager).

Entregables

app/cursor_agent.py (wrapper / mock si no hay Cursor real).

app/context_manager.py (summarize + budget).

Métricas

PR drafts generados sin errores (meta +50%).

Tiempo promedio para generar draft (meta -30%).

Semana 4 — Verificación, auditoría y evaluación

Tareas

Implementar verification subagent y checklist.

Añadir logs/audit trail: cada plan/acción debe escribir en progress.md y logs/audit.jsonl.

Crear golden set de 20 issues para medir precisión del plan (baseline).

Entregables

eval/evaluate_plans.py

logs/audit.jsonl

Métricas

Precisión de los planes (meta 90%).

Trazabilidad: % de acciones con logs (meta 100%).

6) Mecanismos de trazabilidad y auditoría (requisitos mínimos)

Cada plan o acción debe incluir:

id único (uuid).

timestamp, author (agent id), contract (spec used).

source_chunks (ids de Milvus) y sus scores.

files_affected (lista con diffs y rutas).

human_approvals (who, when, decision).

artifacts generados (PR numbers, branches, test files).

Registrar todo en logs/audit.jsonl y una entrada resumen en progress.md.

Ejemplo de entrada logs/audit.jsonl:

{
  "id": "uuid-1234",
  "time": "2025-08-30T12:34:56Z",
  "agent": "issue_assistant_v0.2",
  "action": "proposed_plan",
  "contract": { "...": "..." },
  "source_chunks": ["chunk:abc", "chunk:def"],
  "files_affected": ["src/auth/login.py"],
  "human_approvals": [{"user":"devlead","ts":"2025-08-30T12:45:00Z","decision":"approved"}],
  "artifacts": []
}

7) Cambios en el progress.md (este documento)

Este archivo pasa a ser la fuente de verdad para decisiones de product/infra.

Requiere que cada acción relevante actualice un bloque en este archivo (append minimal) y el logs/audit.jsonl.

8) Checklist técnico (tareas concretas para PRs)

 scripts/index_github.py — indexar PRs/issues a Milvus.

 app/spec_layer.py — generar contratos/specs para tasks.

 app/context_manager.py — compactación y resumen del histórico.

 app/retrieval/hybrid.py — vector + BM25 + rerank.

 app/subagents/retrieval.py — búsqueda híbrida (PRs/issues).

 app/subagents/analysis.py — scoring de riesgo y detección de puntos críticos.

 app/human_loop.py — notify_slack + wait_for_approval.

 app/cursor_agent.py — wrapper para background tasks (crear drafts/tests).

 app/subagents/verification.py — checklist y self-check.

 eval/evaluate_plans.py — golden set y scripts de métricas.

 logs/audit.jsonl — iniciar archivo de audit trail.

 docs/CONTRATOS.md — ejemplos de contratos/specs y reglas.

9) Mecanismo de configuración (recomendado)

Variables de entorno:

GITHUB_TOKEN, SLACK_WEBHOOK_URL, MILVUS_URI, MILVUS_COLLECTION, EMBEDDING_MODEL, CURSOR_API_URL (si aplica).

Archivo config.yml (ejemplo):

human_loop:
  critical_paths: ["/auth/", "/payments/", "/migrations/"]
  risk_threshold: 0.65
modes:
  default: "conservative" # conservative | assisted | autonomous

10) Próximos pasos inmediatos (acciónables, listo para commits)

Commit inicial (esta propuesta): agregar/actualizar progress.md (este archivo).

PR-A: scripts/index_github.py + tests básicos (index 50 PRs).

PR-B: app/human_loop.py + Slack notify + simple approval listener (mock).

PR-C: app/spec_layer.py + hook en Agent para generar contratos.

PR-D: app/cursor_agent.py (mock) + app/subagents/ skeleton.

PR-E: logs/audit.jsonl y eval/evaluate_plans.py.

11) Métricas resumen (KPIs)

Indexing coverage: % PRs/issues indexados (meta 100%).

Plan precision: % de planes aceptados por humanos sin cambios (meta 90%).

Automation rate: % subtareas ejecutadas sin intervención (meta 70%).

Human response time: tiempo medio para aprobaciones (meta <1h).

Traceability: % acciones con log completo (meta 100%).

Latency: tiempo medio de análisis por PR (meta -30% respecto baseline).

12) Notas finales y gobernanza

Adoptar modo conservador por defecto. Escalar a modos más autónomos solo con políticas y métricas validadas.

Mantener progress.md y logs/audit.jsonl como artefactos de auditoría.

Realizar revisión semanal de métricas y ajustar thresholds de riesgo.