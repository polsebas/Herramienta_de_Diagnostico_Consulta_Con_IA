# 🧪 Tests y Ejemplos del Sistema Next Level RAG

**Directorio de Tests, Ejemplos y Auditorías del Sistema**

---

## 🎯 **Descripción General**

Este directorio contiene todos los archivos de testing, ejemplos de uso y herramientas de auditoría del sistema **Next Level RAG con Human-in-the-Loop**. Los archivos están organizados por funcionalidad y propósito.

---

## 📋 **Índice de Archivos**

### **🔍 Auditorías y Verificación**

#### **`audit_system_completeness.py`**
- **Propósito**: Auditoría integral del sistema para verificar objetivos cumplidos
- **Funcionalidad**: Verifica que todos los PRs (1-4, A-E) estén implementados
- **Uso**: `python tests/audit_system_completeness.py`
- **Salida**: Reporte detallado de completitud del sistema
- **Estado**: ✅ Activo y funcional

---

### **📚 Ejemplos de Uso por Componente**

#### **`example_spec_layer.py`**
- **Componente**: Spec Layer (PR-1, PR-C)
- **Funcionalidades**: Generación de contratos, validación, integración
- **Ejemplos incluidos**:
  - Generación básica de contratos
  - Renderizado de prompts del sistema
  - Validación de cumplimiento
  - Integración con human loop
  - Contratos con contexto
  - Gestión de contratos
- **Uso**: `python tests/example_spec_layer.py`

#### **`example_human_loop.py`**
- **Componente**: Human-in-the-Loop System (PR-B)
- **Funcionalidades**: Flujos de aprobación, notificaciones, gestión de riesgo
- **Ejemplos incluidos**:
  - Flujos básicos de aprobación
  - Detección de acciones críticas
  - Sistema de notificaciones
  - Manejo de timeouts
  - Mecanismo de callbacks
- **Uso**: `python tests/example_human_loop.py`

#### **`example_cursor_integration.py`**
- **Componente**: Cursor Integration (PR-D)
- **Funcionalidades**: Agentes en background, generación de PRs, tests y docs
- **Ejemplos incluidos**:
  - Inicialización del agente
  - Generación de draft PRs
  - Generación de tests
  - Generación de documentación
  - Múltiples tareas
  - Gestión de tareas
  - Sistema de callbacks
- **Uso**: `python tests/example_cursor_integration.py`

#### **`example_evaluation_system.py`**
- **Componente**: Audit & Evaluation System (PR-E)
- **Funcionalidades**: Evaluación de calidad, golden set, métricas
- **Ejemplos incluidos**:
  - Inicialización del sistema
  - Evaluación de pregunta individual
  - Evaluación en lotes
  - Evaluación del golden set completo
  - Análisis de calidad
  - Exportación y reportes
- **Uso**: `python tests/example_evaluation_system.py`

#### **`example_pipeline_subagents.py`**
- **Componente**: Subagents Pipeline (PR-4)
- **Funcionalidades**: Pipeline completo de subagentes con verificación
- **Ejemplos incluidos**:
  - Pipeline básico de subagentes
  - Pipeline con verificación
  - Pipeline con métricas
  - Pipeline completo integrado
- **Uso**: `python tests/example_pipeline_subagents.py`

---

### **🧪 Tests Unitarios**

#### **`test_github_indexing.py`**
- **Componente**: GitHub Integration (PR-A)
- **Propósito**: Tests unitarios para el sistema de indexación de GitHub
- **Cobertura**:
  - Conexión con GitHub API
  - Generación de embeddings
  - Almacenamiento en Milvus
  - Manejo de errores
- **Uso**: `python tests/test_github_indexing.py`

---

## 🚀 **Cómo Usar los Ejemplos**

### **Ejecución Individual**
```bash
# Ejemplo básico del Spec Layer
python tests/example_spec_layer.py

# Ejemplo del Human Loop
python tests/example_human_loop.py

# Ejemplo del Cursor Integration
python tests/example_cursor_integration.py

# Ejemplo del Evaluation System
python tests/example_evaluation_system.py

# Ejemplo del Pipeline de Subagentes
python tests/example_pipeline_subagents.py
```

### **Ejecución de Tests**
```bash
# Test de GitHub Indexing
python tests/test_github_indexing.py

# Auditoría completa del sistema
python tests/audit_system_completeness.py
```

