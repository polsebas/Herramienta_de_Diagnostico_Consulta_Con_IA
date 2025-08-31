"""
Advanced Contract Generation Module - PR-F

Este módulo implementa un sistema inteligente de generación de contratos que reemplaza
el sistema basado en reglas simples con:

- Clasificador ML para detección de tipos de tarea
- Templates adaptativos por tipo de proyecto
- Motor avanzado de evaluación de riesgo
- Sistema de aprendizaje continuo con feedback

Componentes principales:
- IntelligentTaskClassifier: Clasificación ML con contexto
- AdaptiveTemplateEngine: Templates dinámicos
- AdvancedRiskEngine: Evaluación multi-dimensional de riesgo
- ContractLearningSystem: Aprendizaje continuo
"""

from .intelligent_classifier import IntelligentTaskClassifier, TaskTypeAdvanced
from .adaptive_templates import AdaptiveTemplateEngine, ProjectProfiler
from .risk_engine import AdvancedRiskEngine, RiskAssessment
from .learning_system import ContractLearningSystem, LearningUpdate
from .performance_optimizer import PerformanceOptimizer
from .advanced_generator import AdvancedContractGenerator, create_advanced_contract_generator

__all__ = [
    "IntelligentTaskClassifier",
    "TaskTypeAdvanced", 
    "AdaptiveTemplateEngine",
    "ProjectProfiler",
    "AdvancedRiskEngine",
    "RiskAssessment",
    "ContractLearningSystem",
    "LearningUpdate",
    "PerformanceOptimizer",
    "AdvancedContractGenerator",
    "create_advanced_contract_generator"
]

__version__ = "1.0.0"
