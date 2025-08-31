#!/usr/bin/env python3
"""
Ejemplo del Pipeline Completo de Subagentes (PR-4)

Este script demuestra las nuevas funcionalidades del PR-4:
- Pipeline completo de subagentes con orquestación
- Verificación automática de calidad con múltiples factores
- Integración con métricas del Context Manager
- Sistema de alertas y monitoreo en tiempo real
"""

import asyncio
import logging
import time
from pathlib import Path
import sys
from datetime import datetime, timedelta
import numpy as np

# Asegurar que el proyecto raíz esté en el path para importar paquete `app`
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.subagents.orchestrator import SubagentOrchestrator, PipelineConfig
from app.context_manager import ContextManager
from app.context_logger import ContextLogger
from app.pipeline_metrics import PipelineMetricsManager
from app.retrieval.hybrid import HybridRetriever
from app.retrieval.milvus_store import MilvusConfig, MilvusVectorStore
from app.retrieval.bm25_index import BM25Index

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PipelineSubagentsDemo:
    """
    Demostración del pipeline completo de subagentes.
    """
    
    def __init__(self):
        """Inicializa la demostración."""
        # Crear directorio de logs
        Path("logs").mkdir(exist_ok=True)
        
        # Inicializar Context Manager y Logger
        self.context_manager = ContextManager(model_name="gpt-3.5-turbo")
        self.context_logger = ContextLogger()
        
        # Configuración de Milvus (modo simulado)
        milvus_config = MilvusConfig(
            uri="localhost:19530",
            collection_name="demo_knowledge",
            embedding_dim=384,
            index_type="HNSW",
            metric_type="IP"
        )
        
        # Inicializar almacén vectorial
        self.vector_store = MilvusVectorStore(config=milvus_config)
        
        # Inicializar índice BM25
        self.bm25_index = BM25Index()
        
        # Inicializar retriever híbrido
        self.hybrid_retriever = HybridRetriever(
            vector_store=self.vector_store,
            bm25_index=self.bm25_index
        )
        
        # Configuración del pipeline
        pipeline_config = PipelineConfig(
            enable_verification=True,
            max_retrieval_chunks=15,
            max_analysis_chunks=8,
            synthesis_max_tokens=1500,
            verification_threshold=0.75,
            enable_fallback=True,
            max_retries=3,
            timeout_seconds=30
        )
        
        # Inicializar orquestador
        self.orchestrator = SubagentOrchestrator(
            hybrid_retriever=self.hybrid_retriever,
            context_manager=self.context_manager,
            config=pipeline_config
        )
        
        # Inicializar gestor de métricas
        self.metrics_manager = PipelineMetricsManager(
            context_manager=self.context_manager,
            context_logger=self.context_logger
        )
        
        # Datos de ejemplo
        self.sample_chunks = []
        
        logger.info("PipelineSubagentsDemo inicializado")
    
    def create_sample_chunks(self):
        """Crea chunks de ejemplo para la demostración."""
        chunks_data = [
            {
                "id": "chunk_1",
                "doc_id": "doc_api",
                "title": "API REST Endpoints",
                "section": "Autenticación",
                "path": "docs/api.md",
                "line_start": 15,
                "line_end": 25,
                "text": "La API REST expone endpoints de autenticación en /auth/login y /auth/refresh. Los tokens JWT tienen expiración de 24 horas y se validan mediante middleware de autenticación. El endpoint /auth/logout implementa blacklisting de tokens.",
                "doc_type": "api_documentation",
                "tags": ["api", "rest", "autenticación", "jwt"],
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "id": "chunk_2",
                "doc_id": "doc_db",
                "title": "Configuración de Base de Datos",
                "section": "PostgreSQL",
                "path": "docs/database.md",
                "line_start": 30,
                "line_end": 40,
                "text": "La base de datos PostgreSQL se configura con connection pooling usando PgBouncer. El esquema incluye tablas para usuarios, sesiones, y logs de auditoría. Las migraciones se ejecutan automáticamente al iniciar la aplicación.",
                "doc_type": "database_documentation",
                "tags": ["postgresql", "database", "migraciones", "pooling"],
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "id": "chunk_3",
                "doc_id": "doc_deploy",
                "title": "Guía de Deployment",
                "section": "Docker Compose",
                "path": "docs/deployment.md",
                "line_start": 45,
                "line_end": 55,
                "text": "El deployment se realiza usando Docker Compose con servicios para la aplicación, base de datos, Redis cache, y Nginx reverse proxy. Las variables de entorno se configuran en archivos .env separados para cada ambiente.",
                "doc_type": "deployment_guide",
                "tags": ["docker", "deployment", "nginx", "redis"],
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "id": "chunk_4",
                "doc_id": "doc_monitoring",
                "title": "Sistema de Monitoreo",
                "section": "Prometheus + Grafana",
                "path": "docs/monitoring.md",
                "line_start": 20,
                "line_end": 30,
                "text": "El sistema de monitoreo utiliza Prometheus para recolección de métricas y Grafana para visualización. Se monitorean métricas de aplicación, base de datos, y infraestructura. Las alertas se configuran para CPU >80% y memoria >90%.",
                "doc_type": "monitoring_documentation",
                "tags": ["prometheus", "grafana", "monitoreo", "alertas"],
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "id": "chunk_5",
                "doc_id": "doc_testing",
                "title": "Estrategia de Testing",
                "section": "Tests Unitarios",
                "path": "docs/testing.md",
                "line_start": 35,
                "line_end": 45,
                "text": "La estrategia de testing incluye tests unitarios con Jest, tests de integración con Supertest, y tests end-to-end con Playwright. La cobertura objetivo es 80% y se ejecutan automáticamente en CI/CD pipeline.",
                "doc_type": "testing_documentation",
                "tags": ["testing", "jest", "supertest", "playwright", "ci-cd"],
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
        ]
        
        # Crear chunks para el sistema
        for chunk_data in chunks_data:
            # Generar embedding simulado
            embedding = np.random.rand(384).tolist()
            
            # Agregar a vector store (simulado)
            self.sample_chunks.append({
                "id": chunk_data["id"],
                "text": chunk_data["text"],
                "metadata": chunk_data,
                "embedding": embedding
            })
            
            # Agregar a BM25 index
            from app.retrieval.bm25_index import BM25Document
            doc = BM25Document(
                id=chunk_data["id"],
                text=chunk_data["text"],
                title=chunk_data["title"],
                section=chunk_data["section"],
                path=chunk_data["path"],
                line_start=chunk_data["line_start"],
                line_end=chunk_data["line_end"],
                doc_type=chunk_data["doc_type"],
                tags=chunk_data["tags"],
                created_at=chunk_data["created_at"],
                updated_at=chunk_data["updated_at"]
            )
            
            self.bm25_index.add_document(doc)
        
        logger.info(f"Creados {len(self.sample_chunks)} chunks de ejemplo")
    
    async def run_pipeline_demo(self):
        """Ejecuta demostración del pipeline completo."""
        print("\n🚀 DEMOSTRACIÓN DEL PIPELINE COMPLETO DE SUBAGENTES")
        print("=" * 70)
        
        # Consultas de ejemplo para diferentes tipos de tarea
        example_queries = [
            {
                "query": "¿Cómo configuro la autenticación JWT en la API?",
                "user_role": "developer",
                "risk_level": "medium",
                "description": "Consulta de configuración técnica"
            },
            {
                "query": "¿Qué métricas de monitoreo están disponibles y cómo configuro alertas?",
                "user_role": "devops",
                "risk_level": "high",
                "description": "Consulta de operaciones críticas"
            },
            {
                "query": "¿Cuál es la estrategia de testing y qué herramientas se usan?",
                "user_role": "qa_engineer",
                "risk_level": "low",
                "description": "Consulta de calidad y testing"
            }
        ]
        
        for i, query_info in enumerate(example_queries, 1):
            print(f"\n--- Consulta {i}: {query_info['description']} ---")
            print(f"Query: {query_info['query']}")
            print(f"Usuario: {query_info['user_role']}, Riesgo: {query_info['risk_level']}")
            
            # Ejecutar pipeline completo
            start_time = time.time()
            pipeline_result = await self.orchestrator.process_query(
                query=query_info['query'],
                user_role=query_info['user_role'],
                risk_level=query_info['risk_level']
            )
            total_time = time.time() - start_time
            
            # Mostrar resultados del pipeline
            self._display_pipeline_results(pipeline_result, total_time)
            
            # Registrar métricas
            await self.metrics_manager.record_pipeline_execution(pipeline_result)
            
            # Pausa entre consultas
            time.sleep(2)
    
    def _display_pipeline_results(self, pipeline_result, total_time):
        """Muestra los resultados del pipeline de forma detallada."""
        print(f"\n⏱️  Tiempo total: {total_time:.2f}s")
        print(f"✅ Éxito: {pipeline_result.success}")
        
        if pipeline_result.success:
            # Mostrar contrato generado
            print(f"\n📋 CONTRATO DE TAREA:")
            print(f"   Objetivo: {pipeline_result.contract.goal}")
            print(f"   Requisitos: {len(pipeline_result.contract.musts)}")
            print(f"   Formato: {pipeline_result.contract.format}")
            
            # Mostrar resultados de retrieval
            print(f"\n🔍 RETRIEVAL:")
            print(f"   Chunks recuperados: {len(pipeline_result.retrieved_chunks)}")
            print(f"   Fuentes principales: {[chunk.metadata.get('title', 'N/A')[:30] for chunk in pipeline_result.retrieved_chunks[:3]]}")
            
            # Mostrar análisis
            print(f"\n📊 ANÁLISIS:")
            analysis = pipeline_result.analysis
            if 'clusters' in analysis:
                print(f"   Clusters identificados: {len(analysis['clusters'])}")
            if 'gaps' in analysis:
                print(f"   Gaps detectados: {len(analysis.get('gaps', []))}")
            
            # Mostrar síntesis
            print(f"\n✍️  SÍNTESIS:")
            synthesis = pipeline_result.synthesis
            print(f"   Longitud: {len(synthesis)} caracteres")
            print(f"   Preview: {synthesis[:150]}...")
            
            # Mostrar verificación
            if pipeline_result.verification:
                print(f"\n🔍 VERIFICACIÓN:")
                verification = pipeline_result.verification
                print(f"   Score general: {verification.get('overall_score', 0):.2f}")
                print(f"   Estado: {verification.get('verification_status', 'N/A')}")
                
                # Mostrar scores detallados
                scores = verification.get('scores', {})
                if scores:
                    print(f"   Scores por componente:")
                    for component, score in scores.items():
                        print(f"     - {component}: {score:.2f}")
                
                # Mostrar recomendaciones
                recommendations = verification.get('recommendations', [])
                if recommendations:
                    print(f"   Recomendaciones: {len(recommendations)}")
                    for rec in recommendations[:3]:
                        print(f"     • {rec}")
            
            # Mostrar métricas del pipeline
            print(f"\n📈 MÉTRICAS DEL PIPELINE:")
            pipeline_metrics = pipeline_result.pipeline_metrics
            print(f"   Eficiencia: {pipeline_metrics.get('pipeline_efficiency', 0):.2f}")
            print(f"   Score de calidad: {pipeline_metrics.get('quality_score', 0):.2f}")
            
        else:
            # Mostrar errores
            print(f"\n❌ ERRORES:")
            for error in pipeline_result.errors:
                print(f"   • {error}")
            
            # Mostrar respuesta de fallback si existe
            if pipeline_result.final_response:
                print(f"\n⚠️  RESPUESTA DE FALLBACK:")
                print(f"   {pipeline_result.final_response[:200]}...")
    
    async def run_verification_demo(self):
        """Ejecuta demostración específica de verificación."""
        print("\n🔍 DEMOSTRACIÓN DE VERIFICACIÓN AUTOMÁTICA")
        print("=" * 60)
        
        # Consultas que pueden generar diferentes tipos de problemas
        verification_queries = [
            {
                "query": "¿Cuál es la versión exacta de PostgreSQL y qué puerto usa?",
                "expected_issues": ["información específica no disponible"]
            },
            {
                "query": "¿Cómo se implementa el sistema de cache y qué algoritmos usa?",
                "expected_issues": ["detalles técnicos específicos"]
            },
            {
                "query": "¿Cuáles son los endpoints de la API y sus parámetros exactos?",
                "expected_issues": ["especificaciones técnicas detalladas"]
            }
        ]
        
        for i, query_info in enumerate(verification_queries, 1):
            print(f"\n--- Verificación {i} ---")
            print(f"Query: {query_info['query']}")
            
            # Ejecutar pipeline
            pipeline_result = await self.orchestrator.process_query(
                query=query_info['query'],
                user_role="developer",
                risk_level="medium"
            )
            
            if pipeline_result.success and pipeline_result.verification:
                verification = pipeline_result.verification
                
                print(f"✅ Verificación completada")
                print(f"   Score general: {verification.get('overall_score', 0):.2f}")
                print(f"   Estado: {verification.get('verification_status', 'N/A')}")
                
                # Mostrar análisis detallado de verificación
                self._display_verification_details(verification)
                
                # Mostrar recomendaciones específicas
                recommendations = verification.get('recommendations', [])
                if recommendations:
                    print(f"\n💡 Recomendaciones de mejora:")
                    for rec in recommendations:
                        print(f"   • {rec}")
            
            time.sleep(1)
    
    def _display_verification_details(self, verification):
        """Muestra detalles de la verificación."""
        print(f"\n🔍 ANÁLISIS DETALLADO:")
        
        # Scores por componente
        scores = verification.get('scores', {})
        weights = verification.get('weights', {})
        
        for component in scores:
            score = scores[component]
            weight = weights.get(component, 0.0)
            contribution = score * weight
            print(f"   {component.upper()}: {score:.2f} (peso: {weight:.2f}, contribución: {contribution:.2f})")
        
        # Verificaciones específicas
        checks = [
            ("basic_check", "Verificación Básica"),
            ("hallucination_detection", "Detección de Alucinaciones"),
            ("contract_compliance", "Cumplimiento del Contrato"),
            ("coverage_check", "Cobertura de Fuentes"),
            ("consistency_check", "Consistencia Interna"),
            ("factual_check", "Precisión Factual")
        ]
        
        for check_key, check_name in checks:
            if check_key in verification:
                check_data = verification[check_key]
                if isinstance(check_data, dict):
                    score = check_data.get('score', 0.0)
                    print(f"   {check_name}: {score:.2f}")
    
    async def run_metrics_demo(self):
        """Ejecuta demostración de métricas integradas."""
        print("\n📊 DEMOSTRACIÓN DE MÉTRICAS INTEGRADAS")
        print("=" * 60)
        
        # Obtener rendimiento del pipeline
        performance = await self.metrics_manager.get_pipeline_performance()
        
        print(f"📈 RENDIMIENTO DEL PIPELINE (últimas 24h):")
        print(f"   Total de consultas: {performance.total_queries}")
        print(f"   Consultas exitosas: {performance.successful_queries}")
        print(f"   Consultas fallidas: {performance.failed_queries}")
        print(f"   Tasa de éxito: {performance.success_rate:.2%}")
        print(f"   Tiempo promedio: {performance.avg_execution_time:.2f}s")
        print(f"   Score promedio de verificación: {performance.avg_verification_score:.2f}")
        print(f"   Score promedio de calidad: {performance.avg_quality_score:.2f}")
        print(f"   Chunks promedio recuperados: {performance.avg_chunks_retrieved:.1f}")
        print(f"   Compresión promedio del contexto: {performance.avg_context_compression:.2f}")
        
        # Mostrar tendencia de rendimiento
        if performance.performance_trend:
            print(f"\n📈 TENDENCIA DE RENDIMIENTO:")
            for trend_point in performance.performance_trend[-5:]:  # Últimas 5 horas
                hour = datetime.fromisoformat(trend_point["hour"]).strftime("%H:%M")
                quality = trend_point["avg_quality_score"]
                time_avg = trend_point["avg_execution_time"]
                success = trend_point["success_count"]
                total = trend_point["total_queries"]
                
                print(f"   {hour}: Calidad {quality:.2f}, Tiempo {time_avg:.2f}s, Éxito {success}/{total}")
        
        # Mostrar resumen de métricas
        metrics_summary = self.metrics_manager.get_metrics_summary()
        print(f"\n📋 RESUMEN DE MÉTRICAS:")
        print(f"   Archivo: {metrics_summary.get('metrics_file', 'N/A')}")
        print(f"   Tamaño del cache: {metrics_summary.get('cache_size', 0)}")
        print(f"   Umbrales de alerta: {metrics_summary.get('alert_thresholds', {})}")
    
    async def run_health_check_demo(self):
        """Ejecuta demostración de health check del sistema."""
        print("\n🏥 DEMOSTRACIÓN DE HEALTH CHECK")
        print("=" * 60)
        
        # Health check del orquestador
        health_status = await self.orchestrator.health_check()
        
        print(f"🏥 ESTADO DE SALUD DEL SISTEMA:")
        print(f"   Estado general: {health_status['status']}")
        print(f"   Timestamp: {health_status['timestamp']}")
        
        # Estado de componentes
        components = health_status.get('components', {})
        for component_name, component_status in components.items():
            print(f"\n   {component_name.upper()}:")
            for key, value in component_status.items():
                if isinstance(value, float):
                    print(f"     {key}: {value:.2f}")
                else:
                    print(f"     {key}: {value}")
        
        # Health check del context manager
        context_stats = self.context_manager.get_stats()
        print(f"\n   CONTEXT MANAGER:")
        print(f"     Total queries: {context_stats.get('total_queries', 0)}")
        print(f"     Avg compression: {context_stats.get('avg_compression', 0):.2f}")
        print(f"     Avg efficiency: {context_stats.get('avg_efficiency', 0):.2f}")
    
    async def export_metrics_demo(self):
        """Ejecuta demostración de exportación de métricas."""
        print("\n📤 DEMOSTRACIÓN DE EXPORTACIÓN DE MÉTRICAS")
        print("=" * 60)
        
        try:
            # Exportar métricas en JSON
            json_file = await self.metrics_manager.export_metrics(format="json")
            print(f"✅ Métricas exportadas a JSON: {json_file}")
            
            # Exportar métricas en CSV
            csv_file = await self.metrics_manager.export_metrics(format="csv")
            print(f"✅ Métricas exportadas a CSV: {csv_file}")
            
            # Exportar métricas de las últimas 2 horas
            recent_metrics = await self.metrics_manager.export_metrics(
                format="json", 
                time_window=timedelta(hours=2)
            )
            print(f"✅ Métricas recientes exportadas: {recent_metrics}")
            
        except Exception as e:
            print(f"❌ Error exportando métricas: {e}")
    
    async def main(self):
        """Función principal de la demostración."""
        print("🚀 Pipeline Completo de Subagentes - Demostración PR-4")
        print("=" * 80)
        
        # Crear chunks de ejemplo
        print("\n📝 Creando chunks de ejemplo...")
        self.create_sample_chunks()
        
        # Ejecutar demostraciones
        await self.run_pipeline_demo()
        await self.run_verification_demo()
        await self.run_metrics_demo()
        await self.run_health_check_demo()
        await self.export_metrics_demo()
        
        # Instrucciones para próximos pasos
        print("\n🎯 PRÓXIMOS PASOS")
        print("=" * 60)
        print("1. Configurar Milvus real para mejor rendimiento:")
        print("   docker run -d --name milvus-standalone -p 19530:19530 milvusdb/milvus:latest")
        print("\n2. Ajustar umbrales de verificación:")
        print("   - verification_threshold: 0.8 para producción")
        print("   - max_retries: 2 para balancear calidad/velocidad")
        print("\n3. Configurar alertas personalizadas:")
        print("   - execution_time: 5.0s para consultas rápidas")
        print("   - verification_score: 0.9 para alta calidad")
        print("\n4. Integrar con sistema de monitoreo externo:")
        print("   - Prometheus para métricas del pipeline")
        print("   - Grafana para dashboards personalizados")
        
        print("\n🎉 Demostración del Pipeline Completo de Subagentes completada!")

if __name__ == "__main__":
    # Ejecutar demostración
    demo = PipelineSubagentsDemo()
    asyncio.run(demo.main())
