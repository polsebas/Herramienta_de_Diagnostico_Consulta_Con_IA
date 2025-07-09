#!/usr/bin/env python3
"""
Script organizado específico para analizar el proyecto IntelliAI
Usa la nueva organización de reportes en carpetas autonumeradas
"""

import os
import sys
import argparse
from pathlib import Path
from analizar_proyecto_organizado import analizar_proyecto_organizado, OrganizadorReportes

def verificar_rutas_posibles():
    """Verifica rutas posibles donde podría estar el proyecto IntelliAI"""
    rutas_posibles = [
        "/home/pablo/win/source/repos/IntelliAI",
        "/mnt/c/Users/pablo/source/repos/IntelliAI",
        "/mnt/d/Projects/IntelliAI",
        "/workspaces/IntelliAI",
        "/app/IntelliAI",
        "./IntelliAI",
        "../IntelliAI",
        "/mnt/fuentes/IntelliAI"
    ]
    
    rutas_existentes = []
    for ruta in rutas_posibles:
        if Path(ruta).exists():
            rutas_existentes.append(ruta)
    
    return rutas_existentes

def analizar_intelliai_organizado(project_path: str, use_ai: bool = False, limpiar: bool = True):
    """Analiza específicamente el proyecto IntelliAI con organización"""
    
    print("🔍 ANALIZANDO PROYECTO INTELLIAI (MODO ORGANIZADO)")
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
            print(f"   python analizar_intelliai_organizado.py '{rutas_existentes[0]}'")
        else:
            print("\n💡 Posibles soluciones:")
            print("   1. Verifica que el proyecto IntelliAI existe")
            print("   2. Monta el proyecto en el devcontainer")
            print("   3. Proporciona la ruta correcta")
            print("\n📋 Ejemplos de uso:")
            print("   python analizar_intelliai_organizado.py /ruta/a/IntelliAI")
            print("   python analizar_intelliai_organizado.py ./IntelliAI")
            print("   python analizar_intelliai_organizado.py /mnt/fuentes/IntelliAI")
        
        return None, None, None
    
    # Usar la función del script organizado
    return analizar_proyecto_organizado(project_path, use_ai, limpiar)

def mostrar_estado_reportes():
    """Muestra el estado actual de los reportes"""
    organizador = OrganizadorReportes()
    
    if not organizador.base_dir.exists():
        print("📋 No hay reportes disponibles.")
        return
    
    print("\n📋 ESTADO ACTUAL DE REPORTES")
    print("=" * 40)
    
    # Mostrar carpeta de archivos antiguos
    carpeta_antiguos = organizador.base_dir / "archivos_antiguos"
    if carpeta_antiguos.exists():
        archivos_antiguos = list(carpeta_antiguos.glob("*.md"))
        print(f"🗂️  Archivos antiguos: {len(archivos_antiguos)} archivos")
    
    # Mostrar carpetas de análisis
    carpetas_analisis = [d for d in organizador.base_dir.iterdir() 
                         if d.is_dir() and d.name != "archivos_antiguos"]
    
    if carpetas_analisis:
        print(f"📁 Carpetas de análisis: {len(carpetas_analisis)} carpetas")
        for carpeta in sorted(carpetas_analisis, key=lambda x: x.stat().st_mtime, reverse=True):
            fecha = carpeta.stat().st_mtime
            from datetime import datetime
            fecha_str = datetime.fromtimestamp(fecha).strftime('%Y-%m-%d %H:%M')
            print(f"   • {carpeta.name} ({fecha_str})")
    else:
        print("📁 No hay carpetas de análisis")
    
    # Mostrar índice si existe
    indice = organizador.base_dir / "INDICE_REPORTES.md"
    if indice.exists():
        print(f"📋 Índice disponible: {indice}")

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description='Analizar el proyecto IntelliAI con reportes organizados',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python analizar_intelliai_organizado.py /home/pablo/win/source/repos/IntelliAI
  python analizar_intelliai_organizado.py ./IntelliAI
  python analizar_intelliai_organizado.py /mnt/fuentes/IntelliAI --ai
  python analizar_intelliai_organizado.py --estado

Si no sabes la ruta exacta, ejecuta sin argumentos para ver opciones disponibles.
        """
    )
    parser.add_argument('project_path', nargs='?', help='Ruta al proyecto IntelliAI')
    parser.add_argument('--ai', action='store_true', help='Usar análisis con IA (requiere OpenAI API key)')
    parser.add_argument('--no-limpiar', action='store_true', help='No limpiar archivos antiguos')
    parser.add_argument('--estado', action='store_true', help='Mostrar estado actual de reportes')
    
    args = parser.parse_args()
    
    # Si se solicita mostrar estado
    if args.estado:
        mostrar_estado_reportes()
        return 0
    
    print("🚀 INICIANDO ANÁLISIS ORGANIZADO DEL PROYECTO INTELLIAI")
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
            print(f"   python analizar_intelliai_organizado.py '{rutas_existentes[0]}'")
        else:
            print("❌ No se encontró el proyecto IntelliAI en rutas comunes")
            print("\n💡 Posibles soluciones:")
            print("   1. Verifica que el proyecto existe")
            print("   2. Monta el proyecto en el devcontainer")
            print("   3. Proporciona la ruta correcta")
            print("\n📋 Ejemplos:")
            print("   python analizar_intelliai_organizado.py /ruta/a/IntelliAI")
            print("   python analizar_intelliai_organizado.py ./IntelliAI")
            print("\n📊 Para ver el estado de reportes:")
            print("   python analizar_intelliai_organizado.py --estado")
        
        return 1
    
    try:
        resultados, informe, carpeta = analizar_intelliai_organizado(
            args.project_path, 
            args.ai, 
            not args.no_limpiar
        )
        
        if resultados:
            print("\n🎉 ¡Análisis completado exitosamente!")
            print(f"\n📁 Reportes organizados en: {carpeta}")
            print("\n📋 Archivos generados:")
            print("   • analisis_detallado.md - Informe completo")
            print("   • analisis_resumen.md - Informe resumido")
            print("   • metadatos.md - Metadatos del análisis")
            print("   • INDICE_REPORTES.md - Índice de todos los reportes")
            
            print("\n🎯 Próximos pasos:")
            print("   1. Revisar los informes en la carpeta generada")
            print("   2. Analizar las oportunidades de IA detectadas")
            print("   3. Considerar las recomendaciones de modernización")
            
            print("\n📊 Para ver el estado de todos los reportes:")
            print("   python analizar_intelliai_organizado.py --estado")
            
        else:
            print("❌ Error en el análisis")
            return 1
            
    except Exception as e:
        print(f"\n❌ Error durante el análisis: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 