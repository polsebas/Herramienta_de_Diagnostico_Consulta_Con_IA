#!/usr/bin/env python3
"""
Dashboard de Streamlit para monitorear el Context Manager

Este dashboard proporciona visualizaciones en tiempo real de:
- Uso de tokens y eficiencia de contexto
- Métricas de compresión y calidad
- Rendimiento por modelo
- Recomendaciones de optimización
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from pathlib import Path
from datetime import datetime, timedelta
import sys
from typing import Dict, Any, List

# Agregar el directorio app al path
sys.path.append(str(Path(__file__).parent))

from context_manager import ContextManager, ContextStats, ContextMetrics

# Configuración de la página
st.set_page_config(
    page_title="Context Manager Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("📊 Dashboard del Context Manager")
st.markdown("Monitoreo en tiempo real del rendimiento del contexto y uso de tokens")

# Sidebar para configuración
st.sidebar.header("⚙️ Configuración")
model_name = st.sidebar.selectbox(
    "Modelo LLM",
    ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "claude-3-sonnet"],
    index=0
)

period_hours = st.sidebar.slider(
    "Período de análisis (horas)",
    min_value=1,
    max_value=168,  # 1 semana
    value=24,
    step=1
)

max_context_ratio = st.sidebar.slider(
    "Ratio máximo de contexto",
    min_value=0.1,
    max_value=0.8,
    value=0.4,
    step=0.05,
    help="Porcentaje máximo de la ventana del modelo para contexto"
)

# Inicializar Context Manager
@st.cache_resource
def get_context_manager():
    """Obtiene una instancia del Context Manager."""
    return ContextManager(model_name=model_name, max_context_ratio=max_context_ratio)

context_manager = get_context_manager()

# Función para cargar datos del archivo de logs
def load_log_data() -> List[Dict[str, Any]]:
    """Carga datos del archivo de logs del Context Manager."""
    log_file = Path("logs/context_stats.jsonl")
    if not log_file.exists():
        return []
    
    data = []
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
    except Exception as e:
        st.error(f"Error al cargar logs: {e}")
        return []
    
    return data

# Función para crear métricas agregadas
def create_metrics_df(data: List[Dict[str, Any]], period_hours: int) -> pd.DataFrame:
    """Crea DataFrame con métricas agregadas del período especificado."""
    if not data:
        return pd.DataFrame()
    
    # Convertir a DataFrame
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Filtrar por período
    cutoff_time = datetime.now() - timedelta(hours=period_hours)
    df_filtered = df[df['timestamp'] >= cutoff_time]
    
    return df_filtered

# Cargar datos
log_data = load_log_data()
metrics_df = create_metrics_df(log_data, period_hours)

# Métricas principales
if not metrics_df.empty:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_queries = len(metrics_df)
        st.metric("Total Consultas", total_queries)
    
    with col2:
        avg_compression = metrics_df['compression_ratio'].mean()
        st.metric("Compresión Promedio", f"{avg_compression:.2%}")
    
    with col3:
        avg_efficiency = metrics_df['efficiency_score'].mean()
        st.metric("Eficiencia Promedio", f"{avg_efficiency:.2%}")
    
    with col4:
        total_tokens_saved = (metrics_df['tokens_before'] - metrics_df['tokens_after']).sum()
        st.metric("Tokens Ahorrados", f"{total_tokens_saved:,}")
    
    # Gráficos de rendimiento
    st.header("📈 Métricas de Rendimiento")
    
    # Gráfico de compresión y eficiencia a lo largo del tiempo
    fig_trends = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Ratio de Compresión", "Score de Eficiencia"),
        vertical_spacing=0.1
    )
    
    fig_trends.add_trace(
        go.Scatter(
            x=metrics_df['timestamp'],
            y=metrics_df['compression_ratio'],
            mode='lines+markers',
            name='Compresión',
            line=dict(color='blue')
        ),
        row=1, col=1
    )
    
    fig_trends.add_trace(
        go.Scatter(
            x=metrics_df['timestamp'],
            y=metrics_df['efficiency_score'],
            mode='lines+markers',
            name='Eficiencia',
            line=dict(color='green')
        ),
        row=2, col=1
    )
    
    fig_trends.update_layout(height=600, showlegend=True)
    st.plotly_chart(fig_trends, use_container_width=True)
    
    # Gráfico de distribución de calidad
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribución de scores de eficiencia
        efficiency_bins = pd.cut(metrics_df['efficiency_score'], 
                               bins=[0, 0.6, 0.7, 0.8, 0.9, 1.0],
                               labels=['<0.6', '0.6-0.7', '0.7-0.8', '0.8-0.9', '≥0.9'])
        efficiency_dist = efficiency_bins.value_counts().sort_index()
        
        fig_efficiency = px.bar(
            x=efficiency_dist.index,
            y=efficiency_dist.values,
            title="Distribución de Scores de Eficiencia",
            labels={'x': 'Score', 'y': 'Cantidad de Consultas'}
        )
        fig_efficiency.update_traces(marker_color='lightgreen')
        st.plotly_chart(fig_efficiency, use_container_width=True)
    
    with col2:
        # Distribución de ratios de compresión
        compression_bins = pd.cut(metrics_df['compression_ratio'],
                                bins=[0, 0.3, 0.5, 0.7, 0.9, 1.0],
                                labels=['<0.3', '0.3-0.5', '0.5-0.7', '0.7-0.9', '≥0.9'])
        compression_dist = compression_bins.value_counts().sort_index()
        
        fig_compression = px.bar(
            x=compression_dist.index,
            y=compression_dist.values,
            title="Distribución de Ratios de Compresión",
            labels={'x': 'Ratio', 'y': 'Cantidad de Consultas'}
        )
        fig_compression.update_traces(marker_color='lightblue')
        st.plotly_chart(fig_compression, use_container_width=True)
    
    # Análisis de uso de presupuesto
    st.header("💰 Análisis de Presupuesto de Tokens")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de utilización del presupuesto
        fig_budget = px.scatter(
            metrics_df,
            x='budget_used',
            y='efficiency_score',
            color='compression_ratio',
            size='tokens_after',
            title="Eficiencia vs. Utilización del Presupuesto",
            labels={
                'budget_used': 'Utilización del Presupuesto',
                'efficiency_score': 'Score de Eficiencia',
                'compression_ratio': 'Ratio de Compresión',
                'tokens_after': 'Tokens Finales'
            }
        )
        st.plotly_chart(fig_budget, use_container_width=True)
    
    with col2:
        # Gráfico de tokens antes vs después
        fig_tokens = px.scatter(
            metrics_df,
            x='tokens_before',
            y='tokens_after',
            color='efficiency_score',
            size='chunks_original',
            title="Tokens Antes vs. Después de Compactación",
            labels={
                'tokens_before': 'Tokens Antes',
                'tokens_after': 'Tokens Después',
                'efficiency_score': 'Score de Eficiencia',
                'chunks_original': 'Chunks Originales'
            }
        )
        st.plotly_chart(fig_tokens, use_container_width=True)
    
    # Tabla de consultas recientes
    st.header("📋 Consultas Recientes")
    
    # Preparar datos para la tabla
    table_data = metrics_df[['timestamp', 'query', 'tokens_before', 'tokens_after', 
                            'compression_ratio', 'efficiency_score']].copy()
    table_data['timestamp'] = table_data['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    table_data['compression_ratio'] = table_data['compression_ratio'].apply(lambda x: f"{x:.2%}")
    table_data['efficiency_score'] = table_data['efficiency_score'].apply(lambda x: f"{x:.2%}")
    table_data['tokens_saved'] = table_data['tokens_before'] - table_data['tokens_after']
    
    # Renombrar columnas
    table_data.columns = ['Timestamp', 'Consulta', 'Tokens Antes', 'Tokens Después', 
                         'Compresión', 'Eficiencia', 'Tokens Ahorrados']
    
    st.dataframe(table_data, use_container_width=True)
    
    # Exportar datos
    st.header("💾 Exportar Datos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Exportar CSV"):
            csv_data = metrics_df.to_csv(index=False)
            st.download_button(
                label="Descargar CSV",
                data=csv_data,
                file_name=f"context_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("Exportar JSON"):
            json_data = metrics_df.to_json(orient='records', indent=2)
            st.download_button(
                label="Descargar JSON",
                data=json_data,
                file_name=f"context_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

else:
    # Sin datos disponibles
    st.warning("⚠️ No hay datos disponibles para el período seleccionado.")
    st.info("💡 Los datos aparecerán aquí después de procesar algunas consultas con el Context Manager.")
    
    # Mostrar configuración actual
    st.header("⚙️ Configuración Actual")
    st.json({
        "model_name": model_name,
        "max_context_ratio": max_context_ratio,
        "window_size": context_manager.model_window_size,
        "max_context_tokens": context_manager.max_context_tokens
    })

# Recomendaciones del sistema
st.header("💡 Recomendaciones del Sistema")
recommendations = context_manager.get_recommendations()

if recommendations:
    for i, rec in enumerate(recommendations, 1):
        st.info(f"{i}. {rec}")
else:
    st.success("✅ El sistema está funcionando de manera óptima. No se requieren cambios.")

# Footer
st.markdown("---")
st.markdown(
    "**Context Manager Dashboard** - Monitoreo en tiempo real del rendimiento del contexto RAG. "
    "Actualizado automáticamente con cada consulta procesada."
)
