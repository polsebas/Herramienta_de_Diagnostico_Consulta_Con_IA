#!/usr/bin/env python3
"""
Ejemplo de uso del Context Manager Mejorado

Este script demuestra las nuevas funcionalidades del PR-2:
- Logging avanzado con rotación de archivos
- Métricas en tiempo real
- Alertas automáticas
- Dashboard de estadísticas
"""

import asyncio
import logging
import time
from pathlib import Path
import sys

# Agregar el directorio app al path
sys.path.append(str(Path(__file__).parent / "app"))

from context_manager import ContextManager, ContextStats
from context_logger import ContextLogger
from spec_layer import build_task_contract, render_system_prompt

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ContextManagerDemo:
    """
    Demostración del Context Manager mejorado con logging avanzado.
    """
    
    def __init__(self):
        """Inicializa la demostración."""
        # Crear directorio de logs
        Path("logs").mkdir(exist_ok=True)
        
        # Inicializar Context Manager
        self.context_manager = ContextManager(
            model_name="gpt-3.5-turbo",
            max_context_ratio=0.4
        )
        
        # Inicializar Context Logger
        self.context_logger = ContextLogger(
            logs_dir="logs",
            max_file_size=5 * 1024 * 1024,  # 5MB
            backup_count=3
        )
        
        # Historial de diálogo simulado
        self.dialog_history = []
        
        logger.info("ContextManagerDemo inicializado")
    
    def simulate_dialog_turn(self, user_query: str, assistant_response: str):
        """Simula un turno de diálogo."""
        self.dialog_history.append({
            "role": "user",
            "content": user_query,
            "timestamp": "2024-01-01T12:00:00Z"
        })
        
        self.dialog_history.append({
            "role": "assistant",
            "content": assistant_response,
            "timestamp": "2024-01-01T12:00:01Z"
        })
        
        # Mantener solo los últimos 10 turnos
        if len(self.dialog_history) > 20:
            self.dialog_history = self.dialog_history[-20:]
    
    def simulate_retrieved_chunks(self, query: str) -> list:
        """Simula chunks recuperados para la consulta."""
        # Chunks simulados con diferentes características
        chunks = [
            {
                "id": "chunk_1",
                "text": "El sistema de autenticación utiliza JWT tokens con expiración de 24 horas. Los tokens se validan en cada request y se renuevan automáticamente cuando están próximos a expirar.",
                "metadata": {
                    "title": "Sistema de Autenticación",
                    "section": "JWT Tokens",
                    "line_start": 25,
                    "line_end": 35,
                    "path": "docs/autenticacion.md"
                },
                "score": 0.95,
                "source": "vector"
            },
            {
                "id": "chunk_2",
                "text": "Para configurar el entorno de desarrollo, necesitas instalar Python 3.8+, Node.js 16+, y configurar las variables de entorno en el archivo .env. También se requiere Docker para ejecutar los servicios de base de datos.",
                "metadata": {
                    "title": "Guía de Instalación",
                    "section": "Prerrequisitos",
                    "line_start": 10,
                    "line_end": 20,
                    "path": "docs/instalacion.md"
                },
                "score": 0.87,
                "source": "vector"
            },
            {
                "id": "chunk_3",
                "text": "Los errores comunes incluyen: timeout de conexión a la base de datos, credenciales inválidas, y problemas de red. Verifica la configuración del firewall y las credenciales de API antes de reportar un bug.",
                "metadata": {
                    "title": "Resolución de Problemas",
                    "section": "Errores Comunes",
                    "line_start": 40,
                    "line_end": 50,
                    "path": "docs/troubleshooting.md"
                },
                "score": 0.82,
                "source": "vector"
            },
            {
                "id": "chunk_4",
                "text": "La arquitectura del sistema está basada en microservicios con comunicación asíncrona. Cada servicio tiene su propia base de datos y se comunica con otros servicios a través de APIs REST y mensajes Kafka.",
                "metadata": {
                    "title": "Arquitectura del Sistema",
                    "section": "Microservicios",
                    "line_start": 15,
                    "line_end": 25,
                    "path": "docs/arquitectura.md"
                },
                "score": 0.78,
                "source": "vector"
            },
            {
                "id": "chunk_5",
                "text": "El sistema de logging utiliza Winston con diferentes niveles: error, warn, info, debug. Los logs se almacenan en archivos rotativos y también se envían a un sistema centralizado de monitoreo.",
                "metadata": {
                    "title": "Sistema de Logging",
                    "section": "Configuración",
                    "line_start": 30,
                    "line_end": 40,
                    "path": "docs/logging.md"
                },
                "score": 0.75,
                "source": "vector"
            }
        ]
        
        # Filtrar chunks relevantes según la consulta
        query_lower = query.lower()
        relevant_chunks = []
        
        for chunk in chunks:
            text_lower = chunk["text"].lower()
            relevance_score = 0
            
            # Calcular relevancia simple
            query_words = set(query_lower.split())
            text_words = set(text_lower.split())
            common_words = query_words.intersection(text_words)
            
            if common_words:
                relevance_score = len(common_words) / len(query_words)
                chunk["relevance_score"] = relevance_score
                
                if relevance_score > 0.1:  # Umbral mínimo de relevancia
                    relevant_chunks.append(chunk)
        
        # Ordenar por relevancia
        relevant_chunks.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        return relevant_chunks[:3]  # Top 3 chunks
    
    async def process_query(self, query: str, user_role: str = "developer", 
                           risk_level: str = "medium") -> dict:
        """
        Procesa una consulta completa usando el Context Manager mejorado.
        
        Args:
            query: Consulta del usuario
            user_role: Rol del usuario
            risk_level: Nivel de riesgo
        
        Returns:
            Dict con resultado del procesamiento
        """
        logger.info(f"Procesando consulta: {query[:50]}...")
        
        try:
            # 1. Generar contrato de tarea
            contract = build_task_contract(query, user_role, risk_level)
            
            # 2. Crear prompt del sistema
            system_prompt = render_system_prompt(contract)
            
            # 3. Simular chunks recuperados
            retrieved_chunks = self.simulate_retrieved_chunks(query)
            
            # 4. Crear resumen de contexto usando Context Manager
            context_summary = self.context_manager.create_context_summary(
                system_prompt, query, self.dialog_history, retrieved_chunks
            )
            
            # 5. Logging avanzado usando Context Logger
            self.context_logger.log_context_stats(context_summary["stats"].__dict__)
            
            # 6. Simular respuesta del asistente
            assistant_response = f"Respuesta simulada para: {query[:30]}..."
            self.simulate_dialog_turn(query, assistant_response)
            
            # 7. Resultado final
            result = {
                "query": query,
                "contract": contract.__dict__,
                "context_summary": context_summary,
                "retrieved_chunks": len(retrieved_chunks),
                "tokens_saved": context_summary["stats"].tokens_before - context_summary["stats"].tokens_after,
                "efficiency_score": context_summary["stats"].efficiency_score,
                "compression_ratio": context_summary["stats"].compression_ratio
            }
            
            logger.info(f"Consulta procesada exitosamente. Eficiencia: {result['efficiency_score']:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Error procesando consulta: {e}")
            return {
                "query": query,
                "error": str(e)
            }
    
    def show_real_time_metrics(self):
        """Muestra métricas en tiempo real."""
        metrics = self.context_logger.get_real_time_metrics()
        
        print("\n📊 MÉTRICAS EN TIEMPO REAL")
        print("=" * 50)
        print(f"Total consultas: {metrics['total_queries']}")
        print(f"Total tokens ahorrados: {metrics['total_tokens_saved']:,}")
        print(f"Ratio de compresión promedio: {metrics['avg_compression_ratio']:.2%}")
        print(f"Score de eficiencia promedio: {metrics['avg_efficiency_score']:.2%}")
        print(f"Última actualización: {metrics['last_update']}")
    
    def show_performance_summary(self, period_hours: int = 1):
        """Muestra resumen de rendimiento."""
        summary = self.context_logger.get_performance_summary(period_hours)
        
        print(f"\n📈 RESUMEN DE RENDIMIENTO (últimas {period_hours}h)")
        print("=" * 50)
        
        if "error" in summary:
            print(f"❌ {summary['error']}")
        else:
            print(f"Total consultas: {summary['total_queries']}")
            print(f"Ratio de compresión promedio: {summary['avg_compression_ratio']:.2%}")
            print(f"Score de eficiencia promedio: {summary['avg_efficiency_score']:.2%}")
            print(f"Total tokens ahorrados: {summary['total_tokens_saved']:,}")
            print(f"Eficiencia mínima: {summary['min_efficiency']:.2%}")
            print(f"Eficiencia máxima: {summary['max_efficiency']:.2%}")
            print(f"Generado en: {summary['generated_at']}")
    
    def show_logs_info(self):
        """Muestra información sobre los archivos de log."""
        logs_info = self.context_logger.get_logs_info()
        
        print("\n📁 INFORMACIÓN DE LOGS")
        print("=" * 50)
        print(f"Directorio: {logs_info['logs_directory']}")
        print(f"Tamaño total: {logs_info['total_size_mb']:.2f} MB")
        print(f"Archivos:")
        
        for filename, file_info in logs_info['files'].items():
            print(f"  - {filename}: {file_info['size_mb']:.2f} MB, "
                  f"edad: {file_info['age_days']} días")
    
    def export_metrics(self, format_type: str = "csv"):
        """Exporta métricas en el formato especificado."""
        try:
            output_file = self.context_logger.export_metrics(
                output_format=format_type,
                period_hours=24
            )
            print(f"\n💾 Métricas exportadas a: {output_file}")
            return output_file
        except Exception as e:
            print(f"\n❌ Error exportando métricas: {e}")
            return None

