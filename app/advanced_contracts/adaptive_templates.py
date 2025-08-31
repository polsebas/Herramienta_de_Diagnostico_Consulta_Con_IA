"""
Adaptive Template Engine - Sistema de plantillas dinámicas

Este módulo implementa un motor de plantillas que se adapta automáticamente
al contexto del proyecto, generando contratos personalizados según:
- Tipo de proyecto (Django, FastAPI, React, etc.)
- Arquitectura (monolito, microservicios, serverless)
- Equipo (tamaño, experiencia, metodología)
- Historial de éxito de plantillas similares
"""

import logging
import yaml
import json
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from pathlib import Path
import re

from .intelligent_classifier import TaskTypeAdvanced

logger = logging.getLogger(__name__)


class ProjectType(Enum):
    """Tipos de proyecto detectados automáticamente."""
    DJANGO_WEB = "django_web"
    FASTAPI_API = "fastapi_api"
    REACT_FRONTEND = "react_frontend"
    PYTHON_CLI = "python_cli"
    MICROSERVICES = "microservices"
    DATA_SCIENCE = "data_science"
    MACHINE_LEARNING = "machine_learning"
    DEVOPS_INFRA = "devops_infra"
    MOBILE_APP = "mobile_app"
    GENERIC = "generic"


class ArchitecturePattern(Enum):
    """Patrones arquitecturales detectados."""
    MONOLITH = "monolith"
    MICROSERVICES = "microservices"
    SERVERLESS = "serverless"
    LAYERED = "layered"
    EVENT_DRIVEN = "event_driven"
    HEXAGONAL = "hexagonal"
    MVC = "mvc"
    MVP = "mvp"
    CLEAN_ARCHITECTURE = "clean_architecture"


@dataclass
class ProjectProfile:
    """Perfil completo del proyecto analizado."""
    project_type: ProjectType
    architecture_pattern: ArchitecturePattern
    frameworks: List[str]
    languages: List[str]
    complexity_score: float
    team_size: int
    maturity_level: str  # 'startup', 'growing', 'mature', 'enterprise'
    has_tests: bool
    has_ci_cd: bool
    has_documentation: bool
    lines_of_code: int
    git_activity: Dict[str, Any]
    conventions: Dict[str, Any]


@dataclass
class AdaptiveTemplate:
    """Template adaptado dinámicamente al contexto."""
    base_template_id: str
    adapted_goal: str
    adapted_musts: List[str]
    adapted_format: str
    adapted_metrics: Dict[str, Any]
    project_specific_requirements: List[str]
    framework_specific_guidelines: List[str]
    team_specific_adjustments: List[str]
    risk_multipliers: Dict[str, float]
    estimated_complexity: float
    adaptation_reasoning: str


