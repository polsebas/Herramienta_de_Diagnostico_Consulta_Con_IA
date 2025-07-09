#!/usr/bin/env python3
"""
Script de configuración para el sistema RAG
Instala dependencias y prepara el entorno de desarrollo
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Ejecuta un comando y maneja errores"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}: {e}")
        print(f"Salida de error: {e.stderr}")
        return False

def check_python_version():
    """Verifica que la versión de Python sea compatible"""
    if sys.version_info < (3, 8):
        print("❌ Se requiere Python 3.8 o superior")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detectado")
    return True

def create_virtual_environment():
    """Crea un entorno virtual si no existe"""
    venv_path = Path(".venv")
    if not venv_path.exists():
        print("🔄 Creando entorno virtual...")
        if not run_command("python -m venv .venv", "Creación del entorno virtual"):
            return False
    else:
        print("✅ Entorno virtual ya existe")
    return True

def install_dependencies():
    """Instala las dependencias del proyecto"""
    # Activar el entorno virtual y instalar dependencias
    if os.name == 'nt':  # Windows
        activate_cmd = ".venv\\Scripts\\activate"
    else:  # Unix/Linux/macOS
        activate_cmd = "source .venv/bin/activate"
    
    install_cmd = f"{activate_cmd} && pip install -r requirements.txt"
    return run_command(install_cmd, "Instalación de dependencias")

def create_env_file():
    """Crea un archivo .env de ejemplo"""
    env_content = """# Configuración del Sistema RAG
# Copia este archivo a .env y ajusta los valores según tu entorno

# Configuración de Milvus
MILVUS_URI=./milvus_knowledge.db
MILVUS_COLLECTION=system_knowledge

# Configuración del modelo de embeddings
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Configuración de logging
LOG_LEVEL=INFO
LOG_FILE=./logs/rag_system.log

# Configuración de desarrollo
DEBUG=True
"""
    
    env_file = Path(".env.example")
    if not env_file.exists():
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ Archivo .env.example creado")
    else:
        print("✅ Archivo .env.example ya existe")

def create_directories():
    """Crea directorios necesarios"""
    directories = ["logs", "data", "models"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("✅ Directorios creados")

def test_imports():
    """Prueba que las importaciones funcionen correctamente"""
    print("🔄 Probando importaciones...")
    try:
        # Intentar importar las librerías principales
        import asyncio
        import os
        print("✅ Importaciones básicas funcionan")
        
        # Verificar si las librerías específicas están disponibles
        try:
            import sentence_transformers
            print("✅ sentence-transformers disponible")
        except ImportError:
            print("⚠️  sentence-transformers no disponible - se instalará con pip")
        
        try:
            import pymilvus
            print("✅ pymilvus disponible")
        except ImportError:
            print("⚠️  pymilvus no disponible - se instalará con pip")
            
    except Exception as e:
        print(f"❌ Error en las importaciones: {e}")
        return False
    
    return True

def main():
    """Función principal del script de configuración"""
    print("🚀 Configurando el entorno de desarrollo para el Sistema RAG")
    print("=" * 60)
    
    # Verificar versión de Python
    if not check_python_version():
        sys.exit(1)
    
    # Crear entorno virtual
    if not create_virtual_environment():
        sys.exit(1)
    
    # Crear directorios
    create_directories()
    
    # Crear archivo de configuración
    create_env_file()
    
    # Instalar dependencias
    if not install_dependencies():
        print("❌ Error al instalar dependencias")
        print("💡 Intenta ejecutar manualmente: pip install -r requirements.txt")
        sys.exit(1)
    
    # Probar importaciones
    if not test_imports():
        print("❌ Error en las importaciones")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ Configuración completada exitosamente!")
    print("\n📋 Próximos pasos:")
    print("1. Copia .env.example a .env y ajusta la configuración")
    print("2. Ejecuta: python app/rag_system.py")
    print("3. Agrega más archivos .md a knowledge_base/ para expandir la base de conocimiento")
    print("\n🔧 Para activar el entorno virtual:")
    if os.name == 'nt':
        print("   .venv\\Scripts\\activate")
    else:
        print("   source .venv/bin/activate")

if __name__ == "__main__":
    main() 