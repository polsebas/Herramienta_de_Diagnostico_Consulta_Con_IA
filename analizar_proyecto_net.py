#!/usr/bin/env python3
"""
Script específico para analizar proyectos .NET/Blazor
Optimizado para archivos C#, Razor, y proyectos .NET
"""

import os
import sys
import argparse
from pathlib import Path
from app.agente_analizador import AgenteAnalizador, generate_report

def analizar_proyecto_net(project_path: str, use_ai: bool = False):
    """Analiza específicamente proyectos .NET/Blazor"""
    
    print("🔍 ANALIZANDO PROYECTO .NET/BLAZOR")
    print("=" * 60)
    print(f"📁 Ruta del proyecto: {project_path}")
    
    # Verificar que el proyecto existe
    if not Path(project_path).exists():
        print(f"❌ Error: El proyecto {project_path} no existe")
        print("\n💡 Posibles soluciones:")
        print("   1. Verifica la ruta del proyecto")
        print("   2. Asegúrate de que el proyecto existe")
        print("   3. Usa una ruta relativa o absoluta correcta")
        print("\n📋 Ejemplos de uso:")
        print("   python analizar_proyecto_net.py /mnt/fuentes")
        print("   python analizar_proyecto_net.py ./MiProyectoBlazor")
        print("   python analizar_proyecto_net.py /ruta/a/proyecto --ai")
        return None, None
    
    # Verificar si hay API key de OpenAI
    api_key = None
    if use_ai:
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            print("🤖 OpenAI configurado - usando análisis con IA")
        else:
            print("⚠️  OpenAI no configurado - usando análisis básico")
            print("   Para análisis con IA: export OPENAI_API_KEY='tu-api-key'")
    else:
        print("📊 Usando análisis básico (sin IA)")
    
    # Crear agente
    print("\n🔄 Inicializando agente analizador...")
    agente = AgenteAnalizador(project_path, api_key)
    
    # Ejecutar análisis completo
    print("🔄 Ejecutando análisis completo...")
    resultados = agente.run_analysis()
    
    # Generar informe detallado
    print("📝 Generando informe detallado...")
    informe = generate_report(resultados)
    
    # Obtener nombre del proyecto para los archivos
    project_name = Path(project_path).name
    if not project_name:
        project_name = "proyecto_net"
    
    # Guardar informe principal
    output_file = f"analisis_{project_name}_detallado.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(informe)
    
    print(f"✅ Informe principal guardado en: {output_file}")
    print(f"📄 Tamaño: {len(informe)} caracteres")
    
    # Generar informe resumido
    informe_resumido = generar_informe_resumido_net(resultados, project_name)
    output_resumido = f"analisis_{project_name}_resumen.md"
    with open(output_resumido, 'w', encoding='utf-8') as f:
        f.write(informe_resumido)
    
    print(f"✅ Informe resumido guardado en: {output_resumido}")
    
    # Mostrar resumen en consola
    mostrar_resumen_consola_net(resultados, project_name)
    
    return resultados, informe

