# 🚀 Sistema RAG Next Level - Spec-First + Subagentes

Este documento describe la implementación del **Plan "Next Level"** para tu herramienta de diagnóstico con IA, que introduce una arquitectura avanzada basada en contratos de tarea y subagentes especializados.

## 🎯 Objetivos del Next Level

- **Spec-First**: Contratos de tarea que definen objetivos, restricciones y formato
- **Compactación Intencional**: Mantener uso <40% de la ventana del modelo
- **Subagentes Especializados**: Arquitectura modular para cada fase del proceso
- **Verificación Automática**: Detección de alucinaciones y validación de calidad
- **Recuperación Híbrida**: BM25 + Vectorial + Reranking

## 🏗️ Arquitectura Implementada

### 1. Spec Layer (`app/spec_layer.py`)

**Contratos de Tarea Inteligentes**
- Detección automática del tipo de consulta (procedural, diagnóstico, decisión, código)
- Generación de prompts del sistema basados en contratos
- Validación de cumplimiento de contratos
- Plantillas YAML para diferentes tipos de consulta

**Características:**
- Detección automática del tipo de consulta
- Ajuste dinámico según rol del usuario y nivel de riesgo
- Métricas específicas por tipo de tarea
- Validación automática de cumplimiento

### 2. Context Manager (`app/context_manager.py`)

**Compactación Intencional del Contexto**
- Resumen inteligente del historial de diálogo
- Compactación de chunks con pérdida controlada
- Monitoreo de uso de tokens
- Logging de estadísticas de contexto

**Regla de Oro:**
- Mantener uso <40% de la ventana del modelo
- Presupuesto inteligente para contexto vs. respuesta
- Resumen de "trajectory" del diálogo

### 3. Subagentes Especializados

#### RetrievalSubAgent (`app/subagents/retrieval.py`)
- **Búsqueda Híbrida**: Vectorial + BM25
- **Filtros Inteligentes**: Por tipo de documento, sección, recencia
- **Reranking**: Basado en relevancia y calidad del contenido
- **Fusión Inteligente**: Ponderación de resultados de diferentes fuentes

#### AnalysisSubAgent (`app/subagents/analysis.py`)
- **Clasificación de Contenido**: Por tipo, conceptos, secciones
- **Análisis de Calidad**: Relevancia, precisión, completitud
- **Detección de Huecos**: Información faltante y dependencias
- **Plan de Uso**: Estrategia para síntesis de respuesta

#### SynthesisSubAgent (`app/subagents/synthesis.py`)
- **Generación Basada en Contratos**: Respuestas que cumplen especificaciones
- **Fallback Inteligente**: Funciona sin LLM cuando es necesario
- **Revisión Automática**: Mejora basada en feedback
- **Validación de Cumplimiento**: Verificación de requisitos

#### VerificationSubAgent (`app/subagents/verification.py`)
- **Verificación Automática**: Checklist de calidad
- **Detección de Alucinaciones**: Comparación con contexto
- **Validación de Contratos**: Cumplimiento de especificaciones
- **Evaluación Comprehensiva**: Score general de calidad

### 4. Plantillas de Prompts (`app/prompts/`)

**Prompts Especializados para Cada Subagente:**
- `retrieval.md`: Instrucciones para recuperación híbrida
- `analysis.md`: Guía para análisis de chunks
- `synthesis.md`: Instrucciones para generación de respuestas
- `verification.md`: Checklist de verificación de calidad

### 5. Especificaciones YAML (`app/specs/`)

**Plantillas para Diferentes Tipos de Consulta:**
- `procedural_query.yaml`: Consultas que requieren pasos
- `diagnostic_query.yaml`: Consultas de diagnóstico y resolución
- `decision_query.yaml`: Consultas de toma de decisiones
- `code_query.yaml`: Consultas de implementación de código

## 🚀 Uso del Sistema

### Ejemplo Básico

```python
from app.spec_layer import build_task_contract, render_system_prompt
from app.context_manager import ContextManager
from app.subagents import RetrievalSubAgent, AnalysisSubAgent, SynthesisSubAgent, VerificationSubAgent

# 1. Generar contrato de tarea
contract = build_task_contract(
    query="¿Cómo configuro el entorno de desarrollo?",
    user_role="developer",
    risk_level="low"
)

# 2. Crear prompt del sistema
system_prompt = render_system_prompt(contract)

# 3. Inicializar subagentes
retrieval_agent = RetrievalSubAgent()
analysis_agent = AnalysisSubAgent()
synthesis_agent = SynthesisSubAgent()
verification_agent = VerificationSubAgent()

# 4. Procesar consulta
# ... implementación del flujo completo
```

### Ejemplo Completo

