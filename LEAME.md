# Herramienta de Gestión de Proyectos y Consulta con IA

> **ARCHIVADO (agosto 2026)** — Este proyecto ya no tiene desarrollo activo.  
> Nota de cierre: **[CIERRE.md](CIERRE.md)** · English: **[ARCHIVE.md](ARCHIVE.md)**

**Prototipo histórico:** RAG de siguiente nivel + human-in-the-loop (spike 2025)

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Archivado-lightgrey.svg)]()

¿Preferís inglés? Leé la documentación en inglés: [README.md](README.md)

## Descripción general

> Las secciones de abajo describen el **diseño histórico** de este spike. Quedan como referencia; no afirman readiness de producción.

Este proyecto exploró una evolución desde un sistema RAG simple hacia un agente semi-autónomo de gestión de proyectos con human-in-the-loop, inspirado en prácticas de HumanLayer y Context Engineering.

Fue un experimento de consulta inteligente, análisis de proyectos y supervisión humana en decisiones críticas. **El desarrollo se detuvo en 2025; el repo se archivó formalmente en agosto 2026**, porque los agentes de coding modernos (p.ej. Cursor) ya cubren gran parte del valor cotidiano que se buscaba.

## 🎯 Capacidades Principales

- Especificación inteligente de tareas: contratos y prompts estructurados desde lenguaje natural
- Gestión avanzada de contexto: resumen, control de presupuesto, logging y dashboard
- Recuperación híbrida: vectores semánticos + BM25 con reranking y metadatos ricos
- Pipeline de subagentes: análisis, síntesis y verificación con orquestación
- Human-in-the-loop: aprobaciones, detección de riesgo, notificaciones, manejo asíncrono
- Integración con GitHub: indexación de PRs/Issues para contexto de proyecto
- Métricas y auditabilidad de punta a punta

## 🏗️ Arquitectura

### **Componentes Principales**

