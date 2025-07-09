# Agente Analizador de Sistemas

## Descripción

El **Agente Analizador** es una herramienta basada en inteligencia artificial diseñada para evaluar sistemas de software ajenos con dos enfoques principales:

1. **Análisis Funcional**: Comprender qué hace el sistema, cuál es su propósito y qué servicios ofrece a los usuarios.
2. **Análisis Técnico Profundo**: Examinar la arquitectura, el código y las tecnologías subyacentes para desarrollar un plan de modernización.

## Características Principales

### 🔍 Análisis Funcional
- **Revisión de Documentación**: Analiza manuales, guías y documentación disponible
- **Exploración de Interfaces**: Examina interfaces de usuario y APIs
- **Simulación de Entrevistas**: Usa IA para generar preguntas y respuestas basadas en datos disponibles
- **Diagramas de Flujo**: Crea representaciones textuales de los procesos principales

### 🔧 Análisis Técnico Profundo
- **Análisis de Código**: Emplea análisis estático para evaluar calidad y seguridad
- **Revisión de Dependencias**: Identifica bibliotecas o frameworks obsoletos
- **Evaluación Arquitectónica**: Analiza la estructura del sistema y su capacidad de adaptación
- **Simulación de Rendimiento**: Revisa logs para detectar cuellos de botella
- **Detección de Oportunidades de IA**: Identifica áreas donde la IA pueda mejorar procesos

### 🤖 Integración de IA (Opcional)
- **Análisis de Documentación con IA**: Usa OpenAI para analizar y resumir documentación
- **Entrevistas Simuladas**: Genera preguntas y respuestas típicas de stakeholders
- **Plan de Modernización**: Crea planes integrales basados en análisis funcional y técnico

## Instalación

### Requisitos
```bash
python >= 3.8
pip
```

### Dependencias
```bash
pip install -r requirements.txt
```

### Configuración de OpenAI (Opcional)
Para usar análisis con IA, configura tu API key:
```bash
export OPENAI_API_KEY='tu-api-key-aqui'
```

## Uso

### Uso Básico

```python
from app.agente_analizador import AgenteAnalizador, generate_report

# Crear agente
agente = AgenteAnalizador('./ruta/al/proyecto')

# Ejecutar análisis completo
resultados = agente.run_analysis()

# Generar informe
informe = generate_report(resultados)

# Guardar informe
with open('informe_analisis.md', 'w', encoding='utf-8') as f:
    f.write(informe)
```

### Uso con IA

```python
from app.agente_analizador import AgenteAnalizador
import os

# Configurar OpenAI
api_key = os.getenv('OPENAI_API_KEY')
agente = AgenteAnalizador('./ruta/al/proyecto', api_key)

# Ejecutar análisis con IA
resultados = agente.run_analysis()
```

### Scripts de Demostración

#### Pruebas del Sistema
```bash
python test_agente_analizador.py
```

#### Demostración Completa
```bash
python demo_agente_analizador.py
```

## Estructura del Sistema

### Clase Principal: `AgenteAnalizador`

#### Métodos Principales

- `scan_project_structure()`: Escanea y clasifica archivos del proyecto
- `analisis_funcional()`: Realiza análisis funcional completo
- `analisis_tecnico_profundo()`: Realiza análisis técnico profundo
- `integrar_analisis()`: Combina análisis funcional y técnico
- `run_analysis()`: Ejecuta análisis completo

#### Métodos de Análisis Funcional

- `_analizar_documentacion()`: Analiza documentación disponible
- `_analizar_interfaces()`: Examina interfaces y APIs
- `_simular_entrevistas()`: Simula entrevistas con stakeholders
- `_crear_diagramas_flujo()`: Crea diagramas de flujo textuales

#### Métodos de Análisis Técnico

- `_analizar_codigo()`: Analiza calidad del código
- `_analizar_dependencias()`: Revisa dependencias y obsolescencias
- `_evaluar_arquitectura()`: Evalúa arquitectura del sistema
- `_simular_rendimiento()`: Analiza rendimiento y logs
- `_detectar_oportunidades_ia()`: Busca oportunidades de integración de IA

## Salidas del Sistema

### Informe de Análisis

El sistema genera un informe completo en formato Markdown que incluye:

