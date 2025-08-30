# 🚀 PR-A: Indexación de GitHub + Milvus

Este documento describe la implementación del **PR-A** del plan de implementación detallado en `PROGRESS.MD`. Este PR implementa la **Semana 1** del plan: **Infra e Indexación**.

## 🎯 Objetivos del PR-A

- **Indexación Automática**: Conectar con GitHub API y indexar PRs/issues
- **Almacenamiento Vectorial**: Integrar con Milvus para embeddings
- **Metadata Enriquecida**: Capturar información completa de cada item
- **Métricas de Calidad**: Medir éxito de indexación (meta: 100%)
- **Pruebas de Carga**: Indexar 50 PRs/issues como validación

## 🏗️ Arquitectura Implementada

### 1. Script Principal de Indexación (`scripts/index_github.py`)

**Características Principales:**
- **Conexión GitHub API**: Autenticación con token y manejo de rate limits
- **Indexación Inteligente**: PRs e issues con metadata completa
- **Integración Milvus**: Almacenamiento vectorial con embeddings
- **Manejo de Errores**: Sistema robusto con reintentos y logging
- **Métricas en Tiempo Real**: Seguimiento completo del proceso

**Clases Principales:**
```python
@dataclass
class GitHubItem:
    id: str                    # Identificador único
    type: str                  # 'pr' o 'issue'
    repo: str                  # Repositorio (owner/repo)
    title: str                 # Título del PR/issue
    body: str                  # Cuerpo/descripción
    files: List[str]           # Archivos modificados (solo PRs)
    author: str                # Autor del item
    labels: List[str]          # Etiquetas aplicadas
    created_at: int            # Timestamp de creación
    updated_at: int            # Timestamp de última actualización
    state: str                 # Estado (open, closed, merged)
    number: int                # Número del PR/issue
    raw_text: str              # Texto completo para embedding
    embedding: List[float]     # Vector de embedding

@dataclass
class IndexingStats:
    total_items: int           # Total de items procesados
    prs_indexed: int           # PRs indexados exitosamente
    issues_indexed: int        # Issues indexados exitosamente
    errors: int                # Errores encontrados
    start_time: datetime       # Inicio del proceso
    end_time: datetime         # Fin del proceso
    success_rate: float        # Tasa de éxito calculada
    duration_seconds: float    # Duración total en segundos
```

**Flujo de Indexación:**
```python
1. CONECTAR → GitHub API con token de autenticación
2. OBTENER → Repositorio y lista de PRs/issues
3. PROCESAR → Cada item con metadata completa
4. EMBEDDING → Generar vector de embedding (simulado por ahora)
5. ALMACENAR → En Milvus con estructura ChunkData
6. MÉTRICAS → Calcular estadísticas de éxito
```

### 2. Script de Pruebas (`scripts/test_github_indexing.py`)

**Características de Testing:**
- **Mocks Completos**: GitHub API y Milvus simulados
- **Pruebas Unitarias**: Validación de cada componente
- **Pruebas de Integración**: Flujo completo de indexación
- **Assertions Robustos**: Verificación de métricas y resultados
- **Cobertura Completa**: Todos los métodos y clases probados

**Mocks Implementados:**
```python
class MockGitHubRepo:          # Simula repositorio de GitHub
class MockPullRequest:         # Simula PR individual
class MockIssue:               # Simula issue individual
class MockMilvusStore:         # Simula almacén Milvus
class MockUser:                # Simula usuario de GitHub
class MockLabel:                # Simula etiqueta de GitHub
class MockFile:                 # Simula archivo modificado
```

### 3. Configuración del Sistema (`config/github_indexing.yml`)

**Secciones de Configuración:**
- **GitHub**: API rate limits, reintentos, timeouts
- **Milvus**: URI, colección, dimensiones, tipos de índice
- **Indexación**: Límites, filtros, exclusiones, lotes
- **Embeddings**: Modelo, longitud, normalización
- **Logging**: Niveles, archivos, rotación
- **Métricas**: Umbrales, alertas, rendimiento
- **Notificaciones**: Slack, email (opcionales)
- **Seguridad**: Rutas críticas, labels de riesgo, usuarios autorizados
- **Desarrollo**: Modo debug, mocks, pruebas

## 🚀 Uso del Sistema

### Ejemplo Básico

```bash
# Indexar repositorio completo (PRs + issues)
python scripts/index_github.py --repo owner/repo --limit 50

# Indexar solo PRs
python scripts/index_github.py --repo owner/repo --type prs --limit 25

# Indexar desde fecha específica
python scripts/index_github.py --repo owner/repo --since 2025-01-01

# Modo verbose para debugging
python scripts/index_github.py --repo owner/repo --verbose
```

### Variables de Entorno Requeridas

```bash
# Token de GitHub (obligatorio)
export GITHUB_TOKEN="your_github_token_here"

# Configuración de Milvus (opcional, usa valores por defecto)
export MILVUS_URI="localhost:19530"
export MILVUS_COLLECTION="github_items"
```