class ProjectProfiler:
    """Analizador de proyectos para crear perfiles detallados."""
    
    def __init__(self):
        self.framework_detectors = self._initialize_framework_detectors()
        self.architecture_analyzers = self._initialize_architecture_analyzers()
        
    def _initialize_framework_detectors(self) -> Dict[str, Dict[str, Any]]:
        """Inicializa detectores de frameworks."""
        return {
            'django': {
                'files': ['manage.py', 'settings.py', 'urls.py'],
                'imports': ['django', 'django.conf', 'django.urls'],
                'patterns': [r'from django\.', r'DJANGO_SETTINGS_MODULE']
            },
            'fastapi': {
                'files': ['main.py', 'app.py'],
                'imports': ['fastapi', 'uvicorn'],
                'patterns': [r'from fastapi import', r'FastAPI\(\)']
            },
            'react': {
                'files': ['package.json', 'src/App.js', 'src/App.tsx'],
                'imports': ['react', 'react-dom'],
                'patterns': [r'import React', r'export default function']
            },
            'flask': {
                'files': ['app.py', 'run.py'],
                'imports': ['flask'],
                'patterns': [r'from flask import', r'Flask\(__name__\)']
            }
        }
    
    def _initialize_architecture_analyzers(self) -> Dict[str, callable]:
        """Inicializa analizadores de arquitectura."""
        return {
            'microservices': self._detect_microservices,
            'layered': self._detect_layered_architecture,
            'mvc': self._detect_mvc_pattern,
            'clean': self._detect_clean_architecture
        }
    
    async def analyze_project(self, project_path: str) -> ProjectProfile:
        """
        Analiza proyecto completo para crear perfil detallado.
        
        Args:
            project_path: Ruta al directorio del proyecto
            
        Returns:
            ProjectProfile con análisis completo
        """
        logger.info(f"Analizando proyecto en: {project_path}")
        
        try:
            project_path_obj = Path(project_path)
            
            # Detectar frameworks
            frameworks = await self._detect_frameworks(project_path_obj)
            
            # Detectar tipo de proyecto
            project_type = await self._detect_project_type(project_path_obj, frameworks)
            
            # Analizar arquitectura
            architecture = await self._analyze_architecture(project_path_obj)
            
            # Métricas de código
            code_metrics = await self._analyze_code_metrics(project_path_obj)
            
            # Analizar convenciones
            conventions = await self._analyze_conventions(project_path_obj)
            
            # Detectar herramientas
            tools = await self._detect_tools(project_path_obj)
            
            profile = ProjectProfile(
                project_type=project_type,
                architecture_pattern=architecture,
                frameworks=frameworks,
                languages=code_metrics['languages'],
                complexity_score=code_metrics['complexity'],
                team_size=self._estimate_team_size(project_path_obj),
                maturity_level=self._assess_maturity_level(code_metrics, tools),
                has_tests=tools['has_tests'],
                has_ci_cd=tools['has_ci_cd'],
                has_documentation=tools['has_documentation'],
                lines_of_code=code_metrics['lines_of_code'],
                git_activity=await self._analyze_git_activity(project_path_obj),
                conventions=conventions
            )
            
            logger.info(f"Proyecto analizado: {project_type.value}, "
                       f"arquitectura: {architecture.value}, "
                       f"complejidad: {code_metrics['complexity']:.2f}")
            
            return profile
            
        except Exception as e:
            logger.error(f"Error analizando proyecto: {e}")
            return self._create_default_profile()
    
    async def _detect_frameworks(self, project_path: Path) -> List[str]:
        """Detecta frameworks utilizados en el proyecto."""
        detected_frameworks = []
        
        for framework, detector in self.framework_detectors.items():
            # Verificar archivos característicos
            file_matches = any(
                (project_path / file).exists() 
                for file in detector['files']
            )
            
            # Verificar imports en archivos Python
            import_matches = False
            if file_matches:
                for py_file in project_path.rglob("*.py"):
                    try:
                        content = py_file.read_text(encoding='utf-8')
                        if any(imp in content for imp in detector['imports']):
                            import_matches = True
                            break
                    except Exception:
                        continue
            
            if file_matches and import_matches:
                detected_frameworks.append(framework)
        
        return detected_frameworks
    
    async def _detect_project_type(self, project_path: Path, frameworks: List[str]) -> ProjectType:
        """Detecta el tipo de proyecto basado en frameworks y estructura."""
        
        # Basado en frameworks detectados
        if 'django' in frameworks:
            return ProjectType.DJANGO_WEB
        elif 'fastapi' in frameworks:
            return ProjectType.FASTAPI_API
        elif 'react' in frameworks:
            return ProjectType.REACT_FRONTEND
        elif 'flask' in frameworks:
            return ProjectType.FASTAPI_API  # Tratamos Flask como API
        
        # Basado en estructura de archivos
        if (project_path / 'Dockerfile').exists() and len(list(project_path.rglob('service*'))) > 1:
            return ProjectType.MICROSERVICES
        
        if any(file.exists() for file in [
            project_path / 'requirements.txt',
            project_path / 'pyproject.toml',
            project_path / 'setup.py'
        ]):
            # Verificar si es CLI
            if (project_path / 'cli.py').exists() or any(
                'click' in req or 'argparse' in req 
                for req in self._read_requirements(project_path)
            ):
                return ProjectType.PYTHON_CLI
            
            # Verificar si es data science
            data_science_indicators = ['jupyter', 'pandas', 'numpy', 'scikit-learn', 'tensorflow']
            requirements = self._read_requirements(project_path)
            if any(indicator in ' '.join(requirements) for indicator in data_science_indicators):
                return ProjectType.DATA_SCIENCE
        
        return ProjectType.GENERIC
    
    def _read_requirements(self, project_path: Path) -> List[str]:
        """Lee requirements del proyecto."""
        requirements = []
        
        # requirements.txt
        req_file = project_path / 'requirements.txt'
        if req_file.exists():
            try:
                requirements.extend(req_file.read_text().splitlines())
            except Exception:
                pass
        
        # pyproject.toml (simplificado)
        pyproject_file = project_path / 'pyproject.toml'
        if pyproject_file.exists():
            try:
                content = pyproject_file.read_text()
                # Extraer dependencias básicas (regex simple)
                deps = re.findall(r'"([^"]+)"', content)
                requirements.extend(deps)
            except Exception:
                pass
        
        return requirements
    
    async def _analyze_architecture(self, project_path: Path) -> ArchitecturePattern:
        """Analiza patrones arquitecturales del proyecto."""
        
        # Detectar microservicios
        if await self._detect_microservices(project_path):
            return ArchitecturePattern.MICROSERVICES
        
        # Detectar arquitectura en capas
        if await self._detect_layered_architecture(project_path):
            return ArchitecturePattern.LAYERED
        
        # Detectar MVC
        if await self._detect_mvc_pattern(project_path):
            return ArchitecturePattern.MVC
        
        # Por defecto, monolito
        return ArchitecturePattern.MONOLITH
    
    async def _detect_microservices(self, project_path: Path) -> bool:
        """Detecta si es arquitectura de microservicios."""
        indicators = [
            len(list(project_path.rglob('Dockerfile'))) > 1,
            (project_path / 'docker-compose.yml').exists(),
            len(list(project_path.rglob('service*'))) > 2,
            (project_path / 'kubernetes').exists(),
            len(list(project_path.rglob('*service*.py'))) > 3
        ]
        
        return sum(indicators) >= 2
    
    async def _detect_layered_architecture(self, project_path: Path) -> bool:
        """Detecta arquitectura en capas."""
        layer_indicators = ['models', 'views', 'controllers', 'services', 'repositories']
        
        found_layers = 0
        for indicator in layer_indicators:
            if any(indicator in str(p) for p in project_path.rglob('*')):
                found_layers += 1
        
        return found_layers >= 3
    
    async def _detect_mvc_pattern(self, project_path: Path) -> bool:
        """Detecta patrón MVC."""
        mvc_indicators = ['models', 'views', 'controllers']
        
        return all(
            any(indicator in str(p) for p in project_path.rglob('*'))
            for indicator in mvc_indicators
        )
    
    async def _analyze_code_metrics(self, project_path: Path) -> Dict[str, Any]:
        """Analiza métricas básicas del código."""
        metrics = {
            'lines_of_code': 0,
            'file_count': 0,
            'languages': [],
            'complexity': 0.5
        }
        
        try:
            # Contar archivos y líneas
            for file_path in project_path.rglob('*'):
                if file_path.is_file() and file_path.suffix in ['.py', '.js', '.ts', '.java', '.go']:
                    metrics['file_count'] += 1
                    try:
                        content = file_path.read_text(encoding='utf-8')
                        metrics['lines_of_code'] += len(content.splitlines())
                        
                        # Detectar lenguaje
                        if file_path.suffix == '.py' and 'python' not in metrics['languages']:
                            metrics['languages'].append('python')
                        elif file_path.suffix in ['.js', '.ts'] and 'javascript' not in metrics['languages']:
                            metrics['languages'].append('javascript')
                        
                    except Exception:
                        continue
            
            # Calcular complejidad estimada
            if metrics['lines_of_code'] > 50000:
                metrics['complexity'] = 0.9
            elif metrics['lines_of_code'] > 10000:
                metrics['complexity'] = 0.7
            elif metrics['lines_of_code'] > 1000:
                metrics['complexity'] = 0.5
            else:
                metrics['complexity'] = 0.3
                
        except Exception as e:
            logger.warning(f"Error analizando métricas: {e}")
        
        return metrics
    
    async def _analyze_conventions(self, project_path: Path) -> Dict[str, Any]:
        """Analiza convenciones de código del proyecto."""
        conventions = {
            'naming_style': 'snake_case',  # Por defecto Python
            'max_line_length': 88,
            'docstring_style': 'google',
            'import_style': 'absolute',
            'test_framework': 'pytest'
        }
        
        # Detectar convenciones reales analizando archivos
        try:
            for py_file in list(project_path.rglob('*.py'))[:10]:  # Analizar máximo 10 archivos
                content = py_file.read_text(encoding='utf-8')
                
                # Detectar estilo de naming
                if re.search(r'def [a-z]+[A-Z]', content):
                    conventions['naming_style'] = 'camelCase'
                
                # Detectar framework de testing
                if 'import unittest' in content:
                    conventions['test_framework'] = 'unittest'
                elif 'import pytest' in content:
                    conventions['test_framework'] = 'pytest'
                
        except Exception as e:
            logger.warning(f"Error analizando convenciones: {e}")
        
        return conventions
    
    async def _detect_tools(self, project_path: Path) -> Dict[str, bool]:
        """Detecta herramientas utilizadas en el proyecto."""
        tools = {
            'has_tests': False,
            'has_ci_cd': False,
            'has_documentation': False,
            'has_linting': False,
            'has_type_checking': False
        }
        
        # Detectar tests
        test_indicators = ['test_', 'tests/', 'pytest.ini', 'conftest.py']
        tools['has_tests'] = any(
            list(project_path.rglob(f'*{indicator}*'))
            for indicator in test_indicators
        )
        
        # Detectar CI/CD
        ci_indicators = ['.github/workflows', '.gitlab-ci.yml', 'Jenkinsfile', '.circleci']
        tools['has_ci_cd'] = any(
            (project_path / indicator).exists()
            for indicator in ci_indicators
        )
        
        # Detectar documentación
        doc_indicators = ['README.md', 'docs/', 'documentation/']
        tools['has_documentation'] = any(
            (project_path / indicator).exists()
            for indicator in doc_indicators
        )
        
        return tools
    
    async def _analyze_git_activity(self, project_path: Path) -> Dict[str, Any]:
        """Analiza actividad de Git (simplificado)."""
        return {
            'commits_last_month': 10,  # Placeholder
            'contributors': 3,
            'branches': 5,
            'last_commit': datetime.now().isoformat()
        }
    
    def _estimate_team_size(self, project_path: Path) -> int:
        """Estima tamaño del equipo basado en patrones del código."""
        # Heurísticas simples
        try:
            python_files = list(project_path.rglob('*.py'))
            if len(python_files) > 100:
                return 8  # Equipo grande
            elif len(python_files) > 50:
                return 5  # Equipo mediano
            elif len(python_files) > 10:
                return 3  # Equipo pequeño
            else:
                return 1  # Individual
        except Exception:
            return 3  # Por defecto
    
    def _assess_maturity_level(self, code_metrics: Dict[str, Any], tools: Dict[str, bool]) -> str:
        """Evalúa nivel de madurez del proyecto."""
        maturity_score = 0
        
        # Factores de madurez
        if code_metrics['lines_of_code'] > 10000:
            maturity_score += 2
        elif code_metrics['lines_of_code'] > 1000:
            maturity_score += 1
        
        if tools['has_tests']:
            maturity_score += 2
        if tools['has_ci_cd']:
            maturity_score += 2
        if tools['has_documentation']:
            maturity_score += 1
        
        # Clasificar nivel
        if maturity_score >= 6:
            return 'enterprise'
        elif maturity_score >= 4:
            return 'mature'
        elif maturity_score >= 2:
            return 'growing'
        else:
            return 'startup'
    
    def _create_default_profile(self) -> ProjectProfile:
        """Crea perfil por defecto cuando falla el análisis."""
        return ProjectProfile(
            project_type=ProjectType.GENERIC,
            architecture_pattern=ArchitecturePattern.MONOLITH,
            frameworks=[],
            languages=['python'],
            complexity_score=0.5,
            team_size=3,
            maturity_level='growing',
            has_tests=False,
            has_ci_cd=False,
            has_documentation=False,
            lines_of_code=1000,
            git_activity={},
            conventions={}
        )


