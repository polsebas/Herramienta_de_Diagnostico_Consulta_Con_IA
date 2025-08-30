"""
Módulo de Retrieval Híbrido

Este módulo proporciona funcionalidades avanzadas de recuperación de información:
- Búsqueda híbrida (BM25 + Vectorial + Reranking)
- Integración con Milvus para almacenamiento vectorial
- Índice BM25 para búsqueda por palabras clave
- Metadatos enriquecidos y filtros avanzados
"""

from .hybrid import HybridRetriever, SearchResult, SearchFilters
from .milvus_store import MilvusVectorStore, MilvusConfig, ChunkData
from .bm25_index import BM25Index, BM25Document, BM25SearchResult

__all__ = [
    # Hybrid Retriever
    "HybridRetriever",
    "SearchResult", 
    "SearchFilters",
    
    # Milvus Store
    "MilvusVectorStore",
    "MilvusConfig",
    "ChunkData",
    
    # BM25 Index
    "BM25Index",
    "BM25Document",
    "BM25SearchResult"
]

# Versión del módulo
__version__ = "1.0.0"

# Información del módulo
__description__ = "Sistema de Retrieval Híbrido con BM25, Vectorial y Reranking"
__author__ = "Next Level RAG System"
__license__ = "MIT"
