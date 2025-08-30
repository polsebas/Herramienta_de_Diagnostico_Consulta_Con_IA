"""
Ejemplo completo del Sistema de Evaluación - Golden Set y Métricas de Calidad

Este script demuestra todas las capacidades del sistema de evaluación:
- Evaluación del golden set de 20 preguntas
- Métricas de calidad en tiempo real
- Generación de reportes y gráficos
- Análisis de tendencias y recomendaciones
"""

import asyncio
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from eval.evaluate_plans import (
    PlanEvaluator, GoldenQuestion, EvaluationResult, EvaluationSummary,
    evaluate_system_quality, get_evaluation_summary
)
from app.context_manager import ContextManager
from app.human_loop import HumanLoopManager

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def demo_evaluation_system_initialization():
    """Demo de inicialización del sistema de evaluación."""
    print("\n" + "="*60)
    print("DEMO: Inicialización del Sistema de Evaluación")
    print("="*60)
    
    # Inicializar componentes
    context_manager = ContextManager()
    human_loop_manager = HumanLoopManager()
    
    # Crear evaluador
    evaluator = PlanEvaluator(
        context_manager=context_manager,
        human_loop_manager=human_loop_manager
    )
    
    # Verificar golden set
    print(f"Golden Set cargado:")
    print(f"- Total preguntas: {len(evaluator.golden_set)}")
    
    # Mostrar distribución por dominio
    domain_counts = {}
    difficulty_counts = {}
    
    for question in evaluator.golden_set:
        domain = question.domain
        difficulty = question.difficulty
        
        domain_counts[domain] = domain_counts.get(domain, 0) + 1
        difficulty_counts[difficulty] = difficulty_counts.get(difficulty, 0) + 1
    
    print(f"\nDistribución por dominio:")
    for domain, count in domain_counts.items():
        print(f"- {domain}: {count} preguntas")
    
    print(f"\nDistribución por dificultad:")
    for difficulty, count in difficulty_counts.items():
        print(f"- {difficulty}: {count} preguntas")
    
    # Mostrar configuración
    print(f"\nConfiguración del evaluador:")
    print(f"- Umbrales: {evaluator.config['evaluation_thresholds']}")
    print(f"- Pesos de calidad: {evaluator.config['quality_weights']}")
    print(f"- Máximo evaluaciones paralelas: {evaluator.config['max_parallel_evaluations']}")
    
    return evaluator


async def demo_single_question_evaluation(evaluator: PlanEvaluator):
    """Demo de evaluación de una pregunta individual."""
    print("\n" + "="*60)
    print("DEMO: Evaluación de Pregunta Individual")
    print("="*60)
    
    # Seleccionar pregunta de testing (fácil)
    test_question = None
    for question in evaluator.golden_set:
        if question.domain == "testing" and question.difficulty == "easy":
            test_question = question
            break
    
    if not test_question:
        print("No se encontró pregunta de testing fácil")
        return
    
    print(f"Evaluando pregunta: {test_question.question}")
    print(f"- Dominio: {test_question.domain}")
    print(f"- Dificultad: {test_question.difficulty}")
    print(f"- Tipo esperado: {test_question.expected_type}")
    print(f"- Score baseline: {test_question.baseline_score:.2f}")
    
    # Evaluar pregunta
    start_time = time.time()
    result = await evaluator.evaluate_question(test_question)
    evaluation_time = time.time() - start_time
    
    # Mostrar resultados
    print(f"\nResultados de evaluación:")
    print(f"- Score general: {result.overall_score:.2f}")
    print(f"- Nivel de calidad: {result.quality_level.value}")
    print(f"- Tiempo de evaluación: {evaluation_time:.2f}s")
    print(f"- Contrato generado: {result.contract_generated}")
    print(f"- Tarea ejecutada: {result.task_executed}")
    print(f"- Tarea exitosa: {result.task_success}")
    
    print(f"\nScores de calidad:")
    for metric, score in result.quality_scores.items():
        print(f"- {metric}: {score:.2f}")
    
    print(f"\nFeedback:")
    for feedback_item in result.feedback:
        print(f"- {feedback_item}")
    
    print(f"\nArtefactos generados:")
    for artifact in result.artifacts_generated:
        print(f"- {artifact}")
    
    return result


