import os
import subprocess
import json
import ast
from pathlib import Path
from typing import Dict, List, Any, Optional
from openai import OpenAI
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgenteAnalizador:
    """
    Agente de análisis basado en IA para evaluar sistemas de software ajenos.
    Implementa análisis funcional y técnico profundo según documentos.md
    """
    
    def __init__(self, root_dir: str, openai_api_key: Optional[str] = None):
        """Inicializa el agente con el directorio raíz del proyecto."""
        self.root_dir = Path(root_dir)
        self.openai_client = OpenAI(api_key=openai_api_key) if openai_api_key else None
        
        # Resultados del análisis
        self.analysis_results = {
            'funcional': {},
            'tecnico': {},
            'integracion': {}
        }
        
        # Clasificación de archivos
        self.documentation_files = []
        self.code_files = []
        self.config_files = []
        self.other_files = []

    def classify_file(self, file_path: Path) -> str:
        """Clasifica el tipo de archivo según su extensión o nombre."""
        file_str = str(file_path).lower()
        
        if file_path.suffix in ('.py', '.js', '.java', '.cs', '.php', '.rb', '.go'):
            return 'code'
        elif file_path.suffix in ('.json', '.yml', '.yaml', '.toml', '.ini', '.conf'):
            return 'config'
        elif (file_path.suffix in ('.md', '.txt', '.pdf', '.doc', '.docx') or 
              'readme' in file_str or 'docs' in file_str):
            return 'documentation'
        else:
            return 'other'

    def scan_project_structure(self):
        """Escanea y clasifica todos los archivos del proyecto."""
        logger.info(f"Escaneando estructura del proyecto: {self.root_dir}")
        
        for file_path in self.root_dir.rglob('*'):
            if file_path.is_file():
                file_type = self.classify_file(file_path)
                
                if file_type == 'documentation':
                    self.documentation_files.append(file_path)
                elif file_type == 'code':
                    self.code_files.append(file_path)
                elif file_type == 'config':
                    self.config_files.append(file_path)
                else:
                    self.other_files.append(file_path)
        
        logger.info(f"Archivos encontrados: {len(self.documentation_files)} docs, "
                   f"{len(self.code_files)} código, {len(self.config_files)} config")

    # ===== ANÁLISIS FUNCIONAL =====
    
    def analisis_funcional(self):
        """Realiza el análisis funcional: propósito, servicios, interacciones."""
        logger.info("Iniciando análisis funcional...")
        
        # 1. Revisión de documentación
        self._analizar_documentacion()
        
        # 2. Exploración de interfaces
        self._analizar_interfaces()
        
        # 3. Simulación de entrevistas
        self._simular_entrevistas()
        
        # 4. Crear diagramas de flujo (representación textual)
        self._crear_diagramas_flujo()

    def _analizar_documentacion(self):
        """Analiza manuales, guías y documentación disponible."""
        logger.info("Analizando documentación...")
        
        documentacion_texto = ""
        for doc_file in self.documentation_files:
            try:
                with open(doc_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    documentacion_texto += f"\n--- {doc_file.name} ---\n{content}\n"
            except Exception as e:
                logger.warning(f"No se pudo leer {doc_file}: {e}")
        
        if documentacion_texto and self.openai_client:
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Eres un analista experto en sistemas. Analiza la documentación para identificar el propósito del sistema, sus servicios principales y funcionalidades clave."},
                        {"role": "user", "content": f"Analiza esta documentación y extrae:\n1. Propósito principal del sistema\n2. Servicios y funcionalidades\n3. Usuarios objetivo\n4. Flujos principales\n\nDocumentación:\n{documentacion_texto}"}
                    ],
                    max_tokens=1000
                )
                self.analysis_results['funcional']['documentacion_analisis'] = response.choices[0].message.content
            except Exception as e:
                logger.error(f"Error analizando documentación: {e}")
                self.analysis_results['funcional']['documentacion_analisis'] = "Error en análisis de documentación"

    def _analizar_interfaces(self):
        """Examina interfaces de usuario y APIs."""
        logger.info("Analizando interfaces...")
        
        # Buscar archivos de interfaz
        interface_files = []
        for file_path in self.root_dir.rglob('*'):
            if file_path.suffix in ('.html', '.css', '.js', '.vue', '.react', '.api', '.swagger'):
                interface_files.append(file_path)
        
        # Analizar APIs
        api_files = list(self.root_dir.rglob('*.json')) + list(self.root_dir.rglob('*.yaml'))
        api_files = [f for f in api_files if 'api' in str(f).lower() or 'swagger' in str(f).lower()]
        
        interfaces_info = {
            'archivos_interfaz': [str(f) for f in interface_files],
            'archivos_api': [str(f) for f in api_files],
            'total_interfaces': len(interface_files),
            'total_apis': len(api_files)
        }
        
        self.analysis_results['funcional']['interfaces'] = interfaces_info

    def _simular_entrevistas(self):
        """Simula entrevistas con usuarios y stakeholders usando IA."""
        logger.info("Simulando entrevistas...")
        
        if not self.openai_client:
            self.analysis_results['funcional']['entrevistas'] = "OpenAI no configurado"
            return
        
        try:
            # Simular preguntas típicas de stakeholders
            preguntas = [
                "¿Cuál es el propósito principal de este sistema?",
                "¿Qué problemas resuelve este sistema?",
                "¿Quiénes son los usuarios principales?",
                "¿Cuáles son los flujos de trabajo más importantes?",
                "¿Qué funcionalidades son críticas para el negocio?"
            ]
            
            respuestas_simuladas = []
            for pregunta in preguntas:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Eres un stakeholder analizando un sistema. Responde basándote en la información disponible del proyecto."},
                        {"role": "user", "content": pregunta}
                    ],
                    max_tokens=300
                )
                respuestas_simuladas.append({
                    'pregunta': pregunta,
                    'respuesta': response.choices[0].message.content
                })
            
            self.analysis_results['funcional']['entrevistas'] = respuestas_simuladas
            
        except Exception as e:
            logger.error(f"Error en simulación de entrevistas: {e}")
            self.analysis_results['funcional']['entrevistas'] = f"Error: {e}"

    def _crear_diagramas_flujo(self):
        """Crea representaciones textuales de flujos principales."""
        logger.info("Creando diagramas de flujo...")
        
        # Identificar flujos principales basándose en la estructura del código
        flujos_principales = []
        
        # Buscar archivos principales (main, app, index, etc.)
        archivos_principales = []
        for file_path in self.code_files:
            if any(keyword in file_path.name.lower() for keyword in ['main', 'app', 'index', 'startup']):
                archivos_principales.append(str(file_path))
        
        # Crear descripción de flujos
        flujos_principales.append({
            'tipo': 'Inicialización',
            'archivos': archivos_principales,
            'descripcion': 'Flujo de inicio del sistema'
        })
        
        self.analysis_results['funcional']['diagramas_flujo'] = flujos_principales

    # ===== ANÁLISIS TÉCNICO PROFUNDO =====
    
    def analisis_tecnico_profundo(self):
        """Realiza el análisis técnico profundo: obsolescencia, arquitectura, deuda técnica."""
        logger.info("Iniciando análisis técnico profundo...")
        
        # 1. Análisis de código
        self._analizar_codigo()
        
        # 2. Revisión de dependencias
        self._analizar_dependencias()
        
        # 3. Evaluación arquitectónica
        self._evaluar_arquitectura()
        
        # 4. Simulación de rendimiento
        self._simular_rendimiento()
        
        # 5. Detección de oportunidades de IA
        self._detectar_oportunidades_ia()

    def _analizar_codigo(self):
        """Analiza calidad y seguridad del código."""
        logger.info("Analizando código...")
        
        analisis_codigo = {
            'archivos_analizados': len(self.code_files),
            'lenguajes': {},
            'metricas': {},
            'problemas_detectados': []
        }
        
        # Contar lenguajes
        for file_path in self.code_files:
            lang = file_path.suffix[1:] if file_path.suffix else 'unknown'
            analisis_codigo['lenguajes'][lang] = analisis_codigo['lenguajes'].get(lang, 0) + 1
        
        # Análisis específico para Python
        python_files = [f for f in self.code_files if f.suffix == '.py']
        if python_files:
            self._analizar_codigo_python(python_files, analisis_codigo)
        
        self.analysis_results['tecnico']['codigo'] = analisis_codigo

    def _analizar_codigo_python(self, python_files: List[Path], analisis: Dict):
        """Análisis específico para archivos Python."""
        logger.info(f"Analizando {len(python_files)} archivos Python...")
        
        problemas = []
        metricas = {
            'total_funciones': 0,
            'total_clases': 0,
            'archivos_con_errores': 0
        }
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Análisis AST
                tree = ast.parse(content)
                
                # Contar funciones y clases
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        metricas['total_funciones'] += 1
                    elif isinstance(node, ast.ClassDef):
                        metricas['total_clases'] += 1
                
                # Verificar complejidad
                if len(content.split('\n')) > 500:
                    problemas.append(f"{file_path.name}: Archivo muy largo (>500 líneas)")
                
            except SyntaxError as e:
                metricas['archivos_con_errores'] += 1
                problemas.append(f"{file_path.name}: Error de sintaxis - {e}")
            except Exception as e:
                problemas.append(f"{file_path.name}: Error de lectura - {e}")
        
        analisis['metricas'].update(metricas)
        analisis['problemas_detectados'].extend(problemas)

    def _analizar_dependencias(self):
        """Identifica bibliotecas y frameworks obsoletos."""
        logger.info("Analizando dependencias...")
        
        dependencias_info = {
            'archivos_config': [],
            'dependencias_detectadas': [],
            'posibles_obsolescencias': []
        }
        
        # Buscar archivos de dependencias
        for config_file in self.config_files:
            dependencias_info['archivos_config'].append(str(config_file))
            
            if config_file.name in ('requirements.txt', 'package.json', 'pom.xml', 'build.gradle'):
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Análisis básico de versiones
                    if config_file.name == 'requirements.txt':
                        for line in content.split('\n'):
                            if '==' in line:
                                pkg, version = line.split('==')
                                dependencias_info['dependencias_detectadas'].append({
                                    'paquete': pkg.strip(),
                                    'version': version.strip(),
                                    'archivo': str(config_file)
                                })
                
                except Exception as e:
                    logger.warning(f"Error leyendo {config_file}: {e}")
        
        self.analysis_results['tecnico']['dependencias'] = dependencias_info

    def _evaluar_arquitectura(self):
        """Analiza la estructura del sistema."""
        logger.info("Evaluando arquitectura...")
        
        arquitectura_info = {
            'tipo_estimado': 'Desconocido',
            'componentes_principales': [],
            'estructura_directorios': {},
            'patrones_detectados': []
        }
        
        # Analizar estructura de directorios
        dirs_principales = [d for d in self.root_dir.iterdir() if d.is_dir()]
        for dir_path in dirs_principales:
            if dir_path.name.lower() in ['src', 'app', 'lib', 'api', 'frontend', 'backend']:
                arquitectura_info['componentes_principales'].append(str(dir_path))
        
        # Detectar patrones
        if any('api' in str(d).lower() for d in dirs_principales):
            arquitectura_info['patrones_detectados'].append('API REST')
        
        if len(self.code_files) > 100:
            arquitectura_info['tipo_estimado'] = 'Monolítico Grande'
        elif len(self.code_files) > 20:
            arquitectura_info['tipo_estimado'] = 'Monolítico'
        else:
            arquitectura_info['tipo_estimado'] = 'Aplicación Simple'
        
        self.analysis_results['tecnico']['arquitectura'] = arquitectura_info

    def _simular_rendimiento(self):
        """Revisa logs y simula análisis de rendimiento."""
        logger.info("Simulando análisis de rendimiento...")
        
        rendimiento_info = {
            'logs_encontrados': [],
            'errores_detectados': 0,
            'respuestas_lentas': 0,
            'recomendaciones': []
        }
        
        # Buscar archivos de log
        log_files = list(self.root_dir.rglob('*.log')) + list(self.root_dir.rglob('*.txt'))
        log_files = [f for f in log_files if 'log' in f.name.lower()]
        
        for log_file in log_files:
            rendimiento_info['logs_encontrados'].append(str(log_file))
            
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # Contar errores
                errores = [line for line in lines if 'error' in line.lower()]
                rendimiento_info['errores_detectados'] += len(errores)
                
                # Detectar respuestas lentas
                lentas = [line for line in lines if 'time' in line.lower() and any(char.isdigit() for char in line)]
                rendimiento_info['respuestas_lentas'] += len(lentas)
                
            except Exception as e:
                logger.warning(f"Error analizando log {log_file}: {e}")
        
        # Recomendaciones básicas
        if rendimiento_info['errores_detectados'] > 10:
            rendimiento_info['recomendaciones'].append("Implementar mejor manejo de errores")
        
        if rendimiento_info['respuestas_lentas'] > 5:
            rendimiento_info['recomendaciones'].append("Optimizar consultas y operaciones")
        
        self.analysis_results['tecnico']['rendimiento'] = rendimiento_info

    def _detectar_oportunidades_ia(self):
        """Busca oportunidades para integrar IA en el código."""
        logger.info("Detectando oportunidades de IA...")
        
        oportunidades = []
        keywords_ia = [
            'predict', 'classify', 'analyze', 'recommend', 'learn', 'model',
            'predicción', 'clasificación', 'análisis', 'recomendación', 'aprendizaje'
        ]
        
        for code_file in self.code_files:
            try:
                with open(code_file, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                
                # Buscar palabras clave de IA
                encontradas = [kw for kw in keywords_ia if kw in content]
                
                if encontradas:
                    oportunidades.append({
                        'archivo': str(code_file),
                        'palabras_clave': encontradas,
                        'oportunidad': f"Posible integración de IA en {code_file.name}"
                    })
            
            except Exception as e:
                logger.warning(f"Error analizando {code_file}: {e}")
        
        self.analysis_results['tecnico']['oportunidades_ia'] = oportunidades

    # ===== INTEGRACIÓN DE ANÁLISIS =====
    
    def integrar_analisis(self):
        """Combina análisis funcional y técnico para crear plan integral."""
        logger.info("Integrando análisis funcional y técnico...")
        
        if not self.openai_client:
            self.analysis_results['integracion'] = {
                'plan_modernizacion': "OpenAI no configurado para generar plan",
                'recomendaciones': []
            }
            return
        
        try:
            # Crear resumen para IA
            resumen = {
                'funcional': self.analysis_results['funcional'],
                'tecnico': self.analysis_results['tecnico']
            }
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Eres un experto en modernización de sistemas. Crea un plan integral basado en el análisis funcional y técnico."},
                    {"role": "user", "content": f"Basándote en este análisis, crea un plan de modernización:\n{json.dumps(resumen, indent=2)}"}
                ],
                max_tokens=1500
            )
            
            self.analysis_results['integracion']['plan_modernizacion'] = response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error en integración: {e}")
            self.analysis_results['integracion']['plan_modernizacion'] = f"Error generando plan: {e}"

    def run_analysis(self) -> Dict[str, Any]:
        """Ejecuta el análisis completo del sistema."""
        logger.info("Iniciando análisis completo del sistema...")
        
        # 1. Escanear estructura
        self.scan_project_structure()
        
        # 2. Análisis funcional
        self.analisis_funcional()
        
        # 3. Análisis técnico profundo
        self.analisis_tecnico_profundo()
        
        # 4. Integración
        self.integrar_analisis()
        
        logger.info("Análisis completado")
        return self.analysis_results

