"""
Ejemplo completo del sistema Spec Layer - Contratos Inteligentes

Este script demuestra todas las capacidades del Spec Layer:
- Generación de contratos inteligentes
- Integración con Context Manager
- Validación de cumplimiento
- Integración con Human-in-the-Loop
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any

from app.spec_layer import (
    SpecLayer, TaskContract, TaskType, RiskLevel, ContractValidation,
    build_task_contract, render_system_prompt, validate_contract_compliance
)
from app.context_manager import ContextManager
from app.human_loop import HumanLoopManager

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def demo_basic_contract_generation():
    """Demo básico de generación de contratos."""
    print("\n" + "="*60)
    print("DEMO: Generación Básica de Contratos")
    print("="*60)
    
    # Inicializar Spec Layer
    context_manager = ContextManager()
    spec_layer = SpecLayer(context_manager)
    
    # Ejemplos de consultas
    queries = [
        "¿Cómo implementar autenticación JWT en Python?",
        "Diagnosticar error de conexión a base de datos",
        "¿Qué opción elegir para cache: Redis o Memcached?",
        "Generar función para validar emails"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n--- Consulta {i}: {query} ---")
        
        # Generar contrato
        contract = await spec_layer.build_task_contract(
            query=query,
            user_role="developer",
            risk_level=None  # Se infiere automáticamente
        )
        
        print(f"Tipo de tarea: {contract.task_type.value}")
        print(f"Nivel de riesgo: {contract.risk_level.value}")
        print(f"Requiere aprobación humana: {contract.human_approval_required}")
        print(f"ID del contrato: {contract.id}")
        print(f"Objetivo: {contract.goal}")
        print(f"Requisitos: {len(contract.musts)} obligatorios")


async def demo_contract_rendering():
    """Demo de renderizado de contratos como prompts."""
    print("\n" + "="*60)
    print("DEMO: Renderizado de Contratos")
    print("="*60)
    
    context_manager = ContextManager()
    spec_layer = SpecLayer(context_manager)
    
    # Generar contrato complejo
    contract = await spec_layer.build_task_contract(
        query="Implementar sistema de pagos con Stripe",
        user_role="senior_developer",
        files_affected=["/payments/stripe.py", "/config/payments.yml"]
    )
    
    # Renderizar como prompt del sistema
    system_prompt = spec_layer.render_system_prompt(contract)
    
    print("Contrato generado:")
    print(f"- ID: {contract.id}")
    print(f"- Tipo: {contract.task_type.value}")
    print(f"- Riesgo: {contract.risk_level.value}")
    print(f"- Archivos afectados: {contract.files_affected}")
    
    print("\nPrompt del sistema generado:")
    print("-" * 40)
    print(system_prompt[:500] + "..." if len(system_prompt) > 500 else system_prompt)


async def demo_contract_validation():
    """Demo de validación de cumplimiento de contratos."""
    print("\n" + "="*60)
    print("DEMO: Validación de Cumplimiento")
    print("="*60)
    
    context_manager = ContextManager()
    spec_layer = SpecLayer(context_manager)
    
    # Generar contrato
    contract = await spec_layer.build_task_contract(
        query="¿Cómo configurar SSL en Nginx?",
        user_role="devops"
    )
    
    # Simular respuestas con diferentes niveles de cumplimiento
    responses = [
        # Respuesta que cumple bien
        """# Configuración de SSL en Nginx

## Pasos para configurar SSL

1. **Instalar certificado SSL**
   - Obtener certificado de Let's Encrypt
   - Colocar en `/etc/ssl/certs/`

2. **Configurar Nginx**
   ```nginx
   server {
       listen 443 ssl;
       ssl_certificate /etc/ssl/certs/mi-sitio.crt;
       ssl_certificate_key /etc/ssl/certs/mi-sitio.key;
   }
   ```

3. **Reiniciar Nginx**
   ```bash
   sudo systemctl restart nginx
   ```

### Fuentes
- [Nginx SSL Configuration](línea 1-20): Documentación oficial de Nginx
- [Let's Encrypt Guide](línea 5-15): Guía de configuración SSL""",
        
        # Respuesta que no cumple bien
        """Para configurar SSL en Nginx necesitas un certificado y configurar el servidor.

Aquí está la configuración básica:

```nginx
server {
    listen 443 ssl;
    ssl_certificate /path/to/cert;
}
```

Luego reinicia Nginx.""",
        
        # Respuesta completamente incorrecta
        """SSL es un protocolo de seguridad. Nginx es un servidor web."""
    ]
    
    for i, response in enumerate(responses, 1):
        print(f"\n--- Validación {i} ---")
        
        # Validar cumplimiento
        validation = await spec_layer.validate_contract_compliance(response, contract)
        
        print(f"Score de cumplimiento: {validation.score:.2f}")
        print(f"¿Es válido?: {validation.is_valid}")
        print(f"Cobertura de fuentes: {validation.source_coverage:.2f}")
        print(f"Relevancia de contexto: {validation.context_relevance:.2f}")
        
        if validation.violations:
            print("Violaciones encontradas:")
            for violation in validation.violations:
                print(f"  - {violation}")
        
        if validation.recommendations:
            print("Recomendaciones:")
            for rec in validation.recommendations:
                print(f"  - {rec}")