async def demo_batch_evaluation(evaluator: PlanEvaluator):
    """Demo de evaluación en lotes."""
    print("\n" + "="*60)
    print("DEMO: Evaluación en Lotes")
    print("="*60)
    
    # Seleccionar preguntas de diferentes dominios
    selected_questions = []
    domains_to_evaluate = ["auth", "security", "performance"]
    
    for domain in domains_to_evaluate:
        for question in evaluator.golden_set:
            if question.domain == domain and question.difficulty == "medium":
                selected_questions.append(question)
                break
    
    print(f"Evaluando {len(selected_questions)} preguntas en paralelo:")
    for question in selected_questions:
        print(f"- {question.domain}: {question.question[:50]}...")
    
    # Evaluar en lotes
    start_time = time.time()
    results = []
    
    for i in range(0, len(selected_questions), 2):  # Lotes de 2
        batch = selected_questions[i:i+2]
        print(f"\nEvaluando lote {i//2 + 1}: {len(batch)} preguntas")
        
        batch_results = await asyncio.gather(*[
            evaluator.evaluate_question(question) for question in batch
        ])
        results.extend(batch_results)
        
        # Mostrar progreso
        for result in batch_results:
            print(f"  ✅ {result.question_id}: {result.overall_score:.2f}")
    
    total_time = time.time() - start_time
    
    print(f"\nEvaluación en lotes completada:")
    print(f"- Total preguntas evaluadas: {len(results)}")
    print(f"- Tiempo total: {total_time:.2f}s")
    print(f"- Tiempo promedio por pregunta: {total_time/len(results):.2f}s")
    
    # Mostrar resumen de resultados
    scores = [r.overall_score for r in results]
    print(f"- Score promedio: {sum(scores)/len(scores):.2f}")
    print(f"- Score mínimo: {min(scores):.2f}")
    print(f"- Score máximo: {max(scores):.2f}")
    
    return results


async def demo_golden_set_evaluation(evaluator: PlanEvaluator):
    """Demo de evaluación completa del golden set."""
    print("\n" + "="*60)
    print("DEMO: Evaluación Completa del Golden Set")
    print("="*60)
    
    print("⚠️  ADVERTENCIA: Esta evaluación puede tomar varios minutos")
    print("Evaluando las 20 preguntas del golden set...")
    
    # Evaluar golden set completo
    start_time = time.time()
    summary = await evaluator.evaluate_golden_set(max_parallel=3)
    total_time = time.time() - start_time
    
    # Mostrar resumen completo
    print(f"\n" + "="*60)
    print("RESUMEN DE EVALUACIÓN COMPLETA")
    print("="*60)
    
    print(f"📊 Estadísticas Generales:")
    print(f"- Total preguntas: {summary.total_questions}")
    print(f"- Preguntas evaluadas: {summary.questions_evaluated}")
    print(f"- Score promedio: {summary.average_score:.2f}")
    print(f"- Tiempo total: {total_time:.2f}s")
    print(f"- Tiempo promedio por pregunta: {total_time/summary.questions_evaluated:.2f}s")
    
    print(f"\n🏆 Distribución de Calidad:")
    for level, count in summary.quality_distribution.items():
        percentage = (count / summary.questions_evaluated) * 100
        print(f"- {level}: {count} preguntas ({percentage:.1f}%)")
    
    print(f"\n🌍 Performance por Dominio:")
    for domain, score in summary.domain_performance.items():
        print(f"- {domain}: {score:.2f}")
    
    print(f"\n📈 Performance por Dificultad:")
    for difficulty, score in summary.difficulty_performance.items():
        print(f"- {difficulty}: {score:.2f}")
    
    print(f"\n📊 Tendencia de Mejora:")
    if summary.improvement_trend > 0:
        print(f"✅ Mejora: +{summary.improvement_trend:.2f} sobre baseline")
    elif summary.improvement_trend < 0:
        print(f"❌ Deterioro: {summary.improvement_trend:.2f} sobre baseline")
    else:
        print(f"➡️ Sin cambios sobre baseline")
    
    print(f"\n💡 Recomendaciones:")
    for i, recommendation in enumerate(summary.recommendations, 1):
        print(f"{i}. {recommendation}")
    
    return summary


