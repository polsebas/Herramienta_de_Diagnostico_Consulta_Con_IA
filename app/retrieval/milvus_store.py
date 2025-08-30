"""
Almacén Vectorial Milvus

Este módulo implementa la integración con Milvus para almacenamiento y búsqueda vectorial:
- Esquema optimizado para chunks de conocimiento
- Índices HNSW/IVF_FLAT según el tamaño
- Metadatos enriquecidos
- Operaciones asíncronas
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import json
from datetime import datetime
import numpy as np
import asyncio
from concurrent.futures import ThreadPoolExecutor

try:
    from pymilvus import (
        MilvusClient, DataType, FieldSchema, CollectionSchema, 
        Collection, connections, utility, exceptions
    )
    MILVUS_AVAILABLE = True
except ImportError:
    MILVUS_AVAILABLE = False
    logging.warning("pymilvus no disponible, usando modo simulado")

logger = logging.getLogger(__name__)

@dataclass
class MilvusConfig:
    """Configuración para la conexión a Milvus."""
    uri: str = "localhost:19530"
    collection_name: str = "system_knowledge"
    embedding_dim: int = 384
    index_type: str = "HNSW"  # HNSW o IVF_FLAT
    metric_type: str = "IP"   # IP (Inner Product) o L2
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    batch_size: int = 1000
    enable_async: bool = True

@dataclass
class ChunkData:
    """Datos de un chunk para almacenar en Milvus."""
    id: str
    doc_id: str
    title: str
    section: str
    path: str
    line_start: int
    line_end: int
    text: str
    embedding: List[float]
    doc_type: str = "document"
    version: str = "1.0"
    created_at: Optional[int] = None
    updated_at: Optional[int] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class MilvusVectorStore:
    """
    Almacén vectorial basado en Milvus para chunks de conocimiento.
    """
    
    def __init__(self, config: Optional[MilvusConfig] = None):
        """
        Inicializa el almacén vectorial Milvus.
        
        Args:
            config: Configuración de Milvus
        """
        self.config = config or MilvusConfig()
        
        if not MILVUS_AVAILABLE:
            logger.warning("Milvus no disponible, usando modo simulado")
            self.client = None
            self.collection = None
            self.simulated_data = {}
            return
        
        # Conectar a Milvus
        try:
            connections.connect("default", uri=self.config.uri)
            self.client = MilvusClient(uri=self.config.uri)
            logger.info(f"Conectado a Milvus: {self.config.uri}")
            
            # Inicializar colección
            self._initialize_collection()
            
        except Exception as e:
            logger.error(f"Error conectando a Milvus: {e}")
            self.client = None
            self.collection = None
    
    def _initialize_collection(self):
        """Inicializa la colección de Milvus."""
        try:
            # Verificar si la colección existe
            if utility.has_collection(self.config.collection_name):
                logger.info(f"Colección existente: {self.config.collection_name}")
                self.collection = Collection(self.config.collection_name)
                return
            
            # Crear nueva colección
            logger.info(f"Creando nueva colección: {self.config.collection_name}")
            
            # Definir esquema
            fields = [
                FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=64),
                FieldSchema(name="doc_id", dtype=DataType.VARCHAR, max_length=128),
                FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=256),
                FieldSchema(name="section", dtype=DataType.VARCHAR, max_length=128),
                FieldSchema(name="path", dtype=DataType.VARCHAR, max_length=512),
                FieldSchema(name="line_start", dtype=DataType.INT64),
                FieldSchema(name="line_end", dtype=DataType.INT64),
                FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=16384),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.config.embedding_dim),
                FieldSchema(name="doc_type", dtype=DataType.VARCHAR, max_length=64),
                FieldSchema(name="version", dtype=DataType.VARCHAR, max_length=32),
                FieldSchema(name="created_at", dtype=DataType.INT64),
                FieldSchema(name="updated_at", dtype=DataType.INT64),
                FieldSchema(name="tags", dtype=DataType.VARCHAR, max_length=1024),
                FieldSchema(name="metadata_json", dtype=DataType.VARCHAR, max_length=8192)
            ]
            
            schema = CollectionSchema(fields, description="Knowledge Base Chunks")
            
            # Crear colección
            self.collection = Collection(self.config.collection_name, schema)
            
            # Crear índice
            self._create_index()
            
            logger.info(f"Colección {self.config.collection_name} creada exitosamente")
            
        except Exception as e:
            logger.error(f"Error inicializando colección: {e}")
            self.collection = None
    
    def _create_index(self):
        """Crea el índice vectorial en la colección."""
        try:
            # Parámetros del índice según el tipo
            if self.config.index_type == "HNSW":
                index_params = {
                    "index_type": "HNSW",
                    "metric_type": self.config.metric_type,
                    "params": {
                        "M": 32,           # Número de conexiones por nodo
                        "efConstruction": 200  # Precisión durante construcción
                    }
                }
            else:  # IVF_FLAT
                index_params = {
                    "index_type": "IVF_FLAT",
                    "metric_type": self.config.metric_type,
                    "params": {
                        "nlist": 1024  # Número de clusters
                    }
                }
            
            # Crear índice
            self.collection.create_index("embedding", index_params)
            logger.info(f"Índice {self.config.index_type} creado")
            
        except Exception as e:
            logger.error(f"Error creando índice: {e}")
    
    async def add_chunks(self, chunks: List[ChunkData]) -> bool:
        """
        Agrega chunks a la base de datos vectorial.
        
        Args:
            chunks: Lista de chunks a agregar
        
        Returns:
            True si se agregaron exitosamente
        """
        if not self.collection:
            logger.warning("Colección no disponible, usando modo simulado")
            return self._simulate_add_chunks(chunks)
        
        try:
            # Preparar datos para inserción
            data = []
            for chunk in chunks:
                # Convertir chunk a formato de Milvus
                chunk_dict = asdict(chunk)
                
                # Convertir tags a string
                if chunk.tags:
                    chunk_dict["tags"] = ",".join(chunk.tags)
                
                # Convertir metadata a JSON string
                if chunk.metadata:
                    chunk_dict["metadata_json"] = json.dumps(chunk.metadata, ensure_ascii=False)
                
                # Asegurar timestamps
                if not chunk_dict["created_at"]:
                    chunk_dict["created_at"] = int(datetime.now().timestamp())
                if not chunk_dict["updated_at"]:
                    chunk_dict["updated_at"] = int(datetime.now().timestamp())
                
                data.append(chunk_dict)
            
            # Insertar en lotes
            success = True
            for i in range(0, len(data), self.config.batch_size):
                batch = data[i:i + self.config.batch_size]
                
                try:
                    # Insertar lote
                    insert_result = self.collection.insert(batch)
                    
                    if insert_result.insert_count != len(batch):
                        logger.warning(f"Lote {i//self.config.batch_size + 1}: "
                                     f"insertados {insert_result.insert_count}/{len(batch)}")
                        success = False
                    
                except Exception as e:
                    logger.error(f"Error insertando lote {i//self.config.batch_size + 1}: {e}")
                    success = False
            
            if success:
                # Flush para asegurar persistencia
                self.collection.flush()
                logger.info(f"Agregados {len(chunks)} chunks exitosamente")
            
            return success
            
        except Exception as e:
            logger.error(f"Error agregando chunks: {e}")
            return False
    
    async def similarity_search(self, query_embedding: List[float], 
                               top_k: int = 10, 
                               filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Realiza búsqueda por similitud vectorial.
        
        Args:
            query_embedding: Embedding de la consulta
            top_k: Número máximo de resultados
            filters: Filtros de búsqueda
        
        Returns:
            Lista de resultados ordenados por similitud
        """
        if not self.collection:
            logger.warning("Colección no disponible, usando modo simulado")
            return self._simulate_similarity_search(query_embedding, top_k, filters)
        
        try:
            # Preparar filtros de búsqueda
            search_params = self._prepare_search_params(filters)
            
            # Realizar búsqueda
            search_results = self.collection.search(
                data=[query_embedding],
                anns_field="embedding",
                param=search_params,
                limit=top_k,
                output_fields=["id", "doc_id", "title", "section", "path", 
                             "line_start", "line_end", "text", "doc_type", 
                             "version", "created_at", "updated_at", "tags", "metadata_json"]
            )
            
            # Procesar resultados
            results = []
            for hits in search_results:
                for hit in hits:
                    # Convertir hit a diccionario
                    result = {
                        "id": hit.id,
                        "score": hit.score,
                        "metadata": {}
                    }
                    
                    # Extraer campos del hit
                    for field_name in ["doc_id", "title", "section", "path", 
                                     "line_start", "line_end", "text", "doc_type", 
                                     "version", "created_at", "updated_at", "tags"]:
                        if field_name in hit.entity:
                            result["metadata"][field_name] = hit.entity[field_name]
                    
                    # Parsear metadata JSON
                    if "metadata_json" in hit.entity and hit.entity["metadata_json"]:
                        try:
                            result["metadata"]["extra_metadata"] = json.loads(hit.entity["metadata_json"])
                        except json.JSONDecodeError:
                            logger.warning(f"Error parseando metadata JSON para {hit.id}")
                    
                    # Parsear tags
                    if "tags" in result["metadata"] and result["metadata"]["tags"]:
                        result["metadata"]["tags"] = result["metadata"]["tags"].split(",")
                    
                    results.append(result)
            
            logger.info(f"Búsqueda vectorial completada: {len(results)} resultados")
            return results
            
        except Exception as e:
            logger.error(f"Error en búsqueda vectorial: {e}")
            return []
    
    def _prepare_search_params(self, filters: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepara parámetros de búsqueda para Milvus."""
        search_params = {}
        
        if self.config.index_type == "HNSW":
            search_params = {
                "metric_type": self.config.metric_type,
                "params": {"ef": 64}  # Precisión de búsqueda
            }
        else:  # IVF_FLAT
            search_params = {
                "metric_type": self.config.metric_type,
                "params": {"nprobe": 16}  # Número de clusters a buscar
            }
        
        return search_params
    
    async def delete_chunks(self, chunk_ids: List[str]) -> bool:
        """
        Elimina chunks por ID.
        
        Args:
            chunk_ids: Lista de IDs de chunks a eliminar
        
        Returns:
            True si se eliminaron exitosamente
        """
        if not self.collection:
            logger.warning("Colección no disponible, usando modo simulado")
            return self._simulate_delete_chunks(chunk_ids)
        
        try:
            # Eliminar chunks
            delete_expr = f"id in {chunk_ids}"
            self.collection.delete(delete_expr)
            
            # Flush para asegurar persistencia
            self.collection.flush()
            
            logger.info(f"Eliminados {len(chunk_ids)} chunks exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error eliminando chunks: {e}")
            return False
    
    async def update_chunk(self, chunk_id: str, updates: Dict[str, Any]) -> bool:
        """
        Actualiza un chunk existente.
        
        Args:
            chunk_id: ID del chunk a actualizar
            updates: Campos a actualizar
        
        Returns:
            True si se actualizó exitosamente
        """
        if not self.collection:
            logger.warning("Colección no disponible, usando modo simulado")
            return self._simulate_update_chunk(chunk_id, updates)
        
        try:
            # Preparar datos de actualización
            update_data = {}
            
            for field, value in updates.items():
                if field == "metadata" and isinstance(value, dict):
                    # Convertir metadata a JSON string
                    update_data["metadata_json"] = json.dumps(value, ensure_ascii=False)
                elif field == "tags" and isinstance(value, list):
                    # Convertir tags a string
                    update_data["tags"] = ",".join(value)
                elif field in ["created_at", "updated_at"] and isinstance(value, datetime):
                    # Convertir datetime a timestamp
                    update_data[field] = int(value.timestamp())
                else:
                    update_data[field] = value
            
            # Agregar timestamp de actualización
            update_data["updated_at"] = int(datetime.now().timestamp())
            
            # Actualizar chunk
            self.collection.upsert([{"id": chunk_id, **update_data}])
            
            # Flush para asegurar persistencia
            self.collection.flush()
            
            logger.info(f"Chunk {chunk_id} actualizado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error actualizando chunk {chunk_id}: {e}")
            return False
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de la colección."""
        if not self.collection:
            return {"error": "Colección no disponible"}
        
        try:
            stats = {
                "collection_name": self.config.collection_name,
                "total_rows": self.collection.num_entities,
                "index_type": self.config.index_type,
                "embedding_dim": self.config.embedding_dim,
                "metric_type": self.config.metric_type
            }
            
            # Obtener información del índice
            index_info = self.collection.index().params
            stats["index_params"] = index_info
            
            return stats
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {"error": str(e)}
    
    async def create_backup(self, backup_path: str) -> bool:
        """
        Crea un backup de la colección.
        
        Args:
            backup_path: Ruta donde guardar el backup
        
        Returns:
            True si el backup se creó exitosamente
        """
        if not self.collection:
            logger.warning("Colección no disponible, backup no disponible")
            return False
        
        try:
            # Crear directorio de backup
            backup_dir = Path(backup_path)
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Exportar datos
            export_path = str(backup_dir / f"{self.config.collection_name}_backup.json")
            
            # Obtener todos los datos
            results = self.collection.query(
                expr="id != ''",
                output_fields=["id", "doc_id", "title", "section", "path", 
                             "line_start", "line_end", "text", "doc_type", 
                             "version", "created_at", "updated_at", "tags", "metadata_json"]
            )
            
            # Guardar backup
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Backup creado en: {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creando backup: {e}")
            return False
    
    # Métodos de simulación para cuando Milvus no está disponible
    
    def _simulate_add_chunks(self, chunks: List[ChunkData]) -> bool:
        """Simula agregar chunks en modo simulado."""
        for chunk in chunks:
            self.simulated_data[chunk.id] = asdict(chunk)
        logger.info(f"Simulación: {len(chunks)} chunks agregados")
        return True
    
    def _simulate_similarity_search(self, query_embedding: List[float], 
                                   top_k: int, filters: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Simula búsqueda por similitud en modo simulado."""
        results = []
        
        # Simular búsqueda por similitud
        for i, (chunk_id, chunk_data) in enumerate(self.simulated_data.items()):
            if i >= top_k:
                break
            
            # Simular score de similitud
            score = 0.9 - (i * 0.1)
            
            result = {
                "id": chunk_id,
                "score": score,
                "metadata": {
                    "doc_id": chunk_data.get("doc_id", ""),
                    "title": chunk_data.get("title", ""),
                    "section": chunk_data.get("section", ""),
                    "path": chunk_data.get("path", ""),
                    "line_start": chunk_data.get("line_start", 0),
                    "line_end": chunk_data.get("line_end", 0),
                    "text": chunk_data.get("text", ""),
                    "doc_type": chunk_data.get("doc_type", ""),
                    "version": chunk_data.get("version", ""),
                    "created_at": chunk_data.get("created_at", 0),
                    "updated_at": chunk_data.get("updated_at", 0),
                    "tags": chunk_data.get("tags", [])
                }
            }
            
            results.append(result)
        
        logger.info(f"Simulación: búsqueda vectorial con {len(results)} resultados")
        return results
    
    def _simulate_delete_chunks(self, chunk_ids: List[str]) -> bool:
        """Simula eliminar chunks en modo simulado."""
        for chunk_id in chunk_ids:
            if chunk_id in self.simulated_data:
                del self.simulated_data[chunk_id]
        logger.info(f"Simulación: {len(chunk_ids)} chunks eliminados")
        return True
    
    def _simulate_update_chunk(self, chunk_id: str, updates: Dict[str, Any]) -> bool:
        """Simula actualizar un chunk en modo simulado."""
        if chunk_id in self.simulated_data:
            self.simulated_data[chunk_id].update(updates)
            logger.info(f"Simulación: chunk {chunk_id} actualizado")
            return True
        return False
    
    def is_available(self) -> bool:
        """Verifica si Milvus está disponible."""
        return self.collection is not None
    
    def close(self):
        """Cierra la conexión a Milvus."""
        if self.collection:
            try:
                connections.disconnect("default")
                logger.info("Conexión a Milvus cerrada")
            except Exception as e:
                logger.error(f"Error cerrando conexión a Milvus: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
