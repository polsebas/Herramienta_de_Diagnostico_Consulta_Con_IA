import asyncio
import os
from pathlib import Path
from agno.agent import Agent
from agno.knowledge.text import TextKnowledgeBase
from agno.vectordb.milvus import Milvus
from pymilvus import MilvusClient
from sentence_transformers import SentenceTransformer
import ast
import json

# Configuración de Milvus
vector_db = Milvus(
    collection="system_knowledge",
    uri="http://host.docker.internal:19530",  # Usamos Milvus Lite
)
# client = MilvusClient(
#     uri="http://host.docker.internal:19530",
#     token="root:Milvus"
# )

# res = client.list_collections()

# if "system_knowledge" not in res:
#     raise ValueError(f"Collection {"system_knowledge"} does not exist")

# load_state = client.get_load_state(
#     collection_name="system_knowledge"
# )

# if load_state["state"] != "Loaded":
#     print("Loading collection...")
#     client.load_collection(
#         collection_name="system_knowledge"
#     )


# Modelo de embeddings
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Agente para análisis de código fuente
class SourceCodeAnalyzer:
    def __init__(self, source_dir):
        self.source_dir = source_dir
        self.components = []
        self.interactions = []
        self.functions = []
        self.limitations = []

    def analyze_files(self):
        """Analiza los archivos de código fuente en el directorio especificado."""
        print(f"Analizando archivos en el directorio: {self.source_dir}")
        extensiones = (
            '.py', '.js', '.java', '.json', '.yml',
            '.cs', '.cshtml', '.razor', '.csproj', '.html', '.css', '.md'
        )
        for root, _, files in os.walk(self.source_dir):
            print(f"Analizando directorio: {root}")
            for file in files:
                if file.endswith(extensiones):
                    print(f"Analizando archivo: {file}")
                    file_path = os.path.join(root, file)
                    self._analyze_file(file_path)

    def _analyze_file(self, file_path):
        """Analiza un archivo individual para extraer componentes, funciones e interacciones."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
            except Exception as e:
                self.limitations.append({
                    "file": file_path,
                    "issue": f"No se pudo leer el archivo: {e}"
                })
                return

        # Extraer información básica del archivo
        component = {
            "name": os.path.basename(file_path),
            "path": file_path,
            "type": self._detect_file_type(file_path),
        }

        # Análisis específico según el tipo de archivo
        if file_path.endswith('.py'):
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        self.functions.append({
                            "name": node.name,
                            "file": file_path,
                            "docstring": ast.get_docstring(node) or "No docstring"
                        })
                    if isinstance(node, ast.Call):
                        self.interactions.append({
                            "caller": file_path,
                            "called": "Unknown",  # Podría mejorarse con análisis más profundo
                        })
            except SyntaxError:
                self.limitations.append({
                    "file": file_path,
                    "issue": "Syntax error detected"
                })

        elif file_path.endswith('.json') or file_path.endswith('.yml'):
            component["role"] = "Configuration"
            self.components.append(component)

        # Agregar el componente detectado
        self.components.append(component)

    def _detect_file_type(self, file_path):
        """Determina el tipo de archivo (código, configuración, etc.)."""
        if file_path.endswith(('.py', '.js', '.java')):
            return "Code"
        elif file_path.endswith(('.json', '.yml')):
            return "Configuration"
        return "Unknown"

    def summarize(self):
        """Genera un resumen del análisis."""
        return {
            "components": self.components,
            "interactions": self.interactions,
            "functions": self.functions,
            "limitations": self.limitations
        }

# Agente para generar el prompt de entendimiento
async def generate_understanding_prompt(analysis):
    """Genera un prompt Markdown con el entendimiento básico del sistema."""
    prompt = "# Entendimiento Básico del Sistema\n\n"
    prompt += "## Resumen General\n"
    prompt += "El sistema es una aplicación compuesta por múltiples componentes, incluyendo archivos de código y configuración. A continuación, se detalla su estructura.\n\n"

    prompt += "## Componentes\n"
    for component in analysis["components"]:
        prompt += f"- **{component['name']}**: {component['type']} ubicado en {component['path']}\n"

    prompt += "\n## Interacciones\n"
    for interaction in analysis["interactions"]:
        prompt += f"- Llamada desde {interaction['caller']} a {interaction['called']}\n"

    prompt += "\n## Funciones Principales\n"
    for func in analysis["functions"]:
        prompt += f"- **{func['name']}** en {func['file']}: {func['docstring']}\n"

    prompt += "\n## Limitaciones\n"
    for limitation in analysis["limitations"]:
        prompt += f"- Problema en {limitation['file']}: {limitation['issue']}\n"

    return prompt

# Guardar el prompt en un archivo MD e indexarlo en Milvus
def save_to_knowledge_base(prompt, filename="system_understanding.md"):
    """Guarda el prompt en un archivo MD y lo indexa en Milvus."""
    output_path = os.path.join("./knowledge_base", filename)
    os.makedirs("./knowledge_base", exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(prompt)

    # Indexar en Milvus
    #client = MilvusClient("./milvus_knowledge.db")
    client = MilvusClient(
        uri="http://host.docker.internal:19530",
        token="root:Milvus"
    )
    if not client.has_collection("system_knowledge"):
        client.create_collection(
            collection_name="system_knowledge",
            dimension=384
        )
    embedding = embedding_model.encode([prompt])[0]
    data = [{
        "id": 0,
        "vector": embedding,
        "text": prompt,
        "metadata": {"filename": filename, "tags": ["system_understanding"]}
    }]
    client.insert(collection_name="system_knowledge", data=data)

# Configurar y ejecutar el agente
async def main():
    # Directorio con los archivos fuente
    source_dir = "/mnt/fuentes/"
    
    # Analizar los archivos
    analyzer = SourceCodeAnalyzer(source_dir)
    analyzer.analyze_files()
    analysis = analyzer.summarize()

    print("Análisis completado. Resumen:")
    print(json.dumps(analysis, indent=2))
    # Configurar el agente Agno
    knowledge_base = TextKnowledgeBase(
        texts=[json.dumps(analysis)],
        vector_db=vector_db,
        path=source_dir  # o la ruta relevante a tus documentos
    )
    await knowledge_base.aload(recreate=False)

    agent = Agent(
        knowledge=knowledge_base,
        use_tools=True,
        show_tool_calls=True
    )

    # Generar el prompt de entendimiento
    prompt = await generate_understanding_prompt(analysis)
    print(prompt)

    # Guardar el prompt en la base de conocimiento
    save_to_knowledge_base(prompt)

if __name__ == "__main__":
    asyncio.run(main())