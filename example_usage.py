#!/usr/bin/env python3
"""
Ejemplo de uso del sistema RAG
Este script demuestra cómo usar el sistema para hacer consultas sobre la base de conocimiento
"""

import asyncio
import os
from pathlib import Path

async def ejemplo_consulta_simple():
    """Ejemplo básico de consulta al sistema RAG"""
    print("🔍 Ejemplo: Consulta Simple")
    print("-" * 40)
    
    try:
        from app.rag_system import setup_knowledge_base, Agent
        
        # Configurar base de conocimiento
        print("📚 Configurando base de conocimiento...")
        knowledge_base = await setup_knowledge_base()
        
        # Crear agente
        print("🤖 Creando agente RAG...")
        agent = Agent(
            knowledge=knowledge_base,
            use_tools=True,
            show_tool_calls=True
        )
        
        # Ejemplo de consulta
        query = "¿Cómo funciona el sistema de pagos?"
        print(f"❓ Consulta: {query}")
        
        # Obtener respuesta
        print("🔄 Procesando consulta...")
        response = await agent.aprint_response(query, markdown=True)
        
        print("\n📝 Respuesta:")
        print(response)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Asegúrate de tener configuradas las variables de entorno")

async def ejemplo_consultas_multiples():
    """Ejemplo con múltiples consultas"""
    print("\n🔍 Ejemplo: Múltiples Consultas")
    print("-" * 40)
    
    try:
        from app.rag_system import setup_knowledge_base, Agent
        
        # Configurar una sola vez
        knowledge_base = await setup_knowledge_base()
        agent = Agent(
            knowledge=knowledge_base,
            use_tools=True,
            show_tool_calls=True
        )
        
        # Lista de consultas de ejemplo
        consultas = [
            "¿Qué métodos de autenticación están disponibles?",
            "¿Cómo se manejan los errores en el sistema de pagos?",
            "¿Qué medidas de seguridad implementa el sistema?",
            "¿Cómo funciona el procesamiento de transacciones?"
        ]
        
        for i, consulta in enumerate(consultas, 1):
            print(f"\n{i}. ❓ Consulta: {consulta}")
            print("🔄 Procesando...")
            
            try:
                response = await agent.aprint_response(consulta, markdown=True)
                print(f"📝 Respuesta: {response[:200]}...")
            except Exception as e:
                print(f"❌ Error en consulta {i}: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def ejemplo_procesamiento_documentos():
    """Ejemplo de cómo procesar nuevos documentos"""
    print("\n📄 Ejemplo: Procesamiento de Documentos")
    print("-" * 40)
    
    try:
        from app.rag_system import preprocess_md_files
        
        # Procesar archivos de conocimiento
        fragments, metadata = preprocess_md_files("./knowledge_base")
        
        print(f"📊 Estadísticas de procesamiento:")
        print(f"   - Fragmentos procesados: {len(fragments)}")
        print(f"   - Archivos de metadatos: {len(metadata)}")
        
        # Mostrar algunos fragmentos de ejemplo
        print(f"\n📝 Fragmentos de ejemplo:")
        for i, (fragment, meta) in enumerate(zip(fragments[:3], metadata[:3])):
            print(f"\n   Fragmento {i+1}:")
            print(f"   - Archivo: {meta['filename']}")
            print(f"   - Sección: {meta['section']}")
            print(f"   - Etiquetas: {meta['tags']}")
            print(f"   - Contenido: {fragment[:100]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def ejemplo_configuracion():
    """Ejemplo de configuración del sistema"""
    print("\n⚙️  Ejemplo: Configuración del Sistema")
    print("-" * 40)
    
    # Mostrar estructura de directorios
    print("📁 Estructura del proyecto:")
    for item in Path(".").rglob("*"):
        if item.is_file() and not item.name.startswith("."):
            print(f"   {item}")
    
    # Mostrar archivos de conocimiento
    knowledge_dir = Path("./knowledge_base")
    if knowledge_dir.exists():
        print(f"\n📚 Archivos de conocimiento:")
        for file in knowledge_dir.glob("*.md"):
            print(f"   - {file.name}")
    
    # Mostrar configuración de ejemplo
    print(f"\n🔧 Variables de entorno (ejemplo):")
    env_example = Path(".env.example")
    if env_example.exists():
        with open(env_example, 'r') as f:
            content = f.read()
            print(content)

async def main():
    """Función principal del ejemplo"""
    print("🚀 Ejemplos de Uso del Sistema RAG")
    print("=" * 50)
    
    # Ejecutar ejemplos
    await ejemplo_consulta_simple()
    await ejemplo_consultas_multiples()
    ejemplo_procesamiento_documentos()
    ejemplo_configuracion()
    
    print("\n" + "=" * 50)
    print("✅ Ejemplos completados")
    print("\n💡 Para usar el sistema:")
    print("1. Configura las variables de entorno en .env")
    print("2. Ejecuta: python app/rag_system.py")
    print("3. O usa las funciones programáticamente como en estos ejemplos")

if __name__ == "__main__":
    asyncio.run(main()) 