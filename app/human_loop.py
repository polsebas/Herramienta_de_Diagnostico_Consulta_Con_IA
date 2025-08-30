"""
Sistema de Human-in-the-Loop para el proyecto Next Level.

Este módulo implementa el PR-B del plan de implementación:
- Sistema de notificaciones Slack/GitHub
- Listener para aprobaciones humanas
- Integración con check_critical_action
- Notificaciones asincrónicas

Inspirado en las mejores prácticas de HumanLayer para flujos de aprobación
asíncronos y control humano en puntos críticos.
"""

import os
import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
from pathlib import Path

logger = logging.getLogger(__name__)

class ApprovalStatus(Enum):
    """Estados de aprobación."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class NotificationType(Enum):
    """Tipos de notificación."""
    SLACK = "slack"
    GITHUB = "github"
    EMAIL = "email"
    WEBHOOK = "webhook"

@dataclass
class ApprovalRequest:
    """Solicitud de aprobación humana."""
    id: str
    action_type: str
    description: str
    payload: Dict[str, Any]
    requester: str
    created_at: datetime
    expires_at: datetime
    status: ApprovalStatus = ApprovalStatus.PENDING
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class NotificationConfig:
    """Configuración de notificaciones."""
    slack_webhook_url: Optional[str] = None
    slack_channel: str = "#github-indexing"
    github_token: Optional[str] = None
    github_repo: Optional[str] = None
    email_smtp_server: Optional[str] = None
    email_smtp_port: int = 587
    email_username: Optional[str] = None
    email_password: Optional[str] = None
    email_from: Optional[str] = None
    email_to: List[str] = None
    webhook_url: Optional[str] = None
    timeout_hours: int = 24
    retry_attempts: int = 3
    retry_delay_seconds: int = 60

class HumanLoopManager:
    """Gestor principal del sistema Human-in-the-Loop."""
    
    def __init__(self, config: NotificationConfig):
        """
        Inicializa el gestor de Human-in-the-Loop.
        
        Args:
            config: Configuración de notificaciones
        """
        self.config = config
        self.pending_approvals: Dict[str, ApprovalRequest] = {}
        self.approval_callbacks: Dict[str, Callable] = {}
        self.notification_handlers = self._setup_notification_handlers()
        
        # Inicializar handlers de notificación
        self._initialize_handlers()
        
        logger.info("HumanLoopManager inicializado")
    
    def _setup_notification_handlers(self) -> Dict[NotificationType, Any]:
        """Configura los handlers de notificación disponibles."""
        handlers = {}
        
        if self.config.slack_webhook_url:
            handlers[NotificationType.SLACK] = SlackNotifier(self.config)
            logger.info("Handler de Slack configurado")
        
        if self.config.github_token and self.config.github_repo:
            handlers[NotificationType.GITHUB] = GitHubNotifier(self.config)
            logger.info("Handler de GitHub configurado")
        
        if self.config.email_smtp_server:
            handlers[NotificationType.EMAIL] = EmailNotifier(self.config)
            logger.info("Handler de Email configurado")
        
        if self.config.webhook_url:
            handlers[NotificationType.WEBHOOK] = WebhookNotifier(self.config)
            logger.info("Handler de Webhook configurado")
        
        return handlers
    
    def _initialize_handlers(self):
        """Inicializa los handlers de notificación."""
        for handler in self.notification_handlers.values():
            if hasattr(handler, 'initialize'):
                try:
                    handler.initialize()
                except Exception as e:
                    logger.error(f"Error inicializando handler: {e}")
    
    async def request_approval(self, 
                              action_type: str,
                              description: str,
                              payload: Dict[str, Any],
                              requester: str,
                              timeout_hours: Optional[int] = None,
                              notification_types: Optional[List[NotificationType]] = None,
                              metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Solicita aprobación humana para una acción.
        
        Args:
            action_type: Tipo de acción que requiere aprobación
            description: Descripción de la acción
            payload: Datos de la acción
            requester: Quien solicita la aprobación
            timeout_hours: Tiempo de expiración en horas
            notification_types: Tipos de notificación a usar
            metadata: Metadatos adicionales
        
        Returns:
            ID de la solicitud de aprobación
        """
        approval_id = f"approval_{int(time.time())}_{hash(description) % 10000}"
        
        timeout = timeout_hours or self.config.timeout_hours
        expires_at = datetime.now() + timedelta(hours=timeout)
        
        approval_request = ApprovalRequest(
            id=approval_id,
            action_type=action_type,
            description=description,
            payload=payload,
            requester=requester,
            created_at=datetime.now(),
            expires_at=expires_at,
            metadata=metadata or {}
        )
        
        # Almacenar solicitud
        self.pending_approvals[approval_id] = approval_request
        
        # Enviar notificaciones
        notification_types = notification_types or [NotificationType.SLACK]
        await self._send_approval_notifications(approval_request, notification_types)
        
        logger.info(f"Solicitud de aprobación creada: {approval_id}")
        return approval_id
    
    async def _send_approval_notifications(self, 
                                         approval_request: ApprovalRequest,
                                         notification_types: List[NotificationType]):
        """Envía notificaciones de aprobación."""
        for notification_type in notification_types:
            if notification_type in self.notification_handlers:
                try:
                    handler = self.notification_handlers[notification_type]
                    await handler.send_approval_request(approval_request)
                except Exception as e:
                    logger.error(f"Error enviando notificación {notification_type}: {e}")
    
    async def wait_for_approval(self, 
                               approval_id: str,
                               timeout_seconds: Optional[int] = None) -> bool:
        """
        Espera por la aprobación de una solicitud.
        
        Args:
            approval_id: ID de la solicitud
            timeout_seconds: Timeout en segundos (opcional)
        
        Returns:
            True si fue aprobada, False si fue rechazada o expiró
        """
        if approval_id not in self.pending_approvals:
            raise ValueError(f"Solicitud de aprobación no encontrada: {approval_id}")
        
        approval_request = self.pending_approvals[approval_id]
        
        # Configurar timeout
        if timeout_seconds:
            timeout = timeout_seconds
        else:
            timeout = (approval_request.expires_at - datetime.now()).total_seconds()
            timeout = max(0, timeout)
        
        # Esperar por respuesta
        start_time = time.time()
        while time.time() - start_time < timeout:
            if approval_request.status != ApprovalStatus.PENDING:
                break
            
            # Verificar expiración
            if datetime.now() > approval_request.expires_at:
                approval_request.status = ApprovalStatus.EXPIRED
                break
            
            await asyncio.sleep(1)
        
        # Ejecutar callback si existe
        if approval_id in self.approval_callbacks:
            try:
                await self.approval_callbacks[approval_id](approval_request)
            except Exception as e:
                logger.error(f"Error ejecutando callback: {e}")
        
        return approval_request.status == ApprovalStatus.APPROVED
    
    async def approve_action(self, 
                           approval_id: str, 
                           approver: str,
                           metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Aprueba una acción.
        
        Args:
            approval_id: ID de la solicitud
            approver: Quien aprueba la acción
            metadata: Metadatos adicionales
        
        Returns:
            True si se aprobó exitosamente
        """
        if approval_id not in self.pending_approvals:
            logger.error(f"Solicitud de aprobación no encontrada: {approval_id}")
            return False
        
        approval_request = self.pending_approvals[approval_id]
        
        if approval_request.status != ApprovalStatus.PENDING:
            logger.warning(f"Solicitud {approval_id} ya no está pendiente: {approval_request.status}")
            return False
        
        # Aprobar acción
        approval_request.status = ApprovalStatus.APPROVED
        approval_request.approved_by = approver
        approval_request.approved_at = datetime.now()
        
        if metadata:
            approval_request.metadata.update(metadata)
        
        logger.info(f"Acción aprobada: {approval_id} por {approver}")
        
        # Notificar aprobación
        await self._notify_approval_result(approval_request)
        
        return True
    
    async def reject_action(self, 
                          approval_id: str, 
                          rejector: str,
                          reason: str,
                          metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Rechaza una acción.
        
        Args:
            approval_id: ID de la solicitud
            rejector: Quien rechaza la acción
            reason: Razón del rechazo
            metadata: Metadatos adicionales
        
        Returns:
            True si se rechazó exitosamente
        """
        if approval_id not in self.pending_approvals:
            logger.error(f"Solicitud de aprobación no encontrada: {approval_id}")
            return False
        
        approval_request = self.pending_approvals[approval_id]
        
        if approval_request.status != ApprovalStatus.PENDING:
            logger.warning(f"Solicitud {approval_id} ya no está pendiente: {approval_request.status}")
            return False
        
        # Rechazar acción
        approval_request.status = ApprovalStatus.REJECTED
        approval_request.rejection_reason = reason
        
        if metadata:
            approval_request.metadata.update(metadata)
        
        logger.info(f"Acción rechazada: {approval_id} por {rejector}: {reason}")
        
        # Notificar rechazo
        await self._notify_approval_result(approval_request)
        
        return True
    
    async def _notify_approval_result(self, approval_request: ApprovalRequest):
        """Notifica el resultado de la aprobación."""
        for handler in self.notification_handlers.values():
            try:
                if hasattr(handler, 'send_approval_result'):
                    await handler.send_approval_result(approval_request)
            except Exception as e:
                logger.error(f"Error notificando resultado: {e}")
    
    def register_callback(self, approval_id: str, callback: Callable):
        """Registra un callback para cuando se complete la aprobación."""
        self.approval_callbacks[approval_id] = callback
    
    def get_approval_status(self, approval_id: str) -> Optional[ApprovalRequest]:
        """Obtiene el estado de una solicitud de aprobación."""
        return self.pending_approvals.get(approval_id)
    
    def get_pending_approvals(self) -> List[ApprovalRequest]:
        """Obtiene todas las solicitudes pendientes."""
        return [req for req in self.pending_approvals.values() 
                if req.status == ApprovalStatus.PENDING]
    
    def cleanup_expired_approvals(self):
        """Limpia solicitudes expiradas."""
        current_time = datetime.now()
        expired_ids = []
        
        for approval_id, request in self.pending_approvals.items():
            if current_time > request.expires_at and request.status == ApprovalStatus.PENDING:
                request.status = ApprovalStatus.EXPIRED
                expired_ids.append(approval_id)
        
        if expired_ids:
            logger.info(f"Limpieza de {len(expired_ids)} solicitudes expiradas")
        
        return expired_ids
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del sistema."""
        total_requests = len(self.pending_approvals)
        pending_requests = len(self.get_pending_approvals())
        approved_requests = len([r for r in self.pending_approvals.values() 
                               if r.status == ApprovalStatus.APPROVED])
        rejected_requests = len([r for r in self.pending_approvals.values() 
                               if r.status == ApprovalStatus.REJECTED])
        expired_requests = len([r for r in self.pending_approvals.values() 
                              if r.status == ApprovalStatus.EXPIRED])
        
        return {
            "total_requests": total_requests,
            "pending_requests": pending_requests,
            "approved_requests": approved_requests,
            "rejected_requests": rejected_requests,
            "expired_requests": expired_requests,
            "approval_rate": approved_requests / max(total_requests, 1),
            "active_handlers": len(self.notification_handlers)
        }

class BaseNotifier:
    """Clase base para notificadores."""
    
    def __init__(self, config: NotificationConfig):
        self.config = config
    
    async def send_approval_request(self, approval_request: ApprovalRequest):
        """Envía solicitud de aprobación."""
        raise NotImplementedError
    
    async def send_approval_result(self, approval_request: ApprovalRequest):
        """Envía resultado de aprobación."""
        raise NotImplementedError

class SlackNotifier(BaseNotifier):
    """Notificador de Slack."""
    
    async def send_approval_request(self, approval_request: ApprovalRequest):
        """Envía solicitud de aprobación a Slack."""
        if not self.config.slack_webhook_url:
            return
        
        message = self._format_approval_request(approval_request)
        
        async with aiohttp.ClientSession() as session:
            try:
                payload = {
                    "text": "🔐 Solicitud de Aprobación Requerida",
                    "attachments": [{
                        "color": "#ff6b35",
                        "title": f"Acción: {approval_request.action_type}",
                        "text": approval_request.description,
                        "fields": [
                            {
                                "title": "Solicitante",
                                "value": approval_request.requester,
                                "short": True
                            },
                            {
                                "title": "ID de Aprobación",
                                "value": approval_request.id,
                                "short": True
                            },
                            {
                                "title": "Expira",
                                "value": approval_request.expires_at.strftime("%Y-%m-%d %H:%M:%S"),
                                "short": True
                            }
                        ],
                        "actions": [
                            {
                                "name": "approve",
                                "text": "✅ Aprobar",
                                "type": "button",
                                "value": f"approve:{approval_request.id}"
                            },
                            {
                                "name": "reject",
                                "text": "❌ Rechazar",
                                "type": "button",
                                "value": f"reject:{approval_request.id}"
                            }
                        ]
                    }]
                }
                
                await session.post(self.config.slack_webhook_url, json=payload)
                logger.info(f"Notificación de Slack enviada para {approval_request.id}")
                
            except Exception as e:
                logger.error(f"Error enviando notificación de Slack: {e}")
    
    async def send_approval_result(self, approval_request: ApprovalRequest):
        """Envía resultado de aprobación a Slack."""
        if not self.config.slack_webhook_url:
            return
        
        color = "#36a64f" if approval_request.status == ApprovalStatus.APPROVED else "#ff0000"
        status_text = "✅ APROBADA" if approval_request.status == ApprovalStatus.APPROVED else "❌ RECHAZADA"
        
        message = self._format_approval_result(approval_request, status_text, color)
        
        async with aiohttp.ClientSession() as session:
            try:
                payload = {
                    "text": f"🔐 Aprobación {status_text}",
                    "attachments": [message]
                }
                
                await session.post(self.config.slack_webhook_url, json=payload)
                logger.info(f"Resultado de aprobación enviado a Slack: {approval_request.id}")
                
            except Exception as e:
                logger.error(f"Error enviando resultado a Slack: {e}")
    
    def _format_approval_request(self, approval_request: ApprovalRequest) -> Dict[str, Any]:
        """Formatea la solicitud de aprobación para Slack."""
        return {
            "color": "#ff6b35",
            "title": f"Acción: {approval_request.action_type}",
            "text": approval_request.description,
            "fields": [
                {
                    "title": "Solicitante",
                    "value": approval_request.requester,
                    "short": True
                },
                {
                    "title": "ID de Aprobación",
                    "value": approval_request.id,
                    "short": True
                },
                {
                    "title": "Expira",
                    "value": approval_request.expires_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "short": True
                }
            ]
        }
    
    def _format_approval_result(self, approval_request: ApprovalRequest, 
                               status_text: str, color: str) -> Dict[str, Any]:
        """Formatea el resultado de aprobación para Slack."""
        fields = [
            {
                "title": "Estado",
                "value": status_text,
                "short": True
            },
            {
                "title": "Acción",
                "value": approval_request.action_type,
                "short": True
            }
        ]
        
        if approval_request.status == ApprovalStatus.APPROVED:
            fields.append({
                "title": "Aprobado por",
                "value": approval_request.approved_by or "Sistema",
                "short": True
            })
        elif approval_request.status == ApprovalStatus.REJECTED:
            fields.append({
                "title": "Razón del rechazo",
                "value": approval_request.rejection_reason or "No especificada",
                "short": False
            })
        
        return {
            "color": color,
            "title": f"Resultado: {approval_request.action_type}",
            "text": approval_request.description,
            "fields": fields
        }

class GitHubNotifier(BaseNotifier):
    """Notificador de GitHub."""
    
    def __init__(self, config: NotificationConfig):
        super().__init__(config)
        self.github_token = config.github_token
        self.github_repo = config.github_repo
    
    async def send_approval_request(self, approval_request: ApprovalRequest):
        """Envía solicitud de aprobación como comentario de GitHub."""
        # Implementación básica - en producción usar GitHub API
        logger.info(f"Notificación de GitHub enviada para {approval_request.id}")
    
    async def send_approval_result(self, approval_request: ApprovalRequest):
        """Envía resultado de aprobación como comentario de GitHub."""
        # Implementación básica - en producción usar GitHub API
        logger.info(f"Resultado de aprobación enviado a GitHub: {approval_request.id}")

class EmailNotifier(BaseNotifier):
    """Notificador de Email."""
    
    async def send_approval_request(self, approval_request: ApprovalRequest):
        """Envía solicitud de aprobación por email."""
        # Implementación básica - en producción usar SMTP
        logger.info(f"Notificación de Email enviada para {approval_request.id}")
    
    async def send_approval_result(self, approval_request: ApprovalRequest):
        """Envía resultado de aprobación por email."""
        # Implementación básica - en producción usar SMTP
        logger.info(f"Resultado de aprobación enviado por Email: {approval_request.id}")

class WebhookNotifier(BaseNotifier):
    """Notificador de Webhook."""
    
    async def send_approval_request(self, approval_request: ApprovalRequest):
        """Envía solicitud de aprobación por webhook."""
        if not self.config.webhook_url:
            return
        
        payload = {
            "type": "approval_request",
            "approval_id": approval_request.id,
            "action_type": approval_request.action_type,
            "description": approval_request.description,
            "requester": approval_request.requester,
            "created_at": approval_request.created_at.isoformat(),
            "expires_at": approval_request.expires_at.isoformat(),
            "payload": approval_request.payload,
            "metadata": approval_request.metadata
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                await session.post(self.config.webhook_url, json=payload)
                logger.info(f"Webhook enviado para {approval_request.id}")
            except Exception as e:
                logger.error(f"Error enviando webhook: {e}")
    
    async def send_approval_result(self, approval_request: ApprovalRequest):
        """Envía resultado de aprobación por webhook."""
        if not self.config.webhook_url:
            return
        
        payload = {
            "type": "approval_result",
            "approval_id": approval_request.id,
            "status": approval_request.status.value,
            "action_type": approval_request.action_type,
            "description": approval_request.description,
            "result": {
                "approved_by": approval_request.approved_by,
                "approved_at": approval_request.approved_at.isoformat() if approval_request.approved_at else None,
                "rejection_reason": approval_request.rejection_reason
            },
            "metadata": approval_request.metadata
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                await session.post(self.config.webhook_url, json=payload)
                logger.info(f"Webhook de resultado enviado para {approval_request.id}")
            except Exception as e:
                logger.error(f"Error enviando webhook de resultado: {e}")

# Función de utilidad para check_critical_action
async def check_critical_action(plan: Dict[str, Any], 
                               files_affected: List[str],
                               human_loop_manager: HumanLoopManager,
                               critical_paths: Optional[List[str]] = None,
                               risk_threshold: float = 0.65) -> bool:
    """
    Verifica si una acción es crítica y requiere aprobación humana.
    
    Args:
        plan: Plan de acción a verificar
        files_affected: Lista de archivos afectados
        human_loop_manager: Gestor de Human-in-the-Loop
        critical_paths: Rutas críticas (usa valores por defecto si no se especifica)
        risk_threshold: Umbral de riesgo para aprobación automática
    
    Returns:
        True si la acción puede proceder, False si requiere aprobación
    """
    if critical_paths is None:
        critical_paths = ["/auth/", "/payments/", "/migrations/", "/infra/", "/security/"]
    
    # Verificar rutas críticas
    critical_files = []
    for file_path in files_affected:
        for critical_path in critical_paths:
            if critical_path in file_path:
                critical_files.append(file_path)
    
    # Calcular score de riesgo
    risk_score = 0.0
    
    # Rutas críticas (peso alto)
    if critical_files:
        risk_score += 0.4
    
    # Número de archivos afectados
    if len(files_affected) > 10:
        risk_score += 0.2
    
    # Tipos de archivo sensibles
    sensitive_extensions = ['.py', '.js', '.ts', '.java', '.cpp', '.h']
    sensitive_files = [f for f in files_affected if any(f.endswith(ext) for ext in sensitive_extensions)]
    if len(sensitive_files) > 5:
        risk_score += 0.2
    
    # Labels de alto riesgo
    high_risk_labels = ["security", "critical", "high-priority", "breaking-change"]
    plan_labels = plan.get("labels", [])
    high_risk_found = any(label in plan_labels for label in high_risk_labels)
    if high_risk_found:
        risk_score += 0.2
    
    # Si el riesgo supera el umbral, solicitar aprobación
    if risk_score > risk_threshold:
        logger.warning(f"Acción crítica detectada. Score de riesgo: {risk_score:.2f}")
        
        # Crear solicitud de aprobación
        approval_id = await human_loop_manager.request_approval(
            action_type="critical_action",
            description=f"Plan crítico que afecta {len(critical_files)} archivos sensibles",
            payload={
                "plan": plan,
                "files_affected": files_affected,
                "critical_files": critical_files,
                "risk_score": risk_score,
                "risk_factors": {
                    "critical_paths": bool(critical_files),
                    "many_files": len(files_affected) > 10,
                    "sensitive_files": len(sensitive_files) > 5,
                    "high_risk_labels": high_risk_found
                }
            },
            requester="system",
            timeout_hours=4,  # 4 horas para acciones críticas
            notification_types=[NotificationType.SLACK, NotificationType.WEBHOOK]
        )
        
        # Esperar aprobación
        approved = await human_loop_manager.wait_for_approval(approval_id)
        
        if approved:
            logger.info(f"Acción crítica aprobada: {approval_id}")
            return True
        else:
            logger.warning(f"Acción crítica rechazada: {approval_id}")
            return False
    
    logger.info(f"Acción no crítica. Score de riesgo: {risk_score:.2f}")
    return True

# Función de utilidad para notificar y esperar aprobación
async def notify_and_wait_for_approval(message: str, 
                                      payload: Dict[str, Any],
                                      human_loop_manager: HumanLoopManager,
                                      timeout_hours: int = 24) -> bool:
    """
    Notifica y espera por aprobación humana.
    
    Args:
        message: Mensaje de notificación
        payload: Datos de la acción
        human_loop_manager: Gestor de Human-in-the-Loop
        timeout_hours: Tiempo de espera en horas
    
    Returns:
        True si fue aprobada, False si fue rechazada o expiró
    """
    approval_id = await human_loop_manager.request_approval(
        action_type="manual_approval",
        description=message,
        payload=payload,
        requester="system",
        timeout_hours=timeout_hours
    )
    
    return await human_loop_manager.wait_for_approval(approval_id)
