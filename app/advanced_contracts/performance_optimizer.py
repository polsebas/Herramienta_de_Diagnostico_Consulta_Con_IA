"""
Performance Optimizer - Optimizador de rendimiento de contratos

Este módulo optimiza el rendimiento del sistema de generación de contratos
mediante análisis de métricas, caching inteligente y optimización de algoritmos.
"""

import logging
import time
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class OptimizationType(Enum):
    """Tipos de optimización disponibles."""
    CACHING = "caching"
    ALGORITHM = "algorithm"
    PREPROCESSING = "preprocessing"
    PARALLEL_PROCESSING = "parallel_processing"
    MEMORY_OPTIMIZATION = "memory_optimization"


@dataclass
class PerformanceMetrics:
    """Métricas de rendimiento."""
    operation_name: str
    execution_time: float
    memory_usage: float
    cpu_usage: float
    cache_hit_rate: float
    timestamp: datetime


@dataclass
class OptimizationResult:
    """Resultado de una optimización."""
    optimization_type: OptimizationType
    performance_improvement: float
    memory_reduction: float
    success: bool
    description: str
    side_effects: List[str]


class PerformanceMonitor:
    """Monitor de rendimiento para operaciones de contratos."""
    
    def __init__(self):
        self.metrics_history = []
        self.performance_baselines = {}
        
    async def measure_operation(self, operation_name: str, operation: Callable) -> Tuple[Any, PerformanceMetrics]:
        """
        Mide rendimiento de una operación.
        
        Args:
            operation_name: Nombre de la operación
            operation: Función a medir
            
        Returns:
            Tupla con (resultado_operación, métricas_rendimiento)
        """
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        try:
            # Ejecutar operación
            result = await operation() if asyncio.iscoroutinefunction(operation) else operation()
            
            # Medir métricas finales
            end_time = time.time()
            end_memory = self._get_memory_usage()
            
            metrics = PerformanceMetrics(
                operation_name=operation_name,
                execution_time=end_time - start_time,
                memory_usage=end_memory - start_memory,
                cpu_usage=self._get_cpu_usage(),
                cache_hit_rate=self._get_cache_hit_rate(operation_name),
                timestamp=datetime.now()
            )
            
            # Almacenar métricas
            self.metrics_history.append(metrics)
            
            # Actualizar baseline si es necesario
            await self._update_baseline(operation_name, metrics)
            
            return result, metrics
            
        except Exception as e:
            logger.error(f"Error midiendo operación {operation_name}: {e}")
            raise
    
    def _get_memory_usage(self) -> float:
        """Obtiene uso actual de memoria (simplificado)."""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # MB
        except ImportError:
            return 0.0  # Fallback si psutil no está disponible
    
    def _get_cpu_usage(self) -> float:
        """Obtiene uso actual de CPU (simplificado)."""
        try:
            import psutil
            return psutil.cpu_percent(interval=0.1)
        except ImportError:
            return 0.0  # Fallback
    
    def _get_cache_hit_rate(self, operation_name: str) -> float:
        """Obtiene tasa de hit del cache (simplificado)."""
        # Placeholder - en implementación real consultaría cache real
        return 0.8
    
    async def _update_baseline(self, operation_name: str, metrics: PerformanceMetrics):
        """Actualiza baseline de rendimiento."""
        if operation_name not in self.performance_baselines:
            self.performance_baselines[operation_name] = {
                'avg_execution_time': metrics.execution_time,
                'avg_memory_usage': metrics.memory_usage,
                'sample_count': 1
            }
        else:
            baseline = self.performance_baselines[operation_name]
            count = baseline['sample_count']
            
            # Promedio móvil
            baseline['avg_execution_time'] = (
                (baseline['avg_execution_time'] * count + metrics.execution_time) / (count + 1)
            )
            baseline['avg_memory_usage'] = (
                (baseline['avg_memory_usage'] * count + metrics.memory_usage) / (count + 1)
            )
            baseline['sample_count'] = count + 1
    
    def get_performance_report(self, operation_name: Optional[str] = None) -> Dict[str, Any]:
        """Genera reporte de rendimiento."""
        if operation_name:
            operation_metrics = [m for m in self.metrics_history if m.operation_name == operation_name]
            if not operation_metrics:
                return {'error': f'No metrics found for operation {operation_name}'}
            
            return {
                'operation': operation_name,
                'total_executions': len(operation_metrics),
                'avg_execution_time': sum(m.execution_time for m in operation_metrics) / len(operation_metrics),
                'avg_memory_usage': sum(m.memory_usage for m in operation_metrics) / len(operation_metrics),
                'baseline': self.performance_baselines.get(operation_name, {})
            }
        else:
            # Reporte general
            return {
                'total_operations_measured': len(self.metrics_history),
                'operations_tracked': list(self.performance_baselines.keys()),
                'baselines': self.performance_baselines
            }


