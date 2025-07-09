#!/usr/bin/env python3
"""
Script de demostración del Agente Analizador
Muestra cómo usar el agente para analizar un sistema y generar informes
"""

import os
import sys
from pathlib import Path
from app.agente_analizador import AgenteAnalizador, generate_report

def demo_analysis(project_path: str = ".", openai_api_key: str | None = None):
    """
    Demuestra el análisis completo de un proyecto
    
    Args:
        project_path: Ruta al proyecto a analizar
        openai_api_key: API key de OpenAI (opcional)
    """
    print("🔍 DEMOSTRACIÓN DEL AGENTE ANALIZADOR")
    print("=" * 60)
    print(f"📁 Analizando proyecto: {project_path}")
    print(f"🤖 OpenAI configurado: {'Sí' if openai_api_key else 'No'}")
    print()
    
    # Crear agente
    print("🔄 Inicializando agente analizador...")
    agente = AgenteAnalizador(project_path, openai_api_key)
    
    # Ejecutar análisis completo
    print("🔄 Ejecutando análisis completo...")
    resultados = agente.run_analysis()
    
    # Mostrar resumen de resultados
    print("\n📊 RESUMEN DE RESULTADOS:")
    print("-" * 40)
    
    # Análisis funcional
    funcional = resultados.get('funcional', {})
    print("📋 Análisis Funcional:")
    print(f"   • Documentación analizada: {'✅' if 'documentacion_analisis' in funcional else '❌'}")
    print(f"   • Interfaces detectadas: {'✅' if 'interfaces' in funcional else '❌'}")
    print(f"   • Entrevistas simuladas: {'✅' if 'entrevistas' in funcional else '❌'}")
    print(f"   • Diagramas de flujo: {'✅' if 'diagramas_flujo' in funcional else '❌'}")
    
    # Análisis técnico
    tecnico = resultados.get('tecnico', {})
    print("\n🔧 Análisis Técnico:")
    print(f"   • Código analizado: {'✅' if 'codigo' in tecnico else '❌'}")
    print(f"   • Dependencias revisadas: {'✅' if 'dependencias' in tecnico else '❌'}")
    print(f"   • Arquitectura evaluada: {'✅' if 'arquitectura' in tecnico else '❌'}")
    print(f"   • Rendimiento simulado: {'✅' if 'rendimiento' in tecnico else '❌'}")
    print(f"   • Oportunidades de IA: {'✅' if 'oportunidades_ia' in tecnico else '❌'}")
    
    # Integración
    integracion = resultados.get('integracion', {})
    print("\n🔄 Integración:")
    print(f"   • Plan de modernización: {'✅' if 'plan_modernizacion' in integracion else '❌'}")
    
    # Detalles específicos
    if 'codigo' in tecnico:
        codigo = tecnico['codigo']
        print(f"\n📈 Métricas de Código:")
        print(f"   • Archivos analizados: {codigo.get('archivos_analizados', 0)}")
        print(f"   • Funciones totales: {codigo.get('metricas', {}).get('total_funciones', 0)}")
        print(f"   • Clases totales: {codigo.get('metricas', {}).get('total_clases', 0)}")
        print(f"   • Problemas detectados: {len(codigo.get('problemas_detectados', []))}")
    
    if 'arquitectura' in tecnico:
        arch = tecnico['arquitectura']
        print(f"\n🏗️  Arquitectura:")
        print(f"   • Tipo estimado: {arch.get('tipo_estimado', 'Desconocido')}")
        print(f"   • Patrones detectados: {', '.join(arch.get('patrones_detectados', []))}")
        print(f"   • Componentes principales: {len(arch.get('componentes_principales', []))}")
    
    if 'oportunidades_ia' in tecnico:
        oportunidades = tecnico['oportunidades_ia']
        print(f"\n🤖 Oportunidades de IA:")
        print(f"   • Oportunidades detectadas: {len(oportunidades)}")
        for i, op in enumerate(oportunidades[:3], 1):  # Mostrar solo las primeras 3
            print(f"     {i}. {op['oportunidad']}")
        if len(oportunidades) > 3:
            print(f"     ... y {len(oportunidades) - 3} más")
    
    # Generar informe
    print("\n📝 Generando informe detallado...")
    informe = generate_report(resultados)
    
    # Guardar informe
    output_file = f"informe_analisis_{Path(project_path).name}.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(informe)
    
    print(f"✅ Informe guardado en: {output_file}")
    print(f"📄 Tamaño del informe: {len(informe)} caracteres")
    
    return resultados, informe

