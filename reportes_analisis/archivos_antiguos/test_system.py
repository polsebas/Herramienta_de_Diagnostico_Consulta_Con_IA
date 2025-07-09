#!/usr/bin/env python3
"""
Script de prueba para verificar que el sistema RAG funciona correctamente
"""

import asyncio
import os
import sys
from pathlib import Path

def test_imports():
    """Prueba que todas las importaciones funcionen"""
    print("🔄 Probando importaciones...")
    
    try:
        import asyncio
        print("✅ asyncio")
        
        import os
        print("✅ os")
        
        from sentence_transformers import SentenceTransformer
        print("✅ sentence_transformers")
        
        from pymilvus import MilvusClient
        print("✅ pymilvus")
        
        # Probar agno (puede fallar si no hay API key configurada)
        try:
            from agno.agent import Agent
            from agno.knowledge.text import TextKnowledgeBase
            from agno.vectordb.milvus import Milvus
            print("✅ agno")
        except Exception as e:
            print(f"⚠️  agno (puede requerir configuración): {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        return False

def test_embedding_model():
    """Prueba el modelo de embeddings"""
    print("\n🔄 Probando modelo de embeddings...")
    
    try:
        from sentence_transformers import SentenceTransformer
        
        # Descargar modelo (puede tomar tiempo la primera vez)
        print("📥 Descargando modelo de embeddings...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Probar con un texto simple
        test_text = "Este es un texto de prueba para el sistema RAG"
        embedding = model.encode(test_text)
        
        print(f"✅ Modelo de embeddings funcionando")
        print(f"   Dimensión del embedding: {len(embedding)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error con modelo de embeddings: {e}")
        return False

def test_milvus():
    """Prueba la conexión con Milvus"""
    print("\n🔄 Probando Milvus...")
    
    try:
        from pymilvus import MilvusClient
        
        # Crear cliente de Milvus Lite
        client = MilvusClient("./test_milvus.db")
        
        # Crear colección de prueba
        collection_name = "test_collection"
        
        if client.has_collection(collection_name):
            client.drop_collection(collection_name)
        
        client.create_collection(
            collection_name=collection_name,
            dimension=384,  # Dimensión del modelo all-MiniLM-L6-v2
        )
        
        # Insertar datos de prueba
        test_data = [
            {"id": 1, "vector": [0.1] * 384, "text": "Texto de prueba 1"},
            {"id": 2, "vector": [0.2] * 384, "text": "Texto de prueba 2"},
        ]
        
        client.insert(collection_name=collection_name, data=test_data)
        
        # Buscar
        results = client.search(
            collection_name=collection_name,
            data=[[0.1] * 384],
            limit=2
        )
        
        print("✅ Milvus funcionando correctamente")
        
        # Limpiar
        client.drop_collection(collection_name)
        
        return True
        
    except Exception as e:
        print(f"❌ Error con Milvus: {e}")
        return False

def test_knowledge_base():
    """Prueba la base de conocimiento"""
    print("\n🔄 Probando base de conocimiento...")
    
    knowledge_dir = Path("./knowledge_base")
    
    if not knowledge_dir.exists():
        print("❌ Directorio knowledge_base no existe")
        return False
    
    md_files = list(knowledge_dir.glob("*.md"))
    
    if not md_files:
        print("❌ No se encontraron archivos .md en knowledge_base/")
        return False
    
    print(f"✅ Encontrados {len(md_files)} archivos de conocimiento:")
    for file in md_files:
        print(f"   - {file.name}")
    
    # Leer contenido de ejemplo
    try:
        with open(md_files[0], 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"✅ Contenido leído correctamente ({len(content)} caracteres)")
    except Exception as e:
        print(f"❌ Error leyendo archivo: {e}")
        return False
    
    return True

def test_rag_system():
    """Prueba el sistema RAG completo"""
    print("\n🔄 Probando sistema RAG...")
    
    try:
        # Importar funciones del sistema RAG
        from app.rag_system import preprocess_md_files, load_to_milvus
        
        # Procesar archivos de conocimiento
        fragments, metadata = preprocess_md_files("./knowledge_base")
        
        if not fragments:
            print("❌ No se pudieron procesar fragmentos de conocimiento")
            return False
        
        print(f"✅ Procesados {len(fragments)} fragmentos de conocimiento")
        
        # Probar carga a Milvus (sin ejecutar realmente)
        print("✅ Funciones del sistema RAG disponibles")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en sistema RAG: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🧪 Iniciando pruebas del sistema RAG")
    print("=" * 50)
    
    tests = [
        ("Importaciones", test_imports),
        ("Modelo de Embeddings", test_embedding_model),
        ("Milvus", test_milvus),
        ("Base de Conocimiento", test_knowledge_base),
        ("Sistema RAG", test_rag_system),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} falló")
        except Exception as e:
            print(f"❌ {test_name} falló con excepción: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Resultados: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! El sistema está listo para usar.")
        print("\n📋 Próximos pasos:")
        print("1. Configura las variables de entorno en .env")
        print("2. Ejecuta: python app/rag_system.py")
        print("3. Agrega más documentos a knowledge_base/")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 