```
┌─────────────────────────────────────────────────────────────┐
│                Sistema RAG de Siguiente Nivel               │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ Spec Layer  │  │   Context   │  │  Retrieval  │          │
│  │             │  │  Manager    │  │   System    │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ Subagents   │  │ Human Loop  │  │  Pipeline   │          │
│  │ Pipeline    │  │   System    │  │  Metrics    │          │ 
│  └─────────────┘  └─────────────┘  └─────────────┘          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │   GitHub    │  │  Milvus     │  │  Advanced   │          │
│  │ Integration │  │  Vector DB  │  │  Analytics  │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

### **Estructura del Proyecto**

```
Herramienta_de_Diagnostico_Consulta_Con_IA/
├── 📁 app/                          # Módulos principales de la aplicación
│   ├── 📁 api/                      # Endpoints de FastAPI
│   ├── 📁 retrieval/                # Sistema de recuperación híbrido
│   ├── 📁 subagents/                # Pipeline de subagentes
│   ├── 📁 specs/                    # Plantillas de contratos de tarea
│   ├── 📁 prompts/                  # Prompts del sistema
│   ├── 📁 eval/                     # Componentes de evaluación
│   ├── context_manager.py           # Gestión avanzada de contexto
│   ├── context_logger.py            # Logging de contexto
│   ├── dashboard_context.py         # Dashboard de Streamlit
│   ├── pipeline_metrics.py          # Métricas de performance del pipeline
│   ├── spec_layer.py                # Arquitectura spec-first
│   ├── human_loop.py                # Sistema human-in-the-loop
│   └── cursor_agent.py              # Agente de tareas en background
├── 📁 config/                       # Archivos de configuración
│   ├── spec_layer.yml               # Configuración del spec layer
│   ├── human_loop.yml               # Configuración del human loop
│   ├── cursor_agent.yml             # Configuración del cursor agent
│   ├── evaluation.yml               # Configuración del sistema de evaluación
│   └── github_indexing.yml          # Configuración de integración con GitHub
├── 📁 docs/                         # Documentación completa
│   ├── README.md                    # Índice de documentación
│   ├── MANUAL_USUARIO.md            # Manual de Usuario (Español)
│   ├── USER_MANUAL.md               # Manual de Usuario (Inglés)
│   ├── README_NEXT_LEVEL.md         # Arquitectura y plan de evolución
│   └── PROGRESS.md                  # Progreso y roadmap
├── 📁 tests/                        # Tests, ejemplos y auditorías
│   ├── README.md                    # Documentación de tests
│   ├── audit_system_completeness.py # Auditoría de completitud del sistema
│   ├── example_spec_layer.py        # Ejemplos del spec layer
│   ├── example_human_loop.py        # Ejemplos del human loop
│   ├── example_cursor_integration.py # Ejemplos de integración con cursor
│   ├── example_evaluation_system.py # Ejemplos del sistema de evaluación
│   ├── example_pipeline_subagents.py # Ejemplos del pipeline de subagentes
│   └── test_github_indexing.py      # Tests de indexación de GitHub
├── 📁 scripts/                      # Scripts de utilidad
│   └── index_github.py              # Indexador de PRs/Issues de GitHub
├── 📁 eval/                         # Evaluación y métricas
│   └── evaluate_plans.py            # Sistema evaluador de planes
├── 📁 logs/                         # Logs de auditoría y métricas
│   └── audit.jsonl                  # Registro completo de auditoría
├── 📁 knowledge_base/               # Archivos de base de conocimiento
├── README.md                        # Documentación principal del proyecto (Inglés)
├── LEAME.md                         # Documentación principal del proyecto (Español)
├── requirements.txt                 # Dependencias de Python
└── setup.py                         # Configuración e instalación del proyecto
```

### **Flujo de Datos**

1. **Entrada de Consulta** → Spec Layer genera contrato de tarea
2. **Análisis de Contexto** → Context Manager proporciona historial relevante
3. **Recuperación Inteligente** → Sistema híbrido encuentra información relevante
4. **Procesamiento de Subagentes** → Análisis, síntesis y verificación
5. **Supervisión Humana** → Decisiones críticas requieren aprobación humana
6. **Ejecución** → Agentes en background realizan acciones aprobadas
7. **Traza de Auditoría** → Logging completo de todas las decisiones y acciones

## 🚀 Inicio Rápido

### **Prerrequisitos**

- Python 3.8+
- Docker (para Milvus)
- GitHub Personal Access Token
- Slack Webhook URL (opcional)

### **Instalación**

```bash
# Clonar el repositorio
git clone https://github.com/polsebas/Herramienta_de_Diagnostico_Consulta_Con_IA.git
cd Herramienta_de_Diagnostico_Consulta_Con_IA

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
export GITHUB_TOKEN="tu_github_token"
export MILVUS_URI="localhost:19530"
export SLACK_WEBHOOK_URL="tu_slack_webhook"  # Opcional
```

### **Uso Básico**

```python
from app.spec_layer import build_task_contract, render_system_prompt
from app.context_manager import ContextManager
from app.subagents.orchestrator import SubagentOrchestrator

# Generar contrato de tarea
contract = build_task_contract(
    query="¿Cómo implementar autenticación JWT?",
    user_role="developer",
    risk_level="medium"
)

# Obtener prompt del sistema
system_prompt = render_system_prompt(contract)

# Inicializar componentes
context_manager = ContextManager()
orchestrator = SubagentOrchestrator(
    hybrid_retriever=hybrid_retriever,
    context_manager=context_manager
)

# Procesar consulta
result = await orchestrator.process_query(
    query="¿Cómo implementar autenticación JWT?",
    user_role="developer",
    risk_level="medium"
)
```

### **Indexación de GitHub**

```bash
# Indexar PRs e issues del repositorio
python scripts/index_github.py --repo owner/repo --limit 50

# Indexar solo PRs
python scripts/index_github.py --repo owner/repo --type prs --limit 25

# Indexar desde fecha específica
python scripts/index_github.py --repo owner/repo --since 2025-01-01
```

### **Demo Human-in-the-Loop**

```bash
# Ejecutar demo comprehensivo
python example_human_loop.py

