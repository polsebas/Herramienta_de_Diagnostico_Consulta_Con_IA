# Project Progress Report — Agno Team Coordinate Refactor
**Repo:** polsebas/Herramienta_de_Diagnostico_Consulta_Con_IA  
**Framework:** Agno (Teams · Coordinate mode)  
**Updated:** 31 Aug 2025

---

## 🎯 Objetivo
Migrar el sistema de agentes a la arquitectura **Agno Teams (Coordinate)**:
- Un **Team Agent** central coordina sub-agentes especializados.  
- Cada agente implementa un rol claro (Analyzer, DocGen, Roadmap, CursorTask).  
- Comunicación vía **event streams** compatibles con **Agno Agent UI**.  
- Control humano en decisiones críticas (human-in-the-loop).  

---

## 🧭 Roadmap de PRs

### PR-R1 — Infraestructura de Team Coordinate
**Branch:** `refactor/agno-team-core`  
**Objetivo:** Integrar Agno framework y definir el `TeamAgent` central.  
**Entregables:**
- Dependencia `agno` en `requirements.txt`.
- Crear `/agents/team/TeamCoordinator.py` con rol principal:
  - Coordina flujos.
  - Define protocolo de turnos (Coordinate mode).
  - Exposición a UI vía AG-UI events.
- Endpoints nuevos:
  - `POST /api/team/session` → inicializa team con roles activos.
  - `GET /api/team/status` → progreso coordinado.
**Criterios de aceptación:**  
- El sistema arranca con un **único entrypoint** (TeamAgent).  
- Logs muestran asignación de tareas a sub-agentes.  

---

### PR-R2 — Redefinición de Sub-Agentes (Roles Especializados)
**Branch:** `refactor/agno-subagents`  
**Objetivo:** Migrar agentes actuales al formato Agno Roles.  
**Nuevos agentes:**
- `AnalyzerAgent` → analiza código/repositorios.  
- `DocGenAgent` → genera/actualiza documentación.  
- `RoadmapAgent` → sintetiza planes de evolución.  
- `CursorTaskAgent` → genera `.md` tasks para Cursor.  
**Criterios de aceptación:**  
- Cada agente implementa contrato Agno (`act`, `respond`, `handoff`).  
- TeamAgent puede activar/agrupar agentes en flujos.  

---

### PR-R3 — Flujo Coordinate (Orquestación Completa)
**Branch:** `feature/team-coordinate-flows`  
**Objetivo:** Implementar el ciclo completo de coordinación.  
**Entregables:**
- Definir `workflow/coordinate_flow.py`:
  1. Inicia con **fuentes seleccionadas** (PR-U1).  
  2. `AnalyzerAgent` produce insights.  
  3. `DocGenAgent` actualiza docs.  
  4. `RoadmapAgent` arma plan.  
  5. `CursorTaskAgent` emite paquetes.  
- Manejo de **pause points** (ej. cambios en `/auth/`).  
**Criterios de aceptación:**  
- El TeamAgent muestra **handoffs** claros en UI.  
- Usuario puede aprobar/rechazar pasos.  

---

### PR-R4 — Integración con Agno Agent UI
**Branch:** `feature/team-ui-integration`  
**Objetivo:** Conectar el TeamAgent al frontend Agno Agent UI.  
**Entregables:**
- Conexión AG-UI protocol:
  - Eventos de progreso (per agente).
  - Historial de turnos/decisiones.  
- UI: panel de **orquestación visual** (quién actúa, quién espera).  
**Criterios de aceptación:**  
- El usuario ve un **timeline de agentes** y puede intervenir.  
- Audit trail registrado en `logs/audit.jsonl`.  

---

### PR-R5 — QA & Testing Framework para Coordinación
**Branch:** `feature/team-tests`  
**Objetivo:** Asegurar calidad y regresión.  
**Entregables:**
- Test unitarios por agente (Analyzer, DocGen, etc.).  
- Test integrados de flujos de coordinación.  
- Simulación de decisiones humanas (mock responses).  
**Criterios de aceptación:**  
- CI ejecuta >80% cobertura en sub-agentes.  
- Flujos Coordinate pasan con mock human-in-loop.  

---

### PR-R6 — Extensión: Roles Avanzados (Planned)
**Branch:** `feature/team-advanced-agents`  
**Objetivo:** Añadir agentes especializados para:  
- **RiskAgent** (detectar riesgos de seguridad/privacidad).  
- **IntegrationAgent** (preparar conectores externos, ej. Slack/Azure).  
**Meta:** Escalabilidad hacia uso empresarial.  

---

## 📊 Métricas de Progreso
- % de agentes migrados al modelo Agno (meta: 100%).  
- Tiempo medio de coordinación de flujo (baseline + reducción).  
- Tasa de handoffs exitosos sin error (meta: >90%).  
- Feedback humano capturado (meta: 100% acciones críticas con log).  

---

## 📁 Nueva estructura

/agents
/team
TeamCoordinator.py
/roles
AnalyzerAgent.py
DocGenAgent.py
RoadmapAgent.py
CursorTaskAgent.py
/workflow
coordinate\_flow\.py
/logs
/reports
/docs
/cursor\_tasks



---


---