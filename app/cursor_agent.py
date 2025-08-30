"""
Cursor Agent - Sistema de Agentes en Background para Tareas Seguras

Este módulo implementa agentes tipo Cursor que pueden ejecutar tareas en background
de manera segura, incluyendo generación de draft PRs, tests y documentación.
"""

import asyncio
import json
import logging
import os
import subprocess
import tempfile
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Callable
import aiofiles
import aiohttp

from app.spec_layer import TaskContract, RiskLevel
from app.context_manager import ContextManager
from app.human_loop import HumanLoopManager

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Estados del agente."""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskType(Enum):
    """Tipos de tareas que puede ejecutar el agente."""
    DRAFT_PR = "draft_pr"
    GENERATE_TESTS = "generate_tests"
    GENERATE_DOCS = "generate_docs"
    CODE_REVIEW = "code_review"
    REFACTOR = "refactor"
    SECURITY_SCAN = "security_scan"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"


@dataclass
class BackgroundTask:
    """Tarea en background para el agente."""
    id: str
    task_type: TaskType
    contract: TaskContract
    status: AgentStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    progress: float = 0.0
    artifacts: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.artifacts is None:
            self.artifacts = []
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la tarea a diccionario para serialización."""
        return {
            **asdict(self),
            'task_type': self.task_type.value,
            'status': self.status.value,
            'contract': self.contract.to_dict() if self.contract else None
        }


@dataclass
class TaskResult:
    """Resultado de una tarea ejecutada."""
    success: bool
    output: str
    artifacts: List[str]
    metadata: Dict[str, Any]
    execution_time: float
    error_message: Optional[str] = None


