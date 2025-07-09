import asyncio
import os
import logging
from pathlib import Path
from typing import List, Dict, Any
from pymilvus import MilvusClient
from sentence_transformers import SentenceTransformer
from openai import OpenAI
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = "./milvus_knowledge.db"
COLLECTION = "system_knowledge"
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'

embedding_model = SentenceTransformer(EMBEDDING_MODEL)
openai_api_key = os.getenv('OPENAI_API_KEY')
openai_client = OpenAI(api_key=openai_api_key) if openai_api_key else None

# Fragmentar y cargar documentos
def preprocess_md_files(directory: str) -> tuple[List[str], List[Dict]]:
    fragments = []
    metadata = []
    knowledge_dir = Path(directory)
    for file_path in knowledge_dir.glob("*.md"):
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        sections = content.split('\n## ')
        for i, section in enumerate(sections):
            section = section.strip()
            if section and len(section) > 50:
                fragments.append(section)
                metadata.append({
                    "filename": file_path.name,
                    "section": i,
                    "tags": ["system", file_path.stem],
                    "content_length": len(section)
                })
    return fragments, metadata

def load_to_milvus(fragments: List[str], metadata: List[Dict]):
    client = MilvusClient(DB_PATH)
    if client.has_collection(COLLECTION):
        client.drop_collection(COLLECTION)
    client.create_collection(collection_name=COLLECTION, dimension=384)
    embeddings = embedding_model.encode(fragments)
    data = [
        {"id": i, "vector": embeddings[i].tolist(), "text": fragments[i], "metadata": json.dumps(metadata[i])}
        for i in range(len(fragments))
    ]
    client.insert(collection_name=COLLECTION, data=data)
    logger.info(f"Insertados {len(data)} fragmentos en Milvus")

def search_similar(query: str, limit: int = 5, threshold: float = 0.3) -> List[Dict]:
    client = MilvusClient(DB_PATH)
    query_embedding = embedding_model.encode([query])
    results = client.search(
        collection_name=COLLECTION,
        data=query_embedding.tolist(),
        limit=limit,
        output_fields=["text", "metadata"]
    )
    similar_fragments = []
    if results and len(results) > 0:
        for result in results[0]:
            score = getattr(result, 'score', 0.0)
            if score >= threshold:
                meta = json.loads(result.get('metadata', '{}'))
                similar_fragments.append({
                    'text': result.get('text', ''),
                    'score': score,
                    'metadata': meta
                })
    logger.info(f"Encontrados {len(similar_fragments)} fragmentos similares (threshold: {threshold})")
    return similar_fragments

def generate_response(query: str, context_fragments: List[Dict]) -> str:
    if not openai_client:
        return "Error: OPENAI_API_KEY no configurada. Para usar esta función, configura tu API key en el entorno."
    context_text = "\n\n".join([f"Fragmento {i+1}:\n{frag['text']}" for i, frag in enumerate(context_fragments)])
    prompt = f"""Basándote en la siguiente información técnica, responde a la consulta de manera clara y precisa.\n\nINFORMACIÓN TÉCNICA:\n{context_text}\n\nCONSULTA: {query}\n\nRESPUESTA:"""
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Eres un asistente técnico experto que responde consultas basándose en documentación técnica."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
        temperature=0.3
    )
    return response.choices[0].message.content or "No se pudo generar una respuesta."

async def setup_knowledge_base():
    fragments, metadata = preprocess_md_files("./knowledge_base")
    load_to_milvus(fragments, metadata)
    logger.info("Base de conocimiento cargada en Milvus.")

async def main():
    await setup_knowledge_base()
    query = "¿Cómo funciona el sistema de pagos?"
    similar = search_similar(query, limit=3)
    print(f"\nConsulta: {query}\n")
    if not similar:
        print("No se encontró información relevante para tu consulta.")
        return
    print("Fragmentos relevantes:")
    for i, frag in enumerate(similar, 1):
        print(f"\nFragmento {i} (Score: {frag['score']:.3f}):\n{frag['text'][:200]}...")
    print("\nRespuesta generada:")
    print(generate_response(query, similar))

if __name__ == "__main__":
    asyncio.run(main())