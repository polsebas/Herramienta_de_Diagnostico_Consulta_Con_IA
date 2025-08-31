import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import tiktoken
from dataclasses import dataclass, asdict
import statistics
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class ContextStats:
    """Estadísticas de uso de contexto para monitoreo."""
    timestamp: str
    query: str
    tokens_before: int
    tokens_after: int
    compression_ratio: float
    chunks_original: int
    chunks_final: int
    context_type: str
    model_name: str
    window_size: int
    budget_used: float
    response_tokens_estimated: int
    efficiency_score: float

@dataclass
class ContextMetrics:
    """Métricas agregadas de contexto para análisis."""
    period_start: str
    period_end: str
    total_queries: int
    avg_compression_ratio: float
    avg_efficiency_score: float
    total_tokens_saved: int
    budget_utilization: float
    context_quality_distribution: Dict[str, int]
    model_performance: Dict[str, Dict[str, float]]

class ContextManager:
    """
    Maneja la compactación intencional del contexto y historial de diálogo.
    Implementa la regla de oro: mantener uso <40% de la ventana del modelo.
    """
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", max_context_ratio: float = 0.4):
        """
        Inicializa el gestor de contexto.
        
        Args:
            model_name: Nombre del modelo para calcular tokens
            max_context_ratio: Ratio máximo de contexto (default 0.4 = 40%)
        """
        self.model_name = model_name
        self.max_context_ratio = max_context_ratio
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)
        
        # Configurar tokenizer
        try:
            self.tokenizer = tiktoken.encoding_for_model(model_name)
        except KeyError:
            # Fallback a cl100k_base si no se encuentra el modelo
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
            logger.warning(f"Modelo {model_name} no encontrado, usando cl100k_base")
        
        # Obtener tamaño de ventana del modelo
        self.model_window_size = self._get_model_window_size(model_name)
        self.max_context_tokens = int(self.model_window_size * max_context_ratio)
        
        # Historial de métricas para análisis
        self.metrics_history = []
        self.performance_cache = {}
        
        logger.info(f"ContextManager inicializado: {model_name}, ventana: {self.model_window_size}, "
                   f"máximo contexto: {self.max_context_tokens} tokens")
    
    def _get_model_window_size(self, model_name: str) -> int:
        """Obtiene el tamaño de ventana del modelo en tokens."""
        window_sizes = {
            "gpt-3.5-turbo": 4096,
            "gpt-3.5-turbo-16k": 16384,
            "gpt-4": 8192,
            "gpt-4-32k": 32768,
            "gpt-4-turbo": 128000,
            "claude-3-sonnet": 200000,
            "claude-3-opus": 200000
        }
        return window_sizes.get(model_name, 4096)  # Default a 4k
    
    def count_tokens(self, text: str) -> int:
        """Cuenta tokens en un texto usando el tokenizer del modelo."""
        return len(self.tokenizer.encode(text))
    
    def summarize_dialog(self, turns: List[Dict[str, Any]], budget_tokens: int = 800) -> str:
        """
        Resume el historial de diálogo usando LLM para crear un "trajectory summary".
        
        Args:
            turns: Lista de turnos del diálogo
            budget_tokens: Presupuesto de tokens para el resumen
        
        Returns:
            Resumen compacto del diálogo
        """
        if not turns:
            return ""
        
        # Si el historial es corto, no necesita resumen
        total_tokens = sum(self.count_tokens(turn.get("content", "")) for turn in turns)
        if total_tokens <= budget_tokens:
            return self._format_dialog_history(turns)
        
        # Crear resumen estructurado
        summary_parts = []
        current_topic = None
        
        for turn in turns[-5:]:  # Últimos 5 turnos
            role = turn.get("role", "unknown")
            content = turn.get("content", "")
            
            if role == "user":
                # Extraer tema principal de la consulta
                topic = self._extract_topic(content)
                if topic != current_topic:
                    current_topic = topic
                    summary_parts.append(f"**Tema**: {topic}")
                summary_parts.append(f"**Usuario**: {content[:100]}...")
            elif role == "assistant":
                # Resumir respuesta del asistente
                summary_parts.append(f"**Asistente**: {content[:150]}...")
        
        summary = "\n".join(summary_parts)
        
        # Si el resumen es muy largo, truncar
        if self.count_tokens(summary) > budget_tokens:
            summary = self._truncate_text(summary, budget_tokens)
        
        return f"## Resumen del Diálogo\n{summary}"
    
    def _extract_topic(self, text: str) -> str:
        """Extrae el tema principal de una consulta."""
        # Implementación simple - en producción usar LLM
        text_lower = text.lower()
        if any(word in text_lower for word in ["configuración", "setup", "instalación"]):
            return "Configuración del Sistema"
        elif any(word in text_lower for word in ["error", "problema", "bug", "falla"]):
            return "Resolución de Problemas"
        elif any(word in text_lower for word in ["código", "implementación", "desarrollo"]):
            return "Desarrollo de Código"
        elif any(word in text_lower for word in ["decisión", "elección", "recomendación"]):
            return "Toma de Decisiones"
        else:
            return "Consulta General"
    
    def _format_dialog_history(self, turns: List[Dict[str, Any]]) -> str:
        """Formatea el historial completo del diálogo."""
        formatted = ["## Historial del Diálogo"]
        
        for i, turn in enumerate(turns[-3:], 1):  # Últimos 3 turnos
            role = turn.get("role", "unknown")
            content = turn.get("content", "")
            formatted.append(f"**{role.title()}**: {content[:200]}...")
        
        return "\n".join(formatted)
    
    def compact_chunks(self, chunks: List[Dict[str, Any]], max_tokens: int) -> str:
        """
        Fusiona y deduplica chunks con pérdida controlada.
        
        Args:
            chunks: Lista de chunks a compactar
            max_tokens: Máximo de tokens permitidos
        
        Returns:
            Contexto compactado
        """
        if not chunks:
            return ""
        
        # Ordenar chunks por relevancia (score) si está disponible
        sorted_chunks = sorted(chunks, key=lambda x: x.get("score", 0), reverse=True)
        
        # Inicializar contexto compactado
        compacted_parts = []
        current_tokens = 0
        
        for chunk in sorted_chunks:
            # Extraer información del chunk
            text = chunk.get("text", "")
            metadata = chunk.get("metadata", {})
            
            # Crear entrada compacta
            title = metadata.get("title", "Documento")
            section = metadata.get("section", "")
            line_start = metadata.get("line_start", "")
            line_end = metadata.get("line_end", "")
            
            # Formato: [Título](línea X-Y): contenido relevante
            header = f"[{title}]"
            if section:
                header += f" ({section})"
            if line_start and line_end:
                header += f"(línea {line_start}-{line_end})"
            
            # Calcular tokens del chunk
            chunk_tokens = self.count_tokens(text)
            
            # Si agregar este chunk excede el límite, parar
            if current_tokens + chunk_tokens > max_tokens:
                break
            
            # Agregar chunk al contexto
            compacted_parts.append(f"{header}: {text}")
            current_tokens += chunk_tokens
        
        # Si no hay chunks que quepan, tomar solo el más relevante
        if not compacted_parts and chunks:
            best_chunk = chunks[0]
            text = best_chunk.get("text", "")
            metadata = best_chunk.get("metadata", {})
            title = metadata.get("title", "Documento")
            
            # Truncar si es necesario
            if self.count_tokens(text) > max_tokens:
                text = self._truncate_text(text, max_tokens)
            
            compacted_parts.append(f"[{title}]: {text}")
        
        return "\n\n".join(compacted_parts)
    
    def _truncate_text(self, text: str, max_tokens: int) -> str:
        """Trunca texto al número máximo de tokens."""
        tokens = self.tokenizer.encode(text)
        if len(tokens) <= max_tokens:
            return text
        
        # Truncar y agregar indicador
        truncated_tokens = tokens[:max_tokens-10]  # Dejar espacio para "..."
        truncated_text = self.tokenizer.decode(truncated_tokens)
        return truncated_text + "..."
    
    def log_context_stats(self, stats: ContextStats):
        """Registra estadísticas de uso de contexto."""
        log_file = self.logs_dir / "context_stats.jsonl"
        
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(asdict(stats), ensure_ascii=False) + "\n")
            
            # Agregar a historial en memoria para análisis
            self.metrics_history.append(stats)
            
            # Limpiar historial antiguo (mantener últimos 1000 registros)
            if len(self.metrics_history) > 1000:
                self.metrics_history = self.metrics_history[-1000:]
                
        except Exception as e:
            logger.error(f"Error al escribir estadísticas: {e}")
    
    def get_context_budget(self, query_tokens: int, system_prompt_tokens: int) -> int:
        """
        Calcula el presupuesto de tokens para el contexto.
        
        Args:
            query_tokens: Tokens de la consulta actual
            system_prompt_tokens: Tokens del prompt del sistema
        
        Returns:
            Tokens disponibles para contexto
        """
        # Reservar espacio para la respuesta (aproximadamente 25% de la ventana)
        response_budget = int(self.model_window_size * 0.25)
        
        # Calcular espacio disponible para contexto
        available_tokens = self.max_context_tokens - query_tokens - system_prompt_tokens - response_budget
        
        # Asegurar mínimo de contexto
        return max(available_tokens, 500)
    
    def create_context_summary(self, 
                             system_prompt: str, 
                             query: str, 
                             dialog_history: List[Dict[str, Any]], 
                             retrieved_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Crea un resumen completo del contexto optimizado.
        
        Args:
            system_prompt: Prompt del sistema
            query: Consulta actual
            dialog_history: Historial del diálogo
            retrieved_chunks: Chunks recuperados
        
        Returns:
            Dict con contexto optimizado y estadísticas
        """
        # Contar tokens de componentes
        system_tokens = self.count_tokens(system_prompt)
        query_tokens = self.count_tokens(query)
        
        # Calcular presupuesto para contexto
        context_budget = self.get_context_budget(query_tokens, system_tokens)
        
        # Compactar historial y chunks
        dialog_summary = self.summarize_dialog(dialog_history, budget_tokens=context_budget//2)
        compacted_chunks = self.compact_chunks(retrieved_chunks, context_budget//2)
        
        # Construir contexto final
        final_context = f"{system_prompt}\n\n{dialog_summary}\n\n## Contexto Relevante\n{compacted_chunks}"
        
        # Calcular estadísticas
        final_tokens = self.count_tokens(final_context)
        compression_ratio = final_tokens / (system_tokens + query_tokens + 
                                          sum(self.count_tokens(str(chunk)) for chunk in retrieved_chunks))
        
        # Calcular score de eficiencia
        efficiency_score = self._calculate_efficiency_score(
            final_tokens, context_budget, compression_ratio
        )
        
        # Estimar tokens de respuesta
        response_tokens_estimated = int(self.model_window_size * 0.25)
        
        # Crear estadísticas detalladas
        stats = ContextStats(
            timestamp=datetime.now().isoformat(),
            query=query[:100],
            tokens_before=system_tokens + query_tokens + sum(self.count_tokens(str(chunk)) for chunk in retrieved_chunks),
            tokens_after=final_tokens,
            compression_ratio=compression_ratio,
            chunks_original=len(retrieved_chunks),
            chunks_final=len(compacted_chunks.split("\n\n")),
            context_type="hybrid",
            model_name=self.model_name,
            window_size=self.model_window_size,
            budget_used=final_tokens / context_budget if context_budget > 0 else 0,
            response_tokens_estimated=response_tokens_estimated,
            efficiency_score=efficiency_score
        )
        
        # Registrar estadísticas
        self.log_context_stats(stats)
        
        return {
            "context": final_context,
            "stats": stats,
            "query": query,
            "remaining_tokens": self.max_context_tokens - final_tokens,
            "efficiency_metrics": {
                "compression_ratio": compression_ratio,
                "budget_utilization": final_tokens / context_budget if context_budget > 0 else 0,
                "efficiency_score": efficiency_score
            }
        }
    
    def _calculate_efficiency_score(self, final_tokens: int, context_budget: int, 
                                  compression_ratio: float) -> float:
        """
        Calcula un score de eficiencia del contexto.
        
        Args:
            final_tokens: Tokens del contexto final
            context_budget: Presupuesto disponible
            compression_ratio: Ratio de compresión
        
        Returns:
            Score de eficiencia (0.0-1.0)
        """
        # Score por uso del presupuesto (40%)
        budget_score = 0.0
        if context_budget > 0:
            utilization = final_tokens / context_budget
            if utilization <= 0.8:  # Uso eficiente
                budget_score = 1.0
            elif utilization <= 1.0:  # Uso aceptable
                budget_score = 0.7
            else:  # Exceso de presupuesto
                budget_score = 0.3
        
        # Score por compresión (30%)
        compression_score = 0.0
        if compression_ratio > 0:
            if compression_ratio <= 0.5:  # Excelente compresión
                compression_score = 1.0
            elif compression_ratio <= 0.7:  # Buena compresión
                compression_score = 0.8
            elif compression_ratio <= 0.9:  # Compresión aceptable
                compression_score = 0.6
            else:  # Poca compresión
                compression_score = 0.3
        
        # Score por balance (30%)
        balance_score = 0.0
        if final_tokens > 0:
            # Preferir contexto balanceado (no muy corto, no muy largo)
            if 500 <= final_tokens <= 1500:
                balance_score = 1.0
            elif 300 <= final_tokens <= 2000:
                balance_score = 0.8
            else:
                balance_score = 0.5
        
        # Score final ponderado
        final_score = (budget_score * 0.4) + (compression_score * 0.3) + (balance_score * 0.3)
        return min(1.0, final_score)
    
    def get_performance_metrics(self, period_hours: int = 24) -> ContextMetrics:
        """
        Obtiene métricas de rendimiento del contexto para un período específico.
        
        Args:
            period_hours: Período en horas para analizar
        
        Returns:
            Métricas agregadas del período
        """
        now = datetime.now()
        period_start = now - timedelta(hours=period_hours)
        
        # Filtrar métricas del período
        period_metrics = [
            m for m in self.metrics_history 
            if datetime.fromisoformat(m.timestamp) >= period_start
        ]
        
        if not period_metrics:
            return ContextMetrics(
                period_start=period_start.isoformat(),
                period_end=now.isoformat(),
                total_queries=0,
                avg_compression_ratio=0.0,
                avg_efficiency_score=0.0,
                total_tokens_saved=0,
                budget_utilization=0.0,
                context_quality_distribution={},
                model_performance={}
            )
        
        # Calcular métricas agregadas
        compression_ratios = [m.compression_ratio for m in period_metrics]
        efficiency_scores = [m.efficiency_score for m in period_metrics]
        
        # Calcular tokens ahorrados
        total_tokens_saved = sum(
            m.tokens_before - m.tokens_after for m in period_metrics
        )
        
        # Calcular utilización del presupuesto
        budget_utilizations = [m.budget_used for m in period_metrics]
        avg_budget_utilization = statistics.mean(budget_utilizations) if budget_utilizations else 0.0
        
        # Distribución de calidad del contexto
        quality_distribution = defaultdict(int)
        for score in efficiency_scores:
            if score >= 0.9:
                quality_distribution["excelente"] += 1
            elif score >= 0.8:
                quality_distribution["bueno"] += 1
            elif score >= 0.7:
                quality_distribution["aceptable"] += 1
            else:
                quality_distribution["necesita_mejora"] += 1
        
        # Rendimiento por modelo
        model_performance = defaultdict(lambda: defaultdict(list))
        for metric in period_metrics:
            model_performance[metric.model_name]["compression_ratios"].append(metric.compression_ratio)
            model_performance[metric.model_name]["efficiency_scores"].append(metric.efficiency_score)
            model_performance[metric.model_name]["budget_utilizations"].append(metric.budget_used)
        
        # Calcular promedios por modelo
        for model in model_performance:
            model_performance[model] = {
                "avg_compression_ratio": statistics.mean(model_performance[model]["compression_ratios"]),
                "avg_efficiency_score": statistics.mean(model_performance[model]["efficiency_scores"]),
                "avg_budget_utilization": statistics.mean(model_performance[model]["budget_utilizations"]),
                "total_queries": len(model_performance[model]["compression_ratios"])
            }
        
        return ContextMetrics(
            period_start=period_start.isoformat(),
            period_end=now.isoformat(),
            total_queries=len(period_metrics),
            avg_compression_ratio=statistics.mean(compression_ratios),
            avg_efficiency_score=statistics.mean(efficiency_scores),
            total_tokens_saved=total_tokens_saved,
            budget_utilization=avg_budget_utilization,
            context_quality_distribution=dict(quality_distribution),
            model_performance=dict(model_performance)
        )
    
    def get_recommendations(self) -> List[str]:
        """
        Genera recomendaciones basadas en el análisis de métricas.
        
        Returns:
            Lista de recomendaciones
        """
        recommendations = []
        
        # Obtener métricas de las últimas 24 horas
        metrics = self.get_performance_metrics(24)
        
        if metrics.total_queries == 0:
            return ["No hay datos suficientes para generar recomendaciones"]
        
        # Recomendaciones basadas en ratio de compresión
        if metrics.avg_compression_ratio > 0.8:
            recommendations.append("El ratio de compresión es alto. Considera ajustar la estrategia de compactación.")
        
        # Recomendaciones basadas en eficiencia
        if metrics.avg_efficiency_score < 0.7:
            recommendations.append("La eficiencia del contexto es baja. Revisa la configuración de presupuesto.")
        
        # Recomendaciones basadas en utilización del presupuesto
        if metrics.budget_utilization > 0.9:
            recommendations.append("El presupuesto de contexto se está agotando. Considera aumentar el límite.")
        elif metrics.budget_utilization < 0.5:
            recommendations.append("El presupuesto de contexto no se está utilizando eficientemente.")
        
        # Recomendaciones basadas en calidad
        if metrics.context_quality_distribution.get("necesita_mejora", 0) > metrics.total_queries * 0.3:
            recommendations.append("Más del 30% de las consultas necesitan mejora. Revisa la configuración del sistema.")
        
        return recommendations
    
    def export_metrics_csv(self, output_file: str = "context_metrics.csv"):
        """
        Exporta métricas a formato CSV para análisis externo.
        
        Args:
            output_file: Archivo de salida CSV
        """
        try:
            import pandas as pd
            
            # Convertir métricas a DataFrame
            data = []
            for metric in self.metrics_history:
                data.append(asdict(metric))
            
            df = pd.DataFrame(data)
            
            # Guardar CSV
            df.to_csv(output_file, index=False, encoding='utf-8')
            logger.info(f"Métricas exportadas a {output_file}")
            
        except ImportError:
            logger.warning("pandas no disponible, exportando como JSON")
            # Fallback a JSON
            with open(output_file.replace('.csv', '.json'), 'w', encoding='utf-8') as f:
                json.dump([asdict(m) for m in self.metrics_history], f, indent=2, ensure_ascii=False)
    
    def clear_old_metrics(self, days_to_keep: int = 30):
        """
        Limpia métricas antiguas para liberar memoria.
        
        Args:
            days_to_keep: Días de métricas a mantener
        """
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        # Filtrar métricas recientes
        self.metrics_history = [
            m for m in self.metrics_history
            if datetime.fromisoformat(m.timestamp) >= cutoff_date
        ]
        
        logger.info(f"Métricas limpiadas. Manteniendo {len(self.metrics_history)} registros recientes.")
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas del gestor de contexto."""
        return {
            "model_name": self.model_name,
            "window_size": self.model_window_size,
            "max_context_tokens": self.max_context_tokens,
            "max_context_ratio": self.max_context_ratio,
            "metrics_history_size": len(self.metrics_history),
            "recent_performance": self.get_performance_metrics(1),  # Última hora
            "recommendations": self.get_recommendations()
        }

    # Compatibilidad con SpecLayer: método asincrónico utilizado para recuperar historial relevante
    async def get_relevant_history(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retorna historial relevante para una query.
        Implementación mínima para smoke tests: retorna lista vacía.
        """
        return []
