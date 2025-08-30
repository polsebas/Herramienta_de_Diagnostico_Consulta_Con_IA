"""
Ejemplo completo del sistema de Cursor Integration - Background Agents

Este script demuestra todas las capacidades del Cursor Agent:
- Generación de Draft PRs
- Generación automática de tests
- Generación de documentación
- Integración con Spec Layer
- Gestión de tareas en background
"""

import asyncio
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from app.cursor_agent import (
    CursorAgent, TaskType, AgentStatus, BackgroundTask,
    create_cursor_agent, submit_background_task, get_task_status
)
from app.spec_layer import (
    build_task_contract, TaskType as SpecTaskType, RiskLevel
)
from app.context_manager import ContextManager
from app.human_loop import HumanLoopManager

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def demo_cursor_agent_initialization():
    """Demo de inicialización del Cursor Agent."""
    print("\n" + "="*60)
    print("DEMO: Inicialización del Cursor Agent")
    print("="*60)
    
    # Inicializar componentes
    context_manager = ContextManager()
    human_loop_manager = HumanLoopManager()
    
    # Crear Cursor Agent
    agent = await create_cursor_agent(
        context_manager=context_manager,
        human_loop_manager=human_loop_manager,
        workspace_path="."
    )
    
    # Verificar estado del agente
    stats = agent.get_agent_stats()
    print(f"Cursor Agent inicializado:")
    print(f"- Workspace seguro: {stats['workspace_safe']}")
    print(f"- Máximo tareas concurrentes: {stats['max_concurrent_tasks']}")
    print(f"- Tareas activas: {stats['active_tasks']}")
    print(f"- Tareas completadas: {stats['completed_tasks']}")
    
    return agent


async def demo_draft_pr_generation(agent: CursorAgent):
    """Demo de generación de Draft PRs."""
    print("\n" + "="*60)
    print("DEMO: Generación de Draft PRs")
    print("="*60)
    
    # Crear contrato para generación de código
    contract = await build_task_contract(
        query="Implementar función de validación de emails",
        user_role="developer",
        risk_level=RiskLevel.LOW
    )
    
    print(f"Contrato creado:")
    print(f"- ID: {contract.id}")
    print(f"- Tipo: {contract.task_type.value}")
    print(f"- Riesgo: {contract.risk_level.value}")
    print(f"- Objetivo: {contract.goal}")
    
    # Enviar tarea para generar Draft PR
    task_id = await submit_background_task(
        agent=agent,
        task_type=TaskType.DRAFT_PR,
        contract=contract,
        priority=5
    )
    
    print(f"\nTarea enviada: {task_id}")
    
    # Monitorear progreso
    await monitor_task_progress(agent, task_id)
    
    return task_id


async def demo_test_generation(agent: CursorAgent):
    """Demo de generación automática de tests."""
    print("\n" + "="*60)
    print("DEMO: Generación de Tests")
    print("="*60)
    
    # Crear contrato para tests
    contract = await build_task_contract(
        query="Generar tests unitarios para función de validación",
        user_role="developer",
        risk_level=RiskLevel.LOW
    )
    
    # Modificar métricas para requerir tests
    contract.metrics['require_tests'] = True
    contract.metrics['require_integration_tests'] = True
    
    print(f"Contrato para tests creado:")
    print(f"- ID: {contract.id}")
    print(f"- Requiere tests: {contract.metrics.get('require_tests')}")
    print(f"- Requiere tests de integración: {contract.metrics.get('require_integration_tests')}")
    
    # Enviar tarea para generar tests
    task_id = await submit_background_task(
        agent=agent,
        task_type=TaskType.GENERATE_TESTS,
        contract=contract,
        priority=4
    )
    
    print(f"\nTarea de tests enviada: {task_id}")
    
    # Monitorear progreso
    await monitor_task_progress(agent, task_id)
    
    return task_id


