"""
Subagente de Síntesis - Generación de Respuestas
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import asyncio

logger = logging.getLogger(__name__)

class SynthesisSubAgent:
    """
    Subagente especializado en crear respuestas coherentes y bien estructuradas
    basadas en el contrato de tarea, el análisis de chunks y la consulta del usuario.
    """
    
    def __init__(self, llm_client=None):
        """
        Inicializa el subagente de síntesis.
        
        Args:
            llm_client: Cliente LLM para generación de respuestas
        """
        self.llm_client = llm_client
        self.logger = logging.getLogger(__name__)
        self.logger.info("SynthesisSubAgent inicializado")
        
        # Cargar plantillas de prompts
        self.prompts_dir = Path(__file__).parent.parent / "prompts"
        self.synthesis_prompt = self._load_synthesis_prompt()
    
    def _load_synthesis_prompt(self) -> str:
        """Carga la plantilla de prompt para síntesis."""
        try:
            prompt_file = self.prompts_dir / "synthesis.md"
            if prompt_file.exists():
                with open(prompt_file, "r", encoding="utf-8") as f:
                    return f.read()
            else:
                self.logger.warning("Archivo de prompt synthesis.md no encontrado")
                return self._get_default_synthesis_prompt()
        except Exception as e:
            self.logger.error(f"Error al cargar prompt de síntesis: {e}")
            return self._get_default_synthesis_prompt()
    
    def _get_default_synthesis_prompt(self) -> str:
        """Retorna un prompt de síntesis por defecto."""
        return """
        Eres un experto en síntesis de información técnica. Tu tarea es crear respuestas claras, 
        accionables y bien documentadas siguiendo estrictamente el contrato de tarea.
        
        Reglas críticas:
        1. NUNCA inventes información que no esté en las fuentes
        2. SIEMPRE cita las fuentes con el formato especificado
        3. SIGUE estrictamente la estructura del contrato
        4. MANTÉN la respuesta dentro de los límites de tokens
        5. INCLUYE la sección "Fuentes" obligatoria
        """
    
    async def write(self, contract: Dict[str, Any], analysis: Dict[str, Any], 
                   query: str, context: str) -> str:
        """
        Genera una respuesta basada en el contrato, análisis y contexto.
        
        Args:
            contract: Contrato de tarea
            analysis: Análisis de chunks
            query: Consulta del usuario
            context: Contexto recuperado y compactado
        
        Returns:
            Respuesta generada
        """
        self.logger.info("Iniciando síntesis de respuesta")
        
        # Preparar prompt de síntesis
        synthesis_prompt = self._prepare_synthesis_prompt(contract, analysis, query, context)
        
        # Generar respuesta
        if self.llm_client:
            try:
                response = await self._generate_with_llm(synthesis_prompt, contract)
                self.logger.info("Respuesta generada con LLM")
                return response
            except Exception as e:
                self.logger.error(f"Error en generación con LLM: {e}")
                return self._generate_fallback_response(contract, analysis, query, context)
        else:
            # Fallback sin LLM
            return self._generate_fallback_response(contract, analysis, query, context)
    
    def _prepare_synthesis_prompt(self, contract: Dict[str, Any], analysis: Dict[str, Any], 
                                 query: str, context: str) -> str:
        """
        Prepara el prompt completo para la síntesis.
        
        Args:
            contract: Contrato de tarea
            analysis: Análisis de chunks
            query: Consulta del usuario
            context: Contexto recuperado
        
        Returns:
            Prompt completo para síntesis
        """
        # Construir prompt estructurado
        prompt_parts = [
            "# PROMPT DE SÍNTESIS",
            "",
            "## CONTRATO DE TAREA",
            f"**Objetivo**: {contract.get('goal', 'Responder la consulta')}",
            f"**Formato**: {contract.get('format', 'Markdown estructurado')}",
            "",
            "## REQUISITOS OBLIGATORIOS",
        ]
        
        # Agregar requisitos del contrato
        for req in contract.get('musts', []):
            prompt_parts.append(f"- {req}")
        
        # Agregar análisis de chunks
        if analysis:
            prompt_parts.extend([
                "",
                "## ANÁLISIS DE CHUNKS",
                f"**Clasificación**: {analysis.get('summary', 'No disponible')}",
                f"**Plan de Uso**: {analysis.get('usage_plan', {}).get('suggested_structure', 'Estructura general')}",
            ])
        
        # Agregar contexto
        prompt_parts.extend([
            "",
            "## CONTEXTO RECUPERADO",
            context,
            "",
            "## CONSULTA DEL USUARIO",
            query,
            "",
            "## INSTRUCCIONES",
            self.synthesis_prompt,
            "",
            "Genera ahora la respuesta siguiendo estrictamente el contrato y usando solo la información del contexto."
        ])
        
        return "\n".join(prompt_parts)
    
    async def _generate_with_llm(self, prompt: str, contract: Dict[str, Any]) -> str:
        """
        Genera respuesta usando el LLM.
        
        Args:
            prompt: Prompt completo para síntesis
            contract: Contrato de tarea
        
        Returns:
            Respuesta generada
        """
        try:
            # Configurar parámetros según el contrato
            max_tokens = contract.get('metrics', {}).get('max_tokens', 800)
            temperature = 0.3  # Baja temperatura para respuestas consistentes
            
            # Generar respuesta
            if hasattr(self.llm_client, 'achat_completion'):
                # OpenAI async
                response = await self.llm_client.achat_completion(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": "Genera la respuesta ahora."}
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                return response.choices[0].message.content
            elif hasattr(self.llm_client, 'generate'):
                # Otros clientes LLM
                response = self.llm_client.generate(
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                return response.text
            else:
                raise NotImplementedError("Cliente LLM no compatible")
                
        except Exception as e:
            self.logger.error(f"Error en generación con LLM: {e}")
            raise
    
    def _generate_fallback_response(self, contract: Dict[str, Any], analysis: Dict[str, Any], 
                                  query: str, context: str) -> str:
        """
        Genera una respuesta de fallback sin LLM.
        
        Args:
            contract: Contrato de tarea
            analysis: Análisis de chunks
            query: Consulta del usuario
            context: Contexto recuperado
        
        Returns:
            Respuesta de fallback
        """
        self.logger.warning("Generando respuesta de fallback sin LLM")
        
        # Crear respuesta básica basada en el contrato
        response_parts = []
        
        # Encabezado
        response_parts.append(f"# Respuesta a: {query}")
        response_parts.append("")
        
        # Advertencia sobre método de fallback
        response_parts.append("⚠️ **Nota**: Esta respuesta fue generada usando el método de fallback.")
        response_parts.append("")
        
        # Información del contrato
        response_parts.append("## Información del Contrato")
        response_parts.append(f"- **Objetivo**: {contract.get('goal', 'No especificado')}")
        response_parts.append(f"- **Formato**: {contract.get('format', 'No especificado')}")
        response_parts.append("")
        
        # Análisis disponible
        if analysis:
            response_parts.append("## Análisis Disponible")
            response_parts.append(analysis.get('summary', 'No disponible'))
            response_parts.append("")
        
        # Contexto recuperado (resumido)
        response_parts.append("## Contexto Recuperado")
        context_lines = context.split('\n')[:10]  # Primeras 10 líneas
        response_parts.extend(context_lines)
        if len(context.split('\n')) > 10:
            response_parts.append("... (contexto truncado)")
        response_parts.append("")
        
        # Sección de fuentes (obligatoria)
        response_parts.append("## Fuentes")
        response_parts.append("- [Contexto Recuperado]: Información extraída de la base de conocimiento")
        response_parts.append("")
        
        # Advertencia sobre limitaciones
        response_parts.append("## Limitaciones")
        response_parts.append("Esta respuesta de fallback puede no cumplir completamente con todos los requisitos del contrato.")
        response_parts.append("Se recomienda usar el LLM para respuestas completas y precisas.")
        
        return "\n".join(response_parts)
    
    async def revise(self, draft: str, feedback: List[str], contract: Dict[str, Any]) -> str:
        """
        Revisa y mejora una respuesta basada en feedback.
        
        Args:
            draft: Respuesta inicial
            feedback: Lista de problemas detectados
            contract: Contrato de tarea
        
        Returns:
            Respuesta revisada
        """
        self.logger.info(f"Revisando respuesta con {len(feedback)} problemas detectados")
        
        # Crear prompt de revisión
        revision_prompt = self._prepare_revision_prompt(draft, feedback, contract)
        
        # Generar versión revisada
        if self.llm_client:
            try:
                revised_response = await self._generate_with_llm(revision_prompt, contract)
                self.logger.info("Respuesta revisada generada")
                return revised_response
            except Exception as e:
                self.logger.error(f"Error en revisión con LLM: {e}")
                return self._revise_fallback(draft, feedback, contract)
        else:
            return self._revise_fallback(draft, feedback, contract)
    
    def _prepare_revision_prompt(self, draft: str, feedback: List[str], 
                                contract: Dict[str, Any]) -> str:
        """
        Prepara el prompt para revisión de respuesta.
        
        Args:
            draft: Respuesta inicial
            feedback: Lista de problemas detectados
            contract: Contrato de tarea
        
        Returns:
            Prompt para revisión
        """
        feedback_text = "\n".join(f"- {issue}" for issue in feedback)
        
        return f"""
        # REVISIÓN DE RESPUESTA
        
        ## CONTRATO ORIGINAL
        {contract.get('goal', 'No especificado')}
        
        ## PROBLEMAS DETECTADOS
        {feedback_text}
        
        ## RESPUESTA ACTUAL
        {draft}
        
        ## INSTRUCCIONES DE REVISIÓN
        Corrige todos los problemas detectados y asegúrate de que la respuesta cumpla completamente con el contrato.
        Mantén la estructura y contenido original, solo corrige los problemas específicos.
        
        Genera la respuesta revisada ahora.
        """
    
    def _revise_fallback(self, draft: str, feedback: List[str], contract: Dict[str, Any]) -> str:
        """
        Revisa la respuesta usando método de fallback.
        
        Args:
            draft: Respuesta inicial
            feedback: Lista de problemas detectados
            contract: Contrato de tarea
        
        Returns:
            Respuesta revisada
        """
        self.logger.warning("Revisando respuesta usando método de fallback")
        
        # Agregar advertencia sobre problemas detectados
        revision_parts = [draft]
        revision_parts.append("")
        revision_parts.append("---")
        revision_parts.append("## PROBLEMAS DETECTADOS (NO CORREGIDOS)")
        for issue in feedback:
            revision_parts.append(f"- {issue}")
        revision_parts.append("")
        revision_parts.append("⚠️ **Nota**: Esta respuesta requiere revisión manual para corregir los problemas detectados.")
        
        return "\n".join(revision_parts)
    
    def validate_response(self, response: str, contract: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida que la respuesta cumpla con el contrato.
        
        Args:
            response: Respuesta generada
            contract: Contrato de tarea
        
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
        if "## Fuentes" in response or "### Fuentes" in response:
            validation["passed_checks"].append("Sección Fuentes presente")
            validation["compliance_score"] += 0.3
        else:
            validation["violations"].append("Falta sección 'Fuentes' obligatoria")
        
        # Verificar citas con formato correcto
        import re
        citation_pattern = r'\[([^\]]+)\]\(línea\s+\d+-\d+\)'
        citations = re.findall(citation_pattern, response)
        if citations:
            validation["passed_checks"].append(f"Citas encontradas: {len(citations)}")
            validation["compliance_score"] += 0.3
        else:
            validation["warnings"].append("No se encontraron citas con formato estándar")
        
        # Verificar longitud aproximada
        estimated_tokens = len(response.split()) * 1.3
        max_tokens = contract.get('metrics', {}).get('max_tokens', 800)
        if estimated_tokens <= max_tokens:
            validation["passed_checks"].append("Longitud dentro del límite")
            validation["compliance_score"] += 0.2
        else:
            validation["warnings"].append(f"Respuesta puede exceder límite de {max_tokens} tokens")
        
        # Verificar estructura según tipo de consulta
        if "pasos" in contract.get('format', '').lower():
            if any(word in response.lower() for word in ["1.", "2.", "3.", "paso"]):
                validation["passed_checks"].append("Estructura de pasos presente")
                validation["compliance_score"] += 0.2
            else:
                validation["warnings"].append("Estructura de pasos no detectada")
        
        # Normalizar score
        validation["compliance_score"] = min(1.0, validation["compliance_score"])
        
        return validation
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas del subagente."""
        return {
            "agent_type": "SynthesisSubAgent",
            "llm_available": self.llm_client is not None,
            "prompt_loaded": bool(self.synthesis_prompt),
            "capabilities": [
                "Generación de respuestas",
                "Revisión de respuestas",
                "Validación de cumplimiento",
                "Fallback sin LLM"
            ]
        }