### **Ejecución de Auditoría**
```bash
# Verificar completitud del sistema
python tests/audit_system_completeness.py
```

---

## 📊 **Estructura de Ejemplos**

### **Formato Estándar**
Cada archivo de ejemplo sigue una estructura consistente:

```python
async def demo_basic_functionality():
    """Demuestra funcionalidad básica del componente."""
    # Configuración inicial
    # Ejecución de funcionalidad
    # Verificación de resultados
    # Logging de métricas

async def main():
    """Función principal que ejecuta todos los ejemplos."""
    await demo_basic_functionality()
    await demo_advanced_functionality()
    # ... más ejemplos

if __name__ == "__main__":
    asyncio.run(main())
```

### **Integración entre Componentes**
Los ejemplos demuestran cómo los diferentes componentes trabajan juntos:

- **Spec Layer** → **Human Loop** → **Cursor Agent**
- **Context Manager** → **Subagents** → **Evaluation**
- **GitHub Indexing** → **Retrieval** → **Synthesis**

---

## 🔧 **Configuración para Ejemplos**

### **Variables de Entorno**
```bash
# Configuración básica
export MILVUS_URI="localhost:19530"
export GITHUB_TOKEN="your_github_token"
export SLACK_WEBHOOK_URL="your_slack_webhook"

# Configuración de desarrollo
export LOG_LEVEL="DEBUG"
export ENVIRONMENT="development"
```

### **Archivos de Configuración**
Los ejemplos utilizan archivos de configuración en `../config/`:

- `spec_layer.yml` - Configuración del Spec Layer
- `human_loop.yml` - Configuración del Human Loop
- `cursor_agent.yml` - Configuración del Cursor Agent
- `evaluation.yml` - Configuración del sistema de evaluación
- `github_indexing.yml` - Configuración de indexación de GitHub

---

## 📈 **Métricas y Monitoreo**

### **Logging Estándar**
Todos los ejemplos incluyen logging estructurado:

```python
import logging
logger = logging.getLogger(__name__)

logger.info("Iniciando ejemplo de funcionalidad")
logger.debug("Configuración cargada: %s", config)
logger.info("Ejemplo completado exitosamente")
```

### **Métricas de Performance**
Los ejemplos registran métricas clave:

- **Tiempo de ejecución** por funcionalidad
- **Uso de recursos** (tokens, memoria, CPU)
- **Tasa de éxito** de operaciones
- **Calidad** de resultados generados

---

## 🧹 **Mantenimiento y Limpieza**

### **Limpieza Automática**
Los ejemplos incluyen limpieza de recursos:

```python
async def cleanup():
    """Limpia recursos utilizados durante el ejemplo."""
    # Cerrar conexiones
    # Limpiar archivos temporales
    # Resetear estado del sistema
```

### **Logs de Auditoría**
Todos los ejemplos generan logs de auditoría:

- **Acciones ejecutadas** con timestamps
- **Recursos utilizados** y modificados
- **Resultados obtenidos** y métricas
- **Errores** y excepciones encontradas

---

## 🔗 **Enlaces Rápidos**

- **📚 [Documentación Principal](../docs/)**
- **🏠 [README del Proyecto](../README.md)**
- **🇪🇸 [LEAME del Proyecto](../LEAME.md)**
- **⚙️ [Configuración](../config/)**
- **📊 [Evaluación](../eval/)**
- **📝 [Logs](../logs/)**

---

## 📝 **Notas de Desarrollo**

### **Convenciones de Naming**
- **Archivos de ejemplo**: `example_<componente>.py`
- **Archivos de test**: `test_<componente>.py`
- **Archivos de auditoría**: `audit_<funcionalidad>.py`

### **Estructura de Funciones**
- **Funciones demo**: `demo_<funcionalidad>()`
- **Función principal**: `main()`
- **Funciones de utilidad**: `_<funcionalidad>()`

### **Manejo de Errores**
- **Try-catch** en todas las operaciones críticas
- **Logging detallado** de errores y excepciones
- **Fallbacks** para operaciones fallidas
- **Cleanup** en caso de errores

---

*Última actualización: 2025-08-30*  
*Versión del sistema: Next Level RAG v1.0 - 100% Completado*  
*Estado de tests: ✅ Todos los ejemplos funcionales*
