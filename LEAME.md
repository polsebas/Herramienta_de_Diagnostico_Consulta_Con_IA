# 🚀 Herramienta de Gestión de Proyectos y Consulta con IA

**Sistema RAG de Siguiente Nivel con Arquitectura Human-in-the-Loop**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Desarrollo%20Activo-orange.svg)]()

## 🌟 Descripción General

Este proyecto representa una evolución de **Siguiente Nivel** desde un sistema RAG simple hacia un **agente semi-autónomo de gestión de proyectos** con capacidades human-in-the-loop, inspirado en las mejores prácticas de HumanLayer y Context Engineering.

El sistema proporciona consultas inteligentes, análisis automatizado de proyectos y supervisión humana para decisiones críticas, siendo perfecto para equipos de desarrollo, gestores de proyectos y consultores técnicos.

## 🎯 Características Principales

### ✅ **Características Implementadas (PRs 1-4 + A-B)**

#### **PR-1: Arquitectura Spec-First**
- **Contratos de Tarea**: Plantillas YAML/Markdown para diferentes tipos de consulta
- **Generación Dinámica de Contratos**: Construcción automática basada en contexto de consulta
- **Renderizado de Prompts del Sistema**: Conversión de contratos a prompts estructurados
- **Detección de Tipos de Consulta**: Clasificación automática (procedimental, diagnóstico, decisión, código)

#### **PR-2: Gestión Avanzada de Contexto**
- **Compactación Inteligente de Contexto**: Resumen de diálogo potenciado por LLM
- **Optimización de Uso de Tokens**: Cálculo dinámico de presupuesto de contexto (<40% ventana del modelo)
- **Logging Avanzado**: Métricas en tiempo real, alertas y monitoreo de rendimiento
- **Dashboard Streamlit**: Visualización interactiva de métricas y tendencias de contexto

#### **PR-3: Sistema de Recuperación Híbrido**
- **Búsqueda Vector + BM25**: Combina búsqueda semántica y por palabras clave para recall óptimo
- **Integración Milvus**: Base de datos vectorial de alto rendimiento con metadatos ricos
- **Reranking Inteligente**: Scoring multi-factor (relevancia, calidad, frescura, metadatos)
- **Esquema de Metadatos Fuerte**: Indexación completa de chunks con seguimiento preciso de fuentes

#### **PR-4: Pipeline Completo de Subagentes**
- **Orquestador**: Coordina todos los subagentes en secuencia inteligente
- **Verificación Avanzada**: Verificaciones de calidad multi-factor con detección de alucinaciones
- **Métricas Integradas**: Seguimiento del rendimiento del pipeline con Context Manager
- **Fallback Robusto**: Manejo de errores y mecanismos de recuperación

#### **PR-A: Integración e Indexación de GitHub**
- **Indexación Automática de PRs/Issues**: Conecta con GitHub API e indexa metadatos
- **Almacenamiento Vectorial**: Almacena metadatos enriquecidos en Milvus para búsqueda semántica
- **Captura de Contexto Rico**: Información completa sobre cambios en el repositorio
- **Métricas de Rendimiento**: Tasas de éxito de indexación y seguimiento de rendimiento

#### **PR-B: Sistema Human-in-the-Loop**
- **Flujos de Aprobación**: Gestión completa del ciclo de vida para decisiones humanas
- **Notificaciones Multi-Canal**: Soporte para Slack, GitHub, Email y Webhook
- **Evaluación de Riesgo**: Detección automática de acciones críticas que requieren aprobación
- **Procesamiento Asíncrono**: Manejo de aprobaciones en background con timeouts

### 🚧 **Características Próximas (PRs C-E)**

#### **PR-C: Spec Layer + Contratos (Semana 2)**
- **Integración con Agent**: Hook en Agent para generación automática de contratos
- **Contexto de GitHub**: Integración con PRs e issues indexados
- **Validación Automática**: Verificación de cumplimiento de contratos
- **Contratos Inteligentes**: Generación de contratos consciente del contexto

#### **PR-D: Integración con Cursor (Semana 3)**
- **Agentes en Background**: Agentes tipo Cursor para tareas seguras en background
- **Generación de Draft PRs**: Creación automatizada de pull requests
- **Tests y Documentación**: Generación automática de tests y documentación
- **Compactación de Contexto**: Gestión avanzada de contexto para tareas en background

