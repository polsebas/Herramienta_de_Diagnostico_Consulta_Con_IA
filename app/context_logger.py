"""
Logger Avanzado para el Context Manager

Este módulo proporciona funcionalidades avanzadas de logging:
- Rotación automática de archivos
- Análisis en tiempo real
- Alertas de rendimiento
- Exportación de métricas
"""

import json
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import threading
import time
from dataclasses import asdict
import statistics

logger = logging.getLogger(__name__)

class ContextLogger:
    """
    Logger avanzado para el Context Manager con funcionalidades de monitoreo.
    """
    
    def __init__(self, logs_dir: str = "logs", max_file_size: int = 10 * 1024 * 1024, 
                 backup_count: int = 5):
        """
        Inicializa el logger avanzado.
        
        Args:
            logs_dir: Directorio para los logs
            max_file_size: Tamaño máximo del archivo de log (bytes)
            backup_count: Número de archivos de backup a mantener
        """
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(exist_ok=True)
        
        # Configurar logger principal
        self.setup_logger(max_file_size, backup_count)
        
        # Configurar logger de estadísticas
        self.setup_stats_logger()
        
        # Configurar logger de alertas
        self.setup_alerts_logger()
        
        # Métricas en tiempo real
        self.real_time_metrics = {
            "total_queries": 0,
            "total_tokens_saved": 0,
            "avg_compression_ratio": 0.0,
            "avg_efficiency_score": 0.0,
            "last_update": datetime.now()
        }
        
        # Lock para thread safety
        self.metrics_lock = threading.Lock()
        
        # Iniciar thread de monitoreo
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        logger.info("ContextLogger inicializado")
    
    def setup_logger(self, max_file_size: int, backup_count: int):
        """Configura el logger principal con rotación de archivos."""
        # Logger principal
        main_logger = logging.getLogger("context_manager")
        main_logger.setLevel(logging.INFO)
        
        # Handler con rotación
        main_handler = logging.handlers.RotatingFileHandler(
            self.logs_dir / "context_manager.log",
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        
        # Formato del log
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        main_handler.setFormatter(formatter)
        
        # Agregar handler
        main_logger.addHandler(main_handler)
        
        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        main_logger.addHandler(console_handler)
        
        self.main_logger = main_logger
    
    def setup_stats_logger(self):
        """Configura el logger de estadísticas."""
        # Logger de estadísticas
        stats_logger = logging.getLogger("context_stats")
        stats_logger.setLevel(logging.INFO)
        
        # Handler para estadísticas
        stats_handler = logging.handlers.RotatingFileHandler(
            self.logs_dir / "context_stats.jsonl",
            maxBytes=50 * 1024 * 1024,  # 50MB
            backupCount=3,
            encoding='utf-8'
        )
        
        # Formato JSON
        stats_formatter = logging.Formatter('%(message)s')
        stats_handler.setFormatter(stats_formatter)
        
        # Agregar handler
        stats_logger.addHandler(stats_handler)
        
        self.stats_logger = stats_logger
    
    def setup_alerts_logger(self):
        """Configura el logger de alertas."""
        # Logger de alertas
        alerts_logger = logging.getLogger("context_alerts")
        alerts_logger.setLevel(logging.WARNING)
        
        # Handler para alertas
        alerts_handler = logging.handlers.RotatingFileHandler(
            self.logs_dir / "context_alerts.log",
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        
        # Formato de alertas
        alerts_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        alerts_handler.setFormatter(alerts_formatter)
        
        # Agregar handler
        alerts_logger.addHandler(alerts_handler)
        
        self.alerts_logger = alerts_logger
    
    def log_context_stats(self, stats: Dict[str, Any]):
        """
        Registra estadísticas de contexto.
        
        Args:
            stats: Estadísticas a registrar
        """
        try:
            # Log principal
            self.main_logger.info(
                f"Context stats: compression={stats.get('compression_ratio', 0):.2f}, "
                f"efficiency={stats.get('efficiency_score', 0):.2f}, "
                f"tokens_saved={stats.get('tokens_before', 0) - stats.get('tokens_after', 0)}"
            )
            
            # Log de estadísticas (JSON)
            self.stats_logger.info(json.dumps(stats, ensure_ascii=False))
            
            # Actualizar métricas en tiempo real
            self._update_real_time_metrics(stats)
            
            # Verificar alertas
            self._check_alerts(stats)
            
        except Exception as e:
            logger.error(f"Error al registrar estadísticas: {e}")
    
    def _update_real_time_metrics(self, stats: Dict[str, Any]):
        """Actualiza métricas en tiempo real."""
        with self.metrics_lock:
            self.real_time_metrics["total_queries"] += 1
            
            # Calcular tokens ahorrados
            tokens_saved = stats.get("tokens_before", 0) - stats.get("tokens_after", 0)
            self.real_time_metrics["total_tokens_saved"] += tokens_saved
            
            # Actualizar promedios
            current_compression = stats.get("compression_ratio", 0)
            current_efficiency = stats.get("efficiency_score", 0)
            
            # Promedio móvil simple
            total_queries = self.real_time_metrics["total_queries"]
            if total_queries == 1:
                self.real_time_metrics["avg_compression_ratio"] = current_compression
                self.real_time_metrics["avg_efficiency_score"] = current_efficiency
            else:
                # Promedio móvil ponderado (más peso a valores recientes)
                alpha = 0.1  # Factor de suavizado
                self.real_time_metrics["avg_compression_ratio"] = (
                    (1 - alpha) * self.real_time_metrics["avg_compression_ratio"] + 
                    alpha * current_compression
                )
                self.real_time_metrics["avg_efficiency_score"] = (
                    (1 - alpha) * self.real_time_metrics["avg_efficiency_score"] + 
                    alpha * current_efficiency
                )
            
            self.real_time_metrics["last_update"] = datetime.now()
    
    def _check_alerts(self, stats: Dict[str, Any]):
        """Verifica si se deben generar alertas."""
        alerts = []
        
        # Alerta por compresión baja
        if stats.get("compression_ratio", 1.0) > 0.9:
            alerts.append({
                "level": "WARNING",
                "message": f"Ratio de compresión alto: {stats.get('compression_ratio', 0):.2f}",
                "metric": "compression_ratio",
                "value": stats.get("compression_ratio", 0),
                "threshold": 0.9
            })
        
        # Alerta por eficiencia baja
        if stats.get("efficiency_score", 1.0) < 0.6:
            alerts.append({
                "level": "WARNING",
                "message": f"Score de eficiencia bajo: {stats.get('efficiency_score', 0):.2f}",
                "metric": "efficiency_score",
                "value": stats.get("efficiency_score", 0),
                "threshold": 0.6
            })
        
        # Alerta por uso excesivo del presupuesto
        if stats.get("budget_used", 0) > 0.95:
            alerts.append({
                "level": "WARNING",
                "message": f"Presupuesto de contexto casi agotado: {stats.get('budget_used', 0):.2f}",
                "metric": "budget_used",
                "value": stats.get("budget_used", 0),
                "threshold": 0.95
            })
        
        # Registrar alertas
        for alert in alerts:
            self.alerts_logger.warning(
                f"{alert['message']} | {alert['metric']}={alert['value']:.2f} | "
                f"threshold={alert['threshold']:.2f}"
            )
    
    def _monitoring_loop(self):
        """Loop de monitoreo en tiempo real."""
        while True:
            try:
                # Generar reporte de estado cada 5 minutos
                time.sleep(300)  # 5 minutos
                
                with self.metrics_lock:
                    if self.real_time_metrics["total_queries"] > 0:
                        self._generate_status_report()
                        
            except Exception as e:
                logger.error(f"Error en loop de monitoreo: {e}")
    
    def _generate_status_report(self):
        """Genera reporte de estado del sistema."""
        try:
            # Calcular métricas adicionales
            total_queries = self.real_time_metrics["total_queries"]
            total_tokens_saved = self.real_time_metrics["total_tokens_saved"]
            
            # Eficiencia general
            efficiency_score = self.real_time_metrics["avg_efficiency_score"]
            
            # Generar reporte
            report = {
                "timestamp": datetime.now().isoformat(),
                "status": "healthy" if efficiency_score >= 0.7 else "needs_attention",
                "metrics": {
                    "total_queries": total_queries,
                    "total_tokens_saved": total_tokens_saved,
                    "avg_compression_ratio": self.real_time_metrics["avg_compression_ratio"],
                    "avg_efficiency_score": efficiency_score,
                    "last_update": self.real_time_metrics["last_update"].isoformat()
                },
                "recommendations": self._generate_recommendations()
            }
            
            # Guardar reporte
            report_file = self.logs_dir / "status_report.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            # Log del reporte
            self.main_logger.info(
                f"Status report generated: {report['status']}, "
                f"efficiency={efficiency_score:.2f}, queries={total_queries}"
            )
            
        except Exception as e:
            logger.error(f"Error generando reporte de estado: {e}")
    
    def _generate_recommendations(self) -> List[str]:
        """Genera recomendaciones basadas en métricas en tiempo real."""
        recommendations = []
        
        efficiency_score = self.real_time_metrics["avg_efficiency_score"]
        compression_ratio = self.real_time_metrics["avg_compression_ratio"]
        
        if efficiency_score < 0.7:
            recommendations.append("La eficiencia del contexto es baja. Considera ajustar la configuración.")
        
        if compression_ratio > 0.8:
            recommendations.append("El ratio de compresión es alto. Revisa la estrategia de compactación.")
        
        if not recommendations:
            recommendations.append("El sistema está funcionando de manera óptima.")
        
        return recommendations
    
    def get_real_time_metrics(self) -> Dict[str, Any]:
        """Obtiene métricas en tiempo real."""
        with self.metrics_lock:
            return self.real_time_metrics.copy()
    
    def get_performance_summary(self, period_hours: int = 24) -> Dict[str, Any]:
        """
        Obtiene resumen de rendimiento del período especificado.
        
        Args:
            period_hours: Período en horas para analizar
        
        Returns:
            Resumen de rendimiento
        """
        try:
            # Cargar datos del archivo de estadísticas
            stats_file = self.logs_dir / "context_stats.jsonl"
            if not stats_file.exists():
                return {"error": "No hay datos disponibles"}
            
            data = []
            cutoff_time = datetime.now() - timedelta(hours=period_hours)
            
            with open(stats_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        record = json.loads(line)
                        record_time = datetime.fromisoformat(record['timestamp'])
                        if record_time >= cutoff_time:
                            data.append(record)
            
            if not data:
                return {"error": f"No hay datos en las últimas {period_hours} horas"}
            
            # Calcular métricas agregadas
            compression_ratios = [r.get('compression_ratio', 0) for r in data]
            efficiency_scores = [r.get('efficiency_score', 0) for r in data]
            tokens_saved = [r.get('tokens_before', 0) - r.get('tokens_after', 0) for r in data]
            
            summary = {
                "period_hours": period_hours,
                "total_queries": len(data),
                "avg_compression_ratio": statistics.mean(compression_ratios),
                "avg_efficiency_score": statistics.mean(efficiency_scores),
                "total_tokens_saved": sum(tokens_saved),
                "min_efficiency": min(efficiency_scores),
                "max_efficiency": max(efficiency_scores),
                "min_compression": min(compression_ratios),
                "max_compression": max(compression_ratios),
                "generated_at": datetime.now().isoformat()
            }
            
            return summary
            
        except Exception as e:
            return {"error": f"Error al generar resumen: {e}"}
    
    def export_metrics(self, output_format: str = "csv", period_hours: int = 24) -> str:
        """
        Exporta métricas en el formato especificado.
        
        Args:
            output_format: Formato de salida (csv, json, excel)
            period_hours: Período en horas para exportar
        
        Returns:
            Ruta del archivo exportado
        """
        try:
            # Cargar datos
            stats_file = self.logs_dir / "context_stats.jsonl"
            if not stats_file.exists():
                raise FileNotFoundError("No hay archivo de estadísticas disponible")
            
            data = []
            cutoff_time = datetime.now() - timedelta(hours=period_hours)
            
            with open(stats_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        record = json.loads(line)
                        record_time = datetime.fromisoformat(record['timestamp'])
                        if record_time >= cutoff_time:
                            data.append(record)
            
            if not data:
                raise ValueError(f"No hay datos en las últimas {period_hours} horas")
            
            # Generar nombre de archivo
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"context_metrics_{period_hours}h_{timestamp}"
            
            if output_format == "csv":
                import pandas as pd
                df = pd.DataFrame(data)
                output_file = self.logs_dir / f"{filename}.csv"
                df.to_csv(output_file, index=False, encoding='utf-8')
                
            elif output_format == "json":
                output_file = self.logs_dir / f"{filename}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                    
            elif output_format == "excel":
                import pandas as pd
                df = pd.DataFrame(data)
                output_file = self.logs_dir / f"{filename}.xlsx"
                df.to_excel(output_file, index=False, engine='openpyxl')
                
            else:
                raise ValueError(f"Formato no soportado: {output_format}")
            
            logger.info(f"Métricas exportadas a {output_file}")
            return str(output_file)
            
        except Exception as e:
            logger.error(f"Error exportando métricas: {e}")
            raise
    
    def cleanup_old_logs(self, days_to_keep: int = 30):
        """
        Limpia logs antiguos para liberar espacio.
        
        Args:
            days_to_keep: Días de logs a mantener
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            # Limpiar archivos de log antiguos
            for log_file in self.logs_dir.glob("*.log.*"):
                try:
                    file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                    if file_time < cutoff_date:
                        log_file.unlink()
                        logger.info(f"Archivo de log antiguo eliminado: {log_file}")
                except Exception as e:
                    logger.warning(f"No se pudo eliminar {log_file}: {e}")
            
            # Limpiar archivos de estadísticas antiguos
            for stats_file in self.logs_dir.glob("context_stats.jsonl.*"):
                try:
                    file_time = datetime.fromtimestamp(stats_file.stat().st_mtime)
                    if file_time < cutoff_date:
                        stats_file.unlink()
                        logger.info(f"Archivo de estadísticas antiguo eliminado: {stats_file}")
                except Exception as e:
                    logger.warning(f"No se pudo eliminar {stats_file}: {e}")
            
            logger.info(f"Limpieza de logs completada. Manteniendo logs de los últimos {days_to_keep} días.")
            
        except Exception as e:
            logger.error(f"Error en limpieza de logs: {e}")
    
    def get_logs_info(self) -> Dict[str, Any]:
        """Obtiene información sobre los archivos de log."""
        try:
            logs_info = {
                "logs_directory": str(self.logs_dir),
                "files": {},
                "total_size": 0
            }
            
            for log_file in self.logs_dir.glob("*"):
                if log_file.is_file():
                    file_info = {
                        "size_bytes": log_file.stat().st_size,
                        "size_mb": log_file.stat().st_size / (1024 * 1024),
                        "modified": datetime.fromtimestamp(log_file.stat().st_mtime).isoformat(),
                        "age_days": (datetime.now() - datetime.fromtimestamp(log_file.stat().st_mtime)).days
                    }
                    
                    logs_info["files"][log_file.name] = file_info
                    logs_info["total_size"] += file_info["size_bytes"]
            
            logs_info["total_size_mb"] = logs_info["total_size"] / (1024 * 1024)
            
            return logs_info
            
        except Exception as e:
            return {"error": f"Error obteniendo información de logs: {e}"}