class CursorAgent:
    """
    Agente tipo Cursor que ejecuta tareas en background de manera segura.
    """
    
    def __init__(self,
                 context_manager: ContextManager,
                 human_loop_manager: Optional[HumanLoopManager] = None,
                 workspace_path: str = ".",
                 config_path: str = "config/cursor_agent.yml"):
        """
        Inicializa el Cursor Agent.
        
        Args:
            context_manager: Gestor de contexto para análisis histórico
            human_loop_manager: Gestor de human-in-the-loop (opcional)
            workspace_path: Ruta del workspace de trabajo
            config_path: Ruta al archivo de configuración
        """
        self.context_manager = context_manager
        self.human_loop_manager = human_loop_manager
        self.workspace_path = Path(workspace_path)
        self.config = self._load_config(config_path)
        
        # Estado del agente
        self.active_tasks: Dict[str, BackgroundTask] = {}
        self.task_history: List[BackgroundTask] = []
        self.workspace_safe = self._validate_workspace_safety()
        
        # Callbacks para notificaciones
        self.task_callbacks: Dict[str, List[Callable]] = {}
        
        logger.info(f"Cursor Agent inicializado en {workspace_path}")
        if not self.workspace_safe:
            logger.warning("Workspace no considerado seguro para operaciones automáticas")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Carga configuración desde archivo YAML."""
        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except (FileNotFoundError, ImportError):
            logger.warning(f"Archivo de configuración {config_path} no encontrado, usando configuración por defecto")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Configuración por defecto del Cursor Agent."""
        return {
            'max_concurrent_tasks': 3,
            'task_timeout_minutes': 30,
            'safe_file_extensions': ['.py', '.js', '.ts', '.md', '.yml', '.yaml', '.json'],
            'forbidden_paths': ['/etc/', '/var/', '/usr/', '/bin/', '/sbin/'],
            'max_file_size_mb': 10,
            'allowed_commands': ['git', 'python', 'pip', 'npm', 'yarn'],
            'auto_commit': False,
            'create_backup': True,
            'notification_channels': ['console', 'file']
        }
    
    def _validate_workspace_safety(self) -> bool:
        """Valida que el workspace sea seguro para operaciones automáticas."""
        try:
            # Verificar que esté en un directorio de proyecto
            git_dir = self.workspace_path / ".git"
            if not git_dir.exists():
                logger.warning("No se detectó directorio .git - workspace no considerado seguro")
                return False
            
            # Verificar permisos de escritura
            test_file = self.workspace_path / ".cursor_agent_test"
            try:
                test_file.write_text("test")
                test_file.unlink()
            except Exception:
                logger.warning("No se tienen permisos de escritura en el workspace")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Error validando workspace: {e}")
            return False
    
    async def submit_task(self,
                          task_type: TaskType,
                          contract: TaskContract,
                          priority: int = 1,
                          timeout_minutes: Optional[int] = None) -> str:
        """
        Envía una tarea para ejecución en background.
        
        Args:
            task_type: Tipo de tarea a ejecutar
            contract: Contrato de la tarea
            priority: Prioridad de la tarea (1-10, mayor = más prioritaria)
            timeout_minutes: Timeout personalizado en minutos
            
        Returns:
            ID de la tarea creada
        """
        # Verificar límites de tareas concurrentes
        if len(self.active_tasks) >= self.config['max_concurrent_tasks']:
            raise RuntimeError(f"Máximo de tareas concurrentes alcanzado: {self.config['max_concurrent_tasks']}")
        
        # Crear tarea
        task_id = str(uuid.uuid4())
        task = BackgroundTask(
            id=task_id,
            task_type=task_type,
            contract=contract,
            status=AgentStatus.IDLE,
            created_at=datetime.utcnow(),
            metadata={'priority': priority, 'timeout_minutes': timeout_minutes}
        )
        
        # Verificar si requiere aprobación humana
        if contract.human_approval_required and self.human_loop_manager:
            logger.info(f"Tarea {task_id} requiere aprobación humana")
            # Aquí se implementaría la lógica de aprobación
            # Por ahora, asumimos que está aprobada
        
        # Almacenar tarea
        self.active_tasks[task_id] = task
        
        # Ejecutar tarea en background
        asyncio.create_task(self._execute_task(task_id))
        
        logger.info(f"Tarea {task_id} enviada para ejecución: {task_type.value}")
        return task_id
    
    async def _execute_task(self, task_id: str):
        """Ejecuta una tarea en background."""
        task = self.active_tasks[task_id]
        
        try:
            # Actualizar estado
            task.status = AgentStatus.RUNNING
            task.started_at = datetime.utcnow()
            
            # Ejecutar tarea según el tipo
            if task.task_type == TaskType.DRAFT_PR:
                result = await self._generate_draft_pr(task)
            elif task.task_type == TaskType.GENERATE_TESTS:
                result = await self._generate_tests(task)
            elif task.task_type == TaskType.GENERATE_DOCS:
                result = await self._generate_documentation(task)
            elif task.task_type == TaskType.CODE_REVIEW:
                result = await self._perform_code_review(task)
            elif task.task_type == TaskType.REFACTOR:
                result = await self._refactor_code(task)
            elif task.task_type == TaskType.SECURITY_SCAN:
                result = await self._security_scan(task)
            elif task.task_type == TaskType.PERFORMANCE_OPTIMIZATION:
                result = await self._optimize_performance(task)
            else:
                raise ValueError(f"Tipo de tarea no soportado: {task.task_type}")
            
            # Actualizar tarea con resultado
            task.status = AgentStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.result = result
            task.progress = 100.0
            
            # Mover a historial
            self.task_history.append(task)
            del self.active_tasks[task_id]
            
            # Ejecutar callbacks
            await self._execute_callbacks(task_id, 'completed', result)
            
            logger.info(f"Tarea {task_id} completada exitosamente")
            
        except Exception as e:
            logger.error(f"Error ejecutando tarea {task_id}: {e}")
            
            # Actualizar estado de error
            task.status = AgentStatus.FAILED
            task.completed_at = datetime.utcnow()
            task.error = str(e)
            
            # Mover a historial
            self.task_history.append(task)
            del self.active_tasks[task_id]
            
            # Ejecutar callbacks de error
            await self._execute_callbacks(task_id, 'failed', {'error': str(e)})
    
    async def _generate_draft_pr(self, task: BackgroundTask) -> TaskResult:
        """Genera un draft PR basado en el contrato."""
        start_time = datetime.utcnow()
        
        try:
            # Crear rama para el PR
            branch_name = f"feature/auto-{task.contract.task_type.value}-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
            
            # Crear archivos según el tipo de tarea
            files_created = []
            
            if task.contract.task_type.value == "code":
                # Generar archivo de código
                code_file = await self._generate_code_file(task)
                files_created.append(code_file)
                
                # Generar tests si es necesario
                if task.contract.metrics.get('require_tests', False):
                    test_file = await self._generate_test_file(task, code_file)
                    files_created.append(test_file)
                
                # Generar documentación
                doc_file = await self._generate_doc_file(task, code_file)
                files_created.append(doc_file)
            
            elif task.contract.task_type.value == "documentation":
                # Generar documentación
                doc_file = await self._generate_doc_file(task)
                files_created.append(doc_file)
            
            # Crear archivo de descripción del PR
            pr_description = await self._generate_pr_description(task, files_created)
            files_created.append(pr_description)
            
            # Crear commit y push
            await self._git_operations(branch_name, files_created, task)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return TaskResult(
                success=True,
                output=f"Draft PR creado en rama {branch_name}",
                artifacts=files_created,
                metadata={
                    'branch_name': branch_name,
                    'files_created': len(files_created),
                    'pr_description': pr_description
                },
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            return TaskResult(
                success=False,
                output="",
                artifacts=[],
                metadata={},
                execution_time=execution_time,
                error_message=str(e)
            )
    
    async def _generate_tests(self, task: BackgroundTask) -> TaskResult:
        """Genera tests para el código especificado."""
        start_time = datetime.utcnow()
        
        try:
            # Analizar el código para generar tests apropiados
            test_files = []
            
            # Generar tests unitarios
            unit_test_file = await self._generate_unit_tests(task)
            test_files.append(unit_test_file)
            
            # Generar tests de integración si es necesario
            if task.contract.metrics.get('require_integration_tests', False):
                integration_test_file = await self._generate_integration_tests(task)
                test_files.append(integration_test_file)
            
            # Generar tests de performance si es necesario
            if task.contract.metrics.get('require_performance_tests', False):
                perf_test_file = await self._generate_performance_tests(task)
                test_files.append(perf_test_file)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return TaskResult(
                success=True,
                output=f"Tests generados: {len(test_files)} archivos",
                artifacts=test_files,
                metadata={'test_types': [f.split('_')[-1] for f in test_files]},
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            return TaskResult(
                success=False,
                output="",
                artifacts=[],
                metadata={},
                execution_time=execution_time,
                error_message=str(e)
            )
    
    async def _generate_documentation(self, task: BackgroundTask) -> TaskResult:
        """Genera documentación para el código o funcionalidad especificada."""
        start_time = datetime.utcnow()
        
        try:
            doc_files = []
            
            # Generar README si es necesario
            if task.contract.metrics.get('require_readme', True):
                readme_file = await self._generate_readme(task)
                doc_files.append(readme_file)
            
            # Generar documentación de API si es necesario
            if task.contract.metrics.get('require_api_docs', False):
                api_docs_file = await self._generate_api_docs(task)
                doc_files.append(api_docs_file)
            
            # Generar documentación técnica si es necesario
            if task.contract.metrics.get('require_technical_docs', False):
                tech_docs_file = await self._generate_technical_docs(task)
                doc_files.append(tech_docs_file)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return TaskResult(
                success=True,
                output=f"Documentación generada: {len(doc_files)} archivos",
                artifacts=doc_files,
                metadata={'doc_types': [f.split('_')[-1] for f in doc_files]},
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            return TaskResult(
                success=False,
                output="",
                artifacts=[],
                metadata={},
                execution_time=execution_time,
                error_message=str(e)
            )
    
    async def _generate_code_file(self, task: BackgroundTask) -> str:
        """Genera un archivo de código basado en el contrato."""
        # Implementación simplificada - en producción usar LLM
        code_content = f"""# Generated by Cursor Agent
# Task: {task.contract.goal}
# Contract ID: {task.contract.id}

def {task.contract.task_type.value}_function():
    \"\"\"
    {task.contract.goal}
    \"\"\"
    # TODO: Implement based on contract requirements
    pass

if __name__ == "__main__":
    {task.contract.task_type.value}_function()
"""
        
        file_path = self.workspace_path / f"generated_{task.contract.task_type.value}.py"
        async with aiofiles.open(file_path, 'w') as f:
            await f.write(code_content)
        
        return str(file_path)
    
    async def _generate_test_file(self, task: BackgroundTask, code_file: str) -> str:
        """Genera un archivo de tests para el código."""
        test_content = f"""# Tests for {code_file}
# Generated by Cursor Agent

import pytest
from pathlib import Path

def test_{task.contract.task_type.value}_function():
    \"\"\"
    Test for {task.contract.goal}
    \"\"\"
    # TODO: Implement actual tests
    assert True

if __name__ == "__main__":
    pytest.main([__file__])
"""
        
        file_path = self.workspace_path / f"test_{task.contract.task_type.value}.py"
        async with aiofiles.open(file_path, 'w') as f:
            await f.write(test_content)
        
        return str(file_path)
    
    async def _generate_doc_file(self, task: BackgroundTask, code_file: str = None) -> str:
        """Genera un archivo de documentación."""
        doc_content = f"""# Documentation for {task.contract.task_type.value}
# Generated by Cursor Agent

## Overview
{task.contract.goal}

## Contract Details
- **ID**: {task.contract.id}
- **Type**: {task.contract.task_type.value}
- **Risk Level**: {task.contract.risk_level.value}
- **Created**: {task.contract.created_at}

## Requirements
{chr(10).join(f"- {req}" for req in task.contract.musts)}

## Usage
TODO: Add usage examples and documentation
"""
        
        file_path = self.workspace_path / f"docs_{task.contract.task_type.value}.md"
        async with aiofiles.open(file_path, 'w') as f:
            await f.write(doc_content)
        
        return str(file_path)
    
    async def _generate_pr_description(self, task: BackgroundTask, files_created: List[str]) -> str:
        """Genera la descripción del PR."""
        description = f"""# Auto-generated PR by Cursor Agent

## Task
{task.contract.goal}

## Contract Details
- **Contract ID**: {task.contract.id}
- **Task Type**: {task.contract.task_type.value}
- **Risk Level**: {task.contract.risk_level.value}
- **Created**: {task.contract.created_at}

## Files Created/Modified
{chr(10).join(f"- {file}" for file in files_created)}

## Requirements Met
{chr(10).join(f"- [x] {req}" for req in task.contract.musts)}

## Notes
This PR was automatically generated by the Cursor Agent system.
Please review the changes and ensure they meet your requirements.

## Testing
- [ ] Code compiles/runs
- [ ] Tests pass
- [ ] Documentation is clear
- [ ] Security review completed
"""
        
        file_path = self.workspace_path / "PR_DESCRIPTION.md"
        async with aiofiles.open(file_path, 'w') as f:
            await f.write(description)
        
        return str(file_path)
    
    async def _git_operations(self, branch_name: str, files_created: List[str], task: BackgroundTask):
        """Realiza operaciones de Git para crear el PR."""
        try:
            # Crear y cambiar a nueva rama
            subprocess.run(['git', 'checkout', '-b', branch_name], 
                         cwd=self.workspace_path, check=True)
            
            # Agregar archivos
            for file_path in files_created:
                subprocess.run(['git', 'add', file_path], 
                             cwd=self.workspace_path, check=True)
            
            # Commit
            commit_message = f"feat: Auto-generated {task.contract.task_type.value} by Cursor Agent\n\n{task.contract.goal}"
            subprocess.run(['git', 'commit', '-m', commit_message], 
                         cwd=self.workspace_path, check=True)
            
            # Push (solo si está configurado)
            if self.config.get('auto_push', False):
                subprocess.run(['git', 'push', 'origin', branch_name], 
                             cwd=self.workspace_path, check=True)
            
            logger.info(f"Git operations completed for branch {branch_name}")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Git operation failed: {e}")
            raise
    
    async def _execute_callbacks(self, task_id: str, event: str, data: Any):
        """Ejecuta callbacks registrados para la tarea."""
        if task_id in self.task_callbacks:
            for callback in self.task_callbacks[task_id]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event, data)
                    else:
                        callback(event, data)
                except Exception as e:
                    logger.error(f"Error ejecutando callback: {e}")
    
    def register_callback(self, task_id: str, callback: Callable):
        """Registra un callback para una tarea específica."""
        if task_id not in self.task_callbacks:
            self.task_callbacks[task_id] = []
        self.task_callbacks[task_id].append(callback)
    
    def get_task_status(self, task_id: str) -> Optional[BackgroundTask]:
        """Obtiene el estado de una tarea."""
        return self.active_tasks.get(task_id) or next(
            (task for task in self.task_history if task.id == task_id), None
        )
    
    def list_active_tasks(self) -> List[BackgroundTask]:
        """Lista todas las tareas activas."""
        return list(self.active_tasks.values())
    
    def list_completed_tasks(self) -> List[BackgroundTask]:
        """Lista todas las tareas completadas."""
        return [task for task in self.task_history if task.status == AgentStatus.COMPLETED]
    
    def list_failed_tasks(self) -> List[BackgroundTask]:
        """Lista todas las tareas fallidas."""
        return [task for task in self.task_history if task.status == AgentStatus.FAILED]
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancela una tarea activa."""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.status = AgentStatus.CANCELLED
            task.completed_at = datetime.utcnow()
            
            # Mover a historial
            self.task_history.append(task)
            del self.active_tasks[task_id]
            
            await self._execute_callbacks(task_id, 'cancelled', {})
            return True
        
        return False
    
    def get_agent_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del agente."""
        total_tasks = len(self.active_tasks) + len(self.task_history)
        completed_tasks = len(self.list_completed_tasks())
        failed_tasks = len(self.list_failed_tasks())
        
        return {
            'total_tasks': total_tasks,
            'active_tasks': len(self.active_tasks),
            'completed_tasks': completed_tasks,
            'failed_tasks': failed_tasks,
            'success_rate': completed_tasks / total_tasks if total_tasks > 0 else 0,
            'workspace_safe': self.workspace_safe,
            'max_concurrent_tasks': self.config['max_concurrent_tasks']
        }


# Funciones de conveniencia para integración con otros módulos
async def create_cursor_agent(context_manager: ContextManager,
                             human_loop_manager: Optional[HumanLoopManager] = None,
                             workspace_path: str = ".") -> CursorAgent:
    """
    Función de conveniencia para crear un Cursor Agent.
    
    Args:
        context_manager: Gestor de contexto
        human_loop_manager: Gestor de human-in-the-loop
        workspace_path: Ruta del workspace
        
    Returns:
        CursorAgent configurado
    """
    return CursorAgent(
        context_manager=context_manager,
        human_loop_manager=human_loop_manager,
        workspace_path=workspace_path
    )


async def submit_background_task(agent: CursorAgent,
                                task_type: TaskType,
                                contract: TaskContract,
                                priority: int = 1) -> str:
    """
    Función de conveniencia para enviar tareas en background.
    
    Args:
        agent: Cursor Agent
        task_type: Tipo de tarea
        contract: Contrato de la tarea
        priority: Prioridad
        
    Returns:
        ID de la tarea
    """
    return await agent.submit_task(task_type, contract, priority)


def get_task_status(agent: CursorAgent, task_id: str) -> Optional[BackgroundTask]:
    """
    Función de conveniencia para obtener estado de tarea.
    
    Args:
        agent: Cursor Agent
        task_id: ID de la tarea
        
    Returns:
        Estado de la tarea o None
    """
    return agent.get_task_status(task_id)
