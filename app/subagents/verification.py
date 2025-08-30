"""
Subagente de Verificación - Validación de Calidad y Cumplimiento
"""

import logging
import re
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class VerificationSubAgent:
    """
    Subagente especializado en verificar que las respuestas generadas cumplan con el contrato
    de tarea y detecte posibles alucinaciones o violaciones.
    """
    
    def __init__(self):
        """Inicializa el subagente de verificación."""
        self.logger = logging.getLogger(__name__)
        self.logger.info("VerificationSubAgent inicializado")
        
        # Checklist de verificación
        self.checklist = [
            "¿Todas las afirmaciones citan fuentes?",
            "¿Las fuentes corresponden a la sección/archivo correcto?",
            "¿Se indicaron suposiciones?",
            "¿Se respetó el formato del contrato?",
            "¿La información es factual y verificable?",
            "¿No hay extrapolaciones no justificadas?",
            "¿La respuesta es consistente internamente?",
            "¿Se incluye la sección 'Fuentes' obligatoria?"
        ]
        
        # Cargar plantilla de prompt
        self.prompts_dir = Path(__file__).parent.parent / "prompts"
        self.verification_prompt = self._load_verification_prompt()
    
    def _load_verification_prompt(self) -> str:
        """Carga la plantilla de prompt para verificación."""
        try:
            prompt_file = self.prompts_dir / "verification.md"
            if prompt_file.exists():
                with open(prompt_file, "r", encoding="utf-8") as f:
                    return f.read()
            else:
                self.logger.warning("Archivo de prompt verification.md no encontrado")
                return self._get_default_verification_prompt()
        except Exception as e:
            self.logger.error(f"Error al cargar prompt de verificación: {e}")
            return self._get_default_verification_prompt()
    
    def _get_default_verification_prompt(self) -> str:
        """Retorna un prompt de verificación por defecto."""
        return """
        Eres un verificador experto que revisa respuestas técnicas para asegurar calidad, 
        precisión y cumplimiento de requisitos.
        
        Reglas críticas:
        1. Sé estricto en la verificación de fuentes
        2. No dudes en rechazar respuestas con alucinaciones
        3. Documenta todos los problemas encontrados
        4. Mantén estándares altos de calidad
        """
    
    def self_check(self, text: str, contract: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Realiza una verificación automática de la respuesta.
        
        Args:
            text: Texto de la respuesta a verificar
            contract: Contrato de tarea (opcional)
        
        Returns:
            Dict con resultados de la verificación automática
        """
        self.logger.info("Iniciando verificación automática")
        
        verification_result = {
            "compliance_score": 0.0,
            "violations": [],
            "warnings": [],
            "passed_checks": [],
            "overall_status": "PENDING"
        }
        
        # Verificar sección Fuentes
        if self._check_sources_section(text):
            verification_result["passed_checks"].append("Sección 'Fuentes' presente")
            verification_result["compliance_score"] += 0.3
        else:
            verification_result["violations"].append("Sin sección 'Fuentes' obligatoria")
        
        # Verificar citas con formato correcto
        citations = self._check_citation_format(text)
        if citations:
            verification_result["passed_checks"].append(f"Citas encontradas: {len(citations)}")
            verification_result["compliance_score"] += 0.3
        else:
            verification_result["warnings"].append("Sin citas con formato estándar")
        
        # Verificar suposiciones explícitas
        if self._check_explicit_assumptions(text):
            verification_result["passed_checks"].append("Suposiciones explícitas mencionadas")
            verification_result["compliance_score"] += 0.2
        else:
            verification_result["warnings"].append("Sin 'Suposiciones' explícitas")
        
        # Verificar longitud (si hay contrato)
        if contract:
            length_check = self._check_response_length(text, contract)
            if length_check["passed"]:
                verification_result["passed_checks"].append("Longitud dentro del límite")
                verification_result["compliance_score"] += 0.2
            else:
                verification_result["warnings"].append(length_check["message"])
        
        # Determinar estado general
        verification_result["overall_status"] = self._determine_overall_status(verification_result)
        
        self.logger.info(f"Verificación automática completada: {verification_result['overall_status']}")
        return verification_result
    
    def _check_sources_section(self, text: str) -> bool:
        """
        Verifica que la respuesta incluya la sección de fuentes.
        
        Args:
            text: Texto de la respuesta
        
        Returns:
            True si la sección está presente
        """
        source_patterns = [
            r"##\s*Fuentes",
            r"###\s*Fuentes",
            r"##\s*Referencias",
            r"###\s*Referencias"
        ]
        
        for pattern in source_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _check_citation_format(self, text: str) -> List[str]:
        """
        Verifica el formato de las citas en la respuesta.
        
        Args:
            text: Texto de la respuesta
        
        Returns:
            Lista de citas encontradas
        """
        # Patrón para citas: [Título](línea X-Y)
        citation_pattern = r'\[([^\]]+)\]\(línea\s+\d+-\d+\)'
        citations = re.findall(citation_pattern, text)
        
        # También buscar citas alternativas
        alt_patterns = [
            r'\[([^\]]+)\]\([^)]+\)',  # [Título](cualquier cosa)
            r'fuente:\s*([^\n]+)',     # fuente: Título
            r'referencia:\s*([^\n]+)'   # referencia: Título
        ]
        
        for pattern in alt_patterns:
            alt_citations = re.findall(pattern, text, re.IGNORECASE)
            citations.extend(alt_citations)
        
        return list(set(citations))  # Eliminar duplicados
    
    def _check_explicit_assumptions(self, text: str) -> bool:
        """
        Verifica que se mencionen suposiciones explícitas.
        
        Args:
            text: Texto de la respuesta
        
        Returns:
            True si se mencionan suposiciones
        """
        assumption_patterns = [
            r"suposición",
            r"assumption",
            r"asumiendo",
            r"asumimos",
            r"nota:\s*[^.]*suponemos",
            r"⚠️\s*[^.]*suposición"
        ]
        
        for pattern in assumption_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _check_response_length(self, text: str, contract: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verifica que la respuesta esté dentro de los límites de longitud.
        
        Args:
            text: Texto de la respuesta
            contract: Contrato de tarea
        
        Returns:
            Dict con resultado de la verificación
        """
        max_tokens = contract.get('metrics', {}).get('max_tokens', 800)
        
        # Estimación simple de tokens (aproximadamente 1.3 palabras por token)
        estimated_tokens = len(text.split()) * 1.3
        
        if estimated_tokens <= max_tokens:
            return {
                "passed": True,
                "message": f"Longitud estimada: {estimated_tokens:.0f} tokens (límite: {max_tokens})"
            }
        else:
            return {
                "passed": False,
                "message": f"Respuesta puede exceder límite: {estimated_tokens:.0f} tokens (límite: {max_tokens})"
            }
    
    def _determine_overall_status(self, verification_result: Dict[str, Any]) -> str:
        """
        Determina el estado general basado en los resultados de verificación.
        
        Args:
            verification_result: Resultados de la verificación
        
        Returns:
            Estado general (APROBADO/REQUIERE_REVISIÓN/RECHAZADO)
        """
        compliance_score = verification_result.get("compliance_score", 0.0)
        violations = verification_result.get("violations", [])
        
        if compliance_score >= 0.9 and not violations:
            return "APROBADO"
        elif compliance_score >= 0.7 and len(violations) <= 1:
            return "REQUIERE_REVISIÓN"
        else:
            return "RECHAZADO"
    
    def detect_hallucinations(self, text: str, context: str) -> Dict[str, Any]:
        """
        Detecta posibles alucinaciones comparando la respuesta con el contexto.
        
        Args:
            text: Texto de la respuesta
            query: Consulta original
            context: Contexto recuperado
        
        Returns:
            Dict con análisis de alucinaciones
        """
        self.logger.info("Detectando posibles alucinaciones")
        
        hallucination_analysis = {
            "potential_hallucinations": [],
            "confidence_score": 0.0,
            "risk_factors": [],
            "recommendations": []
        }
        
        # Extraer afirmaciones principales de la respuesta
        claims = self._extract_claims(text)
        
        # Verificar cada afirmación contra el contexto
        for claim in claims:
            verification = self._verify_claim_against_context(claim, context)
            if not verification["supported"]:
                hallucination_analysis["potential_hallucinations"].append({
                    "claim": claim,
                    "confidence": verification["confidence"],
                    "reason": verification["reason"]
                })
        
        # Calcular score de confianza
        total_claims = len(claims)
        supported_claims = total_claims - len(hallucination_analysis["potential_hallucinations"])
        
        if total_claims > 0:
            hallucination_analysis["confidence_score"] = supported_claims / total_claims
        
        # Identificar factores de riesgo
        if len(hallucination_analysis["potential_hallucinations"]) > 0:
            hallucination_analysis["risk_factors"].append("Afirmaciones sin respaldo en contexto")
        
        if not self._check_sources_section(text):
            hallucination_analysis["risk_factors"].append("Falta sección de fuentes")
        
        # Generar recomendaciones
        if hallucination_analysis["confidence_score"] < 0.8:
            hallucination_analysis["recommendations"].append("Revisar y validar todas las afirmaciones")
        
        if len(hallucination_analysis["potential_hallucinations"]) > 0:
            hallucination_analysis["recommendations"].append("Eliminar o corregir afirmaciones no verificadas")
        
        return hallucination_analysis
    
    def _extract_claims(self, text: str) -> List[str]:
        """
        Extrae afirmaciones principales del texto.
        
        Args:
            text: Texto de la respuesta
        
        Returns:
            Lista de afirmaciones identificadas
        """
        claims = []
        
        # Patrones para identificar afirmaciones
        claim_patterns = [
            r'([^.!?]*(?:es|son|está|están|funciona|requiere|necesita|debe|puede)[^.!?]*[.!?])',
            r'([^.!?]*(?:configuración|error|problema|solución|paso|proceso)[^.!?]*[.!?])',
            r'([^.!?]*(?:para|mediante|usando|con|desde)[^.!?]*[.!?])'
        ]
        
        for pattern in claim_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            claims.extend(matches)
        
        # Limpiar y filtrar afirmaciones
        cleaned_claims = []
        for claim in claims:
            claim = claim.strip()
            if len(claim) > 10 and not claim.startswith(('##', '###', '-', '*', '1.', '2.')):
                cleaned_claims.append(claim)
        
        return cleaned_claims[:10]  # Limitar a 10 afirmaciones
    
    def _verify_claim_against_context(self, claim: str, context: str) -> Dict[str, Any]:
        """
        Verifica si una afirmación está respaldada por el contexto.
        
        Args:
            claim: Afirmación a verificar
            context: Contexto disponible
        
        Returns:
            Dict con resultado de la verificación
        """
        # Implementación simple - en producción usar análisis semántico más sofisticado
        
        # Extraer palabras clave de la afirmación
        claim_words = set(re.findall(r'\b\w+\b', claim.lower()))
        
        # Buscar coincidencias en el contexto
        context_words = set(re.findall(r'\b\w+\b', context.lower()))
        
        # Calcular solapamiento
        common_words = claim_words.intersection(context_words)
        overlap_ratio = len(common_words) / len(claim_words) if claim_words else 0
        
        # Determinar si está respaldado
        if overlap_ratio >= 0.3:  # Umbral de 30%
            return {
                "supported": True,
                "confidence": min(1.0, overlap_ratio),
                "reason": f"Coincidencia de {overlap_ratio:.2f}"
            }
        else:
            return {
                "supported": False,
                "confidence": overlap_ratio,
                "reason": f"Baja coincidencia: {overlap_ratio:.2f}"
            }
    
    def comprehensive_verification(self, response: str, contract: Dict[str, Any], 
                                 context: str) -> Dict[str, Any]:
        """
        Realiza una verificación comprehensiva de la respuesta.
        
        Args:
            response: Respuesta generada
            contract: Contrato de tarea
            context: Contexto recuperado
        
        Returns:
            Dict con verificación comprehensiva
        """
        self.logger.info("Iniciando verificación comprehensiva")
        
        # Verificación automática
        auto_check = self.self_check(response, contract)
        
        # Detección de alucinaciones
        hallucination_check = self.detect_hallucinations(response, context)
        
        # Verificación de cumplimiento del contrato
        contract_compliance = self._verify_contract_compliance(response, contract)
        
        # Resultado comprehensivo
        comprehensive_result = {
            "automatic_check": auto_check,
            "hallucination_detection": hallucination_check,
            "contract_compliance": contract_compliance,
            "overall_assessment": self._generate_overall_assessment(
                auto_check, hallucination_check, contract_compliance
            )
        }
        
        self.logger.info("Verificación comprehensiva completada")
        return comprehensive_result
    
    def _verify_contract_compliance(self, response: str, contract: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verifica el cumplimiento específico del contrato.
        
        Args:
            response: Respuesta generada
            contract: Contrato de tarea
        
        Returns:
            Dict con verificación de cumplimiento
        """
        compliance_check = {
            "goal_achieved": False,
            "requirements_met": [],
            "requirements_missing": [],
            "format_compliant": False,
            "metrics_respected": True
        }
        
        # Verificar objetivo
        goal = contract.get('goal', '')
        if goal and goal.lower() in response.lower():
            compliance_check["goal_achieved"] = True
        
        # Verificar requisitos
        requirements = contract.get('musts', [])
        for req in requirements:
            if self._check_requirement_met(req, response):
                compliance_check["requirements_met"].append(req)
            else:
                compliance_check["requirements_missing"].append(req)
        
        # Verificar formato
        expected_format = contract.get('format', '')
        if expected_format:
            compliance_check["format_compliant"] = self._check_format_compliance(response, expected_format)
        
        # Verificar métricas
        metrics = contract.get('metrics', {})
        if 'max_tokens' in metrics:
            estimated_tokens = len(response.split()) * 1.3
            if estimated_tokens > metrics['max_tokens']:
                compliance_check["metrics_respected"] = False
        
        return compliance_check
    
    def _check_requirement_met(self, requirement: str, response: str) -> bool:
        """
        Verifica si un requisito específico se cumple.
        
        Args:
            requirement: Requisito a verificar
            response: Respuesta generada
        
        Returns:
            True si el requisito se cumple
        """
        requirement_lower = requirement.lower()
        response_lower = response.lower()
        
        # Verificaciones específicas por tipo de requisito
        if "fuentes" in requirement_lower and "citar" in requirement_lower:
            return self._check_sources_section(response)
        elif "suposiciones" in requirement_lower:
            return self._check_explicit_assumptions(response)
        elif "pasos" in requirement_lower:
            return bool(re.search(r'\d+\.', response))
        elif "código" in requirement_lower:
            return bool(re.search(r'```|`.*`', response))
        else:
            # Verificación general por palabras clave
            key_words = requirement_lower.split()
            return all(word in response_lower for word in key_words if len(word) > 3)
    
    def _check_format_compliance(self, response: str, expected_format: str) -> bool:
        """
        Verifica si la respuesta cumple con el formato esperado.
        
        Args:
            response: Respuesta generada
            expected_format: Formato esperado
        
        Returns:
            True si el formato es correcto
        """
        expected_format_lower = expected_format.lower()
        
        if "markdown" in expected_format_lower:
            # Verificar elementos Markdown básicos
            has_headers = bool(re.search(r'^#+\s+', response, re.MULTILINE))
            has_lists = bool(re.search(r'^[-*]\s+', response, re.MULTILINE))
            return has_headers or has_lists
        
        elif "pasos" in expected_format_lower:
            return bool(re.search(r'\d+\.', response))
        
        elif "estructurado" in expected_format_lower:
            return bool(re.search(r'^##\s+', response, re.MULTILINE))
        
        return True  # Por defecto, asumir cumplimiento
    
    def _generate_overall_assessment(self, auto_check: Dict[str, Any], 
                                   hallucination_check: Dict[str, Any],
                                   contract_compliance: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera una evaluación general basada en todos los checks.
        
        Args:
            auto_check: Verificación automática
            hallucination_check: Detección de alucinaciones
            contract_compliance: Cumplimiento del contrato
        
        Returns:
            Dict con evaluación general
        """
        # Calcular score general
        auto_score = auto_check.get("compliance_score", 0.0)
        hallucination_score = hallucination_check.get("confidence_score", 0.0)
        
        # Score de cumplimiento del contrato
        contract_score = 0.0
        if contract_compliance.get("goal_achieved"):
            contract_score += 0.3
        if contract_compliance.get("format_compliant"):
            contract_score += 0.2
        if contract_compliance.get("metrics_respected"):
            contract_score += 0.2
        
        requirements_met = len(contract_compliance.get("requirements_met", []))
        requirements_total = len(contract_compliance.get("requirements_met", [])) + len(contract_compliance.get("requirements_missing", []))
        if requirements_total > 0:
            contract_score += (requirements_met / requirements_total) * 0.3
        
        # Score general ponderado
        overall_score = (auto_score * 0.4) + (hallucination_score * 0.4) + (contract_score * 0.2)
        
        # Determinar estado general
        if overall_score >= 0.9:
            status = "EXCELENTE"
        elif overall_score >= 0.8:
            status = "BUENO"
        elif overall_score >= 0.7:
            status = "ACEPTABLE"
        elif overall_score >= 0.6:
            status = "REQUIERE_MEJORAS"
        else:
            status = "INSUFICIENTE"
        
        return {
            "overall_score": overall_score,
            "status": status,
            "component_scores": {
                "automatic_check": auto_score,
                "hallucination_detection": hallucination_score,
                "contract_compliance": contract_score
            },
            "recommendations": self._generate_recommendations(
                auto_check, hallucination_check, contract_compliance
            )
        }
    
    def _generate_recommendations(self, auto_check: Dict[str, Any], 
                                hallucination_check: Dict[str, Any],
                                contract_compliance: Dict[str, Any]) -> List[str]:
        """
        Genera recomendaciones basadas en los resultados de verificación.
        
        Args:
            auto_check: Verificación automática
            hallucination_check: Detección de alucinaciones
            contract_compliance: Cumplimiento del contrato
        
        Returns:
            Lista de recomendaciones
        """
        recommendations = []
        
        # Recomendaciones basadas en verificación automática
        if auto_check.get("compliance_score", 0) < 0.8:
            recommendations.append("Mejorar cumplimiento de requisitos básicos")
        
        if auto_check.get("violations"):
            recommendations.append("Corregir violaciones críticas identificadas")
        
        # Recomendaciones basadas en detección de alucinaciones
        if hallucination_check.get("confidence_score", 0) < 0.8:
            recommendations.append("Revisar y validar afirmaciones no respaldadas")
        
        if hallucination_check.get("potential_hallucinations"):
            recommendations.append("Eliminar o corregir alucinaciones detectadas")
        
        # Recomendaciones basadas en cumplimiento del contrato
        if not contract_compliance.get("goal_achieved"):
            recommendations.append("Asegurar que se cumpla el objetivo principal")
        
        if not contract_compliance.get("format_compliance"):
            recommendations.append("Ajustar formato según especificaciones del contrato")
        
        if contract_compliance.get("requirements_missing"):
            missing_count = len(contract_compliance["requirements_missing"])
            recommendations.append(f"Implementar {missing_count} requisitos faltantes")
        
        return recommendations
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas del subagente."""
        return {
            "agent_type": "VerificationSubAgent",
            "checklist_items": len(self.checklist),
            "capabilities": [
                "Verificación automática",
                "Detección de alucinaciones",
                "Verificación de cumplimiento",
                "Evaluación comprehensiva"
            ]
        }
