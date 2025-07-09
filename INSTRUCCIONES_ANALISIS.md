# 📋 Instrucciones para Analizar tu Proyecto IntelliAI

## 🚀 Cómo Usar el Sistema de Análisis

### **Opción 1: Script Específico para IntelliAI (Recomendado)**

```bash
# Analizar con ruta específica
python analizar_intelliai.py /ruta/a/tu/proyecto/IntelliAI

# Con análisis de IA (si tienes OpenAI API key)
python analizar_intelliai.py /ruta/a/tu/proyecto/IntelliAI --ai
```

### **Opción 2: Script Flexible para Cualquier Proyecto**

```bash
# Analizar cualquier proyecto
python analizar_proyecto_flexible.py /ruta/a/tu/proyecto

# Con análisis de IA
python analizar_proyecto_flexible.py /ruta/a/tu/proyecto --ai
```

### **Opción 3: Script de Demostración**

```bash
# Usar el demo que analiza el proyecto actual
python demo_agente_analizador.py
```

## 📁 Rutas Comunes para tu Proyecto

Basándome en tu mención de `/home/pablo/win/source/repos/IntelliAI`, aquí tienes algunas opciones:

### **En Windows (WSL)**
```bash
# Si estás en WSL
python analizar_intelliai.py /mnt/c/Users/pablo/source/repos/IntelliAI

# O si está en el sistema de archivos de Windows
python analizar_intelliai.py /mnt/d/Projects/IntelliAI
```

### **En Linux/Mac**
```bash
# Ruta absoluta
python analizar_intelliai.py /home/pablo/win/source/repos/IntelliAI

# Ruta relativa (si estás cerca del proyecto)
python analizar_intelliai.py ../IntelliAI
python analizar_intelliai.py ./IntelliAI
```

### **En Contenedor Docker**
```bash
# Si el proyecto está montado en el contenedor
python analizar_intelliai.py /workspaces/IntelliAI
python analizar_intelliai.py /app/IntelliAI
```

## 🔧 Configuración de OpenAI (Opcional)

Para obtener análisis más detallado con IA:

```bash
# Configurar API key
export OPENAI_API_KEY="tu-api-key-aqui"

# Luego ejecutar con --ai
python analizar_intelliai.py /ruta/a/IntelliAI --ai
```

## 📊 Archivos que se Generarán

Después de ejecutar el análisis, obtendrás:

1. **`analisis_intelliai_detallado.md`** - Informe completo (200K+ caracteres)
2. **`analisis_intelliai_resumen.md`** - Informe resumido (1-2K caracteres)

## 🎯 Contenido del Análisis

### **Análisis Funcional**
- ✅ Documentación del sistema
- ✅ Interfaces y APIs detectadas
- ✅ Simulación de entrevistas con usuarios
- ✅ Diagramas de flujo de procesos

### **Análisis Técnico**
- ✅ Análisis de código fuente
- ✅ Métricas de calidad
- ✅ Dependencias y librerías
- ✅ Arquitectura del sistema
- ✅ Análisis de rendimiento
- ✅ Oportunidades de IA

### **Informe Integrado**
- ✅ Plan de modernización
- ✅ Recomendaciones específicas
- ✅ Roadmap de mejora

## 🚨 Solución de Problemas

### **Error: "El proyecto no existe"**
```bash
# Verificar que la ruta existe
ls -la /ruta/a/tu/proyecto

# Usar ruta absoluta
python analizar_intelliai.py $(pwd)/IntelliAI

# Verificar desde dónde ejecutas el script
pwd
```

### **Error: "No se puede leer archivo"**
- El sistema ignora archivos binarios automáticamente
- Los warnings son normales para archivos `.pyc`, `.dll`, etc.

### **Error: "OpenAI no configurado"**
- El análisis funciona sin OpenAI
- Para análisis con IA: `export OPENAI_API_KEY="tu-key"`

## 📈 Ejemplo de Salida Esperada

```
🚀 INICIANDO ANÁLISIS DEL PROYECTO INTELLIAI
============================================================
🔍 ANALIZANDO PROYECTO INTELLIAI
============================================================
📁 Ruta del proyecto: /ruta/a/IntelliAI
📊 Usando análisis básico (sin IA)

🔄 Inicializando agente analizador...
🔄 Ejecutando análisis completo...
📝 Generando informe detallado...
✅ Informe principal guardado en: analisis_intelliai_detallado.md
✅ Informe resumido guardado en: analisis_intelliai_resumen.md

============================================================
📊 RESUMEN DEL ANÁLISIS - INTELLIAI
============================================================

📋 Análisis Funcional:
   • Documentación analizada: ✅
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
   • Archivos analizados: 150
   • Funciones totales: 2500
   • Clases totales: 300
   • Problemas detectados: 25

🤖 Oportunidades de IA:
   • Oportunidades detectadas: 45
     1. Integración de IA en sistema de análisis
     2. Automatización de reportes
     3. Optimización de consultas
     ... y 42 más

✅ ANÁLISIS COMPLETADO
```

## 🎯 Próximos Pasos

1. **Ejecutar el análisis** con la ruta correcta de tu proyecto
2. **Revisar los informes** generados en formato Markdown
3. **Analizar las oportunidades de IA** detectadas
4. **Considerar las recomendaciones** de modernización
5. **Implementar mejoras** basadas en el análisis

## 📞 Ayuda Adicional

Si tienes problemas:

1. **Verifica la ruta**: `ls -la /ruta/a/tu/proyecto`
2. **Usa ruta absoluta**: `python analizar_intelliai.py $(realpath ./IntelliAI)`
3. **Ejecuta desde el directorio correcto**: `cd /workspaces/Herramienta_de_Diagnostico_Consulta_Con_IA`

---

*¡El sistema está listo para analizar tu proyecto IntelliAI! 🚀* 