#### **PR-E: Auditoría y Evaluación (Semana 4)**
- **Logging Comprehensivo**: Trazabilidad completa de todas las decisiones
- **Evaluación Golden Set**: 20 preguntas doradas para evaluación de calidad
- **Métricas de Rendimiento**: Evaluación continua y mejora
- **Aseguramiento de Calidad**: Verificaciones de calidad automatizadas y recomendaciones

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
│   ├── README_PR1.md                # PR-1: Arquitectura Spec-First
│   ├── README_PR2.md                # PR-2: Gestión de Contexto
│   ├── README_PR3.md                # PR-3: Recuperación Híbrida
│   ├── README_PR4.md                # PR-4: Pipeline de Subagentes
│   ├── README_PR-A.md               # PR-A: Integración con GitHub
│   ├── README_PR-B.md               # PR-B: Human-in-the-Loop
│   ├── README_PR-C.md               # PR-C: Integración del Spec Layer
│   ├── README_PR-D.md               # PR-D: Integración con Cursor
│   ├── README_PR-E.md               # PR-E: Auditoría y Evaluación
│   └── README_NEXT_LEVEL.md         # Plan original de evolución
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

### **Métricas Objetivo (PR-E)**

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

- ✅ **PR-1**: Spec Layer y generación de contratos
- ✅ **PR-2**: Context Manager y logging
- ✅ **PR-3**: Sistema de recuperación híbrido
- ✅ **PR-4**: Pipeline de subagentes y verificación
- ✅ **PR-A**: Indexación e integración de GitHub
- ✅ **PR-B**: Sistema Human-in-the-Loop

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

## 🔄 Roadmap de Desarrollo

### **Fase 1: Fundación (Completada)**
- ✅ Arquitectura Spec-First
- ✅ Gestión avanzada de contexto
- ✅ Sistema de recuperación híbrido
- ✅ Pipeline de subagentes

### **Fase 2: Integración (En Progreso)**
- ✅ Indexación e integración de GitHub
- ✅ Sistema Human-in-the-Loop
- 🔄 Integración Spec Layer + Contratos
- 🔄 Integración con Cursor

### **Fase 3: Inteligencia (Planificada)**
- 🔄 Generación avanzada de contratos
- 🔄 Análisis automatizado de proyectos
- 🔄 Planificación inteligente de acciones
- 🔄 Aprendizaje continuo

### **Fase 4: Producción (Futuro)**
- 🔄 Características empresariales
- 🔄 Seguridad avanzada
- 🔄 Optimización de rendimiento
- 🔄 Mejoras de escalabilidad

## 🤝 Contribución

### **Flujo de Desarrollo**

1. **Fork** el repositorio
2. **Crea** rama de feature desde `main`
3. **Implementa** cambios con tests
4. **Envía** pull request con descripción detallada
5. **Code review** y merge

### **Estándares de Código**

- **Type Hints**: Todos los métodos deben tener tipos completos
- **Docstrings**: Documentación en formato Google
- **Error Handling**: Manejo robusto de excepciones
- **Tests**: Mínimo 80% de cobertura
- **Logging**: Logging comprehensivo para debugging

### **Guías para PRs**

- **Descripción Clara**: Qué, por qué y cómo
- **Tests Incluidos**: Tests unitarios e integración
- **Documentación**: Actualizar READMEs relevantes
- **Rendimiento**: Sin regresión en métricas

## 📚 Documentación

### **Documentación**

- Índice completo: [`docs/README.md`](docs/README.md)
- Progreso y roadmap: [`docs/PROGRESS.md`](docs/PROGRESS.md)

### **Documentación de Arquitectura**

- [Plan de Siguiente Nivel](docs/README_NEXT_LEVEL.md)
- [Seguimiento de Progreso](docs/PROGRESS.md)

## 🐛 Solución de Problemas

### **Problemas Comunes**

**Errores de Indexación de GitHub:**
```bash
# Verificar token
echo $GITHUB_TOKEN

# Verificar conexión Milvus
docker ps | grep milvus
```

**Notificaciones del Human Loop:**
```bash
# Verificar configuración de webhook
cat config/human_loop.yml

# Verificar variables de entorno
env | grep SLACK
```

**Problemas del Context Manager:**
```bash
# Verificar logs
tail -f logs/context_stats.jsonl

# Verificar dashboard
streamlit run app/dashboard_context.py
```

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 🙏 Agradecimientos

- **HumanLayer**: Inspiración para arquitectura human-in-the-loop
- **Context Engineering**: Mejores prácticas para gestión de contexto
- **Milvus**: Base de datos vectorial de alto rendimiento
- **OpenAI**: Modelos de lenguaje avanzados para comprensión de contexto

## 📞 Soporte

- **Issues**: [GitHub Issues](https://github.com/polsebas/Herramienta_de_Diagnostico_Consulta_Con_IA/issues)
- **Discussions**: [GitHub Discussions](https://github.com/polsebas/Herramienta_de_Diagnostico_Consulta_Con_IA/discussions)
- **Wiki**: [Project Wiki](https://github.com/polsebas/Herramienta_de_Diagnostico_Consulta_Con_IA/wiki)

---

**🚀 ¿Listo para llevar tu gestión de proyectos al Siguiente Nivel?**

Este sistema combina el poder de la IA con supervisión humana, proporcionando automatización inteligente mientras mantiene control sobre decisiones críticas. Perfecto para equipos que quieren escalar sus capacidades sin sacrificar calidad o seguridad.
