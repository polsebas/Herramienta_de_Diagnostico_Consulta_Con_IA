#!/usr/bin/env python3
"""
Script de indexación de GitHub para el proyecto Next Level.
Indexa PRs e issues en Milvus para RAG y análisis de contexto.

Este script implementa el PR-A del plan de implementación:
- Conecta con GitHub API
- Indexa metadata de PRs e issues
- Almacena en Milvus con embeddings
- Proporciona métricas de indexación

Uso:
    python scripts/index_github.py --repo owner/repo --limit 50
    python scripts/index_github.py --repo owner/repo --type prs --since 2025-01-01
"""

import os
import sys
import asyncio
import argparse
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, asdict
import json
import uuid

# Agregar el directorio app al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

try:
    from github import Github, GithubException
    from app.retrieval.milvus_store import MilvusVectorStore, ChunkData
    from app.spec_layer import build_task_contract
except ImportError as e:
    print(f"Error de importación: {e}")
    print("Asegúrate de tener las dependencias instaladas:")
    print("pip install PyGithub pymilvus")
    sys.exit(1)

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class GitHubItem:
    """Representa un item de GitHub (PR o Issue)."""
    id: str
    type: str  # 'pr' o 'issue'
    repo: str
    title: str
    body: str
    files: List[str]
    author: str
    labels: List[str]
    created_at: int
    updated_at: int
    state: str
    number: int
    raw_text: str
    embedding: Optional[List[float]] = None

@dataclass
class IndexingStats:
    """Estadísticas de indexación."""
    total_items: int = 0
    prs_indexed: int = 0
    issues_indexed: int = 0
    errors: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    @property
    def success_rate(self) -> float:
        """Calcula la tasa de éxito de indexación."""
        if self.total_items == 0:
            return 0.0
        return (self.total_items - self.errors) / self.total_items
    
    @property
    def duration_seconds(self) -> float:
        """Calcula la duración total en segundos."""
        if not self.start_time or not self.end_time:
            return 0.0
        return (self.end_time - self.start_time).total_seconds()

