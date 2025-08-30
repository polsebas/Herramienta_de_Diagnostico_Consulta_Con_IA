#!/usr/bin/env python3
"""
Ejemplo de uso del Sistema de Retrieval Híbrido (PR-3)

Este script demuestra las nuevas funcionalidades del PR-3:
- Búsqueda híbrida BM25 + Vectorial + Reranking
- Integración con Milvus (modo simulado)
- Índice BM25 con metadatos enriquecidos
- Filtros avanzados y metadatos fuertes
"""

import asyncio
import logging
import time
from pathlib import Path
import sys
from datetime import datetime
import numpy as np

# Agregar el directorio app al path
sys.path.append(str(Path(__file__).parent / "app"))

from retrieval import (
    HybridRetriever, SearchResult, SearchFilters,
    MilvusVectorStore, MilvusConfig, ChunkData,
    BM25Index, BM25Document
)

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HybridRetrievalDemo:
    """
    Demostración del sistema de retrieval híbrido.
    """
    
    def __init__(self):
        """Inicializa la demostración."""
        # Crear directorio de logs
        Path("logs").mkdir(exist_ok=True)
        
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
        self.bm25_index = BM25Index(config={
            "k1": 1.5,
            "b": 0.75,
            "min_score": 0.1,
            "enable_stemming": True,
            "enable_stopwords": True,
            "language": "spanish"
        })
        
        # Inicializar retriever híbrido
        self.hybrid_retriever = HybridRetriever(
            vector_store=self.vector_store,
            bm25_index=self.bm25_index,
            config={
                "hybrid_weights": {"vector": 0.7, "bm25": 0.3},
                "rerank_top_k": 50,
                "enable_filters": True,
                "enable_reranking": True,
                "metadata_boost": 1.2,
                "freshness_boost": 1.1
            }
        )
        
        # Datos de ejemplo
        self.sample_chunks = []
        
        logger.info("HybridRetrievalDemo inicializado")
    
    def create_sample_chunks(self):
        """Crea chunks de ejemplo para la demostración."""
        chunks_data = [
            {
                "id": "chunk_1",
                "doc_id": "doc_auth",
                "title": "Sistema de Autenticación",
                "section": "JWT Tokens",
                "path": "docs/autenticacion.md",
                "line_start": 25,
                "line_end": 35,
                "text": "El sistema de autenticación utiliza JWT tokens con expiración de 24 horas. Los tokens se validan en cada request y se renuevan automáticamente cuando están próximos a expirar. La implementación incluye refresh tokens y blacklisting para mayor seguridad.",
                "doc_type": "documentation",
                "tags": ["autenticación", "jwt", "seguridad"],
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "id": "chunk_2",
                "doc_id": "doc_setup",
                "title": "Guía de Instalación",
                "section": "Prerrequisitos",
                "path": "docs/instalacion.md",
                "line_start": 10,
                "line_end": 20,
                "text": "Para configurar el entorno de desarrollo, necesitas instalar Python 3.8+, Node.js 16+, y configurar las variables de entorno en el archivo .env. También se requiere Docker para ejecutar los servicios de base de datos. Asegúrate de tener al menos 8GB de RAM disponible.",
                "doc_type": "guide",
                "tags": ["instalación", "desarrollo", "docker"],
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "id": "chunk_3",
                "doc_id": "doc_troubleshoot",
                "title": "Resolución de Problemas",
                "section": "Errores Comunes",
                "path": "docs/troubleshooting.md",
                "line_start": 40,
                "line_end": 50,
                "text": "Los errores comunes incluyen: timeout de conexión a la base de datos, credenciales inválidas, y problemas de red. Verifica la configuración del firewall y las credenciales de API antes de reportar un bug. Revisa los logs del sistema para obtener más detalles.",
                "doc_type": "troubleshooting",
                "tags": ["errores", "debugging", "logs"],
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "id": "chunk_4",
                "doc_id": "doc_arch",
                "title": "Arquitectura del Sistema",
                "section": "Microservicios",
                "path": "docs/arquitectura.md",
                "line_start": 15,
                "line_end": 25,
                "text": "La arquitectura del sistema está basada en microservicios con comunicación asíncrona. Cada servicio tiene su propia base de datos y se comunica con otros servicios a través de APIs REST y mensajes Kafka. El sistema utiliza un patrón de event-driven architecture.",
                "doc_type": "architecture",
                "tags": ["microservicios", "kafka", "event-driven"],
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "id": "chunk_5",
                "doc_id": "doc_logging",
                "title": "Sistema de Logging",
                "section": "Configuración",
                "path": "docs/logging.md",
                "line_start": 30,
                "line_end": 40,
                "text": "El sistema de logging utiliza Winston con diferentes niveles: error, warn, info, debug. Los logs se almacenan en archivos rotativos y también se envían a un sistema centralizado de monitoreo. Se implementa correlación de requests mediante trace IDs.",
                "doc_type": "configuration",
                "tags": ["logging", "winston", "monitoreo"],
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
        ]
        
        # Crear chunks para Milvus
        for chunk_data in chunks_data:
            # Generar embedding simulado
            embedding = np.random.rand(384).tolist()
            
            chunk = ChunkData(
                id=chunk_data["id"],
                doc_id=chunk_data["doc_id"],
                title=chunk_data["title"],
                section=chunk_data["section"],
                path=chunk_data["path"],
                line_start=chunk_data["line_start"],
                line_end=chunk_data["line_end"],
                text=chunk_data["text"],
                embedding=embedding,
                doc_type=chunk_data["doc_type"],
                tags=chunk_data["tags"],
                created_at=int(chunk_data["created_at"].timestamp()),
                updated_at=int(chunk_data["updated_at"].timestamp()),
                metadata={"source": "demo", "quality": "high"}
            )
            
            self.sample_chunks.append(chunk)
        
        # Crear documentos para BM25
        for chunk_data in chunks_data:
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
    
    async def populate_vector_store(self):
        """Pobla el almacén vectorial con chunks de ejemplo."""
        try:
            # Agregar chunks a Milvus
            success = await self.vector_store.add_chunks(self.sample_chunks)
            
            if success:
                logger.info("Vector store poblado exitosamente")
            else:
                logger.warning("Vector store poblado con algunos errores")
            
            # Mostrar estadísticas
            stats = await self.vector_store.get_collection_stats()
            logger.info(f"Estadísticas del vector store: {stats}")
            
        except Exception as e:
            logger.error(f"Error poblando vector store: {e}")
    
    async def run_hybrid_search_demo(self):
        """Ejecuta demostración de búsqueda híbrida."""
        print("\n🚀 DEMOSTRACIÓN DE BÚSQUEDA HÍBRIDA")
        print("=" * 60)
        
        # Consultas de ejemplo
        example_queries = [
            "¿Cómo configuro la autenticación JWT?",
            "¿Qué errores comunes puedo encontrar?",
            "¿Cómo funciona la arquitectura de microservicios?",
            "¿Qué sistema de logging se usa?",
            "¿Cuáles son los prerrequisitos de instalación?"
        ]
        
        for i, query in enumerate(example_queries, 1):
            print(f"\n--- Consulta {i} ---")
            print(f"Query: {query}")
            
            # Búsqueda híbrida
            start_time = time.time()
            results = self.hybrid_retriever.search(query, top_k=5)
            search_time = time.time() - start_time
            
            print(f"⏱️  Tiempo de búsqueda: {search_time:.3f}s")
            print(f"📊 Resultados encontrados: {len(results)}")
            
            # Mostrar resultados
            for j, result in enumerate(results[:3], 1):  # Top 3
                print(f"\n  {j}. Score: {result.score:.3f}")
                print(f"     Título: {result.metadata.get('title', 'N/A')}")
                print(f"     Sección: {result.metadata.get('section', 'N/A')}")
                print(f"     Fuente: {result.source}")
                print(f"     Relevancia: {result.relevance_score:.3f}")
                print(f"     Calidad: {result.quality_score:.3f}")
                print(f"     Frescura: {result.freshness_score:.3f}")
                print(f"     Texto: {result.text[:100]}...")
            
            # Pausa entre consultas
            time.sleep(1)
    
    async def run_filtered_search_demo(self):
        """Ejecuta demostración de búsqueda con filtros."""
        print("\n🔍 DEMOSTRACIÓN DE BÚSQUEDA CON FILTROS")
        print("=" * 60)
        
        # Filtros de ejemplo
        filter_examples = [
            {
                "name": "Por tipo de documento",
                "filters": SearchFilters(doc_type="documentation", min_score=0.3)
            },
            {
                "name": "Por sección específica",
                "filters": SearchFilters(section="JWT Tokens", min_score=0.3)
            },
            {
                "name": "Por tags",
                "filters": SearchFilters(min_score=0.3)  # Los filtros por tags se aplican en el código
            }
        ]
        
        query = "autenticación y seguridad"
        
        for filter_example in filter_examples:
            print(f"\n--- {filter_example['name']} ---")
            print(f"Query: {query}")
            print(f"Filtros: {filter_example['filters']}")
            
            # Búsqueda con filtros
            start_time = time.time()
            results = self.hybrid_retriever.search(query, top_k=5, filters=filter_example['filters'])
            search_time = time.time() - start_time
            
            print(f"⏱️  Tiempo de búsqueda: {search_time:.3f}s")
            print(f"📊 Resultados filtrados: {len(results)}")
            
            # Mostrar resultados
            for j, result in enumerate(results[:2], 1):  # Top 2
                print(f"\n  {j}. Score: {result.score:.3f}")
                print(f"     Título: {result.metadata.get('title', 'N/A')}")
                print(f"     Tipo: {result.metadata.get('doc_type', 'N/A')}")
                print(f"     Sección: {result.metadata.get('section', 'N/A')}")
            
            time.sleep(1)
    
    async def run_bm25_demo(self):
        """Ejecuta demostración específica de BM25."""
        print("\n📚 DEMOSTRACIÓN DE BÚSQUEDA BM25")
        print("=" * 60)
        
        # Consultas específicas para BM25
        bm25_queries = [
            "timeout conexión base datos",
            "microservicios kafka",
            "winston logging niveles",
            "Python Node.js Docker"
        ]
        
        for i, query in enumerate(bm25_queries, 1):
            print(f"\n--- Consulta BM25 {i} ---")
            print(f"Query: {query}")
            
            # Búsqueda BM25 directa
            start_time = time.time()
            results = self.bm25_index.search(query, top_k=3)
            search_time = time.time() - start_time
            
            print(f"⏱️  Tiempo de búsqueda: {search_time:.3f}s")
            print(f"📊 Resultados BM25: {len(results)}")
            
            # Mostrar resultados
            for j, result in enumerate(results, 1):
                print(f"\n  {j}. Score BM25: {result.score:.3f}")
                print(f"     Título: {result.metadata.get('title', 'N/A')}")
                print(f"     Sección: {result.metadata.get('section', 'N/A')}")
                print(f"     Texto: {result.text[:80]}...")
            
            time.sleep(1)
    
    async def run_vector_search_demo(self):
        """Ejecuta demostración específica de búsqueda vectorial."""
        print("\n🧠 DEMOSTRACIÓN DE BÚSQUEDA VECTORIAL")
        print("=" * 60)
        
        # Consultas para búsqueda vectorial
        vector_queries = [
            "sistema de autenticación y tokens",
            "arquitectura de microservicios y comunicación",
            "configuración de logging y monitoreo"
        ]
        
        for i, query in enumerate(vector_queries, 1):
            print(f"\n--- Consulta Vectorial {i} ---")
            print(f"Query: {query}")
            
            # Generar embedding simulado para la consulta
            query_embedding = np.random.rand(384).tolist()
            
            # Búsqueda vectorial directa
            start_time = time.time()
            results = await self.vector_store.similarity_search(query_embedding, top_k=3)
            search_time = time.time() - start_time
            
            print(f"⏱️  Tiempo de búsqueda: {search_time:.3f}s")
            print(f"📊 Resultados vectoriales: {len(results)}")
            
            # Mostrar resultados
            for j, result in enumerate(results, 1):
                print(f"\n  {j}. Score: {result['score']:.3f}")
                print(f"     Título: {result['metadata'].get('title', 'N/A')}")
                print(f"     Sección: {result['metadata'].get('section', 'N/A')}")
                print(f"     Texto: {result['metadata'].get('text', 'N/A')[:80]}...")
            
            time.sleep(1)
    
    def show_system_stats(self):
        """Muestra estadísticas del sistema."""
        print("\n📊 ESTADÍSTICAS DEL SISTEMA")
        print("=" * 60)
        
        # Estadísticas del índice BM25
        bm25_stats = self.bm25_index.get_stats()
        print(f"📚 Índice BM25:")
        print(f"   - Total documentos: {bm25_stats['total_documents']}")
        print(f"   - Total tokens: {bm25_stats['total_tokens']}")
        print(f"   - Longitud promedio: {bm25_stats['avg_document_length']:.1f}")
        print(f"   - Última actualización: {bm25_stats['last_updated']}")
        
        # Estadísticas del retriever híbrido
        hybrid_stats = self.hybrid_retriever.get_search_stats()
        print(f"\n🔍 Retriever Híbrido:")
        print(f"   - Vector store disponible: {hybrid_stats['vector_store_available']}")
        print(f"   - BM25 index disponible: {hybrid_stats['bm25_index_available']}")
        print(f"   - Filtros habilitados: {hybrid_stats['filters_enabled']}")
        print(f"   - Reranking habilitado: {hybrid_stats['reranking_enabled']}")
        print(f"   - Tamaño del cache: {hybrid_stats['cache_size']}")
        
        # Configuración
        print(f"\n⚙️  Configuración:")
        print(f"   - Pesos híbridos: {hybrid_stats['config']['hybrid_weights']}")
        print(f"   - Top-K reranking: {hybrid_stats['config']['rerank_top_k']}")
        print(f"   - Score mínimo: {hybrid_stats['config']['min_hybrid_score']}")
    
    async def run_performance_test(self):
        """Ejecuta test de rendimiento del sistema."""
        print("\n⚡ TEST DE RENDIMIENTO")
        print("=" * 60)
        
        # Consultas de test
        test_queries = [
            "autenticación",
            "microservicios",
            "logging",
            "instalación",
            "errores",
            "configuración",
            "base de datos",
            "API REST"
        ]
        
        total_time = 0
        total_results = 0
        
        for query in test_queries:
            start_time = time.time()
            results = self.hybrid_retriever.search(query, top_k=10)
            search_time = time.time() - start_time
            
            total_time += search_time
            total_results += len(results)
            
            print(f"Query: {query[:20]:<20} | Tiempo: {search_time:.3f}s | Resultados: {len(results)}")
        
        # Estadísticas de rendimiento
        avg_time = total_time / len(test_queries)
        avg_results = total_results / len(test_queries)
        
        print(f"\n📈 Estadísticas de Rendimiento:")
        print(f"   - Tiempo promedio por consulta: {avg_time:.3f}s")
        print(f"   - Resultados promedio por consulta: {avg_results:.1f}")
        print(f"   - Consultas por segundo: {1/avg_time:.1f}")
    
    async def main(self):
        """Función principal de la demostración."""
        print("🚀 Sistema de Retrieval Híbrido - Demostración PR-3")
        print("=" * 70)
        
        # Crear chunks de ejemplo
        print("\n📝 Creando chunks de ejemplo...")
        self.create_sample_chunks()
        
        # Poblar vector store
        print("\n🗄️  Poblando vector store...")
        await self.populate_vector_store()
        
        # Ejecutar demostraciones
        await self.run_hybrid_search_demo()
        await self.run_filtered_search_demo()
        await self.run_bm25_demo()
        await self.run_vector_search_demo()
        
        # Mostrar estadísticas
        self.show_system_stats()
        
        # Test de rendimiento
        await self.run_performance_test()
        
        # Instrucciones para próximos pasos
        print("\n🎯 PRÓXIMOS PASOS")
        print("=" * 60)
        print("1. Configurar Milvus real:")
        print("   docker run -d --name milvus-standalone -p 19530:19530 milvusdb/milvus:latest")
        print("\n2. Ejecutar con Milvus real:")
        print("   export MILVUS_URI=localhost:19530")
        print("\n3. Probar con datos reales:")
        print("   - Indexar documentos del proyecto")
        print("   - Configurar embeddings reales")
        print("   - Ajustar parámetros de BM25")
        
        print("\n🎉 Demostración del Sistema de Retrieval Híbrido completada!")

if __name__ == "__main__":
    # Ejecutar demostración
    demo = HybridRetrievalDemo()
    asyncio.run(demo.main())
