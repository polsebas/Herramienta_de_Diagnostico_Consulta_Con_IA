#!/usr/bin/env python3
"""
Ejemplo de uso del Agente Analizador
Este script muestra cómo usar el agente para analizar un proyecto específico
"""

import os
import sys
from pathlib import Path
from app.agente_analizador import AgenteAnalizador, generate_report

def analizar_proyecto(project_path: str, output_file: str | None = None, use_ai: bool = False):
    """
    Analiza un proyecto específico y genera un informe
    
    Args:
        project_path: Ruta al proyecto a analizar
        output_file: Nombre del archivo de salida (opcional)
        use_ai: Si usar análisis con IA (requiere OpenAI API key)
    """
    print(f"🔍 Analizando proyecto: {project_path}")
    
    # Verificar que el proyecto existe
    if not Path(project_path).exists():
        print(f"❌ Error: El proyecto {project_path} no existe")
        return None, None
    
    # Configurar OpenAI si se solicita
    api_key = None
    if use_ai:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("⚠️  OpenAI API key no configurada. Usando análisis básico.")
            print("   Para usar IA, configura: export OPENAI_API_KEY='tu-api-key'")
        else:
            print("🤖 Usando análisis con IA")
    
    # Crear agente
    print("🔄 Inicializando agente analizador...")
    agente = AgenteAnalizador(project_path, api_key)
    
    # Ejecutar análisis
    print("🔄 Ejecutando análisis completo...")
    resultados = agente.run_analysis()
    
    # Generar informe
    print("📝 Generando informe...")
    informe = generate_report(resultados)
    
    # Guardar informe
    if not output_file:
        project_name = Path(project_path).name
        output_file = f"informe_{project_name}.md"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(informe)
    
    print(f"✅ Informe guardado en: {output_file}")
    print(f"📄 Tamaño: {len(informe)} caracteres")
    
    return resultados, informe

def mostrar_resumen(resultados):
    """Muestra un resumen de los resultados del análisis"""
    print("\n📊 RESUMEN DEL ANÁLISIS")
    print("=" * 50)
    
    # Análisis funcional
    funcional = resultados.get('funcional', {})
    print("\n📋 Análisis Funcional:")
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
        for i, op in enumerate(oportunidades[:5], 1):  # Mostrar las primeras 5
            print(f"     {i}. {op['oportunidad']}")
        if len(oportunidades) > 5:
            print(f"     ... y {len(oportunidades) - 5} más")

def ejemplo_analisis_basico():
    """Ejemplo de análisis básico sin IA"""
    print("🎯 EJEMPLO: ANÁLISIS BÁSICO")
    print("=" * 50)
    
    # Analizar el proyecto actual
    project_path = "."
    
    resultados, informe = analizar_proyecto(project_path, "ejemplo_basico.md", use_ai=False)
    
    if resultados:
        mostrar_resumen(resultados)
    
    return resultados

def ejemplo_analisis_con_ia():
    """Ejemplo de análisis con IA (si está disponible)"""
    print("\n🤖 EJEMPLO: ANÁLISIS CON IA")
    print("=" * 50)
    
    # Verificar si hay API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠️  OpenAI API key no configurada")
        print("   Para usar este ejemplo, configura:")
        print("   export OPENAI_API_KEY='tu-api-key-aqui'")
        return None
    
    # Analizar con IA
    project_path = "."
    resultados, informe = analizar_proyecto(project_path, "ejemplo_con_ia.md", use_ai=True)
    
    if resultados:
        mostrar_resumen(resultados)
        
        # Mostrar fragmento del análisis con IA
        funcional = resultados.get('funcional', {})
        if 'documentacion_analisis' in funcional:
            print("\n📖 ANÁLISIS DE DOCUMENTACIÓN CON IA:")
            print("-" * 40)
            analisis = funcional['documentacion_analisis']
            if not analisis.startswith('Error'):
                lines = analisis.split('\n')[:5]
                for line in lines:
                    print(line)
                print("...")
    
    return resultados

def ejemplo_analisis_personalizado():
    """Ejemplo de análisis personalizado"""
    print("\n⚙️  EJEMPLO: ANÁLISIS PERSONALIZADO")
    print("=" * 50)
    
    # Crear agente
    agente = AgenteAnalizador(".", os.getenv('OPENAI_API_KEY'))
    
    # Escanear proyecto
    print("🔄 Escaneando estructura del proyecto...")
    agente.scan_project_structure()
    
    print(f"📁 Archivos encontrados:")
    print(f"   • Documentación: {len(agente.documentation_files)}")
    print(f"   • Código: {len(agente.code_files)}")
    print(f"   • Configuración: {len(agente.config_files)}")
    print(f"   • Otros: {len(agente.other_files)}")
    
    # Análisis funcional personalizado
    print("\n🔄 Ejecutando análisis funcional...")
    agente.analisis_funcional()
    
    # Análisis técnico personalizado
    print("🔄 Ejecutando análisis técnico...")
    agente.analisis_tecnico_profundo()
    
    # Mostrar algunos resultados específicos
    tecnico = agente.analysis_results.get('tecnico', {})
    if 'codigo' in tecnico:
        codigo = tecnico['codigo']
        print(f"\n📊 Lenguajes detectados:")
        for lang, count in codigo.get('lenguajes', {}).items():
            print(f"   • {lang}: {count} archivos")
    
    if 'dependencias' in tecnico:
        deps = tecnico['dependencias']
        print(f"\n📦 Dependencias detectadas:")
        for dep in deps.get('dependencias_detectadas', [])[:5]:
            print(f"   • {dep.get('paquete', 'N/A')} v{dep.get('version', 'N/A')}")
    
    return agente.analysis_results

def main():
    """Función principal del ejemplo"""
    print("🚀 EJEMPLOS DE USO DEL AGENTE ANALIZADOR")
    print("=" * 60)
    
    try:
        # Ejemplo 1: Análisis básico
        ejemplo_analisis_basico()
        
        # Ejemplo 2: Análisis con IA
        ejemplo_analisis_con_ia()
        
        # Ejemplo 3: Análisis personalizado
        ejemplo_analisis_personalizado()
        
        print("\n" + "=" * 60)
        print("✅ EJEMPLOS COMPLETADOS")
        print("\n📋 Archivos generados:")
        print("   • ejemplo_basico.md - Análisis básico")
        print("   • ejemplo_con_ia.md - Análisis con IA (si está disponible)")
        print("   • informe_analisis_.md - Informe del proyecto actual")
        
        print("\n🎯 Próximos pasos:")
        print("   1. Revisar los informes generados")
        print("   2. Personalizar el análisis según necesidades")
        print("   3. Configurar OpenAI para análisis con IA")
        
    except Exception as e:
        print(f"\n❌ Error en ejemplos: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 