1. **Resumen Ejecutivo**: Descripción general del análisis
2. **Análisis Funcional**: Propósito, servicios e interacciones
3. **Análisis Técnico Profundo**: Arquitectura, obsolescencias, oportunidades
4. **Plan de Modernización**: Recomendaciones específicas (con IA)
5. **Conclusiones**: Resumen de hallazgos

### Estructura de Resultados

```python
{
    'funcional': {
        'documentacion_analisis': 'Análisis de documentación...',
        'interfaces': {'archivos_interfaz': [...], 'total_interfaces': 5},
        'entrevistas': [{'pregunta': '...', 'respuesta': '...'}],
        'diagramas_flujo': [{'tipo': '...', 'descripcion': '...'}]
    },
    'tecnico': {
        'codigo': {'archivos_analizados': 100, 'metricas': {...}},
        'dependencias': {'dependencias_detectadas': [...]},
        'arquitectura': {'tipo_estimado': 'Monolítico', 'patrones_detectados': [...]},
        'rendimiento': {'errores_detectados': 5, 'recomendaciones': [...]},
        'oportunidades_ia': [{'archivo': '...', 'oportunidad': '...'}]
    },
    'integracion': {
        'plan_modernizacion': 'Plan detallado de modernización...'
    }
}
```

## Ejemplo Práctico

### Sistema Hipotético: Plataforma de Gestión de Inventarios

#### Análisis Funcional
- **Propósito**: Controlar el inventario de una empresa
- **Servicios**: Registro de productos, seguimiento de existencias, reportes
- **Interacciones**: Ingreso de datos por empleados, generación de reportes

#### Análisis Técnico
- **Obsolescencia**: MySQL 5.1 con soporte descontinuado
- **Arquitectura**: Sistema monolítico con dificultades de integración
- **Deuda Técnica**: Funciones duplicadas en gestión de reportes
- **Oportunidad**: Implementar IA para predecir niveles óptimos de inventario

#### Plan de Modernización
1. Actualizar base de datos a MySQL 8.0
2. Migrar a microservicios para mejorar escalabilidad
3. Refactorizar código duplicado
4. Agregar predicciones de IA para optimizar inventario

## Configuración Avanzada

### Personalización de Análisis

```python
# Crear agente personalizado
agente = AgenteAnalizador('./proyecto')

# Ejecutar análisis específicos
agente.scan_project_structure()
agente.analisis_funcional()  # Solo análisis funcional
agente.analisis_tecnico_profundo()  # Solo análisis técnico
agente.integrar_analisis()  # Solo integración
```

### Filtros de Archivos

El sistema clasifica automáticamente los archivos:

- **Código**: `.py`, `.js`, `.java`, `.cs`, `.php`, `.rb`, `.go`
- **Configuración**: `.json`, `.yml`, `.yaml`, `.toml`, `.ini`, `.conf`
- **Documentación**: `.md`, `.txt`, `.pdf`, `.doc`, `.docx`
- **Otros**: Cualquier otro tipo de archivo

## Troubleshooting

### Problemas Comunes

1. **Error de codificación**: El sistema maneja automáticamente archivos con diferentes codificaciones
2. **Archivos muy grandes**: Se procesan en chunks para evitar problemas de memoria
3. **Sin API key de OpenAI**: El sistema funciona en modo básico sin IA

### Logs

El sistema genera logs detallados:
```bash
INFO:app.agente_analizador:Escaneando estructura del proyecto
INFO:app.agente_analizador:Iniciando análisis funcional
WARNING:app.agente_analizador:No se pudo leer archivo.py
```

## Contribución

Para contribuir al desarrollo del agente analizador:

1. Fork el repositorio
2. Crea una rama para tu feature
3. Implementa tus cambios
4. Ejecuta las pruebas: `python test_agente_analizador.py`
5. Envía un pull request

## Licencia

Este proyecto está bajo la licencia MIT. Ver `LICENSE` para más detalles.

## Contacto

Para preguntas o soporte, contacta al equipo de desarrollo.

---

**Nota**: Este agente analizador está diseñado para trabajar con sistemas ajenos y proporcionar una base sólida para entender y modernizar sistemas de software de manera eficiente. 