class GitHubIndexer:
    """Indexador de GitHub para PRs e issues."""
    
    def __init__(self, github_token: str, milvus_store: MilvusVectorStore):
        """
        Inicializa el indexador.
        
        Args:
            github_token: Token de GitHub API
            milvus_store: Instancia de MilvusVectorStore
        """
        self.github = Github(github_token)
        self.milvus_store = milvus_store
        self.stats = IndexingStats()
        
        # Verificar conexión a GitHub
        try:
            user = self.github.get_user()
            logger.info(f"Conectado a GitHub como: {user.login}")
        except GithubException as e:
            logger.error(f"Error conectando a GitHub: {e}")
            raise
    
    async def index_repository(self, repo_name: str, 
                             item_type: str = "both",
                             limit: int = 50,
                             since_date: Optional[str] = None) -> IndexingStats:
        """
        Indexa un repositorio completo.
        
        Args:
            repo_name: Nombre del repositorio (owner/repo)
            item_type: Tipo de items a indexar ('prs', 'issues', 'both')
            limit: Límite de items por tipo
            since_date: Fecha desde la cual indexar (YYYY-MM-DD)
        
        Returns:
            Estadísticas de indexación
        """
        logger.info(f"Iniciando indexación de {repo_name}")
        self.stats = IndexingStats(start_time=datetime.now())
        
        try:
            repo = self.github.get_repo(repo_name)
            logger.info(f"Repositorio encontrado: {repo.full_name}")
            
            # Indexar según el tipo especificado
            if item_type in ["both", "prs"]:
                await self._index_pull_requests(repo, limit, since_date)
            
            if item_type in ["both", "issues"]:
                await self._index_issues(repo, limit, since_date)
            
            self.stats.end_time = datetime.now()
            logger.info(f"Indexación completada: {self.stats}")
            
            return self.stats
            
        except GithubException as e:
            logger.error(f"Error accediendo al repositorio {repo_name}: {e}")
            self.stats.errors += 1
            return self.stats
    
    async def _index_pull_requests(self, repo, limit: int, since_date: Optional[str] = None):
        """Indexa pull requests del repositorio."""
        logger.info(f"Indexando PRs de {repo.full_name}")
        
        try:
            # Obtener PRs con filtros
            prs = repo.get_pulls(state='all', sort='updated', direction='desc')
            
            if since_date:
                since = datetime.strptime(since_date, '%Y-%m-%d')
                prs = [pr for pr in prs if pr.updated_at >= since]
            
            prs = list(prs)[:limit]
            
            for pr in prs:
                try:
                    await self._index_pr(pr, repo)
                    self.stats.prs_indexed += 1
                    self.stats.total_items += 1
                except Exception as e:
                    logger.error(f"Error indexando PR #{pr.number}: {e}")
                    self.stats.errors += 1
                    
        except Exception as e:
            logger.error(f"Error obteniendo PRs: {e}")
            self.stats.errors += 1
    
    async def _index_issues(self, repo, limit: int, since_date: Optional[str] = None):
        """Indexa issues del repositorio."""
        logger.info(f"Indexando issues de {repo.full_name}")
        
        try:
            # Obtener issues con filtros
            issues = repo.get_issues(state='all', sort='updated', direction='desc')
            
            if since_date:
                since = datetime.strptime(since_date, '%Y-%m-%d')
                issues = [issue for issue in issues if issue.updated_at >= since]
            
            issues = list(issues)[:limit]
            
            for issue in issues:
                try:
                    await self._index_issue(issue, repo)
                    self.stats.issues_indexed += 1
                    self.stats.total_items += 1
                except Exception as e:
                    logger.error(f"Error indexando issue #{issue.number}: {e}")
                    self.stats.errors += 1
                    
        except Exception as e:
            logger.error(f"Error obteniendo issues: {e}")
            self.stats.errors += 1
    
    async def _index_pr(self, pr, repo) -> None:
        """Indexa un pull request específico."""
        try:
            # Obtener archivos modificados
            pr_files = [f.filename for f in pr.get_files()]
            
            # Obtener labels
            labels = [label.name for label in pr.labels]
            
            # Crear texto raw para embedding
            raw_text = f"{pr.title}\n\n{pr.body or ''}\n\nArchivos: {', '.join(pr_files)}"
            
            # Crear item de GitHub
            item = GitHubItem(
                id=f"pr:{repo.full_name}:{pr.number}",
                type="pr",
                repo=repo.full_name,
                title=pr.title,
                body=pr.body or "",
                files=pr_files,
                author=pr.user.login if pr.user else "unknown",
                labels=labels,
                created_at=int(pr.created_at.timestamp()),
                updated_at=int(pr.updated_at.timestamp()),
                state=pr.state,
                number=pr.number,
                raw_text=raw_text
            )
            
            # Generar embedding (simulado por ahora)
            item.embedding = self._generate_embedding(raw_text)
            
            # Indexar en Milvus
            await self._store_in_milvus(item)
            
            logger.debug(f"PR #{pr.number} indexado: {pr.title[:50]}...")
            
        except Exception as e:
            logger.error(f"Error procesando PR #{pr.number}: {e}")
            raise
    
    async def _index_issue(self, issue, repo) -> None:
        """Indexa un issue específico."""
        try:
            # Obtener labels
            labels = [label.name for label in issue.labels]
            
            # Crear texto raw para embedding
            raw_text = f"{issue.title}\n\n{issue.body or ''}"
            
            # Crear item de GitHub
            item = GitHubItem(
                id=f"issue:{repo.full_name}:{issue.number}",
                type="issue",
                repo=repo.full_name,
                title=issue.title,
                body=issue.body or "",
                files=[],  # Issues no tienen archivos
                author=issue.user.login if issue.user else "unknown",
                labels=labels,
                created_at=int(issue.created_at.timestamp()),
                updated_at=int(issue.updated_at.timestamp()),
                state=issue.state,
                number=issue.number,
                raw_text=raw_text
            )
            
            # Generar embedding (simulado por ahora)
            item.embedding = self._generate_embedding(raw_text)
            
            # Indexar en Milvus
            await self._store_in_milvus(item)
            
            logger.debug(f"Issue #{issue.number} indexado: {issue.title[:50]}...")
            
        except Exception as e:
            logger.error(f"Error procesando issue #{issue.number}: {e}")
            raise
    
    def _generate_embedding(self, text: str) -> List[float]:
        """
        Genera embedding para el texto.
        
        Por ahora simula embeddings de 384 dimensiones.
        En producción, usar un modelo real como sentence-transformers.
        """
        # Simulación de embedding (reemplazar con modelo real)
        import random
        random.seed(hash(text) % 2**32)
        return [random.uniform(-1, 1) for _ in range(384)]
    
    async def _store_in_milvus(self, item: GitHubItem) -> None:
        """Almacena el item en Milvus."""
        try:
            # Convertir a ChunkData
            chunk_data = ChunkData(
                id=item.id,
                doc_id=item.id,
                title=item.title,
                section=f"{item.type.upper()} #{item.number}",
                path=f"github://{item.repo}",
                line_start=0,
                line_end=0,
                text=item.raw_text,
                embedding=item.embedding,
                doc_type=f"github_{item.type}",
                version="1.0",
                created_at=item.created_at,
                updated_at=item.updated_at,
                tags=item.labels,
                metadata={
                    "github_type": item.type,
                    "repo": item.repo,
                    "number": item.number,
                    "author": item.author,
                    "state": item.state,
                    "files": item.files,
                    "labels": item.labels
                }
            )
            
            # Insertar en Milvus
            await self.milvus_store.add_chunks([chunk_data])
            
        except Exception as e:
            logger.error(f"Error almacenando en Milvus: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas de indexación en formato dict."""
        return asdict(self.stats)

async def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(description="Indexar PRs e issues de GitHub en Milvus")
    parser.add_argument("--repo", required=True, help="Repositorio (owner/repo)")
    parser.add_argument("--type", choices=["prs", "issues", "both"], default="both", 
                       help="Tipo de items a indexar")
    parser.add_argument("--limit", type=int, default=50, help="Límite de items por tipo")
    parser.add_argument("--since", help="Fecha desde la cual indexar (YYYY-MM-DD)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Logging verbose")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Verificar variables de entorno
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        logger.error("GITHUB_TOKEN no está configurado")
        sys.exit(1)
    
    milvus_uri = os.getenv("MILVUS_URI", "localhost:19530")
    milvus_collection = os.getenv("MILVUS_COLLECTION", "github_items")
    
    try:
        # Inicializar Milvus (modo simulado si no está disponible)
        from app.retrieval.milvus_store import MilvusVectorStore
        milvus_store = MilvusVectorStore(
            uri=milvus_uri,
            collection_name=milvus_collection
        )
        
        # Inicializar indexador
        indexer = GitHubIndexer(github_token, milvus_store)
        
        # Ejecutar indexación
        stats = await indexer.index_repository(
            repo_name=args.repo,
            item_type=args.type,
            limit=args.limit,
            since_date=args.since
        )
        
        # Mostrar resultados
        print("\n" + "="*60)
        print("📊 RESULTADOS DE INDEXACIÓN")
        print("="*60)
        print(f"Repositorio: {args.repo}")
        print(f"Tipo: {args.type}")
        print(f"Total items: {stats.total_items}")
        print(f"PRs indexados: {stats.prs_indexed}")
        print(f"Issues indexados: {stats.issues_indexed}")
        print(f"Errores: {stats.errors}")
        print(f"Tasa de éxito: {stats.success_rate:.1%}")
        print(f"Duración: {stats.duration_seconds:.1f} segundos")
        
        if stats.success_rate >= 0.95:
            print("✅ Indexación exitosa (≥95% éxito)")
        elif stats.success_rate >= 0.8:
            print("⚠️  Indexación parcial (80-95% éxito)")
        else:
            print("❌ Indexación problemática (<80% éxito)")
        
        print("="*60)
        
    except Exception as e:
        logger.error(f"Error en indexación: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
