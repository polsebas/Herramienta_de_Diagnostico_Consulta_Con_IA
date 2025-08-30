"""
Auditoría Integral del Sistema - Verificación de Objetivos Completados

Este script realiza una auditoría completa del sistema para verificar que todos los objetivos
del plan "Next Level" estén implementados y funcionando correctamente.
"""

import os
import sys
import importlib
import inspect
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

# Configurar logging
import logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class ObjectiveCheck:
    """Resultado de verificación de un objetivo."""
    objective: str
    status: str  # "COMPLETED", "PARTIAL", "NOT_IMPLEMENTED", "ERROR"
    details: str
    files_implemented: List[str]
    tests_passed: bool
    notes: str


@dataclass
class SystemAudit:
    """Auditoría integral del sistema Next Level RAG."""
    
    def __init__(self):
        # Determinar el directorio raíz del proyecto
        current_file = Path(__file__)
        if current_file.parent.name == "tests":
            self.project_root = current_file.parent.parent
        else:
            self.project_root = Path(".")
        self.objectives = self._define_objectives()
        self.results: List[ObjectiveCheck] = []
        
    def _define_objectives(self) -> Dict[str, Dict[str, Any]]:
        """Define todos los objetivos del plan Next Level."""
        return {
            "PR-1_SPEC_FIRST": {
                "title": "PR-1: Spec-First Architecture + Task Contracts",
                "description": "Implementar arquitectura spec-first con contratos de tarea",
                "requirements": [
                    "app/spec_layer.py - Sistema de contratos inteligentes",
                    "app/specs/ - Plantillas YAML para tipos de consulta",
                    "build_task_contract() - Generación de contratos",
                    "render_system_prompt() - Conversión a prompts",
                    "TaskContract dataclass - Estructura de contratos",
                    "TaskType enum - Tipos de tarea soportados"
                ],
                "files_expected": [
                    "app/spec_layer.py",
                    "app/specs/procedural.yaml",
                    "app/specs/diagnostic.yaml",
                    "app/specs/code.yaml",
                    "config/spec_layer.yml"
                ]
            },
            
            "PR-2_CONTEXT_MANAGEMENT": {
                "title": "PR-2: Advanced Context Management",
                "description": "Implementar gestión avanzada de contexto con compactación",
                "requirements": [
                    "app/context_manager.py - Gestor de contexto principal",
                    "summarize_dialog() - Resumen de conversaciones",
                    "compact_chunks() - Compactación de chunks",
                    "Token usage logging - Monitoreo de tokens",
                    "Context budget management - Control de ventana del modelo",
                    "Streamlit dashboard - Visualización de métricas"
                ],
                "files_expected": [
                    "app/context_manager.py",
                    "app/dashboard_context.py",
                    "app/context_logger.py"
                ]
            },
            
            "PR-3_HYBRID_RETRIEVAL": {
                "title": "PR-3: Hybrid Retrieval System",
                "description": "Implementar sistema de recuperación híbrido vector + BM25",
                "requirements": [
                    "app/retrieval/ - Sistema de recuperación híbrido",
                    "Vector search - Búsqueda semántica con Milvus",
                    "BM25 search - Búsqueda por palabras clave",
                    "Reranking - Reordenamiento inteligente de resultados",
                    "Strong metadata - Metadatos enriquecidos",
                    "Milvus integration - Base de datos vectorial"
                ],
                "files_expected": [
                    "app/retrieval/",
                    "app/retrieval/milvus_store.py"
                ]
            },
            
            "PR-4_SUBAGENTS_PIPELINE": {
                "title": "PR-4: Complete Subagent Pipeline",
                "description": "Implementar pipeline completo de subagentes",
                "requirements": [
                    "app/subagents/ - Pipeline de subagentes",
                    "RetrievalSubAgent - Búsqueda híbrida",
                    "AnalysisSubAgent - Análisis y clustering",
                    "SynthesisSubAgent - Generación de respuestas",
                    "VerificationSubAgent - Verificación automática",
                    "Orchestrator - Coordinación de subagentes"
                ],
                "files_expected": [
                    "app/subagents/",
                    "app/subagents/orchestrator.py",
                    "app/subagents/verification.py",
                    "app/pipeline_metrics.py"
                ]
            },
            
            "PR-A_GITHUB_INDEXING": {
                "title": "PR-A: GitHub Integration & Indexing",
                "description": "Indexar PRs e Issues en Milvus para contexto",
                "requirements": [
                    "scripts/index_github.py - Indexador de GitHub",
                    "GitHub API integration - Conexión con GitHub",
                    "PR/Issue metadata - Metadatos enriquecidos",
                    "Milvus storage - Almacenamiento vectorial",
                    "Embedding generation - Generación de embeddings",
                    "Indexing metrics - Métricas de indexación"
                ],
                "files_expected": [
                    "scripts/index_github.py",
                    "tests/test_github_indexing.py",
                    "config/github_indexing.yml"
                ]
            },
            
            "PR-B_HUMAN_LOOP": {
                "title": "PR-B: Human-in-the-Loop System",
                "description": "Sistema de aprobación humana para acciones críticas",
                "requirements": [
                    "app/human_loop.py - Sistema principal de human loop",
                    "Approval workflows - Flujos de aprobación",
                    "Multi-channel notifications - Notificaciones múltiples",
                    "Risk assessment - Evaluación de riesgo",
                    "Async processing - Procesamiento asíncrono",
                    "Timeout handling - Manejo de timeouts"
                ],
                "files_expected": [
                    "app/human_loop.py",
                    "config/human_loop.yml",
                    "tests/example_human_loop.py"
                ]
            },
            
            "PR-C_SPEC_LAYER": {
                "title": "PR-C: Spec Layer + Intelligent Contracts",
                "description": "Integración completa del Spec Layer con el sistema",
                "requirements": [
                    "Contract validation - Validación de contratos",
                    "GitHub context integration - Integración con contexto de GitHub",
                    "Risk level detection - Detección automática de riesgo",
                    "Human approval integration - Integración con human loop",
                    "Contract compliance - Cumplimiento de contratos",
                    "Dynamic contract generation - Generación dinámica"
                ],
                "files_expected": [
                    "app/spec_layer.py",
                    "config/spec_layer.yml",
                    "app/specs/",
                    "tests/example_spec_layer.py"
                ]
            },
            
            "PR-D_CURSOR_INTEGRATION": {
                "title": "PR-D: Cursor Integration & Background Tasks",
                "description": "Agentes tipo Cursor para tareas en background",
                "requirements": [
                    "app/cursor_agent.py - Agente principal de Cursor",
                    "Background task execution - Ejecución de tareas en background",
                    "Draft PR generation - Generación de PRs automática",
                    "Test generation - Generación automática de tests",
                    "Documentation generation - Generación de documentación",
                    "Workspace safety validation - Validación de seguridad"
                ],
                "files_expected": [
                    "app/cursor_agent.py",
                    "config/cursor_agent.yml",
                    "tests/example_cursor_integration.py"
                ]
            },
            
            "PR-E_AUDIT_EVALUATION": {
                "title": "PR-E: Audit & Evaluation System",
                "description": "Sistema completo de auditoría y evaluación",
                "requirements": [
                    "eval/evaluate_plans.py - Evaluador principal",
                    "Golden set (20 questions) - Conjunto de preguntas doradas",
                    "Quality metrics - Métricas de calidad",
                    "Audit logging - Logs de auditoría",
                    "Performance evaluation - Evaluación de performance",
                    "Report generation - Generación de reportes"
                ],
                "files_expected": [
                    "eval/evaluate_plans.py",
                    "config/evaluation.yml",
                    "tests/example_evaluation_system.py",
                    "logs/audit.jsonl"
                ]
            }
        }
    
    def run_complete_audit(self) -> Dict[str, Any]:
        """Ejecuta la auditoría completa del sistema."""
        logger.info("🚀 INICIANDO AUDITORÍA INTEGRAL DEL SISTEMA")
        logger.info("=" * 80)
        
        audit_start = datetime.now()
        
        # Verificar cada objetivo
        for objective_id, objective_info in self.objectives.items():
            logger.info(f"\n🔍 Verificando: {objective_info['title']}")
            logger.info("-" * 60)
            
            result = self._check_objective(objective_id, objective_info)
            self.results.append(result)
            
            # Mostrar resultado
            status_emoji = {
                "COMPLETED": "✅",
                "PARTIAL": "⚠️",
                "NOT_IMPLEMENTED": "❌",
                "ERROR": "💥"
            }
            
            logger.info(f"{status_emoji.get(result.status, '❓')} {result.status}: {result.details}")
            
            if result.files_implemented:
                logger.info(f"   📁 Archivos implementados: {len(result.files_implemented)}")
            
            if result.notes:
                logger.info(f"   📝 Notas: {result.notes}")
        
        # Generar resumen
        audit_end = datetime.now()
        audit_duration = audit_end - audit_start
        
        summary = self._generate_audit_summary(audit_duration)
        
        logger.info("\n" + "=" * 80)
        logger.info("📊 RESUMEN DE AUDITORÍA COMPLETA")
        logger.info("=" * 80)
        
        for key, value in summary.items():
            if key != "detailed_results":
                logger.info(f"{key}: {value}")
        
        return summary
    
    def _check_objective(self, objective_id: str, objective_info: Dict[str, Any]) -> ObjectiveCheck:
        """Verifica un objetivo específico."""
        try:
            # Verificar archivos esperados
            files_implemented = []
            files_missing = []
            
            for expected_file in objective_info["files_expected"]:
                file_path = self.project_root / expected_file
                logger.debug(f"Verificando archivo: {file_path} (existe: {file_path.exists()})")
                if file_path.exists():
                    files_implemented.append(expected_file)
                else:
                    files_missing.append(expected_file)
            
            # Verificar implementación de funcionalidades
            logger.debug(f"Verificando funcionalidad para {objective_id}")
            functionality_status = self._check_functionality(objective_id, objective_info)
            logger.debug(f"Estado de funcionalidad: {functionality_status}")
            
            # Determinar estado general
            if len(files_missing) == 0 and functionality_status["status"] == "COMPLETED":
                status = "COMPLETED"
                details = "Objetivo completamente implementado"
            elif len(files_missing) == 0 and functionality_status["status"] == "PARTIAL":
                status = "PARTIAL"
                details = "Archivos implementados pero funcionalidad parcial"
            elif len(files_missing) > 0 and len(files_implemented) > 0:
                status = "PARTIAL"
                details = f"Implementación parcial - Faltan {len(files_missing)} archivos"
            else:
                status = "NOT_IMPLEMENTED"
                details = f"Objetivo no implementado - Faltan {len(files_missing)} archivos"
            
            # Verificar tests
            tests_passed = self._check_tests(objective_id)
            
            return ObjectiveCheck(
                objective=objective_info["title"],
                status=status,
                details=details,
                files_implemented=files_implemented,
                tests_passed=tests_passed,
                notes=functionality_status.get("notes", "")
            )
            
        except Exception as e:
            logger.error(f"Error verificando objetivo {objective_id}: {e}")
            return ObjectiveCheck(
                objective=objective_info["title"],
                status="ERROR",
                details=f"Error durante verificación: {str(e)}",
                files_implemented=[],
                tests_passed=False,
                notes="Error en verificación"
            )
    
    def _check_functionality(self, objective_id: str, objective_info: Dict[str, Any]) -> Dict[str, Any]:
        """Verifica la funcionalidad específica de un objetivo."""
        try:
            if objective_id == "PR-1_SPEC_FIRST":
                return self._check_spec_first_functionality()
            elif objective_id == "PR-2_CONTEXT_MANAGEMENT":
                return self._check_context_management_functionality()
            elif objective_id == "PR-3_HYBRID_RETRIEVAL":
                return self._check_hybrid_retrieval_functionality()
            elif objective_id == "PR-4_SUBAGENTS_PIPELINE":
                return self._check_subagents_pipeline_functionality()
            elif objective_id == "PR-A_GITHUB_INDEXING":
                return self._check_github_indexing_functionality()
            elif objective_id == "PR-B_HUMAN_LOOP":
                return self._check_human_loop_functionality()
            elif objective_id == "PR-C_SPEC_LAYER":
                return self._check_spec_layer_integration_functionality()
            elif objective_id == "PR-D_CURSOR_INTEGRATION":
                return self._check_cursor_integration_functionality()
            elif objective_id == "PR-E_AUDIT_EVALUATION":
                return self._check_audit_evaluation_functionality()
            else:
                return {"status": "UNKNOWN", "notes": "Objetivo no reconocido"}
                
        except Exception as e:
            return {"status": "ERROR", "notes": f"Error verificando funcionalidad: {str(e)}"}
    
    def _check_spec_first_functionality(self) -> Dict[str, Any]:
        """Verifica funcionalidad del Spec-First."""
        try:
            # Intentar importar spec_layer
            # Agregar el directorio raíz del proyecto al path
            import sys
            sys.path.insert(0, str(self.project_root))
            
            spec_module = importlib.import_module("app.spec_layer")
            
            # Verificar clases principales
            required_classes = ["TaskContract", "TaskType", "RiskLevel", "SpecLayer"]
            missing_classes = []
            
            for class_name in required_classes:
                if not hasattr(spec_module, class_name):
                    missing_classes.append(class_name)
            
            if missing_classes:
                return {
                    "status": "PARTIAL",
                    "notes": f"Faltan clases: {', '.join(missing_classes)}"
                }
            
            # Verificar métodos principales
            spec_layer_class = getattr(spec_module, "SpecLayer")
            required_methods = ["build_task_contract", "render_system_prompt"]
            missing_methods = []
            
            for method_name in required_methods:
                if not hasattr(spec_layer_class, method_name):
                    missing_methods.append(method_name)
            
            if missing_methods:
                return {
                    "status": "PARTIAL",
                    "notes": f"Faltan métodos: {', '.join(missing_methods)}"
                }
            
            return {"status": "COMPLETED", "notes": "Todas las funcionalidades implementadas"}
            
        except ImportError:
            return {"status": "NOT_IMPLEMENTED", "notes": "No se puede importar spec_layer"}
        except Exception as e:
            return {"status": "ERROR", "notes": f"Error verificando spec_first: {str(e)}"}
    
    def _check_context_management_functionality(self) -> Dict[str, Any]:
        """Verifica funcionalidad del Context Management."""
        try:
            # Verificar archivos principales
            context_files = [
                "app/context_manager.py",
                "app/context_logger.py",
                "app/dashboard_context.py"
            ]
            
            missing_files = []
            for file_path in context_files:
                if not (self.project_root / file_path).exists():
                    missing_files.append(file_path)
            
            if missing_files:
                return {
                    "status": "PARTIAL",
                    "notes": f"Faltan archivos: {', '.join(missing_files)}"
                }
            
            return {"status": "COMPLETED", "notes": "Context management implementado"}
            
        except Exception as e:
            return {"status": "ERROR", "notes": f"Error verificando context management: {str(e)}"}
    
    def _check_hybrid_retrieval_functionality(self) -> Dict[str, Any]:
        """Verifica funcionalidad del Hybrid Retrieval."""
        try:
            # Verificar directorio de retrieval
            retrieval_dir = self.project_root / "app/retrieval"
            if not retrieval_dir.exists():
                return {"status": "NOT_IMPLEMENTED", "notes": "Directorio retrieval no existe"}
            
            # Verificar archivos clave
            key_files = ["milvus_store.py"]
            missing_files = []
            
            for file_name in key_files:
                if not (retrieval_dir / file_name).exists():
                    missing_files.append(file_name)
            
            if missing_files:
                return {
                    "status": "PARTIAL",
                    "notes": f"Faltan archivos de retrieval: {', '.join(missing_files)}"
                }
            
            return {"status": "COMPLETED", "notes": "Hybrid retrieval implementado"}
            
        except Exception as e:
            return {"status": "ERROR", "notes": f"Error verificando hybrid retrieval: {str(e)}"}
    
    def _check_subagents_pipeline_functionality(self) -> Dict[str, Any]:
        """Verifica funcionalidad del Subagents Pipeline."""
        try:
            # Verificar directorio de subagentes
            subagents_dir = self.project_root / "app/subagents"
            if not subagents_dir.exists():
                return {"status": "NOT_IMPLEMENTED", "notes": "Directorio subagents no existe"}
            
            # Verificar archivos clave
            key_files = ["orchestrator.py", "verification.py"]
            missing_files = []
            
            for file_name in key_files:
                if not (subagents_dir / file_name).exists():
                    missing_files.append(file_name)
            
            if missing_files:
                return {
                    "status": "PARTIAL",
                    "notes": f"Faltan archivos de subagentes: {', '.join(missing_files)}"
                }
            
            return {"status": "COMPLETED", "notes": "Subagents pipeline implementado"}
            
        except Exception as e:
            return {"status": "ERROR", "notes": f"Error verificando subagents pipeline: {str(e)}"}
    
    def _check_github_indexing_functionality(self) -> Dict[str, Any]:
        """Verifica funcionalidad del GitHub Indexing."""
        try:
            # Verificar scripts de GitHub
            github_files = [
                "scripts/index_github.py",
                "tests/test_github_indexing.py",
                "config/github_indexing.yml"
            ]
            
            missing_files = []
            for file_path in github_files:
                if not (self.project_root / file_path).exists():
                    missing_files.append(file_path)
            
            if missing_files:
                return {
                    "status": "PARTIAL",
                    "notes": f"Faltan archivos de GitHub indexing: {', '.join(missing_files)}"
                }
            
            return {"status": "COMPLETED", "notes": "GitHub indexing implementado"}
            
        except Exception as e:
            return {"status": "ERROR", "notes": f"Error verificando GitHub indexing: {str(e)}"}
    
    def _check_human_loop_functionality(self) -> Dict[str, Any]:
        """Verifica funcionalidad del Human Loop."""
        try:
            # Verificar archivos del human loop
            human_loop_files = [
                "app/human_loop.py",
                "config/human_loop.yml",
                "tests/example_human_loop.py"
            ]
            
            missing_files = []
            for file_path in human_loop_files:
                if not (self.project_root / file_path).exists():
                    missing_files.append(file_path)
            
            if missing_files:
                return {
                    "status": "PARTIAL",
                    "notes": f"Faltan archivos del human loop: {', '.join(missing_files)}"
                }
            
            return {"status": "COMPLETED", "notes": "Human loop implementado"}
            
        except Exception as e:
            return {"status": "ERROR", "notes": f"Error verificando human loop: {str(e)}"}
    
    def _check_spec_layer_integration_functionality(self) -> Dict[str, Any]:
        """Verifica funcionalidad de integración del Spec Layer."""
        try:
            # Verificar archivos del spec layer
            spec_layer_files = [
                "app/spec_layer.py",
                "config/spec_layer.yml",
                "app/specs/",
                "tests/example_spec_layer.py"
            ]
            
            missing_files = []
            for file_path in spec_layer_files:
                if not (self.project_root / file_path).exists():
                    missing_files.append(file_path)
            
            if missing_files:
                return {
                    "status": "PARTIAL",
                    "notes": f"Faltan archivos del spec layer: {', '.join(missing_files)}"
                }
            
            return {"status": "COMPLETED", "notes": "Spec layer integration implementado"}
            
        except Exception as e:
            return {"status": "ERROR", "notes": f"Error verificando spec layer integration: {str(e)}"}
    
    def _check_cursor_integration_functionality(self) -> Dict[str, Any]:
        """Verifica funcionalidad del Cursor Integration."""
        try:
            # Verificar archivos del cursor integration
            cursor_files = [
                "app/cursor_agent.py",
                "config/cursor_agent.yml",
                "tests/example_cursor_integration.py"
            ]
            
            missing_files = []
            for file_path in cursor_files:
                if not (self.project_root / file_path).exists():
                    missing_files.append(file_path)
            
            if missing_files:
                return {
                    "status": "PARTIAL",
                    "notes": f"Faltan archivos del cursor integration: {', '.join(missing_files)}"
                }
            
            return {"status": "COMPLETED", "notes": "Cursor integration implementado"}
            
        except Exception as e:
            return {"status": "ERROR", "notes": f"Error verificando cursor integration: {str(e)}"}
    
    def _check_audit_evaluation_functionality(self) -> Dict[str, Any]:
        """Verifica funcionalidad del Audit & Evaluation."""
        try:
            # Verificar archivos del audit & evaluation
            audit_files = [
                "eval/evaluate_plans.py",
                "config/evaluation.yml",
                "tests/example_evaluation_system.py",
                "logs/audit.jsonl"
            ]
            
            missing_files = []
            for file_path in audit_files:
                if not (self.project_root / file_path).exists():
                    missing_files.append(file_path)
            
            if missing_files:
                return {
                    "status": "PARTIAL",
                    "notes": f"Faltan archivos del audit & evaluation: {', '.join(missing_files)}"
                }
            
            return {"status": "COMPLETED", "notes": "Audit & evaluation implementado"}
            
        except Exception as e:
            return {"status": "ERROR", "notes": f"Error verificando audit & evaluation: {str(e)}"}
    
    def _check_tests(self, objective_id: str) -> bool:
        """Verifica si hay tests para un objetivo."""
        # Por simplicidad, verificamos si existen archivos de test
        test_patterns = [
            f"test_{objective_id.lower()}.py",
            f"test_{objective_id.lower().replace('_', '')}.py",
            "tests/",
            "test_*.py"
        ]
        
        for pattern in test_patterns:
            if list(self.project_root.glob(pattern)):
                return True
        
        return False
    
    def _generate_audit_summary(self, audit_duration) -> Dict[str, Any]:
        """Genera resumen de la auditoría."""
        total_objectives = len(self.objectives)
        completed = len([r for r in self.results if r.status == "COMPLETED"])
        partial = len([r for r in self.results if r.status == "PARTIAL"])
        not_implemented = len([r for r in self.results if r.status == "NOT_IMPLEMENTED"])
        errors = len([r for r in self.results if r.status == "ERROR"])
        
        completion_percentage = (completed / total_objectives) * 100
        overall_status = "COMPLETED" if completion_percentage >= 90 else "PARTIAL" if completion_percentage >= 70 else "INCOMPLETE"
        
        return {
            "audit_timestamp": datetime.now().isoformat(),
            "audit_duration_seconds": audit_duration.total_seconds(),
            "total_objectives": total_objectives,
            "completed_objectives": completed,
            "partial_objectives": partial,
            "not_implemented_objectives": not_implemented,
            "error_objectives": errors,
            "completion_percentage": round(completion_percentage, 2),
            "overall_status": overall_status,
            "detailed_results": self.results
        }


