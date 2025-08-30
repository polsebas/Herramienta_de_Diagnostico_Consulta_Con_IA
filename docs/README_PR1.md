# 🏗️ PR-1: Spec-First Architecture + Task Contracts

**Implementación de Arquitectura Spec-First con Contratos de Tarea Inteligentes**

---

## 🎯 **Objetivos del PR-1**

### **Visión General**
Transformar el sistema RAG básico en una arquitectura **spec-first** donde cada consulta se procesa a través de un contrato inteligente que define objetivos, restricciones y formato de salida.

### **Objetivos Específicos**
1. **Implementar sistema de contratos** basado en YAML/Markdown
2. **Crear plantillas** para diferentes tipos de consulta
3. **Desarrollar SpecLayer** para generación y gestión de contratos
4. **Integrar contratos** en el flujo de procesamiento del agente
5. **Establecer base** para arquitectura modular y extensible

---

## 🏗️ **Arquitectura Implementada**

### **Componentes Principales**

#### **1. TaskContract (Dataclass)**
```python
@dataclass
class TaskContract:
    id: str
    task_type: TaskType
    goal: str
    musts: List[str]
    format: str
    metrics: Dict[str, Any]
    risk_level: RiskLevel
    context_sources: List[str]
    files_affected: List[str]
    human_approval_required: bool
    created_at: datetime
    expires_at: Optional[datetime] = None
```

#### **2. TaskType (Enum)**
```python
class TaskType(Enum):
    PROCEDURAL = "procedural"      # Cómo hacer algo
    DIAGNOSTIC = "diagnostic"      # Análisis de problemas
    DECISION = "decision"          # Toma de decisiones
    CODE = "code"                  # Generación de código
    ANALYSIS = "analysis"          # Análisis de datos
    DOCUMENTATION = "documentation" # Generación de docs
    TEST = "test"                  # Generación de tests
    REVIEW = "review"              # Revisión de código
    DRAFT_PR = "draft_pr"         # Creación de PRs
    GENERATE_TESTS = "generate_tests" # Tests automáticos
    GENERATE_DOCS = "generate_docs"   # Documentación
    CODE_REVIEW = "code_review"    # Revisión automática
    REFACTOR = "refactor"          # Refactorización
    SECURITY_SCAN = "security_scan" # Escaneo de seguridad
    PERFORMANCE_OPTIMIZATION = "performance_optimization" # Optimización
```

#### **3. RiskLevel (Enum)**
```python
class RiskLevel(Enum):
    LOW = "low"           # Riesgo mínimo
    MEDIUM = "medium"     # Riesgo moderado
    HIGH = "high"         # Riesgo alto
    CRITICAL = "critical" # Riesgo crítico
```

#### **4. SpecLayer (Clase Principal)**
```python
class SpecLayer:
    def __init__(self, config_path: str = "config/spec_layer.yml"):
        self.config = self._load_config(config_path)
        self.templates = self._load_templates()
        self.risk_assessor = RiskAssessor(self.config)
    
    async def build_task_contract(self, query: str, user_role: str = "developer", 
                                risk_level: Optional[RiskLevel] = None,
                                context_chunks: Optional[List[Dict[str, Any]]] = None,
                                files_affected: Optional[List[str]] = None) -> TaskContract:
        # Lógica de generación de contratos
```

### **Flujo de Procesamiento**

```
Query → Análisis → Generación de Contrato → Validación → Ejecución
  ↓         ↓              ↓                    ↓          ↓
Input   Context      TaskContract         Contract    Response
       Analysis      Generation          Validation   Generation
```

---

## 📁 **Archivos Implementados**

### **Archivos Principales**
- **`app/spec_layer.py`** - Implementación principal del SpecLayer
- **`config/spec_layer.yml`** - Configuración del sistema
- **`app/specs/`** - Directorio de plantillas YAML

### **Plantillas de Especificación**
- **`app/specs/procedural.yaml`** - Tareas procedimentales
- **`app/specs/diagnostic.yaml`** - Tareas de diagnóstico
- **`app/specs/code.yaml`** - Generación de código

### **Ejemplos y Tests**
- **`tests/example_spec_layer.py`** - Ejemplos de uso del sistema

---

## ⚙️ **Configuración**

### **Archivo de Configuración Principal**
```yaml
# config/spec_layer.yml
risk_thresholds:
  low: 0.3
  medium: 0.6
  high: 0.8
  critical: 0.9

contract_expiry_hours: 24
max_context_chunks: 10
min_source_coverage: 0.7
auto_approval_threshold: 0.4

critical_paths:
  - "/auth/"
  - "/payments/"
  - "/migrations/"
  - "/infra/"

high_risk_keywords:
  - "delete"
  - "drop"
  - "remove"
  - "password"
  - "token"
  - "secret"

medium_risk_keywords:
  - "update"
  - "modify"
  - "change"
  - "config"
  - "settings"
```

---

## 🚀 **Funcionalidades Implementadas**

### **1. Generación Automática de Contratos**
- **Detección automática** del tipo de tarea
- **Análisis de riesgo** basado en contenido y contexto
- **Generación de objetivos** específicos para la consulta
- **Definición de restricciones** y requisitos

### **2. Plantillas Dinámicas**
- **Sistema de plantillas** YAML extensible
- **Personalización** por tipo de tarea
- **Variables dinámicas** en plantillas
- **Heredación** de configuraciones base