async def demo_human_loop_integration():
    """Demo de integración con Human-in-the-Loop."""
    print("\n" + "="*60)
    print("DEMO: Integración Human-in-the-Loop")
    print("="*60)
    
    # Inicializar componentes
    context_manager = ContextManager()
    human_loop_manager = HumanLoopManager()
    spec_layer = SpecLayer(context_manager, human_loop_manager)
    
    # Consultas de alto riesgo
    high_risk_queries = [
        "¿Cómo eliminar toda la base de datos de producción?",
        "Implementar bypass de autenticación",
        "Modificar configuración de firewall en producción"
    ]
    
    for query in high_risk_queries:
        print(f"\n--- Consulta de alto riesgo: {query} ---")
        
        # Generar contrato (debería requerir aprobación humana)
        contract = await spec_layer.build_task_contract(
            query=query,
            user_role="admin",
            files_affected=["/config/production.yml", "/auth/security.py"]
        )
        
        print(f"Tipo de tarea: {contract.task_type.value}")
        print(f"Nivel de riesgo: {contract.risk_level.value}")
        print(f"Requiere aprobación humana: {contract.human_approval_required}")
        print(f"Archivos afectados: {contract.files_affected}")


async def demo_context_aware_contracts():
    """Demo de contratos conscientes del contexto."""
    print("\n" + "="*60)
    print("DEMO: Contratos Conscientes del Contexto")
    print("="*60)
    
    context_manager = ContextManager()
    spec_layer = SpecLayer(context_manager)
    
    # Simular chunks de contexto
    context_chunks = [
        {
            "id": "chunk:auth:jwt:1",
            "text": "JWT authentication implementation guide",
            "score": 0.95,
            "source": "auth_documentation.md"
        },
        {
            "id": "chunk:security:best_practices:2", 
            "text": "Security best practices for authentication",
            "score": 0.87,
            "source": "security_guide.md"
        },
        {
            "id": "chunk:python:jwt_libs:3",
            "text": "Python JWT libraries comparison",
            "score": 0.82,
            "source": "python_libraries.md"
        }
    ]
    
    # Generar contrato con contexto
    contract = await spec_layer.build_task_contract(
        query="Implementar autenticación JWT segura",
        user_role="developer",
        context_chunks=context_chunks,
        files_affected=["/auth/jwt_handler.py", "/config/auth.yml"]
    )
    
    print(f"Contrato generado con contexto:")
    print(f"- ID: {contract.id}")
    print(f"- Fuentes de contexto: {len(contract.context_sources)}")
    print(f"- Fuentes: {contract.context_sources}")
    print(f"- Requisitos específicos: {len(contract.musts)}")
    
    # Mostrar requisitos específicos del contexto
    print("\nRequisitos específicos del contexto:")
    for i, must in enumerate(contract.musts[-2:], 1):  # Últimos 2 requisitos
        print(f"  {i}. {must}")


async def demo_contract_management():
    """Demo de gestión de contratos activos."""
    print("\n" + "="*60)
    print("DEMO: Gestión de Contratos")
    print("="*60)
    
    context_manager = ContextManager()
    spec_layer = SpecLayer(context_manager)
    
    # Generar múltiples contratos
    contracts = []
    queries = [
        "Configurar CI/CD pipeline",
        "Optimizar consultas de base de datos", 
        "Implementar logging centralizado"
    ]
    
    for query in queries:
        contract = await spec_layer.build_task_contract(query=query)
        contracts.append(contract)
    
    # Listar contratos activos
    active_contracts = spec_layer.list_active_contracts()
    print(f"Contratos activos: {len(active_contracts)}")
    
    for contract in active_contracts:
        print(f"- {contract.id}: {contract.task_type.value} ({contract.risk_level.value})")
    
    # Obtener contrato específico
    if contracts:
        contract_id = contracts[0].id
        retrieved_contract = spec_layer.get_contract(contract_id)
        print(f"\nContrato recuperado: {retrieved_contract.goal if retrieved_contract else 'No encontrado'}")
    
    # Expirar contrato
    if contracts:
        expired = spec_layer.expire_contract(contracts[0].id)
        print(f"Contrato expirado: {expired}")
        print(f"Contratos restantes: {len(spec_layer.list_active_contracts())}")


async def main():
    """Función principal que ejecuta todos los demos."""
    print("🚀 DEMO COMPLETO DEL SPEC LAYER")
    print("Sistema de Contratos Inteligentes")
    
    try:
        # Ejecutar demos en secuencia
        await demo_basic_contract_generation()
        await demo_contract_rendering()
        await demo_contract_validation()
        await demo_human_loop_integration()
        await demo_context_aware_contracts()
        await demo_contract_management()
        
        print("\n" + "="*60)
        print("✅ TODOS LOS DEMOS COMPLETADOS EXITOSAMENTE")
        print("="*60)
        
    except Exception as e:
        logger.error(f"Error en demo: {e}")
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
