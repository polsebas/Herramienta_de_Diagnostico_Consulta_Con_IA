"""
Tests para el Intelligent Task Classifier - PR-F

Tests unitarios e integración para el clasificador ML avanzado.
"""

import pytest
import asyncio
import numpy as np
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from app.advanced_contracts.intelligent_classifier import (
    IntelligentTaskClassifier,
    TaskTypeAdvanced,
    ClassificationFeatures,
    ClassificationResult,
    AdvancedFeatureExtractor,
    classify_task_advanced
)


class TestAdvancedFeatureExtractor:
    """Tests para el extractor de features avanzadas."""
    
    @pytest.fixture
    def feature_extractor(self):
        return AdvancedFeatureExtractor()
    
    @pytest.mark.asyncio
    async def test_extract_query_features_basic(self, feature_extractor):
        """Test extracción básica de features de query."""
        query = "¿Cómo implementar autenticación JWT en Django?"
        
        features = await feature_extractor.extract_query_features(query)
        
        assert 'embedding' in features
        assert 'length' in features
        assert 'keyword_scores' in features
        assert features['length'] == len(query)
        assert isinstance(features['embedding'], np.ndarray)
        assert len(features['embedding']) == 384  # Dimensión esperada
    
    @pytest.mark.asyncio
    async def test_extract_query_features_code_detection(self, feature_extractor):
        """Test detección de indicadores de código."""
        query_with_code = "Crear función def authenticate_user() que valide JWT"
        query_without_code = "¿Cuál es el proceso de autenticación?"
        
        features_with_code = await feature_extractor.extract_query_features(query_with_code)
        features_without_code = await feature_extractor.extract_query_features(query_without_code)
        
        assert features_with_code['has_code_indicators'] == True
        assert features_without_code['has_code_indicators'] == False
    
    @pytest.mark.asyncio
    async def test_extract_project_features(self, feature_extractor):
        """Test extracción de features del proyecto."""
        project_context = {
            'complexity_score': 0.8,
            'team_size': 5,
            'frameworks': ['django', 'celery'],
            'has_tests': True,
            'primary_language': 'python'
        }
        
        features = await feature_extractor.extract_project_features(project_context)
        
        assert features['complexity_score'] == 0.8
        assert features['team_size'] == 5
        assert features['framework_count'] == 2
        assert features['has_tests'] == True
    
    @pytest.mark.asyncio
    async def test_extract_user_features_empty_history(self, feature_extractor):
        """Test extracción de features con historial vacío."""
        user_history = []
        
        features = await feature_extractor.extract_user_features(user_history)
        
        assert features['avg_task_complexity'] == 0.5
        assert features['success_rate'] == 0.8
        assert features['total_tasks'] == 0
        assert features['recent_activity'] == 0
    
    @pytest.mark.asyncio
    async def test_extract_user_features_with_history(self, feature_extractor):
        """Test extracción de features con historial."""
        user_history = [
            {
                'complexity': 0.8,
                'success': True,
                'type': 'code',
                'timestamp': '2025-01-01T00:00:00'
            },
            {
                'complexity': 0.6,
                'success': False,
                'type': 'procedural',
                'timestamp': '2025-01-02T00:00:00'
            }
        ]
        
        features = await feature_extractor.extract_user_features(user_history)
        
        assert features['avg_task_complexity'] == 0.7
        assert features['success_rate'] == 0.5
        assert features['total_tasks'] == 2
        assert 'code' in features['preferred_task_types']


