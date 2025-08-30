"""
Subagente de Verificación - Validación de Calidad y Cumplimiento
"""

import logging
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

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
    
    async def comprehensive_verification(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Realiza una verificación comprehensiva de la respuesta.
        
        Args:
            context: Contexto completo para la verificación
                - synthesis: Respuesta generada a verificar
                - contract: Contrato de tarea
                - chunks: Chunks utilizados para generar la respuesta
                - threshold: Umbral mínimo de verificación
        
        Returns:
            Dict con verificación comprehensiva
        """
        try:
            synthesis = context["synthesis"]
            contract = context["contract"]
            chunks = context["chunks"]
            threshold = context.get("threshold", 0.8)
            
            self.logger.info("Iniciando verificación comprehensiva")
            
            # Verificación automática
            auto_check = self.self_check(synthesis, contract)
            
            # Detección de alucinaciones
            chunks_text = "\n".join([chunk.text for chunk in chunks])
            hallucination_check = self.detect_hallucinations(synthesis, chunks_text)
            
            # Verificación de cumplimiento del contrato
            contract_compliance = self._verify_contract_compliance(synthesis, contract)
            
            # Verificación de cobertura de fuentes
            coverage_check = self._verify_source_coverage(synthesis, chunks)
            
            # Verificación de consistencia interna
            consistency_check = self._verify_internal_consistency(synthesis)
            
            # Verificación de factualidad
            factual_check = self._verify_factual_accuracy(synthesis, chunks)
            
            # Calcular scores ponderados
            scores = {
                "basic": max(0.0, 1.0 - (len(auto_check.get("violations", [])) * 0.15)),
                "hallucination": hallucination_check.get("confidence_score", 0.0),
                "contract": self._calculate_contract_score(contract_compliance),
                "coverage": coverage_check.get("score", 0.0),
                "consistency": consistency_check.get("score", 0.0),
                "factual": factual_check.get("score", 0.0)
            }
            
            # Pesos para cada tipo de verificación
            weights = {
                "basic": 0.15,
                "hallucination": 0.25,      # Más importante
                "contract": 0.20,
                "coverage": 0.15,
                "consistency": 0.15,
                "factual": 0.10
            }
            
            # Score general ponderado
            overall_score = sum(scores[key] * weights[key] for key in scores)
            
            # Determinar estado de verificación
            verification_status = "passed" if overall_score >= threshold else "failed"
            
            # Generar recomendaciones
            recommendations = self._generate_verification_recommendations(
                auto_check, hallucination_check, contract_compliance
            )
            
            # Resultado comprehensivo
            comprehensive_result = {
                "overall_score": overall_score,
                "verification_status": verification_status,
                "threshold": threshold,
                "scores": scores,
                "weights": weights,
                "automatic_check": auto_check,
                "hallucination_detection": hallucination_check,
                "contract_compliance": contract_compliance,
                "coverage_check": coverage_check,
                "consistency_check": consistency_check,
                "factual_check": factual_check,
                "recommendations": recommendations,
                "verification_timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"Verificación comprehensiva completada: score {overall_score:.2f}")
            return comprehensive_result
            
        except Exception as e:
            self.logger.error(f"Error en verificación comprehensiva: {e}")
            return {
                "overall_score": 0.0,
                "verification_status": "error",
                "error": str(e),
                "verification_timestamp": datetime.now().isoformat()
            }
    
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
    
    def _verify_source_coverage(self, synthesis: str, chunks: List[Any]) -> Dict[str, Any]:
        """
        Verifica la cobertura de fuentes en la respuesta.
        
        Args:
            synthesis: Respuesta generada
            chunks: Chunks utilizados para generar la respuesta
        
        Returns:
            Dict con análisis de cobertura de fuentes
        """
        try:
            # Extraer fuentes mencionadas en la síntesis
            mentioned_sources = self._extract_mentioned_sources(synthesis)
            
            # Obtener fuentes disponibles de los chunks
            available_sources = set()
            for chunk in chunks:
                if hasattr(chunk, 'metadata') and chunk.metadata:
                    source = chunk.metadata.get('title', '') or chunk.metadata.get('path', '')
                    if source:
                        available_sources.add(source)
            
            # Calcular métricas de cobertura
            total_mentioned = len(mentioned_sources)
            total_available = len(available_sources)
            
            if total_available == 0:
                coverage_score = 0.0
            else:
                coverage_score = min(1.0, total_mentioned / total_available)
            
            # Identificar fuentes no utilizadas
            unused_sources = available_sources - mentioned_sources
            
            return {
                "score": coverage_score,
                "mentioned_sources": list(mentioned_sources),
                "available_sources": list(available_sources),
                "unused_sources": list(unused_sources),
                "coverage_ratio": coverage_score,
                "total_mentioned": total_mentioned,
                "total_available": total_available
            }
            
        except Exception as e:
            self.logger.error(f"Error verificando cobertura de fuentes: {e}")
            return {
                "score": 0.0,
                "error": str(e)
            }
    
    def _verify_internal_consistency(self, synthesis: str) -> Dict[str, Any]:
        """
        Verifica la consistencia interna de la respuesta.
        
        Args:
            synthesis: Respuesta generada
        
        Returns:
            Dict con análisis de consistencia
        """
        try:
            consistency_issues = []
            
            # Verificar consistencia de numeración
            if re.search(r'\d+\.', synthesis):
                numbers = re.findall(r'(\d+)\.', synthesis)
                if numbers:
                    expected_sequence = list(range(1, len(numbers) + 1))
                    actual_sequence = [int(n) for n in numbers]
                    if actual_sequence != expected_sequence:
                        consistency_issues.append("Numeración de pasos inconsistente")
            
            # Verificar consistencia de formato
            headers = re.findall(r'^#+\s+', synthesis, re.MULTILINE)
            if headers:
                header_levels = [len(h.strip()) for h in headers]
                if len(set(header_levels)) > 2:  # Más de 2 niveles diferentes
                    consistency_issues.append("Estructura de headers inconsistente")
            
            # Verificar consistencia de terminología
            technical_terms = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', synthesis)
            if technical_terms:
                term_frequency = {}
                for term in technical_terms:
                    term_frequency[term] = term_frequency.get(term, 0) + 1
                
                # Identificar términos que aparecen solo una vez (posible inconsistencia)
                single_occurrence = [term for term, freq in term_frequency.items() if freq == 1]
                if len(single_occurrence) > len(term_frequency) * 0.5:
                    consistency_issues.append("Muchos términos técnicos aparecen solo una vez")
            
            # Calcular score de consistencia
            consistency_score = max(0.0, 1.0 - (len(consistency_issues) * 0.2))
            
            return {
                "score": consistency_score,
                "issues": consistency_issues,
                "total_issues": len(consistency_issues)
            }
            
        except Exception as e:
            self.logger.error(f"Error verificando consistencia interna: {e}")
            return {
                "score": 0.0,
                "error": str(e)
            }
    
    def _verify_factual_accuracy(self, synthesis: str, chunks: List[Any]) -> Dict[str, Any]:
        """
        Verifica la precisión factual de la respuesta.
        
        Args:
            synthesis: Respuesta generada
            chunks: Chunks utilizados para generar la respuesta
        
        Returns:
            Dict con análisis de precisión factual
        """
        try:
            factual_issues = []
            
            # Extraer afirmaciones factuales
            factual_claims = self._extract_factual_claims(synthesis)
            
            # Verificar cada afirmación contra los chunks
            verified_claims = 0
            total_claims = len(factual_claims)
            
            for claim in factual_claims:
                if self._verify_factual_claim(claim, chunks):
                    verified_claims += 1
                else:
                    factual_issues.append(f"Afirmación no verificada: {claim[:100]}...")
            
            # Calcular score de precisión factual
            if total_claims > 0:
                factual_score = verified_claims / total_claims
            else:
                factual_score = 1.0
            
            return {
                "score": factual_score,
                "verified_claims": verified_claims,
                "total_claims": total_claims,
                "factual_issues": factual_issues,
                "verification_rate": factual_score
            }
            
        except Exception as e:
            self.logger.error(f"Error verificando precisión factual: {e}")
            return {
                "score": 0.0,
                "error": str(e)
            }
    
    def _extract_mentioned_sources(self, synthesis: str) -> set:
        """Extrae las fuentes mencionadas en la síntesis."""
        sources = set()
        
        # Buscar citas en formato [Título](línea X-Y)
        citation_pattern = r'\[([^\]]+)\]\(línea\s+\d+-\d+\)'
        citations = re.findall(citation_pattern, synthesis)
        sources.update(citations)
        
        # Buscar menciones de archivos
        file_pattern = r'`([^`]+\.(?:md|py|js|ts|java|cpp|h))`'
        files = re.findall(file_pattern, synthesis)
        sources.update(files)
        
        # Buscar menciones de secciones
        section_pattern = r'sección\s+["\']([^"\']+)["\']'
        sections = re.findall(section_pattern, synthesis)
        sources.update(sections)
        
        return sources
    
    def _extract_factual_claims(self, synthesis: str) -> List[str]:
        """Extrae afirmaciones factuales de la síntesis."""
        factual_patterns = [
            r'([^.!?]*(?:es\s+\d+[^.!?]*[.!?])',  # "X es 123"
            r'([^.!?]*(?:requiere\s+\d+[^.!?]*[.!?])',  # "X requiere 123"
            r'([^.!?]*(?:tiene\s+\d+[^.!?]*[.!?])',  # "X tiene 123"
            r'([^.!?]*(?:versión\s+\d+[^.!?]*[.!?])',  # "versión 1.2.3"
            r'([^.!?]*(?:línea\s+\d+[^.!?]*[.!?])',  # "línea 45"
        ]
        
        claims = []
        for pattern in factual_patterns:
            matches = re.findall(pattern, synthesis, re.IGNORECASE)
            claims.extend(matches)
        
        return [claim.strip() for claim in claims if len(claim.strip()) > 10]
    
    def _verify_factual_claim(self, claim: str, chunks: List[Any]) -> bool:
        """Verifica si una afirmación factual está respaldada por los chunks."""
        try:
            # Buscar números y valores específicos en la afirmación
            numbers = re.findall(r'\d+(?:\.\d+)?', claim)
            
            if not numbers:
                return True  # Sin números específicos, considerar verificada
            
            # Buscar estos números en los chunks
            for chunk in chunks:
                chunk_text = chunk.text if hasattr(chunk, 'text') else str(chunk)
                for number in numbers:
                    if number in chunk_text:
                        return True
            
            return False
            
        except Exception:
            return False
    
    def _calculate_contract_score(self, contract_compliance: Dict[str, Any]) -> float:
        """Calcula el score de cumplimiento del contrato."""
        try:
            score = 0.0
            
            # Objetivo logrado
            if contract_compliance.get("goal_achieved"):
                score += 0.3
            
            # Formato cumplido
            if contract_compliance.get("format_compliant"):
                score += 0.2
            
            # Métricas respetadas
            if contract_compliance.get("metrics_respected"):
                score += 0.2
            
            # Requisitos cumplidos
            requirements_met = len(contract_compliance.get("requirements_met", []))
            requirements_total = len(contract_compliance.get("requirements_met", [])) + len(contract_compliance.get("requirements_missing", []))
            if requirements_total > 0:
                score += (requirements_met / requirements_total) * 0.3
            
            return score
            
        except Exception:
            return 0.0
    
    def _generate_verification_recommendations(self, auto_check: Dict[str, Any], 
                                            hallucination_check: Dict[str, Any],
                                            contract_compliance: Dict[str, Any]) -> List[str]:
        """Genera recomendaciones específicas para verificación."""
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
        
        if not contract_compliance.get("format_compliant"):
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
