from agno import Agent, Team

# Crear agentes especializados
documentation_agent = Agent(
    name="DocumentationAgent",
    role="Analizar y resumir documentación",
    tools=["openai_gpt4o_mini"]
)

code_analysis_agent = Agent(
    name="CodeAnalysisAgent",
    role="Analizar código fuente",
    tools=["pylint"]
)

dependencies_agent = Agent(
    name="DependenciesAgent",
    role="Revisar dependencias",
    tools=["dependency_checker"]
)

architecture_agent = Agent(
    name="ArchitectureAgent",
    role="Analizar arquitectura",
    tools=["structure_analyzer"]
)

performance_agent = Agent(
    name="PerformanceAgent",
    role="Evaluar rendimiento",
    tools=["log_analyzer"]
)

ai_opportunities_agent = Agent(
    name="AIOpportunitiesAgent",
    role="Identificar oportunidades de IA",
    tools=["pattern_recognizer"]
)

# Nuevo Agente de Seguridad
security_agent = Agent(
    name="SecurityAgent",
    role="Analizar seguridad informática",
    tools=["bandit"]  # Herramienta para análisis de seguridad en Python
)

# Configurar el equipo de agentes
team = Team(
    agents=[
        documentation_agent,
        code_analysis_agent,
        dependencies_agent,
        architecture_agent,
        performance_agent,
        ai_opportunities_agent,
        security_agent  # Agregado al equipo
    ],
    coordinator=True  # Habilita el agente orquestador
)

# Ejecutar el análisis
results = team.run_analysis(project_dir="/ruta/al/proyecto")

# Generar un informe
report = generate_report(results)
with open('informe_analisis.md', 'w', encoding='utf-8') as f:
    f.write(report)