class AdaptiveTemplateEngine:
    """
    Motor de plantillas que se adapta dinámicamente al contexto del proyecto.
    """
    
    def __init__(self, templates_path: str = "config/advanced_contracts/adaptive_templates"):
        """
        Inicializa el motor de templates adaptativos.
        
        Args:
            templates_path: Directorio con templates adaptativos
        """
        self.templates_path = Path(templates_path)
        self.base_templates = self._load_base_templates()
        self.project_profiler = ProjectProfiler()
        self.adaptation_rules = self._load_adaptation_rules()
        
        logger.info("AdaptiveTemplateEngine inicializado")
    
    def _load_base_templates(self) -> Dict[str, Dict[str, Any]]:
        """Carga templates base desde el sistema actual."""
        base_templates = {}
        
        # Cargar desde app/specs/ (sistema actual)
        specs_path = Path("app/specs")
        if specs_path.exists():
            for template_file in specs_path.glob("*.yaml"):
                try:
                    with open(template_file, 'r', encoding='utf-8') as f:
                        template_data = yaml.safe_load(f)
                        template_name = template_file.stem
                        base_templates[template_name] = template_data
                except Exception as e:
                    logger.warning(f"Error cargando template {template_file}: {e}")
        
        # Templates por defecto si no se encuentran
        if not base_templates:
            base_templates = self._get_default_templates()
        
        return base_templates
    
    def _get_default_templates(self) -> Dict[str, Dict[str, Any]]:
        """Templates por defecto para fallback."""
        return {
            'procedural': {
                'goal_template': "Proporcionar pasos claros y accionables para: {query}",
                'musts': [
                    "Usar solo información de fuentes verificadas y citarlas",
                    "Incluir pasos numerados y secuenciales",
                    "Incluir sección 'Fuentes' con referencias precisas"
                ],
                'format': "Markdown con pasos numerados",
                'metrics': {'max_tokens': 1000, 'clarity_score': 0.9}
            },
            'code': {
                'goal_template': "Generar código funcional y bien documentado para: {query}",
                'musts': [
                    "Incluir comentarios explicativos",
                    "Seguir mejores prácticas del lenguaje",
                    "Incluir ejemplos de uso"
                ],
                'format': "Código con comentarios y documentación",
                'metrics': {'max_tokens': 1500, 'code_quality': 0.9}
            }
        }
    
    def _load_adaptation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Carga reglas de adaptación por tipo de proyecto."""
        return {
            ProjectType.DJANGO_WEB.value: {
                'risk_multipliers': {'security': 1.5, 'database': 1.3, 'deployment': 1.2},
                'additional_musts': [
                    "Considerar migraciones de Django si afecta modelos",
                    "Verificar compatibilidad con versión de Django",
                    "Incluir tests unitarios con Django TestCase"
                ],
                'framework_guidelines': [
                    "Seguir convenciones de Django (PEP 8 + Django style)",
                    "Usar Django ORM para operaciones de base de datos",
                    "Implementar vistas basadas en clases cuando sea apropiado"
                ]
            },
            ProjectType.FASTAPI_API.value: {
                'risk_multipliers': {'api': 1.4, 'security': 1.3, 'performance': 1.2},
                'additional_musts': [
                    "Incluir documentación OpenAPI/Swagger",
                    "Implementar validación con Pydantic",
                    "Considerar rate limiting y autenticación"
                ],
                'framework_guidelines': [
                    "Usar type hints en todas las funciones",
                    "Implementar dependency injection",
                    "Seguir convenciones de FastAPI para endpoints"
                ]
            },
            ProjectType.MICROSERVICES.value: {
                'risk_multipliers': {'deployment': 1.8, 'networking': 1.4, 'monitoring': 1.3},
                'additional_musts': [
                    "Considerar impacto en otros servicios",
                    "Implementar health checks",
                    "Incluir logging distribuido y tracing"
                ],
                'framework_guidelines': [
                    "Mantener contratos de API estables",
                    "Implementar circuit breakers",
                    "Usar versionado semántico para APIs"
                ]
            }
        }
    
    async def generate_adaptive_template(self,
                                       task_type: TaskTypeAdvanced,
                                       project_profile: ProjectProfile,
                                       user_preferences: Optional[Dict[str, Any]] = None) -> AdaptiveTemplate:
        """
        Genera template adaptado al contexto específico.
        
        Args:
            task_type: Tipo de tarea clasificado
            project_profile: Perfil del proyecto
            user_preferences: Preferencias del usuario (opcional)
            
        Returns:
            AdaptiveTemplate personalizado
        """
        logger.info(f"Generando template adaptativo para {task_type.value} "
                   f"en proyecto {project_profile.project_type.value}")
        
        try:
            # Seleccionar template base
            base_template = self._select_base_template(task_type)
            
            # Adaptar según perfil del proyecto
            adapted_template = await self._adapt_to_project(base_template, project_profile)
            
            # Personalizar según usuario
            if user_preferences:
                adapted_template = await self._personalize_for_user(adapted_template, user_preferences)
            
            # Calcular complejidad estimada
            complexity = self._estimate_task_complexity(task_type, project_profile)
            
            return AdaptiveTemplate(
                base_template_id=base_template['id'],
                adapted_goal=adapted_template['goal'],
                adapted_musts=adapted_template['musts'],
                adapted_format=adapted_template['format'],
                adapted_metrics=adapted_template['metrics'],
                project_specific_requirements=adapted_template['project_requirements'],
                framework_specific_guidelines=adapted_template['framework_guidelines'],
                team_specific_adjustments=adapted_template['team_adjustments'],
                risk_multipliers=adapted_template['risk_multipliers'],
                estimated_complexity=complexity,
                adaptation_reasoning=adapted_template['reasoning']
            )
            
        except Exception as e:
            logger.error(f"Error generando template adaptativo: {e}")
            return self._create_fallback_template(task_type)
    
    def _select_base_template(self, task_type: TaskTypeAdvanced) -> Dict[str, Any]:
        """Selecciona template base según tipo de tarea."""
        # Mapear tipos avanzados a templates base
        type_mapping = {
            TaskTypeAdvanced.PROCEDURAL: 'procedural',
            TaskTypeAdvanced.CODE: 'code',
            TaskTypeAdvanced.DIAGNOSTIC: 'diagnostic',
            TaskTypeAdvanced.SECURITY_AUDIT: 'procedural',  # Usar procedural como base
            TaskTypeAdvanced.PERFORMANCE_OPTIMIZATION: 'code',  # Usar code como base
            TaskTypeAdvanced.ARCHITECTURE_DESIGN: 'procedural'
        }
        
        base_type = type_mapping.get(task_type, 'procedural')
        template = self.base_templates.get(base_type, self.base_templates['procedural'])
        
        # Añadir ID para tracking
        template['id'] = f"{base_type}_{task_type.value}"
        
        return template
    
    async def _adapt_to_project(self, base_template: Dict[str, Any], 
                              project_profile: ProjectProfile) -> Dict[str, Any]:
        """Adapta template según perfil del proyecto."""
        adapted = base_template.copy()
        
        # Obtener reglas de adaptación para este tipo de proyecto
        adaptation_rules = self.adaptation_rules.get(
            project_profile.project_type.value, {}
        )
        
        # Adaptar goal
        adapted['goal'] = base_template['goal_template']
        
        # Añadir musts específicos del proyecto
        adapted['musts'] = base_template['musts'].copy()
        if 'additional_musts' in adaptation_rules:
            adapted['musts'].extend(adaptation_rules['additional_musts'])
        
        # Añadir guidelines específicos del framework
        adapted['framework_guidelines'] = adaptation_rules.get('framework_guidelines', [])
        
        # Aplicar multiplicadores de riesgo
        adapted['risk_multipliers'] = adaptation_rules.get('risk_multipliers', {})
        
        # Ajustar métricas según complejidad del proyecto
        adapted['metrics'] = base_template['metrics'].copy()
        if project_profile.complexity_score > 0.8:
            adapted['metrics']['max_tokens'] = int(adapted['metrics'].get('max_tokens', 1000) * 1.5)
        
        # Añadir requirements específicos del proyecto
        project_requirements = []
        
        if project_profile.has_tests:
            project_requirements.append("Incluir tests apropiados para el framework")
        
        if project_profile.has_ci_cd:
            project_requirements.append("Considerar impacto en pipeline de CI/CD")
        
        if project_profile.maturity_level == 'enterprise':
            project_requirements.extend([
                "Seguir estándares enterprise de la organización",
                "Incluir documentación de arquitectura si aplica",
                "Considerar impacto en compliance y auditoría"
            ])
        
        adapted['project_requirements'] = project_requirements
        
        # Ajustes específicos del equipo
        team_adjustments = []
        
        if project_profile.team_size > 5:
            team_adjustments.append("Coordinar con múltiples miembros del equipo")
        
        if project_profile.maturity_level in ['startup', 'growing']:
            team_adjustments.append("Priorizar simplicidad y velocidad de implementación")
        
        adapted['team_adjustments'] = team_adjustments
        
        # Reasoning de la adaptación
        adapted['reasoning'] = (
            f"Template adaptado para proyecto {project_profile.project_type.value} "
            f"con arquitectura {project_profile.architecture_pattern.value}, "
            f"complejidad {project_profile.complexity_score:.1f}, "
            f"equipo de {project_profile.team_size} personas, "
            f"nivel {project_profile.maturity_level}"
        )
        
        return adapted
    
    async def _personalize_for_user(self, template: Dict[str, Any], 
                                  user_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Personaliza template según preferencias del usuario."""
        personalized = template.copy()
        
        # Ajustar nivel de detalle
        detail_level = user_preferences.get('detail_level', 'medium')
        if detail_level == 'high':
            personalized['musts'].append("Incluir explicaciones detalladas de cada paso")
        elif detail_level == 'low':
            personalized['musts'] = [must for must in personalized['musts'] 
                                   if 'detallado' not in must.lower()]
        
        # Ajustar formato preferido
        format_preference = user_preferences.get('format', 'markdown')
        if format_preference == 'json':
            personalized['format'] = "JSON estructurado con campos obligatorios"
        elif format_preference == 'yaml':
            personalized['format'] = "YAML con estructura jerárquica"
        
        # Ajustar según experiencia del usuario
        experience_level = user_preferences.get('experience_level', 'intermediate')
        if experience_level == 'beginner':
            personalized['musts'].append("Incluir explicaciones básicas de conceptos")
        elif experience_level == 'expert':
            personalized['musts'] = [must for must in personalized['musts']
                                   if 'básico' not in must.lower()]
        
        return personalized
    
    def _estimate_task_complexity(self, task_type: TaskTypeAdvanced, 
                                 project_profile: ProjectProfile) -> float:
        """Estima complejidad de la tarea."""
        base_complexity = {
            TaskTypeAdvanced.PROCEDURAL: 0.3,
            TaskTypeAdvanced.CODE: 0.6,
            TaskTypeAdvanced.DIAGNOSTIC: 0.5,
            TaskTypeAdvanced.SECURITY_AUDIT: 0.8,
            TaskTypeAdvanced.PERFORMANCE_OPTIMIZATION: 0.7,
            TaskTypeAdvanced.ARCHITECTURE_DESIGN: 0.9
        }.get(task_type, 0.5)
        
        # Ajustar según proyecto
        project_multiplier = 1.0
        if project_profile.complexity_score > 0.8:
            project_multiplier += 0.3
        if project_profile.architecture_pattern == ArchitecturePattern.MICROSERVICES:
            project_multiplier += 0.2
        if project_profile.maturity_level == 'enterprise':
            project_multiplier += 0.1
        
        return min(1.0, base_complexity * project_multiplier)
    
    def _create_fallback_template(self, task_type: TaskTypeAdvanced) -> AdaptiveTemplate:
        """Crea template de fallback cuando falla la adaptación."""
        return AdaptiveTemplate(
            base_template_id="fallback",
            adapted_goal=f"Completar tarea de tipo {task_type.value}",
            adapted_musts=["Usar información verificada", "Citar fuentes"],
            adapted_format="Markdown estructurado",
            adapted_metrics={'max_tokens': 1000},
            project_specific_requirements=[],
            framework_specific_guidelines=[],
            team_specific_adjustments=[],
            risk_multipliers={},
            estimated_complexity=0.5,
            adaptation_reasoning="Template de fallback - adaptación básica"
        )


# Función de conveniencia para integración
async def generate_adaptive_contract_template(
    task_type: TaskTypeAdvanced,
    project_path: str,
    user_preferences: Optional[Dict[str, Any]] = None
) -> AdaptiveTemplate:
    """
    Función de conveniencia para generar template adaptativo.
    
    Args:
        task_type: Tipo de tarea clasificado
        project_path: Ruta al proyecto
        user_preferences: Preferencias del usuario
        
    Returns:
        AdaptiveTemplate personalizado
    """
    profiler = ProjectProfiler()
    template_engine = AdaptiveTemplateEngine()
    
    # Analizar proyecto
    project_profile = await profiler.analyze_project(project_path)
    
    # Generar template adaptativo
    return await template_engine.generate_adaptive_template(
        task_type, project_profile, user_preferences
    )
