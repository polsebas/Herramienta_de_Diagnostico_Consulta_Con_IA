# 🚀 PR-3: Retrieval Híbrido + Milvus

Este documento describe la implementación del **PR-3** del plan "Next Level", que implementa un sistema de recuperación híbrido avanzado combinando BM25, búsqueda vectorial y reranking inteligente.

## 🎯 Objetivos del PR-3

- **Retrieval Híbrido**: BM25 + Vectorial + Reranking inteligente
- **Integración Milvus**: Almacén vectorial optimizado con esquema robusto
- **Metadatos Fuertes**: Enriquecimiento de chunks con información detallada
- **Filtros Avanzados**: Por tipo de documento, sección y recency

## 🏗️ Arquitectura Implementada

### 1. Sistema de Retrieval Híbrido (`app/retrieval/hybrid.py`)

**Características Principales:**
- **Fusión Inteligente**: Combina resultados de BM25 y búsqueda vectorial
- **Reranking Avanzado**: Score ponderado por múltiples factores
- **Filtros Granulares**: Por metadatos, score y contenido
- **Fallback Robusto**: Sistema de respaldo cuando fallan componentes

**Algoritmo de Fusión Híbrida:**
```python
# Score híbrido = (vector_score * 0.7) + (bm25_score * 0.3)
# Boost para documentos que aparecen en ambas búsquedas (1.2x)
# Normalización por ranking para evitar sesgos
```

**Reranking Inteligente:**
- **Score Base (40%)**: Score híbrido original
- **Relevancia Semántica (30%)**: Overlap de palabras clave
- **Calidad del Contenido (20%)**: Estructura, legibilidad, metadatos
- **Frescura (5%)**: Fecha de creación/actualización
- **Metadatos (5%)**: Completitud de información

### 2. Almacén Vectorial Milvus (`app/retrieval/milvus_store.py`)

**Esquema Optimizado:**
```python
fields = [
    FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=64),
    FieldSchema(name="doc_id", dtype=DataType.VARCHAR, max_length=128),
    FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=256),
    FieldSchema(name="section", dtype=DataType.VARCHAR, max_length=128),
    FieldSchema(name="path", dtype=DataType.VARCHAR, max_length=512),
    FieldSchema(name="line_start", dtype=DataType.INT64),
    FieldSchema(name="line_end", dtype=DataType.INT64),
    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=16384),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=384),
    FieldSchema(name="doc_type", dtype=DataType.VARCHAR, max_length=64),
    FieldSchema(name="version", dtype=DataType.VARCHAR, max_length=32),
    FieldSchema(name="created_at", dtype=DataType.INT64),
    FieldSchema(name="updated_at", dtype=DataType.INT64),
    FieldSchema(name="tags", dtype=DataType.VARCHAR, max_length=1024),
    FieldSchema(name="metadata_json", dtype=DataType.VARCHAR, max_length=8192)
]
```

**Tipos de Índice:**
- **HNSW**: Para colecciones pequeñas (<1M vectores) - alta precisión
- **IVF_FLAT**: Para colecciones grandes (>1M vectores) - balance precisión/velocidad

**Operaciones Soportadas:**
- Inserción en lotes con validación
- Búsqueda por similitud con filtros
- Actualización y eliminación de chunks
- Backup y restauración de colecciones
- Estadísticas de rendimiento

### 3. Índice BM25 (`app/retrieval/bm25_index.py`)

**Características Avanzadas:**
- **Tokenización Inteligente**: Stemming y eliminación de stopwords en español
- **Índices de Metadatos**: Filtrado rápido por tipo, sección, ruta y tags
- **Configuración Flexible**: Parámetros k1 y b ajustables
- **Persistencia**: Exportación/importación en JSON

**Algoritmo BM25:**
```python
# Score BM25 = IDF * TF_normalizado
# TF_normalizado = (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * (doc_length / avg_length)))
# IDF = log((total_docs - df + 0.5) / (df + 0.5))
```

**Filtros Disponibles:**
- Por tipo de documento (`doc_type`)
- Por sección (`section`)
- Por ruta (`path`)
- Por tags específicos
- Por score mínimo
- Por fecha de creación/actualización

## 🚀 Uso del Sistema

### Ejemplo Básico

