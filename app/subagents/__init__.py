"""
Subagentes para el sistema RAG de diagnóstico con IA.

Este módulo implementa la arquitectura de subagentes especializados:
- RetrievalSubAgent: Recuperación híbrida de información
- AnalysisSubAgent: Análisis y clasificación de chunks
- SynthesisSubAgent: Síntesis de respuestas
- VerificationSubAgent: Verificación de calidad y cumplimiento
"""

from .retrieval import RetrievalSubAgent
from .analysis import AnalysisSubAgent
from .synthesis import SynthesisSubAgent
from .verification import VerificationSubAgent

__all__ = [
    "RetrievalSubAgent",
    "AnalysisSubAgent", 
    "SynthesisSubAgent",
    "VerificationSubAgent"
]
