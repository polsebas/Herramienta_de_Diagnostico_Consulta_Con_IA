#!/usr/bin/env python3
"""
Script para limpiar archivos antiguos del directorio raíz
Mueve archivos de análisis, test, demo, etc. a la carpeta organizada
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

def limpiar_archivos_antiguos():
    """Limpia archivos antiguos del directorio raíz"""
    
    print("🧹 LIMPIANDO ARCHIVOS ANTIGUOS")
    print("=" * 40)
    
    # Patrones de archivos a mover
    patrones = [
        "analisis_*.md",
        "test_*.md",
        "informe_*.md",
        "ejemplo_*.md",
        "demo_*.md",
        "test_*.db",
        "test_*.py",
        "demo_*.py",
        "ejemplo_*.py"
    ]
    
    # Crear carpeta de reportes si no existe
    reportes_dir = Path("reportes_analisis")
    reportes_dir.mkdir(exist_ok=True)
    
    # Crear carpeta de archivos antiguos
    archivos_antiguos = reportes_dir / "archivos_antiguos"
    archivos_antiguos.mkdir(exist_ok=True)
    
    archivos_movidos = []
    
    # Buscar y mover archivos
    for patron in patrones:
        for archivo in Path(".").glob(patron):
            if archivo.is_file():
                try:
                    # Mover archivo
                    destino = archivos_antiguos / archivo.name
                    shutil.move(str(archivo), str(destino))
                    archivos_movidos.append(archivo.name)
                    print(f"📁 Movido: {archivo.name}")
                except Exception as e:
                    print(f"❌ Error moviendo {archivo.name}: {e}")
    
    if archivos_movidos:
        print(f"\n✅ Se movieron {len(archivos_movidos)} archivos a archivos_antiguos/")
        print("📁 Archivos movidos:")
        for archivo in archivos_movidos:
            print(f"   • {archivo}")
    else:
        print("\n✅ No se encontraron archivos para mover")
    
    # Mostrar estado final
    print(f"\n📋 Estado final:")
    print(f"   📁 Carpeta de reportes: {reportes_dir}")
    print(f"   🗂️  Archivos antiguos: {len(list(archivos_antiguos.glob('*')))} archivos")
    
    # Verificar si hay archivos de análisis en el directorio raíz
    archivos_restantes = []
    for patron in ["analisis_*.md", "test_*.md", "informe_*.md"]:
        archivos_restantes.extend(Path(".").glob(patron))
    
    if archivos_restantes:
        print(f"\n⚠️  Archivos restantes en directorio raíz:")
        for archivo in archivos_restantes:
            print(f"   • {archivo.name}")
        print("\n💡 Para mover estos archivos manualmente:")
        print("   python limpiar_archivos_antiguos.py")
    else:
        print("\n✅ Directorio raíz limpio")
    
    return len(archivos_movidos)

def mostrar_estado_limpieza():
    """Muestra el estado actual de limpieza"""
    
    print("📋 ESTADO DE LIMPIEZA")
    print("=" * 30)
    
    # Verificar archivos en directorio raíz
    patrones = ["analisis_*.md", "test_*.md", "informe_*.md", "ejemplo_*.md", "demo_*.md"]
    archivos_raiz = []
    
    for patron in patrones:
        archivos_raiz.extend(Path(".").glob(patron))
    
    if archivos_raiz:
        print(f"📄 Archivos en directorio raíz: {len(archivos_raiz)}")
        for archivo in archivos_raiz:
            print(f"   • {archivo.name}")
    else:
        print("✅ Directorio raíz limpio")
    
    # Verificar carpeta de archivos antiguos
    archivos_antiguos = Path("reportes_analisis/archivos_antiguos")
    if archivos_antiguos.exists():
        archivos = list(archivos_antiguos.glob("*"))
        print(f"\n🗂️  Archivos antiguos: {len(archivos)} archivos")
        if archivos:
            print("   Ubicación: reportes_analisis/archivos_antiguos/")
    
    # Verificar carpetas de análisis
    reportes_dir = Path("reportes_analisis")
    if reportes_dir.exists():
        carpetas = [d for d in reportes_dir.iterdir() if d.is_dir() and d.name != "archivos_antiguos"]
        if carpetas:
            print(f"\n📁 Carpetas de análisis: {len(carpetas)} carpetas")
            for carpeta in sorted(carpetas, key=lambda x: x.stat().st_mtime, reverse=True):
                fecha = datetime.fromtimestamp(carpeta.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
                print(f"   • {carpeta.name} ({fecha})")

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Limpiar archivos antiguos del directorio raíz',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python limpiar_archivos_antiguos.py
  python limpiar_archivos_antiguos.py --estado
        """
    )
    parser.add_argument('--estado', action='store_true', help='Mostrar estado de limpieza sin mover archivos')
    
    args = parser.parse_args()
    
    if args.estado:
        mostrar_estado_limpieza()
    else:
        archivos_movidos = limpiar_archivos_antiguos()
        
        if archivos_movidos > 0:
            print(f"\n🎉 ¡Limpieza completada! Se movieron {archivos_movidos} archivos.")
            print("\n📋 Para ver el estado:")
            print("   python limpiar_archivos_antiguos.py --estado")
        else:
            print("\n✅ No se encontraron archivos para limpiar")

if __name__ == "__main__":
    main() 