class TestIntelligentTaskClassifier:
    """Tests para el clasificador inteligente."""
    
    @pytest.fixture
    def classifier(self):
        return IntelligentTaskClassifier()
    
    @pytest.mark.asyncio
    async def test_classify_procedural_query(self, classifier):
        """Test clasificación de query procedimental."""
        query = "¿Cómo configurar autenticación en Django?"
        project_context = {'frameworks': ['django']}
        user_history = []
        
        result = await classifier.classify_with_context(query, project_context, user_history)
        
        assert isinstance(result, ClassificationResult)
        assert result.primary_type in [TaskTypeAdvanced.PROCEDURAL, TaskTypeAdvanced.CODE]
        assert 0.0 <= result.confidence <= 1.0
        assert result.reasoning is not None
        assert isinstance(result.context_factors, dict)
    
    @pytest.mark.asyncio
    async def test_classify_code_query(self, classifier):
        """Test clasificación de query de código."""
        query = "Implementar función de validación JWT con FastAPI"
        project_context = {'frameworks': ['fastapi'], 'complexity_score': 0.6}
        user_history = [{'type': 'code', 'success': True, 'complexity': 0.7}]
        
        result = await classifier.classify_with_context(query, project_context, user_history)
        
        assert result.primary_type == TaskTypeAdvanced.CODE
        assert result.confidence > 0.5
        assert 'fastapi' in result.reasoning.lower() or 'code' in result.reasoning.lower()
    
    @pytest.mark.asyncio
    async def test_classify_security_query(self, classifier):
        """Test clasificación de query de seguridad."""
        query = "Auditar vulnerabilidades de seguridad en el sistema de autenticación"
        project_context = {'maturity_level': 'enterprise'}
        user_history = []
        
        result = await classifier.classify_with_context(query, project_context, user_history)
        
        # Debería detectar como security audit o procedural
        assert result.primary_type in [TaskTypeAdvanced.SECURITY_AUDIT, TaskTypeAdvanced.PROCEDURAL]
        assert result.confidence > 0.4
    
    @pytest.mark.asyncio
    async def test_fallback_classification(self, classifier):
        """Test clasificación de fallback con error."""
        query = ""  # Query vacía para forzar fallback
        
        result = await classifier.classify_with_context(query, {}, [])
        
        assert isinstance(result, ClassificationResult)
        assert result.primary_type is not None
        assert result.confidence > 0.0
        assert "emergencia" in result.reasoning.lower() or "fallback" in result.reasoning.lower()
    
    @pytest.mark.asyncio
    async def test_performance_metrics_tracking(self, classifier):
        """Test que las métricas de performance se trackean."""
        initial_predictions = classifier.performance_metrics['predictions_made']
        
        query = "Test query"
        await classifier.classify_with_context(query, {}, [])
        
        assert classifier.performance_metrics['predictions_made'] == initial_predictions + 1
    
    @pytest.mark.asyncio
    async def test_model_training_with_data(self, classifier):
        """Test entrenamiento del modelo con datos."""
        training_data = [
            {
                'query': '¿Cómo implementar login?',
                'context': {'frameworks': ['django']},
                'history': [],
                'label': TaskTypeAdvanced.PROCEDURAL.value
            },
            {
                'query': 'Crear función de validación',
                'context': {'frameworks': ['fastapi']},
                'history': [],
                'label': TaskTypeAdvanced.CODE.value
            },
            {
                'query': 'Diagnosticar error de conexión',
                'context': {},
                'history': [],
                'label': TaskTypeAdvanced.DIAGNOSTIC.value
            }
        ]
        
        training_result = await classifier.train_model(training_data)
        
        assert 'accuracy' in training_result
        assert 'samples' in training_result
        assert training_result['samples'] == len(training_data)
        
        # Verificar que el modelo se marcó como entrenado
        if training_result['accuracy'] > 0:  # Solo si ML está disponible
            assert classifier.is_trained == True


class TestClassificationFeatures:
    """Tests para la clase ClassificationFeatures."""
    
    def test_to_feature_vector(self):
        """Test conversión a vector de features."""
        features = ClassificationFeatures(
            query_embedding=np.random.random(384),
            query_length=50,
            keyword_scores={'procedural': 0.8, 'code': 0.2},
            project_context_features={'complexity_score': 0.7, 'team_size': 5, 'framework_count': 2},
            user_history_features={'avg_task_complexity': 0.6, 'success_rate': 0.9},
            semantic_similarity_scores={'procedural': 0.8}
        )
        
        vector = features.to_feature_vector()
        
        assert isinstance(vector, np.ndarray)
        assert len(vector) > 384  # Al menos embeddings + features adicionales
        assert not np.isnan(vector).any()  # No debe tener NaN