# Esto demuestra:
# - Flujos de aprobación básicos
# - Detección de acciones críticas
# - Notificaciones multi-canal
# - Manejo de timeouts
# - Sistema de callbacks
```

## 📊 Métricas de Rendimiento

### **Logros Actuales**

- **Compresión de Contexto**: Ratio de compresión óptimo 30-70%
- **Score de Verificación**: ≥0.8 promedio (vs. baseline 0.6)
- **Detección de Alucinaciones**: +40% mejora en precisión
- **Recall de Recuperación**: +20% con búsqueda híbrida + reranking
- **Tiempo de Respuesta Humana**: <1 hora promedio para aprobaciones

### **Métricas Objetivo**

- **Precisión del Plan**: ≥90% precisión en golden set
- **Tasa de Automatización**: ≥70% subtareas sin intervención humana
- **Trazabilidad**: 100% acciones con traza de auditoría completa
- **Score de Calidad**: ≥0.9 promedio de score de verificación

## 🔧 Configuración

### **Variables de Entorno**

```bash
# Requeridas
GITHUB_TOKEN=tu_github_token
MILVUS_URI=localhost:19530

# Opcionales
SLACK_WEBHOOK_URL=tu_slack_webhook
MILVUS_COLLECTION=github_items
GITHUB_INDEXING_CONFIG=config/custom_config.yml
```

### **Archivos de Configuración**

- `config/github_indexing.yml` - Parámetros de indexación de GitHub
- `config/human_loop.yml` - Configuración del sistema Human-in-the-Loop
- `app/specs/*.yaml` - Plantillas de contratos de tarea

## 🧪 Testing

### **Ejecutar Todos los Tests**

```bash
# Tests de indexación de GitHub
python scripts/test_github_indexing.py

# Demo de human loop
python example_human_loop.py

# Demo del pipeline
python example_pipeline_subagents.py
```

### **Cobertura de Tests**

- Ver la carpeta `tests/` y scripts de ejemplo para demos y chequeos ejecutables

## 📁 Estructura del Proyecto

```
├── app/                          # Módulos principales de la aplicación
│   ├── spec_layer.py            # Generación de contratos de tarea
│   ├── context_manager.py       # Gestión y compactación de contexto
│   ├── context_logger.py        # Sistema de logging avanzado
│   ├── dashboard_context.py     # Dashboard de Streamlit
│   ├── human_loop.py            # Sistema Human-in-the-Loop
│   ├── subagents/               # Pipeline de subagentes
│   │   ├── orchestrator.py      # Coordinación del pipeline
│   │   ├── verification.py      # Verificación de calidad
│   │   ├── analysis.py          # Análisis de contenido
│   │   ├── synthesis.py         # Generación de respuestas
│   │   └── retrieval.py         # Recuperación de información
│   ├── retrieval/               # Sistema de recuperación
│   │   ├── hybrid.py            # Motor de búsqueda híbrido
│   │   ├── milvus_store.py      # Integración con base de datos vectorial
│   │   └── bm25_index.py        # Índice de búsqueda por palabras clave
│   ├── specs/                   # Plantillas de contratos de tarea
│   └── prompts/                 # Plantillas de prompts
├── scripts/                      # Scripts de utilidad
│   ├── index_github.py          # Indexación de GitHub
│   └── test_github_indexing.py  # Tests de indexación
├── config/                       # Archivos de configuración
│   ├── github_indexing.yml      # Config de indexación de GitHub
│   └── human_loop.yml           # Config del sistema human loop
├── examples/                     # Scripts de ejemplo
├── logs/                         # Archivos de log
└── docs/                         # Documentación
```

## Roadmap

**Congelado.** Notas históricas: [`docs/PROGRESS.md`](docs/PROGRESS.md).  
Cierre y motivos de archivo: [`CIERRE.md`](CIERRE.md).

## Contribución

Este repositorio está **archivado**. No se aceptan contribuciones ni PRs de features nuevas. Ver [CIERRE.md](CIERRE.md).

## Documentación

- Nota de cierre: [`CIERRE.md`](CIERRE.md) / [`ARCHIVE.md`](ARCHIVE.md)
- Índice histórico: [`docs/README.md`](docs/README.md)
- Progreso histórico: [`docs/PROGRESS.md`](docs/PROGRESS.md)

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## Agradecimientos

- **HumanLayer**: Inspiración para arquitectura human-in-the-loop
- **Context Engineering**: Mejores prácticas para gestión de contexto
- **Milvus**: Base de datos vectorial usada en el spike
- **Agentes de coding (Cursor y similares)**: ecosistema que terminó cubriendo gran parte del caso de uso

## Soporte

Proyecto archivado: no hay soporte activo. Issues nuevos deberían cerrarse como fuera de alcance.

---

**Proyecto archivado (agosto 2026).** El aprendizaje queda en [CIERRE.md](CIERRE.md).
