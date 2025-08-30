# 🚀 PR-2: Context Manager + Logging Avanzado

Este documento describe la implementación del **PR-2** del plan "Next Level", que mejora significativamente el Context Manager con logging avanzado, métricas en tiempo real y un dashboard de monitoreo.

## 🎯 Objetivos del PR-2

- **Context Manager Mejorado**: Métricas avanzadas y score de eficiencia
- **Logging Avanzado**: Rotación automática, alertas y monitoreo en tiempo real
- **Dashboard de Streamlit**: Visualizaciones interactivas de métricas
- **Exportación de Datos**: CSV, JSON y Excel para análisis externo

## 🏗️ Arquitectura Implementada

### 1. Context Manager Mejorado (`app/context_manager.py`)

**Nuevas Funcionalidades:**
- **Score de Eficiencia**: Cálculo inteligente basado en presupuesto, compresión y balance
- **Métricas Agregadas**: Análisis por períodos con estadísticas detalladas
- **Recomendaciones Automáticas**: Sugerencias basadas en métricas de rendimiento
- **Gestión de Presupuesto**: Cálculo inteligente del presupuesto de tokens

**Score de Eficiencia:**
```python
# Componentes del score (ponderados):
# - Uso del presupuesto (40%): Preferir uso eficiente
# - Ratio de compresión (30%): Preferir compresión alta
# - Balance del contexto (30%): Preferir contexto balanceado
```

### 2. Context Logger Avanzado (`app/context_logger.py`)

**Características Principales:**
- **Rotación Automática**: Archivos de log con límite de tamaño y backup
- **Logging Especializado**: Separación de logs principales, estadísticas y alertas
- **Monitoreo en Tiempo Real**: Thread de monitoreo con métricas actualizadas
- **Alertas Automáticas**: Detección de problemas de rendimiento

**Tipos de Logs:**
- `context_manager.log`: Log principal con rotación
- `context_stats.jsonl`: Estadísticas en formato JSON
- `context_alerts.log`: Alertas y advertencias
- `status_report.json`: Reporte de estado del sistema

### 3. Dashboard de Streamlit (`app/dashboard_context.py`)

**Visualizaciones Disponibles:**
- **Métricas Principales**: Total consultas, compresión promedio, eficiencia, tokens ahorrados
- **Gráficos de Rendimiento**: Tendencias de compresión y eficiencia a lo largo del tiempo
- **Distribución de Calidad**: Histogramas de scores de eficiencia y ratios de compresión
- **Análisis de Presupuesto**: Scatter plots de eficiencia vs. utilización
- **Tabla de Consultas**: Lista detallada de consultas recientes con métricas

**Características del Dashboard:**
- **Configuración Dinámica**: Selección de modelo, período de análisis y ratio de contexto
- **Exportación de Datos**: Descarga de métricas en CSV y JSON
- **Recomendaciones del Sistema**: Sugerencias automáticas de optimización
- **Responsive Design**: Interfaz adaptativa para diferentes tamaños de pantalla

## 🚀 Uso del Sistema

### Ejemplo Básico

```python
from app.context_manager import ContextManager
from app.context_logger import ContextLogger

# Inicializar Context Manager
context_manager = ContextManager(
    model_name="gpt-3.5-turbo",
    max_context_ratio=0.4
)

# Inicializar Context Logger
context_logger = ContextLogger(
    logs_dir="logs",
    max_file_size=5 * 1024 * 1024,  # 5MB
    backup_count=3
)

# Procesar consulta
context_summary = context_manager.create_context_summary(
    system_prompt, query, dialog_history, retrieved_chunks
)

# Logging automático
context_logger.log_context_stats(context_summary["stats"].__dict__)
```

### Ejemplo Completo

Ver `example_context_manager.py` para una demostración completa del sistema.

## 📊 Métricas y Monitoreo

### Métricas en Tiempo Real

- **Total Consultas**: Número de consultas procesadas
- **Total Tokens Ahorrados**: Tokens ahorrados por compactación
- **Ratio de Compresión Promedio**: Eficiencia de la compactación
- **Score de Eficiencia Promedio**: Calidad general del contexto

### Score de Eficiencia

El score de eficiencia se calcula considerando:

1. **Uso del Presupuesto (40%)**
   - Uso eficiente (≤80%): 1.0
   - Uso aceptable (≤100%): 0.7
   - Exceso de presupuesto (>100%): 0.3

2. **Ratio de Compresión (30%)**
   - Excelente (≤50%): 1.0
   - Buena (≤70%): 0.8
   - Aceptable (≤90%): 0.6
   - Poca compresión (>90%): 0.3

3. **Balance del Contexto (30%)**
   - Balanceado (500-1500 tokens): 1.0
   - Aceptable (300-2000 tokens): 0.8
   - Otros: 0.5

### Alertas Automáticas

El sistema genera alertas cuando:

- **Ratio de compresión > 90%**: Contexto poco compactado
- **Score de eficiencia < 60%**: Baja calidad del contexto
- **Uso de presupuesto > 95%**: Presupuesto casi agotado

## 🔧 Configuración

### Variables de Entorno

```bash
# Configuración del Context Manager
MODEL_NAME=gpt-3.5-turbo
MAX_CONTEXT_RATIO=0.4

# Configuración del Logger
LOGS_DIR=logs
MAX_LOG_SIZE=10MB
BACKUP_COUNT=5
```

### Dependencias

