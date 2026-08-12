# Documentación del Sistema Next Level RAG

> **Archivado (agosto 2026).** Este índice es histórico.  
> Cierre del proyecto: [CIERRE.md](../CIERRE.md) · [ARCHIVE.md](../ARCHIVE.md) · progreso: [PROGRESS.md](PROGRESS.md)

**Herramienta de Diagnóstico y Consulta con IA — documentación del spike 2025**

---

## Descripción general

Este directorio contiene la documentación detallada del experimento **Next Level RAG con Human-in-the-Loop**, organizada por Pull Request. **No hay roadmap vigente**; los estados “completado / planeado” de abajo reflejan la narrativa de 2025, no un compromiso de mantenimiento.

---

## 📋 **Índice de Documentación**

### **🏗️ Arquitectura Base (PRs 1-4)**

#### **PR-1: Spec-First Architecture + Task Contracts**
- **Archivo**: [README_PR1.md](README_PR1.md) *(Pendiente de creación)*
- **Descripción**: Implementación de arquitectura spec-first con contratos de tarea
- **Funcionalidades**: TaskContract, TaskType, RiskLevel, SpecLayer
- **Estado**: ✅ Completado

#### **PR-2: Advanced Context Management**
- **Archivo**: [README_PR2.md](README_PR2.md)
- **Descripción**: Gestión avanzada de contexto con compactación inteligente
- **Funcionalidades**: ContextManager, ContextLogger, Dashboard
- **Estado**: ✅ Completado

#### **PR-3: Hybrid Retrieval System**
- **Archivo**: [README_PR3.md](README_PR3.md)
- **Descripción**: Sistema de recuperación híbrido vector + BM25
- **Funcionalidades**: Milvus, BM25, Reranking, Metadata
- **Estado**: ✅ Completado

#### **PR-4: Complete Subagent Pipeline**
- **Archivo**: [README_PR4.md](README_PR4.md)
- **Descripción**: Pipeline completo de subagentes con orquestador
- **Funcionalidades**: Orchestrator, Verification, PipelineMetrics
- **Estado**: ✅ Completado

### **🚀 Evolución Next Level (PRs A-E)**

#### **PR-A: GitHub Integration & Indexing**
- **Archivo**: [README_PR-A.md](README_PR-A.md)
- **Descripción**: Indexación automática de PRs e Issues en Milvus
- **Funcionalidades**: GitHub API, Metadata, Vector Storage
- **Estado**: ✅ Completado

#### **PR-B: Human-in-the-Loop System**
- **Archivo**: [README_PR-B.md](README_PR-B.md)
- **Descripción**: Sistema de aprobación humana para acciones críticas
- **Funcionalidades**: Approval Workflows, Notifications, Risk Assessment
- **Estado**: ✅ Completado

#### **PR-C: Spec Layer + Intelligent Contracts**
- **Archivo**: [README_PR-C.md](README_PR-C.md)
- **Descripción**: Integración completa del Spec Layer con el sistema
- **Funcionalidades**: Contract Validation, GitHub Context, Risk Detection
- **Estado**: ✅ Completado

#### **PR-D: Cursor Integration & Background Tasks**
- **Archivo**: [README_PR-D.md](README_PR-D.md)
- **Descripción**: Agentes tipo Cursor para tareas en background
- **Funcionalidades**: Background Tasks, Draft PRs, Test Generation
- **Estado**: ✅ Completado

#### **PR-E: Audit & Evaluation System**
- **Archivo**: [README_PR-E.md](README_PR-E.md)
- **Descripción**: Sistema completo de auditoría y evaluación
- **Funcionalidades**: Golden Set, Quality Metrics, Audit Logging
- **Estado**: ✅ Completado

---

## 📖 **Documentación Adicional**

### **Plan de Evolución**
- **Archivo**: [README_NEXT_LEVEL.md](README_NEXT_LEVEL.md)
- **Descripción**: Plan original de evolución del sistema RAG
- **Contenido**: Especificaciones técnicas y roadmap de implementación

### **Manuales de Usuario**
- **Archivo**: [MANUAL_USUARIO.md](MANUAL_USUARIO.md) *(Español)*
- **Descripción**: Manual completo para usuarios finales sin conocimientos técnicos
- **Contenido**: Guía paso a paso, casos de uso prácticos, solución de problemas

- **Archivo**: [USER_MANUAL.md](USER_MANUAL.md) *(English)*
- **Descripción**: Complete user manual for end users without technical knowledge
- **Content**: Step-by-step guide, practical use cases, troubleshooting

---

## 🔍 **Cómo Usar Esta Documentación**

### **Para Desarrolladores**
1. **Nuevos en el proyecto**: Comenzar con [README.md](../README.md) (documentación principal)
2. **Implementación específica**: Consultar README del PR correspondiente
3. **Arquitectura**: Revisar PRs 1-4 para entender la base del sistema
4. **Funcionalidades avanzadas**: Consultar PRs A-E para características Next Level

### **Para Usuarios**
1. **Inicio rápido**: [README.md](../README.md) con ejemplos básicos
2. **Configuración**: Revisar archivos de configuración en `../config/`
3. **Casos de uso**: Ejemplos en `../tests/example_*.py`

### **Para Administradores**
1. **Deployment**: [README.md](../README.md) con instrucciones de instalación
2. **Configuración**: Archivos YAML en `../config/`
3. **Monitoreo**: Logs en `../logs/` y métricas en `../eval/`

---

## 📊 **Estado del Sistema**

### **✅ Completitud General: 100%**
- **PRs Base (1-4)**: 4/4 Completados
- **PRs Next Level (A-E)**: 5/5 Completados
- **Total**: 9/9 Objetivos Implementados

### **🎯 Funcionalidades Principales**
- ✅ **Spec-First Architecture** con contratos inteligentes
- ✅ **Context Management** avanzado con compactación
- ✅ **Hybrid Retrieval** vector + BM25 + Milvus
- ✅ **Subagent Pipeline** completo con orquestador
- ✅ **GitHub Integration** para contexto automático
- ✅ **Human-in-the-Loop** para aprobaciones críticas
- ✅ **Cursor Integration** para tareas en background
- ✅ **Audit & Evaluation** con golden set de 20 preguntas

---

## 🔗 **Enlaces Rápidos**

- **🏠 [Documentación Principal](../README.md)**
- **🇪🇸 [Documentación en Español](../LEAME.md)**
- **📋 [Plan de Progreso](PROGRESS.md)**
- **🧪 [Tests y Ejemplos](../tests/)**
- **⚙️ [Configuración](../config/)**
- **📊 [Evaluación](../eval/)**
- **📝 [Logs](../logs/)**

---

## 📝 **Mantenimiento de Documentación**

### **Reglas de Actualización**
1. **Cada PR** debe incluir su README correspondiente
2. **READMEs** deben actualizarse cuando cambien las funcionalidades
3. **Ejemplos** deben mantenerse sincronizados con el código
4. **Configuraciones** deben documentarse en los archivos YAML

### **Responsabilidades**
- **Desarrolladores**: Mantener READMEs de sus PRs actualizados
- **Tech Lead**: Revisar consistencia de documentación
- **QA**: Verificar que ejemplos funcionen correctamente

---

*Última actualización: 2025-08-30*
*Versión del sistema: Next Level RAG v1.0 - 100% Completado*
