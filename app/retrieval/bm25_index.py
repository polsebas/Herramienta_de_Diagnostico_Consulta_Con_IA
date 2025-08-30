"""
Índice BM25 para Búsqueda por Palabras Clave

Este módulo implementa un índice BM25 para búsqueda eficiente por palabras clave:
- Indexación de documentos con metadatos
- Búsqueda BM25 con scoring
- Filtros por campos específicos
- Operaciones de actualización y eliminación
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import json
from datetime import datetime
import re
import hashlib
from collections import defaultdict, Counter

try:
    from rank_bm25 import BM25Okapi
    BM25_AVAILABLE = True
except ImportError:
    BM25_AVAILABLE = False
    logging.warning("rank_bm25 no disponible, usando implementación básica")

logger = logging.getLogger(__name__)

@dataclass
class BM25Document:
    """Documento para indexación BM25."""
    id: str
    text: str
    title: str
    section: str
    path: str
    line_start: int
    line_end: int
    doc_type: str = "document"
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class BM25SearchResult:
    """Resultado de búsqueda BM25."""
    id: str
    text: str
    score: float
    metadata: Dict[str, Any]
    rank: int

class BM25Index:
    """
    Índice BM25 para búsqueda eficiente por palabras clave.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializa el índice BM25.
        
        Args:
            config: Configuración del índice
        """
        self.config = config or {
            "k1": 1.5,           # Parámetro k1 de BM25
            "b": 0.75,           # Parámetro b de BM25
            "min_score": 0.1,    # Score mínimo para resultados
            "max_results": 100,  # Máximo de resultados por búsqueda
            "enable_stemming": True,
            "enable_stopwords": True,
            "language": "spanish"
        }
        
        # Datos del índice
        self.documents = {}  # id -> BM25Document
        self.doc_ids = []    # Lista ordenada de IDs
        self.corpus = []     # Lista de textos tokenizados
        self.bm25_model = None
        
        # Metadatos para filtrado
        self.metadata_index = {
            "doc_type": defaultdict(set),
            "section": defaultdict(set),
            "path": defaultdict(set),
            "tags": defaultdict(set)
        }
        
        # Estadísticas del índice
        self.stats = {
            "total_documents": 0,
            "total_tokens": 0,
            "avg_document_length": 0.0,
            "last_updated": None
        }
        
        # Cache de búsquedas
        self.search_cache = {}
        self.cache_ttl = 300  # 5 minutos
        
        logger.info("BM25Index inicializado")
    
    def add_document(self, document: BM25Document) -> bool:
        """
        Agrega un documento al índice.
        
        Args:
            document: Documento a agregar
        
        Returns:
            True si se agregó exitosamente
        """
        try:
            # Generar ID único si no se proporciona
            if not document.id:
                document.id = self._generate_document_id(document)
            
            # Verificar si el documento ya existe
            if document.id in self.documents:
                logger.warning(f"Documento {document.id} ya existe, actualizando")
                return self.update_document(document.id, document)
            
            # Agregar documento
            self.documents[document.id] = document
            self.doc_ids.append(document.id)
            
            # Tokenizar texto
            tokens = self._tokenize_text(document.text)
            self.corpus.append(tokens)
            
            # Actualizar índices de metadatos
            self._update_metadata_index(document)
            
            # Actualizar estadísticas
            self._update_stats()
            
            # Marcar índice como desactualizado
            self.bm25_model = None
            
            logger.info(f"Documento {document.id} agregado al índice")
            return True
            
        except Exception as e:
            logger.error(f"Error agregando documento {document.id}: {e}")
            return False
    
    def add_documents(self, documents: List[BM25Document]) -> bool:
        """
        Agrega múltiples documentos al índice.
        
        Args:
            documents: Lista de documentos a agregar
        
        Returns:
            True si se agregaron exitosamente
        """
        success_count = 0
        
        for document in documents:
            if self.add_document(document):
                success_count += 1
        
        logger.info(f"Agregados {success_count}/{len(documents)} documentos al índice")
        
        # Reconstruir modelo BM25
        if success_count > 0:
            self._build_bm25_model()
        
        return success_count == len(documents)
    
    def update_document(self, doc_id: str, new_document: BM25Document) -> bool:
        """
        Actualiza un documento existente en el índice.
        
        Args:
            doc_id: ID del documento a actualizar
            new_document: Nuevo documento
        
        Returns:
            True si se actualizó exitosamente
        """
        try:
            if doc_id not in self.documents:
                logger.error(f"Documento {doc_id} no encontrado para actualizar")
                return False
            
            # Obtener documento anterior
            old_document = self.documents[doc_id]
            
            # Actualizar documento
            self.documents[doc_id] = new_document
            
            # Actualizar corpus
            doc_index = self.doc_ids.index(doc_id)
            new_tokens = self._tokenize_text(new_document.text)
            self.corpus[doc_index] = new_tokens
            
            # Actualizar índices de metadatos
            self._remove_from_metadata_index(old_document)
            self._update_metadata_index(new_document)
            
            # Marcar índice como desactualizado
            self.bm25_model = None
            
            # Actualizar estadísticas
            self._update_stats()
            
            logger.info(f"Documento {doc_id} actualizado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error actualizando documento {doc_id}: {e}")
            return False
    
    def delete_document(self, doc_id: str) -> bool:
        """
        Elimina un documento del índice.
        
        Args:
            doc_id: ID del documento a eliminar
        
        Returns:
            True si se eliminó exitosamente
        """
        try:
            if doc_id not in self.documents:
                logger.warning(f"Documento {doc_id} no encontrado para eliminar")
                return False
            
            # Obtener documento
            document = self.documents[doc_id]
            
            # Eliminar del corpus
            doc_index = self.doc_ids.index(doc_id)
            del self.corpus[doc_index]
            del self.doc_ids[doc_index]
            
            # Eliminar documento
            del self.documents[doc_id]
            
            # Actualizar índices de metadatos
            self._remove_from_metadata_index(document)
            
            # Marcar índice como desactualizado
            self.bm25_model = None
            
            # Actualizar estadísticas
            self._update_stats()
            
            logger.info(f"Documento {doc_id} eliminado del índice")
            return True
            
        except Exception as e:
            logger.error(f"Error eliminando documento {doc_id}: {e}")
            return False
    
    def search(self, query: str, top_k: int = 20, 
               filters: Optional[Dict[str, Any]] = None) -> List[BM25SearchResult]:
        """
        Realiza búsqueda BM25 en el índice.
        
        Args:
            query: Consulta de búsqueda
            top_k: Número máximo de resultados
            filters: Filtros de búsqueda
        
        Returns:
            Lista de resultados ordenados por score
        """
        try:
            # Verificar si hay documentos
            if not self.documents:
                logger.warning("Índice vacío, no hay documentos para buscar")
                return []
            
            # Construir modelo BM25 si es necesario
            if self.bm25_model is None:
                self._build_bm25_model()
            
            # Tokenizar consulta
            query_tokens = self._tokenize_text(query)
            
            if not query_tokens:
                logger.warning("Consulta vacía después de tokenización")
                return []
            
            # Realizar búsqueda BM25
            if BM25_AVAILABLE and self.bm25_model:
                # Usar rank_bm25
                scores = self.bm25_model.get_scores(query_tokens)
                doc_scores = list(enumerate(scores))
            else:
                # Implementación básica
                doc_scores = self._basic_bm25_search(query_tokens)
            
            # Aplicar filtros si se especifican
            if filters:
                doc_scores = self._apply_filters(doc_scores, filters)
            
            # Ordenar por score y limitar resultados
            doc_scores.sort(key=lambda x: x[1], reverse=True)
            doc_scores = doc_scores[:top_k]
            
            # Construir resultados
            results = []
            for rank, (doc_index, score) in enumerate(doc_scores):
                if score < self.config["min_score"]:
                    continue
                
                doc_id = self.doc_ids[doc_index]
                document = self.documents[doc_id]
                
                result = BM25SearchResult(
                    id=doc_id,
                    text=document.text,
                    score=score,
                    metadata=asdict(document),
                    rank=rank + 1
                )
                
                results.append(result)
            
            logger.info(f"Búsqueda BM25 completada: {len(results)} resultados")
            return results
            
        except Exception as e:
            logger.error(f"Error en búsqueda BM25: {e}")
            return []
    
    def _build_bm25_model(self):
        """Construye el modelo BM25."""
        try:
            if not self.corpus:
                logger.warning("No hay documentos para construir modelo BM25")
                return
            
            if BM25_AVAILABLE:
                # Usar rank_bm25
                self.bm25_model = BM25Okapi(
                    self.corpus,
                    k1=self.config["k1"],
                    b=self.config["b"]
                )
                logger.info("Modelo BM25 construido con rank_bm25")
            else:
                # Modelo simulado
                self.bm25_model = "simulated"
                logger.info("Modelo BM25 simulado")
                
        except Exception as e:
            logger.error(f"Error construyendo modelo BM25: {e}")
            self.bm25_model = None
    
    def _basic_bm25_search(self, query_tokens: List[str]) -> List[Tuple[int, float]]:
        """Implementación básica de BM25 para cuando rank_bm25 no está disponible."""
        doc_scores = []
        
        # Parámetros BM25
        k1 = self.config["k1"]
        b = self.config["b"]
        
        # Calcular estadísticas del corpus
        avg_doc_length = self.stats["avg_document_length"]
        total_docs = len(self.documents)
        
        for doc_index, doc_tokens in enumerate(self.corpus):
            doc_length = len(doc_tokens)
            
            # Calcular score BM25
            score = 0.0
            
            for term in query_tokens:
                # Frecuencia del término en el documento
                tf = doc_tokens.count(term)
                
                # Frecuencia del término en el corpus
                df = sum(1 for tokens in self.corpus if term in tokens)
                
                if df == 0:
                    continue
                
                # IDF (Inverse Document Frequency)
                idf = np.log((total_docs - df + 0.5) / (df + 0.5))
                
                # TF normalizado
                tf_norm = (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * (doc_length / avg_doc_length)))
                
                # Score del término
                term_score = idf * tf_norm
                score += term_score
            
            doc_scores.append((doc_index, score))
        
        return doc_scores
    
    def _tokenize_text(self, text: str) -> List[str]:
        """Tokeniza el texto para indexación."""
        try:
            # Convertir a minúsculas
            text = text.lower()
            
            # Eliminar caracteres especiales
            text = re.sub(r'[^\w\s]', ' ', text)
            
            # Dividir en tokens
            tokens = text.split()
            
            # Aplicar stemming si está habilitado
            if self.config["enable_stemming"]:
                tokens = self._apply_stemming(tokens)
            
            # Eliminar stopwords si está habilitado
            if self.config["enable_stopwords"]:
                tokens = self._remove_stopwords(tokens)
            
            # Filtrar tokens muy cortos
            tokens = [token for token in tokens if len(token) > 2]
            
            return tokens
            
        except Exception as e:
            logger.error(f"Error tokenizando texto: {e}")
            return []
    
    def _apply_stemming(self, tokens: List[str]) -> List[str]:
        """Aplica stemming a los tokens."""
        try:
            # Implementación básica de stemming para español
            stemmed_tokens = []
            
            for token in tokens:
                # Reglas básicas de stemming
                if token.endswith('s'):
                    stemmed = token[:-1]
                elif token.endswith('es'):
                    stemmed = token[:-2]
                elif token.endswith('ar') or token.endswith('er') or token.endswith('ir'):
                    stemmed = token[:-2]
                else:
                    stemmed = token
                
                stemmed_tokens.append(stemmed)
            
            return stemmed_tokens
            
        except Exception as e:
            logger.error(f"Error aplicando stemming: {e}")
            return tokens
    
    def _remove_stopwords(self, tokens: List[str]) -> List[str]:
        """Elimina stopwords de los tokens."""
        try:
            # Lista básica de stopwords en español
            spanish_stopwords = {
                'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se',
                'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con',
                'para', 'al', 'del', 'como', 'pero', 'sus', 'me', 'hasta',
                'hay', 'donde', 'han', 'quien', 'están', 'estado', 'desde',
                'todo', 'nos', 'durante', 'todos', 'uno', 'les', 'ni',
                'contra', 'otros', 'ese', 'eso', 'ante', 'ellos', 'e',
                'esto', 'mí', 'antes', 'algunos', 'qué', 'unos', 'yo',
                'otro', 'otras', 'otra', 'él', 'tanto', 'esa', 'estos',
                'mucho', 'quienes', 'nada', 'muchos', 'cual', 'poco',
                'ella', 'estar', 'estas', 'algunas', 'algo', 'nosotros'
            }
            
            return [token for token in tokens if token not in spanish_stopwords]
            
        except Exception as e:
            logger.error(f"Error eliminando stopwords: {e}")
            return tokens
    
    def _update_metadata_index(self, document: BM25Document):
        """Actualiza los índices de metadatos."""
        try:
            # Índice por tipo de documento
            self.metadata_index["doc_type"][document.doc_type].add(document.id)
            
            # Índice por sección
            self.metadata_index["section"][document.section].add(document.id)
            
            # Índice por ruta
            self.metadata_index["path"][document.path].add(document.id)
            
            # Índice por tags
            if document.tags:
                for tag in document.tags:
                    self.metadata_index["tags"][tag].add(document.id)
                    
        except Exception as e:
            logger.error(f"Error actualizando índices de metadatos: {e}")
    
    def _remove_from_metadata_index(self, document: BM25Document):
        """Elimina un documento de los índices de metadatos."""
        try:
            # Remover de todos los índices
            for field_name in self.metadata_index:
                for value, doc_ids in self.metadata_index[field_name].items():
                    if document.id in doc_ids:
                        doc_ids.remove(document.id)
                        
                        # Eliminar valor si no hay más documentos
                        if not doc_ids:
                            del self.metadata_index[field_name][value]
                            
        except Exception as e:
            logger.error(f"Error removiendo de índices de metadatos: {e}")
    
    def _apply_filters(self, doc_scores: List[Tuple[int, float]], 
                       filters: Dict[str, Any]) -> List[Tuple[int, float]]:
        """Aplica filtros a los resultados de búsqueda."""
        try:
            filtered_scores = []
            
            for doc_index, score in doc_scores:
                doc_id = self.doc_ids[doc_index]
                document = self.documents[doc_id]
                
                # Verificar filtros
                include_doc = True
                
                for filter_field, filter_value in filters.items():
                    if filter_field == "doc_type" and document.doc_type != filter_value:
                        include_doc = False
                        break
                    elif filter_field == "section" and document.section != filter_value:
                        include_doc = False
                        break
                    elif filter_field == "path" and filter_value not in document.path:
                        include_doc = False
                        break
                    elif filter_field == "tags" and filter_value not in (document.tags or []):
                        include_doc = False
                        break
                    elif filter_field == "min_score" and score < filter_value:
                        include_doc = False
                        break
                
                if include_doc:
                    filtered_scores.append((doc_index, score))
            
            return filtered_scores
            
        except Exception as e:
            logger.error(f"Error aplicando filtros: {e}")
            return doc_scores
    
    def _update_stats(self):
        """Actualiza las estadísticas del índice."""
        try:
            self.stats["total_documents"] = len(self.documents)
            self.stats["total_tokens"] = sum(len(tokens) for tokens in self.corpus)
            self.stats["avg_document_length"] = (
                self.stats["total_tokens"] / self.stats["total_documents"]
                if self.stats["total_documents"] > 0 else 0.0
            )
            self.stats["last_updated"] = datetime.now().isoformat()
            
        except Exception as e:
            logger.error(f"Error actualizando estadísticas: {e}")
    
    def _generate_document_id(self, document: BM25Document) -> str:
        """Genera un ID único para el documento."""
        try:
            # Usar contenido del documento para generar ID
            content_hash = hashlib.md5(
                f"{document.path}:{document.line_start}:{document.line_end}:{document.text[:100]}".encode()
            ).hexdigest()
            
            return f"doc_{content_hash[:8]}"
            
        except Exception as e:
            logger.error(f"Error generando ID de documento: {e}")
            return f"doc_{datetime.now().timestamp()}"
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas del índice."""
        return self.stats.copy()
    
    def get_metadata_index(self) -> Dict[str, Any]:
        """Retorna el índice de metadatos."""
        return {
            field: dict(values) for field, values in self.metadata_index.items()
        }
    
    def clear_cache(self):
        """Limpia el cache de búsquedas."""
        self.search_cache.clear()
        logger.info("Cache de búsquedas limpiado")
    
    def export_index(self, file_path: str) -> bool:
        """
        Exporta el índice a un archivo JSON.
        
        Args:
            file_path: Ruta del archivo de exportación
        
        Returns:
            True si se exportó exitosamente
        """
        try:
            export_data = {
                "config": self.config,
                "stats": self.stats,
                "documents": {
                    doc_id: asdict(doc) for doc_id, doc in self.documents.items()
                },
                "metadata_index": self.get_metadata_index(),
                "exported_at": datetime.now().isoformat()
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Índice exportado a: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exportando índice: {e}")
            return False
    
    def import_index(self, file_path: str) -> bool:
        """
        Importa un índice desde un archivo JSON.
        
        Args:
            file_path: Ruta del archivo de importación
        
        Returns:
            True si se importó exitosamente
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # Limpiar índice actual
            self.documents.clear()
            self.doc_ids.clear()
            self.corpus.clear()
            self.metadata_index.clear()
            
            # Restaurar configuración
            self.config.update(import_data.get("config", {}))
            
            # Restaurar documentos
            for doc_id, doc_data in import_data.get("documents", {}).items():
                # Convertir timestamps de vuelta a datetime
                if "created_at" in doc_data and doc_data["created_at"]:
                    doc_data["created_at"] = datetime.fromisoformat(doc_data["created_at"])
                if "updated_at" in doc_data and doc_data["updated_at"]:
                    doc_data["updated_at"] = datetime.fromisoformat(doc_data["updated_at"])
                
                document = BM25Document(**doc_data)
                self.documents[doc_id] = document
                self.doc_ids.append(doc_id)
                
                # Tokenizar texto
                tokens = self._tokenize_text(document.text)
                self.corpus.append(tokens)
                
                # Actualizar índices de metadatos
                self._update_metadata_index(document)
            
            # Restaurar estadísticas
            self.stats.update(import_data.get("stats", {}))
            
            # Marcar índice como desactualizado
            self.bm25_model = None
            
            logger.info(f"Índice importado desde: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error importando índice: {e}")
            return False
    
    def clear_index(self):
        """Limpia completamente el índice."""
        try:
            self.documents.clear()
            self.doc_ids.clear()
            self.corpus.clear()
            self.metadata_index.clear()
            self.bm25_model = None
            
            # Resetear estadísticas
            self.stats = {
                "total_documents": 0,
                "total_tokens": 0,
                "avg_document_length": 0.0,
                "last_updated": None
            }
            
            logger.info("Índice limpiado completamente")
            
        except Exception as e:
            logger.error(f"Error limpiando índice: {e}")
    
    def is_empty(self) -> bool:
        """Verifica si el índice está vacío."""
        return len(self.documents) == 0
    
    def get_document_count(self) -> int:
        """Retorna el número de documentos en el índice."""
        return len(self.documents)