async def demo_quality_analysis(evaluator: PlanEvaluator):
    """Demo de análisis de calidad detallado."""
    print("\n" + "="*60)
    print("DEMO: Análisis de Calidad Detallado")
    print("="*60)
    
    if not evaluator.evaluation_history:
        print("No hay historial de evaluación para analizar")
        return
    
    # Análisis por métrica de calidad
    print("📊 Análisis por Métrica de Calidad:")
    
    metrics = ['accuracy', 'completeness', 'relevance', 'actionability', 
               'security', 'performance', 'maintainability', 'testability', 'documentation']
    
    for metric in metrics:
        scores = []
        for result in evaluator.evaluation_history:
            if metric in result.quality_scores:
                scores.append(result.quality_scores[metric])
        
        if scores:
            avg_score = sum(scores) / len(scores)
            min_score = min(scores)
            max_score = max(scores)
            print(f"- {metric}:")
            print(f"  Promedio: {avg_score:.2f}")
            print(f"  Rango: {min_score:.2f} - {max_score:.2f}")
            print(f"  Muestras: {len(scores)}")
    
    # Análisis de tendencias
    print(f"\n📈 Análisis de Tendencias:")
    
    # Agrupar por timestamp (por hora)
    hourly_results = {}
    for result in evaluator.evaluation_history:
        hour = result.timestamp.strftime("%Y-%m-%d %H:00")
        if hour not in hourly_results:
            hourly_results[hour] = []
        hourly_results[hour].append(result.overall_score)
    
    if len(hourly_results) > 1:
        print("Evolución por hora:")
        for hour in sorted(hourly_results.keys()):
            avg_score = sum(hourly_results[hour]) / len(hourly_results[hour])
            print(f"- {hour}: {avg_score:.2f}")
    
    # Análisis de outliers
    print(f"\n🔍 Análisis de Outliers:")
    all_scores = [r.overall_score for r in evaluator.evaluation_history]
    
    if all_scores:
        avg_score = sum(all_scores) / len(all_scores)
        threshold = 0.2  # 20% del promedio
        
        outliers = []
        for result in evaluator.evaluation_history:
            if abs(result.overall_score - avg_score) > threshold:
                outliers.append(result)
        
        if outliers:
            print(f"Se encontraron {len(outliers)} outliers:")
            for outlier in outliers[:3]:  # Mostrar solo los primeros 3
                print(f"- {outlier.question_id}: {outlier.overall_score:.2f} (esperado ~{avg_score:.2f})")
        else:
            print("No se encontraron outliers significativos")
    
    return evaluator.evaluation_history


async def demo_export_and_reporting(evaluator: PlanEvaluator):
    """Demo de exportación y reportes."""
    print("\n" + "="*60)
    print("DEMO: Exportación y Reportes")
    print("="*60)
    
    if not evaluator.evaluation_history:
        print("No hay datos para exportar")
        return
    
    # Crear directorio de resultados
    output_dir = Path("eval/results")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Exportando resultados a: {output_dir}")
    
    # Exportar resultados
    evaluator.export_results(str(output_dir))
    
    # Verificar archivos generados
    print(f"\nArchivos generados:")
    for file_path in output_dir.glob("*"):
        if file_path.is_file():
            size_kb = file_path.stat().st_size / 1024
            print(f"- {file_path.name}: {size_kb:.1f} KB")
    
    # Generar reporte personalizado
    print(f"\nGenerando reporte personalizado...")
    
    # Crear reporte HTML simple
    html_report = generate_html_report(evaluator)
    report_file = output_dir / "evaluation_report.html"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html_report)
    
    print(f"✅ Reporte HTML generado: {report_file}")
    
    return output_dir


