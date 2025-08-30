from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from textwrap import dedent
import re

@dataclass
class TaskContract:
    """Contrato que define los objetivos, restricciones y formato de salida para una tarea."""
    goal: str
    musts: List[str]
    format: str
    metrics: Dict[str, Any]
    risk_level: str = "medium"
    user_role: str = "developer"

def build_task_contract(query: str, user_role: str = "developer", risk_level: str = "medium") -> TaskContract:
    """
    Genera un contrato de tarea basado en la consulta, rol del usuario y nivel de riesgo.
    
    Args:
        query: La consulta del usuario
        user_role: Rol del usuario (developer, analyst, manager, etc.)
        risk_level: Nivel de riesgo (low, medium, high)
    
    Returns:
        TaskContract configurado para la consulta
    """
    # Detectar tipo de consulta
    query_lower = query.lower()
    
    if any(word in query_lower for word in ["cómo", "pasos", "proceso", "workflow"]):
        task_type = "procedural"
        format_spec = "Markdown con pasos numerados y accionables"
        musts = [
            "Usar solo pasajes recuperados y citarlos",
            "Limitar a 3-5 chunks relevantes",
            "Indicar suposiciones explícitas",
            "Incluir sección 'Fuentes' con título de doc y línea",
            "Proporcionar pasos secuenciales y verificables"
        ]
    elif any(word in query_lower for word in ["diagnóstico", "problema", "error", "bug"]):
        task_type = "diagnostic"
        format_spec = "Markdown con análisis estructurado y recomendaciones"
        musts = [
            "Usar solo pasajes recuperados y citarlos",
            "Limitar a 3-5 chunks relevantes",
            "Indicar suposiciones explícitas",
            "Incluir sección 'Fuentes' con título de doc y línea",
            "Identificar causa raíz y posibles soluciones",
            "Incluir nivel de confianza en el diagnóstico"
        ]
    elif any(word in query_lower for word in ["decisión", "elección", "recomendación", "opción"]):
        task_type = "decision"
        format_spec = "Markdown con análisis de opciones y justificación"
        musts = [
            "Usar solo pasajes recuperados y citarlos",
            "Limitar a 3-5 chunks relevantes",
            "Indicar suposiciones explícitas",
            "Incluir sección 'Fuentes' con título de doc y línea",
            "Presentar opciones con pros y contras",
            "Recomendar basado en evidencia del contexto"
        ]
    elif any(word in query_lower for word in ["código", "implementación", "ejemplo", "snippet"]):
        task_type = "code"
        format_spec = "Markdown con código comentado y explicación"
        musts = [
            "Usar solo pasajes recuperados y citarlos",
            "Limitar a 3-5 chunks relevantes",
            "Indicar suposiciones explícitas",
            "Incluir sección 'Fuentes' con título de doc y línea",
            "Proporcionar código funcional y bien comentado",
            "Explicar la lógica y consideraciones de implementación"
        ]
    else:
        task_type = "general"
        format_spec = "Markdown breve y estructurado"
        musts = [
            "Usar solo pasajes recuperados y citarlos",
            "Limitar a 3-5 chunks relevantes",
            "Indicar suposiciones explícitas",
            "Incluir sección 'Fuentes' con título de doc y línea"
        ]
    
    # Ajustar requisitos según rol y riesgo
    if user_role == "manager":
        musts.append("Incluir resumen ejecutivo al inicio")
        musts.append("Destacar impactos y riesgos")
    
    if risk_level == "high":
        musts.append("Validar todas las afirmaciones con múltiples fuentes")
        musts.append("Incluir advertencias sobre limitaciones")
    
    # Configurar métricas según tipo de tarea
    if task_type == "procedural":
        metrics = {"precision_target": 0.95, "max_tokens": 1000, "steps_min": 3}
    elif task_type == "diagnostic":
        metrics = {"precision_target": 0.9, "max_tokens": 1200, "confidence_threshold": 0.7}
    elif task_type == "decision":
        metrics = {"precision_target": 0.85, "max_tokens": 1000, "options_min": 2}
    elif task_type == "code":
        metrics = {"precision_target": 0.9, "max_tokens": 1500, "code_quality": "high"}
    else:
        metrics = {"precision_target": 0.9, "max_tokens": 800}
    
    return TaskContract(
        goal=f"Responder la consulta: {query}",
        musts=musts,
        format=format_spec,
        metrics=metrics,
        risk_level=risk_level,
        user_role=user_role
    )