def generate_report(analysis_results: Dict[str, Any]) -> str:
    """Genera un informe en formato Markdown basado en los resultados del análisis."""
    report = "# Informe de Análisis del Sistema\n\n"
    report += "## Resumen Ejecutivo\n\n"
    report += "Este informe presenta el análisis funcional y técnico del sistema, "
    report += "incluyendo recomendaciones para su modernización.\n\n"
    
    # Análisis Funcional
    report += "## 1. Análisis Funcional\n\n"
    
    if 'documentacion_analisis' in analysis_results.get('funcional', {}):
        report += "### Propósito y Servicios\n"
        report += analysis_results['funcional']['documentacion_analisis'] + "\n\n"
    
    if 'interfaces' in analysis_results.get('funcional', {}):
        report += "### Interfaces Detectadas\n"
        interfaces = analysis_results['funcional']['interfaces']
        report += f"- Archivos de interfaz: {interfaces.get('total_interfaces', 0)}\n"
        report += f"- Archivos de API: {interfaces.get('total_apis', 0)}\n\n"
    
    # Análisis Técnico
    report += "## 2. Análisis Técnico Profundo\n\n"
    
    if 'codigo' in analysis_results.get('tecnico', {}):
        codigo = analysis_results['tecnico']['codigo']
        report += "### Análisis de Código\n"
        report += f"- Archivos analizados: {codigo.get('archivos_analizados', 0)}\n"
        report += f"- Funciones totales: {codigo.get('metricas', {}).get('total_funciones', 0)}\n"
        report += f"- Clases totales: {codigo.get('metricas', {}).get('total_clases', 0)}\n\n"
    
    if 'arquitectura' in analysis_results.get('tecnico', {}):
        arch = analysis_results['tecnico']['arquitectura']
        report += "### Arquitectura\n"
        report += f"- Tipo estimado: {arch.get('tipo_estimado', 'Desconocido')}\n"
        report += f"- Patrones detectados: {', '.join(arch.get('patrones_detectados', []))}\n\n"
    
    if 'oportunidades_ia' in analysis_results.get('tecnico', {}):
        report += "### Oportunidades de IA\n"
        for op in analysis_results['tecnico']['oportunidades_ia']:
            report += f"- {op['oportunidad']}\n"
        report += "\n"
    
    # Plan de Modernización
    report += "## 3. Plan de Modernización\n\n"
    if 'plan_modernizacion' in analysis_results.get('integracion', {}):
        report += analysis_results['integracion']['plan_modernizacion'] + "\n\n"
    
    report += "## 4. Conclusiones\n\n"
    report += "El análisis completo del sistema proporciona una base sólida para "
    report += "entender su propósito y planificar su modernización de manera efectiva.\n\n"
    
    return report

# Uso del agente
if __name__ == "__main__":
    # Configurar API key de OpenAI
    api_key = os.getenv('OPENAI_API_KEY')
    
    # Crear y ejecutar el agente
    agente = AgenteAnalizador('.', api_key)
    resultados = agente.run_analysis()
    
    # Generar informe
    informe = generate_report(resultados)
    
    # Guardar informe
    with open('informe_analisis_completo.md', 'w', encoding='utf-8') as f:
        f.write(informe)
    
    print("Análisis completado. Informe guardado en 'informe_analisis_completo.md'")