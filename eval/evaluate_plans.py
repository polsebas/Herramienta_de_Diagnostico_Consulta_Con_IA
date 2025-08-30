"""
Sistema de Evaluación de Planes - Golden Set y Métricas de Calidad

Este módulo implementa el sistema de evaluación continua que utiliza un golden set
de 20 preguntas para medir la precisión y calidad de los planes generados por el sistema.
"""

import asyncio
import json
import logging
import statistics
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from app.spec_layer import build_task_contract, validate_contract_compliance
from app.cursor_agent import CursorAgent, TaskType
from app.context_manager import ContextManager
from app.human_loop import HumanLoopManager

logger = logging.getLogger(__name__)


class EvaluationMetric(Enum):
    """Métricas de evaluación disponibles."""
    ACCURACY = "accuracy"
    COMPLETENESS = "completeness"
    RELEVANCE = "relevance"
    ACTIONABILITY = "actionability"
    SECURITY = "security"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"
    TESTABILITY = "testability"
    DOCUMENTATION = "documentation"
    COMPLIANCE = "compliance"


class QualityLevel(Enum):
    """Niveles de calidad."""
    EXCELLENT = "excellent"  # 90-100%
    GOOD = "good"           # 80-89%
    ACCEPTABLE = "acceptable" # 70-79%
    POOR = "poor"           # 60-69%
    UNACCEPTABLE = "unacceptable" # <60%


@dataclass
class GoldenQuestion:
    """Pregunta del golden set para evaluación."""
    id: str
    question: str
    expected_type: str
    expected_components: List[str]
    difficulty: str  # easy, medium, hard
    domain: str     # auth, security, performance, etc.
    expected_risk_level: str
    expected_approval_required: bool
    expected_artifacts: List[str]
    baseline_score: float  # Score histórico promedio


@dataclass
class EvaluationResult:
    """Resultado de una evaluación individual."""
    question_id: str
    timestamp: datetime
    agent_version: str
    contract_generated: bool
    contract_quality: float
    task_executed: bool
    task_success: bool
    execution_time: float
    artifacts_generated: List[str]
    human_approval_required: bool
    human_approval_granted: Optional[bool]
    quality_scores: Dict[str, float]
    overall_score: float
    quality_level: QualityLevel
    feedback: List[str]
    metadata: Dict[str, Any]


@dataclass
class EvaluationSummary:
    """Resumen de evaluación del sistema."""
    total_questions: int
    questions_evaluated: int
    average_score: float
    quality_distribution: Dict[QualityLevel, int]
    domain_performance: Dict[str, float]
    difficulty_performance: Dict[str, float]
    improvement_trend: float
    recommendations: List[str]
    generated_at: datetime


