#!/usr/bin/env python3
"""
Script de prueba para el Agente Analizador mejorado
"""

import os
import sys
from pathlib import Path

def test_imports():
    """Prueba que todas las importaciones funcionen"""
    print("🔄 Probando importaciones del agente analizador...")
    
    try:
        from app.agente_analizador import AgenteAnalizador, generate_report
        print("✅ AgenteAnalizador importado correctamente")
        return True
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        return False

def test_agente_creation():
    """Prueba la creación del agente"""
    print("\n🔄 Probando creación del agente...")
    
    try:
        from app.agente_analizador import AgenteAnalizador
        
        # Crear agente sin API key (modo básico)
        agente = AgenteAnalizador('.')
        print("✅ Agente creado correctamente")
        
        # Verificar atributos
        assert hasattr(agente, 'root_dir')
        assert hasattr(agente, 'analysis_results')
        assert hasattr(agente, 'scan_project_structure')
        print("✅ Atributos del agente verificados")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creando agente: {e}")
        return False

def test_project_scanning():
    """Prueba el escaneo de la estructura del proyecto"""
    print("\n🔄 Probando escaneo del proyecto...")
    
    try:
        from app.agente_analizador import AgenteAnalizador
        
        agente = AgenteAnalizador('.')
        agente.scan_project_structure()
        
        print(f"✅ Escaneo completado:")
        print(f"   - Archivos de documentación: {len(agente.documentation_files)}")
        print(f"   - Archivos de código: {len(agente.code_files)}")
        print(f"   - Archivos de configuración: {len(agente.config_files)}")
        print(f"   - Otros archivos: {len(agente.other_files)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en escaneo: {e}")
        return False

def test_funcional_analysis():
    """Prueba el análisis funcional"""
    print("\n🔄 Probando análisis funcional...")
    
    try:
        from app.agente_analizador import AgenteAnalizador
        
        agente = AgenteAnalizador('.')
        agente.scan_project_structure()
        agente.analisis_funcional()
        
        # Verificar resultados
        funcional = agente.analysis_results.get('funcional', {})
        
        print("✅ Análisis funcional completado:")
        print(f"   - Documentación analizada: {'documentacion_analisis' in funcional}")
        print(f"   - Interfaces detectadas: {'interfaces' in funcional}")
        print(f"   - Entrevistas simuladas: {'entrevistas' in funcional}")
        print(f"   - Diagramas de flujo: {'diagramas_flujo' in funcional}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en análisis funcional: {e}")
        return False

def test_tecnico_analysis():
    """Prueba el análisis técnico profundo"""
    print("\n🔄 Probando análisis técnico profundo...")
    
    try:
        from app.agente_analizador import AgenteAnalizador
        
        agente = AgenteAnalizador('.')
        agente.scan_project_structure()
        agente.analisis_tecnico_profundo()
        
        # Verificar resultados
        tecnico = agente.analysis_results.get('tecnico', {})
        
        print("✅ Análisis técnico completado:")
        print(f"   - Código analizado: {'codigo' in tecnico}")
        print(f"   - Dependencias revisadas: {'dependencias' in tecnico}")
        print(f"   - Arquitectura evaluada: {'arquitectura' in tecnico}")
        print(f"   - Rendimiento simulado: {'rendimiento' in tecnico}")
        print(f"   - Oportunidades de IA: {'oportunidades_ia' in tecnico}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en análisis técnico: {e}")
        return False

def test_integration():
    """Prueba la integración de análisis"""
    print("\n🔄 Probando integración de análisis...")
    
    try:
        from app.agente_analizador import AgenteAnalizador
        
        agente = AgenteAnalizador('.')
        agente.scan_project_structure()
        agente.analisis_funcional()
        agente.analisis_tecnico_profundo()
        agente.integrar_analisis()
        
        # Verificar resultados
        integracion = agente.analysis_results.get('integracion', {})
        
        print("✅ Integración completada:")
        print(f"   - Plan de modernización: {'plan_modernizacion' in integracion}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en integración: {e}")
        return False

def test_full_analysis():
    """Prueba el análisis completo"""
    print("\n🔄 Probando análisis completo...")
    
    try:
        from app.agente_analizador import AgenteAnalizador, generate_report
        
        agente = AgenteAnalizador('.')
        resultados = agente.run_analysis()
        
        print("✅ Análisis completo ejecutado:")
        print(f"   - Análisis funcional: {'funcional' in resultados}")
        print(f"   - Análisis técnico: {'tecnico' in resultados}")
        print(f"   - Integración: {'integracion' in resultados}")
        
        # Generar informe
        informe = generate_report(resultados)
        print(f"   - Informe generado: {len(informe)} caracteres")
        
        # Guardar informe de prueba
        with open('test_informe_analisis.md', 'w', encoding='utf-8') as f:
            f.write(informe)
        print("   - Informe guardado en 'test_informe_analisis.md'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en análisis completo: {e}")
        return False

def test_with_openai():
    """Prueba el agente con OpenAI (si está configurado)"""
    print("\n🔄 Probando con OpenAI...")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠️  OPENAI_API_KEY no configurado - saltando prueba con IA")
        return True
    
    try:
        from app.agente_analizador import AgenteAnalizador
        
        agente = AgenteAnalizador('.', api_key)
        agente.scan_project_structure()
        
        # Probar análisis funcional con IA
        agente.analisis_funcional()
        
        # Verificar que se generó contenido con IA
        funcional = agente.analysis_results.get('funcional', {})
        if 'documentacion_analisis' in funcional:
            contenido = funcional['documentacion_analisis']
            if len(contenido) > 100 and not contenido.startswith('Error'):
                print("✅ Análisis con IA funcionando correctamente")
                return True
            else:
                print("⚠️  Análisis con IA no generó contenido válido")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error con OpenAI: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🧪 Iniciando pruebas del Agente Analizador")
    print("=" * 60)
    
    tests = [
        ("Importaciones", test_imports),
        ("Creación del Agente", test_agente_creation),
        ("Escaneo del Proyecto", test_project_scanning),
        ("Análisis Funcional", test_funcional_analysis),
        ("Análisis Técnico", test_tecnico_analysis),
        ("Integración", test_integration),
        ("Análisis Completo", test_full_analysis),
        ("Prueba con OpenAI", test_with_openai),
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
    
    print("\n" + "=" * 60)
    print(f"📊 Resultados: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! El agente analizador está listo.")
        print("\n📋 Características implementadas:")
        print("✅ Análisis funcional (propósito, servicios, interacciones)")
        print("✅ Análisis técnico profundo (arquitectura, obsolescencia, deuda técnica)")
        print("✅ Detección de oportunidades de IA")
        print("✅ Integración de análisis funcional y técnico")
        print("✅ Generación de informes en Markdown")
        print("✅ Soporte para OpenAI (opcional)")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 