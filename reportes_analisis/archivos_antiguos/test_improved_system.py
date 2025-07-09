#!/usr/bin/env python3
"""
Script de prueba para el sistema RAG mejorado
"""

import asyncio
import sys
from pathlib import Path

def test_imports():
    """Prueba que todas las importaciones funcionen"""
    print("🔄 Probando importaciones del sistema mejorado...")
    
    try:
        from app.rag_system_improved import VectorKnowledgeBase, RAGSystem
        print("✅ VectorKnowledgeBase y RAGSystem importados correctamente")
        return True
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        return False

def test_vector_knowledge_base():
    """Prueba la clase VectorKnowledgeBase"""
    print("\n🔄 Probando VectorKnowledgeBase...")
    
    try:
        from app.rag_system_improved import VectorKnowledgeBase
        
        # Crear instancia
        vkb = VectorKnowledgeBase("./test_improved_milvus.db")
        print("✅ VectorKnowledgeBase creado correctamente")
        
        # Probar procesamiento de archivos
        fragments, metadata = vkb.preprocess_md_files("./knowledge_base")
        
        if fragments:
            print(f"✅ Procesamiento de archivos exitoso: {len(fragments)} fragmentos")
            
            # Probar carga a base de datos
            success = vkb.load_to_vector_db(fragments, metadata)
            if success:
                print("✅ Carga a base de datos vectorial exitosa")
                
                # Probar búsqueda
                results = vkb.search_similar("sistema de pagos", limit=3)
                print(f"✅ Búsqueda exitosa: {len(results)} resultados encontrados")
                
                return True
            else:
                print("❌ Error en carga a base de datos")
                return False
        else:
            print("❌ No se encontraron fragmentos para procesar")
            return False
            
    except Exception as e:
        print(f"❌ Error en VectorKnowledgeBase: {e}")
        return False

async def test_rag_system():
    """Prueba el sistema RAG completo"""
    print("\n🔄 Probando sistema RAG completo...")
    
    try:
        from app.rag_system_improved import setup_rag_system
        
        # Configurar sistema
        rag_system = await setup_rag_system("./test_improved_milvus.db")
        print("✅ Sistema RAG configurado correctamente")
        
        # Probar consulta
        result = await rag_system.query("¿Cómo funciona el sistema de pagos?", limit=3)
        
        if result and 'response' in result:
            print("✅ Consulta exitosa")
            print(f"   Respuesta: {result['response'][:100]}...")
            print(f"   Fragmentos encontrados: {len(result['fragments'])}")
            return True
        else:
            print("❌ Error en consulta")
            return False
            
    except Exception as e:
        print(f"❌ Error en sistema RAG: {e}")
        return False

def test_search_only():
    """Prueba la búsqueda sin generación de respuesta"""
    print("\n🔄 Probando búsqueda sin respuesta...")
    
    try:
        from app.rag_system_improved import RAGSystem
        
        # Crear sistema
        rag_system = RAGSystem("./test_improved_milvus.db")
        
        # Probar búsqueda
        results = rag_system.search_only("autenticación", limit=3)
        
        if results:
            print(f"✅ Búsqueda exitosa: {len(results)} resultados")
            for i, result in enumerate(results):
                print(f"   Resultado {i+1}: Score {result.get('score', 0):.3f}")
            return True
        else:
            print("❌ No se encontraron resultados")
            return False
            
    except Exception as e:
        print(f"❌ Error en búsqueda: {e}")
        return False

async def main():
    """Función principal de pruebas"""
    print("🧪 Iniciando pruebas del sistema RAG mejorado")
    print("=" * 60)
    
    tests = [
        ("Importaciones", test_imports),
        ("VectorKnowledgeBase", test_vector_knowledge_base),
        ("Sistema RAG Completo", test_rag_system),
        ("Búsqueda Sin Respuesta", test_search_only),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
                
            if result:
                passed += 1
            else:
                print(f"❌ {test_name} falló")
        except Exception as e:
            print(f"❌ {test_name} falló con excepción: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Resultados: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! El sistema mejorado está listo.")
        print("\n📋 Ventajas del sistema mejorado:")
        print("✅ Usa directamente la base de datos vectorial")
        print("✅ Mejor rendimiento en búsquedas")
        print("✅ Más control sobre el proceso")
        print("✅ Separación clara entre búsqueda y generación")
        print("✅ Mejor manejo de errores y logging")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main())) 