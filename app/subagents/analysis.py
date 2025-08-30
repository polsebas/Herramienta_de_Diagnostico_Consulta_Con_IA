"""
Subagente de Análisis - Clasificación y Análisis de Chunks
"""

import logging
from typing import List, Dict, Any, Optional
from collections import defaultdict
import re

logger = logging.getLogger(__name__)

class AnalysisSubAgent:
    """
    Subagente especializado en analizar chunks recuperados para identificar patrones,
    detectar huecos de información y crear un plan de uso del contexto.
    """
    
    def __init__(self):
        """Inicializa el subagente de análisis."""
        self.logger = logging.getLogger(__name__)
        self.logger.info("AnalysisSubAgent inicializado")
        
        # Patrones para clasificación automática
        self.content_patterns = {
            "code": [
                r"def\s+\w+", r"class\s+\w+", r"import\s+\w+", r"from\s+\w+",
                r"function\s+\w+", r"const\s+\w+", r"let\s+\w+", r"var\s+\w+",
                r"if\s*\(", r"for\s*\(", r"while\s*\(", r"try\s*{"
            ],
            "configuration": [
                r"config", r"setting", r"parameter", r"option", r"env\.",
                r"\.env", r"\.conf", r"\.ini", r"\.yaml", r"\.yml", r"\.json"
            ],
            "error": [
                r"error", r"exception", r"fail", r"crash", r"bug", r"issue",
                r"problem", r"warning", r"critical", r"fatal"
            ],
            "documentation": [
                r"readme", r"docs", r"guide", r"tutorial", r"manual",
                r"example", r"sample", r"note", r"tip", r"warning"
            ]
        }
    
    def analyze(self, chunks: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
        """
        Analiza los chunks recuperados para crear un plan de uso del contexto.
        
        Args:
            chunks: Lista de chunks a analizar
            query: Consulta original del usuario
        
        Returns:
            Dict con análisis completo y plan de uso
        """
        self.logger.info(f"Analizando {len(chunks)} chunks para la consulta")
        
        # Clasificación de contenido
        classification = self._classify_content(chunks)
        
        # Análisis de calidad
        quality_analysis = self._analyze_quality(chunks, query)
        
        # Detección de huecos
        gaps_analysis = self._detect_gaps(chunks, query)
        
        # Plan de uso
        usage_plan = self._create_usage_plan(chunks, classification, quality_analysis, gaps_analysis)
        
        # Análisis final
        analysis_result = {
            "classification": classification,
            "quality_analysis": quality_analysis,
            "gaps_analysis": gaps_analysis,
            "usage_plan": usage_plan,
            "summary": self._create_analysis_summary(classification, quality_analysis, gaps_analysis)
        }
        
        self.logger.info("Análisis completado")
        return analysis_result
    
    def _classify_content(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Clasifica el contenido de los chunks por tipo y características.
        
        Args:
            chunks: Lista de chunks a clasificar
        
        Returns:
            Dict con clasificación detallada
        """
        classification = {
            "concepts": set(),
            "sections": set(),
            "content_types": defaultdict(int),
            "duplicates": [],
            "metadata_completeness": 0
        }
        
        # Analizar cada chunk
        for chunk in chunks:
            text = chunk.get("text", "")
            metadata = chunk.get("metadata", {})
            
            # Clasificar por tipo de contenido
            content_type = self._identify_content_type(text)
            classification["content_types"][content_type] += 1
            
            # Extraer conceptos técnicos
            concepts = self._extract_concepts(text)
            classification["concepts"].update(concepts)
            
            # Extraer secciones
            if metadata.get("section"):
                classification["sections"].add(metadata["section"])
            
            # Verificar metadatos
            metadata_score = self._calculate_metadata_score(metadata)
            classification["metadata_completeness"] += metadata_score
        
        # Normalizar metadatos
        if chunks:
            classification["metadata_completeness"] /= len(chunks)
        
        # Convertir sets a listas para serialización
        classification["concepts"] = list(classification["concepts"])
        classification["sections"] = list(classification["sections"])
        classification["content_types"] = dict(classification["content_types"])
        
        return classification
    
    def _identify_content_type(self, text: str) -> str:
        """
        Identifica el tipo de contenido de un chunk.
        
        Args:
            text: Texto del chunk
        
        Returns:
            Tipo de contenido identificado
        """
        text_lower = text.lower()
        
        # Verificar patrones para cada tipo
        for content_type, patterns in self.content_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    return content_type
        
        # Si no coincide con patrones específicos, clasificar por características
        if len(text) < 100:
            return "short_text"
        elif len(text) > 1000:
            return "long_text"
        else:
            return "general_text"
    
    def _extract_concepts(self, text: str) -> List[str]:
        """
        Extrae conceptos técnicos del texto.
        
        Args:
            text: Texto del chunk
        
        Returns:
            Lista de conceptos identificados
        """
        concepts = []
        
        # Patrones para conceptos técnicos
        concept_patterns = [
            r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)*\b',  # CamelCase
            r'\b[A-Z_]{2,}\b',  # CONSTANTS
            r'\b\w+\.\w+\b',  # module.function
            r'\b\w+://\w+\b',  # URLs
            r'\b\d+\.\d+\.\d+\b',  # version numbers
        ]
        
        for pattern in concept_patterns:
            matches = re.findall(pattern, text)
            concepts.extend(matches)
        
        # Filtrar y limpiar conceptos
        filtered_concepts = []
        for concept in concepts:
            if len(concept) > 2 and concept not in filtered_concepts:
                filtered_concepts.append(concept)
        
        return filtered_concepts[:10]  # Limitar a 10 conceptos
    
    def _calculate_metadata_score(self, metadata: Dict[str, Any]) -> float:
        """
        Calcula un score de completitud de metadatos.
        
        Args:
            metadata: Metadatos del chunk
        
        Returns:
            Score de completitud (0.0-1.0)
        """
        required_fields = ["title", "path", "line_start", "line_end"]
        optional_fields = ["section", "doc_type", "created_at", "updated_at"]
        
        score = 0.0
        
        # Campos requeridos (0.6 del score)
        for field in required_fields:
            if metadata.get(field):
                score += 0.15
        
        # Campos opcionales (0.4 del score)
        for field in optional_fields:
            if metadata.get(field):
                score += 0.1
        
        return min(1.0, score)
    
    def _analyze_quality(self, chunks: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
        """
        Analiza la calidad de los chunks recuperados.
        
        Args:
            chunks: Lista de chunks a analizar
            query: Consulta original
        
        Returns:
            Dict con análisis de calidad
        """
        quality_analysis = {
            "relevance_scores": [],
            "precision_scores": [],
            "completeness_score": 0.0,
            "freshness_score": 0.0,
            "overall_quality": 0.0
        }
        
        if not chunks:
            return quality_analysis
        
        # Calcular scores de relevancia
        for chunk in chunks:
            relevance = self._calculate_relevance_score(chunk, query)
            quality_analysis["relevance_scores"].append(relevance)
        
        # Calcular score de completitud
        coverage = self._calculate_coverage_score(chunks, query)
        quality_analysis["completeness_score"] = coverage
        
        # Calcular score de frescura
        freshness = self._calculate_freshness_score(chunks)
        quality_analysis["freshness_score"] = freshness
        
        # Score general de calidad
        avg_relevance = sum(quality_analysis["relevance_scores"]) / len(quality_analysis["relevance_scores"])
        quality_analysis["overall_quality"] = (avg_relevance + coverage + freshness) / 3
        
        return quality_analysis
    
    def _calculate_relevance_score(self, chunk: Dict[str, Any], query: str) -> float:
        """
        Calcula el score de relevancia de un chunk para la consulta.
        
        Args:
            chunk: Chunk a evaluar
            query: Consulta original
        
        Returns:
            Score de relevancia (0.0-1.0)
        """
        text = chunk.get("text", "")
        query_words = set(query.lower().split())
        text_words = set(text.lower().split())
        
        # Coincidencia de palabras clave
        common_words = query_words.intersection(text_words)
        keyword_score = len(common_words) / len(query_words) if query_words else 0
        
        # Score del chunk (si está disponible)
        chunk_score = chunk.get("score", 0.5)
        
        # Score combinado
        relevance_score = (keyword_score * 0.6) + (chunk_score * 0.4)
        
        return min(1.0, relevance_score)
    
    def _calculate_coverage_score(self, chunks: List[Dict[str, Any]], query: str) -> float:
        """
        Calcula qué tan bien cubren los chunks la consulta.
        
        Args:
            chunks: Lista de chunks
            query: Consulta original
        
        Returns:
            Score de cobertura (0.0-1.0)
        """
        # Análisis simple de cobertura basado en palabras clave
        query_words = set(query.lower().split())
        covered_words = set()
        
        for chunk in chunks:
            text = chunk.get("text", "")
            text_words = set(text.lower().split())
            covered_words.update(query_words.intersection(text_words))
        
        coverage = len(covered_words) / len(query_words) if query_words else 0
        return min(1.0, coverage)
    
    def _calculate_freshness_score(self, chunks: List[Dict[str, Any]]) -> float:
        """
        Calcula el score de frescura de los chunks.
        
        Args:
            chunks: Lista de chunks
        
        Returns:
            Score de frescura (0.0-1.0)
        """
        # Por ahora, score base (en producción usar fechas reales)
        return 0.8
    
    def _detect_gaps(self, chunks: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
        """
        Detecta huecos de información en los chunks recuperados.
        
        Args:
            chunks: Lista de chunks
            query: Consulta original
        
        Returns:
            Dict con análisis de huecos
        """
        gaps_analysis = {
            "missing_information": [],
            "context_needed": [],
            "dependencies": [],
            "suggested_queries": []
        }
        
        # Analizar la consulta para identificar aspectos
        query_aspects = self._identify_query_aspects(query)
        
        # Verificar cobertura de cada aspecto
        for aspect in query_aspects:
            coverage = self._check_aspect_coverage(aspect, chunks)
            if coverage < 0.7:  # Umbral de cobertura
                gaps_analysis["missing_information"].append(aspect)
                gaps_analysis["suggested_queries"].append(f"Buscar información sobre: {aspect}")
        
        # Identificar dependencias faltantes
        dependencies = self._identify_missing_dependencies(chunks)
        gaps_analysis["dependencies"] = dependencies
        
        return gaps_analysis
    
    def _identify_query_aspects(self, query: str) -> List[str]:
        """
        Identifica los aspectos principales de la consulta.
        
        Args:
            query: Consulta del usuario
        
        Returns:
            Lista de aspectos identificados
        """
        # Implementación simple - en producción usar LLM
        aspects = []
        
        if "cómo" in query.lower() or "pasos" in query.lower():
            aspects.append("procedimiento")
        if "error" in query.lower() or "problema" in query.lower():
            aspects.append("diagnóstico")
        if "configuración" in query.lower() or "setup" in query.lower():
            aspects.append("configuración")
        if "código" in query.lower() or "implementación" in query.lower():
            aspects.append("implementación")
        
        return aspects if aspects else ["información_general"]
    
    def _check_aspect_coverage(self, aspect: str, chunks: List[Dict[str, Any]]) -> float:
        """
        Verifica qué tan bien cubren los chunks un aspecto específico.
        
        Args:
            aspect: Aspecto a verificar
            chunks: Lista de chunks
        
        Returns:
            Score de cobertura (0.0-1.0)
        """
        # Implementación simple - en producción usar análisis semántico
        aspect_keywords = {
            "procedimiento": ["paso", "proceso", "workflow", "secuencia"],
            "diagnóstico": ["error", "problema", "síntoma", "causa"],
            "configuración": ["config", "setting", "parameter", "option"],
            "implementación": ["código", "función", "clase", "método"]
        }
        
        keywords = aspect_keywords.get(aspect, [aspect])
        total_matches = 0
        
        for chunk in chunks:
            text = chunk.get("text", "").lower()
            matches = sum(1 for keyword in keywords if keyword in text)
            total_matches += matches
        
        # Normalizar score
        max_possible = len(chunks) * len(keywords)
        coverage = total_matches / max_possible if max_possible > 0 else 0
        
        return min(1.0, coverage)
    
    def _identify_missing_dependencies(self, chunks: List[Dict[str, Any]]) -> List[str]:
        """
        Identifica dependencias que podrían estar faltando.
        
        Args:
            chunks: Lista de chunks
        
        Returns:
            Lista de dependencias faltantes
        """
        # Implementación simple - en producción usar análisis de dependencias
        dependencies = []
        
        for chunk in chunks:
            text = chunk.get("text", "")
            
            # Buscar referencias a otros documentos o secciones
            if "ver" in text.lower() or "referencia" in text.lower():
                dependencies.append("referencias_cruzadas")
            if "requisito" in text.lower() or "dependencia" in text.lower():
                dependencies.append("requisitos_previos")
        
        return list(set(dependencies))
    
    def _create_usage_plan(self, chunks: List[Dict[str, Any]], classification: Dict, 
                           quality_analysis: Dict, gaps_analysis: Dict) -> Dict[str, Any]:
        """
        Crea un plan de uso del contexto para la síntesis.
        
        Args:
            chunks: Lista de chunks
            classification: Clasificación del contenido
            quality_analysis: Análisis de calidad
            gaps_analysis: Análisis de huecos
        
        Returns:
            Dict con plan de uso
        """
        # Ordenar chunks por calidad
        sorted_chunks = sorted(chunks, key=lambda x: x.get("quality_score", 0), reverse=True)
        
        # Seleccionar chunks prioritarios
        priority_chunks = sorted_chunks[:5]  # Top 5 chunks
        
        # Crear plan de uso
        usage_plan = {
            "priority_chunks": [chunk.get("id") for chunk in priority_chunks],
            "suggested_structure": self._suggest_response_structure(classification, gaps_analysis),
            "synthesis_approach": self._suggest_synthesis_approach(classification, quality_analysis),
            "context_organization": self._suggest_context_organization(priority_chunks),
            "quality_warnings": self._generate_quality_warnings(quality_analysis, gaps_analysis)
        }
        
        return usage_plan
    
    def _suggest_response_structure(self, classification: Dict, gaps_analysis: Dict) -> str:
        """
        Sugiere la estructura de la respuesta basada en el análisis.
        
        Args:
            classification: Clasificación del contenido
            gaps_analysis: Análisis de huecos
        
        Returns:
            Estructura sugerida
        """
        if gaps_analysis.get("missing_information"):
            return "Estructura con advertencias sobre información faltante"
        elif "procedimiento" in classification.get("concepts", []):
            return "Estructura paso a paso con verificación"
        elif "diagnóstico" in classification.get("concepts", []):
            return "Estructura de análisis con soluciones"
        else:
            return "Estructura general con información organizada"
    
    def _suggest_synthesis_approach(self, classification: Dict, quality_analysis: Dict) -> str:
        """
        Sugiere el enfoque de síntesis basado en la calidad del contenido.
        
        Args:
            classification: Clasificación del contenido
            quality_analysis: Análisis de calidad
        
        Returns:
            Enfoque sugerido
        """
        if quality_analysis.get("overall_quality", 0) < 0.6:
            return "Síntesis conservadora con advertencias sobre calidad"
        elif quality_analysis.get("overall_quality", 0) > 0.8:
            return "Síntesis completa y detallada"
        else:
            return "Síntesis balanceada con verificación de fuentes"
    
    def _suggest_context_organization(self, priority_chunks: List[Dict[str, Any]]) -> str:
        """
        Sugiere cómo organizar el contexto para la síntesis.
        
        Args:
            priority_chunks: Chunks prioritarios
        
        Returns:
            Organización sugerida
        """
        if len(priority_chunks) <= 3:
            return "Organización secuencial por relevancia"
        else:
            return "Organización temática agrupando chunks relacionados"
    
    def _generate_quality_warnings(self, quality_analysis: Dict, gaps_analysis: Dict) -> List[str]:
        """
        Genera advertencias sobre la calidad del contenido.
        
        Args:
            quality_analysis: Análisis de calidad
            gaps_analysis: Análisis de huecos
        
        Returns:
            Lista de advertencias
        """
        warnings = []
        
        if quality_analysis.get("overall_quality", 0) < 0.6:
            warnings.append("Calidad general del contenido es baja")
        
        if gaps_analysis.get("missing_information"):
            warnings.append("Información faltante detectada")
        
        if gaps_analysis.get("dependencies"):
            warnings.append("Dependencias faltantes identificadas")
        
        return warnings
    
    def _create_analysis_summary(self, classification: Dict, quality_analysis: Dict, 
                                gaps_analysis: Dict) -> str:
        """
        Crea un resumen del análisis para el usuario.
        
        Args:
            classification: Clasificación del contenido
            quality_analysis: Análisis de calidad
            gaps_analysis: Análisis de huecos
        
        Returns:
            Resumen del análisis
        """
        summary_parts = []
        
        # Resumen de clasificación
        content_types = list(classification.get("content_types", {}).keys())
        summary_parts.append(f"Contenido clasificado como: {', '.join(content_types)}")
        
        # Resumen de calidad
        quality_score = quality_analysis.get("overall_quality", 0)
        summary_parts.append(f"Calidad general: {quality_score:.2f}/1.0")
        
        # Resumen de huecos
        if gaps_analysis.get("missing_information"):
            summary_parts.append("⚠️ Información faltante detectada")
        
        if gaps_analysis.get("dependencies"):
            summary_parts.append("⚠️ Dependencias faltantes identificadas")
        
        return " | ".join(summary_parts)
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas del subagente."""
        return {
            "agent_type": "AnalysisSubAgent",
            "content_patterns": len(self.content_patterns),
            "capabilities": [
                "Clasificación de contenido",
                "Análisis de calidad",
                "Detección de huecos",
                "Planificación de uso"
            ]
        }
