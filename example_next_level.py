#!/usr/bin/env python3
"""
Ejemplo de uso del Sistema RAG Next Level con Spec-First y Subagentes

Este script demuestra cómo usar la nueva arquitectura implementada:
- Spec-First con contratos de tarea
- Context Manager para compactación
- Subagentes especializados
- Verificación automática de calidad
"""

import asyncio
import logging
from pathlib import Path
import sys

# Agregar el directorio app al path
sys.path.append(str(Path(__file__).parent / "app"))

from spec_layer import build_task_contract, render_system_prompt, validate_contract_compliance
from context_manager import ContextManager
from subagents import RetrievalSubAgent, AnalysisSubAgent, SynthesisSubAgent, VerificationSubAgent

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NextLevelRAGSystem:
    """
    Sistema RAG Next Level que implementa la arquitectura completa con subagentes.
    """
    
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        """
        Inicializa el sistema RAG Next Level.
        
        Args:
            model_name: Nombre del modelo LLM a usar
        """
        self.model_name = model_name
        
        # Inicializar componentes
        self.context_manager = ContextManager(model_name=model_name)
        self.retrieval_agent = RetrievalSubAgent()
        self.analysis_agent = AnalysisSubAgent()
        self.synthesis_agent = SynthesisSubAgent()
        self.verification_agent = VerificationSubAgent()
        
        # Historial de diálogo
        self.dialog_history = []
        
        logger.info("Sistema RAG Next Level inicializado")
    
    async def process_query(self, query: str, user_role: str = "developer", 
                           risk_level: str = "medium") -> Dict[str, Any]:
        """
        Procesa una consulta completa usando la arquitectura Next Level.
        
        Args:
            query: Consulta del usuario
            user_role: Rol del usuario
            risk_level: Nivel de riesgo
        
        Returns:
            Dict con respuesta completa y metadatos
        """
        logger.info(f"Procesando consulta: {query[:50]}...")
        
        try:
            # 1. RESEARCH: Generar contrato de tarea
            contract = build_task_contract(query, user_role, risk_level)
            logger.info(f"Contrato generado: {contract.goal[:50]}...")
            
            # 2. PLAN: Simular recuperación y análisis
            # (En producción, esto vendría del vector store real)
            retrieved_chunks = self._simulate_retrieval(query)
            analysis = self.analysis_agent.analyze(retrieved_chunks, query)
            logger.info(f"Análisis completado: {analysis['summary']}")
            
            # 3. IMPLEMENT: Generar respuesta
            system_prompt = render_system_prompt(contract)
            context_summary = self.context_manager.create_context_summary(
                system_prompt, query, self.dialog_history, retrieved_chunks
            )
            
            # Generar respuesta usando síntesis
            response = await self.synthesis_agent.write(
                contract.__dict__, analysis, query, context_summary["context"]
            )
            
            # 4. VERIFY: Verificar calidad
            verification = self.verification_agent.comprehensive_verification(
                response, contract.__dict__, context_summary["context"]
            )
            
            # 5. COMPACT: Actualizar historial
            self._update_dialog_history(query, response)
            
            # Resultado final
            result = {
                "query": query,
                "response": response,
                "contract": contract.__dict__,
                "analysis": analysis,
                "verification": verification,
                "context_stats": context_summary["stats"],
                "overall_quality": verification["overall_assessment"]["overall_score"]
            }
            
            logger.info(f"Consulta procesada exitosamente. Calidad: {result['overall_quality']:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Error procesando consulta: {e}")
            return {
                "query": query,
                "error": str(e),
                "response": "Error en el procesamiento de la consulta."
            }
    
    def _simulate_retrieval(self, query: str) -> List[Dict[str, Any]]:
        """
        Simula la recuperación de chunks (en producción usar vector store real).
        
        Args:
            query: Consulta del usuario
        
        Returns:
            Lista de chunks simulados
        """
        # Chunks simulados para demostración
        simulated_chunks = [
            {
                "id": "chunk_1",
                "text": "El sistema de pagos utiliza autenticación JWT para validar transacciones. Los tokens se generan con una clave secreta y expiran después de 24 horas.",
                "metadata": {
                    "title": "Sistema de Pagos",
                    "section": "Autenticación",
                    "line_start": 15,
                    "line_end": 25,
                    "path": "docs/sistema_pagos.md"
                },
                "score": 0.95,
                "source": "vector"
            },
            {
                "id": "chunk_2", 
                "text": "Para configurar el entorno de desarrollo, necesitas instalar Python 3.8+, Node.js 16+ y configurar las variables de entorno en el archivo .env",
                "metadata": {
                    "title": "Guía de Instalación",
                    "section": "Prerrequisitos",
                    "line_start": 8,
                    "line_end": 12,
                    "path": "docs/instalacion.md"
                },
                "score": 0.87,
                "source": "vector"
            },
            {
                "id": "chunk_3",
                "text": "Los errores comunes incluyen: timeout de conexión, credenciales inválidas, y problemas de red. Verifica la configuración del firewall y las credenciales de API.",
                "metadata": {
                    "title": "Resolución de Problemas",
                    "section": "Errores Comunes",
                    "line_start": 30,
                    "line_end": 35,
                    "path": "docs/troubleshooting.md"
                },
                "score": 0.82,
                "source": "vector"
            }
        ]
        
        # Filtrar chunks relevantes según la consulta
        query_lower = query.lower()
        relevant_chunks = []
        
        for chunk in simulated_chunks:
            text_lower = chunk["text"].lower()
            relevance_score = 0
            
            # Calcular relevancia simple
            query_words = set(query_lower.split())
            text_words = set(text_lower.split())
            common_words = query_words.intersection(text_words)
            
            if common_words:
                relevance_score = len(common_words) / len(query_words)
                chunk["relevance_score"] = relevance_score
                
                if relevance_score > 0.1:  # Umbral mínimo de relevancia
                    relevant_chunks.append(chunk)
        
        # Ordenar por relevancia
        relevant_chunks.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        return relevant_chunks[:5]  # Top 5 chunks
    
    def _update_dialog_history(self, query: str, response: str):
        """
        Actualiza el historial del diálogo.
        
        Args:
            query: Consulta del usuario
            response: Respuesta generada
        """
        # Agregar turno actual
        self.dialog_history.append({
            "role": "user",
            "content": query,
            "timestamp": "2024-01-01T12:00:00Z"
        })
        
        self.dialog_history.append({
            "role": "assistant", 
            "content": response,
            "timestamp": "2024-01-01T12:00:01Z"
        })
        
        # Mantener solo los últimos 10 turnos
        if len(self.dialog_history) > 20:
            self.dialog_history = self.dialog_history[-20:]
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas del sistema."""
        return {
            "model_name": self.model_name,
            "dialog_turns": len(self.dialog_history),
            "context_manager": self.context_manager.get_context_budget(100, 200),
            "retrieval_agent": self.retrieval_agent.get_stats(),
            "analysis_agent": self.analysis_agent.get_stats(),
            "synthesis_agent": self.synthesis_agent.get_stats(),
            "verification_agent": self.verification_agent.get_stats()
        }

async def main():
    """Función principal para demostrar el sistema."""
    print("🚀 Sistema RAG Next Level - Demostración")
    print("=" * 50)
    
    # Inicializar sistema
    rag_system = NextLevelRAGSystem()
    
    # Ejemplos de consultas
    example_queries = [
        {
            "query": "¿Cómo configuro el entorno de desarrollo?",
            "user_role": "developer",
            "risk_level": "low"
        },
        {
            "query": "¿Por qué falla la autenticación del sistema de pagos?",
            "user_role": "developer", 
            "risk_level": "high"
        },
        {
            "query": "¿Qué base de datos debería usar para este proyecto?",
            "user_role": "manager",
            "risk_level": "medium"
        }
    ]
    
    # Procesar cada consulta
    for i, query_info in enumerate(example_queries, 1):
        print(f"\n📝 Consulta {i}: {query_info['query']}")
        print(f"👤 Rol: {query_info['user_role']}, 🚨 Riesgo: {query_info['risk_level']}")
        print("-" * 50)
        
        # Procesar consulta
        result = await rag_system.process_query(
            query_info["query"],
            query_info["user_role"],
            query_info["risk_level"]
        )
        
        if "error" not in result:
            # Mostrar respuesta
            print(f"✅ Respuesta generada (Calidad: {result['overall_quality']:.2f})")
            print(f"📊 Verificación: {result['verification']['overall_assessment']['status']}")
            
            # Mostrar resumen de la respuesta
            response_lines = result["response"].split('\n')[:5]
            print("📄 Respuesta (primeras líneas):")
            for line in response_lines:
                print(f"   {line}")
            
            if len(result["response"].split('\n')) > 5:
                print("   ...")
            
            # Mostrar fuentes si están disponibles
            if "## Fuentes" in result["response"]:
                sources_section = result["response"].split("## Fuentes")[1].split('\n')[:3]
                print("🔗 Fuentes:")
                for line in sources_section:
                    if line.strip():
                        print(f"   {line.strip()}")
        else:
            print(f"❌ Error: {result['error']}")
    
    # Mostrar estadísticas del sistema
    print("\n📈 Estadísticas del Sistema")
    print("=" * 50)
    stats = rag_system.get_system_stats()
    print(f"Modelo: {stats['model_name']}")
    print(f"Turnos de diálogo: {stats['dialog_turns']}")
    print(f"Presupuesto de contexto: {stats['context_manager']} tokens")
    
    print("\n🎉 Demostración completada!")

if __name__ == "__main__":
    # Ejecutar demostración
    asyncio.run(main())
