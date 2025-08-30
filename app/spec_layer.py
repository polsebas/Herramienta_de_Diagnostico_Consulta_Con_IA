"""
Spec Layer - Sistema de Contratos Inteligentes para Tareas

Este módulo implementa el sistema Spec-First con contratos dinámicos basados en contexto,
integración con GitHub y validación automática de cumplimiento.
"""

import json
import logging
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import yaml

from app.human_loop import HumanLoopManager, check_critical_action
from app.context_manager import ContextManager

logger = logging.getLogger(__name__)


class TaskType(Enum):
    """Tipos de tareas soportados por el sistema."""
    PROCEDURAL = "procedural"      # Cómo hacer algo
    DIAGNOSTIC = "diagnostic"      # Análisis de problemas
    DECISION = "decision"          # Toma de decisiones
    CODE = "code"                  # Generación de código
    ANALYSIS = "analysis"          # Análisis de datos/código
    DOCUMENTATION = "documentation" # Generación de documentación
    TEST = "test"                  # Generación de tests
    REVIEW = "review"              # Revisión de código


class RiskLevel(Enum):
    """Niveles de riesgo para contratos."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class TaskContract:
    """Contrato de tarea con especificaciones completas."""
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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el contrato a diccionario para serialización."""
        return {
            **asdict(self),
            'task_type': self.task_type.value,
            'risk_level': self.risk_level.value,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }


@dataclass
class ContractValidation:
    """Resultado de validación de contrato."""
    is_valid: bool
    score: float
    violations: List[str]
    recommendations: List[str]
    source_coverage: float
    context_relevance: float