def generate_html_report(evaluator: PlanEvaluator) -> str:
    """Genera un reporte HTML simple de la evaluación."""
    if not evaluator.evaluation_history:
        return "<html><body><h1>No hay datos de evaluación</h1></body></html>"
    
    # Calcular estadísticas
    total_questions = len(evaluator.evaluation_history)
    avg_score = sum(r.overall_score for r in evaluator.evaluation_history) / total_questions
    
    # Distribución de calidad
    quality_dist = {}
    for result in evaluator.evaluation_history:
        level = result.quality_level.value
        quality_dist[level] = quality_dist.get(level, 0) + 1
    
    # Performance por dominio
    domain_perf = {}
    for result in evaluator.evaluation_history:
        domain = result.metadata.get('domain', 'unknown')
        if domain not in domain_perf:
            domain_perf[domain] = []
        domain_perf[domain].append(result.overall_score)
    
    for domain in domain_perf:
        domain_perf[domain] = sum(domain_perf[domain]) / len(domain_perf[domain])
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Reporte de Evaluación del Sistema</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
            .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
            .metric {{ display: inline-block; margin: 10px; padding: 10px; background-color: #e8f4f8; border-radius: 3px; }}
            .score {{ font-size: 24px; font-weight: bold; color: #2c5aa0; }}
            .chart {{ margin: 20px 0; text-align: center; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 Reporte de Evaluación del Sistema</h1>
            <p>Generado el: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
        </div>
        
        <div class="section">
            <h2>📊 Resumen General</h2>
            <div class="metric">
                <div class="score">{total_questions}</div>
                <div>Total Preguntas</div>
            </div>
            <div class="metric">
                <div class="score">{avg_score:.2f}</div>
                <div>Score Promedio</div>
            </div>
        </div>
        
        <div class="section">
            <h2>🏆 Distribución de Calidad</h2>
            <table>
                <tr><th>Nivel</th><th>Cantidad</th><th>Porcentaje</th></tr>
    """
    
    for level, count in quality_dist.items():
        percentage = (count / total_questions) * 100
        html += f"<tr><td>{level}</td><td>{count}</td><td>{percentage:.1f}%</td></tr>"
    
    html += """
            </table>
        </div>
        
        <div class="section">
            <h2>🌍 Performance por Dominio</h2>
            <table>
                <tr><th>Dominio</th><th>Score Promedio</th></tr>
    """
    
    for domain, score in domain_perf.items():
        html += f"<tr><td>{domain}</td><td>{score:.2f}</td></tr>"
    
    html += """
            </table>
        </div>
        
        <div class="section">
            <h2>📋 Detalle de Preguntas</h2>
            <table>
                <tr><th>ID</th><th>Dominio</th><th>Score</th><th>Nivel</th><th>Feedback</th></tr>
    """
    
    for result in evaluator.evaluation_history[:10]:  # Solo las primeras 10
        feedback_summary = "; ".join(result.feedback[:2])  # Solo los primeros 2 feedbacks
        html += f"<tr><td>{result.question_id}</td><td>{result.metadata.get('domain', 'N/A')}</td><td>{result.overall_score:.2f}</td><td>{result.quality_level.value}</td><td>{feedback_summary}</td></tr>"
    
    html += """
            </table>
        </div>
        
        <div class="section">
            <h2>💡 Recomendaciones</h2>
            <ul>
    """
    
    # Generar recomendaciones basadas en los datos
    if avg_score < 0.8:
        html += "<li>El score promedio está por debajo del objetivo de 0.8. Revisar configuración y entrenamiento del sistema.</li>"
    
    low_performance_domains = [domain for domain, score in domain_perf.items() if score < 0.75]
    if low_performance_domains:
        html += f"<li>Los dominios {', '.join(low_performance_domains)} tienen rendimiento bajo. Considerar mejoras específicas.</li>"
    
    html += """
            </ul>
        </div>
    </body>
    </html>
    """
    
    return html


async def main():
    """Función principal que ejecuta todos los demos."""
    print("🚀 DEMO COMPLETO DEL SISTEMA DE EVALUACIÓN")
    print("Golden Set y Métricas de Calidad")
    
    try:
        # Inicializar sistema
        evaluator = await demo_evaluation_system_initialization()
        
        # Ejecutar demos en secuencia
        await demo_single_question_evaluation(evaluator)
        await demo_batch_evaluation(evaluator)
        
        # Preguntar si ejecutar evaluación completa
        print(f"\n" + "="*60)
        print("¿Ejecutar evaluación completa del Golden Set? (puede tomar varios minutos)")
        print("1. Sí - Evaluación completa")
        print("2. No - Solo análisis de datos existentes")
        
        # Por simplicidad, asumimos que queremos la evaluación completa
        print("Ejecutando evaluación completa...")
        await demo_golden_set_evaluation(evaluator)
        
        # Análisis de calidad
        await demo_quality_analysis(evaluator)
        
        # Exportación y reportes
        await demo_export_and_reporting(evaluator)
        
        print("\n" + "="*60)
        print("✅ TODOS LOS DEMOS COMPLETADOS EXITOSAMENTE")
        print("="*60)
        
        # Mostrar estadísticas finales
        if evaluator.evaluation_history:
            final_summary = get_evaluation_summary(evaluator)
            print(f"\n📊 Estadísticas Finales:")
            print(f"- Total evaluaciones: {final_summary.questions_evaluated}")
            print(f"- Score promedio: {final_summary.average_score:.2f}")
            print(f"- Mejora sobre baseline: {final_summary.improvement_trend:+.2f}")
            print(f"- Recomendaciones: {len(final_summary.recommendations)}")
        
    except Exception as e:
        logger.error(f"Error en demo: {e}")
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
