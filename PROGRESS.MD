> Notas de contexto: usaremos **Agno Agent UI** como front-end (plantilla Next.js + Tailwind) y el **AG-UI protocol** para streamear eventos entre backend y UI. ([GitHub][1], [agno-agent-ui.vercel.app][2], [webflow.copilotkit.ai][3])
> Además, nos apoyamos en la noción de agentes con **knowledge/RAG** de Agno para conectar tu pipeline de análisis y documentación al chat. ([docs.agno.com][4])

---

````markdown
# Project Progress Report — Usability-First
**Repo:** polsebas/Herramienta_de_Diagnostico_Consulta_Con_IA  
**UI:** Agno Agent UI (Next.js + Tailwind) — AG-UI protocol  
**Updated:** 31 Aug 2025

## 🎯 Objetivo de esta iteración
Convertir la herramienta en una experiencia “plug-in y usar” enfocada en:
1) Seleccionar fuentes (código + docs),  
2) Ejecutar un análisis profundo,  
3) Entregar un **informe principal** y un **roadmap propuesto**,  
4) Iterar el roadmap **con el usuario en la UI**,  
5) Generar archivos `.md` para que **Cursor agents** ejecuten las tareas.

* **Foundation** (PR1–4)

  * Repo initialization, basic RAG setup, NLP integration.
* **Integration**

  * **PR-A**: Spec Layer merged.
  * **PR-B**: Intelligent Contracts merged (Aug 30).
  * **PR-C**: Cursor Integration merged (Aug 30).
  * **PR-D**: Audit & Evaluation system merged (Aug 30).

### 🔄 In Progress

* **Intelligence Phase**

  * **PR-F**: Advanced contract generation module.
    - 🎯 **Objetivo**: ML classifier + adaptive templates (95% accuracy)
    - 📁 **Archivos**: `app/advanced_contracts/`, `config/advanced_contracts/`
    - ⏱️ **Tiempo**: 2-3 semanas
    - 📊 **Métricas**: Classification accuracy 95%, Template relevance 0.95
  * **PR-G**: Automated project analysis with background agents.
    - 🎯 **Objetivo**: Agentes proactivos 24/7 (85% problemas detectados antes de impacto)
    - 📁 **Archivos**: `app/project_analysis/`, `background_agents/`
    - ⏱️ **Tiempo**: 2-3 semanas
    - 📊 **Métricas**: Problem detection 85%, Automation 80%, Velocity +25%

### 📝 Planned

* **Production Phase**

  * **PR-H**: Enterprise infrastructure (multi-tenant, scaling).
    - 🎯 **Objetivo**: 1000+ usuarios concurrentes, 100+ tenants, 99.99% uptime
    - 📁 **Archivos**: `app/enterprise/`, `infrastructure/kubernetes/`
    - ⏱️ **Tiempo**: 3-4 semanas
    - 📊 **Métricas**: 1000+ concurrent users, 99.99% uptime, <200ms P95
  * **PR-I**: Security & compliance layer (auth, RBAC).
    - 🎯 **Objetivo**: Security score 98+, compliance 100% GDPR/SOX/ISO27001
    - 📁 **Archivos**: `app/security/`, `app/security/compliance/`
    - ⏱️ **Tiempo**: 2-3 semanas
    - 📊 **Métricas**: Security score 98+, 0 security incidents, 100% compliance
  * **PR-J**: Advanced human-in-the-loop workflows.
    - 🎯 **Objetivo**: Workflows enterprise complejos, <15 min tiempo aprobación
    - 📁 **Archivos**: `app/workflows/`, `app/workflows/templates/`
    - ⏱️ **Tiempo**: 2 semanas
    - 📊 **Métricas**: <15 min approval time, 95% workflow completion
> Base funcional referenciada en el MANUAL_USUARIO (pantalla, interacción y resultados), que guiará la simplicidad de los flujos en UI.  

---

## 🧭 Roadmap (Usability-first)
- **Phase U1 – Descubrimiento & Selección de fuentes** ✅ *(en curso)*
- **Phase U2 – Análisis profundo + Métricas de repositorio**
- **Phase U3 – Generación/Upgrade de documentación**
- **Phase U4 – Informe principal + Roadmap editable (human-in-the-loop)**
- **Phase U5 – Generación de paquetes `.md` para Cursor**

---

## 🧩 Plan de PRs

