"""
Advanced Contract Generator - Generador principal de contratos avanzados

Este módulo integra todos los componentes del PR-F para generar contratos
inteligentes y adaptativos que reemplazan el sistema básico.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from app.spec_layer import TaskContract, RiskLevel, TaskType
from app.context_manager import ContextManager
from app.human_loop import HumanLoopManager, check_critical_action

from .intelligent_classifier import (
    IntelligentTaskClassifier, 
    TaskTypeAdvanced,
    classify_task_advanced
)
from .adaptive_templates import (
    AdaptiveTemplateEngine,
    ProjectProfiler,
    generate_adaptive_contract_template
)
from .risk_engine import (
    AdvancedRiskEngine,
    assess_task_risk
)
from .learning_system import (
    ContractLearningSystem,
    learn_from_contract_execution
)
from .performance_optimizer import (
    PerformanceOptimizer,
    optimize_performance,
    OptimizationType
)

logger = logging.getLogger(__name__)


@dataclass
class AdvancedContractConfig:
    """Configuración del generador avanzado."""
    enable_ml_classification: bool = True
    enable_adaptive_templates: bool = True
    enable_advanced_risk_assessment: bool = True
    enable_learning_system: bool = True
    enable_performance_optimization: bool = True
    project_path: str = "."
    fallback_to_basic: bool = True


class AdvancedContractGenerator:
    """
    Generador principal de contratos avanzados que integra todos los componentes del PR-F.
    """
    
    def __init__(self,
                 context_manager: ContextManager,
                 human_loop_manager: Optional[HumanLoopManager] = None,
                 config: Optional[AdvancedContractConfig] = None):
        """
        Inicializa el generador avanzado.
        
        Args:
            context_manager: Gestor de contexto existente
            human_loop_manager: Gestor de human-loop existente
            config: Configuración del sistema avanzado
        """
        self.context_manager = context_manager
        self.human_loop_manager = human_loop_manager
        self.config = config or AdvancedContractConfig()
        
        # Inicializar componentes según configuración
        self.classifier = None
        self.template_engine = None
        self.risk_engine = None
        self.learning_system = None
        self.performance_optimizer = None
        
        self._initialize_components()
        
        # Métricas del generador
        self.generation_metrics = {
            'contracts_generated': 0,
            'advanced_generations': 0,
            'fallback_generations': 0,
            'average_generation_time': 0.0,
            'classification_accuracy': 0.0,
            'user_satisfaction': 0.0
        }
        
        logger.info("AdvancedContractGenerator inicializado")
    
    def _initialize_components(self):
        """Inicializa componentes según configuración."""
        try:
            if self.config.enable_ml_classification:
                self.classifier = IntelligentTaskClassifier()
                logger.info("Clasificador ML inicializado")
            
            if self.config.enable_adaptive_templates:
                self.template_engine = AdaptiveTemplateEngine()
                logger.info("Motor de templates adaptativos inicializado")
            
            if self.config.enable_advanced_risk_assessment:
                self.risk_engine = AdvancedRiskEngine()
                logger.info("Motor avanzado de riesgo inicializado")
            
            if self.config.enable_learning_system:
                self.learning_system = ContractLearningSystem()
                logger.info("Sistema de aprendizaje inicializado")
            
            if self.config.enable_performance_optimization:
                self.performance_optimizer = PerformanceOptimizer()
                logger.info("Optimizador de performance inicializado")
                
        except Exception as e:
            logger.warning(f"Error inicializando componentes avanzados: {e}")
            if not self.config.fallback_to_basic:
                raise
    
    @optimize_performance("generate_advanced_contract", [OptimizationType.CACHING, OptimizationType.PREPROCESSING])
    async def generate_advanced_contract(self,
                                       query: str,
                                       user_role: str = "developer",
                                       risk_level: Optional[RiskLevel] = None,
                                       context_chunks: Optional[List[Dict[str, Any]]] = None,
                                       files_affected: Optional[List[str]] = None,
                                       user_history: Optional[List[Dict]] = None) -> TaskContract:
        """
        Genera contrato avanzado usando todos los componentes del PR-F.
        
        Args:
            query: Consulta del usuario
            user_role: Rol del usuario
            risk_level: Nivel de riesgo (se evalúa si no se proporciona)
            context_chunks: Chunks de contexto
            files_affected: Archivos afectados
            user_history: Historial del usuario
            
        Returns:
            TaskContract avanzado y optimizado
        """
        logger.info(f"Generando contrato avanzado para: '{query[:50]}...'")
        
        try:
            start_time = datetime.now()
            
            # 1. CLASIFICACIÓN INTELIGENTE
            classification_result = None
            if self.classifier:
                project_context = await self._build_project_context()
                classification_result = await self.classifier.classify_with_context(
                    query=query,
                    project_context=project_context,
                    user_history=user_history or []
                )
                logger.info(f"Clasificación: {classification_result.primary_type.value} "
                           f"(confianza: {classification_result.confidence:.2f})")
            
            # 2. ANÁLISIS DE PROYECTO Y TEMPLATE ADAPTATIVO
            adaptive_template = None
            if self.template_engine and classification_result:
                profiler = ProjectProfiler()
                project_profile = await profiler.analyze_project(self.config.project_path)
                
                adaptive_template = await self.template_engine.generate_adaptive_template(
                    task_type=classification_result.primary_type,
                    project_profile=project_profile,
                    user_preferences=self._extract_user_preferences(user_role, user_history)
                )
                logger.info(f"Template adaptativo generado: {adaptive_template.base_template_id}")
            
            # 3. EVALUACIÓN AVANZADA DE RIESGO
            advanced_risk_assessment = None
            if self.risk_engine:
                advanced_risk_assessment = await self.risk_engine.assess_comprehensive_risk(
                    task_description=query,
                    files_affected=files_affected or [],
                    project_profile=project_profile if 'project_profile' in locals() else None,
                    historical_data=self._get_historical_risk_data()
                )
                logger.info(f"Riesgo evaluado: {advanced_risk_assessment.overall_level.value} "
                           f"(score: {advanced_risk_assessment.overall_score:.2f})")
            
            # 4. CONSTRUCCIÓN DEL CONTRATO AVANZADO
            contract = await self._build_advanced_contract(
                query=query,
                user_role=user_role,
                classification_result=classification_result,
                adaptive_template=adaptive_template,
                risk_assessment=advanced_risk_assessment,
                context_chunks=context_chunks,
                files_affected=files_affected
            )
            
            # 5. APRENDIZAJE Y OPTIMIZACIÓN
            if self.learning_system:
                # Registrar generación para aprendizaje futuro
                await self._register_for_learning(contract, classification_result, adaptive_template)
            
            # Actualizar métricas
            generation_time = (datetime.now() - start_time).total_seconds()
            await self._update_generation_metrics(generation_time, advanced=True)
            
            logger.info(f"Contrato avanzado generado en {generation_time:.2f}s: {contract.id}")
            
            return contract
            
        except Exception as e:
            logger.error(f"Error en generación avanzada: {e}")
            
            if self.config.fallback_to_basic:
                logger.info("Usando fallback al sistema básico")
                return await self._generate_basic_fallback(query, user_role, risk_level, 
                                                         context_chunks, files_affected)
            else:
                raise
    
    async def _build_project_context(self) -> Dict[str, Any]:
        """Construye contexto del proyecto para clasificación."""
        try:
            # Analizar proyecto actual
            profiler = ProjectProfiler()
            project_profile = await profiler.analyze_project(self.config.project_path)
            
            return {
                'project_type': project_profile.project_type.value,
                'frameworks': project_profile.frameworks,
                'complexity_score': project_profile.complexity_score,
                'team_size': project_profile.team_size,
                'maturity_level': project_profile.maturity_level,
                'has_tests': project_profile.has_tests,
                'has_ci_cd': project_profile.has_ci_cd,
                'lines_of_code': project_profile.lines_of_code
            }
        except Exception as e:
            logger.warning(f"Error construyendo contexto de proyecto: {e}")
            return {}
    
    def _extract_user_preferences(self, user_role: str, 
                                 user_history: Optional[List[Dict]]) -> Dict[str, Any]:
        """Extrae preferencias del usuario basado en rol e historial."""
        preferences = {
            'detail_level': 'medium',
            'format': 'markdown',
            'experience_level': 'intermediate'
        }
        
        # Ajustar según rol
        if user_role == 'manager':
            preferences['detail_level'] = 'high'
            preferences['experience_level'] = 'intermediate'
        elif user_role == 'senior_developer':
            preferences['detail_level'] = 'medium'
            preferences['experience_level'] = 'expert'
        elif user_role == 'junior_developer':
            preferences['detail_level'] = 'high'
            preferences['experience_level'] = 'beginner'
        
        # Ajustar según historial
        if user_history:
            avg_complexity = sum(task.get('complexity', 0.5) for task in user_history) / len(user_history)
            if avg_complexity > 0.8:
                preferences['experience_level'] = 'expert'
            elif avg_complexity < 0.3:
                preferences['experience_level'] = 'beginner'
        
        return preferences
    
    def _get_historical_risk_data(self) -> Optional[Dict[str, Any]]:
        """Obtiene datos históricos de riesgo."""
        if self.risk_engine:
            risk_history = self.risk_engine.get_risk_history()
            if risk_history:
                return {
                    'similar_incidents': [],  # Simplificado
                    'avg_risk_score': sum(r.overall_score for r in risk_history) / len(risk_history),
                    'recent_assessments': len([r for r in risk_history 
                                             if (datetime.utcnow() - r.assessment_timestamp).days < 30])
                }
        return None
    
    async def _build_advanced_contract(self,
                                     query: str,
                                     user_role: str,
                                     classification_result: Optional[Any],
                                     adaptive_template: Optional[Any],
                                     risk_assessment: Optional[Any],
                                     context_chunks: Optional[List[Dict[str, Any]]],
                                     files_affected: Optional[List[str]]) -> TaskContract:
        """Construye el contrato final usando todos los componentes avanzados."""
        
        # Usar clasificación avanzada o fallback
        if classification_result:
            # Mapear TaskTypeAdvanced a TaskType del sistema actual
            task_type_mapping = {
                TaskTypeAdvanced.PROCEDURAL: TaskType.PROCEDURAL,
                TaskTypeAdvanced.CODE: TaskType.CODE,
                TaskTypeAdvanced.DIAGNOSTIC: TaskType.DIAGNOSTIC,
                TaskTypeAdvanced.ANALYSIS: TaskType.ANALYSIS,
                TaskTypeAdvanced.DOCUMENTATION: TaskType.DOCUMENTATION,
                TaskTypeAdvanced.TEST: TaskType.TEST,
                TaskTypeAdvanced.REVIEW: TaskType.REVIEW,
                # Mapear tipos nuevos a existentes
                TaskTypeAdvanced.SECURITY_AUDIT: TaskType.ANALYSIS,
                TaskTypeAdvanced.PERFORMANCE_OPTIMIZATION: TaskType.CODE,
                TaskTypeAdvanced.ARCHITECTURE_DESIGN: TaskType.ANALYSIS
            }
            task_type = task_type_mapping.get(classification_result.primary_type, TaskType.PROCEDURAL)
        else:
            # Fallback a detección básica
            task_type = self._detect_task_type_basic(query)
        
        # Usar evaluación de riesgo avanzada o básica
        if risk_assessment:
            risk_level = risk_assessment.overall_level
        else:
            risk_level = self._assess_risk_level_basic(query, files_affected or [])
        
        # Construir goal usando template adaptativo
        if adaptive_template:
            goal = adaptive_template.adapted_goal.format(query=query)
            musts = adaptive_template.adapted_musts
            format_spec = adaptive_template.adapted_format
            metrics = adaptive_template.adapted_metrics
        else:
            # Fallback a template básico
            basic_template = self._get_basic_template(task_type)
            goal = basic_template['goal_template'].format(query=query)
            musts = basic_template['musts']
            format_spec = basic_template['format']
            metrics = basic_template['metrics']
        
        # Analizar contexto
        context_analysis = await self._analyze_context_advanced(query, context_chunks)
        
        # Crear contrato
        contract = TaskContract(
            id=str(uuid.uuid4()),
            task_type=task_type,
            goal=goal,
            musts=musts + self._get_context_specific_musts(context_analysis),
            format=format_spec,
            metrics=metrics,
            risk_level=risk_level,
            context_sources=context_analysis.get('source_ids', []),
            files_affected=files_affected or [],
            human_approval_required=risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL],
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        
        # Añadir metadatos avanzados
        if hasattr(contract, 'metadata'):
            contract.metadata = {}
        else:
            # Si TaskContract no tiene metadata, lo añadimos como atributo
            contract.advanced_metadata = {}
        
        metadata_target = getattr(contract, 'metadata', getattr(contract, 'advanced_metadata', {}))
        
        if classification_result:
            metadata_target['classification'] = {
                'primary_type': classification_result.primary_type.value,
                'confidence': classification_result.confidence,
                'reasoning': classification_result.reasoning
            }
        
        if adaptive_template:
            metadata_target['template_adaptation'] = {
                'base_template': adaptive_template.base_template_id,
                'adaptation_reasoning': adaptive_template.adaptation_reasoning,
                'estimated_complexity': adaptive_template.estimated_complexity
            }
        
        if risk_assessment:
            metadata_target['advanced_risk'] = {
                'overall_score': risk_assessment.overall_score,
                'confidence': risk_assessment.confidence,
                'mitigation_strategies': risk_assessment.mitigation_strategies
            }
        
        # Verificar aprobación humana con sistema avanzado
        if contract.human_approval_required and self.human_loop_manager:
            approval_needed = await check_critical_action(
                plan={'goal': contract.goal, 'files': contract.files_affected},
                files_affected=contract.files_affected,
                human_loop_manager=self.human_loop_manager
            )
            if not approval_needed:
                contract.human_approval_required = False
        
        return contract
    
    def _detect_task_type_basic(self, query: str) -> TaskType:
        """Detección básica de tipo de tarea (fallback)."""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['cómo', 'how', 'pasos', 'steps']):
            return TaskType.PROCEDURAL
        elif any(word in query_lower for word in ['error', 'problema', 'bug']):
            return TaskType.DIAGNOSTIC
        elif any(word in query_lower for word in ['código', 'code', 'función']):
            return TaskType.CODE
        else:
            return TaskType.PROCEDURAL
    
    def _assess_risk_level_basic(self, query: str, files_affected: List[str]) -> RiskLevel:
        """Evaluación básica de riesgo (fallback)."""
        risk_score = 0.0
        
        # Factores básicos de riesgo
        high_risk_keywords = ['delete', 'remove', 'drop', 'migrate', 'deploy']
        for keyword in high_risk_keywords:
            if keyword in query.lower():
                risk_score += 0.3
        
        # Archivos críticos
        critical_paths = ['/auth/', '/payments/', '/security/']
        for file_path in files_affected:
            for critical_path in critical_paths:
                if critical_path in file_path:
                    risk_score += 0.4
                    break
        
        # Determinar nivel
        if risk_score >= 0.8:
            return RiskLevel.CRITICAL
        elif risk_score >= 0.6:
            return RiskLevel.HIGH
        elif risk_score >= 0.3:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _get_basic_template(self, task_type: TaskType) -> Dict[str, Any]:
        """Obtiene template básico para fallback."""
        templates = {
            TaskType.PROCEDURAL: {
                'goal_template': "Proporcionar pasos claros para: {query}",
                'musts': ["Usar información verificada", "Incluir pasos numerados", "Citar fuentes"],
                'format': "Markdown con pasos numerados",
                'metrics': {'max_tokens': 1000, 'clarity_score': 0.9}
            },
            TaskType.CODE: {
                'goal_template': "Generar código funcional para: {query}",
                'musts': ["Incluir comentarios", "Seguir mejores prácticas", "Incluir ejemplos"],
                'format': "Código con comentarios",
                'metrics': {'max_tokens': 1500, 'code_quality': 0.9}
            }
        }
        
        return templates.get(task_type, templates[TaskType.PROCEDURAL])
    
    async def _analyze_context_advanced(self, query: str, 
                                      context_chunks: Optional[List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Análisis avanzado de contexto."""
        analysis = {
            'source_ids': [],
            'relevance_scores': [],
            'context_quality': 0.8,
            'coverage_score': 0.7
        }
        
        if context_chunks:
            analysis['source_ids'] = [chunk.get('id', f'chunk_{i}') 
                                    for i, chunk in enumerate(context_chunks)]
            analysis['relevance_scores'] = [chunk.get('relevance_score', 0.8) 
                                          for chunk in context_chunks]
            analysis['context_quality'] = sum(analysis['relevance_scores']) / len(analysis['relevance_scores'])
        
        return analysis
    
    def _get_context_specific_musts(self, context_analysis: Dict[str, Any]) -> List[str]:
        """Genera musts específicos del contexto."""
        additional_musts = []
        
        if context_analysis.get('context_quality', 0) < 0.7:
            additional_musts.append("Verificar calidad de fuentes antes de usar")
        
        if len(context_analysis.get('source_ids', [])) > 5:
            additional_musts.append("Priorizar fuentes más relevantes")
        
        return additional_musts
    
    async def _register_for_learning(self, contract: TaskContract, 
                                   classification_result: Optional[Any],
                                   adaptive_template: Optional[Any]):
        """Registra contrato para aprendizaje futuro."""
        if not self.learning_system:
            return
        
        try:
            # Crear registro para seguimiento
            learning_data = {
                'contract_id': contract.id,
                'classification_used': classification_result.primary_type.value if classification_result else None,
                'template_used': adaptive_template.base_template_id if adaptive_template else None,
                'risk_level': contract.risk_level.value,
                'created_at': contract.created_at.isoformat()
            }
            
            # En implementación completa, esto se almacenaría para seguimiento
            logger.debug(f"Contrato registrado para aprendizaje: {contract.id}")
            
        except Exception as e:
            logger.warning(f"Error registrando para aprendizaje: {e}")
    
    async def _generate_basic_fallback(self, query: str, user_role: str, 
                                     risk_level: Optional[RiskLevel],
                                     context_chunks: Optional[List[Dict[str, Any]]],
                                     files_affected: Optional[List[str]]) -> TaskContract:
        """Genera contrato usando sistema básico como fallback."""
        task_type = self._detect_task_type_basic(query)
        
        if risk_level is None:
            risk_level = self._assess_risk_level_basic(query, files_affected or [])
        
        basic_template = self._get_basic_template(task_type)
        context_analysis = await self._analyze_context_advanced(query, context_chunks)
        
        contract = TaskContract(
            id=str(uuid.uuid4()),
            task_type=task_type,
            goal=basic_template['goal_template'].format(query=query),
            musts=basic_template['musts'] + self._get_context_specific_musts(context_analysis),
            format=basic_template['format'],
            metrics=basic_template['metrics'],
            risk_level=risk_level,
            context_sources=context_analysis.get('source_ids', []),
            files_affected=files_affected or [],
            human_approval_required=risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL],
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        
        # Actualizar métricas de fallback
        await self._update_generation_metrics(0.5, advanced=False)
        
        return contract
    
    async def _update_generation_metrics(self, generation_time: float, advanced: bool):
        """Actualiza métricas de generación."""
        self.generation_metrics['contracts_generated'] += 1
        
        if advanced:
            self.generation_metrics['advanced_generations'] += 1
        else:
            self.generation_metrics['fallback_generations'] += 1
        
        # Actualizar tiempo promedio
        total_contracts = self.generation_metrics['contracts_generated']
        current_avg = self.generation_metrics['average_generation_time']
        self.generation_metrics['average_generation_time'] = (
            (current_avg * (total_contracts - 1) + generation_time) / total_contracts
        )
    
    async def learn_from_contract_feedback(self, contract_id: str,
                                         execution_success: bool,
                                         quality_score: float,
                                         user_rating: Optional[float] = None):
        """
        Aprende de feedback de ejecución de contrato.
        
        Args:
            contract_id: ID del contrato ejecutado
            execution_success: Si la ejecución fue exitosa
            quality_score: Score de calidad del resultado
            user_rating: Rating del usuario (1-5)
        """
        if not self.learning_system:
            logger.warning("Sistema de aprendizaje no disponible")
            return
        
        try:
            learning_update = await learn_from_contract_execution(
                contract_id=contract_id,
                execution_success=execution_success,
                quality_score=quality_score,
                user_rating=user_rating
            )
            
            logger.info(f"Aprendizaje completado para contrato {contract_id}: "
                       f"{len(learning_update.templates_updated)} templates actualizados")
            
            # Actualizar métricas de satisfacción
            if user_rating:
                current_satisfaction = self.generation_metrics['user_satisfaction']
                total_contracts = self.generation_metrics['contracts_generated']
                
                self.generation_metrics['user_satisfaction'] = (
                    (current_satisfaction * (total_contracts - 1) + user_rating) / total_contracts
                )
            
        except Exception as e:
            logger.error(f"Error en aprendizaje de feedback: {e}")
    
    def get_generation_metrics(self) -> Dict[str, Any]:
        """Retorna métricas de generación."""
        metrics = self.generation_metrics.copy()
        
        # Añadir métricas de componentes
        if self.classifier:
            metrics['classifier_metrics'] = self.classifier.get_performance_metrics()
        
        if self.risk_engine:
            metrics['risk_engine_stats'] = self.risk_engine.get_risk_statistics()
        
        if self.learning_system:
            metrics['learning_metrics'] = self.learning_system.get_learning_metrics()
        
        if self.performance_optimizer:
            metrics['performance_stats'] = await self.performance_optimizer.get_optimization_report()
        
        return metrics
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Retorna estado de salud del sistema avanzado."""
        health = {
            'overall_status': 'healthy',
            'components': {},
            'performance': {},
            'recommendations': []
        }
        
        # Verificar salud de componentes
        if self.classifier:
            classifier_metrics = self.classifier.get_performance_metrics()
            health['components']['classifier'] = {
                'status': 'healthy' if classifier_metrics.get('accuracy', 0) > 0.8 else 'degraded',
                'accuracy': classifier_metrics.get('accuracy', 0),
                'predictions_made': classifier_metrics.get('predictions_made', 0)
            }
        
        # Performance general
        health['performance'] = {
            'avg_generation_time': self.generation_metrics['average_generation_time'],
            'advanced_usage_rate': (
                self.generation_metrics['advanced_generations'] / 
                max(1, self.generation_metrics['contracts_generated'])
            ),
            'user_satisfaction': self.generation_metrics['user_satisfaction']
        }
        
        # Recomendaciones
        if health['performance']['avg_generation_time'] > 10:
            health['recommendations'].append("Considerar optimización de performance")
        
        if health['performance']['user_satisfaction'] < 4.0:
            health['recommendations'].append("Revisar calidad de templates")
        
        return health


# Función de conveniencia para crear generador avanzado
def create_advanced_contract_generator(context_manager: ContextManager,
                                     human_loop_manager: Optional[HumanLoopManager] = None,
                                     project_path: str = ".") -> AdvancedContractGenerator:
    """
    Crea instancia del generador avanzado con configuración por defecto.
    
    Args:
        context_manager: Gestor de contexto
        human_loop_manager: Gestor de human-loop
        project_path: Ruta al proyecto
        
    Returns:
        AdvancedContractGenerator configurado
    """
    config = AdvancedContractConfig(
        enable_ml_classification=True,
        enable_adaptive_templates=True,
        enable_advanced_risk_assessment=True,
        enable_learning_system=True,
        enable_performance_optimization=True,
        project_path=project_path,
        fallback_to_basic=True
    )
    
    return AdvancedContractGenerator(
        context_manager=context_manager,
        human_loop_manager=human_loop_manager,
        config=config
    )