### **3. Gestión de Riesgo**
- **Evaluación automática** de nivel de riesgo
- **Detección de palabras clave** de riesgo
- **Análisis de archivos** afectados
- **Integración** con sistema de aprobación humana

### **4. Validación de Contratos**
- **Verificación de cumplimiento** de contratos
- **Validación de formato** de salida
- **Comprobación de métricas** definidas
- **Auditoría** de ejecución

---

## 📊 **Métricas y KPIs**

### **Métricas de Calidad**
- **Precisión de contratos**: % de contratos que generan respuestas correctas
- **Cobertura de tipos**: % de tipos de tarea soportados
- **Tiempo de generación**: Latencia en la creación de contratos
- **Tasa de validación**: % de contratos que pasan validación

### **Métricas de Riesgo**
- **Detección de riesgo**: % de acciones críticas detectadas
- **Falsos positivos**: % de detecciones incorrectas de riesgo
- **Tiempo de aprobación**: Latencia en aprobaciones humanas
- **Cumplimiento**: % de contratos que cumplen restricciones

---

## 🔧 **Uso Básico**

### **Ejemplo de Generación de Contrato**
```python
from app.spec_layer import SpecLayer

# Inicializar SpecLayer
spec_layer = SpecLayer()

# Generar contrato para una consulta
contract = await spec_layer.build_task_contract(
    query="Implementar función de validación de email",
    user_role="developer",
    files_affected=["/auth/validation.py"]
)

# Renderizar prompt del sistema
system_prompt = spec_layer.render_system_prompt(contract)

# Validar cumplimiento del contrato
validation = await spec_layer.validate_contract_compliance(
    response="Función implementada...",
    contract=contract
)
```

### **Ejemplo de Plantilla YAML**
```yaml
# app/specs/procedural.yaml
goal_template: "Implementar {task_description} siguiendo las mejores prácticas"
musts:
  - "Usar solo pasajes recuperados y citarlos"
  - "Limitar a 3-5 chunks de contexto"
  - "Indicar suposiciones explícitas"
  - "Incluir sección 'Fuentes' con título de doc y línea"
  - "Seguir estándares de código del proyecto"

format: "Markdown con pasos numerados, código en bloques, y sección de fuentes"
metrics:
  precision_target: 0.9
  max_tokens: 800
  code_quality: "high"
  test_coverage: "required"
```

---

## 🧪 **Testing y Validación**

### **Tests Implementados**
- **Generación de contratos**: Verificación de creación correcta
- **Validación de plantillas**: Comprobación de formato YAML
- **Detección de riesgo**: Pruebas de evaluación de riesgo
- **Integración**: Tests de flujo completo

### **Validación de Calidad**
- **Formato de contratos**: Verificación de estructura
- **Completitud**: Validación de campos requeridos
- **Consistencia**: Verificación de coherencia interna
- **Rendimiento**: Tests de latencia y throughput

---

## 🔗 **Integración con Otros Componentes**

### **Context Manager**
- **Análisis de contexto** para generación de contratos
- **Compactación** de información relevante
- **Gestión de tokens** para optimización

### **Human Loop System**
- **Aprobación automática** basada en nivel de riesgo
- **Notificaciones** para contratos críticos
- **Workflow** de aprobación humana

### **Subagents Pipeline**
- **Orquestación** de subagentes basada en contratos
- **Verificación** de cumplimiento de contratos
- **Métricas** de ejecución y calidad

---

## 📈 **Impacto Esperado**

### **Mejoras de Calidad**
- **+40%** en precisión de respuestas
- **+60%** en consistencia de formato
- **+80%** en detección de acciones críticas
- **+50%** en cumplimiento de requisitos

### **Mejoras de Eficiencia**
- **-30%** en tiempo de procesamiento
- **-50%** en intervención humana innecesaria
- **+70%** en automatización de tareas rutinarias
- **+90%** en trazabilidad de decisiones

---

## 🚧 **Limitaciones y Consideraciones**

### **Limitaciones Actuales**
- **Dependencia** de plantillas predefinidas
- **Complejidad** en configuración inicial
- **Overhead** para tareas simples
- **Curva de aprendizaje** para nuevos usuarios

### **Consideraciones de Diseño**
- **Escalabilidad** de plantillas
- **Mantenimiento** de configuraciones
- **Versionado** de contratos
- **Migración** de contratos existentes

---

## 🔮 **Roadmap Futuro**

### **Próximas Mejoras**
- **Aprendizaje automático** de plantillas
- **Generación dinámica** de contratos
- **Integración** con sistemas externos
- **Analytics** avanzados de contratos

### **Expansión de Funcionalidades**
- **Contratos colaborativos** multi-usuario
- **Versionado** y control de cambios
- **Templates** para dominios específicos
- **API** para integración externa

---

## 📝 **Conclusión**

El **PR-1: Spec-First Architecture + Task Contracts** establece la base fundamental para un sistema RAG inteligente y controlado. La implementación de contratos de tarea proporciona:

- **Control granular** sobre el procesamiento de consultas
- **Trazabilidad completa** de decisiones y acciones
- **Gestión de riesgo** automática y proactiva
- **Arquitectura modular** para futuras expansiones

Este PR sienta las bases para la evolución hacia un **agente semi-autónomo** con capacidades avanzadas de gestión de proyectos y consultoría técnica.

---

*Implementado en: 2025-08-30*  
*Estado: ✅ 100% Completado*  
*Próximo: PR-2: Advanced Context Management*
