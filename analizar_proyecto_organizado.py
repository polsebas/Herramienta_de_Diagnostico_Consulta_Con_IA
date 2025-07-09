#!/usr/bin/env python3
"""
Script organizado para analizar proyectos
Genera reportes en carpetas autonumeradas y mantiene todo ordenado
"""

import os
import sys
import argparse
import shutil
from datetime import datetime
from pathlib import Path
from app.agente_analizador import AgenteAnalizador, generate_report

class OrganizadorReportes:
    """Clase para organizar reportes de análisis"""
    
    def __init__(self):
        self.base_dir = Path("reportes_analisis")
        self.base_dir.mkdir(exist_ok=True)
        
    def crear_carpeta_analisis(self, nombre_proyecto: str) -> Path:
        """Crea una carpeta autonumerada para el análisis"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_limpio = nombre_proyecto.replace("/", "_").replace("\\", "_").replace(" ", "_")
        
        # Buscar el siguiente número disponible
        contador = 1
        while True:
            carpeta = self.base_dir / f"{contador:03d}_{nombre_limpio}_{timestamp}"
            if not carpeta.exists():
                break
            contador += 1
        
        carpeta.mkdir(parents=True, exist_ok=True)
        return carpeta
    
    def limpiar_archivos_antiguos(self, max_archivos: int = 10):
        """Limpia archivos antiguos manteniendo solo los más recientes"""
        if not self.base_dir.exists():
            return
            
        carpetas = sorted([d for d in self.base_dir.iterdir() if d.is_dir()], 
                         key=lambda x: x.stat().st_mtime, reverse=True)
        
        if len(carpetas) > max_archivos:
            for carpeta in carpetas[max_archivos:]:
                shutil.rmtree(carpeta)
                print(f"🗑️  Eliminada carpeta antigua: {carpeta.name}")
    
    def mover_archivos_antiguos(self):
        """Mueve archivos de análisis antiguos a la carpeta de reportes"""
        archivos_antiguos = [
            "analisis_*.md",
            "test_*.md", 
            "informe_*.md",
            "ejemplo_*.md",
            "demo_*.md"
        ]
        
        for patron in archivos_antiguos:
            for archivo in Path(".").glob(patron):
                if archivo.is_file():
                    # Crear carpeta para archivos antiguos si no existe
                    carpeta_antiguos = self.base_dir / "archivos_antiguos"
                    carpeta_antiguos.mkdir(exist_ok=True)
                    
                    # Mover archivo
                    destino = carpeta_antiguos / archivo.name
                    shutil.move(str(archivo), str(destino))
                    print(f"📁 Movido: {archivo.name} → archivos_antiguos/")

def analizar_proyecto_organizado(project_path: str, use_ai: bool = False, limpiar: bool = True):
    """Analiza un proyecto y organiza los reportes"""
    
    print("🔍 ANALIZANDO PROYECTO (MODO ORGANIZADO)")
    print("=" * 60)
    print(f"📁 Ruta del proyecto: {project_path}")
    
    # Inicializar organizador
    organizador = OrganizadorReportes()
    
    # Limpiar archivos antiguos si se solicita
    if limpiar:
        print("\n🧹 Limpiando archivos antiguos...")
        organizador.limpiar_archivos_antiguos()
        organizador.mover_archivos_antiguos()
    
    # Verificar que el proyecto existe
    if not Path(project_path).exists():
        print(f"❌ Error: El proyecto {project_path} no existe")
        print("   Verifica la ruta del proyecto")
        return None, None, None
    
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
    
    # Obtener nombre del proyecto para la carpeta
    project_name = Path(project_path).name
    if not project_name:
        project_name = "proyecto"
    
    # Crear carpeta organizada
    carpeta_analisis = organizador.crear_carpeta_analisis(project_name)
    print(f"📁 Carpeta creada: {carpeta_analisis.name}")
    
    # Guardar informe principal
    output_file = carpeta_analisis / "analisis_detallado.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(informe)
    
    print(f"✅ Informe principal guardado en: {output_file}")
    print(f"📄 Tamaño: {len(informe)} caracteres")
    
    # Generar informe resumido
    informe_resumido = generar_informe_resumido_organizado(resultados, project_name)
    output_resumido = carpeta_analisis / "analisis_resumen.md"
    with open(output_resumido, 'w', encoding='utf-8') as f:
        f.write(informe_resumido)
    
    print(f"✅ Informe resumido guardado en: {output_resumido}")
    
    # Generar archivo de metadatos
    generar_metadatos(carpeta_analisis, project_path, resultados, use_ai)
    
    # Generar índice de reportes
    generar_indice_reportes(organizador.base_dir)
    
    # Mostrar resumen en consola
    mostrar_resumen_consola_organizado(resultados, project_name, carpeta_analisis)
    
    return resultados, informe, carpeta_analisis

def generar_informe_resumido_organizado(resultados, project_name: str):
    """Genera un informe resumido organizado"""
    
    informe = f"# Análisis Resumido - Proyecto {project_name}\n\n"
    informe += f"**Fecha de análisis**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
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
    informe += f"*Proyecto: {project_name}*\n"
    
    return informe

def generar_metadatos(carpeta: Path, project_path: str, resultados: dict, use_ai: bool):
    """Genera archivo de metadatos del análisis"""
    
    metadatos = f"""# Metadatos del Análisis