class TestIntegrationFunctions:
    """Tests de integración para funciones de conveniencia."""
    
    @pytest.mark.asyncio
    async def test_classify_task_advanced_function(self):
        """Test función de conveniencia classify_task_advanced."""
        query = "¿Cómo optimizar queries de base de datos?"
        project_context = {'frameworks': ['django'], 'complexity_score': 0.8}
        user_history = [{'type': 'performance', 'success': True}]
        
        result = await classify_task_advanced(query, project_context, user_history)
        
        assert isinstance(result, ClassificationResult)
        assert result.primary_type is not None
        assert result.confidence > 0.0
    
    @pytest.mark.asyncio
    async def test_classify_task_advanced_with_custom_classifier(self):
        """Test función con clasificador personalizado."""
        classifier = IntelligentTaskClassifier()
        query = "Crear API endpoint para usuarios"
        
        result = await classify_task_advanced(query, classifier=classifier)
        
        assert isinstance(result, ClassificationResult)
        assert result.primary_type in [TaskTypeAdvanced.CODE, TaskTypeAdvanced.PROCEDURAL]


class TestEdgeCases:
    """Tests para casos edge y manejo de errores."""
    
    @pytest.fixture
    def classifier(self):
        return IntelligentTaskClassifier()
    
    @pytest.mark.asyncio
    async def test_empty_query(self, classifier):
        """Test con query vacía."""
        result = await classifier.classify_with_context("", {}, [])
        
        assert isinstance(result, ClassificationResult)
        assert result.confidence < 0.8  # Baja confianza esperada
    
    @pytest.mark.asyncio
    async def test_very_long_query(self, classifier):
        """Test con query muy larga."""
        long_query = "¿Cómo " + "implementar " * 1000 + "autenticación?"
        
        result = await classifier.classify_with_context(long_query, {}, [])
        
        assert isinstance(result, ClassificationResult)
        assert result.primary_type is not None
    
    @pytest.mark.asyncio
    async def test_malformed_context(self, classifier):
        """Test con contexto malformado."""
        query = "Test query"
        malformed_context = {"invalid": None, "nested": {"deep": {"very": "deep"}}}
        
        # No debería fallar, debería manejar gracefully
        result = await classifier.classify_with_context(query, malformed_context, [])
        
        assert isinstance(result, ClassificationResult)
    
    @pytest.mark.asyncio
    async def test_malformed_history(self, classifier):
        """Test con historial malformado."""
        query = "Test query"
        malformed_history = [
            {"missing_fields": True},
            {"timestamp": "invalid_date"},
            None,  # Entrada nula
            {"success": "not_boolean"}
        ]
        
        # No debería fallar
        result = await classifier.classify_with_context(query, {}, malformed_history)
        
        assert isinstance(result, ClassificationResult)


@pytest.mark.integration
class TestClassifierIntegration:
    """Tests de integración con sistema actual."""
    
    @pytest.mark.asyncio
    async def test_integration_with_spec_layer(self):
        """Test integración con SpecLayer existente."""
        # Simular integración con sistema actual
        from app.spec_layer import TaskType
        
        classifier = IntelligentTaskClassifier()
        query = "¿Cómo configurar base de datos?"
        
        result = await classifier.classify_with_context(query, {}, [])
        
        # Verificar que el resultado puede mapearse a tipos del sistema actual
        mapping = {
            TaskTypeAdvanced.PROCEDURAL: TaskType.PROCEDURAL,
            TaskTypeAdvanced.CODE: TaskType.CODE,
            TaskTypeAdvanced.DIAGNOSTIC: TaskType.DIAGNOSTIC
        }
        
        mapped_type = mapping.get(result.primary_type)
        assert mapped_type is not None or result.primary_type in TaskTypeAdvanced
    
    @pytest.mark.asyncio
    async def test_backward_compatibility(self):
        """Test compatibilidad hacia atrás."""
        # El clasificador debe poder trabajar sin contexto avanzado
        classifier = IntelligentTaskClassifier()
        
        # Test con inputs mínimos (como sistema actual)
        result = await classifier.classify_with_context(
            query="Test query",
            project_context={},
            user_history=[]
        )
        
        assert isinstance(result, ClassificationResult)
        assert result.primary_type is not None
    
    @pytest.mark.asyncio
    async def test_performance_under_load(self):
        """Test performance con múltiples clasificaciones."""
        classifier = IntelligentTaskClassifier()
        queries = [
            "¿Cómo implementar autenticación?",
            "Crear función de validación",
            "Diagnosticar error de conexión",
            "Optimizar query de base de datos",
            "Revisar código de seguridad"
        ]
        
        start_time = datetime.now()
        
        # Ejecutar múltiples clasificaciones
        tasks = [
            classifier.classify_with_context(query, {}, [])
            for query in queries
        ]
        results = await asyncio.gather(*tasks)
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        # Verificar resultados
        assert len(results) == len(queries)
        assert all(isinstance(result, ClassificationResult) for result in results)
        
        # Performance: debería completar 5 clasificaciones en menos de 10 segundos
        assert execution_time < 10.0
        
        logger.info(f"5 clasificaciones completadas en {execution_time:.2f} segundos")


