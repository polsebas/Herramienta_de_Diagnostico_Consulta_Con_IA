"""
Contract Learning System - Sistema de aprendizaje continuo

Este módulo implementa un sistema que aprende de cada ejecución de contrato,
mejora las plantillas y optimiza la generación basándose en feedback del usuario
y resultados de ejecución.
"""

import logging
import json
import pickle
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)


class FeedbackType(Enum):
    """Tipos de feedback del usuario."""
    CONTRACT_QUALITY = "contract_quality"
    TASK_RELEVANCE = "task_relevance"
    COMPLETION_SUCCESS = "completion_success"
    USER_SATISFACTION = "user_satisfaction"
    TEMPLATE_USEFULNESS = "template_usefulness"


class LearningMetric(Enum):
    """Métricas de aprendizaje."""
    ACCURACY_IMPROVEMENT = "accuracy_improvement"
    TEMPLATE_OPTIMIZATION = "template_optimization"
    USER_SATISFACTION = "user_satisfaction"
    PREDICTION_CONFIDENCE = "prediction_confidence"
    ADAPTATION_SUCCESS = "adaptation_success"


@dataclass
class UserFeedback:
    """Feedback del usuario sobre un contrato."""
    contract_id: str
    user_id: str
    feedback_type: FeedbackType
    rating: float  # 1.0 - 5.0
    comments: Optional[str]
    specific_issues: List[str]
    suggestions: List[str]
    timestamp: datetime


@dataclass
class ExecutionResult:
    """Resultado de ejecución de un contrato."""
    contract_id: str
    success: bool
    completion_time: float
    quality_score: float
    user_satisfaction: float
    errors_encountered: List[str]
    metrics_achieved: Dict[str, float]
    final_output_quality: float


@dataclass
class LearningUpdate:
    """Actualización resultado del aprendizaje."""
    templates_updated: List[str]
    models_retrained: bool
    confidence_improvement: float
    performance_delta: Dict[str, float]
    next_optimization_date: datetime
    learning_insights: List[str]


@dataclass
class PatternInsight:
    """Insight de patrón detectado."""
    pattern_type: str
    description: str
    frequency: int
    confidence: float
    suggested_action: str
    impact_estimate: float