class SpecLayer:
    """
    Capa de especificaciones que genera contratos inteligentes basados en contexto.
    """
    
    def __init__(self, 
                 context_manager: ContextManager,
                 human_loop_manager: Optional[HumanLoopManager] = None,
                 config_path: str = "config/spec_layer.yml"):
        """
        Inicializa el Spec Layer.
        
        Args:
            context_manager: Gestor de contexto para análisis histórico
            human_loop_manager: Gestor de human-in-the-loop (opcional)
            config_path: Ruta al archivo de configuración
        """
        self.context_manager = context_manager
        self.human_loop_manager = human_loop_manager
        self.config = self._load_config(config_path)
        self.contract_templates = self._load_templates()
        self.active_contracts: Dict[str, TaskContract] = {}
        
        logger.info("Spec Layer inicializado")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Carga configuración desde archivo YAML."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Archivo de configuración {config_path} no encontrado, usando configuración por defecto")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Configuración por defecto del Spec Layer."""
        return {
            'risk_thresholds': {
                'low': 0.3,
                'medium': 0.6,
                'high': 0.8,
                'critical': 0.9
            },
            'contract_expiry_hours': 24,
            'max_context_chunks': 5,
            'min_source_coverage': 0.7,
            'auto_approval_threshold': 0.8
        }
    
    def _load_templates(self) -> Dict[str, Dict[str, Any]]:
        """Carga plantillas de contratos desde directorio specs/."""
        templates = {}
        specs_dir = Path("app/specs")
        
        if specs_dir.exists():
            for yaml_file in specs_dir.glob("*.yaml"):
                try:
                    with open(yaml_file, 'r', encoding='utf-8') as f:
                        template_data = yaml.safe_load(f)
                        task_type = yaml_file.stem
                        templates[task_type] = template_data
                except Exception as e:
                    logger.error(f"Error cargando plantilla {yaml_file}: {e}")
        
        # Plantillas por defecto si no hay archivos
        if not templates:
            templates = self._get_default_templates()
        
        return templates
    
    def _get_default_templates(self) -> Dict[str, Dict[str, Any]]:
        """Plantillas por defecto para diferentes tipos de tarea."""
        return {
            'procedural': {
                'goal_template': "Proporcionar pasos claros para: {query}",
                'musts': [
                    "Usar solo información de fuentes verificadas",
                    "Incluir pasos numerados y secuenciales",
                    "Mencionar requisitos previos si existen",
                    "Incluir sección 'Fuentes' con referencias precisas"
                ],
                'format': "Markdown con pasos numerados y sección de fuentes",
                'metrics': {
                    'clarity_score': 0.9,
                    'completeness_score': 0.8,
                    'max_tokens': 1000
                }
            },
            'diagnostic': {
                'goal_template': "Analizar y diagnosticar el problema: {query}",
                'musts': [
                    "Identificar síntomas específicos",
                    "Proponer causas probables",
                    "Sugerir soluciones verificadas",
                    "Incluir sección 'Diagnóstico' y 'Soluciones'"
                ],
                'format': "Markdown con secciones de diagnóstico y soluciones",
                'metrics': {
                    'accuracy_score': 0.9,
                    'solution_quality': 0.8,
                    'max_tokens': 1200
                }
            },
            'code': {
                'goal_template': "Generar código para: {query}",
                'musts': [
                    "Incluir comentarios explicativos",
                    "Seguir mejores prácticas del lenguaje",
                    "Incluir ejemplos de uso",
                    "Mencionar dependencias requeridas"
                ],
                'format': "Código con comentarios y documentación",
                'metrics': {
                    'code_quality': 0.9,
                    'documentation_score': 0.8,
                    'max_tokens': 1500
                }
            },
            'decision': {
                'goal_template': "Analizar opciones y recomendar decisión para: {query}",
                'musts': [
                    "Presentar opciones claras",
                    "Analizar pros y contras",
                    "Recomendar con justificación",
                    "Considerar impacto y riesgos"
                ],
                'format': "Markdown con análisis estructurado",
                'metrics': {
                    'analysis_depth': 0.9,
                    'recommendation_quality': 0.8,
                    'max_tokens': 1000
                }
            }
        }
    
    async def build_task_contract(self,
                                 query: str,
                                 user_role: str = "developer",
                                 risk_level: Optional[RiskLevel] = None,
                                 context_chunks: Optional[List[Dict[str, Any]]] = None,
                                 files_affected: Optional[List[str]] = None) -> TaskContract:
        """
        Construye un contrato de tarea inteligente basado en contexto.
        
        Args:
            query: Consulta del usuario
            user_role: Rol del usuario (developer, manager, etc.)
            risk_level: Nivel de riesgo (se infiere si no se proporciona)
            context_chunks: Chunks de contexto relevantes
            files_affected: Archivos que podrían verse afectados
            
        Returns:
            TaskContract configurado
        """
        # Detectar tipo de tarea
        task_type = self._detect_task_type(query)
        
        # Inferir nivel de riesgo si no se proporciona
        if risk_level is None:
            risk_level = self._assess_risk_level(query, files_affected or [])
        
        # Obtener plantilla base
        template = self.contract_templates.get(task_type.value, self.contract_templates['procedural'])
        
        # Analizar contexto histórico
        context_analysis = await self._analyze_context(query, context_chunks)
        
        # Generar contrato
        contract = TaskContract(
            id=str(uuid.uuid4()),
            task_type=task_type,
            goal=template['goal_template'].format(query=query),
            musts=template['musts'] + self._get_context_specific_musts(context_analysis),
            format=template['format'],
            metrics=template['metrics'],
            risk_level=risk_level,
            context_sources=context_analysis.get('source_ids', []),
            files_affected=files_affected or [],
            human_approval_required=risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL],
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=self.config['contract_expiry_hours'])
        )
        
        # Verificar si requiere aprobación humana
        if contract.human_approval_required and self.human_loop_manager:
            approval_needed = await check_critical_action(
                plan={'goal': contract.goal, 'files': contract.files_affected},
                files_affected=contract.files_affected,
                human_loop_manager=self.human_loop_manager
            )
            if not approval_needed:
                contract.human_approval_required = False
        
        # Almacenar contrato activo
        self.active_contracts[contract.id] = contract
        
        logger.info(f"Contrato generado: {contract.id} - Tipo: {task_type.value} - Riesgo: {risk_level.value}")
        return contract
    
    def _detect_task_type(self, query: str) -> TaskType:
        """Detecta el tipo de tarea basado en la consulta."""
        query_lower = query.lower()
        
        # Palabras clave para cada tipo
        type_keywords = {
            TaskType.PROCEDURAL: ['cómo', 'how', 'pasos', 'steps', 'proceso', 'process'],
            TaskType.DIAGNOSTIC: ['error', 'problema', 'issue', 'bug', 'diagnosticar', 'diagnose'],
            TaskType.DECISION: ['decidir', 'decide', 'opción', 'option', 'recomendar', 'recommend'],
            TaskType.CODE: ['código', 'code', 'implementar', 'implement', 'función', 'function'],
            TaskType.ANALYSIS: ['analizar', 'analyze', 'revisar', 'review', 'evaluar', 'evaluate'],
            TaskType.DOCUMENTATION: ['documentar', 'document', 'readme', 'docs'],
            TaskType.TEST: ['test', 'prueba', 'testing', 'unit', 'integration'],
            TaskType.REVIEW: ['revisar', 'review', 'code review', 'pull request']
        }
        
        # Contar coincidencias
        scores = {}
        for task_type, keywords in type_keywords.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                scores[task_type] = score
        
        # Retornar tipo con mayor score
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        
        # Por defecto, procedural
        return TaskType.PROCEDURAL
    
    def _assess_risk_level(self, query: str, files_affected: List[str]) -> RiskLevel:
        """Evalúa el nivel de riesgo basado en la consulta y archivos afectados."""
        risk_score = 0.0
        
        # Factores de riesgo en la consulta
        high_risk_keywords = ['delete', 'remove', 'drop', 'migrate', 'deploy', 'production']
        medium_risk_keywords = ['update', 'modify', 'change', 'refactor', 'optimize']
        
        query_lower = query.lower()
        for keyword in high_risk_keywords:
            if keyword in query_lower:
                risk_score += 0.4
        
        for keyword in medium_risk_keywords:
            if keyword in query_lower:
                risk_score += 0.2
        
        # Factores de riesgo en archivos
        critical_paths = ['/auth/', '/payments/', '/migrations/', '/infra/', '/config/']
        for file_path in files_affected:
            for critical_path in critical_paths:
                if critical_path in file_path:
                    risk_score += 0.3
                    break
        
        # Determinar nivel de riesgo
        if risk_score >= self.config['risk_thresholds']['critical']:
            return RiskLevel.CRITICAL
        elif risk_score >= self.config['risk_thresholds']['high']:
            return RiskLevel.HIGH
        elif risk_score >= self.config['risk_thresholds']['medium']:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    async def _analyze_context(self, query: str, context_chunks: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Analiza el contexto histórico y chunks relevantes."""
        analysis = {
            'source_ids': [],
            'relevance_scores': [],
            'context_summary': '',
            'related_tasks': []
        }
        
        if context_chunks:
            analysis['source_ids'] = [chunk.get('id', '') for chunk in context_chunks]
            analysis['relevance_scores'] = [chunk.get('score', 0.0) for chunk in context_chunks]
        
        # Obtener historial relevante del Context Manager
        if self.context_manager:
            history = await self.context_manager.get_relevant_history(query, limit=5)
            analysis['related_tasks'] = history
        
        return analysis
    
    def _get_context_specific_musts(self, context_analysis: Dict[str, Any]) -> List[str]:
        """Genera requisitos específicos basados en el contexto."""
        musts = []
        
        # Si hay tareas relacionadas, asegurar consistencia
        if context_analysis.get('related_tasks'):
            musts.append("Mantener consistencia con tareas relacionadas anteriores")
        
        # Si hay múltiples fuentes, asegurar cobertura
        if len(context_analysis.get('source_ids', [])) > 2:
            musts.append("Sintetizar información de múltiples fuentes")
        
        return musts
    
    def render_system_prompt(self, contract: TaskContract) -> str:
        """
        Renderiza el contrato como prompt del sistema.
        
        Args:
            contract: Contrato de tarea
            
        Returns:
            Prompt del sistema formateado
        """
        musts_formatted = "\n".join(f"- {must}" for must in contract.musts)
        
        prompt = f"""# Contrato de Tarea

**ID:** {contract.id}
**Tipo:** {contract.task_type.value}
**Objetivo:** {contract.goal}
**Nivel de Riesgo:** {contract.risk_level.value}
**Requiere Aprobación Humana:** {'Sí' if contract.human_approval_required else 'No'}

## Requisitos Obligatorios
{musts_formatted}

## Formato de Salida
{contract.format}

## Métricas Objetivo
{json.dumps(contract.metrics, indent=2, ensure_ascii=False)}

## Archivos Afectados
{', '.join(contract.files_affected) if contract.files_affected else 'Ninguno especificado'}

## Fuentes de Contexto
{', '.join(contract.context_sources) if contract.context_sources else 'Contexto general'}

**IMPORTANTE:** Cumple estrictamente con este contrato. Si no puedes cumplir algún requisito, indícalo explícitamente."""
        
        return prompt
    
    async def validate_contract_compliance(self, 
                                         response: str, 
                                         contract: TaskContract) -> ContractValidation:
        """
        Valida el cumplimiento de un contrato.
        
        Args:
            response: Respuesta generada
            contract: Contrato original
            
        Returns:
            ContractValidation con resultados
        """
        violations = []
        recommendations = []
        score = 1.0
        
        # Verificar requisitos obligatorios
        for must in contract.musts:
            if not self._check_requirement_compliance(response, must):
                violations.append(f"No cumple: {must}")
                score -= 0.1
        
        # Verificar formato
        if not self._check_format_compliance(response, contract.format):
            violations.append("No cumple formato especificado")
            score -= 0.2
        
        # Verificar cobertura de fuentes
        source_coverage = self._calculate_source_coverage(response, contract.context_sources)
        if source_coverage < self.config['min_source_coverage']:
            violations.append(f"Cobertura de fuentes insuficiente: {source_coverage:.2f}")
            score -= 0.15
        
        # Verificar relevancia de contexto
        context_relevance = self._calculate_context_relevance(response, contract)
        if context_relevance < 0.7:
            violations.append(f"Relevancia de contexto baja: {context_relevance:.2f}")
            score -= 0.1
        
        # Generar recomendaciones
        if violations:
            recommendations = self._generate_recommendations(violations, contract)
        
        return ContractValidation(
            is_valid=score >= 0.8,
            score=max(0.0, score),
            violations=violations,
            recommendations=recommendations,
            source_coverage=source_coverage,
            context_relevance=context_relevance
        )
    
    def _check_requirement_compliance(self, response: str, requirement: str) -> bool:
        """Verifica si la respuesta cumple un requisito específico."""
        response_lower = response.lower()
        
        # Verificaciones específicas por tipo de requisito
        if "fuentes" in requirement.lower():
            return "fuentes" in response_lower or "sources" in response_lower
        elif "pasos" in requirement.lower():
            return any(marker in response_lower for marker in ["1.", "paso", "step"])
        elif "código" in requirement.lower():
            return "```" in response or "`" in response
        elif "comentarios" in requirement.lower():
            return "#" in response or "//" in response
        
        # Verificación general
        return True
    
    def _check_format_compliance(self, response: str, format_spec: str) -> bool:
        """Verifica si la respuesta cumple el formato especificado."""
        if "markdown" in format_spec.lower():
            return "#" in response or "**" in response or "[" in response
        elif "código" in format_spec.lower():
            return "```" in response
        elif "numerados" in format_spec.lower():
            return any(f"{i}." in response for i in range(1, 10))
        
        return True
    
    def _calculate_source_coverage(self, response: str, context_sources: List[str]) -> float:
        """Calcula la cobertura de fuentes en la respuesta."""
        if not context_sources:
            return 1.0
        
        mentioned_sources = 0
        for source in context_sources:
            if source.lower() in response.lower():
                mentioned_sources += 1
        
        return mentioned_sources / len(context_sources)
    
    def _calculate_context_relevance(self, response: str, contract: TaskContract) -> float:
        """Calcula la relevancia del contexto en la respuesta."""
        # Implementación simplificada - en producción usar embeddings
        query_terms = contract.goal.lower().split()
        response_terms = response.lower().split()
        
        common_terms = set(query_terms) & set(response_terms)
        return len(common_terms) / len(query_terms) if query_terms else 0.0
    
    def _generate_recommendations(self, violations: List[str], contract: TaskContract) -> List[str]:
        """Genera recomendaciones para mejorar el cumplimiento."""
        recommendations = []
        
        for violation in violations:
            if "fuentes" in violation.lower():
                recommendations.append("Agregar sección 'Fuentes' con referencias específicas")
            elif "formato" in violation.lower():
                recommendations.append(f"Usar formato: {contract.format}")
            elif "cobertura" in violation.lower():
                recommendations.append("Incluir más referencias a las fuentes de contexto")
        
        return recommendations
    
    def get_contract(self, contract_id: str) -> Optional[TaskContract]:
        """Obtiene un contrato activo por ID."""
        return self.active_contracts.get(contract_id)
    
    def list_active_contracts(self) -> List[TaskContract]:
        """Lista todos los contratos activos."""
        return list(self.active_contracts.values())
    
    def expire_contract(self, contract_id: str) -> bool:
        """Expira un contrato activo."""
        if contract_id in self.active_contracts:
            del self.active_contracts[contract_id]
            return True
        return False


