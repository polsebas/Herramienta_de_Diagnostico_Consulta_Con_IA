import asyncio
import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from pymilvus import MilvusClient
from sentence_transformers import SentenceTransformer
from openai import OpenAI
import json

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorKnowledgeBase:
    """Base de conocimiento optimizada para bases de datos vectoriales"""
    
    def __init__(self, db_path: str = "./milvus_knowledge.db", collection_name: str = "system_knowledge"):
        self.db_path = db_path
        self.collection_name = collection_name
        self.client = MilvusClient(db_path)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.openai_client = None
        
        # Configurar OpenAI si hay API key
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            self.openai_client = OpenAI(api_key=api_key)
    
    def preprocess_md_files(self, directory: str) -> tuple[List[str], List[Dict]]:
        """Preprocesar archivos Markdown y dividirlos en fragmentos"""
        fragments = []
        metadata = []
        
        knowledge_dir = Path(directory)
        if not knowledge_dir.exists():
            logger.warning(f"Directorio {directory} no existe")
            return fragments, metadata
        
        for file_path in knowledge_dir.glob("*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    
                # Dividir por secciones (##)
                sections = content.split('\n## ')
                
                for i, section in enumerate(sections):
                    section = section.strip()
                    if section and len(section) > 50:  # Filtrar secciones muy cortas
                        fragments.append(section)
                        metadata.append({
                            "filename": file_path.name,
                            "section": i,
                            "tags": ["system", file_path.stem],
                            "content_length": len(section)
                        })
                        
            except Exception as e:
                logger.error(f"Error procesando {file_path}: {e}")
        
        logger.info(f"Procesados {len(fragments)} fragmentos de {len(set(m['filename'] for m in metadata))} archivos")
        return fragments, metadata
    
    def load_to_vector_db(self, fragments: List[str], metadata: List[Dict]) -> bool:
        """Cargar fragmentos a la base de datos vectorial"""
        try:
            # Eliminar colección existente si existe
            if self.client.has_collection(self.collection_name):
                self.client.drop_collection(self.collection_name)
            
            # Crear nueva colección
            self.client.create_collection(
                collection_name=self.collection_name,
                dimension=384,  # Dimensión del modelo all-MiniLM-L6-v2
            )
            
            # Generar embeddings
            logger.info("Generando embeddings...")
            embeddings = self.embedding_model.encode(fragments)
            
            # Preparar datos para inserción
            data = []
            for i, (fragment, meta) in enumerate(zip(fragments, metadata)):
                data.append({
                    "id": i,
                    "vector": embeddings[i].tolist(),
                    "text": fragment,
                    "metadata": json.dumps(meta)  # Serializar metadata como JSON
                })
            
            # Insertar en Milvus
            self.client.insert(collection_name=self.collection_name, data=data)
            logger.info(f"Insertados {len(data)} fragmentos en la base de datos vectorial")
            return True
            
        except Exception as e:
            logger.error(f"Error cargando a la base de datos: {e}")
            return False
    
    def search_similar(self, query: str, limit: int = 5, threshold: float = 0.3) -> List[Dict]:
        """Buscar fragmentos similares a la consulta"""
        try:
            # Generar embedding de la consulta
            query_embedding = self.embedding_model.encode([query])
            
            # Buscar en la base de datos vectorial
            results = self.client.search(
                collection_name=self.collection_name,
                data=query_embedding.tolist(),
                limit=limit,
                output_fields=["text", "metadata"]
            )
            
            # Procesar resultados
            similar_fragments = []
            if results and len(results) > 0:
                for result in results[0]:  # results[0] porque solo tenemos una consulta
                    score = result.score if hasattr(result, 'score') else 0.0
                    if score >= threshold:
                        metadata = json.loads(result.entity.get('metadata', '{}'))
                        similar_fragments.append({
                            'text': result.entity.get('text', ''),
                            'score': score,
                            'metadata': metadata
                        })
            
            logger.info(f"Encontrados {len(similar_fragments)} fragmentos similares (threshold: {threshold})")
            return similar_fragments
            
        except Exception as e:
            logger.error(f"Error en búsqueda: {e}")
            return []
    
    def generate_response(self, query: str, context_fragments: List[Dict]) -> str:
        """Generar respuesta usando OpenAI con el contexto encontrado"""
        if not self.openai_client:
            return "Error: OpenAI API key no configurada. Para usar esta función, configura OPENAI_API_KEY en tu archivo .env"
        
        try:
            # Preparar contexto
            context_text = "\n\n".join([f"Fragmento {i+1}:\n{frag['text']}" 
                                       for i, frag in enumerate(context_fragments)])
            
            # Crear prompt
            prompt = f"""Basándote en la siguiente información técnica, responde a la consulta de manera clara y precisa.

INFORMACIÓN TÉCNICA:
{context_text}

CONSULTA: {query}

RESPUESTA:"""
            
            # Generar respuesta
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un asistente técnico experto que responde consultas basándose en documentación técnica."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            return response.choices[0].message.content or "No se pudo generar una respuesta."
            
        except Exception as e:
            logger.error(f"Error generando respuesta: {e}")
            return f"Error generando respuesta: {e}"
    
    async def query(self, question: str, limit: int = 5, threshold: float = 0.3) -> Dict[str, Any]:
        """Realizar consulta completa al sistema RAG"""
        logger.info(f"Procesando consulta: {question}")
        
        # Buscar fragmentos similares
        similar_fragments = self.search_similar(question, limit, threshold)
        
        if not similar_fragments:
            return {
                'query': question,
                'response': 'No se encontró información relevante para tu consulta.',
                'fragments': [],
                'scores': [],
                'metadata': []
            }
        
        # Generar respuesta
        response = self.generate_response(question, similar_fragments)
        
        return {
            'query': question,
            'response': response,
            'fragments': [frag['text'] for frag in similar_fragments],
            'scores': [frag['score'] for frag in similar_fragments],
            'metadata': [frag['metadata'] for frag in similar_fragments]
        }
    
    def setup_knowledge_base(self, knowledge_dir: str = "./knowledge_base") -> bool:
        """Configurar la base de conocimiento"""
        logger.info("Configurando base de conocimiento...")
        
        # Procesar archivos
        fragments, metadata = self.preprocess_md_files(knowledge_dir)
        
        if not fragments:
            logger.error("No se encontraron fragmentos para procesar")
            return False
        
        # Cargar a la base de datos vectorial
        return self.load_to_vector_db(fragments, metadata)

class RAGSystem:
    """Sistema RAG mejorado usando base de datos vectorial directamente"""
    
    def __init__(self, db_path: str = "./milvus_knowledge.db"):
        self.knowledge_base = VectorKnowledgeBase(db_path)
    
    async def initialize(self, knowledge_dir: str = "./knowledge_base") -> bool:
        """Inicializar el sistema RAG"""
        return self.knowledge_base.setup_knowledge_base(knowledge_dir)
    
    async def query(self, question: str, limit: int = 5, threshold: float = 0.3) -> Dict[str, Any]:
        """Realizar consulta al sistema"""
        return await self.knowledge_base.query(question, limit, threshold)
    
    def search_only(self, query: str, limit: int = 5, threshold: float = 0.3) -> List[Dict]:
        """Solo buscar fragmentos similares sin generar respuesta"""
        return self.knowledge_base.search_similar(query, limit, threshold)

# Función de conveniencia para uso directo
async def setup_rag_system(db_path: str = "./milvus_knowledge.db") -> RAGSystem:
    """Configurar y retornar un sistema RAG listo para usar"""
    system = RAGSystem(db_path)
    success = await system.initialize()
    if not success:
        raise RuntimeError("Error configurando el sistema RAG")
    return system

# Ejemplo de uso
async def main():
    """Ejemplo de uso del sistema RAG mejorado"""
    try:
        # Configurar sistema
        rag_system = await setup_rag_system()
        
        # Ejemplos de consultas
        queries = [
            "¿Cómo funciona el sistema de pagos?",
            "¿Qué métodos de autenticación están disponibles?",
            "¿Cómo se manejan los errores en las transacciones?",
            "¿Qué medidas de seguridad implementa el sistema?"
        ]
        
        for query in queries:
            print(f"\n{'='*60}")
            print(f"❓ CONSULTA: {query}")
            print(f"{'='*60}")
            
            # Realizar consulta
            result = await rag_system.query(query)
            
            # Mostrar resultados
            print(f"📝 RESPUESTA:")
            print(result['response'])
            
            print(f"\n🔍 FRAGMENTOS ENCONTRADOS ({len(result['fragments'])}):")
            for i, (fragment, score, meta) in enumerate(zip(result['fragments'], result['scores'], result['metadata'])):
                print(f"\n  Fragmento {i+1} (Score: {score:.3f}):")
                print(f"    Archivo: {meta.get('filename', 'N/A')}")
                print(f"    Contenido: {fragment[:200]}...")
            
            print(f"\n" + "="*60)
    
    except Exception as e:
        logger.error(f"Error en el sistema RAG: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 