Ver `example_next_level.py` para una demostración completa del sistema.

## 📊 Métricas y Monitoreo

### Compliance con Contratos
- **Objetivo**: ≥80% (baseline estimado: 40-50%)
- **Método**: Validación automática con `validate_contract_compliance()`

### Uso de Tokens
- **Objetivo**: -30% promedio por compactación
- **Método**: Logging automático en `logs/context_stats.jsonl`

### Calidad de Respuestas
- **Objetivo**: Score general ≥0.8
- **Método**: Verificación comprehensiva con `VerificationSubAgent`

## 🔧 Configuración

### Variables de Entorno

```bash
# Modelo LLM
MODEL_NAME=gpt-3.5-turbo

# Configuración de contexto
MAX_CONTEXT_RATIO=0.4

# Configuración de Milvus
MILVUS_URI=localhost:19530
MILVUS_COLLECTION=system_knowledge
```

### Dependencias

```bash
pip install -r requirements.txt
```

**Nuevas dependencias agregadas:**
- `tiktoken`: Conteo de tokens
- `rank-bm25`: Búsqueda léxica
- `fastapi`: API REST
- `uvicorn`: Servidor ASGI
- `streamlit`: Dashboard de monitoreo

## 📁 Estructura del Proyecto

```
app/
├── specs/                    # Plantillas YAML de consultas
├── prompts/                  # Prompts especializados
├── subagents/               # Subagentes especializados
│   ├── retrieval.py         # Recuperación híbrida
│   ├── analysis.py          # Análisis de chunks
│   ├── synthesis.py         # Generación de respuestas
│   └── verification.py      # Verificación de calidad
├── retrieval/               # Módulos de recuperación
├── eval/                    # Evaluación y benchmarking
├── api/                     # API FastAPI
├── spec_layer.py            # Capa de contratos
└── context_manager.py       # Gestión de contexto

logs/                        # Logs de estadísticas
tests/                       # Tests unitarios y e2e
```

## 🧪 Testing

### Tests Unitarios

```bash
# Instalar dependencias de testing
pip install pytest pytest-asyncio

# Ejecutar tests
pytest tests/ -v
```

### Tests de Integración

```bash
# Ejecutar ejemplo completo
python example_next_level.py
```

## 📈 Próximos Pasos (PRs Futuros)

### PR-2: Context Manager + Logging
- Implementar logging detallado de tokens
- Dashboard de estadísticas de contexto

### PR-3: Retrieval Híbrido + Milvus
- Integración con Milvus para almacenamiento vectorial
- Implementación de BM25 con Whoosh/Elasticsearch
- Reranking con modelos locales

### PR-4: Subagentes + Verificación
- Integración completa de subagentes
- Pipeline de verificación automática

### PR-5: Evaluación + Benchmarking
- Conjunto de 40 preguntas doradas
- Scripts de benchmarking automático

### PR-6: CLI + API
- Interfaz de línea de comandos `ragc`
- API FastAPI con endpoints `/ask`, `/health`, `/metrics`

## 🎯 Beneficios del Next Level

### Para Desarrolladores
- **Respuestas Más Precisas**: Contratos garantizan cumplimiento de requisitos
- **Mejor Trazabilidad**: Fuentes citadas con precisión de línea
- **Menos Alucinaciones**: Verificación automática de calidad

### Para Usuarios
- **Respuestas Estructuradas**: Formato consistente según tipo de consulta
- **Información Verificable**: Todas las afirmaciones están citadas
- **Mejor Experiencia**: Respuestas más relevantes y accionables

### Para el Sistema
- **Escalabilidad**: Arquitectura modular y extensible
- **Monitoreo**: Métricas detalladas de calidad y rendimiento
- **Mantenibilidad**: Código organizado y bien documentado

## 🤝 Contribución

### Estándares de Código
- **Type Hints**: Todos los métodos deben tener tipos
- **Docstrings**: Documentación completa en formato Google
- **Logging**: Uso consistente del sistema de logging
- **Tests**: Cobertura mínima del 80%

### Flujo de Trabajo
1. Crear feature branch desde `main`
2. Implementar cambios con tests
3. Verificar cumplimiento de estándares
4. Crear Pull Request con descripción detallada
5. Code review y merge

## 📚 Recursos Adicionales

- **Documentación de Milvus**: [pymilvus.readthedocs.io](https://pymilvus.readthedocs.io/)
- **Guía de Contratos**: `docs/guia_contratos.md`
- **Playbooks**: `docs/playbooks/` (Research→Plan→Implement)
- **Benchmarks**: `docs/benchmarks/` (métricas y comparativas)

---

**¡El sistema Next Level está listo para elevar la calidad de tus respuestas RAG al siguiente nivel! 🚀**