# Funciones de conveniencia para integración con Agent
async def build_task_contract(query: str,
                            user_role: str = "developer",
                            risk_level: Optional[RiskLevel] = None,
                            context_manager: Optional[ContextManager] = None,
                            human_loop_manager: Optional[HumanLoopManager] = None) -> TaskContract:
    """
    Función de conveniencia para generar contratos de tarea.
    
    Args:
        query: Consulta del usuario
        user_role: Rol del usuario
        risk_level: Nivel de riesgo
        context_manager: Gestor de contexto
        human_loop_manager: Gestor de human-in-the-loop
        
    Returns:
        TaskContract generado
    """
    spec_layer = SpecLayer(
        context_manager=context_manager or ContextManager(),
        human_loop_manager=human_loop_manager
    )
    
    return await spec_layer.build_task_contract(
        query=query,
        user_role=user_role,
        risk_level=risk_level
    )


def render_system_prompt(contract: TaskContract) -> str:
    """
    Función de conveniencia para renderizar prompts del sistema.
    
    Args:
        contract: Contrato de tarea
        
    Returns:
        Prompt del sistema formateado
    """
    spec_layer = SpecLayer(ContextManager())
    return spec_layer.render_system_prompt(contract)


async def validate_contract_compliance(response: str, contract: TaskContract) -> ContractValidation:
    """
    Función de conveniencia para validar cumplimiento de contratos.
    
    Args:
        response: Respuesta generada
        contract: Contrato original
        
    Returns:
        ContractValidation con resultados
    """
    spec_layer = SpecLayer(ContextManager())
    return await spec_layer.validate_contract_compliance(response, contract)