```bash
pip install -r requirements.txt
```

**Nuevas dependencias agregadas:**
- `plotly`: Gráficos interactivos para el dashboard
- `openpyxl`: Exportación a Excel
- `streamlit`: Dashboard web interactivo

## 📁 Estructura de Archivos

```
app/
├── context_manager.py          # Context Manager mejorado
├── context_logger.py           # Logger avanzado
├── dashboard_context.py        # Dashboard de Streamlit
└── ...

logs/                           # Directorio de logs
├── context_manager.log         # Log principal
├── context_manager.log.1       # Backup 1
├── context_stats.jsonl         # Estadísticas JSON
├── context_alerts.log          # Alertas
└── status_report.json          # Reporte de estado

example_context_manager.py      # Ejemplo de uso
```

## 🧪 Testing

### Ejecutar Demostración

```bash
# Ejecutar ejemplo completo
python example_context_manager.py

# Ejecutar dashboard
streamlit run app/dashboard_context.py
```

### Ver Logs en Tiempo Real

```bash
# Log principal
tail -f logs/context_manager.log

# Alertas
tail -f logs/context_alerts.log

# Estadísticas
tail -f logs/context_stats.jsonl

# Reporte de estado
cat logs/status_report.json
```

## 📈 Métricas Esperadas del PR-2

### Mejoras en Monitoreo
- **Visibilidad Completa**: 100% de las consultas monitoreadas
- **Alertas en Tiempo Real**: Detección automática de problemas
- **Métricas Granulares**: Análisis detallado por período y modelo

### Eficiencia del Contexto
- **Score de Eficiencia**: Objetivo ≥0.8 (baseline estimado 0.6-0.7)
- **Utilización de Presupuesto**: Objetivo 70-90% (óptimo)
- **Ratio de Compresión**: Objetivo ≤0.7 (buena compactación)

### Gestión de Logs
- **Rotación Automática**: Sin intervención manual
- **Retención Inteligente**: Mantener solo logs relevantes
- **Exportación Fácil**: Múltiples formatos para análisis

## 🎯 Beneficios del PR-2

### Para Desarrolladores
- **Monitoreo en Tiempo Real**: Visibilidad inmediata del rendimiento
- **Alertas Proactivas**: Detección temprana de problemas
- **Métricas Granulares**: Análisis detallado para optimización

### Para el Sistema
- **Gestión Automática de Logs**: Sin intervención manual
- **Optimización Continua**: Recomendaciones automáticas
- **Escalabilidad**: Sistema de logging preparado para alto volumen

### Para el Usuario Final
- **Respuestas Más Eficientes**: Mejor uso del contexto
- **Menor Latencia**: Optimización automática del presupuesto
- **Mayor Calidad**: Monitoreo continuo de la eficiencia

## 🔄 Integración con PR-1

El PR-2 se integra perfectamente con el PR-1:

- **Spec Layer**: Proporciona métricas de cumplimiento de contratos
- **Subagentes**: Monitorea el rendimiento de cada fase
- **Context Manager**: Optimiza el uso de tokens según métricas
- **Verificación**: Alimenta el sistema de alertas con problemas de calidad

## 📋 Checklist de Implementación

### ✅ Context Manager Mejorado
- [x] Score de eficiencia implementado
- [x] Métricas agregadas por período
- [x] Sistema de recomendaciones
- [x] Gestión inteligente de presupuesto

### ✅ Context Logger Avanzado
- [x] Rotación automática de archivos
- [x] Logging especializado por tipo
- [x] Monitoreo en tiempo real
- [x] Sistema de alertas automáticas

### ✅ Dashboard de Streamlit
- [x] Visualizaciones interactivas
- [x] Configuración dinámica
- [x] Exportación de datos
- [x] Recomendaciones del sistema

### ✅ Ejemplos y Documentación
- [x] Script de demostración completo
- [x] README detallado
- [x] Ejemplos de uso
- [x] Instrucciones de configuración

## 🚀 Próximos Pasos

### PR-3: Retrieval Híbrido + Milvus
- Integración con Milvus para almacenamiento vectorial
- Implementación de BM25 con Whoosh/Elasticsearch
- Reranking con modelos locales

### PR-4: Subagentes + Verificación
- Pipeline completo de subagentes
- Verificación automática de calidad
- Integración con métricas del Context Manager

### PR-5: Evaluación + Benchmarking
- Conjunto de 40 preguntas doradas
- Scripts de benchmarking automático
- Métricas de calidad integradas

## 🤝 Contribución

### Estándares de Código
- **Type Hints**: Todos los métodos deben tener tipos
- **Docstrings**: Documentación completa en formato Google
- **Logging**: Uso consistente del sistema de logging avanzado
- **Tests**: Cobertura mínima del 80%

### Flujo de Trabajo
1. Crear feature branch desde `feature/pr-2-context-manager-logging`
2. Implementar cambios con tests
3. Verificar cumplimiento de estándares
4. Crear Pull Request con descripción detallada
5. Code review y merge

---

**¡El PR-2 está listo para elevar el monitoreo y la eficiencia del Context Manager al siguiente nivel! 🚀**

Con este PR, tu sistema RAG ahora tiene:
- **Monitoreo completo** del rendimiento del contexto
- **Alertas automáticas** para problemas de calidad
- **Dashboard interactivo** para análisis en tiempo real
- **Logging avanzado** con rotación automática
- **Métricas granulares** para optimización continua