async def main():
    """Función principal para demostrar el Context Manager mejorado."""
    print("🚀 Context Manager Mejorado - Demostración PR-2")
    print("=" * 60)
    
    # Inicializar demostración
    demo = ContextManagerDemo()
    
    # Ejemplos de consultas
    example_queries = [
        {
            "query": "¿Cómo configuro el sistema de autenticación JWT?",
            "user_role": "developer",
            "risk_level": "low"
        },
        {
            "query": "¿Por qué falla la conexión a la base de datos?",
            "user_role": "developer",
            "risk_level": "high"
        },
        {
            "query": "¿Qué arquitectura de microservicios debo usar?",
            "user_role": "architect",
            "risk_level": "medium"
        },
        {
            "query": "¿Cómo implemento logging centralizado?",
            "user_role": "devops",
            "risk_level": "low"
        }
    ]
    
    # Procesar consultas
    print("\n📝 Procesando consultas de ejemplo...")
    
    for i, query_info in enumerate(example_queries, 1):
        print(f"\n--- Consulta {i} ---")
        print(f"Query: {query_info['query']}")
        print(f"Rol: {query_info['user_role']}, Riesgo: {query_info['risk_level']}")
        
        # Procesar consulta
        result = await demo.process_query(
            query_info["query"],
            query_info["user_role"],
            query_info["risk_level"]
        )
        
        if "error" not in result:
            print(f"✅ Procesada exitosamente")
            print(f"   Chunks recuperados: {result['retrieved_chunks']}")
            print(f"   Tokens ahorrados: {result['tokens_saved']:,}")
            print(f"   Score de eficiencia: {result['efficiency_score']:.2%}")
            print(f"   Ratio de compresión: {result['compression_ratio']:.2%}")
        else:
            print(f"❌ Error: {result['error']}")
        
        # Pausa entre consultas para simular procesamiento real
        time.sleep(1)
    
    # Mostrar métricas en tiempo real
    demo.show_real_time_metrics()
    
    # Mostrar resumen de rendimiento
    demo.show_performance_summary(1)  # Última hora
    
    # Mostrar información de logs
    demo.show_logs_info()
    
    # Exportar métricas
    print("\n💾 Exportando métricas...")
    demo.export_metrics("csv")
    
    # Recomendaciones del sistema
    print("\n💡 RECOMENDACIONES DEL SISTEMA")
    print("=" * 50)
    recommendations = demo.context_manager.get_recommendations()
    
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
    else:
        print("✅ El sistema está funcionando de manera óptima.")
    
    # Instrucciones para el dashboard
    print("\n🎯 PRÓXIMOS PASOS")
    print("=" * 50)
    print("1. Ejecutar el dashboard de Streamlit:")
    print("   streamlit run app/dashboard_context.py")
    print("\n2. Ver logs en tiempo real:")
    print("   tail -f logs/context_manager.log")
    print("\n3. Ver alertas:")
    print("   tail -f logs/context_alerts.log")
    print("\n4. Ver reporte de estado:")
    print("   cat logs/status_report.json")
    
    print("\n🎉 Demostración del Context Manager Mejorado completada!")

if __name__ == "__main__":
    # Ejecutar demostración
    asyncio.run(main())