### PR-U1 — Agent UI Shell + Selector de Fuentes
**Branch:** `feature/ui-shell-source-selector`  
**Objetivo:** Montar Agno Agent UI, crear sesión y permitir seleccionar el sistema a analizar.

**Entregables**
- UI mínima (Agno Agent UI) con panel: Chat, Acciones, Estado de sesión. :contentReference[oaicite:4]{index=4}
- Módulo “Seleccionar Sistema” con 3 modos:
  1) **Ruta en servidor** (para despliegues on-prem).
  2) **Importar Git** (URL + token opcional).
  3) **Subir ZIP** (fuentes + docs).
- Backend endpoints:
  - `POST /api/session` → crea sesión (id, timestamp, flags).
  - `POST /api/sources/select` → `{ mode, server_path|git_url|zip_id }`.
  - `GET /api/sources/status` → progreso de ingesta (stream AG-UI).
- Indexado inicial: rutas, tamaños, tipado básico de archivos (código/docs), pre-conteo de tokens.

**Criterios de aceptación**
- El usuario puede **iniciar** una sesión y **ver** el estado de selección/ingesta en tiempo real desde la UI (event stream). :contentReference[oaicite:5]{index=5}
- Persistimos `session.json` y `sources.json` en `.cache/<session_id>/`.
- Manejo de errores (repo privado inválido, ZIP corrupto) con mensajes en UI.

**Tests**
- Subir ZIP pequeño (≤50MB) ✅
- Clonar repo público y listar N archivos ✅
- Ruta local válida/ inválida (simulada en dev) ✅

---

## 4. Next Steps (Detailed PRs)

### **🔄 Intelligence Phase (Enero-Febrero 2025)**
* **PR-F**: Advanced contract generation module.
  - ML classifier con 95% accuracy + templates adaptativos
  - **Documentación**: `docs/PR-F_ADVANCED_CONTRACTS_SPEC.md`
* **PR-G**: Project analysis agents (background + async).
  - Agentes proactivos 24/7 + análisis automatizado
  - **Documentación**: `docs/PR-G_PROJECT_ANALYSIS_SPEC.md`

### **📝 Production Phase (Marzo-Mayo 2025)**
* **PR-H**: Enterprise infrastructure (multi-tenant, scaling).
  - 1000+ usuarios, 100+ tenants, auto-scaling
  - **Documentación**: `docs/PR-H_ENTERPRISE_INFRASTRUCTURE_SPEC.md`
* **PR-I**: Security & compliance layer (auth, RBAC).
  - Seguridad enterprise + compliance GDPR/SOX/ISO27001
  - **Documentación**: `docs/PR-I_SECURITY_COMPLIANCE_SPEC.md`
* **PR-J**: Advanced human-in-the-loop workflows.
  - Workflows complejos + escalamiento inteligente
  - **Documentación**: `docs/PR-J_ADVANCED_WORKFLOWS_SPEC.md`

### **🧪 Robustness Phase (Junio 2025)**
* **PR-K**: Mutation testing & fuzzing for RAG robustness.
  - Testing avanzado + chaos engineering
  - **Documentación**: `docs/PR-K_MUTATION_TESTING_SPEC.md`

### **📋 Plan Maestro**
* **Documentación completa**: `docs/MASTER_IMPLEMENTATION_PLAN.md`
* **Análisis detallado**: `docs/DETAILED_PR_ANALYSIS.md`

---

📌 **Nota**: Este documento será actualizado en cada merge significativo. Los PRs futuros deberían **referenciar esta hoja de ruta** para mantener la trazabilidad.

---

## 5. Resultados de pruebas (31-08-2025)

- ✅ Smoke test Spec Layer: demo completo ejecutado con éxito.
  - Ajustes menores realizados para habilitar la demo end-to-end:
    - `app/context_manager.py`: agregado método async `get_relevant_history()` (stub para smoke tests).
    - `app/human_loop.py`: `HumanLoopManager` acepta `NotificationConfig` por defecto.
- ⏭️ Human-in-the-Loop demo: salteado temporalmente por falta de herramientas de respuesta externas (Slack/Webhook).
- ✅ Auditoría de completitud: 100% objetivos completados (`tests/audit_system_completeness.py`).

### Próximos pasos inmediatos
- Ejecutar smoke del pipeline de subagentes: `PYTHONPATH=. python3 tests/example_pipeline_subagents.py` (ajustar imports si es necesario).
- Integrar smoke tests en CI (Spec Layer + Auditoría) y marcar como required.
- Opcional: correr `eval/evaluate_plans.py` para una corrida del golden set (puede ser pesado).