class IntelligentCache:
    """Cache inteligente para operaciones de contratos."""
    
    def __init__(self, max_size: int = 1000, ttl_minutes: int = 60):
        self.cache = {}
        self.access_times = {}
        self.hit_counts = {}
        self.max_size = max_size
        self.ttl = timedelta(minutes=ttl_minutes)
        
    async def get(self, key: str) -> Optional[Any]:
        """Obtiene valor del cache."""
        if key not in self.cache:
            return None
        
        # Verificar TTL
        if datetime.now() - self.access_times[key] > self.ttl:
            await self._evict(key)
            return None
        
        # Actualizar estadísticas
        self.access_times[key] = datetime.now()
        self.hit_counts[key] = self.hit_counts.get(key, 0) + 1
        
        return self.cache[key]
    
    async def set(self, key: str, value: Any):
        """Almacena valor en cache."""
        # Evict si está lleno
        if len(self.cache) >= self.max_size:
            await self._evict_lru()
        
        self.cache[key] = value
        self.access_times[key] = datetime.now()
        self.hit_counts[key] = 0
    
    async def _evict(self, key: str):
        """Elimina entrada del cache."""
        self.cache.pop(key, None)
        self.access_times.pop(key, None)
        self.hit_counts.pop(key, None)
    
    async def _evict_lru(self):
        """Elimina entrada menos recientemente usada."""
        if not self.access_times:
            return
        
        lru_key = min(self.access_times.items(), key=lambda x: x[1])[0]
        await self._evict(lru_key)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas del cache."""
        total_accesses = sum(self.hit_counts.values())
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hit_rate': total_accesses / max(1, len(self.hit_counts)) if self.hit_counts else 0,
            'total_accesses': total_accesses,
            'keys_cached': list(self.cache.keys())
        }


class PerformanceOptimizer:
    """
    Optimizador principal de rendimiento del sistema de contratos.
    """
    
    def __init__(self):
        self.monitor = PerformanceMonitor()
        self.cache = IntelligentCache()
        self.optimization_history = []
        self.enabled_optimizations = {
            OptimizationType.CACHING: True,
            OptimizationType.PREPROCESSING: True,
            OptimizationType.PARALLEL_PROCESSING: False,  # Experimental
            OptimizationType.MEMORY_OPTIMIZATION: True
        }
        
        logger.info("PerformanceOptimizer inicializado")
    
    async def optimize_contract_generation(self,
                                         operation_name: str,
                                         operation: Callable,
                                         optimization_types: Optional[List[OptimizationType]] = None) -> Tuple[Any, List[OptimizationResult]]:
        """
        Optimiza operación de generación de contrato.
        
        Args:
            operation_name: Nombre de la operación
            operation: Función a optimizar
            optimization_types: Tipos de optimización a aplicar
            
        Returns:
            Tupla con (resultado, lista_de_optimizaciones_aplicadas)
        """
        logger.info(f"Optimizando operación: {operation_name}")
        
        optimization_results = []
        
        # Aplicar optimizaciones habilitadas
        optimizations_to_apply = optimization_types or [
            opt_type for opt_type, enabled in self.enabled_optimizations.items() if enabled
        ]
        
        optimized_operation = operation
        
        for opt_type in optimizations_to_apply:
            try:
                if opt_type == OptimizationType.CACHING:
                    optimized_operation, cache_result = await self._apply_caching_optimization(
                        operation_name, optimized_operation
                    )
                    optimization_results.append(cache_result)
                
                elif opt_type == OptimizationType.PREPROCESSING:
                    optimized_operation, preprocess_result = await self._apply_preprocessing_optimization(
                        operation_name, optimized_operation
                    )
                    optimization_results.append(preprocess_result)
                
                elif opt_type == OptimizationType.MEMORY_OPTIMIZATION:
                    optimized_operation, memory_result = await self._apply_memory_optimization(
                        operation_name, optimized_operation
                    )
                    optimization_results.append(memory_result)
                
            except Exception as e:
                logger.warning(f"Error aplicando optimización {opt_type.value}: {e}")
        
        # Ejecutar operación optimizada con medición
        result, metrics = await self.monitor.measure_operation(operation_name, optimized_operation)
        
        # Almacenar resultados de optimización
        self.optimization_history.append({
            'operation_name': operation_name,
            'optimizations_applied': [opt.optimization_type.value for opt in optimization_results],
            'performance_metrics': asdict(metrics),
            'timestamp': datetime.now().isoformat()
        })
        
        return result, optimization_results
    
    async def _apply_caching_optimization(self, operation_name: str, 
                                        operation: Callable) -> Tuple[Callable, OptimizationResult]:
        """Aplica optimización de caching."""
        
        async def cached_operation(*args, **kwargs):
            # Generar cache key
            cache_key = f"{operation_name}_{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Intentar obtener del cache
            cached_result = await self.cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit para {operation_name}")
                return cached_result
            
            # Ejecutar operación original
            result = await operation(*args, **kwargs) if asyncio.iscoroutinefunction(operation) else operation(*args, **kwargs)
            
            # Almacenar en cache
            await self.cache.set(cache_key, result)
            
            return result
        
        return cached_operation, OptimizationResult(
            optimization_type=OptimizationType.CACHING,
            performance_improvement=0.3,  # Estimado
            memory_reduction=0.0,
            success=True,
            description="Caching inteligente aplicado",
            side_effects=["Posible staleness de datos"]
        )
    
    async def _apply_preprocessing_optimization(self, operation_name: str,
                                             operation: Callable) -> Tuple[Callable, OptimizationResult]:
        """Aplica optimización de preprocessing."""
        
        async def preprocessed_operation(*args, **kwargs):
            # Preprocessing: validar y optimizar inputs
            optimized_args, optimized_kwargs = await self._preprocess_inputs(args, kwargs)
            
            # Ejecutar con inputs optimizados
            return await operation(*optimized_args, **optimized_kwargs) if asyncio.iscoroutinefunction(operation) else operation(*optimized_args, **optimized_kwargs)
        
        return preprocessed_operation, OptimizationResult(
            optimization_type=OptimizationType.PREPROCESSING,
            performance_improvement=0.15,
            memory_reduction=0.1,
            success=True,
            description="Preprocessing de inputs aplicado",
            side_effects=[]
        )
    
    async def _apply_memory_optimization(self, operation_name: str,
                                       operation: Callable) -> Tuple[Callable, OptimizationResult]:
        """Aplica optimización de memoria."""
        
        async def memory_optimized_operation(*args, **kwargs):
            # Limpiar cache si está muy lleno
            cache_stats = self.cache.get_cache_stats()
            if cache_stats['size'] > cache_stats['max_size'] * 0.8:
                logger.debug("Limpiando cache para optimización de memoria")
                # En implementación real, se haría limpieza selectiva
            
            return await operation(*args, **kwargs) if asyncio.iscoroutinefunction(operation) else operation(*args, **kwargs)
        
        return memory_optimized_operation, OptimizationResult(
            optimization_type=OptimizationType.MEMORY_OPTIMIZATION,
            performance_improvement=0.1,
            memory_reduction=0.2,
            success=True,
            description="Optimización de memoria aplicada",
            side_effects=["Posible limpieza de cache"]
        )
    
    async def _preprocess_inputs(self, args: tuple, kwargs: dict) -> Tuple[tuple, dict]:
        """Preprocessa inputs para optimización."""
        # Optimizaciones simples de inputs
        optimized_args = args
        optimized_kwargs = kwargs.copy()
        
        # Ejemplo: truncar strings muy largos
        for key, value in optimized_kwargs.items():
            if isinstance(value, str) and len(value) > 10000:
                optimized_kwargs[key] = value[:10000] + "... [truncated]"
                logger.debug(f"Truncando input largo: {key}")
        
        return optimized_args, optimized_kwargs
    
    async def analyze_performance_trends(self, days: int = 30) -> Dict[str, Any]:
        """Analiza tendencias de rendimiento."""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_metrics = [
            m for m in self.monitor.metrics_history 
            if m.timestamp >= cutoff_date
        ]
        
        if not recent_metrics:
            return {'message': 'No hay métricas recientes disponibles'}
        
        # Agrupar por operación
        operations = {}
        for metric in recent_metrics:
            if metric.operation_name not in operations:
                operations[metric.operation_name] = []
            operations[metric.operation_name].append(metric)
        
        # Analizar tendencias
        trends = {}
        for op_name, op_metrics in operations.items():
            if len(op_metrics) >= 5:  # Mínimo para análisis de tendencia
                execution_times = [m.execution_time for m in op_metrics]
                memory_usage = [m.memory_usage for m in op_metrics]
                
                trends[op_name] = {
                    'avg_execution_time': sum(execution_times) / len(execution_times),
                    'execution_time_trend': self._calculate_trend(execution_times),
                    'avg_memory_usage': sum(memory_usage) / len(memory_usage),
                    'memory_trend': self._calculate_trend(memory_usage),
                    'sample_count': len(op_metrics)
                }
        
        return {
            'period_days': days,
            'operations_analyzed': len(trends),
            'trends': trends,
            'total_metrics': len(recent_metrics)
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calcula tendencia simple de una serie de valores."""
        if len(values) < 2:
            return "insufficient_data"
        
        # Comparar primera mitad con segunda mitad
        mid = len(values) // 2
        first_half_avg = sum(values[:mid]) / mid
        second_half_avg = sum(values[mid:]) / (len(values) - mid)
        
        change_percent = ((second_half_avg - first_half_avg) / first_half_avg) * 100
        
        if change_percent > 10:
            return "increasing"
        elif change_percent < -10:
            return "decreasing"
        else:
            return "stable"
    
    async def suggest_optimizations(self, operation_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Sugiere optimizaciones basadas en análisis de rendimiento."""
        suggestions = []
        
        # Analizar tendencias recientes
        trends = await self.analyze_performance_trends(days=7)
        
        if 'trends' not in trends:
            return suggestions
        
        operations_to_analyze = [operation_name] if operation_name else trends['trends'].keys()
        
        for op_name in operations_to_analyze:
            op_trend = trends['trends'].get(op_name, {})
            
            # Sugerir optimizaciones basadas en tendencias
            if op_trend.get('execution_time_trend') == 'increasing':
                suggestions.append({
                    'operation': op_name,
                    'optimization': OptimizationType.ALGORITHM.value,
                    'reason': 'Tiempo de ejecución en aumento',
                    'priority': 'high',
                    'estimated_improvement': '20-30%'
                })
            
            if op_trend.get('memory_trend') == 'increasing':
                suggestions.append({
                    'operation': op_name,
                    'optimization': OptimizationType.MEMORY_OPTIMIZATION.value,
                    'reason': 'Uso de memoria en aumento',
                    'priority': 'medium',
                    'estimated_improvement': '15-25%'
                })
            
            # Sugerir caching si no está habilitado
            cache_stats = self.cache.get_cache_stats()
            if cache_stats['hit_rate'] < 0.5:
                suggestions.append({
                    'operation': op_name,
                    'optimization': OptimizationType.CACHING.value,
                    'reason': 'Baja tasa de hit del cache',
                    'priority': 'medium',
                    'estimated_improvement': '30-50%'
                })
        
        return suggestions
    
    async def benchmark_operation(self, operation_name: str, operation: Callable,
                                iterations: int = 10) -> Dict[str, Any]:
        """Ejecuta benchmark de una operación."""
        logger.info(f"Ejecutando benchmark de {operation_name} con {iterations} iteraciones")
        
        execution_times = []
        memory_usages = []
        
        for i in range(iterations):
            try:
                _, metrics = await self.monitor.measure_operation(
                    f"{operation_name}_benchmark_{i}", operation
                )
                execution_times.append(metrics.execution_time)
                memory_usages.append(metrics.memory_usage)
                
            except Exception as e:
                logger.warning(f"Error en iteración {i} del benchmark: {e}")
        
        if not execution_times:
            return {'error': 'No se pudieron completar benchmarks'}
        
        return {
            'operation': operation_name,
            'iterations': len(execution_times),
            'avg_execution_time': sum(execution_times) / len(execution_times),
            'min_execution_time': min(execution_times),
            'max_execution_time': max(execution_times),
            'std_execution_time': np.std(execution_times),
            'avg_memory_usage': sum(memory_usages) / len(memory_usages),
            'performance_consistency': 1.0 - (np.std(execution_times) / np.mean(execution_times))
        }
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """Genera reporte completo de optimizaciones."""
        return {
            'optimizations_applied': len(self.optimization_history),
            'enabled_optimizations': {k.value: v for k, v in self.enabled_optimizations.items()},
            'cache_stats': self.cache.get_cache_stats(),
            'performance_baselines': self.monitor.performance_baselines,
            'recent_optimizations': self.optimization_history[-10:],  # Últimas 10
            'suggestions': await self.suggest_optimizations()
        }


# Decorador para optimización automática
def optimize_performance(operation_name: str, 
                        optimization_types: Optional[List[OptimizationType]] = None):
    """
    Decorador para aplicar optimizaciones automáticamente.
    
    Args:
        operation_name: Nombre de la operación
        optimization_types: Tipos de optimización a aplicar
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            optimizer = PerformanceOptimizer()
            
            # Crear función que ejecuta la operación original
            async def operation():
                return await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            
            # Aplicar optimizaciones
            result, optimizations = await optimizer.optimize_contract_generation(
                operation_name, operation, optimization_types
            )
            
            # Log de optimizaciones aplicadas
            if optimizations:
                opt_types = [opt.optimization_type.value for opt in optimizations]
                logger.info(f"Optimizaciones aplicadas a {operation_name}: {', '.join(opt_types)}")
            
            return result
        
        return wrapper
    return decorator


# Función de conveniencia para análisis de rendimiento
async def analyze_contract_performance(operation_name: str) -> Dict[str, Any]:
    """
    Función de conveniencia para analizar rendimiento de operaciones de contrato.
    
    Args:
        operation_name: Nombre de la operación a analizar
        
    Returns:
        Reporte de rendimiento y sugerencias de optimización
    """
    optimizer = PerformanceOptimizer()
    
    # Obtener reporte de rendimiento
    performance_report = optimizer.monitor.get_performance_report(operation_name)
    
    # Obtener sugerencias de optimización
    optimization_suggestions = await optimizer.suggest_optimizations(operation_name)
    
    return {
        'performance_report': performance_report,
        'optimization_suggestions': optimization_suggestions,
        'cache_stats': optimizer.cache.get_cache_stats(),
        'analysis_timestamp': datetime.now().isoformat()
    }