class FeedbackStore:
    """Almacén de feedback del usuario."""
    
    def __init__(self, storage_path: str = "data/learning/feedback.jsonl"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
    async def store_feedback(self, feedback: UserFeedback) -> bool:
        """Almacena feedback del usuario."""
        try:
            feedback_data = asdict(feedback)
            feedback_data['timestamp'] = feedback.timestamp.isoformat()
            
            with open(self.storage_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(feedback_data) + '\n')
            
            logger.info(f"Feedback almacenado para contrato {feedback.contract_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error almacenando feedback: {e}")
            return False
    
    async def get_feedback_for_contract(self, contract_id: str) -> List[UserFeedback]:
        """Obtiene feedback para un contrato específico."""
        feedback_list = []
        
        try:
            if not self.storage_path.exists():
                return feedback_list
            
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                for line in f:
                    data = json.loads(line.strip())
                    if data['contract_id'] == contract_id:
                        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
                        data['feedback_type'] = FeedbackType(data['feedback_type'])
                        feedback_list.append(UserFeedback(**data))
        
        except Exception as e:
            logger.error(f"Error leyendo feedback: {e}")
        
        return feedback_list
    
    async def get_recent_feedback(self, days: int = 30) -> List[UserFeedback]:
        """Obtiene feedback reciente."""
        cutoff_date = datetime.now() - timedelta(days=days)
        all_feedback = []
        
        try:
            if not self.storage_path.exists():
                return all_feedback
            
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                for line in f:
                    data = json.loads(line.strip())
                    timestamp = datetime.fromisoformat(data['timestamp'])
                    
                    if timestamp >= cutoff_date:
                        data['timestamp'] = timestamp
                        data['feedback_type'] = FeedbackType(data['feedback_type'])
                        all_feedback.append(UserFeedback(**data))
        
        except Exception as e:
            logger.error(f"Error leyendo feedback reciente: {e}")
        
        return all_feedback


class PatternLearner:
    """Aprendizaje de patrones en feedback y resultados."""
    
    def __init__(self):
        self.pattern_cache = {}
        self.min_pattern_frequency = 3
        
    async def identify_improvement_patterns(self,
                                          feedback_data: List[UserFeedback],
                                          execution_data: List[ExecutionResult]) -> List[PatternInsight]:
        """Identifica patrones de mejora en los datos."""
        patterns = []
        
        # Patrones de feedback
        feedback_patterns = await self._analyze_feedback_patterns(feedback_data)
        patterns.extend(feedback_patterns)
        
        # Patrones de ejecución
        execution_patterns = await self._analyze_execution_patterns(execution_data)
        patterns.extend(execution_patterns)
        
        # Patrones cruzados
        cross_patterns = await self._analyze_cross_patterns(feedback_data, execution_data)
        patterns.extend(cross_patterns)
        
        return patterns
    
    async def _analyze_feedback_patterns(self, feedback_data: List[UserFeedback]) -> List[PatternInsight]:
        """Analiza patrones en feedback del usuario."""
        patterns = []
        
        if not feedback_data:
            return patterns
        
        # Patrón: Ratings bajos consistentes
        low_ratings = [f for f in feedback_data if f.rating < 3.0]
        if len(low_ratings) >= self.min_pattern_frequency:
            # Analizar issues comunes
            common_issues = {}
            for feedback in low_ratings:
                for issue in feedback.specific_issues:
                    common_issues[issue] = common_issues.get(issue, 0) + 1
            
            if common_issues:
                most_common_issue = max(common_issues.items(), key=lambda x: x[1])
                patterns.append(PatternInsight(
                    pattern_type="low_satisfaction",
                    description=f"Ratings bajos frecuentes, issue principal: {most_common_issue[0]}",
                    frequency=len(low_ratings),
                    confidence=min(0.9, len(low_ratings) / len(feedback_data)),
                    suggested_action=f"Mejorar template para abordar: {most_common_issue[0]}",
                    impact_estimate=0.3
                ))
        
        # Patrón: Sugerencias recurrentes
        all_suggestions = []
        for feedback in feedback_data:
            all_suggestions.extend(feedback.suggestions)
        
        if all_suggestions:
            suggestion_counts = {}
            for suggestion in all_suggestions:
                suggestion_counts[suggestion] = suggestion_counts.get(suggestion, 0) + 1
            
            # Sugerencias que aparecen múltiples veces
            frequent_suggestions = {k: v for k, v in suggestion_counts.items() 
                                  if v >= self.min_pattern_frequency}
            
            for suggestion, count in frequent_suggestions.items():
                patterns.append(PatternInsight(
                    pattern_type="recurring_suggestion",
                    description=f"Sugerencia recurrente: {suggestion}",
                    frequency=count,
                    confidence=min(0.8, count / len(feedback_data)),
                    suggested_action=f"Implementar en template: {suggestion}",
                    impact_estimate=0.2
                ))
        
        return patterns
    
    async def _analyze_execution_patterns(self, execution_data: List[ExecutionResult]) -> List[PatternInsight]:
        """Analiza patrones en resultados de ejecución."""
        patterns = []
        
        if not execution_data:
            return patterns
        
        # Patrón: Fallos consistentes
        failures = [e for e in execution_data if not e.success]
        if len(failures) >= self.min_pattern_frequency:
            # Analizar errores comunes
            error_patterns = {}
            for execution in failures:
                for error in execution.errors_encountered:
                    error_patterns[error] = error_patterns.get(error, 0) + 1
            
            if error_patterns:
                most_common_error = max(error_patterns.items(), key=lambda x: x[1])
                patterns.append(PatternInsight(
                    pattern_type="execution_failure",
                    description=f"Fallos recurrentes, error principal: {most_common_error[0]}",
                    frequency=len(failures),
                    confidence=min(0.9, len(failures) / len(execution_data)),
                    suggested_action=f"Ajustar template para prevenir: {most_common_error[0]}",
                    impact_estimate=0.4
                ))
        
        # Patrón: Baja calidad de output
        low_quality = [e for e in execution_data if e.final_output_quality < 0.7]
        if len(low_quality) >= self.min_pattern_frequency:
            avg_quality = np.mean([e.final_output_quality for e in low_quality])
            patterns.append(PatternInsight(
                pattern_type="low_output_quality",
                description=f"Calidad de output consistentemente baja (avg: {avg_quality:.2f})",
                frequency=len(low_quality),
                confidence=0.8,
                suggested_action="Mejorar criterios de calidad en templates",
                impact_estimate=0.3
            ))
        
        return patterns
    
    async def _analyze_cross_patterns(self, feedback_data: List[UserFeedback],
                                    execution_data: List[ExecutionResult]) -> List[PatternInsight]:
        """Analiza patrones cruzados entre feedback y ejecución."""
        patterns = []
        
        # Correlacionar feedback con resultados de ejecución
        if feedback_data and execution_data:
            # Buscar contratos con tanto feedback como resultados
            feedback_by_contract = {f.contract_id: f for f in feedback_data}
            execution_by_contract = {e.contract_id: e for e in execution_data}
            
            common_contracts = set(feedback_by_contract.keys()) & set(execution_by_contract.keys())
            
            if len(common_contracts) >= self.min_pattern_frequency:
                # Analizar correlación entre satisfaction y success
                correlations = []
                for contract_id in common_contracts:
                    feedback = feedback_by_contract[contract_id]
                    execution = execution_by_contract[contract_id]
                    
                    correlations.append({
                        'satisfaction': feedback.rating,
                        'success': 1.0 if execution.success else 0.0,
                        'quality': execution.final_output_quality
                    })
                
                # Detectar patrones de correlación
                avg_satisfaction = np.mean([c['satisfaction'] for c in correlations])
                avg_success = np.mean([c['success'] for c in correlations])
                
                if avg_satisfaction < 3.5 and avg_success < 0.8:
                    patterns.append(PatternInsight(
                        pattern_type="satisfaction_success_correlation",
                        description="Baja satisfacción correlacionada con baja tasa de éxito",
                        frequency=len(common_contracts),
                        confidence=0.7,
                        suggested_action="Revisar criterios de éxito y calidad de templates",
                        impact_estimate=0.5
                    ))
        
        return patterns


class TemplateOptimizer:
    """Optimizador de templates basado en aprendizaje."""
    
    def __init__(self):
        self.optimization_history = []
        
    async def optimize_template(self,
                              template_id: str,
                              patterns: List[PatternInsight],
                              performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimiza template basado en patrones aprendidos.
        
        Args:
            template_id: ID del template a optimizar
            patterns: Patrones identificados
            performance_data: Datos de performance del template
            
        Returns:
            Template optimizado
        """
        logger.info(f"Optimizando template {template_id} basado en {len(patterns)} patrones")
        
        optimizations = []
        
        for pattern in patterns:
            if pattern.impact_estimate > 0.2:  # Solo patrones con impacto significativo
                optimization = await self._apply_pattern_optimization(template_id, pattern)
                if optimization:
                    optimizations.append(optimization)
        
        # Aplicar optimizaciones de performance
        performance_optimizations = await self._apply_performance_optimizations(
            template_id, performance_data
        )
        optimizations.extend(performance_optimizations)
        
        # Registrar optimización
        self.optimization_history.append({
            'template_id': template_id,
            'optimizations_applied': len(optimizations),
            'patterns_processed': len(patterns),
            'timestamp': datetime.now().isoformat()
        })
        
        return {
            'optimizations_applied': optimizations,
            'improvement_estimate': sum(opt.get('impact', 0) for opt in optimizations),
            'next_review_date': datetime.now() + timedelta(days=30)
        }
    
    async def _apply_pattern_optimization(self, template_id: str, 
                                        pattern: PatternInsight) -> Optional[Dict[str, Any]]:
        """Aplica optimización basada en un patrón específico."""
        optimization = None
        
        if pattern.pattern_type == "low_satisfaction":
            optimization = {
                'type': 'quality_improvement',
                'description': f"Mejorar template para abordar: {pattern.description}",
                'action': pattern.suggested_action,
                'impact': pattern.impact_estimate
            }
        
        elif pattern.pattern_type == "recurring_suggestion":
            optimization = {
                'type': 'feature_addition',
                'description': f"Añadir feature sugerida: {pattern.description}",
                'action': pattern.suggested_action,
                'impact': pattern.impact_estimate
            }
        
        elif pattern.pattern_type == "execution_failure":
            optimization = {
                'type': 'reliability_improvement',
                'description': f"Mejorar confiabilidad: {pattern.description}",
                'action': pattern.suggested_action,
                'impact': pattern.impact_estimate
            }
        
        return optimization
    
    async def _apply_performance_optimizations(self, template_id: str,
                                             performance_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Aplica optimizaciones de performance."""
        optimizations = []
        
        # Optimización de tiempo de generación
        avg_generation_time = performance_data.get('avg_generation_time', 0)
        if avg_generation_time > 30:  # Más de 30 segundos
            optimizations.append({
                'type': 'performance_optimization',
                'description': 'Reducir tiempo de generación de template',
                'action': 'Optimizar algoritmos de adaptación',
                'impact': 0.2
            })
        
        # Optimización de accuracy
        accuracy = performance_data.get('accuracy', 0)
        if accuracy < 0.9:
            optimizations.append({
                'type': 'accuracy_optimization',
                'description': 'Mejorar precisión del template',
                'action': 'Ajustar criterios de adaptación',
                'impact': 0.3
            })
        
        return optimizations


class ContractLearningSystem:
    """
    Sistema principal de aprendizaje continuo para contratos.
    """
    
    def __init__(self, storage_path: str = "data/learning"):
        """
        Inicializa el sistema de aprendizaje.
        
        Args:
            storage_path: Directorio para almacenar datos de aprendizaje
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.feedback_store = FeedbackStore(str(self.storage_path / "feedback.jsonl"))
        self.pattern_learner = PatternLearner()
        self.template_optimizer = TemplateOptimizer()
        
        self.learning_metrics = {
            'total_feedback_processed': 0,
            'templates_optimized': 0,
            'accuracy_improvements': 0,
            'last_learning_cycle': None
        }
        
        logger.info("ContractLearningSystem inicializado")
    
    async def learn_from_execution(self,
                                 contract_id: str,
                                 execution_result: ExecutionResult,
                                 user_feedback: Optional[UserFeedback] = None) -> LearningUpdate:
        """
        Aprende de una ejecución de contrato.
        
        Args:
            contract_id: ID del contrato ejecutado
            execution_result: Resultado de la ejecución
            user_feedback: Feedback del usuario (opcional)
            
        Returns:
            LearningUpdate con cambios aplicados
        """
        logger.info(f"Aprendiendo de ejecución del contrato {contract_id}")
        
        try:
            # Almacenar feedback si se proporciona
            if user_feedback:
                await self.feedback_store.store_feedback(user_feedback)
                self.learning_metrics['total_feedback_processed'] += 1
            
            # Almacenar resultado de ejecución
            await self._store_execution_result(execution_result)
            
            # Obtener datos recientes para análisis
            recent_feedback = await self.feedback_store.get_recent_feedback(days=30)
            recent_executions = await self._get_recent_execution_results(days=30)
            
            # Identificar patrones de mejora
            improvement_patterns = await self.pattern_learner.identify_improvement_patterns(
                recent_feedback, recent_executions
            )
            
            # Aplicar optimizaciones si hay suficientes datos
            templates_updated = []
            confidence_improvement = 0.0
            
            if len(improvement_patterns) > 0:
                # Optimizar templates afectados
                affected_templates = self._identify_affected_templates(improvement_patterns)
                
                for template_id in affected_templates:
                    template_patterns = [p for p in improvement_patterns 
                                       if self._pattern_affects_template(p, template_id)]
                    
                    if template_patterns:
                        performance_data = await self._get_template_performance_data(template_id)
                        optimization_result = await self.template_optimizer.optimize_template(
                            template_id, template_patterns, performance_data
                        )
                        
                        templates_updated.append(template_id)
                        confidence_improvement += optimization_result.get('improvement_estimate', 0)
            
            # Determinar si reentrenar modelo
            models_retrained = await self._should_retrain_models(recent_feedback, recent_executions)
            
            # Calcular métricas de performance
            performance_delta = await self._calculate_performance_delta(
                execution_result, recent_executions
            )
            
            # Generar insights de aprendizaje
            learning_insights = self._generate_learning_insights(improvement_patterns)
            
            # Actualizar métricas
            if templates_updated:
                self.learning_metrics['templates_optimized'] += len(templates_updated)
            if confidence_improvement > 0:
                self.learning_metrics['accuracy_improvements'] += 1
            self.learning_metrics['last_learning_cycle'] = datetime.now().isoformat()
            
            update = LearningUpdate(
                templates_updated=templates_updated,
                models_retrained=models_retrained,
                confidence_improvement=confidence_improvement,
                performance_delta=performance_delta,
                next_optimization_date=datetime.now() + timedelta(days=7),
                learning_insights=learning_insights
            )
            
            logger.info(f"Aprendizaje completado: {len(templates_updated)} templates actualizados, "
                       f"mejora de confianza: {confidence_improvement:.3f}")
            
            return update
            
        except Exception as e:
            logger.error(f"Error en aprendizaje: {e}")
            return LearningUpdate(
                templates_updated=[],
                models_retrained=False,
                confidence_improvement=0.0,
                performance_delta={},
                next_optimization_date=datetime.now() + timedelta(days=7),
                learning_insights=[f"Error en aprendizaje: {str(e)}"]
            )
    
    async def _store_execution_result(self, execution_result: ExecutionResult) -> bool:
        """Almacena resultado de ejecución."""
        try:
            execution_file = self.storage_path / "executions.jsonl"
            
            execution_data = asdict(execution_result)
            
            with open(execution_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(execution_data) + '\n')
            
            return True
            
        except Exception as e:
            logger.error(f"Error almacenando resultado de ejecución: {e}")
            return False
    
    async def _get_recent_execution_results(self, days: int = 30) -> List[ExecutionResult]:
        """Obtiene resultados de ejecución recientes."""
        results = []
        execution_file = self.storage_path / "executions.jsonl"
        
        if not execution_file.exists():
            return results
        
        try:
            with open(execution_file, 'r', encoding='utf-8') as f:
                for line in f:
                    data = json.loads(line.strip())
                    results.append(ExecutionResult(**data))
        
        except Exception as e:
            logger.error(f"Error leyendo resultados de ejecución: {e}")
        
        return results
    
    def _identify_affected_templates(self, patterns: List[PatternInsight]) -> List[str]:
        """Identifica templates que necesitan optimización."""
        # Simplificado: todos los templates base pueden ser afectados
        return ['procedural', 'code', 'diagnostic', 'decision']
    
    def _pattern_affects_template(self, pattern: PatternInsight, template_id: str) -> bool:
        """Determina si un patrón afecta a un template específico."""
        # Simplificado: todos los patrones pueden afectar cualquier template
        return pattern.impact_estimate > 0.1
    
    async def _get_template_performance_data(self, template_id: str) -> Dict[str, Any]:
        """Obtiene datos de performance de un template."""
        # Simplificado: datos de performance básicos
        return {
            'avg_generation_time': 15.0,
            'accuracy': 0.85,
            'user_satisfaction': 4.2,
            'usage_count': 100
        }
    
    async def _should_retrain_models(self, feedback_data: List[UserFeedback],
                                   execution_data: List[ExecutionResult]) -> bool:
        """Determina si es necesario reentrenar modelos ML."""
        # Criterios para reentrenamiento
        if len(feedback_data) >= 100:  # Suficientes datos nuevos
            return True
        
        if len(execution_data) >= 50:  # Suficientes ejecuciones
            # Verificar si accuracy está bajando
            recent_quality = [e.final_output_quality for e in execution_data[-20:]]
            if len(recent_quality) >= 10 and np.mean(recent_quality) < 0.8:
                return True
        
        return False
    
    async def _calculate_performance_delta(self, current_result: ExecutionResult,
                                         historical_results: List[ExecutionResult]) -> Dict[str, float]:
        """Calcula cambio en performance."""
        if not historical_results:
            return {}
        
        # Comparar con promedio histórico
        historical_quality = np.mean([r.final_output_quality for r in historical_results])
        historical_satisfaction = np.mean([r.user_satisfaction for r in historical_results])
        
        return {
            'quality_delta': current_result.final_output_quality - historical_quality,
            'satisfaction_delta': current_result.user_satisfaction - historical_satisfaction,
            'success_rate_current': 1.0 if current_result.success else 0.0,
            'success_rate_historical': np.mean([1.0 if r.success else 0.0 for r in historical_results])
        }
    
    def _generate_learning_insights(self, patterns: List[PatternInsight]) -> List[str]:
        """Genera insights de aprendizaje."""
        insights = []
        
        if not patterns:
            insights.append("No se detectaron patrones significativos en esta iteración")
            return insights
        
        # Insights por tipo de patrón
        pattern_types = set(p.pattern_type for p in patterns)
        
        if "low_satisfaction" in pattern_types:
            insights.append("Se detectó patrón de baja satisfacción - revisar calidad de templates")
        
        if "recurring_suggestion" in pattern_types:
            insights.append("Usuarios sugieren mejoras consistentes - considerar implementar")
        
        if "execution_failure" in pattern_types:
            insights.append("Fallos recurrentes detectados - mejorar robustez de templates")
        
        # Insight general
        high_impact_patterns = [p for p in patterns if p.impact_estimate > 0.3]
        if high_impact_patterns:
            insights.append(f"{len(high_impact_patterns)} patrones de alto impacto identificados")
        
        return insights
    
    def get_learning_metrics(self) -> Dict[str, Any]:
        """Retorna métricas del sistema de aprendizaje."""
        return self.learning_metrics.copy()
    
    async def generate_learning_report(self) -> Dict[str, Any]:
        """Genera reporte completo de aprendizaje."""
        recent_feedback = await self.feedback_store.get_recent_feedback(days=30)
        recent_executions = await self._get_recent_execution_results(days=30)
        
        return {
            'period': '30 days',
            'feedback_count': len(recent_feedback),
            'execution_count': len(recent_executions),
            'avg_user_satisfaction': np.mean([f.rating for f in recent_feedback]) if recent_feedback else 0,
            'success_rate': np.mean([1.0 if e.success else 0.0 for e in recent_executions]) if recent_executions else 0,
            'learning_metrics': self.learning_metrics,
            'optimization_history': self.template_optimizer.optimization_history[-10:]  # Últimas 10
        }


# Función de conveniencia para integración
async def learn_from_contract_execution(contract_id: str,
                                      execution_success: bool,
                                      quality_score: float,
                                      user_rating: Optional[float] = None,
                                      user_comments: Optional[str] = None) -> LearningUpdate:
    """
    Función de conveniencia para aprender de ejecución de contrato.
    
    Args:
        contract_id: ID del contrato
        execution_success: Si la ejecución fue exitosa
        quality_score: Score de calidad del resultado
        user_rating: Rating del usuario (1-5)
        user_comments: Comentarios del usuario
        
    Returns:
        LearningUpdate con cambios aplicados
    """
    learning_system = ContractLearningSystem()
    
    # Crear resultado de ejecución
    execution_result = ExecutionResult(
        contract_id=contract_id,
        success=execution_success,
        completion_time=30.0,  # Placeholder
        quality_score=quality_score,
        user_satisfaction=user_rating or 4.0,
        errors_encountered=[],
        metrics_achieved={'quality': quality_score},
        final_output_quality=quality_score
    )
    
    # Crear feedback si se proporciona
    user_feedback = None
    if user_rating is not None:
        user_feedback = UserFeedback(
            contract_id=contract_id,
            user_id="default_user",
            feedback_type=FeedbackType.USER_SATISFACTION,
            rating=user_rating,
            comments=user_comments,
            specific_issues=[],
            suggestions=[],
            timestamp=datetime.now()
        )
    
    return await learning_system.learn_from_execution(
        contract_id, execution_result, user_feedback
    )
