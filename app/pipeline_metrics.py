"""
Métricas del Pipeline de Subagentes

Este módulo implementa un sistema de métricas integrado que conecta el pipeline
de subagentes con el Context Manager para monitoreo completo del rendimiento.
"""

import logging
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import asyncio

from .context_manager import ContextManager
from .context_logger import ContextLogger

logger = logging.getLogger(__name__)

@dataclass
class PipelineMetrics:
    """Métricas del pipeline de subagentes."""
    timestamp: str
    query_id: str
    query: str
    execution_time: float
    success: bool
    subagent_metrics: Dict[str, Any]
    verification_score: float
    chunks_retrieved: int
    context_compression: float
    quality_score: float
    errors: List[str]

@dataclass
class PipelinePerformance:
    """Rendimiento agregado del pipeline."""
    total_queries: int
    successful_queries: int
    failed_queries: int
    avg_execution_time: float
    avg_verification_score: float
    avg_quality_score: float
    success_rate: float
    avg_chunks_retrieved: float
    avg_context_compression: float
    performance_trend: List[Dict[str, Any]]

class PipelineMetricsManager:
    """
    Gestor de métricas del pipeline que integra con el Context Manager.
    """
    
    def __init__(self, context_manager: ContextManager, context_logger: ContextLogger):
        """
        Inicializa el gestor de métricas del pipeline.
        
        Args:
            context_manager: Gestor de contexto para métricas de tokens
            context_logger: Logger de contexto para almacenamiento
        """
        self.context_manager = context_manager
        self.context_logger = context_logger
        
        # Directorio para métricas del pipeline
        self.metrics_dir = Path("logs/pipeline_metrics")
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        
        # Archivo de métricas del pipeline
        self.pipeline_metrics_file = self.metrics_dir / "pipeline_metrics.jsonl"
        
        # Cache de métricas en memoria
        self.metrics_cache = []
        self.cache_max_size = 1000
        
        # Configuración de alertas
        self.alert_thresholds = {
            "execution_time": 10.0,      # segundos
            "verification_score": 0.7,   # score mínimo
            "success_rate": 0.9,         # tasa de éxito mínima
            "context_compression": 0.3   # compresión mínima
        }
        
        logger.info("PipelineMetricsManager inicializado")
    
    async def record_pipeline_execution(self, pipeline_result: Any) -> bool:
        """
        Registra la ejecución de un pipeline completo.
        
        Args:
            pipeline_result: Resultado del pipeline (PipelineResult)
        
        Returns:
            True si se registró exitosamente
        """
        try:
            # Extraer métricas del resultado del pipeline
            metrics = PipelineMetrics(
                timestamp=datetime.now().isoformat(),
                query_id=self._generate_query_id(pipeline_result.query),
                query=pipeline_result.query[:100],  # Limitar longitud
                execution_time=pipeline_result.execution_time,
                success=pipeline_result.success,
                subagent_metrics=pipeline_result.pipeline_metrics,
                verification_score=pipeline_result.verification.get("overall_score", 0.0),
                chunks_retrieved=len(pipeline_result.retrieved_chunks),
                context_compression=0.0,  # Se calculará después
                quality_score=0.0,        # Se calculará después
                errors=pipeline_result.errors
            )
            
            # Calcular métricas adicionales
            await self._calculate_additional_metrics(metrics, pipeline_result)
            
            # Registrar métricas
            await self._store_metrics(metrics)
            
            # Verificar alertas
            await self._check_alerts(metrics)
            
            # Actualizar métricas del contexto
            await self._update_context_metrics(metrics)
            
            logger.info(f"Métricas del pipeline registradas para query {metrics.query_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error registrando métricas del pipeline: {e}")
            return False
    
    async def _calculate_additional_metrics(self, metrics: PipelineMetrics, 
                                          pipeline_result: Any):
        """Calcula métricas adicionales del pipeline."""
        try:
            # Calcular compresión del contexto
            if hasattr(pipeline_result, 'retrieved_chunks') and pipeline_result.retrieved_chunks:
                total_chunks_text = sum(len(chunk.text) for chunk in pipeline_result.retrieved_chunks)
                synthesis_length = len(pipeline_result.synthesis)
                
                if total_chunks_text > 0:
                    metrics.context_compression = synthesis_length / total_chunks_text
                else:
                    metrics.context_compression = 1.0
            
            # Calcular score de calidad general
            quality_factors = {
                "verification": metrics.verification_score,
                "success": 1.0 if metrics.success else 0.0,
                "compression": min(1.0, metrics.context_compression),
                "efficiency": 1.0 / max(metrics.execution_time, 0.1)
            }
            
            # Normalizar eficiencia (0-1)
            quality_factors["efficiency"] = min(1.0, quality_factors["efficiency"] / 10.0)
            
            # Score ponderado
            weights = {"verification": 0.4, "success": 0.3, "compression": 0.2, "efficiency": 0.1}
            metrics.quality_score = sum(
                quality_factors[key] * weights[key] for key in quality_factors
            )
            
        except Exception as e:
            logger.error(f"Error calculando métricas adicionales: {e}")
    
    async def _store_metrics(self, metrics: PipelineMetrics):
        """Almacena las métricas en archivo y cache."""
        try:
            # Convertir a diccionario
            metrics_dict = asdict(metrics)
            
            # Agregar al cache
            self.metrics_cache.append(metrics_dict)
            
            # Limpiar cache si es muy grande
            if len(self.metrics_cache) > self.cache_max_size:
                self.metrics_cache = self.metrics_cache[-self.cache_max_size:]
            
            # Escribir a archivo
            with open(self.pipeline_metrics_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(metrics_dict, ensure_ascii=False) + '\n')
            
        except Exception as e:
            logger.error(f"Error almacenando métricas: {e}")
    
    async def _check_alerts(self, metrics: PipelineMetrics):
        """Verifica si se deben generar alertas."""
        try:
            alerts = []
            
            # Alerta por tiempo de ejecución
            if metrics.execution_time > self.alert_thresholds["execution_time"]:
                alerts.append({
                    "type": "execution_time",
                    "severity": "warning",
                    "message": f"Pipeline lento: {metrics.execution_time:.2f}s",
                    "threshold": self.alert_thresholds["execution_time"]
                })
            
            # Alerta por score de verificación bajo
            if metrics.verification_score < self.alert_thresholds["verification_score"]:
                alerts.append({
                    "type": "verification_score",
                    "severity": "error",
                    "message": f"Score de verificación bajo: {metrics.verification_score:.2f}",
                    "threshold": self.alert_thresholds["verification_score"]
                })
            
            # Alerta por fallo del pipeline
            if not metrics.success:
                alerts.append({
                    "type": "pipeline_failure",
                    "severity": "error",
                    "message": f"Pipeline falló: {', '.join(metrics.errors[:3])}",
                    "threshold": "N/A"
                })
            
            # Alerta por compresión de contexto baja
            if metrics.context_compression < self.alert_thresholds["context_compression"]:
                alerts.append({
                    "type": "context_compression",
                    "severity": "warning",
                    "message": f"Compresión de contexto baja: {metrics.context_compression:.2f}",
                    "threshold": self.alert_thresholds["context_compression"]
                })
            
            # Registrar alertas si las hay
            if alerts:
                await self.context_logger.log_alerts(alerts)
                logger.warning(f"Generadas {len(alerts)} alertas para query {metrics.query_id}")
            
        except Exception as e:
            logger.error(f"Error verificando alertas: {e}")
    
    async def _update_context_metrics(self, metrics: PipelineMetrics):
        """Actualiza métricas del contexto con información del pipeline."""
        try:
            # Crear métricas de contexto
            context_metrics = {
                "pipeline_execution_time": metrics.execution_time,
                "pipeline_success": metrics.success,
                "pipeline_verification_score": metrics.verification_score,
                "pipeline_quality_score": metrics.quality_score,
                "chunks_retrieved": metrics.chunks_retrieved,
                "context_compression": metrics.context_compression
            }
            
            # Actualizar contexto
            await self.context_manager.add_metrics(context_metrics)
            
        except Exception as e:
            logger.error(f"Error actualizando métricas del contexto: {e}")
    
    def _generate_query_id(self, query: str) -> str:
        """Genera un ID único para la consulta."""
        import hashlib
        query_hash = hashlib.md5(query.encode()).hexdigest()
        return f"query_{query_hash[:8]}_{int(datetime.now().timestamp())}"
    
    async def get_pipeline_performance(self, 
                                     time_window: Optional[timedelta] = None) -> PipelinePerformance:
        """
        Obtiene el rendimiento agregado del pipeline.
        
        Args:
            time_window: Ventana de tiempo para las métricas (por defecto: últimas 24h)
        
        Returns:
            Rendimiento agregado del pipeline
        """
        try:
            if time_window is None:
                time_window = timedelta(hours=24)
            
            # Filtrar métricas por ventana de tiempo
            cutoff_time = datetime.now() - time_window
            filtered_metrics = []
            
            for metric in self.metrics_cache:
                metric_time = datetime.fromisoformat(metric["timestamp"])
                if metric_time >= cutoff_time:
                    filtered_metrics.append(metric)
            
            if not filtered_metrics:
                return PipelinePerformance(
                    total_queries=0,
                    successful_queries=0,
                    failed_queries=0,
                    avg_execution_time=0.0,
                    avg_verification_score=0.0,
                    avg_quality_score=0.0,
                    success_rate=0.0,
                    avg_chunks_retrieved=0.0,
                    avg_context_compression=0.0,
                    performance_trend=[]
                )
            
            # Calcular métricas agregadas
            total_queries = len(filtered_metrics)
            successful_queries = sum(1 for m in filtered_metrics if m["success"])
            failed_queries = total_queries - successful_queries
            
            avg_execution_time = sum(m["execution_time"] for m in filtered_metrics) / total_queries
            avg_verification_score = sum(m["verification_score"] for m in filtered_metrics) / total_queries
            avg_quality_score = sum(m["quality_score"] for m in filtered_metrics) / total_queries
            avg_chunks_retrieved = sum(m["chunks_retrieved"] for m in filtered_metrics) / total_queries
            avg_context_compression = sum(m["context_compression"] for m in filtered_metrics) / total_queries
            
            success_rate = successful_queries / total_queries if total_queries > 0 else 0.0
            
            # Calcular tendencia de rendimiento
            performance_trend = self._calculate_performance_trend(filtered_metrics)
            
            return PipelinePerformance(
                total_queries=total_queries,
                successful_queries=successful_queries,
                failed_queries=failed_queries,
                avg_execution_time=avg_execution_time,
                avg_verification_score=avg_verification_score,
                avg_quality_score=avg_quality_score,
                success_rate=success_rate,
                avg_chunks_retrieved=avg_chunks_retrieved,
                avg_context_compression=avg_context_compression,
                performance_trend=performance_trend
            )
            
        except Exception as e:
            logger.error(f"Error obteniendo rendimiento del pipeline: {e}")
            return PipelinePerformance(
                total_queries=0,
                successful_queries=0,
                failed_queries=0,
                avg_execution_time=0.0,
                avg_verification_score=0.0,
                avg_quality_score=0.0,
                success_rate=0.0,
                avg_chunks_retrieved=0.0,
                avg_context_compression=0.0,
                performance_trend=[]
            )
    
    def _calculate_performance_trend(self, metrics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calcula la tendencia de rendimiento del pipeline."""
        try:
            # Agrupar métricas por hora
            hourly_metrics = {}
            
            for metric in metrics:
                metric_time = datetime.fromisoformat(metric["timestamp"])
                hour_key = metric_time.replace(minute=0, second=0, microsecond=0)
                
                if hour_key not in hourly_metrics:
                    hourly_metrics[hour_key] = []
                
                hourly_metrics[hour_key].append(metric)
            
            # Calcular métricas por hora
            trend = []
            for hour, hour_metrics in sorted(hourly_metrics.items()):
                if hour_metrics:
                    avg_quality = sum(m["quality_score"] for m in hour_metrics) / len(hour_metrics)
                    avg_time = sum(m["execution_time"] for m in hour_metrics) / len(hour_metrics)
                    success_count = sum(1 for m in hour_metrics if m["success"])
                    
                    trend.append({
                        "hour": hour.isoformat(),
                        "avg_quality_score": avg_quality,
                        "avg_execution_time": avg_time,
                        "success_count": success_count,
                        "total_queries": len(hour_metrics)
                    })
            
            return trend
            
        except Exception as e:
            logger.error(f"Error calculando tendencia de rendimiento: {e}")
            return []
    
    async def export_metrics(self, 
                            format: str = "json",
                            time_window: Optional[timedelta] = None) -> str:
        """
        Exporta métricas del pipeline en diferentes formatos.
        
        Args:
            format: Formato de exportación (json, csv)
            time_window: Ventana de tiempo para las métricas
        
        Returns:
            Ruta del archivo exportado
        """
        try:
            performance = await self.get_pipeline_performance(time_window)
            
            if format.lower() == "json":
                return await self._export_json(performance)
            elif format.lower() == "csv":
                return await self._export_csv(performance)
            else:
                raise ValueError(f"Formato no soportado: {format}")
                
        except Exception as e:
            logger.error(f"Error exportando métricas: {e}")
            raise
    
    async def _export_json(self, performance: PipelinePerformance) -> str:
        """Exporta métricas en formato JSON."""
        try:
            export_file = self.metrics_dir / f"pipeline_performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "performance": asdict(performance),
                "alert_thresholds": self.alert_thresholds
            }
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Métricas exportadas a JSON: {export_file}")
            return str(export_file)
            
        except Exception as e:
            logger.error(f"Error exportando JSON: {e}")
            raise
    
    async def _export_csv(self, performance: PipelinePerformance) -> str:
        """Exporta métricas en formato CSV."""
        try:
            import csv
            
            export_file = self.metrics_dir / f"pipeline_performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            with open(export_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Headers
                writer.writerow([
                    "Métrica", "Valor", "Descripción"
                ])
                
                # Datos principales
                writer.writerow(["Total Queries", performance.total_queries, "Total de consultas procesadas"])
                writer.writerow(["Successful Queries", performance.successful_queries, "Consultas exitosas"])
                writer.writerow(["Failed Queries", performance.failed_queries, "Consultas fallidas"])
                writer.writerow(["Success Rate", f"{performance.success_rate:.2%}", "Tasa de éxito"])
                writer.writerow(["Avg Execution Time", f"{performance.avg_execution_time:.2f}s", "Tiempo promedio de ejecución"])
                writer.writerow(["Avg Verification Score", f"{performance.avg_verification_score:.2f}", "Score promedio de verificación"])
                writer.writerow(["Avg Quality Score", f"{performance.avg_quality_score:.2f}", "Score promedio de calidad"])
                writer.writerow(["Avg Chunks Retrieved", f"{performance.avg_chunks_retrieved:.1f}", "Chunks promedio recuperados"])
                writer.writerow(["Avg Context Compression", f"{performance.avg_context_compression:.2f}", "Compresión promedio del contexto"])
            
            logger.info(f"Métricas exportadas a CSV: {export_file}")
            return str(export_file)
            
        except Exception as e:
            logger.error(f"Error exportando CSV: {e}")
            raise
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Retorna un resumen de las métricas del pipeline."""
        try:
            return {
                "metrics_file": str(self.pipeline_metrics_file),
                "cache_size": len(self.metrics_cache),
                "alert_thresholds": self.alert_thresholds,
                "last_metrics_count": len(self.metrics_cache[-100:]) if self.metrics_cache else 0
            }
        except Exception as e:
            logger.error(f"Error obteniendo resumen de métricas: {e}")
            return {"error": str(e)}
    
    def clear_metrics(self):
        """Limpia todas las métricas del pipeline."""
        try:
            self.metrics_cache.clear()
            
            # Limpiar archivo de métricas
            if self.pipeline_metrics_file.exists():
                self.pipeline_metrics_file.unlink()
            
            logger.info("Métricas del pipeline limpiadas")
            
        except Exception as e:
            logger.error(f"Error limpiando métricas: {e}")
    
    def update_alert_thresholds(self, new_thresholds: Dict[str, float]):
        """Actualiza los umbrales de alerta."""
        try:
            self.alert_thresholds.update(new_thresholds)
            logger.info(f"Umbrales de alerta actualizados: {new_thresholds}")
        except Exception as e:
            logger.error(f"Error actualizando umbrales de alerta: {e}")
