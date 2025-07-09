#!/usr/bin/env python3
"""
Script final optimizado para analizar el proyecto IntelliAI
Incluye mejor manejo de errores y instrucciones claras
"""

import os
import sys
import argparse
from pathlib import Path
from app.agente_analizador import AgenteAnalizador, generate_report

def verificar_rutas_posibles():
    """Verifica rutas posibles donde podría estar el proyecto IntelliAI"""
    rutas_posibles = [
        "/home/pablo/win/source/repos/IntelliAI",
        "/mnt/c/Users/pablo/source/repos/IntelliAI",
        "/mnt/d/Projects/IntelliAI",
        "/workspaces/IntelliAI",
        "/app/IntelliAI",
        "./IntelliAI",
        "../IntelliAI"
    ]
    
    rutas_existentes = []
    for ruta in rutas_posibles:
        if Path(ruta).exists():
            rutas_existentes.append(ruta)
    
    return rutas_existentes

def analizar_intelliai_final(project_path: str, use_ai: bool = False):
    """Analiza específicamente el proyecto IntelliAI con mejor manejo de errores"""
    
    print("🔍 ANALIZANDO PROYECTO INTELLIAI")
    print("=" * 60)
    print(f"📁 Ruta del proyecto: {project_path}")
    
    # Verificar que el proyecto existe
    if not Path(project_path).exists():
        print(f"❌ Error: El proyecto {project_path} no existe")
        
        # Verificar rutas posibles
        print("\n🔍 Verificando rutas posibles...")
        rutas_existentes = verificar_rutas_posibles()
        
        if rutas_existentes:
            print("✅ Proyectos encontrados en las siguientes rutas:")
            for ruta in rutas_existentes:
                print(f"   • {ruta}")
            print(f"\n💡 Usa una de estas rutas:")
            print(f"   python analizar_intelliai_final.py '{rutas_existentes[0]}'")
        else:
            print("\n💡 Posibles soluciones:")
            print("   1. Verifica que el proyecto IntelliAI existe")
            print("   2. Asegúrate de que la ruta es correcta")
            print("   3. Monta el proyecto en el devcontainer si es necesario")
            print("\n📋 Ejemplos de uso:")
            print("   python analizar_intelliai_final.py /ruta/a/IntelliAI")
            print("   python analizar_intelliai_final.py ./IntelliAI")
            print("   python analizar_intelliai_final.py /mnt/fuentes/IntelliAI")
        
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
    
    # Guardar informe principal
    output_file = "analisis_intelliai_detallado.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(informe)
    
    print(f"✅ Informe principal guardado en: {output_file}")
    print(f"📄 Tamaño: {len(informe)} caracteres")
    
    # Generar informe resumido
    informe_resumido = generar_informe_resumido_intelliai(resultados)
    output_resumido = "analisis_intelliai_resumen.md"
    with open(output_resumido, 'w', encoding='utf-8') as f:
        f.write(informe_resumido)
    
    print(f"✅ Informe resumido guardado en: {output_resumido}")
    
    # Mostrar resumen en consola
    mostrar_resumen_consola_intelliai(resultados)
    
    return resultados, informe

def generar_informe_resumido_intelliai(resultados):
    """Genera un informe resumido específico para IntelliAI"""
    
    informe = "# Análisis Resumido - Proyecto IntelliAI\n\n"
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
            for i, op in enumerate(oportunidades[:20], 1):
                informe += f"{i}. {op['oportunidad']}\n"
            if len(oportunidades) > 20:
                informe += f"... y {len(oportunidades) - 20} más\n"
            informe += "\n"
    
    # Dependencias
    if 'tecnico' in resultados and 'dependencias' in resultados['tecnico']:
        deps = resultados['tecnico']['dependencias']
        if deps.get('dependencias_detectadas'):
            informe += "### 📦 Dependencias Principales\n\n"
            for dep in deps['dependencias_detectadas'][:15]:
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
            lines = plan.split('\n')[:30]
            for line in lines:
                informe += f"{line}\n"
            if len(plan.split('\n')) > 30:
                informe += "...\n"
            informe += "\n"
    
    informe += "---\n"
    informe += "*Informe generado automáticamente por el Agente Analizador de Sistemas*\n"
    informe += "*Proyecto: IntelliAI*\n"
    
    return informe

def mostrar_resumen_consola_intelliai(resultados):
    """Muestra un resumen en la consola específico para IntelliAI"""
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DEL ANÁLISIS - INTELLIAI")
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
        for i, op in enumerate(oportunidades[:10], 1):
            print(f"     {i}. {op['oportunidad']}")
        if len(oportunidades) > 10:
            print(f"     ... y {len(oportunidades) - 10} más")
    
    print("\n" + "=" * 60)
    print("✅ ANÁLISIS COMPLETADO")
    print("📋 Archivos generados:")
    print("   • analisis_intelliai_detallado.md - Informe completo")
    print("   • analisis_intelliai_resumen.md - Informe resumido")

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description='Analizar el proyecto IntelliAI con el Agente Analizador',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python analizar_intelliai_final.py /home/pablo/win/source/repos/IntelliAI
  python analizar_intelliai_final.py ./IntelliAI
  python analizar_intelliai_final.py /mnt/fuentes/IntelliAI --ai

Si no sabes la ruta exacta, ejecuta sin argumentos para ver opciones disponibles.
        """
    )
    parser.add_argument('project_path', nargs='?', help='Ruta al proyecto IntelliAI')
    parser.add_argument('--ai', action='store_true', help='Usar análisis con IA (requiere OpenAI API key)')
    
    args = parser.parse_args()
    
    print("🚀 INICIANDO ANÁLISIS DEL PROYECTO INTELLIAI")
    print("=" * 60)
    
    # Si no se proporciona ruta, mostrar opciones
    if not args.project_path:
        print("❌ No se proporcionó ruta del proyecto")
        print("\n🔍 Verificando rutas posibles...")
        rutas_existentes = verificar_rutas_posibles()
        
        if rutas_existentes:
            print("✅ Proyectos encontrados:")
            for ruta in rutas_existentes:
                print(f"   • {ruta}")
            print(f"\n💡 Usa una de estas rutas:")
            print(f"   python analizar_intelliai_final.py '{rutas_existentes[0]}'")
        else:
            print("❌ No se encontró el proyecto IntelliAI en rutas comunes")
            print("\n💡 Posibles soluciones:")
            print("   1. Verifica que el proyecto existe")
            print("   2. Monta el proyecto en el devcontainer")
            print("   3. Proporciona la ruta correcta")
            print("\n📋 Ejemplos:")
            print("   python analizar_intelliai_final.py /ruta/a/IntelliAI")
            print("   python analizar_intelliai_final.py ./IntelliAI")
        
        return 1
    
    try:
        resultados, informe = analizar_intelliai_final(args.project_path, args.ai)
        
        if resultados:
            print("\n🎉 ¡Análisis completado exitosamente!")
            print("\n📋 Archivos generados:")
            print("   • analisis_intelliai_detallado.md - Informe completo")
            print("   • analisis_intelliai_resumen.md - Informe resumido")
            
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