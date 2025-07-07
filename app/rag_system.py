import asyncio
import os
from agno.agent import Agent
from agno.knowledge.text import TextKnowledgeBase
from agno.vectordb.milvus import Milvus
from pymilvus import MilvusClient
from sentence_transformers import SentenceTransformer

# Configuración de Milvus
vector_db = Milvus(
    collection="system_knowledge",
    uri="./milvus_knowledge.db",  # Usamos Milvus Lite para prototipos
)

# Modelo de embeddings
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Función para preprocesar y fragmentar archivos MD
def preprocess_md_files(directory):
    fragments = []
    metadata = []
    for filename in os.listdir(directory):
        if filename.endswith(".md"):
            with open(os.path.join(directory, filename), 'r', encoding='utf-8') as file:
                content = file.read()
                # Divide por secciones (simplificado, usar lógica más robusta si necesario)
                sections = content.split('\n## ')
                for i, section in enumerate(sections):
                    section = section.strip()
                    if section:
                        fragments.append(section)
                        metadata.append({
                            "filename": filename,
                            "section": i,
                            "tags": ["system", filename.split('.')[0]]  # Ejemplo de etiquetas
                        })
    return fragments, metadata

# Generar embeddings e insertar en Milvus
def load_to_milvus(fragments, metadata):
    client = MilvusClient("./milvus_knowledge.db")
    if client.has_collection("system_knowledge"):
        client.drop_collection("system_knowledge")
    client.create_collection(
        collection_name="system_knowledge",
        dimension=384,  # Dimensión del modelo all-MiniLM-L6-v2
    )
    embeddings = embedding_model.encode(fragments)
    data = [
        {"id": i, "vector": embeddings[i], "text": fragments[i], "metadata": metadata[i]}
        for i in range(len(fragments))
    ]
    client.insert(collection_name="system_knowledge", data=data)

# Crear base de conocimiento con Agno
async def setup_knowledge_base():
    fragments, metadata = preprocess_md_files("./knowledge_base")
    load_to_milvus(fragments, metadata)
    knowledge_base = TextKnowledgeBase(
        texts=fragments,
        vector_db=vector_db,
    )
    await knowledge_base.aload(recreate=False)
    return knowledge_base

# Crear y usar el agente RAG
async def main():
    knowledge_base = await setup_knowledge_base()
    agent = Agent(
        knowledge=knowledge_base,
        use_tools=True,
        show_tool_calls=True
    )
    # Ejemplo de consulta
    query = "Explicar cómo funciona el módulo de pagos"
    response = await agent.aprint_response(query, markdown=True)
    print(response)

if __name__ == "__main__":
    asyncio.run(main())