async def demo_documentation_generation(agent: CursorAgent):
    """Demo de generación automática de documentación."""
    print("\n" + "="*60)
    print("DEMO: Generación de Documentación")
    print("="*60)
    
    # Crear contrato para documentación
    contract = await build_task_contract(
        query="Generar documentación técnica para sistema de validación",
        user_role="technical_writer",
        risk_level=RiskLevel.LOW
    )
    
    # Modificar métricas para requerir documentación
    contract.metrics['require_readme'] = True
    contract.metrics['require_api_docs'] = True
    contract.metrics['require_technical_docs'] = True
    
    print(f"Contrato para documentación creado:")
    print(f"- ID: {contract.id}")
    print(f"- Requiere README: {contract.metrics.get('require_readme')}")
    print(f"- Requiere API docs: {contract.metrics.get('require_api_docs')}")
    print(f"- Requiere docs técnicas: {contract.metrics.get('require_technical_docs')}")
    
    # Enviar tarea para generar documentación
    task_id = await submit_background_task(
        agent=agent,
        task_type=TaskType.GENERATE_DOCS,
        contract=contract,
        priority=3
    )
    
    print(f"\nTarea de documentación enviada: {task_id}")
    
    # Monitorear progreso
    await monitor_task_progress(agent, task_id)
    
    return task_id


async def demo_multiple_tasks(agent: CursorAgent):
    """Demo de ejecución de múltiples tareas en paralelo."""
    print("\n" + "="*60)
    print("DEMO: Múltiples Tareas en Paralelo")
    print("="*60)
    
    # Crear múltiples contratos
    contracts = []
    queries = [
        "Implementar función de logging",
        "Crear tests para sistema de autenticación",
        "Generar documentación de API"
    ]
    
    for i, query in enumerate(queries):
        contract = await build_task_contract(
            query=query,
            user_role="developer",
            risk_level=RiskLevel.LOW
        )
        contracts.append(contract)
        print(f"Contrato {i+1}: {contract.goal[:50]}...")
    
    # Enviar tareas en paralelo
    task_ids = []
    task_types = [TaskType.DRAFT_PR, TaskType.GENERATE_TESTS, TaskType.GENERATE_DOCS]
    
    for i, (contract, task_type) in enumerate(zip(contracts, task_types)):
        task_id = await submit_background_task(
            agent=agent,
            task_type=task_type,
            contract=contract,
            priority=5 - i  # Prioridades decrecientes
        )
        task_ids.append(task_id)
        print(f"Tarea {i+1} enviada: {task_id}")
    
    # Monitorear todas las tareas
    print(f"\nMonitoreando {len(task_ids)} tareas en paralelo...")
    await asyncio.gather(*[
        monitor_task_progress(agent, task_id) for task_id in task_ids
    ])
    
    return task_ids


async def demo_task_management(agent: CursorAgent):
    """Demo de gestión de tareas."""
    print("\n" + "="*60)
    print("DEMO: Gestión de Tareas")
    print("="*60)
    
    # Listar tareas activas
    active_tasks = agent.list_active_tasks()
    print(f"Tareas activas: {len(active_tasks)}")
    
    for task in active_tasks:
        print(f"- {task.id}: {task.task_type.value} - {task.status.value}")
    
    # Listar tareas completadas
    completed_tasks = agent.list_completed_tasks()
    print(f"\nTareas completadas: {len(completed_tasks)}")
    
    for task in completed_tasks[:3]:  # Mostrar solo las primeras 3
        print(f"- {task.id}: {task.task_type.value} - {task.status.value}")
        if task.result:
            print(f"  Resultado: {task.result.get('output', 'N/A')[:50]}...")
    
    # Listar tareas fallidas
    failed_tasks = agent.list_failed_tasks()
    print(f"\nTareas fallidas: {len(failed_tasks)}")
    
    for task in failed_tasks:
        print(f"- {task.id}: {task.task_type.value} - {task.error}")
    
    # Estadísticas del agente
    stats = agent.get_agent_stats()
    print(f"\nEstadísticas del agente:")
    print(f"- Total tareas: {stats['total_tasks']}")
    print(f"- Tasa de éxito: {stats['success_rate']:.2%}")
    print(f"- Workspace seguro: {stats['workspace_safe']}")


