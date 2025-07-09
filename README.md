# Sistema RAG de Diagnóstico y Consulta con IA

Este proyecto implementa un sistema de Retrieval-Augmented Generation (RAG) que permite consultar una base de conocimiento técnica usando inteligencia artificial.

## 🚀 Características

- **Base de Conocimiento Vectorial**: Almacena y busca información técnica usando embeddings
- **Búsqueda Semántica**: Encuentra información relevante usando similitud de significado
- **Generación de Respuestas**: Genera respuestas contextualizadas basadas en la información encontrada
- **Procesamiento de Documentos Markdown**: Lee y procesa archivos .md automáticamente
- **Interfaz Simple**: API fácil de usar para consultas

## 📋 Requisitos

- Python 3.8 o superior
- 4GB RAM mínimo (recomendado 8GB)
- 2GB espacio en disco

## 🛠️ Instalación

### Opción 1: Instalación Automática (Recomendada)

```bash
# Clonar el repositorio
git clone <url-del-repositorio>
cd Herramienta_de_Diagnostico_Consulta_Con_IA

# Ejecutar el script de configuración
python setup.py
```

### Opción 2: Instalación Manual

```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
# En Windows:
.venv\Scripts\activate
# En Linux/macOS:
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Crear directorios necesarios
mkdir -p logs data models

# Copiar archivo de configuración
cp .env.example .env
```

## ⚙️ Configuración

1. **Configurar variables de entorno**:
   ```bash
   cp .env.example .env
   # Editar .env con tus configuraciones
   ```

2. **Agregar documentos a la base de conocimiento**:
   ```bash
   # Agregar archivos .md al directorio knowledge_base/
   cp tu-documento.md knowledge_base/
   ```

## 🚀 Uso

### Ejecutar el Sistema

```bash
# Activar entorno virtual
source .venv/bin/activate  # Linux/macOS
# o
.venv\Scripts\activate     # Windows

# Ejecutar el sistema RAG
python app/rag_system.py
```

### Ejemplo de Uso Programático

```python
import asyncio
from app.rag_system import setup_knowledge_base, Agent

async def consultar_sistema():
    # Configurar base de conocimiento
    knowledge_base = await setup_knowledge_base()
    
    # Crear agente
    agent = Agent(
        knowledge=knowledge_base,
        use_tools=True,
        show_tool_calls=True
    )
    
    # Hacer consulta
    query = "¿Cómo funciona el sistema de pagos?"
    response = await agent.aprint_response(query, markdown=True)
    print(response)

# Ejecutar
asyncio.run(consultar_sistema())
```

## 📁 Estructura del Proyecto

```
Herramienta_de_Diagnostico_Consulta_Con_IA/
├── app/
│   ├── rag_system.py          # Sistema RAG principal
│   └── source_analysis_agents.py
├── knowledge_base/            # Base de conocimiento
│   ├── sistema_pagos.md
│   └── autenticacion.md
├── logs/                      # Archivos de log
├── data/                      # Datos temporales
├── models/                    # Modelos descargados
├── requirements.txt           # Dependencias
├── setup.py                   # Script de configuración
├── .env.example              # Configuración de ejemplo
└── README.md                 # Este archivo
```

## 🔧 Configuración Avanzada

### Variables de Entorno

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `MILVUS_URI` | URI de la base de datos vectorial | `./milvus_knowledge.db` |
| `MILVUS_COLLECTION` | Nombre de la colección | `system_knowledge` |
| `EMBEDDING_MODEL` | Modelo de embeddings | `all-MiniLM-L6-v2` |
| `LOG_LEVEL` | Nivel de logging | `INFO` |
| `DEBUG` | Modo debug | `True` |

### Personalizar el Modelo de Embeddings

```python
# En rag_system.py
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')  # Cambiar por otro modelo
```

### Agregar Nuevos Documentos

1. Coloca archivos `.md` en el directorio `knowledge_base/`
2. El sistema los procesará automáticamente
3. Los documentos se dividirán en fragmentos y se indexarán

## 🐛 Solución de Problemas

### Error: "Import could not be resolved"

```bash
# Asegúrate de que el entorno virtual esté activado
source .venv/bin/activate
pip install -r requirements.txt
```

### Error: "Milvus connection failed"

```bash
# Verificar que Milvus Lite esté funcionando
python -c "from pymilvus import MilvusClient; print('Milvus OK')"
```

### Error: "Model not found"

```bash
# El modelo se descargará automáticamente en la primera ejecución
# Si falla, descarga manualmente:
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

## 📊 Monitoreo

### Logs

Los logs se guardan en `logs/rag_system.log` con información sobre:
- Consultas procesadas
- Tiempo de respuesta
- Errores y advertencias
- Uso de memoria

### Métricas

El sistema registra:
- Número de consultas por hora
- Tiempo promedio de respuesta
- Tasa de éxito de búsquedas
- Uso de recursos

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

Si encuentras problemas:

1. Revisa la sección de [Solución de Problemas](#-solución-de-problemas)
2. Consulta los logs en `logs/rag_system.log`
3. Abre un issue en el repositorio

## 🔮 Roadmap

- [ ] Interfaz web para consultas
- [ ] Soporte para más formatos de documento
- [ ] Integración con bases de datos externas
- [ ] Sistema de feedback para mejorar respuestas
- [ ] Cache inteligente para consultas frecuentes 