```python
from app.retrieval import HybridRetriever, MilvusVectorStore, BM25Index

# Inicializar componentes
vector_store = MilvusVectorStore(config=MilvusConfig())
bm25_index = BM25Index()

# Crear retriever híbrido
retriever = HybridRetriever(
    vector_store=vector_store,
    bm25_index=bm25_index,
    config={
        "hybrid_weights": {"vector": 0.7, "bm25": 0.3},
        "enable_reranking": True,
        "enable_filters": True
    }
)

# Búsqueda híbrida
results = retriever.search(
    query="¿Cómo configuro la autenticación JWT?",
    top_k=10,
    filters=SearchFilters(doc_type="documentation", min_score=0.5)
)
```

### Ejemplo Completo

Ver `example_hybrid_retrieval.py` para una demostración completa del sistema.

## 📊 Métricas y Rendimiento

### Métricas de Calidad

- **Precisión**: Porcentaje de resultados relevantes
- **Recall**: Porcentaje de documentos relevantes recuperados
- **nDCG**: Normalized Discounted Cumulative Gain
- **MRR**: Mean Reciprocal Rank

### Métricas de Rendimiento

- **Latencia de Búsqueda**: Tiempo promedio por consulta
- **Throughput**: Consultas por segundo
- **Uso de Memoria**: Consumo de RAM del sistema
- **Escalabilidad**: Rendimiento con diferentes tamaños de colección

### Configuración de Milvus

**Parámetros HNSW:**
```python
index_params = {
    "index_type": "HNSW",
    "metric_type": "IP",
    "params": {
        "M": 32,           # Conexiones por nodo
        "efConstruction": 200  # Precisión durante construcción
    }
}
```

**Parámetros IVF_FLAT:**
```python
index_params = {
    "index_type": "IVF_FLAT",
    "metric_type": "IP",
    "params": {
        "nlist": 1024  # Número de clusters
    }
}
```

## 🔧 Configuración

### Variables de Entorno

```bash
# Configuración de Milvus
MILVUS_URI=localhost:19530
MILVUS_COLLECTION=system_knowledge
EMBEDDING_DIM=384
INDEX_TYPE=HNSW

# Configuración del Retriever
HYBRID_VECTOR_WEIGHT=0.7
HYBRID_BM25_WEIGHT=0.3
ENABLE_RERANKING=true
ENABLE_FILTERS=true
```

### Dependencias

```bash
pip install -r requirements.txt
```

**Nuevas dependencias agregadas:**
- `pymilvus`: Cliente oficial de Milvus
- `rank-bm25`: Implementación BM25 optimizada
- `numpy`: Operaciones numéricas para embeddings

## 📁 Estructura de Archivos

```
app/retrieval/
├── __init__.py              # Exportaciones del módulo
├── hybrid.py                # Retriever híbrido principal
├── milvus_store.py          # Integración con Milvus
└── bm25_index.py            # Índice BM25

example_hybrid_retrieval.py  # Ejemplo de uso completo
README_PR3.md                # Esta documentación
```

## 🧪 Testing

### Ejecutar Demostración

```bash
# Ejecutar ejemplo completo
python example_hybrid_retrieval.py

# Ejecutar con Milvus real
export MILVUS_URI=localhost:19530
python example_hybrid_retrieval.py
```

### Configurar Milvus Local

```bash
# Usando Docker
docker run -d --name milvus-standalone \
  -p 19530:19530 \
  -p 9091:9091 \
  milvusdb/milvus:latest

# Verificar estado
docker logs milvus-standalone
```

## 📈 Métricas Esperadas del PR-3

### Mejoras en Retrieval
- **Recall@5**: +20% con búsqueda híbrida vs. solo vectorial
- **Precisión@5**: +15% con reranking inteligente
- **Latencia**: <100ms para consultas simples, <500ms para complejas
- **Escalabilidad**: Soporte para colecciones de 1M+ chunks

### Calidad de Resultados
- **Relevancia**: Score de relevancia ≥0.8 para top-5 resultados
- **Diversidad**: Evitar resultados duplicados o muy similares
- **Metadatos**: 100% de chunks con metadatos completos
- **Trazabilidad**: Citas precisas con línea de código

### Rendimiento del Sistema
- **Throughput**: 100+ consultas por segundo
- **Memoria**: <2GB RAM para colección de 100K chunks
- **Disco**: <10GB para colección de 100K chunks
- **CPU**: <20% uso promedio durante búsquedas

## 🎯 Beneficios del PR-3

### Para Desarrolladores
- **Búsqueda Más Precisa**: Combinación de semántica y palabras clave
- **Filtros Granulares**: Búsquedas específicas por contexto
- **Metadatos Enriquecidos**: Información completa de cada chunk
- **API Unificada**: Interfaz simple para búsquedas complejas