def demo_specific_project():
    """Demuestra el análisis de un proyecto específico"""
    print("\n🎯 DEMOSTRACIÓN CON PROYECTO ESPECÍFICO")
    print("=" * 60)
    
    # Analizar el proyecto actual
    project_path = "."
    
    # Verificar si hay API key de OpenAI
    api_key = os.getenv('OPENAI_API_KEY')
    
    if api_key:
        print("🔑 OpenAI API key detectada - usando análisis con IA")
    else:
        print("⚠️  No se detectó OpenAI API key - usando análisis básico")
        print("   Para análisis con IA, configura OPENAI_API_KEY")
    
    # Ejecutar análisis
    resultados, informe = demo_analysis(project_path, api_key)
    
    # Mostrar fragmento del informe
    print("\n📋 FRAGMENTO DEL INFORME:")
    print("-" * 40)
    lines = informe.split('\n')[:20]  # Primeras 20 líneas
    for line in lines:
        print(line)
    print("...")
    
    return resultados

def demo_with_openai():
    """Demuestra el análisis con OpenAI (si está disponible)"""
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("\n⚠️  DEMOSTRACIÓN CON IA NO DISPONIBLE")
        print("=" * 60)
        print("Para usar análisis con IA, configura la variable de entorno:")
        print("export OPENAI_API_KEY='tu-api-key-aqui'")
        print("\nEl agente funcionará en modo básico sin IA.")
        return
    
    print("\n🤖 DEMOSTRACIÓN CON ANÁLISIS DE IA")
    print("=" * 60)
    
    # Crear agente con IA
    agente = AgenteAnalizador(".", api_key)
    
    # Ejecutar solo análisis funcional con IA
    print("🔄 Ejecutando análisis funcional con IA...")
    agente.scan_project_structure()
    agente.analisis_funcional()
    
    # Mostrar resultados de IA
    funcional = agente.analysis_results.get('funcional', {})
    
    if 'documentacion_analisis' in funcional:
        print("\n📖 ANÁLISIS DE DOCUMENTACIÓN CON IA:")
        print("-" * 40)
        analisis = funcional['documentacion_analisis']
        if not analisis.startswith('Error'):
            # Mostrar primeras líneas del análisis
            lines = analisis.split('\n')[:10]
            for line in lines:
                print(line)
            if len(analisis.split('\n')) > 10:
                print("...")
        else:
            print("❌ Error en análisis de documentación")
    
    if 'entrevistas' in funcional:
        print("\n👥 ENTREVISTAS SIMULADAS CON IA:")
        print("-" * 40)
        entrevistas = funcional['entrevistas']
        if isinstance(entrevistas, list):
            for i, entrevista in enumerate(entrevistas[:3], 1):
                print(f"\n{i}. {entrevista['pregunta']}")
                respuesta = entrevista['respuesta'][:200] + "..." if len(entrevista['respuesta']) > 200 else entrevista['respuesta']
                print(f"   Respuesta: {respuesta}")

def main():
    """Función principal de demostración"""
    print("🚀 INICIANDO DEMOSTRACIÓN DEL AGENTE ANALIZADOR")
    print("=" * 60)
    
    try:
        # Demostración básica
        demo_specific_project()
        
        # Demostración con IA (si está disponible)
        demo_with_openai()
        
        print("\n" + "=" * 60)
        print("✅ DEMOSTRACIÓN COMPLETADA")
        print("\n📋 Archivos generados:")
        print("   • informe_analisis_[proyecto].md - Informe completo")
        print("   • test_informe_analisis.md - Informe de pruebas")
        
        print("\n🎯 Próximos pasos:")
        print("   1. Revisar los informes generados")
        print("   2. Configurar OPENAI_API_KEY para análisis con IA")
        print("   3. Personalizar el agente según necesidades específicas")
        
    except Exception as e:
        print(f"\n❌ Error en demostración: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 