## Información del Proyecto
- **Ruta del proyecto**: {project_path}
- **Nombre del proyecto**: {Path(project_path).name}
- **Fecha de análisis**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Análisis con IA**: {'Sí' if use_ai else 'No'}

## Métricas del Análisis
"""
    
    if 'tecnico' in resultados and 'codigo' in resultados['tecnico']:
        codigo = resultados['tecnico']['codigo']
        metadatos += f"- **Archivos analizados**: {codigo.get('archivos_analizados', 0)}\n"
        metadatos += f"- **Funciones totales**: {codigo.get('metricas', {}).get('total_funciones', 0)}\n"
        metadatos += f"- **Clases totales**: {codigo.get('metricas', {}).get('total_clases', 0)}\n"
        metadatos += f"- **Problemas detectados**: {len(codigo.get('problemas_detectados', []))}\n"
    
    if 'tecnico' in resultados and 'oportunidades_ia' in resultados['tecnico']:
        oportunidades = resultados['tecnico']['oportunidades_ia']
        metadatos += f"- **Oportunidades de IA**: {len(oportunidades)}\n"
    
    metadatos += f"""
## Archivos Generados
- `analisis_detallado.md` - Informe completo del análisis
- `analisis_resumen.md` - Informe resumido
- `metadatos.md` - Este archivo

## Configuración
- **OpenAI API**: {'Configurado' if use_ai and os.getenv('OPENAI_API_KEY') else 'No configurado'}
- **Modo de análisis**: {'Avanzado con IA' if use_ai else 'Básico'}
"""
    
    with open(carpeta / "metadatos.md", 'w', encoding='utf-8') as f:
        f.write(metadatos)

def generar_indice_reportes(base_dir: Path):
    """Genera un índice de todos los reportes"""
    
    indice = "# 📋 Índice de Reportes de Análisis\n\n"
    indice += f"**Última actualización**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    carpetas = sorted([d for d in base_dir.iterdir() if d.is_dir()], 
                     key=lambda x: x.stat().st_mtime, reverse=True)
    
    if not carpetas:
        indice += "No hay reportes disponibles.\n"
    else:
        indice += "## 📁 Reportes Disponibles\n\n"
        
        for carpeta in carpetas:
            if carpeta.name == "archivos_antiguos":
                continue
                
            fecha = datetime.fromtimestamp(carpeta.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
            indice += f"### 📂 {carpeta.name}\n"
            indice += f"- **Fecha**: {fecha}\n"
            indice += f"- **Ruta**: `{carpeta}`\n"
            
            # Verificar archivos disponibles
            archivos = list(carpeta.glob("*.md"))
            if archivos:
                indice += "- **Archivos**:\n"
                for archivo in archivos:
                    indice += f"  - `{archivo.name}`\n"
            
            indice += "\n"
    
    with open(base_dir / "INDICE_REPORTES.md", 'w', encoding='utf-8') as f:
        f.write(indice)

def mostrar_resumen_consola_organizado(resultados, project_name: str, carpeta: Path):
    """Muestra un resumen en la consola organizado"""
    
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
    print(f"   📁 Carpeta: {carpeta.name}")
    print(f"   📄 analisis_detallado.md - Informe completo")
    print(f"   📄 analisis_resumen.md - Informe resumido")
    print(f"   📄 metadatos.md - Metadatos del análisis")
    print(f"   📋 INDICE_REPORTES.md - Índice de todos los reportes")

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description='Analizar proyecto con reportes organizados',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python analizar_proyecto_organizado.py /mnt/fuentes
  python analizar_proyecto_organizado.py ./MiProyecto
  python analizar_proyecto_organizado.py /ruta/a/proyecto --ai
  python analizar_proyecto_organizado.py /ruta/a/proyecto --no-limpiar
        """
    )
    parser.add_argument('project_path', help='Ruta al proyecto a analizar')
    parser.add_argument('--ai', action='store_true', help='Usar análisis con IA (requiere OpenAI API key)')
    parser.add_argument('--no-limpiar', action='store_true', help='No limpiar archivos antiguos')
    
    args = parser.parse_args()
    
    print("🚀 INICIANDO ANÁLISIS ORGANIZADO")
    print("=" * 60)
    
    try:
        resultados, informe, carpeta = analizar_proyecto_organizado(
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
            
        else:
            print("❌ Error en el análisis")
            return 1
            
    except Exception as e:
        print(f"\n❌ Error durante el análisis: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 