### Para el Sistema
- **Escalabilidad**: Preparado para grandes volúmenes de datos
- **Flexibilidad**: Múltiples estrategias de búsqueda
- **Robustez**: Fallback automático en caso de errores
- **Monitoreo**: Métricas detalladas de rendimiento

### Para el Usuario Final
- **Resultados Más Relevantes**: Mejor ranking de respuestas
- **Búsquedas Contextuales**: Filtros por tipo y sección
- **Respuestas Rápidas**: Optimización de latencia
- **Mayor Precisión**: Menos resultados irrelevantes

## 🔄 Integración con PRs Anteriores

### PR-1: Spec Layer
- **Contratos de Tarea**: Metadatos de búsqueda basados en contratos
- **Tipos de Consulta**: Filtros automáticos según el tipo
- **Validación**: Verificación de cumplimiento de contratos

### PR-2: Context Manager
- **Métricas de Retrieval**: Logging de performance de búsqueda
- **Optimización**: Ajuste automático de parámetros
- **Monitoreo**: Dashboard de estadísticas de retrieval

## 📋 Checklist de Implementación

### ✅ Sistema Híbrido
- [x] Retriever híbrido con fusión inteligente
- [x] Reranking basado en múltiples factores
- [x] Sistema de filtros avanzados
- [x] Fallback robusto para errores

### ✅ Integración Milvus
- [x] Esquema optimizado para chunks
- [x] Índices HNSW/IVF_FLAT configurables
- [x] Operaciones CRUD completas
- [x] Backup y restauración

### ✅ Índice BM25
- [x] Implementación BM25 con stemming
- [x] Índices de metadatos para filtrado
- [x] Configuración flexible de parámetros
- [x] Persistencia en JSON

### ✅ Ejemplos y Documentación
- [x] Script de demostración completo
- [x] README detallado
- [x] Ejemplos de configuración
- [x] Instrucciones de deployment

## 🚀 Próximos Pasos

### PR-4: Subagentes + Verificación
- Pipeline completo de subagentes
- Verificación automática de calidad
- Integración con métricas del Context Manager

### PR-5: Evaluación + Benchmarking
- Conjunto de 40 preguntas doradas
- Scripts de benchmarking automático
- Métricas de calidad integradas

### PR-6: CLI + FastAPI
- Herramienta de línea de comandos
- API REST para integración
- Dashboard web de monitoreo

## 🤝 Contribución

### Estándares de Código
- **Type Hints**: Todos los métodos deben tener tipos
- **Docstrings**: Documentación completa en formato Google
- **Error Handling**: Manejo robusto de excepciones
- **Tests**: Cobertura mínima del 80%

### Flujo de Trabajo
1. Crear feature branch desde `feature/pr-3-hybrid-retrieval-milvus`
2. Implementar cambios con tests
3. Verificar cumplimiento de estándares
4. Crear Pull Request con descripción detallada
5. Code review y merge

## 🔧 Troubleshooting

### Problemas Comunes

**Milvus no responde:**
```bash
# Verificar estado del contenedor
docker ps | grep milvus

# Ver logs
docker logs milvus-standalone

# Reiniciar si es necesario
docker restart milvus-standalone
```

**Búsquedas lentas:**
```python
# Ajustar parámetros de índice
config = MilvusConfig(
    index_type="HNSW",  # Cambiar a IVF_FLAT para colecciones grandes
    metric_type="IP"    # Cambiar a L2 si es necesario
)
```

**Resultados de baja calidad:**
```python
# Ajustar pesos híbridos
retriever.update_config({
    "hybrid_weights": {"vector": 0.8, "bm25": 0.2}
})

# Habilitar reranking
retriever.update_config({
    "enable_reranking": True,
    "rerank_top_k": 100
})
```

---

**¡El PR-3 está listo para elevar la calidad del retrieval al siguiente nivel! 🚀**

Con este PR, tu sistema RAG ahora tiene:
- **Búsqueda híbrida inteligente** que combina lo mejor de BM25 y vectorial
- **Integración robusta con Milvus** para escalabilidad empresarial
- **Reranking avanzado** basado en múltiples factores de calidad
- **Metadatos enriquecidos** para búsquedas contextuales precisas
- **Filtros granulares** para consultas específicas
- **Sistema de fallback** para máxima robustez
