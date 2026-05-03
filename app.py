import streamlit as st
import pandas as pd
import numpy as np
from datetime import date
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Noah · Stats",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# CSS personalizado
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;500;600&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Header */
    .main-header {
        background: linear-gradient(135deg, #0a0f1e 0%, #1a2744 50%, #0d1b2a 100%);
        border-radius: 16px;
        padding: 28px 32px;
        margin-bottom: 24px;
        border: 1px solid rgba(255,255,255,0.08);
        display: flex;
        align-items: center;
        gap: 20px;
    }
    .main-header h1 {
        font-family: 'Bebas Neue', cursive;
        font-size: 3rem;
        color: #f0f0f0;
        letter-spacing: 3px;
        margin: 0;
        line-height: 1;
    }
    .main-header .subtitle {
        color: #64b3f4;
        font-size: 0.85rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        font-weight: 500;
    }
    .badge {
        background: #f0c040;
        color: #0a0f1e;
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    /* KPI cards */
    .kpi-card {
        background: linear-gradient(145deg, #1a2744, #0d1b2a);
        border: 1px solid rgba(100,179,244,0.15);
        border-radius: 14px;
        padding: 20px 22px;
        text-align: center;
        transition: border-color 0.2s;
    }
    .kpi-card:hover { border-color: rgba(100,179,244,0.4); }
    .kpi-value {
        font-family: 'Bebas Neue', cursive;
        font-size: 2.6rem;
        color: #64b3f4;
        line-height: 1;
        margin: 4px 0;
    }
    .kpi-label {
        font-size: 0.72rem;
        color: #8899aa;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 500;
    }
    .kpi-sub {
        font-size: 0.78rem;
        color: #aabbcc;
        margin-top: 4px;
    }

    /* Titular badge */
    .titular-si {
        background: #16a34a22;
        color: #4ade80;
        border: 1px solid #4ade8044;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .titular-no {
        background: #6b728022;
        color: #94a3b8;
        border: 1px solid #6b728044;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
    }

    /* Form styling */
    div[data-testid="stForm"] {
        background: #0d1525;
        border: 1px solid rgba(100,179,244,0.12);
        border-radius: 16px;
        padding: 20px;
    }
    div.stButton > button {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        border-radius: 10px;
        transition: all 0.2s;
    }

    /* Tab override */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.85rem;
        letter-spacing: 0.5px;
    }

    /* Section titles */
    .section-title {
        font-family: 'Bebas Neue', cursive;
        font-size: 1.6rem;
        letter-spacing: 2px;
        color: #e2e8f0;
        margin: 8px 0 16px 0;
        border-left: 4px solid #64b3f4;
        padding-left: 12px;
    }

    /* Alert box */
    .info-box {
        background: #0a1628;
        border: 1px solid #64b3f444;
        border-radius: 12px;
        padding: 16px 20px;
        color: #94a3b8;
        font-size: 0.88rem;
    }

    /* Metric override for dark theme */
    [data-testid="metric-container"] {
        background: #111827;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 12px 16px;
    }

    /* Dark theme overrides */
    .main { background-color: #060d1a; }
    .block-container { padding-top: 1.5rem; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────
ARCHIVO_CSV = "datos_noah.csv"

# Todas las columnas del CSV – NUNCA cambia el orden
COLUMNAS = [
    "fecha",           # str ISO: YYYY-MM-DD  (único formato en disco)
    "oponente",        # str
    "titular",         # int 0/1
    "minutos",         # int
    "pases_buenos",    # int
    "perdidas",        # int
    "recuperaciones",  # int
    "tiros",           # int
    "goles",           # int
    "asistencias",     # int
    "faltas_cometidas",# int
    "faltas_recibidas",# int
    "despejes",        # int
    "tarjetas_amarillas",# int
    "tarjetas_rojas",  # int
]

COLUMNAS_NUM = [c for c in COLUMNAS if c not in ("fecha", "oponente", "titular")]

ETIQUETAS = {
    "minutos": "Minutos", "pases_buenos": "Pases buenos", "perdidas": "Pérdidas",
    "recuperaciones": "Recuperaciones", "tiros": "Tiros", "goles": "Goles",
    "asistencias": "Asistencias", "faltas_cometidas": "Faltas cometidas",
    "faltas_recibidas": "Faltas recibidas", "despejes": "Despejes",
    "tarjetas_amarillas": "Amarillas", "tarjetas_rojas": "Rojas",
}

COLORES_PLOTLY = ["#64b3f4", "#f0c040", "#4ade80", "#f87171", "#c084fc",
                   "#fb923c", "#34d399", "#60a5fa", "#a78bfa", "#fbbf24"]

# ─────────────────────────────────────────────
# PERSISTENCIA – funciones sin bugs
# ─────────────────────────────────────────────

def _df_vacio() -> pd.DataFrame:
    """DataFrame vacío con los tipos correctos."""
    df = pd.DataFrame(columns=COLUMNAS)
    df["fecha"] = pd.Series(dtype="datetime64[ns]")
    df["titular"] = pd.Series(dtype="int64")
    for c in COLUMNAS_NUM:
        df[c] = pd.Series(dtype="int64")
    df["oponente"] = pd.Series(dtype="object")
    return df


def cargar_datos() -> pd.DataFrame:
    """
    Lee el CSV. Siempre devuelve un DataFrame limpio con tipos correctos.
    Tolerante a CSVs antiguos que usaban DD/MM/YYYY o valores boolean en titular.
    """
    if not os.path.exists(ARCHIVO_CSV):
        return _df_vacio()

    try:
        df = pd.read_csv(ARCHIVO_CSV, dtype=str)  # leer todo como string, sin asumir tipos
    except Exception:
        return _df_vacio()

    # Añadir columnas que falten
    for col in COLUMNAS:
        if col not in df.columns:
            df[col] = "0" if col != "oponente" else ""

    # ── Parsear fecha ──────────────────────────────────────────────────────
    # Intentar ISO primero, luego DD/MM/YYYY (compatibilidad con versión antigua)
    fecha_iso = pd.to_datetime(df["fecha"], format="%Y-%m-%d", errors="coerce")
    fecha_dmy = pd.to_datetime(df["fecha"], format="%d/%m/%Y", errors="coerce")
    df["fecha"] = fecha_iso.fillna(fecha_dmy)

    # ── Parsear titular ────────────────────────────────────────────────────
    def _parse_titular(v):
        s = str(v).strip().lower()
        if s in ("1", "true", "sí", "si", "yes", "s"):
            return 1
        return 0

    df["titular"] = df["titular"].apply(_parse_titular).astype(int)

    # ── Parsear columnas numéricas ─────────────────────────────────────────
    for col in COLUMNAS_NUM:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    # Eliminar filas con fecha inválida
    df = df[df["fecha"].notna()].copy()

    # Ordenar
    df = df.sort_values("fecha", ascending=True).reset_index(drop=True)
    return df


def guardar_datos(df: pd.DataFrame) -> None:
    """
    Guarda en formato canónico: fecha ISO, titular 0/1, numéricos como int.
    Esta función es la ÚNICA que escribe en disco.
    """
    df_out = df.copy()

    # Fecha → ISO string
    df_out["fecha"] = pd.to_datetime(df_out["fecha"]).dt.strftime("%Y-%m-%d")

    # Titular → int
    df_out["titular"] = df_out["titular"].astype(int)

    # Numéricos → int
    for col in COLUMNAS_NUM:
        df_out[col] = pd.to_numeric(df_out[col], errors="coerce").fillna(0).astype(int)

    # Orden de columnas garantizado
    df_out = df_out[COLUMNAS]
    df_out.to_csv(ARCHIVO_CSV, index=False)


def agregar_partido(datos: dict) -> None:
    """Añade un partido nuevo y guarda."""
    df = cargar_datos()
    nueva_fila = pd.DataFrame([{
        "fecha": pd.Timestamp(datos["fecha"]),
        "oponente": datos["oponente"].strip(),
        "titular": int(datos["titular"]),
        "minutos": int(datos["minutos"]),
        "pases_buenos": int(datos["pases_buenos"]),
        "perdidas": int(datos["perdidas"]),
        "recuperaciones": int(datos["recuperaciones"]),
        "tiros": int(datos["tiros"]),
        "goles": int(datos["goles"]),
        "asistencias": int(datos["asistencias"]),
        "faltas_cometidas": int(datos["faltas_cometidas"]),
        "faltas_recibidas": int(datos["faltas_recibidas"]),
        "despejes": int(datos["despejes"]),
        "tarjetas_amarillas": int(datos["tarjetas_amarillas"]),
        "tarjetas_rojas": int(datos["tarjetas_rojas"]),
    }])
    df = pd.concat([df, nueva_fila], ignore_index=True)
    df = df.sort_values("fecha").reset_index(drop=True)
    guardar_datos(df)


def actualizar_partido(idx: int, datos: dict) -> None:
    """Actualiza un partido existente por posición en el DataFrame."""
    df = cargar_datos()
    if idx >= len(df):
        return
    for k, v in datos.items():
        if k == "fecha":
            df.at[idx, k] = pd.Timestamp(v)
        elif k == "titular":
            df.at[idx, k] = int(v)
        elif k in COLUMNAS_NUM:
            df.at[idx, k] = int(v)
        else:
            df.at[idx, k] = v
    df = df.sort_values("fecha").reset_index(drop=True)
    guardar_datos(df)


def eliminar_partido(idx: int) -> None:
    """Elimina un partido por posición."""
    df = cargar_datos()
    if idx >= len(df):
        return
    df = df.drop(index=idx).reset_index(drop=True)
    guardar_datos(df)


# ─────────────────────────────────────────────
# HELPERS UI
# ─────────────────────────────────────────────

def fmt_fecha(ts) -> str:
    try:
        return pd.Timestamp(ts).strftime("%d/%m/%Y")
    except Exception:
        return "–"


def nota_rendimiento(row) -> float:
    """Nota de 0-10 basada en métricas ponderadas."""
    nota = 5.0
    nota += row["goles"] * 1.5
    nota += row["asistencias"] * 1.0
    nota += row["recuperaciones"] * 0.3
    nota += row["pases_buenos"] * 0.1
    nota += row["faltas_recibidas"] * 0.15
    nota -= row["perdidas"] * 0.2
    nota -= row["faltas_cometidas"] * 0.2
    nota -= row["tarjetas_amarillas"] * 0.5
    nota -= row["tarjetas_rojas"] * 1.5
    if row["minutos"] > 0:
        nota += min(row["minutos"] / 90 * 0.5, 0.5)
    return max(0.0, min(10.0, round(nota, 1)))


def color_nota(n: float) -> str:
    if n >= 8:
        return "#4ade80"
    if n >= 6:
        return "#f0c040"
    if n >= 4:
        return "#fb923c"
    return "#f87171"


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
df = cargar_datos()

st.markdown("""
<div class="main-header">
  <div style="font-size:3.5rem">⚽</div>
  <div>
    <div class="subtitle">Temporada 25/26</div>
    <h1>NOAH · STATS</h1>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TABS PRINCIPALES
# ─────────────────────────────────────────────
tab_dashboard, tab_partidos, tab_nuevo, tab_editar = st.tabs([
    "📊  Dashboard", "📋  Partidos", "➕  Nuevo partido", "✏️  Editar / Eliminar"
])


# ══════════════════════════════════════════════
# TAB 1 · DASHBOARD
# ══════════════════════════════════════════════
with tab_dashboard:
    if df.empty:
        st.markdown('<div class="info-box">🏟️ Aún no hay partidos. Ve a <strong>Nuevo partido</strong> para empezar.</div>', unsafe_allow_html=True)
    else:
        # ── KPIs ──────────────────────────────────────────────────────────
        st.markdown('<div class="section-title">TEMPORADA EN NÚMEROS</div>', unsafe_allow_html=True)

        partidos = len(df)
        titulares = int(df["titular"].sum())
        goles = int(df["goles"].sum())
        asistencias = int(df["asistencias"].sum())
        minutos = int(df["minutos"].sum())
        media_min = round(df["minutos"].mean(), 0)
        participaciones = goles + asistencias
        media_pases = round(df["pases_buenos"].mean(), 1)
        tarjetas = int(df["tarjetas_amarillas"].sum() + df["tarjetas_rojas"].sum())

        k1, k2, k3, k4, k5, k6 = st.columns(6)
        kpis = [
            (k1, partidos, "Partidos", f"{titulares} como titular"),
            (k2, goles, "Goles", f"⌀ {round(goles/partidos,2)}/partido"),
            (k3, asistencias, "Asistencias", f"⌀ {round(asistencias/partidos,2)}/partido"),
            (k4, participaciones, "G+A", "Participaciones"),
            (k5, f"{minutos}'", "Minutos", f"⌀ {int(media_min)}' por partido"),
            (k6, media_pases, "Pases/partido", f"{int(df['recuperaciones'].sum())} recuperaciones"),
        ]
        for col, val, label, sub in kpis:
            with col:
                st.markdown(f"""
                <div class="kpi-card">
                  <div class="kpi-label">{label}</div>
                  <div class="kpi-value">{val}</div>
                  <div class="kpi-sub">{sub}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Último partido ────────────────────────────────────────────────
        ultimo = df.iloc[-1]
        nota_ult = nota_rendimiento(ultimo)
        c_nota = color_nota(nota_ult)
        tit_str = "Titular ✅" if ultimo["titular"] == 1 else "Suplente"
        st.markdown(f"""
        <div style="background:#0d1525;border:1px solid #1e293b;border-radius:14px;padding:18px 24px;margin-bottom:20px;">
          <span style="color:#8899aa;font-size:0.72rem;letter-spacing:1.5px;text-transform:uppercase">ÚLTIMO PARTIDO</span>
          <div style="display:flex;align-items:center;gap:24px;margin-top:8px;flex-wrap:wrap">
            <div>
              <span style="font-family:'Bebas Neue',cursive;font-size:1.5rem;color:#f0f0f0">
                {fmt_fecha(ultimo['fecha'])} · vs {ultimo['oponente']}
              </span>
              <span style="margin-left:12px;font-size:0.78rem;color:#64b3f4">{tit_str} · {int(ultimo['minutos'])}'</span>
            </div>
            <div style="margin-left:auto;text-align:center">
              <div style="font-size:0.7rem;color:#8899aa;letter-spacing:1px">NOTA</div>
              <div style="font-family:'Bebas Neue',cursive;font-size:2.2rem;color:{c_nota}">{nota_ult}</div>
            </div>
            <div style="display:flex;gap:20px;flex-wrap:wrap">
              <div style="text-align:center"><div style="font-size:1.5rem">⚽</div><div style="color:#f0f0f0;font-weight:700">{int(ultimo['goles'])}</div></div>
              <div style="text-align:center"><div style="font-size:1.5rem">🤝</div><div style="color:#f0f0f0;font-weight:700">{int(ultimo['asistencias'])}</div></div>
              <div style="text-align:center"><div style="font-size:1.5rem">✅</div><div style="color:#f0f0f0;font-weight:700">{int(ultimo['pases_buenos'])}</div></div>
              <div style="text-align:center"><div style="font-size:1.5rem">🔄</div><div style="color:#f0f0f0;font-weight:700">{int(ultimo['recuperaciones'])}</div></div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Gráficos ──────────────────────────────────────────────────────
        col_izq, col_der = st.columns([3, 2])

        with col_izq:
            st.markdown('<div class="section-title">EVOLUCIÓN</div>', unsafe_allow_html=True)
            metricas_ev = {
                "Goles": "goles", "Asistencias": "asistencias",
                "Pases buenos": "pases_buenos", "Pérdidas": "perdidas",
                "Recuperaciones": "recuperaciones",
            }
            sel = st.multiselect(
                "Métricas", list(metricas_ev.keys()),
                default=["Goles", "Asistencias"],
                label_visibility="collapsed"
            )
            if sel:
                fig = go.Figure()
                fechas_str = df["fecha"].dt.strftime("%d/%m")
                for i, m in enumerate(sel):
                    col_m = metricas_ev[m]
                    fig.add_trace(go.Scatter(
                        x=fechas_str, y=df[col_m],
                        mode="lines+markers",
                        name=m,
                        line=dict(color=COLORES_PLOTLY[i % len(COLORES_PLOTLY)], width=2),
                        marker=dict(size=7),
                    ))
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(13,21,37,0.6)",
                    font=dict(color="#94a3b8", size=11),
                    legend=dict(bgcolor="rgba(0,0,0,0)"),
                    hovermode="x unified",
                    margin=dict(l=0, r=0, t=10, b=0),
                    height=300,
                    xaxis=dict(gridcolor="#1e293b", showgrid=True),
                    yaxis=dict(gridcolor="#1e293b", showgrid=True),
                )
                st.plotly_chart(fig, use_container_width=True)

        with col_der:
            st.markdown('<div class="section-title">RADAR OFENSIVO/DEFENSIVO</div>', unsafe_allow_html=True)
            radar_cats = ["Goles", "Asistencias", "Pases", "Recuperaciones", "Tiros", "Despejes"]
            maximos = [
                max(df["goles"].max(), 1),
                max(df["asistencias"].max(), 1),
                max(df["pases_buenos"].max(), 1),
                max(df["recuperaciones"].max(), 1),
                max(df["tiros"].max(), 1),
                max(df["despejes"].max(), 1),
            ]
            valores_med = [
                df["goles"].mean() / maximos[0] * 10,
                df["asistencias"].mean() / maximos[1] * 10,
                df["pases_buenos"].mean() / maximos[2] * 10,
                df["recuperaciones"].mean() / maximos[3] * 10,
                df["tiros"].mean() / maximos[4] * 10,
                df["despejes"].mean() / maximos[5] * 10,
            ]
            fig_radar = go.Figure(go.Scatterpolar(
                r=valores_med + [valores_med[0]],
                theta=radar_cats + [radar_cats[0]],
                fill="toself",
                line=dict(color="#64b3f4", width=2),
                fillcolor="rgba(100,179,244,0.15)",
            ))
            fig_radar.update_layout(
                polar=dict(
                    bgcolor="rgba(13,21,37,0.8)",
                    radialaxis=dict(visible=True, range=[0, 10], gridcolor="#1e293b", tickcolor="#1e293b"),
                    angularaxis=dict(gridcolor="#1e293b"),
                ),
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94a3b8", size=11),
                margin=dict(l=20, r=20, t=20, b=20),
                height=300,
                showlegend=False,
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        # ── Notas por partido ─────────────────────────────────────────────
        st.markdown('<div class="section-title">NOTA POR PARTIDO</div>', unsafe_allow_html=True)
        df_notas = df.copy()
        df_notas["nota"] = df_notas.apply(nota_rendimiento, axis=1)
        df_notas["fecha_str"] = df_notas["fecha"].dt.strftime("%d/%m")
        df_notas["color"] = df_notas["nota"].apply(color_nota)
        df_notas["label"] = df_notas.apply(lambda r: f"vs {r['oponente']}<br>{r['nota']}", axis=1)

        fig_notas = go.Figure(go.Bar(
            x=df_notas["fecha_str"],
            y=df_notas["nota"],
            marker_color=df_notas["color"],
            text=df_notas["nota"],
            textposition="outside",
            customdata=df_notas["oponente"],
            hovertemplate="<b>%{customdata}</b><br>Nota: %{y}<extra></extra>",
        ))
        fig_notas.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(13,21,37,0.6)",
            font=dict(color="#94a3b8", size=11),
            yaxis=dict(range=[0, 11], gridcolor="#1e293b"),
            xaxis=dict(gridcolor="#1e293b"),
            margin=dict(l=0, r=0, t=10, b=0),
            height=280,
            showlegend=False,
        )
        st.plotly_chart(fig_notas, use_container_width=True)


# ══════════════════════════════════════════════
# TAB 2 · HISTORIAL DE PARTIDOS
# ══════════════════════════════════════════════
with tab_partidos:
    if df.empty:
        st.markdown('<div class="info-box">No hay partidos registrados todavía.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="section-title">TODOS LOS PARTIDOS</div>', unsafe_allow_html=True)

        # Filtros
        fc1, fc2 = st.columns([2, 1])
        with fc1:
            buscar = st.text_input("🔍 Buscar oponente", placeholder="Escribe el nombre del equipo...")
        with fc2:
            filtro_tit = st.selectbox("Rol", ["Todos", "Titular", "Suplente"])

        df_filtrado = df.copy()
        if buscar:
            df_filtrado = df_filtrado[df_filtrado["oponente"].str.contains(buscar, case=False, na=False)]
        if filtro_tit == "Titular":
            df_filtrado = df_filtrado[df_filtrado["titular"] == 1]
        elif filtro_tit == "Suplente":
            df_filtrado = df_filtrado[df_filtrado["titular"] == 0]

        # Añadir nota
        df_filtrado = df_filtrado.copy()
        df_filtrado["nota"] = df_filtrado.apply(nota_rendimiento, axis=1)

        # Preparar para mostrar
        df_show = df_filtrado[["fecha","oponente","titular","minutos","goles","asistencias",
                                 "pases_buenos","perdidas","recuperaciones","tiros",
                                 "despejes","tarjetas_amarillas","tarjetas_rojas","nota"]].copy()
        df_show["fecha"] = df_show["fecha"].apply(fmt_fecha)
        df_show["titular"] = df_show["titular"].map({1: "✅ Titular", 0: "▫️ Suplente"})
        df_show = df_show.rename(columns={
            "fecha": "Fecha", "oponente": "Oponente", "titular": "Rol",
            "minutos": "Min", "goles": "⚽", "asistencias": "🤝",
            "pases_buenos": "Pases ✅", "perdidas": "Pérd ❌",
            "recuperaciones": "Recup 🔄", "tiros": "Tiros 🎯",
            "despejes": "Desp", "tarjetas_amarillas": "🟨",
            "tarjetas_rojas": "🟥", "nota": "Nota ⭐",
        })
        df_show = df_show.sort_values("Fecha", ascending=False)

        st.dataframe(
            df_show,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Nota ⭐": st.column_config.ProgressColumn(
                    "Nota ⭐", min_value=0, max_value=10, format="%.1f"
                ),
            }
        )

        # Resumen del filtro
        st.caption(f"Mostrando {len(df_filtrado)} de {len(df)} partidos")


# ══════════════════════════════════════════════
# TAB 3 · NUEVO PARTIDO
# ══════════════════════════════════════════════
with tab_nuevo:
    st.markdown('<div class="section-title">REGISTRAR PARTIDO</div>', unsafe_allow_html=True)

    if "form_reset" not in st.session_state:
        st.session_state.form_reset = 0

    with st.form(key=f"nuevo_partido_{st.session_state.form_reset}", clear_on_submit=True):
        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("##### 📋 Información del partido")
            f_fecha = st.date_input("📅 Fecha", value=date.today(), format="DD/MM/YYYY")
            f_oponente = st.text_input("🆚 Oponente", placeholder="Nombre del equipo rival")
            f_titular = st.checkbox("⚪ Titular en este partido", value=True)
            f_minutos = st.number_input("⏱️ Minutos jugados", 0, 120, 0, 1)

            st.markdown("##### ⚔️ Ataque")
            f_goles = st.number_input("⚽ Goles", 0, 20, 0, 1)
            f_asistencias = st.number_input("🤝 Asistencias", 0, 20, 0, 1)
            f_tiros = st.number_input("🎯 Tiros a puerta", 0, 20, 0, 1)

        with col_b:
            st.markdown("##### 🔄 Pase y control")
            f_pases_buenos = st.number_input("✅ Pases buenos", 0, 200, 0, 1)
            f_perdidas = st.number_input("❌ Pérdidas de balón", 0, 50, 0, 1)
            f_recuperaciones = st.number_input("🔄 Recuperaciones", 0, 50, 0, 1)

            st.markdown("##### 🛡️ Defensa")
            f_despejes = st.number_input("🧹 Despejes", 0, 50, 0, 1)
            f_faltas_c = st.number_input("👟 Faltas cometidas", 0, 20, 0, 1)
            f_faltas_r = st.number_input("🛡️ Faltas recibidas", 0, 20, 0, 1)

            st.markdown("##### 🟨 Disciplina")
            f_amarillas = st.number_input("🟨 Tarjetas amarillas", 0, 2, 0, 1)
            f_rojas = st.number_input("🟥 Tarjetas rojas", 0, 1, 0, 1)

        st.markdown("---")
        col_btn1, col_btn2 = st.columns([1, 3])
        with col_btn1:
            submitted = st.form_submit_button("💾 Guardar partido", type="primary", use_container_width=True)

        if submitted:
            if not f_oponente.strip():
                st.error("⚠️ El nombre del oponente es obligatorio.")
            else:
                agregar_partido({
                    "fecha": f_fecha,
                    "oponente": f_oponente,
                    "titular": f_titular,
                    "minutos": f_minutos,
                    "pases_buenos": f_pases_buenos,
                    "perdidas": f_perdidas,
                    "recuperaciones": f_recuperaciones,
                    "tiros": f_tiros,
                    "goles": f_goles,
                    "asistencias": f_asistencias,
                    "faltas_cometidas": f_faltas_c,
                    "faltas_recibidas": f_faltas_r,
                    "despejes": f_despejes,
                    "tarjetas_amarillas": f_amarillas,
                    "tarjetas_rojas": f_rojas,
                })
                st.session_state.form_reset += 1
                st.success(f"✅ Partido vs **{f_oponente}** guardado correctamente.")
                st.balloons()
                st.rerun()


# ══════════════════════════════════════════════
# TAB 4 · EDITAR / ELIMINAR
# ══════════════════════════════════════════════
with tab_editar:
    st.markdown('<div class="section-title">EDITAR / ELIMINAR PARTIDO</div>', unsafe_allow_html=True)

    if df.empty:
        st.markdown('<div class="info-box">No hay partidos para editar.</div>', unsafe_allow_html=True)
    else:
        # Selector de partido
        opciones_ed = [
            f"{fmt_fecha(row['fecha'])} · vs {row['oponente']} ({'Titular' if row['titular']==1 else 'Suplente'}) — ⚽{int(row['goles'])} 🤝{int(row['asistencias'])}"
            for _, row in df.iterrows()
        ]
        opciones_ed_inv = list(reversed(range(len(df))))  # más reciente primero

        idx_sel_inv = st.selectbox(
            "Selecciona el partido",
            options=range(len(df)),
            format_func=lambda i: opciones_ed[opciones_ed_inv[i]],
        )
        idx_real = opciones_ed_inv[idx_sel_inv]
        partido = df.iloc[idx_real]

        # Acciones rápidas
        col_del, col_edit_btn = st.columns([1, 4])
        with col_del:
            if st.button("🗑️ Eliminar este partido", type="secondary", use_container_width=True):
                st.session_state["confirm_delete"] = idx_real

        # Confirmación de borrado
        if st.session_state.get("confirm_delete") == idx_real:
            st.warning(f"⚠️ ¿Seguro que quieres eliminar el partido vs **{partido['oponente']}** del {fmt_fecha(partido['fecha'])}?")
            cc1, cc2 = st.columns(2)
            with cc1:
                if st.button("✅ Sí, eliminar", type="primary"):
                    eliminar_partido(idx_real)
                    del st.session_state["confirm_delete"]
                    st.success("Partido eliminado.")
                    st.rerun()
            with cc2:
                if st.button("❌ Cancelar"):
                    del st.session_state["confirm_delete"]
                    st.rerun()

        st.markdown("---")
        st.markdown(f"**Editando:** {fmt_fecha(partido['fecha'])} vs {partido['oponente']}")

        with st.form("formulario_edicion"):
            col_a, col_b = st.columns(2)

            with col_a:
                st.markdown("##### 📋 Partido")
                e_fecha = st.date_input("📅 Fecha", value=pd.Timestamp(partido["fecha"]).date(), format="DD/MM/YYYY")
                e_oponente = st.text_input("🆚 Oponente", value=str(partido["oponente"]))
                e_titular = st.checkbox("⚪ Titular", value=bool(partido["titular"]))
                e_minutos = st.number_input("⏱️ Minutos", 0, 120, int(partido["minutos"]), 1)

                st.markdown("##### ⚔️ Ataque")
                e_goles = st.number_input("⚽ Goles", 0, 20, int(partido["goles"]), 1)
                e_asistencias = st.number_input("🤝 Asistencias", 0, 20, int(partido["asistencias"]), 1)
                e_tiros = st.number_input("🎯 Tiros", 0, 20, int(partido["tiros"]), 1)

            with col_b:
                st.markdown("##### 🔄 Pase y control")
                e_pases = st.number_input("✅ Pases buenos", 0, 200, int(partido["pases_buenos"]), 1)
                e_perdidas = st.number_input("❌ Pérdidas", 0, 50, int(partido["perdidas"]), 1)
                e_recup = st.number_input("🔄 Recuperaciones", 0, 50, int(partido["recuperaciones"]), 1)

                st.markdown("##### 🛡️ Defensa")
                e_despejes = st.number_input("🧹 Despejes", 0, 50, int(partido["despejes"]), 1)
                e_faltas_c = st.number_input("👟 Faltas cometidas", 0, 20, int(partido["faltas_cometidas"]), 1)
                e_faltas_r = st.number_input("🛡️ Faltas recibidas", 0, 20, int(partido["faltas_recibidas"]), 1)

                st.markdown("##### 🟨 Disciplina")
                e_amarillas = st.number_input("🟨 Amarillas", 0, 2, int(partido["tarjetas_amarillas"]), 1)
                e_rojas = st.number_input("🟥 Rojas", 0, 1, int(partido["tarjetas_rojas"]), 1)

            st.markdown("---")
            guardar_ed = st.form_submit_button("💾 Guardar cambios", type="primary")

            if guardar_ed:
                if not e_oponente.strip():
                    st.error("⚠️ El oponente es obligatorio.")
                else:
                    actualizar_partido(idx_real, {
                        "fecha": e_fecha,
                        "oponente": e_oponente,
                        "titular": e_titular,
                        "minutos": e_minutos,
                        "pases_buenos": e_pases,
                        "perdidas": e_perdidas,
                        "recuperaciones": e_recup,
                        "tiros": e_tiros,
                        "goles": e_goles,
                        "asistencias": e_asistencias,
                        "faltas_cometidas": e_faltas_c,
                        "faltas_recibidas": e_faltas_r,
                        "despejes": e_despejes,
                        "tarjetas_amarillas": e_amarillas,
                        "tarjetas_rojas": e_rojas,
                    })
                    st.success("✅ Partido actualizado correctamente.")
                    st.rerun()

# Footer
st.markdown("---")
st.markdown(
    '<div style="text-align:center;color:#334155;font-size:0.75rem;letter-spacing:1px">NOAH STATS · Hecho con ❤️</div>',
    unsafe_allow_html=True
)
