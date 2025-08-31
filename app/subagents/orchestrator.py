"""
Orquestador de Subagentes

Este módulo implementa el pipeline completo de subagentes que coordina:
- RetrievalSubAgent: Búsqueda híbrida inteligente
- AnalysisSubAgent: Análisis de contenido y detección de gaps
- SynthesisSubAgent: Generación de respuestas con contratos
- VerificationSubAgent: Verificación automática de calidad
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import time
from pathlib import Path

from .retrieval import RetrievalSubAgent
from .analysis import AnalysisSubAgent
from .synthesis import SynthesisSubAgent
from .verification import VerificationSubAgent
from ..spec_layer import TaskContract, build_task_contract
from ..context_manager import ContextManager
from ..retrieval import HybridRetriever, SearchResult, SearchFilters

logger = logging.getLogger(__name__)

@dataclass
class PipelineResult:
    """Resultado del pipeline completo de subagentes."""
    query: str
    contract: TaskContract
    retrieved_chunks: List[SearchResult]
    analysis: Dict[str, Any]
    synthesis: str
    verification: Dict[str, Any]
    final_response: str
    pipeline_metrics: Dict[str, Any]
    execution_time: float
    success: bool
    errors: List[str]

@dataclass
class PipelineConfig:
    """Configuración del pipeline de subagentes."""
    enable_verification: bool = True
    max_retrieval_chunks: int = 20
    max_analysis_chunks: int = 10
    synthesis_max_tokens: int = 2000
    verification_threshold: float = 0.8
    enable_fallback: bool = True
    max_retries: int = 3
    timeout_seconds: int = 30

class SubagentOrchestrator:
    """
    Orquestador principal que coordina todos los subagentes en un pipeline completo.
    """
    
    def __init__(self, 
                 hybrid_retriever: HybridRetriever,
                 context_manager: ContextManager,
                 config: Optional[PipelineConfig] = None):
        """
        Inicializa el orquestador de subagentes.
        
        Args:
            hybrid_retriever: Retriever híbrido para búsquedas
            context_manager: Gestor de contexto para optimización
            config: Configuración del pipeline
        """
        self.config = config or PipelineConfig()
        self.hybrid_retriever = hybrid_retriever
        self.context_manager = context_manager
        
        # Inicializar subagentes
        self.retrieval_agent = RetrievalSubAgent(hybrid_retriever)
        self.analysis_agent = AnalysisSubAgent()
        self.synthesis_agent = SynthesisSubAgent()
        self.verification_agent = VerificationSubAgent()
        
        # Métricas del pipeline
        self.pipeline_metrics = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "avg_execution_time": 0.0,
            "avg_retrieval_chunks": 0.0,
            "avg_verification_score": 0.0,
            "verification_failures": 0,
            "last_execution": None
        }
        
        logger.info("SubagentOrchestrator inicializado")
    
    async def process_query(self, 
                           query: str, 
                           user_role: str = "developer",
                           risk_level: str = "medium",
                           context_filters: Optional[Dict[str, Any]] = None) -> PipelineResult:
        """
        Procesa una consulta completa a través del pipeline de subagentes.
        
        Args:
            query: Consulta del usuario
            user_role: Rol del usuario para el contrato
            risk_level: Nivel de riesgo para el contrato
            context_filters: Filtros adicionales para el contexto
        
        Returns:
            Resultado completo del pipeline
        """
        start_time = time.time()
        pipeline_result = PipelineResult(
            query=query,
            contract=None,
            retrieved_chunks=[],
            analysis={},
            synthesis="",
            verification={},
            final_response="",
            pipeline_metrics={},
            execution_time=0.0,
            success=False,
            errors=[]
        )
        
        try:
            logger.info(f"Iniciando pipeline para consulta: '{query[:50]}...'")
            
            # 1. GENERAR CONTRATO DE TAREA
            logger.info("Paso 1: Generando contrato de tarea...")
            # build_task_contract es async y espera RiskLevel o None; dejamos que infiera el riesgo
            contract = await build_task_contract(query=query, user_role=user_role, risk_level=None)
            pipeline_result.contract = contract
            
            # 2. RETRIEVAL - Búsqueda híbrida
            logger.info("Paso 2: Ejecutando búsqueda híbrida...")
            retrieved_chunks = await self._execute_retrieval(query, contract, context_filters)
            pipeline_result.retrieved_chunks = retrieved_chunks
            
            if not retrieved_chunks:
                raise Exception("No se encontraron chunks relevantes para la consulta")
            
            # 3. ANÁLISIS - Clasificación y detección de gaps
            logger.info("Paso 3: Analizando contenido recuperado...")
            analysis = await self._execute_analysis(retrieved_chunks, contract)
            pipeline_result.analysis = analysis
            
            # 4. SÍNTESIS - Generación de respuesta
            logger.info("Paso 4: Generando respuesta...")
            synthesis = await self._execute_synthesis(query, contract, analysis, retrieved_chunks)
            pipeline_result.synthesis = synthesis
            
            # 5. VERIFICACIÓN - Control de calidad
            if self.config.enable_verification:
                logger.info("Paso 5: Verificando calidad de respuesta...")
                verification = await self._execute_verification(synthesis, contract, retrieved_chunks)
                pipeline_result.verification = verification
                
                # Si la verificación falla, intentar revisión
                if verification.get("overall_score", 0) < self.config.verification_threshold:
                    logger.warning("Verificación falló, intentando revisión...")
                    synthesis = await self._execute_revision(synthesis, verification, contract, retrieved_chunks)
                    pipeline_result.synthesis = synthesis
                    
                    # Verificación final
                    verification = await self._execute_verification(synthesis, contract, retrieved_chunks)
                    pipeline_result.verification = verification
            
            # 6. RESPUESTA FINAL
            pipeline_result.final_response = synthesis
            pipeline_result.success = True
            
            # 7. ACTUALIZAR CONTEXTO
            await self._update_context(query, retrieved_chunks, synthesis)
            
            # 8. CALCULAR MÉTRICAS
            execution_time = time.time() - start_time
            pipeline_result.execution_time = execution_time
            pipeline_result.pipeline_metrics = self._calculate_pipeline_metrics(
                execution_time, len(retrieved_chunks), 
                pipeline_result.verification.get("overall_score", 0)
            )
            
            # 9. ACTUALIZAR MÉTRICAS GLOBALES
            self._update_global_metrics(pipeline_result)
            
            logger.info(f"Pipeline completado exitosamente en {execution_time:.2f}s")
            return pipeline_result
            
        except Exception as e:
            error_msg = f"Error en pipeline: {str(e)}"
            logger.error(error_msg)
            pipeline_result.errors.append(error_msg)
            pipeline_result.success = False
            pipeline_result.execution_time = time.time() - start_time
            
            # Intentar fallback si está habilitado
            if self.config.enable_fallback:
                logger.info("Intentando fallback...")
                try:
                    fallback_response = await self._execute_fallback(query, contract)
                    pipeline_result.final_response = fallback_response
                    pipeline_result.success = True
                    logger.info("Fallback ejecutado exitosamente")
                except Exception as fallback_error:
                    logger.error(f"Fallback también falló: {fallback_error}")
                    pipeline_result.errors.append(f"Fallback falló: {str(fallback_error)}")
            
            return pipeline_result
    
    async def _execute_retrieval(self, 
                                query: str, 
                                contract: TaskContract,
                                context_filters: Optional[Dict[str, Any]] = None) -> List[SearchResult]:
        """Ejecuta la fase de retrieval."""
        try:
            # Aplicar filtros del contrato
            filters = SearchFilters(
                min_score=0.5,
                max_results=self.config.max_retrieval_chunks
            )
            
            # Agregar filtros de contexto si se especifican
            if context_filters:
                if "doc_type" in context_filters:
                    filters.doc_type = context_filters["doc_type"]
                if "section" in context_filters:
                    filters.section = context_filters["section"]
                if "min_date" in context_filters:
                    filters.min_date = context_filters["min_date"]
            
            # Ejecutar búsqueda híbrida
            results = self.hybrid_retriever.search(
                query=query,
                filters=filters,
                top_k=self.config.max_retrieval_chunks
            )
            
            logger.info(f"Retrieval completado: {len(results)} chunks encontrados")
            return results
            
        except Exception as e:
            logger.error(f"Error en retrieval: {e}")
            raise
    
    async def _execute_analysis(self, 
                               chunks: List[SearchResult], 
                               contract: TaskContract) -> Dict[str, Any]:
        """Ejecuta la fase de análisis."""
        try:
            # Preparar chunks para análisis
            chunk_data = []
            for chunk in chunks:
                # Soportar resultados como objetos o dicts
                if isinstance(chunk, dict):
                    cid = chunk.get("id", "")
                    text = chunk.get("text", "")
                    metadata = chunk.get("metadata", {})
                    score = chunk.get("score", 0.0)
                    source = chunk.get("source", "")
                else:
                    cid = getattr(chunk, "id", "")
                    text = getattr(chunk, "text", "")
                    metadata = getattr(chunk, "metadata", {})
                    score = getattr(chunk, "score", 0.0)
                    source = getattr(chunk, "source", "")

                chunk_data.append({
                    "id": cid,
                    "text": text,
                    "metadata": metadata,
                    "score": score,
                    "source": source
                })
            
            # Ejecutar análisis
            # Pasar la consulta (usamos el objetivo del contrato como representación)
            analysis = self.analysis_agent.analyze(chunk_data, contract.goal)
            
            # Agregar información del contrato
            analysis["contract_requirements"] = {
                "goal": contract.goal,
                "musts": contract.musts,
                "format": contract.format,
                "metrics": contract.metrics
            }
            
            logger.info(f"Análisis completado: {len(analysis.get('clusters', []))} clusters identificados")
            return analysis
            
        except Exception as e:
            logger.error(f"Error en análisis: {e}")
            raise
    
    async def _execute_synthesis(self, 
                                query: str, 
                                contract: TaskContract,
                                analysis: Dict[str, Any],
                                chunks: List[SearchResult]) -> str:
        """Ejecuta la fase de síntesis."""
        try:
            # Preparar contexto para síntesis
            context = {
                "query": query,
                "contract": contract,
                "analysis": analysis,
                "chunks": chunks,
                "max_tokens": self.config.synthesis_max_tokens
            }
            
            # Ejecutar síntesis
            synthesis = await self.synthesis_agent.write(context)
            
            logger.info(f"Síntesis completada: {len(synthesis)} caracteres generados")
            return synthesis
            
        except Exception as e:
            logger.error(f"Error en síntesis: {e}")
            raise
    
    async def _execute_verification(self, 
                                   synthesis: str, 
                                   contract: TaskContract,
                                   chunks: List[SearchResult]) -> Dict[str, Any]:
        """Ejecuta la fase de verificación."""
        try:
            # Preparar contexto para verificación
            context = {
                "synthesis": synthesis,
                "contract": contract,
                "chunks": chunks,
                "threshold": self.config.verification_threshold
            }
            
            # Ejecutar verificación completa
            verification = await self.verification_agent.comprehensive_verification(context)
            
            logger.info(f"Verificación completada: score {verification.get('overall_score', 0):.2f}")
            return verification
            
        except Exception as e:
            logger.error(f"Error en verificación: {e}")
            raise
    
    async def _execute_revision(self, 
                               synthesis: str, 
                               verification: Dict[str, Any],
                               contract: TaskContract,
                               chunks: List[SearchResult]) -> str:
        """Ejecuta la fase de revisión basada en verificación fallida."""
        try:
            # Preparar feedback para revisión
            feedback = {
                "original_synthesis": synthesis,
                "verification_results": verification,
                "contract": contract,
                "chunks": chunks,
                "max_tokens": self.config.synthesis_max_tokens
            }
            
            # Ejecutar revisión
            revised_synthesis = await self.synthesis_agent.revise(feedback)
            
            logger.info(f"Revisión completada: {len(revised_synthesis)} caracteres")
            return revised_synthesis
            
        except Exception as e:
            logger.error(f"Error en revisión: {e}")
            raise
    
    async def _execute_fallback(self, 
                               query: str, 
                               contract: TaskContract) -> str:
        """Ejecuta respuesta de fallback cuando falla el pipeline principal."""
        try:
            # Respuesta de fallback simple
            fallback_response = f"""