### Ejecutar Pruebas

```bash
# Ejecutar suite completa de pruebas
python scripts/test_github_indexing.py

# Verificar que las pruebas pasen
# Deberías ver: "🎉 ¡Todas las pruebas pasaron exitosamente!"
```

## 📊 Métricas y Rendimiento

### Métricas de Indexación

- **Tasa de Éxito**: Porcentaje de items indexados correctamente (meta: ≥95%)
- **Items por Minuto**: Velocidad de indexación (meta: ≥10 items/min)
- **Tiempo Total**: Duración completa del proceso (meta: <5min para 50 items)
- **Tasa de Error**: Porcentaje de fallos (meta: <5%)

### Métricas por Tipo

- **PRs Indexados**: Número de pull requests procesados
- **Issues Indexados**: Número de issues procesados
- **Archivos Procesados**: Total de archivos modificados en PRs
- **Labels Capturados**: Etiquetas y categorías identificadas

### Configuración de Umbrales

```yaml
metrics:
  success_rate_threshold: 0.95     # 95% mínimo de éxito
  error_rate_threshold: 0.05       # 5% máximo de errores
  max_indexing_time_seconds: 300   # 5 minutos máximo
  min_items_per_minute: 10         # 10 items por minuto mínimo
```

## 🔧 Configuración

### Archivo de Configuración

El sistema usa `config/github_indexing.yml` para configuración centralizada:

```yaml
# Ejemplo de configuración personalizada
github:
  api_rate_limit: 10000        # Aumentar rate limit
  retry_attempts: 5            # Más reintentos
  
milvus:
  uri: "milvus-prod:19530"    # Milvus en producción
  collection_name: "prod_github_items"
  
indexing:
  default_limit: 100           # Más items por defecto
  batch_delay_seconds: 0.5     # Menos delay entre lotes
```

### Variables de Entorno

```bash
# Configuración obligatoria
GITHUB_TOKEN=your_token_here

# Configuración opcional
MILVUS_URI=localhost:19530
MILVUS_COLLECTION=github_items
GITHUB_INDEXING_CONFIG=config/custom_config.yml
```

## 📁 Estructura de Archivos

```
scripts/
├── index_github.py              # Script principal de indexación
└── test_github_indexing.py      # Script de pruebas

config/
└── github_indexing.yml          # Configuración del sistema

app/
├── retrieval/
│   └── milvus_store.py          # Integración con Milvus
└── spec_layer.py                 # Generación de contratos

README_PR-A.md                    # Esta documentación
```

## 🧪 Testing

### Suite de Pruebas

```bash
# Ejecutar todas las pruebas
python scripts/test_github_indexing.py

# Verificar cobertura
# Las pruebas cubren:
# ✅ Creación de items de GitHub
# ✅ Estadísticas de indexación
# ✅ Flujo completo de indexación
# ✅ Integración con Milvus (mock)
# ✅ Manejo de errores
```

### Pruebas de Carga

```bash
# Probar con repositorio real (requiere GITHUB_TOKEN)
python scripts/index_github.py --repo owner/repo --limit 50

# Verificar métricas de rendimiento
# Meta: indexar 50 items en <5 minutos con ≥95% éxito
```

## 📈 Métricas Esperadas del PR-A

### Objetivos de Calidad
- **Cobertura de Indexación**: 100% de PRs/issues indexados correctamente
- **Tasa de Éxito**: ≥95% de items procesados sin errores
- **Tiempo de Respuesta**: <5 minutos para indexar 50 items
- **Precisión de Metadata**: 100% de campos capturados correctamente

### Objetivos de Rendimiento
- **Velocidad**: ≥10 items por minuto
- **Eficiencia**: <1 segundo por item promedio
- **Escalabilidad**: Preparado para repositorios grandes
- **Confiabilidad**: Sistema robusto con manejo de errores

### Objetivos de Integración
- **GitHub API**: Conexión estable y manejo de rate limits
- **Milvus**: Almacenamiento vectorial eficiente
- **Metadata**: Estructura compatible con sistema RAG existente
- **Logging**: Trazabilidad completa del proceso

## 🎯 Beneficios del PR-A

### Para Desarrolladores
- **Indexación Automática**: No más indexación manual de PRs/issues
- **Metadata Completa**: Información rica para análisis y búsqueda
- **Sistema Robusto**: Manejo automático de errores y reintentos
- **Configuración Flexible**: Parámetros ajustables según necesidades

### Para el Sistema RAG
- **Contexto Enriquecido**: PRs/issues como fuente de conocimiento
- **Búsqueda Semántica**: Embeddings para consultas inteligentes
- **Trazabilidad**: Seguimiento completo de cambios en el repositorio
- **Análisis Temporal**: Evolución del proyecto a lo largo del tiempo