class TestClassificationAccuracy:
    """Tests de accuracy del clasificador."""
    
    @pytest.fixture
    def test_cases(self):
        """Casos de test con clasificaciones esperadas."""
        return [
            {
                'query': '¿Cómo configurar Django settings?',
                'expected': TaskTypeAdvanced.PROCEDURAL,
                'context': {'frameworks': ['django']}
            },
            {
                'query': 'Implementar endpoint POST /users',
                'expected': TaskTypeAdvanced.CODE,
                'context': {'frameworks': ['fastapi']}
            },
            {
                'query': 'Error 500 en login endpoint',
                'expected': TaskTypeAdvanced.DIAGNOSTIC,
                'context': {}
            },
            {
                'query': 'Auditar vulnerabilidades de seguridad',
                'expected': TaskTypeAdvanced.SECURITY_AUDIT,
                'context': {'maturity_level': 'enterprise'}
            },
            {
                'query': 'Optimizar rendimiento de queries',
                'expected': TaskTypeAdvanced.PERFORMANCE_OPTIMIZATION,
                'context': {'complexity_score': 0.8}
            }
        ]
    
    @pytest.mark.asyncio
    async def test_classification_accuracy(self, test_cases):
        """Test accuracy general del clasificador."""
        classifier = IntelligentTaskClassifier()
        
        correct_predictions = 0
        total_predictions = len(test_cases)
        
        for test_case in test_cases:
            result = await classifier.classify_with_context(
                test_case['query'],
                test_case['context'],
                []
            )
            
            if result.primary_type == test_case['expected']:
                correct_predictions += 1
            else:
                # Verificar si está en tipos secundarios
                if test_case['expected'] in result.secondary_types:
                    correct_predictions += 0.5  # Crédito parcial
        
        accuracy = correct_predictions / total_predictions
        
        # El clasificador debería tener al menos 60% accuracy sin entrenamiento
        assert accuracy >= 0.6
        
        logger.info(f"Accuracy del clasificador: {accuracy:.1%}")


@pytest.mark.performance
class TestPerformanceRequirements:
    """Tests de requerimientos de performance."""
    
    @pytest.mark.asyncio
    async def test_classification_speed(self):
        """Test velocidad de clasificación."""
        classifier = IntelligentTaskClassifier()
        query = "¿Cómo implementar cache en Redis?"
        
        start_time = datetime.now()
        result = await classifier.classify_with_context(query, {}, [])
        end_time = datetime.now()
        
        execution_time = (end_time - start_time).total_seconds()
        
        # Clasificación debe completarse en menos de 5 segundos
        assert execution_time < 5.0
        assert isinstance(result, ClassificationResult)
        
        logger.info(f"Clasificación completada en {execution_time:.3f} segundos")
    
    @pytest.mark.asyncio
    async def test_memory_usage(self):
        """Test uso de memoria del clasificador."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Crear múltiples clasificadores
        classifiers = [IntelligentTaskClassifier() for _ in range(5)]
        
        # Ejecutar clasificaciones
        for i, classifier in enumerate(classifiers):
            await classifier.classify_with_context(f"Query {i}", {}, [])
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # No debería usar más de 100MB adicionales
        assert memory_increase < 100
        
        logger.info(f"Incremento de memoria: {memory_increase:.1f} MB")


if __name__ == "__main__":
    # Ejecutar tests básicos
    pytest.main([__file__, "-v"])
