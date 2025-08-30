#!/usr/bin/env python3
"""
Script de prueba para la indexación de GitHub.
Este script verifica que la funcionalidad de indexación funcione correctamente
sin necesidad de conexión real a GitHub o Milvus.
"""

import os
import sys
import asyncio
import logging
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Agregar el directorio app al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

# Importar desde el directorio padre
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from scripts.index_github import GitHubIndexer, GitHubItem, IndexingStats

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockGitHubRepo:
    """Mock del repositorio de GitHub para pruebas."""
    
    def __init__(self, full_name: str):
        self.full_name = full_name
    
    def get_pulls(self, state='all', sort='updated', direction='desc'):
        """Mock de get_pulls."""
        return [
            MockPullRequest(1, "Fix login bug", "Corregir error en autenticación", ["src/auth/login.py"]),
            MockPullRequest(2, "Add user validation", "Validación de usuarios mejorada", ["src/models/user.py"]),
            MockPullRequest(3, "Update dependencies", "Actualizar dependencias", ["requirements.txt"])
        ]
    
    def get_issues(self, state='all', sort='updated', direction='desc'):
        """Mock de get_issues."""
        return [
            MockIssue(1, "Bug report", "Error al cargar página principal"),
            MockIssue(2, "Feature request", "Agregar filtros de búsqueda"),
            MockIssue(3, "Documentation", "Mejorar README del proyecto")
        ]

class MockPullRequest:
    """Mock de un Pull Request."""
    
    def __init__(self, number: int, title: str, body: str, files: list):
        self.number = number
        self.title = title
        self.body = body
        self.files = files  # Agregar este atributo
        self.state = "open"
        self.user = MockUser("dev_user")
        self.labels = [MockLabel("bug"), MockLabel("frontend")]
        self.created_at = datetime(2025, 1, 1)
        self.updated_at = datetime(2025, 1, 15)
    
    def get_files(self):
        """Mock de get_files."""
        return [MockFile(filename) for filename in self.files]

class MockIssue:
    """Mock de un Issue."""
    
    def __init__(self, number: int, title: str, body: str):
        self.number = number
        self.title = title
        self.body = body
        self.state = "open"
        self.user = MockUser("user_reporter")
        self.labels = [MockLabel("enhancement")]
        self.created_at = datetime(2025, 1, 1)
        self.updated_at = datetime(2025, 1, 10)

class MockUser:
    """Mock de un usuario de GitHub."""
    
    def __init__(self, login: str):
        self.login = login

class MockLabel:
    """Mock de una etiqueta de GitHub."""
    
    def __init__(self, name: str):
        self.name = name

class MockFile:
    """Mock de un archivo de GitHub."""
    
    def __init__(self, filename: str):
        self.filename = filename

class MockMilvusStore:
    """Mock del almacén Milvus para pruebas."""
    
    def __init__(self):
        self.chunks = []
        self.add_calls = 0
    
    async def add_chunks(self, chunks):
        """Mock de add_chunks."""
        self.chunks.extend(chunks)
        self.add_calls += 1
        logger.info(f"Mock Milvus: {len(chunks)} chunks agregados")

async def test_github_indexer():
    """Prueba principal del indexador de GitHub."""
    logger.info("🧪 Iniciando pruebas del indexador de GitHub...")
    
    # Crear mocks
    mock_github = Mock()
    mock_repo = MockGitHubRepo("test-owner/test-repo")
    mock_milvus = MockMilvusStore()
    
    # Configurar mock de GitHub
    mock_github.get_repo.return_value = mock_repo
    mock_github.get_user.return_value = MockUser("test_user")
    
    # Crear indexador con mocks
    with patch('scripts.index_github.Github') as mock_github_class:
        mock_github_class.return_value = mock_github
        
        indexer = GitHubIndexer("fake_token", mock_milvus)
        
        # Probar indexación
        logger.info("📝 Probando indexación de repositorio...")
        stats = await indexer.index_repository(
            repo_name="test-owner/test-repo",
            item_type="both",
            limit=3
        )
        
        # Verificar resultados
        logger.info("🔍 Verificando resultados...")
        
        assert stats.total_items == 6, f"Esperado 6 items, obtenido {stats.total_items}"
        assert stats.prs_indexed == 3, f"Esperado 3 PRs, obtenido {stats.prs_indexed}"
        assert stats.issues_indexed == 3, f"Esperado 3 issues, obtenido {stats.issues_indexed}"
        assert stats.errors == 0, f"Esperado 0 errores, obtenido {stats.errors}"
        assert stats.success_rate == 1.0, f"Esperado 100% éxito, obtenido {stats.success_rate:.1%}"
        
        # Verificar que se llamó a Milvus
        assert mock_milvus.add_calls == 6, f"Esperado 6 llamadas a Milvus, obtenido {mock_milvus.add_calls}"
        assert len(mock_milvus.chunks) == 6, f"Esperado 6 chunks, obtenido {len(mock_milvus.chunks)}"
        
        logger.info("✅ Todas las pruebas pasaron exitosamente!")
        
        # Mostrar estadísticas
        print("\n" + "="*50)
        print("📊 ESTADÍSTICAS DE PRUEBA")
        print("="*50)
        print(f"Total items indexados: {stats.total_items}")
        print(f"PRs indexados: {stats.prs_indexed}")
        print(f"Issues indexados: {stats.issues_indexed}")
        print(f"Tasa de éxito: {stats.success_rate:.1%}")
        print(f"Duración: {stats.duration_seconds:.1f} segundos")
        print(f"Chunks en Milvus: {len(mock_milvus.chunks)}")
        print("="*50)
        
        return True

async def test_github_item_creation():
    """Prueba la creación de items de GitHub."""
    logger.info("🔧 Probando creación de items de GitHub...")
    
    # Crear item de PR
    pr_item = GitHubItem(
        id="pr:test/repo:123",
        type="pr",
        repo="test/repo",
        title="Test PR",
        body="Test body",
        files=["test.py"],
        author="test_user",
        labels=["bug"],
        created_at=1640995200,  # 2022-01-01
        updated_at=1640995200,
        state="open",
        number=123,
        raw_text="Test PR\n\nTest body\n\nArchivos: test.py"
    )
    
    assert pr_item.id == "pr:test/repo:123"
    assert pr_item.type == "pr"
    assert pr_item.title == "Test PR"
    assert len(pr_item.files) == 1
    assert pr_item.author == "test_user"
    
    logger.info("✅ Creación de items de GitHub exitosa!")
    return True

async def test_indexing_stats():
    """Prueba las estadísticas de indexación."""
    logger.info("📈 Probando estadísticas de indexación...")
    
    stats = IndexingStats()
    stats.total_items = 10
    stats.prs_indexed = 6
    stats.issues_indexed = 4
    stats.errors = 1
    stats.start_time = datetime(2025, 1, 1, 10, 0, 0)
    stats.end_time = datetime(2025, 1, 1, 10, 5, 0)
    
    assert stats.success_rate == 0.9, f"Esperado 90% éxito, obtenido {stats.success_rate:.1%}"
    assert stats.duration_seconds == 300, f"Esperado 300 segundos, obtenido {stats.duration_seconds}"
    
    logger.info("✅ Estadísticas de indexación exitosas!")
    return True

async def main():
    """Función principal de pruebas."""
    logger.info("🚀 Iniciando suite de pruebas del indexador de GitHub...")
    
    try:
        # Ejecutar todas las pruebas
        await test_github_item_creation()
        await test_indexing_stats()
        await test_github_indexer()
        
        logger.info("🎉 ¡Todas las pruebas pasaron exitosamente!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en las pruebas: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