### Para el Equipo
- **Visibilidad**: Estado completo del repositorio indexado
- **Análisis**: Métricas de actividad y tendencias
- **Auditoría**: Historial completo de cambios y decisiones
- **Colaboración**: Contexto compartido para todos los miembros

## 🔄 Integración con PRs Anteriores

### PR-1: Spec Layer
- **Contratos de Indexación**: Generación automática de especificaciones
- **Tipos de Item**: Filtros automáticos según tipo (PR vs Issue)
- **Validación**: Verificación de cumplimiento de contratos

### PR-2: Context Manager
- **Métricas Integradas**: Conecta métricas de indexación con contexto
- **Optimización**: Ajuste basado en métricas de éxito
- **Dashboard**: Visualización de estado de indexación

### PR-3: Retrieval Híbrido
- **Búsqueda en PRs**: Consultas semánticas en items indexados
- **Filtros Avanzados**: Búsqueda por autor, labels, archivos
- **Reranking**: Ordenamiento inteligente de resultados

### PR-4: Pipeline de Subagentes
- **Análisis de PRs**: Subagente de análisis para items de GitHub
- **Verificación**: Control de calidad de información indexada
- **Métricas Unificadas**: Integración con métricas del pipeline

## 📋 Checklist de Implementación

### ✅ Indexación de GitHub
- [x] Script principal de indexación (`index_github.py`)
- [x] Conexión con GitHub API
- [x] Procesamiento de PRs e issues
- [x] Captura de metadata completa
- [x] Manejo de errores y reintentos

### ✅ Integración con Milvus
- [x] Almacenamiento en Milvus
- [x] Estructura ChunkData compatible
- [x] Embeddings vectoriales (simulados)
- [x] Metadata enriquecida en JSON

### ✅ Sistema de Pruebas
- [x] Script de pruebas completo
- [x] Mocks de GitHub y Milvus
- [x] Pruebas unitarias e integración
- [x] Validación de métricas

### ✅ Configuración y Documentación
- [x] Archivo de configuración YAML
- [x] README detallado
- [x] Variables de entorno
- [x] Ejemplos de uso

## 🚀 Próximos Pasos

### PR-B: Human-in-the-Loop y Notificaciones (Semana 2)
- Sistema de notificaciones Slack/GitHub
- Listener para aprobaciones humanas
- Integración con `check_critical_action`

### PR-C: Spec Layer + Contratos (Semana 2)
- Hook en Agent para generar contratos
- Integración con sistema de indexación
- Validación automática de cumplimiento

### PR-D: Cursor Integration (Semana 3)
- Background agents para tareas seguras
- Generación de draft PRs
- Tests y documentación automática

### PR-E: Auditoría y Evaluación (Semana 4)
- Sistema de logs/audit trail
- Golden set de 20 issues para evaluación
- Métricas de precisión del plan

## 🤝 Contribución

### Estándares de Código
- **Type Hints**: Todos los métodos tienen tipos completos
- **Docstrings**: Documentación en formato Google
- **Error Handling**: Manejo robusto de excepciones
- **Tests**: Cobertura del 100% de funcionalidad crítica

### Flujo de Trabajo
1. Crear feature branch desde `feature/pr-a-github-indexing`
2. Implementar cambios con tests
3. Verificar cumplimiento de estándares
4. Crear Pull Request con descripción detallada
5. Code review y merge

## 🔧 Troubleshooting

### Problemas Comunes

**Error de autenticación GitHub:**
```bash
# Verificar token
echo $GITHUB_TOKEN

# Configurar token
export GITHUB_TOKEN="your_token_here"
```

**Error de conexión Milvus:**
```bash
# Verificar que Milvus esté corriendo
docker ps | grep milvus

# Usar configuración por defecto (modo simulado)
export MILVUS_URI="localhost:19530"
```

**Rate limiting de GitHub:**
```bash
# Reducir velocidad de indexación
# Ajustar en config/github_indexing.yml:
batch_delay_seconds: 2  # Aumentar delay entre lotes
```

**Errores de indexación:**
```bash
# Verificar logs
tail -f logs/github_indexing.log

# Ejecutar con verbose
python scripts/index_github.py --repo owner/repo --verbose
```

---

**¡El PR-A está listo para indexar tu repositorio de GitHub! 🚀**

Con este PR, tu sistema RAG ahora puede:
- **Indexar automáticamente** todos los PRs e issues de GitHub
- **Almacenar metadata completa** en Milvus para búsqueda semántica
- **Proporcionar contexto rico** sobre el estado del proyecto
- **Mantener trazabilidad** de todos los cambios y decisiones
- **Escalar eficientemente** para repositorios grandes

El sistema ahora proporciona:
- **Visibilidad completa** del repositorio indexado
- **Búsqueda semántica** en PRs e issues
- **Métricas de actividad** del proyecto
- **Contexto histórico** para análisis y decisiones
- **Base sólida** para el siguiente PR: Human-in-the-Loop
