import streamlit as st
import pandas as pd
from datetime import date, datetime
import os
import plotly.express as px
import plotly.graph_objects as go

# Configuración de la página
st.set_page_config(page_title="Estadísticas de Noah", page_icon="⚽", layout="wide")
st.title("⚽ Estadísticas de Noah")

# Inicializar clave del formulario
if 'form_key' not in st.session_state:
    st.session_state.form_key = 0

# Definir el nombre del archivo CSV
ARCHIVO_CSV = "datos_noah.csv"

# Columnas requeridas
COLUMNAS = [
    "fecha", "oponente", "titular", "minutos", "pases_buenos", "perdidas",
    "recuperaciones", "tiros", "goles", "asistencias",
    "faltas_cometidas", "faltas_recibidas", "despejes",
    "tarjetas_amarillas", "tarjetas_rojas"
]

# Columnas numéricas
COLUMNAS_NUMERICAS = [
    "minutos", "pases_buenos", "perdidas", "recuperaciones", "tiros",
    "goles", "asistencias", "faltas_cometidas", "faltas_recibidas",
    "despejes", "tarjetas_amarillas", "tarjetas_rojas"
]

# Función para formatear fecha
def formatear_fecha_segura(fecha):
    if pd.isna(fecha):
        return "Fecha inválida"
    return fecha.strftime('%d/%m/%Y')

# Función para cargar los datos (sin limpieza agresiva para depurar)
def cargar_datos():
    if os.path.exists(ARCHIVO_CSV):
        df = pd.read_csv(ARCHIVO_CSV)
        
        # Asegurar columnas existan
        for col in COLUMNAS:
            if col not in df.columns:
                df[col] = 0 if col != 'titular' else False
        
        # Convertir fechas
        df['fecha'] = pd.to_datetime(df['fecha'], format='%d/%m/%Y', errors='coerce')
        
        # No hacemos conversión automática de titular aquí para poder ver el valor original
        # Pero creamos una columna auxiliar para el valor interpretado
        return df
    else:
        df = pd.DataFrame(columns=COLUMNAS)
        df['fecha'] = pd.to_datetime([])
        for col in COLUMNAS_NUMERICAS:
            df[col] = 0
        df['titular'] = False
        return df

# Función para guardar datos (guardamos titular como 0/1)
def guardar_datos(df):
    # Asegurar que titular es entero antes de guardar
    df_guardar = df.copy()
    # Convertir titular a entero de forma robusta
    if df_guardar['titular'].dtype == 'object':
        df_guardar['titular'] = df_guardar['titular'].map({'True': 1, 'False': 0, True: 1, False: 0}).fillna(0).astype(int)
    else:
        df_guardar['titular'] = df_guardar['titular'].astype(int)
    df_guardar = df_guardar.sort_values('fecha')
    df_guardar.to_csv(ARCHIVO_CSV, index=False, date_format='%d/%m/%Y')

# Cargar datos
df = cargar_datos()

# --- SECCIÓN DE REPARACIÓN (para diagnosticar y corregir) ---
with st.expander("🛠️ Herramientas de reparación (para solucionar el problema de titular)", expanded=True):
    st.warning("Aquí puedes ver los valores reales de la columna 'titular' y corregirlos manualmente.")
    
    if not df.empty:
        # Mostrar los valores originales de la columna titular
        st.write("**Valores originales de 'titular' en el CSV:**")
        st.write(df[['fecha', 'oponente', 'titular']].head(10))
        
        # Mostrar los valores únicos y tipos
        st.write("**Valores únicos en 'titular':**", df['titular'].unique())
        st.write("**Tipo de dato de 'titular':**", df['titular'].dtype)
        
        # Seleccionar partido a reparar
        opciones_reparar = []
        for idx, row in df.iterrows():
            fecha_str = formatear_fecha_segura(row['fecha']) if not pd.isna(row['fecha']) else "Fecha inválida"
            opciones_reparar.append(f"{idx}: {fecha_str} vs {row['oponente']} (titular actual: {row['titular']})")
        
        idx_reparar = st.selectbox("Selecciona el índice del partido a reparar", options=range(len(df)), format_func=lambda x: opciones_reparar[x])
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔧 Marcar como Titular (1)"):
                df.loc[idx_reparar, 'titular'] = 1
                guardar_datos(df)
                st.success("Partido marcado como titular. Recargando...")
                st.rerun()
        with col2:
            if st.button("🔧 Marcar como No Titular (0)"):
                df.loc[idx_reparar, 'titular'] = 0
                guardar_datos(df)
                st.success("Partido marcado como no titular. Recargando...")
                st.rerun()
    else:
        st.info("No hay datos para reparar.")