def render_system_prompt(contract: TaskContract) -> str:
    """
    Convierte el contrato a un prompt de sistema estructurado.
    
    Args:
        contract: El contrato de tarea
    
    Returns:
        Prompt del sistema en formato string
    """
    musts = "\n".join(f"- {m}" for m in contract.musts)
    
    # Ajustar formato según el tipo de tarea
    format_instructions = contract.format
    if "pasos" in contract.format.lower():
        format_instructions += "\n\nEstructura esperada:\n1. Resumen ejecutivo\n2. Pasos detallados\n3. Consideraciones\n4. Fuentes"
    elif "diagnóstico" in contract.format.lower():
        format_instructions += "\n\nEstructura esperada:\n1. Síntomas identificados\n2. Análisis de causa raíz\n3. Soluciones recomendadas\n4. Fuentes"
    
    return dedent(f"""
    # CONTRATO DE TAREA - SISTEMA DE DIAGNÓSTICO CON IA
    
    ## OBJETIVO
    {contract.goal}
    
    ## REQUISITOS OBLIGATORIOS
    {musts}
    
    ## FORMATO DE SALIDA
    {format_instructions}
    
    ## MÉTRICAS Y LÍMITES
    - Precisión objetivo: {contract.metrics.get('precision_target', 0.9)}
    - Máximo tokens: {contract.metrics.get('max_tokens', 800)}
    - Nivel de riesgo: {contract.risk_level.upper()}
    - Rol del usuario: {contract.user_role}
    
    ## REGLAS CRÍTICAS
    1. NUNCA inventes información que no esté en las fuentes
    2. SIEMPRE cita las fuentes con formato [Título del Doc](línea X-Y)
    3. Si no hay suficiente contexto, indica "INSUFICIENTE CONTEXTO" y sugiere qué buscar
    4. Mantén respuestas concisas pero completas
    5. Usa Markdown para estructura clara
    
    ## SECCIÓN FUENTES OBLIGATORIA
    Al final de tu respuesta, incluye:
    
    ### Fuentes
    - [Nombre del Documento](línea X-Y): Descripción breve del contenido relevante
    - [Otro Documento](línea A-B): Otra descripción relevante
    
    ---
    Ahora procede con la consulta del usuario siguiendo estrictamente este contrato.
    """)

def validate_contract_compliance(response: str, contract: TaskContract) -> Dict[str, Any]:
    """
    Valida que la respuesta cumpla con el contrato.
    
    Args:
        response: La respuesta generada
        contract: El contrato que debe cumplir
    
    Returns:
        Dict con resultados de validación
    """
    validation = {
        "compliance_score": 0.0,
        "violations": [],
        "warnings": [],
        "passed_checks": []
    }
    
    # Verificar sección Fuentes
    if "### Fuentes" in response or "## Fuentes" in response:
        validation["passed_checks"].append("Sección Fuentes presente")
        validation["compliance_score"] += 0.3
    else:
        validation["violations"].append("Falta sección 'Fuentes' obligatoria")
    
    # Verificar citas con formato correcto
    citation_pattern = r'\[([^\]]+)\]\(línea\s+\d+-\d+\)'
    citations = re.findall(citation_pattern, response)
    if citations:
        validation["passed_checks"].append(f"Citas encontradas: {len(citations)}")
        validation["compliance_score"] += 0.3
    else:
        validation["warnings"].append("No se encontraron citas con formato estándar")
    
    # Verificar suposiciones explícitas
    if "suposición" in response.lower() or "assumption" in response.lower():
        validation["passed_checks"].append("Suposiciones explícitas mencionadas")
        validation["compliance_score"] += 0.2
    else:
        validation["warnings"].append("No se mencionaron suposiciones explícitas")
    
    # Verificar longitud aproximada
    estimated_tokens = len(response.split()) * 1.3  # Aproximación
    max_tokens = contract.metrics.get("max_tokens", 800)
    if estimated_tokens <= max_tokens:
        validation["passed_checks"].append("Longitud dentro del límite")
        validation["compliance_score"] += 0.2
    else:
        validation["warnings"].append(f"Respuesta puede exceder límite de {max_tokens} tokens")
    
    # Normalizar score a 0-1
    validation["compliance_score"] = min(1.0, validation["compliance_score"])
    
    return validation

# Plantillas predefinidas para tipos comunes de consulta
QUERY_TEMPLATES = {
    "procedural": {
        "goal": "Proporcionar pasos claros y accionables",
        "format": "Lista numerada con pasos secuenciales",
        "metrics": {"precision_target": 0.95, "max_tokens": 1000}
    },
    "diagnostic": {
        "goal": "Identificar causa raíz y soluciones",
        "format": "Análisis estructurado con recomendaciones",
        "metrics": {"precision_target": 0.9, "max_tokens": 1200}
    },
    "decision": {
        "goal": "Analizar opciones y recomendar",
        "format": "Comparación de alternativas con justificación",
        "metrics": {"precision_target": 0.85, "max_tokens": 1000}
    },
    "code": {
        "goal": "Proporcionar implementación funcional",
        "format": "Código comentado con explicación",
        "metrics": {"precision_target": 0.9, "max_tokens": 1500}
    }
}