class PlanEvaluator:
    """
    Evaluador de planes que utiliza el golden set para medir la calidad del sistema.
    """
    
    def __init__(self, 
                 context_manager: ContextManager,
                 human_loop_manager: Optional[HumanLoopManager] = None,
                 config_path: str = "config/evaluation.yml"):
        """
        Inicializa el evaluador de planes.
        
        Args:
            context_manager: Gestor de contexto
            human_loop_manager: Gestor de human-in-the-loop
            config_path: Ruta al archivo de configuración
        """
        self.context_manager = context_manager
        self.human_loop_manager = human_loop_manager
        self.config = self._load_config(config_path)
        self.golden_set = self._load_golden_set()
        self.evaluation_history: List[EvaluationResult] = []
        
        logger.info("Plan Evaluator inicializado")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Carga configuración desde archivo YAML."""
        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except (FileNotFoundError, ImportError):
            logger.warning(f"Archivo de configuración {config_path} no encontrado, usando configuración por defecto")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Configuración por defecto del evaluador."""
        return {
            'evaluation_thresholds': {
                'excellent': 0.9,
                'good': 0.8,
                'acceptable': 0.7,
                'poor': 0.6
            },
            'quality_weights': {
                'accuracy': 0.25,
                'completeness': 0.20,
                'relevance': 0.15,
                'actionability': 0.15,
                'security': 0.10,
                'performance': 0.05,
                'maintainability': 0.05,
                'testability': 0.03,
                'documentation': 0.02
            },
            'evaluation_timeout_minutes': 10,
            'max_parallel_evaluations': 3,
            'auto_retry_failed': True,
            'export_results': True
        }
    
    def _load_golden_set(self) -> List[GoldenQuestion]:
        """Carga el golden set de preguntas para evaluación."""
        golden_set = [
            # Preguntas de Autenticación y Autorización
            GoldenQuestion(
                id="auth-001",
                question="¿Cómo implementar autenticación JWT segura?",
                expected_type="procedural",
                expected_components=["JWT implementation", "security best practices", "error handling"],
                difficulty="medium",
                domain="auth",
                expected_risk_level="medium",
                expected_approval_required=False,
                expected_artifacts=["jwt_auth.py", "test_jwt_auth.py", "jwt_docs.md"],
                baseline_score=0.85
            ),
            GoldenQuestion(
                id="auth-002",
                question="Implementar sistema de roles y permisos",
                expected_type="code",
                expected_components=["role management", "permission system", "access control"],
                difficulty="hard",
                domain="auth",
                expected_risk_level="high",
                expected_approval_required=True,
                expected_artifacts=["roles.py", "permissions.py", "tests/", "docs/"],
                baseline_score=0.78
            ),
            
            # Preguntas de Seguridad
            GoldenQuestion(
                id="security-001",
                question="Configurar firewall y reglas de seguridad",
                expected_type="procedural",
                expected_components=["firewall rules", "security policies", "monitoring"],
                difficulty="hard",
                domain="security",
                expected_risk_level="critical",
                expected_approval_required=True,
                expected_artifacts=["firewall.yml", "security_policies.md", "monitoring.py"],
                baseline_score=0.72
            ),
            GoldenQuestion(
                id="security-002",
                question="Implementar validación de entrada segura",
                expected_type="code",
                expected_components=["input validation", "sanitization", "security checks"],
                difficulty="medium",
                domain="security",
                expected_risk_level="medium",
                expected_approval_required=False,
                expected_artifacts=["validation.py", "test_validation.py", "security_guide.md"],
                baseline_score=0.88
            ),
            
            # Preguntas de Performance
            GoldenQuestion(
                id="performance-001",
                question="Optimizar consultas de base de datos",
                expected_type="analysis",
                expected_components=["query analysis", "indexing", "optimization"],
                difficulty="medium",
                domain="performance",
                expected_risk_level="low",
                expected_approval_required=False,
                expected_artifacts=["query_analysis.md", "optimization_plan.md", "benchmarks.py"],
                baseline_score=0.82
            ),
            GoldenQuestion(
                id="performance-002",
                question="Implementar sistema de cache",
                expected_type="code",
                expected_components=["cache strategy", "invalidation", "monitoring"],
                difficulty="medium",
                domain="performance",
                expected_risk_level="low",
                expected_approval_required=False,
                expected_artifacts=["cache.py", "cache_config.yml", "test_cache.py"],
                baseline_score=0.85
            ),
            
            # Preguntas de Testing
            GoldenQuestion(
                id="testing-001",
                question="Generar tests unitarios para función de validación",
                expected_type="test",
                expected_components=["unit tests", "test coverage", "edge cases"],
                difficulty="easy",
                domain="testing",
                expected_risk_level="low",
                expected_approval_required=False,
                expected_artifacts=["test_validation.py", "coverage_report.md"],
                baseline_score=0.90
            ),
            GoldenQuestion(
                id="testing-002",
                question="Implementar tests de integración",
                expected_type="test",
                expected_components=["integration tests", "test data", "mocking"],
                difficulty="medium",
                domain="testing",
                expected_risk_level="low",
                expected_approval_required=False,
                expected_artifacts=["integration_tests.py", "test_data.yml", "mocks.py"],
                baseline_score=0.83
            ),
            
            # Preguntas de Documentación
            GoldenQuestion(
                id="docs-001",
                question="Generar documentación técnica para API",
                expected_type="documentation",
                expected_components=["API docs", "examples", "usage guide"],
                difficulty="medium",
                domain="documentation",
                expected_risk_level="low",
                expected_approval_required=False,
                expected_artifacts=["api_docs.md", "examples.py", "usage_guide.md"],
                baseline_score=0.87
            ),
            GoldenQuestion(
                id="docs-002",
                question="Crear README completo del proyecto",
                expected_type="documentation",
                expected_components=["overview", "installation", "usage", "contributing"],
                difficulty="easy",
                domain="documentation",
                expected_risk_level="low",
                expected_approval_required=False,
                expected_artifacts=["README.md", "CONTRIBUTING.md", "CHANGELOG.md"],
                baseline_score=0.92
            ),
            
            # Preguntas de DevOps
            GoldenQuestion(
                id="devops-001",
                question="Configurar pipeline CI/CD",
                expected_type="procedural",
                expected_components=["CI/CD setup", "testing", "deployment"],
                difficulty="hard",
                domain="devops",
                expected_risk_level="high",
                expected_approval_required=True,
                expected_artifacts=[".github/workflows/", "docker-compose.yml", "deploy.sh"],
                baseline_score=0.75
            ),
            GoldenQuestion(
                id="devops-002",
                question="Implementar logging centralizado",
                expected_type="code",
                expected_components=["logging system", "log aggregation", "monitoring"],
                difficulty="medium",
                domain="devops",
                expected_risk_level="low",
                expected_approval_required=False,
                expected_artifacts=["logging.py", "log_config.yml", "monitoring.py"],
                baseline_score=0.80
            ),
            
            # Preguntas de Refactoring
            GoldenQuestion(
                id="refactor-001",
                question="Refactorizar función compleja",
                expected_type="refactor",
                expected_components=["code analysis", "refactoring", "testing"],
                difficulty="medium",
                domain="refactoring",
                expected_risk_level="medium",
                expected_approval_required=False,
                expected_artifacts=["refactored_code.py", "test_refactored.py", "refactor_notes.md"],
                baseline_score=0.78
            ),
            GoldenQuestion(
                id="refactor-002",
                question="Extraer clase común",
                expected_type="refactor",
                expected_components=["class extraction", "inheritance", "testing"],
                difficulty="medium",
                domain="refactoring",
                expected_risk_level="low",
                expected_approval_required=False,
                expected_artifacts=["base_class.py", "derived_classes.py", "tests/"],
                baseline_score=0.82
            ),
            
            # Preguntas de Análisis
            GoldenQuestion(
                id="analysis-001",
                question="Analizar performance de endpoint",
                expected_type="analysis",
                expected_components=["performance analysis", "bottlenecks", "recommendations"],
                difficulty="medium",
                domain="analysis",
                expected_risk_level="low",
                expected_approval_required=False,
                expected_artifacts=["performance_report.md", "benchmarks.py", "optimization_plan.md"],
                baseline_score=0.85
            ),
            GoldenQuestion(
                id="analysis-002",
                question="Revisar código para vulnerabilidades",
                expected_type="code_review",
                expected_components=["security review", "vulnerability scan", "fixes"],
                difficulty="hard",
                domain="security",
                expected_risk_level="high",
                expected_approval_required=True,
                expected_artifacts=["security_report.md", "vulnerability_fixes.py", "security_tests.py"],
                baseline_score=0.70
            ),
            
            # Preguntas de Migración
            GoldenQuestion(
                id="migration-001",
                question="Migrar base de datos a nueva versión",
                expected_type="procedural",
                expected_components=["migration plan", "backup strategy", "rollback plan"],
                difficulty="hard",
                domain="migration",
                expected_risk_level="critical",
                expected_approval_required=True,
                expected_artifacts=["migration_plan.md", "migration_scripts.py", "rollback_plan.md"],
                baseline_score=0.68
            ),
            GoldenQuestion(
                id="migration-002",
                question="Actualizar dependencias del proyecto",
                expected_type="procedural",
                expected_components=["dependency analysis", "update plan", "testing"],
                difficulty="medium",
                domain="migration",
                expected_risk_level="medium",
                expected_approval_required=False,
                expected_artifacts=["dependency_report.md", "update_plan.md", "test_results.md"],
                baseline_score=0.80
            ),
            
            # Preguntas de Monitoreo
            GoldenQuestion(
                id="monitoring-001",
                question="Implementar sistema de alertas",
                expected_type="code",
                expected_components=["alert system", "thresholds", "notifications"],
                difficulty="medium",
                domain="monitoring",
                expected_risk_level="low",
                expected_approval_required=False,
                expected_artifacts=["alerts.py", "alert_config.yml", "test_alerts.py"],
                baseline_score=0.83
            ),
            GoldenQuestion(
                id="monitoring-002",
                question="Configurar dashboard de métricas",
                expected_type="procedural",
                expected_components=["metrics collection", "visualization", "dashboard"],
                difficulty="medium",
                domain="monitoring",
                expected_risk_level="low",
                expected_approval_required=False,
                expected_artifacts=["metrics.py", "dashboard_config.yml", "dashboard.py"],
                baseline_score=0.78
            )
        ]
        
        logger.info(f"Golden set cargado con {len(golden_set)} preguntas")
        return golden_set
    
    async def evaluate_question(self, question: GoldenQuestion) -> EvaluationResult:
        """
        Evalúa una pregunta del golden set.
        
        Args:
            question: Pregunta del golden set a evaluar
            
        Returns:
            EvaluationResult con los resultados de la evaluación
        """
        start_time = datetime.utcnow()
        
        try:
            # 1. Generar contrato
            contract = await build_task_contract(
                query=question.question,
                user_role="developer",
                risk_level=None  # Se infiere automáticamente
            )
            
            # 2. Validar contrato
            contract_validation = await validate_contract_compliance(
                response=f"Contrato generado para: {question.question}",
                contract=contract
            )
            
            # 3. Ejecutar tarea si es posible
            task_executed = False
            task_success = False
            execution_time = 0.0
            artifacts_generated = []
            
            if contract.risk_level.value != "critical":
                try:
                    # Crear Cursor Agent para ejecutar tarea
                    cursor_agent = CursorAgent(
                        context_manager=self.context_manager,
                        human_loop_manager=self.human_loop_manager,
                        workspace_path="."
                    )
                    
                    # Enviar tarea
                    task_id = await cursor_agent.submit_task(
                        task_type=self._map_question_to_task_type(question),
                        contract=contract,
                        priority=5
                    )
                    
                    # Esperar completación
                    task = await self._wait_for_task_completion(cursor_agent, task_id)
                    
                    if task and task.status.value == "completed":
                        task_executed = True
                        task_success = True
                        execution_time = (task.completed_at - task.started_at).total_seconds()
                        artifacts_generated = task.artifacts or []
                    
                except Exception as e:
                    logger.warning(f"Error ejecutando tarea para pregunta {question.id}: {e}")
            
            # 4. Calcular scores de calidad
            quality_scores = self._calculate_quality_scores(
                question, contract, contract_validation, task_success, artifacts_generated
            )
            
            # 5. Calcular score general
            overall_score = self._calculate_overall_score(quality_scores)
            quality_level = self._determine_quality_level(overall_score)
            
            # 6. Generar feedback
            feedback = self._generate_feedback(question, quality_scores, overall_score)
            
            # 7. Crear resultado de evaluación
            result = EvaluationResult(
                question_id=question.id,
                timestamp=datetime.utcnow(),
                agent_version="v1.0",
                contract_generated=True,
                contract_quality=contract_validation.score if contract_validation else 0.0,
                task_executed=task_executed,
                task_success=task_success,
                execution_time=execution_time,
                artifacts_generated=artifacts_generated,
                human_approval_required=contract.human_approval_required,
                human_approval_granted=None,  # No implementado en esta versión
                quality_scores=quality_scores,
                overall_score=overall_score,
                quality_level=quality_level,
                feedback=feedback,
                metadata={
                    'expected_type': question.expected_type,
                    'difficulty': question.difficulty,
                    'domain': question.domain,
                    'baseline_score': question.baseline_score
                }
            )
            
            # 8. Almacenar en historial
            self.evaluation_history.append(result)
            
            logger.info(f"Evaluación completada para pregunta {question.id}: {overall_score:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Error evaluando pregunta {question.id}: {e}")
            
            # Crear resultado de error
            return EvaluationResult(
                question_id=question.id,
                timestamp=datetime.utcnow(),
                agent_version="v1.0",
                contract_generated=False,
                contract_quality=0.0,
                task_executed=False,
                task_success=False,
                execution_time=0.0,
                artifacts_generated=[],
                human_approval_required=False,
                human_approval_granted=None,
                quality_scores={},
                overall_score=0.0,
                quality_level=QualityLevel.UNACCEPTABLE,
                feedback=[f"Error en evaluación: {str(e)}"],
                metadata={'error': str(e)}
            )
    
    def _map_question_to_task_type(self, question: GoldenQuestion) -> TaskType:
        """Mapea el tipo de pregunta al tipo de tarea del Cursor Agent."""
        mapping = {
            "procedural": TaskType.DRAFT_PR,
            "code": TaskType.DRAFT_PR,
            "test": TaskType.GENERATE_TESTS,
            "documentation": TaskType.GENERATE_DOCS,
            "refactor": TaskType.REFACTOR,
            "code_review": TaskType.CODE_REVIEW,
            "analysis": TaskType.DRAFT_PR
        }
        return mapping.get(question.expected_type, TaskType.DRAFT_PR)
    
    async def _wait_for_task_completion(self, agent: CursorAgent, task_id: str, 
                                       timeout_seconds: int = 300) -> Optional[Any]:
        """Espera a que una tarea se complete."""
        start_time = datetime.utcnow()
        
        while (datetime.utcnow() - start_time).total_seconds() < timeout_seconds:
            task = agent.get_task_status(task_id)
            
            if task and task.status.value in ["completed", "failed", "cancelled"]:
                return task
            
            await asyncio.sleep(2)
        
        return None
    
    def _calculate_quality_scores(self, question: GoldenQuestion, contract: Any, 
                                 validation: Any, task_success: bool, 
                                 artifacts: List[str]) -> Dict[str, float]:
        """Calcula scores de calidad para diferentes aspectos."""
        scores = {}
        
        # Accuracy - Precisión del tipo de tarea detectado
        expected_type_match = 1.0 if contract.task_type.value == question.expected_type else 0.5
        scores['accuracy'] = expected_type_match
        
        # Completeness - Completitud de componentes esperados
        expected_components = set(question.expected_components)
        actual_components = set(contract.musts) if hasattr(contract, 'musts') else set()
        completeness = len(expected_components & actual_components) / len(expected_components) if expected_components else 1.0
        scores['completeness'] = completeness
        
        # Relevance - Relevancia del contrato generado
        scores['relevance'] = validation.score if validation else 0.8
        
        # Actionability - Capacidad de acción del plan
        actionability = 1.0 if task_success else 0.6
        scores['actionability'] = actionability
        
        # Security - Consideraciones de seguridad
        security_score = 1.0
        if question.domain == "security":
            security_score = 0.9 if contract.risk_level.value in ["high", "critical"] else 0.7
        scores['security'] = security_score
        
        # Performance - Consideraciones de performance
        scores['performance'] = 0.8  # Valor por defecto
        
        # Maintainability - Mantenibilidad del código
        maintainability = 0.9 if len(artifacts) > 1 else 0.7
        scores['maintainability'] = maintainability
        
        # Testability - Capacidad de testing
        testability = 1.0 if any("test" in artifact.lower() for artifact in artifacts) else 0.6
        scores['testability'] = testability
        
        # Documentation - Calidad de documentación
        documentation = 1.0 if any("doc" in artifact.lower() or "md" in artifact.lower() for artifact in artifacts) else 0.5
        scores['documentation'] = documentation
        
        return scores
    
    def _calculate_overall_score(self, quality_scores: Dict[str, float]) -> float:
        """Calcula el score general ponderado."""
        weights = self.config['quality_weights']
        total_score = 0.0
        total_weight = 0.0
        
        for metric, weight in weights.items():
            if metric in quality_scores:
                total_score += quality_scores[metric] * weight
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _determine_quality_level(self, score: float) -> QualityLevel:
        """Determina el nivel de calidad basado en el score."""
        thresholds = self.config['evaluation_thresholds']
        
        if score >= thresholds['excellent']:
            return QualityLevel.EXCELLENT
        elif score >= thresholds['good']:
            return QualityLevel.GOOD
        elif score >= thresholds['acceptable']:
            return QualityLevel.ACCEPTABLE
        elif score >= thresholds['poor']:
            return QualityLevel.POOR
        else:
            return QualityLevel.UNACCEPTABLE
    
    def _generate_feedback(self, question: GoldenQuestion, quality_scores: Dict[str, float], 
                          overall_score: float) -> List[str]:
        """Genera feedback basado en los scores de calidad."""
        feedback = []
        
        # Comparar con baseline
        if overall_score < question.baseline_score:
            feedback.append(f"Score ({overall_score:.2f}) por debajo del baseline ({question.baseline_score:.2f})")
        
        # Feedback específico por métrica
        for metric, score in quality_scores.items():
            if score < 0.7:
                feedback.append(f"Mejorar {metric}: score actual {score:.2f}")
        
        # Feedback general
        if overall_score >= 0.9:
            feedback.append("Excelente rendimiento general")
        elif overall_score >= 0.8:
            feedback.append("Buen rendimiento, algunas áreas de mejora")
        elif overall_score >= 0.7:
            feedback.append("Rendimiento aceptable, necesita mejoras")
        else:
            feedback.append("Rendimiento pobre, requiere atención inmediata")
        
        return feedback
    
    async def evaluate_golden_set(self, max_parallel: int = 3) -> EvaluationSummary:
        """
        Evalúa todo el golden set de preguntas.
        
        Args:
            max_parallel: Máximo número de evaluaciones en paralelo
            
        Returns:
            EvaluationSummary con resumen de la evaluación
        """
        logger.info(f"Iniciando evaluación del golden set ({len(self.golden_set)} preguntas)")
        
        # Evaluar preguntas en lotes para controlar concurrencia
        results = []
        for i in range(0, len(self.golden_set), max_parallel):
            batch = self.golden_set[i:i + max_parallel]
            batch_results = await asyncio.gather(*[
                self.evaluate_question(question) for question in batch
            ])
            results.extend(batch_results)
        
        # Generar resumen
        summary = self._generate_evaluation_summary(results)
        
        logger.info(f"Evaluación del golden set completada. Score promedio: {summary.average_score:.2f}")
        return summary
    
    def _generate_evaluation_summary(self, results: List[EvaluationResult]) -> EvaluationSummary:
        """Genera un resumen de la evaluación."""
        if not results:
            return EvaluationSummary(
                total_questions=len(self.golden_set),
                questions_evaluated=0,
                average_score=0.0,
                quality_distribution={},
                domain_performance={},
                difficulty_performance={},
                improvement_trend=0.0,
                recommendations=[],
                generated_at=datetime.utcnow()
            )
        
        # Estadísticas básicas
        total_questions = len(self.golden_set)
        questions_evaluated = len(results)
        average_score = statistics.mean([r.overall_score for r in results])
        
        # Distribución de calidad
        quality_distribution = {}
        for level in QualityLevel:
            count = len([r for r in results if r.quality_level == level])
            quality_distribution[level.value] = count
        
        # Performance por dominio
        domain_performance = {}
        for result in results:
            domain = result.metadata.get('domain', 'unknown')
            if domain not in domain_performance:
                domain_performance[domain] = []
            domain_performance[domain].append(result.overall_score)
        
        for domain in domain_performance:
            domain_performance[domain] = statistics.mean(domain_performance[domain])
        
        # Performance por dificultad
        difficulty_performance = {}
        for result in results:
            difficulty = result.metadata.get('difficulty', 'unknown')
            if difficulty not in difficulty_performance:
                difficulty_performance[difficulty] = []
            difficulty_performance[difficulty].append(result.overall_score)
        
        for difficulty in difficulty_performance:
            difficulty_performance[difficulty] = statistics.mean(difficulty_performance[difficulty])
        
        # Tendencia de mejora (comparar con baseline)
        baseline_scores = [q.baseline_score for q in self.golden_set[:len(results)]]
        improvement_trend = average_score - statistics.mean(baseline_scores) if baseline_scores else 0.0
        
        # Recomendaciones
        recommendations = self._generate_recommendations(results, domain_performance, difficulty_performance)
        
        return EvaluationSummary(
            total_questions=total_questions,
            questions_evaluated=questions_evaluated,
            average_score=average_score,
            quality_distribution=quality_distribution,
            domain_performance=domain_performance,
            difficulty_performance=difficulty_performance,
            improvement_trend=improvement_trend,
            recommendations=recommendations,
            generated_at=datetime.utcnow()
        )
    
    def _generate_recommendations(self, results: List[EvaluationResult], 
                                 domain_performance: Dict[str, float],
                                 difficulty_performance: Dict[str, float]) -> List[str]:
        """Genera recomendaciones basadas en los resultados."""
        recommendations = []
        
        # Identificar dominios con bajo rendimiento
        for domain, score in domain_performance.items():
            if score < 0.8:
                recommendations.append(f"Mejorar rendimiento en dominio '{domain}' (score: {score:.2f})")
        
        # Identificar niveles de dificultad problemáticos
        for difficulty, score in difficulty_performance.items():
            if score < 0.75:
                recommendations.append(f"Mejorar rendimiento en preguntas '{difficulty}' (score: {score:.2f})")
        
        # Recomendaciones generales
        if len([r for r in results if r.quality_level == QualityLevel.UNACCEPTABLE]) > 0:
            recommendations.append("Revisar preguntas con rendimiento inaceptable")
        
        if len([r for r in results if r.task_success]) < len(results) * 0.8:
            recommendations.append("Mejorar tasa de éxito en ejecución de tareas")
        
        return recommendations
    
    def export_results(self, output_dir: str = "eval/results"):
        """Exporta los resultados de evaluación."""
        if not self.evaluation_history:
            logger.warning("No hay resultados de evaluación para exportar")
            return
        
        # Crear directorio de salida
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Exportar resultados como JSON
        results_file = output_path / f"evaluation_results_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump([asdict(result) for result in self.evaluation_history], f, indent=2, default=str)
        
        # Exportar resumen como CSV
        summary_file = output_path / f"evaluation_summary_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        df = pd.DataFrame([asdict(result) for result in self.evaluation_history])
        df.to_csv(summary_file, index=False)
        
        # Generar gráficos
        self._generate_evaluation_charts(output_path)
        
        logger.info(f"Resultados exportados a {output_path}")
    
    def _generate_evaluation_charts(self, output_path: Path):
        """Genera gráficos de evaluación."""
        if not self.evaluation_history:
            return
        
        # Configurar estilo
        plt.style.use('seaborn-v0_8')
        
        # 1. Distribución de calidad
        quality_counts = {}
        for result in self.evaluation_history:
            level = result.quality_level.value
            quality_counts[level] = quality_counts.get(level, 0) + 1
        
        plt.figure(figsize=(10, 6))
        plt.pie(quality_counts.values(), labels=quality_counts.keys(), autopct='%1.1f%%')
        plt.title('Distribución de Calidad')
        plt.savefig(output_path / 'quality_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Performance por dominio
        domain_scores = {}
        for result in self.evaluation_history:
            domain = result.metadata.get('domain', 'unknown')
            if domain not in domain_scores:
                domain_scores[domain] = []
            domain_scores[domain].append(result.overall_score)
        
        domains = list(domain_scores.keys())
        avg_scores = [statistics.mean(scores) for scores in domain_scores.values()]
        
        plt.figure(figsize=(12, 6))
        plt.bar(domains, avg_scores)
        plt.title('Performance por Dominio')
        plt.ylabel('Score Promedio')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(output_path / 'domain_performance.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. Performance por dificultad
        difficulty_scores = {}
        for result in self.evaluation_history:
            difficulty = result.metadata.get('difficulty', 'unknown')
            if difficulty not in difficulty_scores:
                difficulty_scores[difficulty] = []
            difficulty_scores[difficulty].append(result.overall_score)
        
        difficulties = list(difficulty_scores.keys())
        avg_scores = [statistics.mean(scores) for scores in difficulty_scores.values()]
        
        plt.figure(figsize=(10, 6))
        plt.bar(difficulties, avg_scores)
        plt.title('Performance por Dificultad')
        plt.ylabel('Score Promedio')
        plt.tight_layout()
        plt.savefig(output_path / 'difficulty_performance.png', dpi=300, bbox_inches='tight')
        plt.close()


# Funciones de conveniencia
async def evaluate_system_quality(context_manager: ContextManager,
                                 human_loop_manager: Optional[HumanLoopManager] = None,
                                 max_parallel: int = 3) -> EvaluationSummary:
    """
    Función de conveniencia para evaluar la calidad del sistema.
    
    Args:
        context_manager: Gestor de contexto
        human_loop_manager: Gestor de human-in-the-loop
        max_parallel: Máximo evaluaciones en paralelo
        
    Returns:
        Resumen de la evaluación
    """
    evaluator = PlanEvaluator(context_manager, human_loop_manager)
    return await evaluator.evaluate_golden_set(max_parallel)


def get_evaluation_summary(evaluator: PlanEvaluator) -> EvaluationSummary:
    """
    Función de conveniencia para obtener resumen de evaluación.
    
    Args:
        evaluator: Evaluador de planes
        
    Returns:
        Resumen de la evaluación
    """
    return evaluator._generate_evaluation_summary(evaluator.evaluation_history)
