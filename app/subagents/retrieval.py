"""
Subagente de Recuperación - Búsqueda Híbrida BM25 + Vectorial
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class RetrievalSubAgent:
    """
    Subagente especializado en recuperación de información usando búsqueda híbrida.
    Combina búsqueda vectorial (embeddings) con búsqueda léxica (BM25).
    """
    
    def __init__(self, vector_store=None, bm25_index=None):
        """
        Inicializa el subagente de recuperación.
        
        Args:
            vector_store: Store vectorial (Milvus, Chroma, etc.)
            bm25_index: Índice BM25 (Whoosh, Elasticsearch, etc.)
        """
        self.vector_store = vector_store
        self.bm25_index = bm25_index
        self.hybrid_weights = {"vector": 0.7, "bm25": 0.3}
        
        logger.info("RetrievalSubAgent inicializado")
    
    def retrieve(self, query: str, top_k: int = 8, filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Recupera información usando búsqueda híbrida.
        
        Args:
            query: Consulta del usuario
            top_k: Número máximo de resultados
            filters: Filtros adicionales (tipo_doc, sección, etc.)
        
        Returns:
            Lista de chunks relevantes con metadatos
        """
        logger.info(f"Recuperando información para: {query[:50]}...")
        
        # Búsqueda vectorial
        vector_results = self._vector_search(query, top_k, filters)
        
        # Búsqueda BM25
        bm25_results = self._bm25_search(query, top_k, filters)
        
        # Fusión híbrida
        hybrid_results = self._hybrid_merge(vector_results, bm25_results, top_k)
        
        # Aplicar filtros adicionales
        if filters:
            hybrid_results = self._apply_filters(hybrid_results, filters)
        
        # Reranking final
        final_results = self._rerank_results(hybrid_results, query)
        
        logger.info(f"Recuperados {len(final_results)} chunks relevantes")
        return final_results
    
    def _vector_search(self, query: str, top_k: int, filters: Optional[Dict]) -> List[Dict[str, Any]]:
        """Realiza búsqueda vectorial usando embeddings."""
        if not self.vector_store:
            logger.warning("Vector store no disponible, saltando búsqueda vectorial")
            return []
        
        try:
            # Búsqueda por similitud semántica
            results = self.vector_store.similarity_search(
                query, 
                k=top_k,
                filter=filters
            )
            
            # Convertir a formato estándar
            formatted_results = []
            for i, result in enumerate(results):
                formatted_results.append({
                    "id": getattr(result, "id", f"vec_{i}"),
                    "text": getattr(result, "page_content", str(result)),
                    "metadata": getattr(result, "metadata", {}),
                    "score": 1.0 - (i * 0.1),  # Score decreciente
                    "source": "vector"
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error en búsqueda vectorial: {e}")
            return []
    
    def _bm25_search(self, query: str, top_k: int, filters: Optional[Dict]) -> List[Dict[str, Any]]:
        """Realiza búsqueda BM25 usando palabras clave."""
        if not self.bm25_index:
            logger.warning("BM25 index no disponible, saltando búsqueda léxica")
            return []
        
        try:
            # Búsqueda por palabras clave
            results = self.bm25_index.search(query, top_k)
            
            # Convertir a formato estándar
            formatted_results = []
            for i, result in enumerate(results):
                formatted_results.append({
                    "id": getattr(result, "id", f"bm25_{i}"),
                    "text": getattr(result, "text", str(result)),
                    "metadata": getattr(result, "metadata", {}),
                    "score": getattr(result, "score", 1.0 - (i * 0.1)),
                    "source": "bm25"
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error en búsqueda BM25: {e}")
            return []
    
    def _hybrid_merge(self, vector_results: List[Dict], bm25_results: List[Dict], limit: int) -> List[Dict[str, Any]]:
        """
        Fusiona resultados de búsqueda vectorial y BM25.
        
        Args:
            vector_results: Resultados de búsqueda vectorial
            bm25_results: Resultados de búsqueda BM25
            limit: Límite de resultados finales
        
        Returns:
            Lista fusionada y ordenada por relevancia
        """
        # Agrupar por ID para evitar duplicados
        by_id = {}
        
        # Procesar resultados vectoriales
        for rank, result in enumerate(vector_results):
            doc_id = result.get("id", f"vec_{rank}")
            if doc_id not in by_id:
                by_id[doc_id] = {"score": 0, "hit": result}
            
            # Ponderar por fuente y ranking
            vector_score = result.get("score", 0) * self.hybrid_weights["vector"]
            rank_boost = 1.0 / (1 + rank)  # Boost para primeros resultados
            by_id[doc_id]["score"] += vector_score * rank_boost
        
        # Procesar resultados BM25
        for rank, result in enumerate(bm25_results):
            doc_id = result.get("id", f"bm25_{rank}")
            if doc_id not in by_id:
                by_id[doc_id] = {"score": 0, "hit": result}
            
            # Ponderar por fuente y ranking
            bm25_score = result.get("score", 0) * self.hybrid_weights["bm25"]
            rank_boost = 0.7 / (1 + rank)  # Boost menor para BM25
            by_id[doc_id]["score"] += bm25_score * rank_boost
        
        # Ordenar por score combinado
        sorted_results = sorted(by_id.values(), key=lambda x: -x["score"])
        
        # Retornar top-k resultados
        return [v["hit"] for v in sorted_results[:limit]]
    
    def _apply_filters(self, results: List[Dict[str, Any]], filters: Dict) -> List[Dict[str, Any]]:
        """Aplica filtros adicionales a los resultados."""
        filtered_results = []
        
        for result in results:
            metadata = result.get("metadata", {})
            passes_filters = True
            
            for filter_key, filter_value in filters.items():
                if filter_key in metadata:
                    if isinstance(filter_value, str):
                        # Filtro exacto
                        if metadata[filter_key] != filter_value:
                            passes_filters = False
                            break
                    elif isinstance(filter_value, list):
                        # Filtro de lista
                        if metadata[filter_key] not in filter_value:
                            passes_filters = False
                            break
                    elif isinstance(filter_value, dict):
                        # Filtro de rango
                        if "min" in filter_value and metadata[filter_key] < filter_value["min"]:
                            passes_filters = False
                            break
                        if "max" in filter_value and metadata[filter_key] > filter_value["max"]:
                            passes_filters = False
                            break
            
            if passes_filters:
                filtered_results.append(result)
        
        return filtered_results
    
    def _rerank_results(self, results: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """
        Aplica reranking final basado en relevancia y calidad.
        
        Args:
            results: Resultados a rerankear
            query: Consulta original
        
        Returns:
            Resultados rerankeados
        """
        if not results:
            return results
        
        # Calcular scores de calidad
        for result in results:
            quality_score = self._calculate_quality_score(result, query)
            result["quality_score"] = quality_score
        
        # Ordenar por score de calidad
        reranked = sorted(results, key=lambda x: x.get("quality_score", 0), reverse=True)
        
        return reranked
    
    def _calculate_quality_score(self, result: Dict[str, Any], query: str) -> float:
        """
        Calcula un score de calidad para un resultado.
        
        Args:
            result: Resultado a evaluar
            query: Consulta original
        
        Returns:
            Score de calidad (0.0-1.0)
        """
        base_score = result.get("score", 0.5)
        text = result.get("text", "")
        metadata = result.get("metadata", {})
        
        # Bonus por metadatos completos
        metadata_bonus = 0.0
        if metadata.get("title"):
            metadata_bonus += 0.1
        if metadata.get("section"):
            metadata_bonus += 0.1
        if metadata.get("line_start") and metadata.get("line_end"):
            metadata_bonus += 0.1
        
        # Bonus por longitud apropiada
        length_bonus = 0.0
        text_length = len(text)
        if 100 <= text_length <= 1000:  # Longitud ideal
            length_bonus = 0.2
        elif 50 <= text_length <= 2000:  # Longitud aceptable
            length_bonus = 0.1
        
        # Bonus por relevancia de palabras clave
        keyword_bonus = 0.0
        query_words = set(query.lower().split())
        text_words = set(text.lower().split())
        common_words = query_words.intersection(text_words)
        if common_words:
            keyword_bonus = min(0.3, len(common_words) * 0.1)
        
        # Score final
        final_score = min(1.0, base_score + metadata_bonus + length_bonus + keyword_bonus)
        
        return final_score
    
    def update_weights(self, vector_weight: float, bm25_weight: float):
        """
        Actualiza los pesos de la fusión híbrida.
        
        Args:
            vector_weight: Peso para búsqueda vectorial
            bm25_weight: Peso para búsqueda BM25
        """
        total = vector_weight + bm25_weight
        if total > 0:
            self.hybrid_weights = {
                "vector": vector_weight / total,
                "bm25": bm25_weight / total
            }
            logger.info(f"Pesos híbridos actualizados: vector={self.hybrid_weights['vector']:.2f}, "
                       f"bm25={self.hybrid_weights['bm25']:.2f}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas del subagente."""
        return {
            "vector_store_available": self.vector_store is not None,
            "bm25_index_available": self.bm25_index is not None,
            "hybrid_weights": self.hybrid_weights.copy(),
            "agent_type": "RetrievalSubAgent"
        }
