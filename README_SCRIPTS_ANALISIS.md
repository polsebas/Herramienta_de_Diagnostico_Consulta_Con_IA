# 📋 Scripts de Análisis de Proyectos

## 🚀 Scripts Disponibles

### **1. `analizar_proyecto_net.py` - Para Proyectos .NET/Blazor**
```bash
# Analizar proyecto .NET/Blazor
python analizar_proyecto_net.py /mnt/fuentes

# Con análisis de IA
python analizar_proyecto_net.py /mnt/fuentes --ai
```

**Características:**
- ✅ Optimizado para archivos C#, Razor, .csproj
- ✅ Análisis específico de arquitectura .NET
- ✅ Detección de patrones Blazor
- ✅ Informes adaptados a proyectos .NET

### **2. `analizar_intelliai.py` - Para Proyecto IntelliAI**
```bash
# Analizar proyecto IntelliAI
python analizar_intelliai.py /ruta/a/IntelliAI

# Con análisis de IA
python analizar_intelliai.py /ruta/a/IntelliAI --ai
```

**Características:**
- ✅ Específico para proyectos IntelliAI
- ✅ Análisis detallado de oportunidades de IA
- ✅ Informes personalizados para IntelliAI
- ✅ Recomendaciones específicas de modernización

### **3. `analizar_proyecto_flexible.py` - Para Cualquier Proyecto**
```bash
# Analizar cualquier proyecto
python analizar_proyecto_flexible.py /ruta/a/proyecto

# Con análisis de IA
python analizar_proyecto_flexible.py /ruta/a/proyecto --ai
```

**Características:**
- ✅ Funciona con cualquier tipo de proyecto
- ✅ Detección automática de tecnologías
- ✅ Análisis universal
- ✅ Informes genéricos pero completos

### **4. `demo_agente_analizador.py` - Demo del Sistema**
```bash
# Ejecutar demo
python demo_agente_analizador.py
```

**Características:**
- ✅ Demostración del sistema
- ✅ Análisis del proyecto actual
- ✅ Ejemplo de uso completo

## 📊 Resultados Generados

Todos los scripts generan:

1. **`analisis_[nombre]_detallado.md`** - Informe completo (200K+ caracteres)
2. **`analisis_[nombre]_resumen.md`** - Informe resumido (1-2K caracteres)

### **Contenido de los Informes:**

#### **Análisis Funcional**
- ✅ Documentación del sistema
- ✅ Interfaces y APIs detectadas
- ✅ Simulación de entrevistas con usuarios
- ✅ Diagramas de flujo de procesos

#### **Análisis Técnico**
- ✅ Análisis de código fuente
- ✅ Métricas de calidad
- ✅ Dependencias y librerías
- ✅ Arquitectura del sistema
- ✅ Análisis de rendimiento
- ✅ Oportunidades de IA

#### **Informe Integrado**
- ✅ Plan de modernización
- ✅ Recomendaciones específicas
- ✅ Roadmap de mejora

## 🎯 Casos de Uso

### **Para tu Proyecto Blazor (Actual)**
```bash
# Analizar el proyecto montado en devcontainer
python analizar_proyecto_net.py /mnt/fuentes
```

### **Para tu Proyecto IntelliAI (Cuando esté disponible)**
```bash
# Analizar IntelliAI
python analizar_intelliai.py /ruta/a/IntelliAI

# Con análisis de IA
python analizar_intelliai.py /ruta/a/IntelliAI --ai
```

### **Para Cualquier Otro Proyecto**
```bash
# Proyecto Python
python analizar_proyecto_flexible.py /ruta/a/proyecto_python

# Proyecto JavaScript
python analizar_proyecto_flexible.py /ruta/a/proyecto_js

# Proyecto Java
python analizar_proyecto_flexible.py /ruta/a/proyecto_java
```

## 🔧 Configuración de OpenAI (Opcional)

Para obtener análisis más detallado con IA:

```bash
# Configurar API key
export OPENAI_API_KEY="tu-api-key-aqui"

# Luego ejecutar con --ai
python analizar_proyecto_net.py /mnt/fuentes --ai
```

## 📈 Ejemplo de Salida

```
🚀 INICIANDO ANÁLISIS DE PROYECTO .NET/BLAZOR
============================================================
🔍 ANALIZANDO PROYECTO .NET/BLAZOR
============================================================
📁 Ruta del proyecto: /mnt/fuentes
📊 Usando análisis básico (sin IA)

🔄 Inicializando agente analizador...
🔄 Ejecutando análisis completo...
📝 Generando informe detallado...
✅ Informe principal guardado en: analisis_fuentes_detallado.md
✅ Informe resumido guardado en: analisis_fuentes_resumen.md

============================================================
📊 RESUMEN DEL ANÁLISIS - FUENTES
============================================================

📋 Análisis Funcional:
   • Documentación analizada: ❌
   • Interfaces detectadas: ✅
   • Entrevistas simuladas: ✅
   • Diagramas de flujo: ✅

🔧 Análisis Técnico:
   • Código analizado: ✅
   • Dependencias revisadas: ✅
   • Arquitectura evaluada: ✅
   • Rendimiento simulado: ✅
   • Oportunidades de IA: ✅

📈 Métricas de Código:
   • Archivos analizados: 21
   • Funciones totales: 0
   • Clases totales: 0
   • Problemas detectados: 0

📊 Lenguajes detectados:
   • cs: 9 archivos
   • js: 12 archivos

🏗️  Arquitectura:
   • Tipo estimado: Monolítico
   • Patrones detectados: 
   • Componentes principales: 0

🤖 Oportunidades de IA:
   • Oportunidades detectadas: 3
     1. Posible integración de IA en dotnet.native.js
     2. Posible integración de IA en service-worker-assets.js
     3. Posible integración de IA en dotnet.native.8.0.8.g7qu3cxhjr.js

✅ ANÁLISIS COMPLETADO
```

## 🚨 Solución de Problemas

### **Error: "El proyecto no existe"**
```bash
# Verificar que la ruta existe
ls -la /ruta/a/tu/proyecto

# Usar ruta absoluta
python analizar_proyecto_net.py $(pwd)/proyecto

# Verificar desde dónde ejecutas el script
pwd
```

### **Error: "No se puede leer archivo"**
- El sistema ignora archivos binarios automáticamente
- Los warnings son normales para archivos `.pyc`, `.dll`, etc.

### **Error: "OpenAI no configurado"**
- El análisis funciona sin OpenAI
- Para análisis con IA: `export OPENAI_API_KEY="tu-key"`

## 🎯 Próximos Pasos

1. **Elegir el script apropiado** según tu tipo de proyecto
2. **Ejecutar el análisis** con la ruta correcta
3. **Revisar los informes** generados en formato Markdown
4. **Analizar las oportunidades de IA** detectadas
5. **Implementar mejoras** basadas en las recomendaciones

---

*¡El sistema está listo para analizar cualquier proyecto! 🚀* 