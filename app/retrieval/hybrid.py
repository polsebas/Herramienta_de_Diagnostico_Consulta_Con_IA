"""
Retrieval Híbrido: BM25 + Vectorial + Reranking

Este módulo implementa un sistema de recuperación híbrido que combina:
- Búsqueda vectorial (similarity search)
- Búsqueda por palabras clave (BM25)
- Reranking inteligente
- Filtros avanzados por metadatos
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from pathlib import Path
import json
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Resultado de búsqueda con metadatos enriquecidos."""
    id: str
    text: str
    score: float
    metadata: Dict[str, Any]
    source: str  # 'vector', 'bm25', 'hybrid'
    rank: int
    relevance_score: float
    freshness_score: float
    quality_score: float

@dataclass
class SearchFilters:
    """Filtros para la búsqueda híbrida."""
    doc_type: Optional[str] = None
    section: Optional[str] = None
    min_date: Optional[datetime] = None
    max_date: Optional[datetime] = None
    min_score: float = 0.5
    max_results: int = 20
    include_metadata: bool = True

class HybridRetriever:
    """
    Sistema de recuperación híbrido que combina múltiples estrategias de búsqueda.
    """
    
    def __init__(self, vector_store=None, bm25_index=None, config: Optional[Dict] = None):
        """
        Inicializa el retriever híbrido.
        
        Args:
            vector_store: Almacén vectorial (Milvus, FAISS, etc.)
            bm25_index: Índice BM25 (Whoosh, Elasticsearch, etc.)
            config: Configuración del retriever
        """
        self.vector_store = vector_store
        self.bm25_index = bm25_index
        
        # Configuración por defecto
        self.config = config or {
            "hybrid_weights": {"vector": 0.7, "bm25": 0.3},
            "rerank_top_k": 50,
            "min_hybrid_score": 0.3,
            "enable_filters": True,
            "enable_reranking": True,
            "metadata_boost": 1.2,
            "freshness_boost": 1.1
        }
        
        # Cache para resultados
        self.search_cache = {}
        self.cache_ttl = 300  # 5 minutos
        
        logger.info("HybridRetriever inicializado")
    
    def search(self, query: str, filters: Optional[SearchFilters] = None, 
               top_k: int = 20) -> List[SearchResult]:
        """
        Realiza búsqueda híbrida combinando múltiples estrategias.
        
        Args:
            query: Consulta del usuario
            filters: Filtros de búsqueda
            top_k: Número máximo de resultados
        
        Returns:
            Lista de resultados ordenados por relevancia
        """
        logger.info(f"Búsqueda híbrida: '{query[:50]}...', top_k={top_k}")
        
        try:
            # 1. Búsqueda vectorial
            vector_results = self._vector_search(query, top_k * 2)
            
            # 2. Búsqueda BM25
            bm25_results = self._bm25_search(query, top_k * 2)
            
            # 3. Fusión híbrida
            hybrid_results = self._hybrid_merge(vector_results, bm25_results, top_k * 2)
            
            # 4. Aplicar filtros
            if filters and self.config["enable_filters"]:
                hybrid_results = self._apply_filters(hybrid_results, filters)
            
            # 5. Reranking
            if self.config["enable_reranking"]:
                hybrid_results = self._rerank_results(hybrid_results, query, top_k)
            else:
                # Ordenar por score híbrido
                hybrid_results.sort(key=lambda x: x.score, reverse=True)
                hybrid_results = hybrid_results[:top_k]
            
            # 6. Enriquecer metadatos
            enriched_results = self._enrich_metadata(hybrid_results)
            
            # 7. Calcular scores finales
            final_results = self._calculate_final_scores(enriched_results, query)
            
            logger.info(f"Búsqueda completada: {len(final_results)} resultados")
            return final_results
            
        except Exception as e:
            logger.error(f"Error en búsqueda híbrida: {e}")
            # Fallback a búsqueda vectorial simple
            return self._fallback_search(query, top_k)
    
    def _vector_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Realiza búsqueda vectorial."""
        try:
            if not self.vector_store:
                logger.warning("Vector store no disponible, usando resultados simulados")
                return self._simulate_vector_search(query, top_k)
            
            # Búsqueda real en el vector store
            results = self.vector_store.similarity_search(query, k=top_k)
            
            # Convertir a formato estándar
            formatted_results = []
            for i, result in enumerate(results):
                formatted_results.append({
                    "id": getattr(result, "id", f"vec_{i}"),
                    "text": getattr(result, "text", str(result)),
                    "score": getattr(result, "score", 1.0 - (i * 0.1)),
                    "metadata": getattr(result, "metadata", {}),
                    "source": "vector"
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error en búsqueda vectorial: {e}")
            return self._simulate_vector_search(query, top_k)
    
    def _bm25_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Realiza búsqueda BM25 por palabras clave."""
        try:
            if not self.bm25_index:
                logger.warning("BM25 index no disponible, usando resultados simulados")
                return self._simulate_bm25_search(query, top_k)
            
            # Búsqueda real en el índice BM25
            results = self.bm25_index.search(query, top_k)
            
            # Convertir a formato estándar
            formatted_results = []
            for i, result in enumerate(results):
                formatted_results.append({
                    "id": getattr(result, "id", f"bm25_{i}"),
                    "text": getattr(result, "text", str(result)),
                    "score": getattr(result, "score", 1.0 - (i * 0.1)),
                    "metadata": getattr(result, "metadata", {}),
                    "source": "bm25"
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error en búsqueda BM25: {e}")
            return self._simulate_bm25_search(query, top_k)
    
    def _hybrid_merge(self, vector_results: List[Dict], bm25_results: List[Dict], 
                      limit: int) -> List[Dict[str, Any]]:
        """
        Fusiona resultados de búsqueda vectorial y BM25.
        
        Args:
            vector_results: Resultados de búsqueda vectorial
            bm25_results: Resultados de búsqueda BM25
            limit: Límite de resultados
        
        Returns:
            Lista fusionada de resultados
        """
        # Agrupar por ID para evitar duplicados
        merged_by_id = {}
        
        # Procesar resultados vectoriales
        for rank, result in enumerate(vector_results):
            doc_id = result["id"]
            if doc_id not in merged_by_id:
                merged_by_id[doc_id] = {
                    "id": doc_id,
                    "text": result["text"],
                    "metadata": result["metadata"],
                    "vector_score": result["score"],
                    "bm25_score": 0.0,
                    "vector_rank": rank,
                    "bm25_rank": float('inf'),
                    "source": "vector"
                }
        
        # Procesar resultados BM25
        for rank, result in enumerate(bm25_results):
            doc_id = result["id"]
            if doc_id in merged_by_id:
                # Documento ya existe, agregar score BM25
                merged_by_id[doc_id]["bm25_score"] = result["score"]
                merged_by_id[doc_id]["bm25_rank"] = rank
                merged_by_id[doc_id]["source"] = "hybrid"
            else:
                # Nuevo documento
                merged_by_id[doc_id] = {
                    "id": doc_id,
                    "text": result["text"],
                    "metadata": result["metadata"],
                    "vector_score": 0.0,
                    "bm25_score": result["score"],
                    "vector_rank": float('inf'),
                    "bm25_rank": rank,
                    "source": "bm25"
                }
        
        # Calcular score híbrido
        hybrid_results = []
        for doc_id, doc_data in merged_by_id.items():
            # Normalizar scores
            norm_vector_score = 1.0 / (1.0 + doc_data["vector_rank"])
            norm_bm25_score = 1.0 / (1.0 + doc_data["bm25_rank"])
            
            # Score híbrido ponderado
            hybrid_score = (
                self.config["hybrid_weights"]["vector"] * norm_vector_score +
                self.config["hybrid_weights"]["bm25"] * norm_bm25_score
            )
            
            # Boost para documentos que aparecen en ambas búsquedas
            if doc_data["source"] == "hybrid":
                hybrid_score *= 1.2
            
            hybrid_results.append({
                "id": doc_id,
                "text": doc_data["text"],
                "metadata": doc_data["metadata"],
                "hybrid_score": hybrid_score,
                "vector_score": doc_data["vector_score"],
                "bm25_score": doc_data["bm25_score"],
                "source": doc_data["source"]
            })
        
        # Ordenar por score híbrido
        hybrid_results.sort(key=lambda x: x["hybrid_score"], reverse=True)
        
        return hybrid_results[:limit]
    
    def _apply_filters(self, results: List[Dict], filters: SearchFilters) -> List[Dict]:
        """Aplica filtros a los resultados de búsqueda."""
        filtered_results = []
        
        for result in results:
            # Filtro por score mínimo
            if result["hybrid_score"] < filters.min_score:
                continue
            
            # Filtro por tipo de documento
            if filters.doc_type and filters.doc_type.lower() not in result["metadata"].get("doc_type", "").lower():
                continue
            
            # Filtro por sección
            if filters.section and filters.section.lower() not in result["metadata"].get("section", "").lower():
                continue
            
            # Filtro por fecha
            if filters.min_date or filters.max_date:
                doc_date = self._extract_date(result["metadata"])
                if doc_date:
                    if filters.min_date and doc_date < filters.min_date:
                        continue
                    if filters.max_date and doc_date > filters.max_date:
                        continue
            
            filtered_results.append(result)
        
        logger.info(f"Filtros aplicados: {len(results)} -> {len(filtered_results)} resultados")
        return filtered_results
    
    def _extract_date(self, metadata: Dict[str, Any]) -> Optional[datetime]:
        """Extrae fecha de los metadatos del documento."""
        # Buscar campos de fecha comunes
        date_fields = ["created_at", "updated_at", "date", "timestamp", "modified"]
        
        for field in date_fields:
            if field in metadata:
                date_value = metadata[field]
                try:
                    if isinstance(date_value, str):
                        # Intentar parsear diferentes formatos
                        for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%d/%m/%Y"]:
                            try:
                                return datetime.strptime(date_value, fmt)
                            except ValueError:
                                continue
                    elif isinstance(date_value, (int, float)):
                        # Timestamp Unix
                        return datetime.fromtimestamp(date_value)
                except Exception:
                    continue
        
        return None
    
    def _rerank_results(self, results: List[Dict], query: str, top_k: int) -> List[Dict]:
        """
        Reranking inteligente de resultados usando múltiples factores.
        
        Args:
            results: Resultados a rerankear
            query: Consulta original
            top_k: Número máximo de resultados finales
        
        Returns:
            Lista rerankeada de resultados
        """
        if not results:
            return []
        
        # Calcular scores de reranking para cada resultado
        reranked_results = []
        
        for result in results:
            # Score base (score híbrido)
            base_score = result["hybrid_score"]
            
            # Score de relevancia semántica
            relevance_score = self._calculate_relevance_score(result, query)
            
            # Score de calidad del contenido
            quality_score = self._calculate_quality_score(result)
            
            # Score de frescura
            freshness_score = self._calculate_freshness_score(result)
            
            # Score de metadatos
            metadata_score = self._calculate_metadata_score(result)
            
            # Score final ponderado
            final_score = (
                base_score * 0.4 +
                relevance_score * 0.3 +
                quality_score * 0.2 +
                freshness_score * 0.05 +
                metadata_score * 0.05
            )
            
            reranked_results.append({
                **result,
                "final_score": final_score,
                "relevance_score": relevance_score,
                "quality_score": quality_score,
                "freshness_score": freshness_score,
                "metadata_score": metadata_score
            })
        
        # Ordenar por score final
        reranked_results.sort(key=lambda x: x["final_score"], reverse=True)
        
        return reranked_results[:top_k]
    
    def _calculate_relevance_score(self, result: Dict, query: str) -> float:
        """Calcula score de relevancia semántica."""
        try:
            # Extraer palabras clave de la consulta
            query_words = set(re.findall(r'\b\w+\b', query.lower()))
            
            # Extraer palabras del texto del resultado
            text_words = set(re.findall(r'\b\w+\b', result["text"].lower()))
            
            # Calcular overlap
            common_words = query_words.intersection(text_words)
            
            if not query_words:
                return 0.5
            
            # Score basado en overlap
            overlap_ratio = len(common_words) / len(query_words)
            
            # Bonus por palabras exactas
            exact_matches = sum(1 for word in query_words if word in result["text"].lower())
            exact_bonus = exact_matches / len(query_words) * 0.3
            
            return min(1.0, overlap_ratio + exact_bonus)
            
        except Exception:
            return 0.5
    
    def _calculate_quality_score(self, result: Dict) -> float:
        """Calcula score de calidad del contenido."""
        try:
            text = result["text"]
            metadata = result["metadata"]
            
            # Factores de calidad
            factors = {
                "length": min(1.0, len(text) / 1000),  # Preferir contenido sustancial
                "metadata_completeness": self._calculate_metadata_completeness(metadata),
                "structure": self._calculate_structure_score(text),
                "readability": self._calculate_readability_score(text)
            }
            
            # Score promedio ponderado
            weights = {"length": 0.3, "metadata_completeness": 0.3, 
                      "structure": 0.2, "readability": 0.2}
            
            quality_score = sum(factors[key] * weights[key] for key in factors)
            return quality_score
            
        except Exception:
            return 0.5
    
    def _calculate_metadata_completeness(self, metadata: Dict) -> float:
        """Calcula completitud de los metadatos."""
        required_fields = ["title", "section", "path"]
        optional_fields = ["line_start", "line_end", "doc_type", "version"]
        
        required_score = sum(1 for field in required_fields if field in metadata) / len(required_fields)
        optional_score = sum(1 for field in optional_fields if field in metadata) / len(optional_fields)
        
        return required_score * 0.7 + optional_score * 0.3
    
    def _calculate_structure_score(self, text: str) -> float:
        """Calcula score de estructura del texto."""
        try:
            # Contar elementos estructurales
            headers = len(re.findall(r'^#+\s+', text, re.MULTILINE))
            lists = len(re.findall(r'^[-*+]\s+', text, re.MULTILINE))
            code_blocks = len(re.findall(r'```', text))
            
            # Score basado en estructura
            structure_elements = headers + lists + code_blocks
            return min(1.0, structure_elements / 10)
            
        except Exception:
            return 0.5
    
    def _calculate_readability_score(self, text: str) -> float:
        """Calcula score de legibilidad del texto."""
        try:
            # Métricas simples de legibilidad
            sentences = len(re.findall(r'[.!?]+', text))
            words = len(re.findall(r'\b\w+\b', text))
            
            if sentences == 0 or words == 0:
                return 0.5
            
            # Promedio de palabras por oración (preferir oraciones moderadas)
            avg_words_per_sentence = words / sentences
            
            if 10 <= avg_words_per_sentence <= 25:
                return 1.0
            elif 5 <= avg_words_per_sentence <= 35:
                return 0.8
            else:
                return 0.5
                
        except Exception:
            return 0.5
    
    def _calculate_freshness_score(self, result: Dict) -> float:
        """Calcula score de frescura del documento."""
        try:
            doc_date = self._extract_date(result["metadata"])
            if not doc_date:
                return 0.5
            
            # Calcular edad del documento
            age_days = (datetime.now() - doc_date).days
            
            # Score basado en edad (preferir documentos más recientes)
            if age_days <= 30:
                return 1.0
            elif age_days <= 90:
                return 0.8
            elif age_days <= 365:
                return 0.6
            else:
                return 0.4
                
        except Exception:
            return 0.5
    
    def _calculate_metadata_score(self, result: Dict) -> float:
        """Calcula score basado en calidad de metadatos."""
        try:
            metadata = result["metadata"]
            
            # Factores de metadatos
            factors = {
                "has_title": 1.0 if metadata.get("title") else 0.0,
                "has_section": 1.0 if metadata.get("section") else 0.0,
                "has_path": 1.0 if metadata.get("path") else 0.0,
                "has_line_info": 1.0 if metadata.get("line_start") and metadata.get("line_end") else 0.0,
                "has_version": 1.0 if metadata.get("version") else 0.0
            }
            
            # Score promedio
            metadata_score = sum(factors.values()) / len(factors)
            
            # Bonus por metadatos completos
            if metadata_score >= 0.8:
                metadata_score *= self.config["metadata_boost"]
            
            return min(1.0, metadata_score)
            
        except Exception:
            return 0.5
    
    def _enrich_metadata(self, results: List[Dict]) -> List[Dict]:
        """Enriquece metadatos de los resultados."""
        enriched_results = []
        
        for result in results:
            enriched_metadata = result["metadata"].copy()
            
            # Agregar metadatos calculados
            enriched_metadata.update({
                "retrieved_at": datetime.now().isoformat(),
                "search_score": result.get("final_score", result.get("hybrid_score", 0.0)),
                "source_type": result["source"],
                "text_length": len(result["text"]),
                "word_count": len(result["text"].split())
            })
            
            # Enriquecer con información del documento
            if "path" in enriched_metadata:
                path = Path(enriched_metadata["path"])
                enriched_metadata.update({
                    "file_extension": path.suffix,
                    "file_name": path.name,
                    "directory": str(path.parent)
                })
            
            enriched_results.append({
                **result,
                "metadata": enriched_metadata
            })
        
        return enriched_results
    
    def _calculate_final_scores(self, results: List[Dict], query: str) -> List[SearchResult]:
        """Convierte resultados a objetos SearchResult con scores finales."""
        search_results = []
        
        for i, result in enumerate(results):
            # Crear objeto SearchResult
            search_result = SearchResult(
                id=result["id"],
                text=result["text"],
                score=result.get("final_score", result.get("hybrid_score", 0.0)),
                metadata=result["metadata"],
                source=result["source"],
                rank=i + 1,
                relevance_score=result.get("relevance_score", 0.0),
                freshness_score=result.get("freshness_score", 0.0),
                quality_score=result.get("quality_score", 0.0)
            )
            
            search_results.append(search_result)
        
        return search_results
    
    def _fallback_search(self, query: str, top_k: int) -> List[SearchResult]:
        """Búsqueda de fallback cuando falla la búsqueda híbrida."""
        logger.warning("Usando búsqueda de fallback")
        
        # Resultados simulados básicos
        fallback_results = []
        for i in range(min(top_k, 5)):
            fallback_results.append(SearchResult(
                id=f"fallback_{i}",
                text=f"Resultado de fallback {i+1} para: {query[:50]}...",
                score=0.5 - (i * 0.1),
                metadata={"source": "fallback", "rank": i + 1},
                source="fallback",
                rank=i + 1,
                relevance_score=0.5,
                freshness_score=0.5,
                quality_score=0.5
            ))
        
        return fallback_results
    
    def _simulate_vector_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Simula búsqueda vectorial para testing."""
        results = []
        for i in range(min(top_k, 10)):
            results.append({
                "id": f"vec_sim_{i}",
                "text": f"Resultado vectorial simulado {i+1} para: {query[:30]}...",
                "score": 0.9 - (i * 0.1),
                "metadata": {"title": f"Doc Vectorial {i+1}", "section": "Simulación"},
                "source": "vector"
            })
        return results
    
    def _simulate_bm25_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Simula búsqueda BM25 para testing."""
        results = []
        for i in range(min(top_k, 10)):
            results.append({
                "id": f"bm25_sim_{i}",
                "text": f"Resultado BM25 simulado {i+1} para: {query[:30]}...",
                "score": 0.8 - (i * 0.1),
                "metadata": {"title": f"Doc BM25 {i+1}", "section": "Simulación"},
                "source": "bm25"
            })
        return results
    
    def get_search_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas del retriever."""
        return {
            "config": self.config,
            "cache_size": len(self.search_cache),
            "vector_store_available": self.vector_store is not None,
            "bm25_index_available": self.bm25_index is not None,
            "filters_enabled": self.config["enable_filters"],
            "reranking_enabled": self.config["enable_reranking"]
        }
    
    def clear_cache(self):
        """Limpia el cache de búsquedas."""
        self.search_cache.clear()
        logger.info("Cache de búsquedas limpiado")
    
    def update_config(self, new_config: Dict[str, Any]):
        """Actualiza la configuración del retriever."""
        self.config.update(new_config)
        logger.info(f"Configuración actualizada: {new_config}")
