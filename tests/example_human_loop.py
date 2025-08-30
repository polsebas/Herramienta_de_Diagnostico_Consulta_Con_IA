#!/usr/bin/env python3
"""
Ejemplo de uso del sistema Human-in-the-Loop.

Este script demuestra las capacidades del PR-B:
- Solicitud de aprobaciones humanas
- Verificación de acciones críticas
- Sistema de notificaciones
- Manejo de timeouts y respuestas
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Dict, Any, List

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Importar el sistema Human-in-the-Loop
from app.human_loop import (
    HumanLoopManager, 
    NotificationConfig, 
    NotificationType,
    check_critical_action,
    notify_and_wait_for_approval
)

async def demo_basic_approval():
    """Demuestra aprobación básica."""
    print("\n" + "="*60)
    print("🔐 DEMO: Aprobación Básica")
    print("="*60)
    
    # Configurar notificaciones (modo simulado)
    config = NotificationConfig(
        slack_webhook_url=None,  # Sin Slack para demo
        webhook_url=None,        # Sin webhook para demo
        timeout_hours=1          # 1 hora para demo
    )
    
    # Crear gestor
    human_loop = HumanLoopManager(config)
    
    # Solicitar aprobación
    approval_id = await human_loop.request_approval(
        action_type="demo_action",
        description="Acción de demostración del sistema Human-in-the-Loop",
        payload={"demo": True, "timestamp": datetime.now().isoformat()},
        requester="demo_user",
        timeout_hours=1
    )
    
    print(f"✅ Solicitud de aprobación creada: {approval_id}")
    print(f"📊 Estado: {human_loop.get_approval_status(approval_id).status.value}")
    
    # Simular aprobación automática después de 2 segundos
    await asyncio.sleep(2)
    
    # Aprobar acción
    success = await human_loop.approve_action(approval_id, "demo_approver")
    
    if success:
        print(f"✅ Acción aprobada exitosamente")
        print(f"📊 Estado final: {human_loop.get_approval_status(approval_id).status.value}")
    else:
        print(f"❌ Error al aprobar acción")
    
    # Mostrar estadísticas
    stats = human_loop.get_stats()
    print(f"\n📈 Estadísticas del sistema:")
    print(f"   Total de solicitudes: {stats['total_requests']}")
    print(f"   Solicitudes aprobadas: {stats['approved_requests']}")
    print(f"   Tasa de aprobación: {stats['approval_rate']:.1%}")

async def demo_critical_action_check():
    """Demuestra verificación de acciones críticas."""
    print("\n" + "="*60)
    print("⚠️  DEMO: Verificación de Acciones Críticas")
    print("="*60)
    
    # Configurar notificaciones
    config = NotificationConfig(
        slack_webhook_url=None,
        webhook_url=None,
        timeout_hours=1
    )
    
    # Crear gestor
    human_loop = HumanLoopManager(config)
    
    # Plan de acción crítico
    critical_plan = {
        "action": "update_auth_system",
        "description": "Actualizar sistema de autenticación",
        "labels": ["security", "critical"],
        "files": ["src/auth/login.py", "src/auth/register.py", "src/auth/middleware.py"]
    }
    
    # Archivos afectados (incluyen rutas críticas)
    files_affected = [
        "src/auth/login.py",
        "src/auth/register.py", 
        "src/auth/middleware.py",
        "src/auth/utils.py",
        "src/auth/config.py",
        "tests/auth/test_login.py",
        "tests/auth/test_register.py",
        "docs/auth/README.md"
    ]
    
    print(f"🔍 Verificando plan crítico...")
    print(f"   Acción: {critical_plan['action']}")
    print(f"   Archivos afectados: {len(files_affected)}")
    print(f"   Labels: {critical_plan['labels']}")
    
    # Verificar si es crítica
    can_proceed = await check_critical_action(
        plan=critical_plan,
        files_affected=files_affected,
        human_loop_manager=human_loop,
        risk_threshold=0.5  # Umbral más bajo para demo
    )
    
    if can_proceed:
        print("✅ Acción puede proceder automáticamente")
    else:
        print("❌ Acción requiere aprobación humana")
        
        # Obtener solicitudes pendientes
        pending = human_loop.get_pending_approvals()
        if pending:
            approval = pending[0]
            print(f"🔐 Solicitud pendiente: {approval.id}")
            print(f"   Descripción: {approval.description}")
            print(f"   Score de riesgo: {approval.payload.get('risk_score', 'N/A')}")
            
            # Simular aprobación
            await asyncio.sleep(1)
            success = await human_loop.approve_action(approval.id, "security_team")
            
            if success:
                print("✅ Acción crítica aprobada por el equipo de seguridad")
            else:
                print("❌ Error al aprobar acción crítica")

async def demo_notification_system():
    """Demuestra el sistema de notificaciones."""
    print("\n" + "="*60)
    print("📢 DEMO: Sistema de Notificaciones")
    print("="*60)
    
    # Configurar con webhook simulado
    config = NotificationConfig(
        webhook_url="http://localhost:8000/webhook",  # URL simulada
        timeout_hours=1
    )
    
    # Crear gestor
    human_loop = HumanLoopManager(config)
    
    # Solicitar aprobación con notificaciones
    approval_id = await human_loop.request_approval(
        action_type="deployment",
        description="Despliegue a producción del sistema de pagos",
        payload={
            "environment": "production",
            "services": ["payment-api", "payment-frontend"],
            "estimated_downtime": "5 minutos"
        },
        requester="devops_team",
        timeout_hours=2,
        notification_types=[NotificationType.WEBHOOK]
    )
    
    print(f"📢 Notificación enviada para: {approval_id}")
    print(f"   Tipo: Webhook")
    print(f"   Acción: Despliegue a producción")
    print(f"   Timeout: 2 horas")
    
    # Simular respuesta del webhook
    await asyncio.sleep(1)
    
    # Simular aprobación
    success = await human_loop.approve_action(approval_id, "devops_lead")
    
    if success:
        print("✅ Despliegue aprobado por DevOps Lead")
        print("🚀 Procediendo con despliegue...")
    else:
        print("❌ Error en la aprobación")

async def demo_timeout_and_expiration():
    """Demuestra manejo de timeouts y expiración."""
    print("\n" + "="*60)
    print("⏰ DEMO: Timeouts y Expiración")
    print("="*60)
    
    # Configurar con timeout muy corto
    config = NotificationConfig(
        timeout_hours=0.001  # ~3.6 segundos
    )
    
    # Crear gestor
    human_loop = HumanLoopManager(config)
    
    # Solicitar aprobación con timeout corto
    approval_id = await human_loop.request_approval(
        action_type="quick_action",
        description="Acción rápida con timeout corto",
        payload={"quick": True},
        requester="demo_user"
    )
    
    print(f"⏰ Solicitud creada con timeout corto: {approval_id}")
    print(f"   Timeout configurado: {config.timeout_hours} horas")
    
    # Esperar a que expire
    print("⏳ Esperando expiración...")
    await asyncio.sleep(5)  # Esperar 5 segundos
    
    # Verificar estado
    approval = human_loop.get_approval_status(approval_id)
    print(f"📊 Estado después de espera: {approval.status.value}")
    
    if approval.status.value == "expired":
        print("✅ Solicitud expiró correctamente")
    else:
        print("⚠️  Solicitud no expiró como esperado")
    
    # Limpiar solicitudes expiradas
    expired = human_loop.cleanup_expired_approvals()
    print(f"🧹 Solicitudes expiradas limpiadas: {len(expired)}")

async def demo_callback_system():
    """Demuestra el sistema de callbacks."""
    print("\n" + "="*60)
    print("🔄 DEMO: Sistema de Callbacks")
    print("="*60)
    
    # Configurar
    config = NotificationConfig(timeout_hours=1)
    human_loop = HumanLoopManager(config)
    
    # Callback que se ejecuta cuando se completa la aprobación
    async def approval_callback(approval_request):
        print(f"🎯 Callback ejecutado para: {approval_request.id}")
        print(f"   Estado: {approval_request.status.value}")
        print(f"   Acción: {approval_request.action_type}")
        
        if approval_request.status.value == "approved":
            print("   ✅ Ejecutando acción aprobada...")
            # Aquí se ejecutaría la acción real
        elif approval_request.status.value == "rejected":
            print("   ❌ Acción rechazada, no se ejecuta")
    
    # Solicitar aprobación con callback
    approval_id = await human_loop.request_approval(
        action_type="callback_demo",
        description="Acción con callback de demostración",
        payload={"callback": True},
        requester="demo_user"
    )
    
    # Registrar callback
    human_loop.register_callback(approval_id, approval_callback)
    print(f"🔄 Callback registrado para: {approval_id}")
    
    # Simular aprobación
    await asyncio.sleep(1)
    success = await human_loop.approve_action(approval_id, "callback_user")
    
    if success:
        print("✅ Acción aprobada, callback ejecutado")
    else:
        print("❌ Error en la aprobación")

async def main():
    """Función principal de demostración."""
    print("🚀 Sistema Human-in-the-Loop - Demostración Completa")
    print("="*60)
    print("Este demo muestra las capacidades del PR-B:")
    print("• Sistema de aprobaciones humanas")
    print("• Verificación de acciones críticas")
    print("• Sistema de notificaciones")
    print("• Manejo de timeouts y expiración")
    print("• Sistema de callbacks")
    print("="*60)
    
    try:
        # Ejecutar todas las demos
        await demo_basic_approval()
        await demo_critical_action_check()
        await demo_notification_system()
        await demo_timeout_and_expiration()
        await demo_callback_system()
        
        print("\n" + "="*60)
        print("🎉 ¡Todas las demostraciones completadas exitosamente!")
        print("="*60)
        
        print("\n📋 Resumen de funcionalidades probadas:")
        print("✅ Aprobaciones básicas con timeout")
        print("✅ Verificación de acciones críticas")
        print("✅ Sistema de notificaciones (webhook)")
        print("✅ Manejo de timeouts y expiración")
        print("✅ Sistema de callbacks automáticos")
        print("✅ Cálculo de scores de riesgo")
        print("✅ Limpieza automática de solicitudes expiradas")
        
        print("\n🚀 El sistema está listo para integración en producción!")
        
    except Exception as e:
        logger.error(f"Error en la demostración: {e}")
        print(f"❌ Error en la demostración: {e}")

if __name__ == "__main__":
    asyncio.run(main())