async def demo_callback_system(agent: CursorAgent):
    """Demo del sistema de callbacks."""
    print("\n" + "="*60)
    print("DEMO: Sistema de Callbacks")
    print("="*60)
    
    # Crear contrato simple
    contract = await build_task_contract(
        query="Crear función de utilidad",
        user_role="developer",
        risk_level=RiskLevel.LOW
    )
    
    # Definir callbacks
    def task_started_callback(event: str, data: Any):
        print(f"🔔 Callback: Tarea {event} - {data}")
    
    def task_completed_callback(event: str, data: Any):
        print(f"✅ Callback: Tarea {event} completada")
        if isinstance(data, dict) and 'output' in data:
            print(f"   Output: {data['output'][:50]}...")
    
    def task_failed_callback(event: str, data: Any):
        print(f"❌ Callback: Tarea {event} falló")
        if isinstance(data, dict) and 'error' in data:
            print(f"   Error: {data['error']}")
    
    # Enviar tarea con callbacks
    task_id = await submit_background_task(
        agent=agent,
        task_type=TaskType.DRAFT_PR,
        contract=contract,
        priority=2
    )
    
    # Registrar callbacks
    agent.register_callback(task_id, task_started_callback)
    agent.register_callback(task_id, task_completed_callback)
    agent.register_callback(task_id, task_failed_callback)
    
    print(f"Tarea enviada con callbacks: {task_id}")
    
    # Monitorear progreso
    await monitor_task_progress(agent, task_id)


async def monitor_task_progress(agent: CursorAgent, task_id: str, timeout_seconds: int = 30):
    """Monitorea el progreso de una tarea."""
    start_time = time.time()
    
    while time.time() - start_time < timeout_seconds:
        task = agent.get_task_status(task_id)
        
        if not task:
            print(f"Tarea {task_id} no encontrada")
            return
        
        if task.status in [AgentStatus.COMPLETED, AgentStatus.FAILED, AgentStatus.CANCELLED]:
            if task.status == AgentStatus.COMPLETED:
                print(f"✅ Tarea {task_id} completada exitosamente")
                if task.result:
                    print(f"   Output: {task.result.get('output', 'N/A')}")
                    print(f"   Artifacts: {len(task.result.get('artifacts', []))}")
                    print(f"   Tiempo de ejecución: {task.result.get('execution_time', 0):.2f}s")
            elif task.status == AgentStatus.FAILED:
                print(f"❌ Tarea {task_id} falló: {task.error}")
            elif task.status == AgentStatus.CANCELLED:
                print(f"⏹️ Tarea {task_id} cancelada")
            return
        
        print(f"⏳ Tarea {task_id}: {task.status.value} - Progreso: {task.progress:.1f}%")
        await asyncio.sleep(2)
    
    print(f"⏰ Timeout monitoreando tarea {task_id}")


async def main():
    """Función principal que ejecuta todos los demos."""
    print("🚀 DEMO COMPLETO DEL CURSOR AGENT")
    print("Sistema de Agentes en Background para Tareas Seguras")
    
    try:
        # Inicializar agente
        agent = await demo_cursor_agent_initialization()
        
        # Ejecutar demos en secuencia
        await demo_draft_pr_generation(agent)
        await demo_test_generation(agent)
        await demo_documentation_generation(agent)
        await demo_multiple_tasks(agent)
        await demo_task_management(agent)
        await demo_callback_system(agent)
        
        print("\n" + "="*60)
        print("✅ TODOS LOS DEMOS COMPLETADOS EXITOSAMENTE")
        print("="*60)
        
        # Mostrar estadísticas finales
        final_stats = agent.get_agent_stats()
        print(f"\n📊 Estadísticas Finales:")
        print(f"- Total tareas procesadas: {final_stats['total_tasks']}")
        print(f"- Tasa de éxito: {final_stats['success_rate']:.2%}")
        print(f"- Tareas activas: {final_stats['active_tasks']}")
        
    except Exception as e:
        logger.error(f"Error en demo: {e}")
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