# --- SECCIÓN: AÑADIR NUEVO REGISTRO ---
with st.expander("➕ Añadir nuevo partido", expanded=True):
    with st.form(key=f"formulario_partido_{st.session_state.form_key}"):
        col1, col2 = st.columns(2)
        
        with col1:
            fecha = st.date_input("📅 Fecha", value=date.today(), format="DD/MM/YYYY")
            oponente = st.text_input("🆚 Oponente")
            titular = st.checkbox("⚪ ¿Titular?", value=False)
            minutos = st.number_input("⏱️ Minutos jugados", min_value=0, step=1, value=0)
            pases_buenos = st.number_input("✅ Pases buenos", min_value=0, step=1, value=0)
            perdidas = st.number_input("❌ Pérdidas", min_value=0, step=1, value=0)
            recuperaciones = st.number_input("🔄 Recuperaciones", min_value=0, step=1, value=0)
            tiros = st.number_input("🎯 Tiros a puerta", min_value=0, step=1, value=0)
        
        with col2:
            goles = st.number_input("⚽ Goles", min_value=0, step=1, value=0)
            asistencias = st.number_input("🤝 Asistencias", min_value=0, step=1, value=0)
            faltas_cometidas = st.number_input("👟 Faltas cometidas", min_value=0, step=1, value=0)
            faltas_recibidas = st.number_input("🛡️ Faltas recibidas", min_value=0, step=1, value=0)
            despejes = st.number_input("🧹 Despejes", min_value=0, step=1, value=0)
            tarjetas_amarillas = st.number_input("🟨 Tarjetas amarillas", min_value=0, max_value=2, step=1, value=0)
            tarjetas_rojas = st.number_input("🟥 Tarjetas rojas", min_value=0, max_value=1, step=1, value=0)
        
        guardar = st.form_submit_button("💾 Guardar partido")
        
        if guardar:
            nuevo_registro = pd.DataFrame([[
                fecha.strftime("%d/%m/%Y"), oponente, 1 if titular else 0, minutos, pases_buenos, perdidas,
                recuperaciones, tiros, goles, asistencias,
                faltas_cometidas, faltas_recibidas, despejes,
                tarjetas_amarillas, tarjetas_rojas
            ]], columns=COLUMNAS)
            df = pd.concat([df, nuevo_registro], ignore_index=True)
            df['fecha'] = pd.to_datetime(df['fecha'], format='%d/%m/%Y', errors='coerce')
            guardar_datos(df)
            st.session_state.form_key += 1
            st.success("¡Partido guardado con éxito!")
            st.balloons()
            st.rerun()

# --- SECCIÓN: MOSTRAR HISTORIAL ---
st.subheader("📋 Historial de partidos")
if df.empty:
    st.info("Aún no hay datos. ¡Añade tu primer partido!")