# Respuesta de Fallback

No se pudo procesar completamente tu consulta: **{query}**

## Estado del Sistema
- ❌ Pipeline principal falló
- ⚠️ Usando respuesta de fallback
- 🔄 Reintenta en unos momentos

## Contrato de Tarea
**Objetivo**: {contract.goal}
**Requisitos**: {', '.join(contract.musts[:3])}

## Próximos Pasos
1. Verifica que el sistema esté funcionando
2. Reintenta la consulta
3. Si el problema persiste, contacta al equipo técnico

---
*Respuesta generada automáticamente por el sistema de fallback*
            """.strip()
            
            return fallback_response
            
        except Exception as e:
            logger.error(f"Error en fallback: {e}")
            return f"Error crítico del sistema: {str(e)}"
    
    async def _update_context(self, 
                             query: str, 
                             chunks: List[SearchResult], 
                             synthesis: str):
        """Actualiza el contexto del sistema."""
        try:
            # Crear resumen del turno
            turn_summary = {
                "query": query,
                "chunks_retrieved": len(chunks),
                "synthesis_length": len(synthesis),
                "timestamp": datetime.now().isoformat()
            }
            
            # Actualizar contexto
            await self.context_manager.add_turn(turn_summary)
            
            logger.info("Contexto actualizado exitosamente")
            
        except Exception as e:
            logger.warning(f"No se pudo actualizar contexto: {e}")
    
    def _calculate_pipeline_metrics(self, 
                                   execution_time: float, 
                                   chunks_count: int, 
                                   verification_score: float) -> Dict[str, Any]:
        """Calcula métricas del pipeline."""
        return {
            "execution_time": execution_time,
            "chunks_retrieved": chunks_count,
            "verification_score": verification_score,
            "pipeline_efficiency": chunks_count / max(execution_time, 0.1),
            "quality_score": verification_score * 0.8 + (1.0 / max(execution_time, 0.1)) * 0.2
        }
    
    def _update_global_metrics(self, result: PipelineResult):
        """Actualiza métricas globales del pipeline."""
        try:
            self.pipeline_metrics["total_queries"] += 1
            
            if result.success:
                self.pipeline_metrics["successful_queries"] += 1
            else:
                self.pipeline_metrics["failed_queries"] += 1
            
            # Actualizar métricas promedio
            current_avg = self.pipeline_metrics["avg_execution_time"]
            total_queries = self.pipeline_metrics["total_queries"]
            new_avg = (current_avg * (total_queries - 1) + result.execution_time) / total_queries
            self.pipeline_metrics["avg_execution_time"] = new_avg
            
            # Actualizar métricas de chunks
            current_chunks_avg = self.pipeline_metrics["avg_retrieval_chunks"]
            new_chunks_avg = (current_chunks_avg * (total_queries - 1) + len(result.retrieved_chunks)) / total_queries
            self.pipeline_metrics["avg_retrieval_chunks"] = new_chunks_avg
            
            # Actualizar métricas de verificación
            if result.verification:
                verification_score = result.verification.get("overall_score", 0)
                current_verif_avg = self.pipeline_metrics["avg_verification_score"]
                new_verif_avg = (current_verif_avg * (total_queries - 1) + verification_score) / total_queries
                self.pipeline_metrics["avg_verification_score"] = new_verif_avg
                
                if verification_score < self.config.verification_threshold:
                    self.pipeline_metrics["verification_failures"] += 1
            
            self.pipeline_metrics["last_execution"] = datetime.now().isoformat()
            
        except Exception as e:
            logger.error(f"Error actualizando métricas globales: {e}")
    
    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas del pipeline."""
        return {
            "config": self.config,
            "metrics": self.pipeline_metrics.copy(),
            "subagents": {
                "retrieval": self.retrieval_agent.get_stats(),
                "analysis": self.analysis_agent.get_stats(),
                "synthesis": self.synthesis_agent.get_stats(),
                "verification": self.verification_agent.get_stats()
            }
        }
    
    def update_config(self, new_config: PipelineConfig):
        """Actualiza la configuración del pipeline."""
        self.config = new_config
        logger.info("Configuración del pipeline actualizada")
    
    async def health_check(self) -> Dict[str, Any]:
        """Verifica el estado de salud del pipeline."""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {}
        }
        
        try:
            # Verificar retriever
            retriever_stats = self.hybrid_retriever.get_search_stats()
            health_status["components"]["retriever"] = {
                "status": "healthy" if retriever_stats["vector_store_available"] else "degraded",
                "vector_store": retriever_stats["vector_store_available"],
                "bm25_index": retriever_stats["bm25_index_available"]
            }
            
            # Verificar context manager
            context_stats = self.context_manager.get_stats()
            health_status["components"]["context_manager"] = {
                "status": "healthy",
                "total_queries": context_stats.get("total_queries", 0),
                "avg_compression": context_stats.get("avg_compression", 0.0)
            }
            
            # Verificar métricas del pipeline
            pipeline_stats = self.get_pipeline_stats()
            health_status["components"]["pipeline"] = {
                "status": "healthy",
                "total_queries": pipeline_stats["metrics"]["total_queries"],
                "success_rate": (
                    pipeline_stats["metrics"]["successful_queries"] / 
                    max(pipeline_stats["metrics"]["total_queries"], 1)
                )
            }
            
            # Determinar estado general
            all_healthy = all(
                comp["status"] == "healthy" 
                for comp in health_status["components"].values()
            )
            
            if not all_healthy:
                health_status["status"] = "degraded"
            
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
            logger.error(f"Error en health check: {e}")
        
        return health_status
    
    def clear_metrics(self):
        """Limpia las métricas del pipeline."""
        self.pipeline_metrics = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "avg_execution_time": 0.0,
            "avg_retrieval_chunks": 0.0,
            "avg_verification_score": 0.0,
            "verification_failures": 0,
            "last_execution": None
        }
        logger.info("Métricas del pipeline limpiadas")