### PR-U2 — Análisis Profundo del Sistema (Código + Docs)
**Branch:** `feature/deep-analysis-repo`  
**Objetivo:** Pipeline que analiza estructura, actividad y cambios recientes.

**Entregables**
- Backend endpoints:
  - `POST /api/analyze/run` → dispara pipeline.
  - `GET /api/analyze/progress` → streaming de etapas (AG-UI).
- Módulos:
  - **Repo Stats**: commits por semana/autor, hotspots por “churn”, ficheros más modificados.
  - **Timeline**: ventanas de cambio (rachas), última actividad por directorio.
  - **Docs Gap**: cobertura de docs por módulo (qué falta/obsoleto).
- Artefactos generados en `reports/`:
  - `repo_overview.md`, `hotspots.md`, `activity_timeline.md`, `docs_gap.md`.

**Criterios de aceptación**
- El usuario ve **progreso paso a paso** en UI y obtiene reportes `.md` legibles.
- Para un repo de prueba, `hotspots.md` lista top 10 ficheros por churn.

**Tests**
- Repos de 1K, 5K y 20K archivos (muestras) → tiempo + estabilidad.
- Validación que los `.md` contienen secciones y métricas esperadas.

---

### PR-U3 — Generación / Upgrade de Documentación
**Branch:** `feature/docs-generation`  
**Objetivo:** Crear documentación faltante y actualizar la existente.

**Entregables**
- Generadores:
  - `docs/system_overview.md` (resumen, módulos, dependencias).
  - `docs/architecture.md` (Mermaid diagrams).
  - `docs/runbook.md` (arranque, troubleshooting).
  - Upgrade semántico de docs existentes (mantener autoría + diffs).
- Integración con RAG para sintetizar/normalizar terminología. :contentReference[oaicite:6]{index=6}
- Endpoint: `POST /api/docs/generate` (con opciones: qué generar/actualizar).

**Criterios de aceptación**
- Si no existe doc clave → se genera; si existe → se propone **upgrade** con diffs.
- Diagrama Mermaid compila (lint básico).

**Tests**
- Repo sin docs ⇒ se crean 3 archivos base.
- Repo con docs ⇒ se crea `*_upgrade.md` por archivo modificado.

---

### PR-U4 — Informe Principal + Roadmap Editable (Human-in-the-Loop)
**Branch:** `feature/main-report-roadmap`  
**Objetivo:** Entregar un **informe principal** y un **roadmap** que el usuario pueda **editar/aprobar** en la UI, con pausas de validación.

**Entregables**
- `reports/main_report.md`: hallazgos clave del análisis (estado actual, riesgos, deuda técnica, quick-wins).
- `reports/roadmap_proposed.md`: épicas, hitos, esfuerzos estimados.
- UI: panel “Roadmap Editor” (arrastrar/soltar, toggles, comentarios).
- “Pause points” para aprobación humana al avanzar de borrador → aprobado (AG-UI events). :contentReference[oaicite:7]{index=7}

**Criterios de aceptación**
- El usuario puede **aprobar/rechazar** elementos del roadmap desde la UI.
- Cada acción queda auditada en `logs/audit.jsonl` (quién, cuándo, qué).

**Tests**
- Flujo: generar → editar → aprobar → exportar.

---

### PR-U5 — Generación de Paquetes `.md` para Cursor Agents
**Branch:** `feature/cursor-task-bundles`  
**Objetivo:** Emitir tareas `.md` autocontenidas para que **Cursor** ejecute subtareas (tests, refactors, docs).

**Entregables**
- Plantillas en `cursor_tasks/templates/*.md`.
- Endpoint: `POST /api/cursor/generate` con parámetros:
  - `tasks`: lista (e.g., “tests e2e módulo pagos”),
  - `context_handles`: referencias a reportes/archivos,
  - `risk_level`: `low|medium|high` (afecta detalle/gates).
- Salida en `cursor_tasks/<session_id>/T####-*.md`.

**Criterios de aceptación**
- Los archivos incluyen contexto mínimo reproducible, criterios de done y checklist.
- Compatibles con flujo de trabajo de Cursor (copy-paste/ingesta directa).

**Tests**
- Generar 3 tareas desde un roadmap aprobado y validar consistencia.