else:
    # Ordenar por fecha ascendente
    df = df.sort_values('fecha', ascending=True).reset_index(drop=True)
    
    # Preparar DataFrame para mostrar (conversión a Sí/No para visualización)
    df_display = df.copy()
    df_display['fecha'] = df_display['fecha'].apply(formatear_fecha_segura)
    # Convertir titular a Sí/No de forma segura
    df_display['titular'] = df_display['titular'].apply(lambda x: 'Sí' if str(x).strip().lower() in ['1', 'true', 'sí', 'si', 'yes'] else 'No')
    st.dataframe(df_display, use_container_width=True)
    
    # --- SECCIÓN DE EDICIÓN Y ELIMINACIÓN ---
    st.subheader("✏️ Editar o eliminar partido")
    
    opciones = []
    for idx, row in df.iterrows():
        fecha_str = formatear_fecha_segura(row['fecha'])
        titular_val = row['titular']
        titular_str = "T" if str(titular_val).strip().lower() in ['1', 'true', 'sí', 'si', 'yes'] else "S"
        opciones.append(f"{fecha_str} vs {row['oponente']} ({titular_str}) - G:{row['goles']} A:{row['asistencias']}")
    
    if opciones:
        partido_seleccionado = st.selectbox(
            "Selecciona un partido",
            options=range(len(df)),
            format_func=lambda x: opciones[x]
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Eliminar partido", type="secondary"):
                df = df.drop(index=partido_seleccionado).reset_index(drop=True)
                guardar_datos(df)
                st.success("Partido eliminado")
                st.rerun()
        with col2:
            if st.button("✏️ Editar partido", type="primary"):
                st.session_state['editar_index'] = partido_seleccionado
                st.rerun()
        
        # Formulario de edición
        if 'editar_index' in st.session_state:
            idx = st.session_state['editar_index']
            partido = df.loc[idx]
            
            st.subheader(f"Editando: {formatear_fecha_segura(partido['fecha'])} vs {partido['oponente']}")
            
            with st.form("formulario_edicion"):
                col1, col2 = st.columns(2)
                
                with col1:
                    fecha_edit = st.date_input("📅 Fecha", value=partido['fecha'], format="DD/MM/YYYY")
                    oponente_edit = st.text_input("🆚 Oponente", value=partido['oponente'])
                    # Convertir titular a booleano para el checkbox
                    titular_actual = str(partido['titular']).strip().lower() in ['1', 'true', 'sí', 'si', 'yes']
                    titular_edit = st.checkbox("⚪ ¿Titular?", value=titular_actual)
                    minutos_edit = st.number_input("⏱️ Minutos", min_value=0, step=1, value=int(partido['minutos']))
                    pases_buenos_edit = st.number_input("✅ Pases buenos", min_value=0, step=1, value=int(partido['pases_buenos']))
                    perdidas_edit = st.number_input("❌ Pérdidas", min_value=0, step=1, value=int(partido['perdidas']))
                    recuperaciones_edit = st.number_input("🔄 Recuperaciones", min_value=0, step=1, value=int(partido['recuperaciones']))
                    tiros_edit = st.number_input("🎯 Tiros", min_value=0, step=1, value=int(partido['tiros']))
                
                with col2:
                    goles_edit = st.number_input("⚽ Goles", min_value=0, step=1, value=int(partido['goles']))
                    asistencias_edit = st.number_input("🤝 Asistencias", min_value=0, step=1, value=int(partido['asistencias']))
                    faltas_cometidas_edit = st.number_input("👟 Faltas cometidas", min_value=0, step=1, value=int(partido['faltas_cometidas']))
                    faltas_recibidas_edit = st.number_input("🛡️ Faltas recibidas", min_value=0, step=1, value=int(partido['faltas_recibidas']))
                    despejes_edit = st.number_input("🧹 Despejes", min_value=0, step=1, value=int(partido['despejes']))
                    tarjetas_amarillas_edit = st.number_input("🟨 Amarillas", min_value=0, max_value=2, step=1, value=int(partido['tarjetas_amarillas']))
                    tarjetas_rojas_edit = st.number_input("🟥 Rojas", min_value=0, max_value=1, step=1, value=int(partido['tarjetas_rojas']))
                
                col_guardar, col_cancelar = st.columns(2)
                with col_guardar:
                    guardar_edit = st.form_submit_button("💾 Guardar cambios")
                with col_cancelar:
                    cancelar_edit = st.form_submit_button("❌ Cancelar")
                
                if guardar_edit:
                    # Actualizar la fila
                    df.loc[idx] = [
                        fecha_edit.strftime("%d/%m/%Y"),
                        oponente_edit,
                        1 if titular_edit else 0,
                        minutos_edit,
                        pases_buenos_edit,
                        perdidas_edit,
                        recuperaciones_edit,
                        tiros_edit,
                        goles_edit,
                        asistencias_edit,
                        faltas_cometidas_edit,
                        faltas_recibidas_edit,
                        despejes_edit,
                        tarjetas_amarillas_edit,
                        tarjetas_rojas_edit
                    ]
                    df['fecha'] = pd.to_datetime(df['fecha'], format='%d/%m/%Y', errors='coerce')
                    guardar_datos(df)
                    del st.session_state['editar_index']
                    st.success("Partido actualizado")
                    st.rerun()
                
                if cancelar_edit:
                    del st.session_state['editar_index']
                    st.rerun()
    else:
        st.warning("No hay partidos válidos para editar.")
    
    # --- ESTADÍSTICAS RESUMEN ---
    st.subheader("📊 Resumen estadístico")
    # Para las estadísticas, necesitamos que los valores sean numéricos. Creamos una copia numérica.
    df_numerico = df.copy()
    df_numerico['titular'] = df_numerico['titular'].apply(lambda x: 1 if str(x).strip().lower() in ['1', 'true', 'sí', 'si', 'yes'] else 0)
    for col in COLUMNAS_NUMERICAS:
        df_numerico[col] = pd.to_numeric(df_numerico[col], errors='coerce').fillna(0)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total partidos", len(df_numerico))
        st.metric("Total goles", df_numerico["goles"].sum())
        st.metric("Media goles/partido", round(df_numerico["goles"].mean(), 2))
    with col2:
        st.metric("Total asistencias", df_numerico["asistencias"].sum())
        st.metric("Total minutos", df_numerico["minutos"].sum())
        st.metric("Media minutos/partido", round(df_numerico["minutos"].mean(), 1))
    with col3:
        st.metric("Media pases buenos/partido", round(df_numerico["pases_buenos"].mean(), 1))
        st.metric("Media pérdidas/partido", round(df_numerico["perdidas"].mean(), 1))
        st.metric("Media recuperaciones/partido", round(df_numerico["recuperaciones"].mean(), 1))
    with col4:
        st.metric("Total faltas cometidas", df_numerico["faltas_cometidas"].sum())
        st.metric("Total tarjetas", df_numerico["tarjetas_amarillas"].sum() + df_numerico["tarjetas_rojas"].sum())
        st.metric("Veces titular", df_numerico["titular"].sum())
    
    # --- GRÁFICOS ---
    st.subheader("📈 Evolución de estadísticas")
    df_numerico = df_numerico.sort_values("fecha")
    metricas_disponibles = {
        "Goles": "goles", "Asistencias": "asistencias", "Pases buenos": "pases_buenos",
        "Pérdidas": "perdidas", "Recuperaciones": "recuperaciones", "Tiros": "tiros",
        "Faltas cometidas": "faltas_cometidas", "Faltas recibidas": "faltas_recibidas",
        "Despejes": "despejes", "Tarjetas amarillas": "tarjetas_amarillas",
        "Tarjetas rojas": "tarjetas_rojas"
    }
    metricas_seleccionadas = st.multiselect(
        "Selecciona métricas", options=list(metricas_disponibles.keys()), default=["Goles", "Asistencias"]
    )
    if metricas_seleccionadas:
        fig = go.Figure()
        for metrica in metricas_seleccionadas:
            col = metricas_disponibles[metrica]
            fig.add_trace(go.Scatter(x=df_numerico["fecha"], y=df_numerico[col], mode='lines+markers', name=metrica))
        fig.update_layout(title="Evolución", xaxis_title="Fecha", hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📊 Comparativa por partido")
    col1, col2 = st.columns(2)
    with col1:
        metrica1 = st.selectbox("Métrica 1", options=list(metricas_disponibles.keys()), index=0)
    with col2:
        metrica2 = st.selectbox("Métrica 2", options=list(metricas_disponibles.keys()), index=1)
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(x=df_numerico["fecha"].dt.strftime('%d/%m/%Y'), y=df_numerico[metricas_disponibles[metrica1]], name=metrica1))
    fig_bar.add_trace(go.Bar(x=df_numerico["fecha"].dt.strftime('%d/%m/%Y'), y=df_numerico[metricas_disponibles[metrica2]], name=metrica2))
    fig_bar.update_layout(title=f"{metrica1} vs {metrica2}", barmode='group', xaxis_tickangle=-45)
    st.plotly_chart(fig_bar, use_container_width=True)