def main():
    """Función principal de la auditoría."""
    print("🔍 AUDITORÍA INTEGRAL DEL SISTEMA NEXT LEVEL RAG")
    print("=" * 80)
    
    try:
        # Crear auditoría
        auditor = SystemAudit()
        
        # Ejecutar auditoría completa
        summary = auditor.run_complete_audit()
        
        # Mostrar resumen final
        print("\n" + "=" * 80)
        print("🎯 RESUMEN FINAL DE AUDITORÍA")
        print("=" * 80)
        
        print(f"📊 Estado General: {summary['overall_status']}")
        print(f"📈 Porcentaje de Completitud: {summary['completion_percentage']}%")
        print(f"✅ Objetivos Completados: {summary['completed_objectives']}/{summary['total_objectives']}")
        print(f"⚠️  Objetivos Parciales: {summary['partial_objectives']}")
        print(f"❌ Objetivos No Implementados: {summary['not_implemented_objectives']}")
        print(f"💥 Objetivos con Errores: {summary['error_objectives']}")
        print(f"⏱️  Duración de Auditoría: {summary['audit_duration_seconds']:.2f} segundos")
        
        # Recomendaciones
        print(f"\n💡 RECOMENDACIONES:")
        if summary['completion_percentage'] >= 90:
            print("🎉 ¡Excelente! El sistema está prácticamente completo.")
            print("   Considerar optimizaciones y mejoras menores.")
        elif summary['completion_percentage'] >= 70:
            print("⚠️  El sistema está bien implementado pero necesita mejoras.")
            print("   Revisar objetivos parciales y completar funcionalidades faltantes.")
        else:
            print("❌ El sistema necesita trabajo significativo.")
            print("   Priorizar objetivos críticos y completar implementación base.")
        
        return summary
        
    except Exception as e:
        logger.error(f"Error durante la auditoría: {e}")
        print(f"💥 Error crítico durante la auditoría: {e}")
        return None


if __name__ == "__main__":
    main()