**Ejemplo de plantilla**
```md
---
id: T-001
title: "Agregar tests E2E para módulo de pagos"
risk: low
source_session: ${SESSION_ID}
inputs:
  - reports/main_report.md
  - reports/hotspots.md
acceptance:
  - [ ] Cubre casos felices/errores
  - [ ] Ejecuta en CI
  - [ ] >80% cobertura en `payments/`
steps:
  - Generar casos base
  - Añadir fixtures
  - Integrar en pipeline CI
notes:
  - Evitar tocar `auth/` sin aprobación humana
````

---

## 🔌 API (backend) — resumen

* `POST /api/session`
* `GET /api/system/config` | `POST /api/system/config`
* `GET /api/system/preflight`
* `POST /api/sources/select` | `GET /api/sources/status`
* `POST /api/analyze/run` | `GET /api/analyze/progress`
* `POST /api/docs/generate`
* `POST /api/report/main`
* `POST /api/roadmap/propose` | `POST /api/roadmap/commit`
* `POST /api/cursor/generate`

Todos los endpoints emiten eventos compatibles con **AG-UI** para progreso/estado, integrándose naturalmente con Agno Agent UI. ([webflow.copilotkit.ai][3])

---

## 🧪 QA rápida (guiada por el MANUAL)

* **Flujo simple**: seleccionar fuentes → analizar → ver informe → aceptar roadmap → exportar tareas Cursor.
* **Preflight al iniciar sesión** (chat):
  - Backend ejecuta `GET /api/system/preflight` internamente al crear sesión.
  - Si faltan rutas (`source_folder`, `docs_folder`) → status `needs_configuration` y se guía al usuario en UI.
  - Si todo ok → status `initialized` y se habilita "Analizar".
* **Mensajes claros** en UI, resultados visibles y acciones siguientes sugeridas.
* **Historial**: auditoría de cada acción (aprobaciones/cambios).

---

## 📊 Métricas de usabilidad (por sesión)

* **TTR (Time-to-Report)**: inicio → `main_report.md`.
* **Ediciones por item** en roadmap antes de aprobar.
* **Éxito de exportación** de paquetes Cursor.
* **Errores entendibles** (ratio con remediación sugerida).

---

## 📁 Estructura propuesta

```
/app
  /ui           # Agno Agent UI (Next.js) :contentReference[oaicite:12]{index=12}
  /api          # Endpoints arriba
/reports
/docs
/cursor_tasks
/logs
/.cache/<session_id>/{session.json,sources.json}
```

---

## ⚠️ Riesgos y mitigaciones

* **Repos grandes:** ingesta por lotes y límites de tamaño; modo Git recomendado.
* **Privacidad:** tokens cifrados en servidor; no persistir ZIPs tras ingesta.
* **Falsos positivos en gaps de docs:** revisión humana en PR-U4 antes de generar tareas.

---

```

---

## ¿Qué sigue?
1) Si te parece bien este **progress.md**, lo subo en `progress.md` y preparo ramas iniciales (`feature/ui-shell-source-selector` y `feature/deep-analysis-repo`).  
2) Puedo añadir un **script de bootstrap** (crear carpetas, endpoints stub y README de UI) para acelerar U1.

### Preguntas rápidas (para afinar usabilidad)
- ¿Cuál de los 3 modos de selección de fuentes será el **principal** en tu entorno (ruta local, Git, ZIP)?  
- ¿Preferís que el **informe principal** salga como un único `.md` o dividido por áreas (arquitectura, calidad, delivery)?  
- ¿Los paquetes de tareas para Cursor deben agruparse por **epic** o por **módulo**?

Si me das el ok, lo dejo **listo para commit** con este `progress.md` y las ramas de trabajo.
::contentReference[oaicite:13]{index=13}
```

[1]: https://github.com/agno-agi/agent-ui?utm_source=chatgpt.com "agno-agi/agent-ui: A modern chat interface for AI ..."
[2]: https://agno-agent-ui.vercel.app/?utm_source=chatgpt.com "Agent UI"
[3]: https://webflow.copilotkit.ai/blog/introducing-ag-ui-the-protocol-where-agents-meet-users?utm_source=chatgpt.com "Introducing AG-UI: The Protocol Where Agents Meet Users"
[4]: https://docs.agno.com/agents/introduction?utm_source=chatgpt.com "What are Agents? - Agno"
>>>>>>> b3d8213 (checkpoint before checking out cursor/analizar-pr-ximos-pasos-y-detallar-prs-1768)