def generar_informe_resumido_net(resultados, project_name: str):
    """Genera un informe resumido específico para proyectos .NET"""
    
    informe = f"# Análisis Resumido - Proyecto {project_name}\n\n"
    informe += "## 📊 Métricas Principales\n\n"
    
    # Métricas de código
    if 'tecnico' in resultados and 'codigo' in resultados['tecnico']:
        codigo = resultados['tecnico']['codigo']
        informe += f"- **Archivos analizados**: {codigo.get('archivos_analizados', 0)}\n"
        informe += f"- **Funciones totales**: {codigo.get('metricas', {}).get('total_funciones', 0)}\n"
        informe += f"- **Clases totales**: {codigo.get('metricas', {}).get('total_clases', 0)}\n"
        informe += f"- **Problemas detectados**: {len(codigo.get('problemas_detectados', []))}\n\n"
        
        # Mostrar lenguajes detectados
        if 'lenguajes' in codigo and codigo['lenguajes']:
            informe += "### 📊 Lenguajes Detectados\n\n"
            for lang, count in codigo['lenguajes'].items():
                informe += f"- **{lang}**: {count} archivos\n"
            informe += "\n"
    
    # Arquitectura
    if 'tecnico' in resultados and 'arquitectura' in resultados['tecnico']:
        arch = resultados['tecnico']['arquitectura']
        informe += f"- **Tipo de arquitectura**: {arch.get('tipo_estimado', 'Desconocido')}\n"
        informe += f"- **Patrones detectados**: {', '.join(arch.get('patrones_detectados', []))}\n"
        informe += f"- **Componentes principales**: {len(arch.get('componentes_principales', []))}\n\n"
    
    # Oportunidades de IA
    if 'tecnico' in resultados and 'oportunidades_ia' in resultados['tecnico']:
        oportunidades = resultados['tecnico']['oportunidades_ia']
        informe += f"- **Oportunidades de IA detectadas**: {len(oportunidades)}\n\n"
        
        if oportunidades:
            informe += "### 🤖 Principales Oportunidades de IA\n\n"
            for i, op in enumerate(oportunidades[:10], 1):
                informe += f"{i}. {op['oportunidad']}\n"
            if len(oportunidades) > 10:
                informe += f"... y {len(oportunidades) - 10} más\n"
            informe += "\n"
    
    # Dependencias
    if 'tecnico' in resultados and 'dependencias' in resultados['tecnico']:
        deps = resultados['tecnico']['dependencias']
        if deps.get('dependencias_detectadas'):
            informe += "### 📦 Dependencias Principales\n\n"
            for dep in deps['dependencias_detectadas'][:10]:
                informe += f"- {dep.get('paquete', 'N/A')} v{dep.get('version', 'N/A')}\n"
            informe += "\n"
    
    # Análisis funcional
    if 'funcional' in resultados:
        funcional = resultados['funcional']
        informe += "### 📋 Análisis Funcional\n\n"
        
        if 'interfaces' in funcional:
            interfaces = funcional['interfaces']
            informe += f"- **Archivos de interfaz**: {interfaces.get('total_interfaces', 0)}\n"
            informe += f"- **Archivos de API**: {interfaces.get('total_apis', 0)}\n\n"
        
        if 'diagramas_flujo' in funcional:
            informe += "### 🔄 Flujos Principales\n\n"
            for flujo in funcional['diagramas_flujo']:
                informe += f"- **{flujo.get('tipo', 'N/A')}**: {flujo.get('descripcion', 'N/A')}\n"
            informe += "\n"
    
    # Plan de modernización (si está disponible)
    if 'integracion' in resultados and 'plan_modernizacion' in resultados['integracion']:
        plan = resultados['integracion']['plan_modernizacion']
        if not plan.startswith('Error') and len(plan) > 100:
            informe += "### 🚀 Plan de Modernización\n\n"
            # Tomar solo las primeras líneas del plan
            lines = plan.split('\n')[:20]
            for line in lines:
                informe += f"{line}\n"
            if len(plan.split('\n')) > 20:
                informe += "...\n"
            informe += "\n"
    
    informe += "---\n"
    informe += "*Informe generado automáticamente por el Agente Analizador de Sistemas*\n"
    informe += f"*Proyecto: {project_name} (.NET/Blazor)*\n"
    
    return informe

def mostrar_resumen_consola_net(resultados, project_name: str):
    """Muestra un resumen en la consola para proyectos .NET"""
    
    print("\n" + "=" * 60)
    print(f"📊 RESUMEN DEL ANÁLISIS - {project_name.upper()}")
    print("=" * 60)
    
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
        
        # Mostrar lenguajes detectados
        if 'lenguajes' in codigo:
            print(f"\n📊 Lenguajes detectados:")
            for lang, count in codigo['lenguajes'].items():
                print(f"   • {lang}: {count} archivos")
    
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
        for i, op in enumerate(oportunidades[:5], 1):
            print(f"     {i}. {op['oportunidad']}")
        if len(oportunidades) > 5:
            print(f"     ... y {len(oportunidades) - 5} más")
    
    print("\n" + "=" * 60)
    print("✅ ANÁLISIS COMPLETADO")
    print("📋 Archivos generados:")
    print(f"   • analisis_{project_name}_detallado.md - Informe completo")
    print(f"   • analisis_{project_name}_resumen.md - Informe resumido")

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description='Analizar proyectos .NET/Blazor con el Agente Analizador',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python analizar_proyecto_net.py /mnt/fuentes
  python analizar_proyecto_net.py ./MiProyectoBlazor
  python analizar_proyecto_net.py /ruta/a/proyecto --ai
        """
    )
    parser.add_argument('project_path', help='Ruta al proyecto .NET/Blazor')
    parser.add_argument('--ai', action='store_true', help='Usar análisis con IA (requiere OpenAI API key)')
    
    args = parser.parse_args()
    
    print("🚀 INICIANDO ANÁLISIS DE PROYECTO .NET/BLAZOR")
    print("=" * 60)
    
    try:
        resultados, informe = analizar_proyecto_net(args.project_path, args.ai)
        
        if resultados:
            project_name = Path(args.project_path).name or "proyecto_net"
            print("\n🎉 ¡Análisis completado exitosamente!")
            print("\n📋 Archivos generados:")
            print(f"   • analisis_{project_name}_detallado.md - Informe completo")
            print(f"   • analisis_{project_name}_resumen.md - Informe resumido")
            
            print("\n🎯 Próximos pasos:")
            print("   1. Revisar los informes generados")
            print("   2. Analizar las oportunidades de IA detectadas")
            print("   3. Considerar las recomendaciones de modernización")
            
        else:
            print("❌ Error en el análisis")
            return 1
            
    except Exception as e:
        print(f"\n❌ Error durante el análisis: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 