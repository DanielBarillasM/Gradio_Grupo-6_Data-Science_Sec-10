"""Laboratorio de analítica comercial construido con Gradio.

El conjunto de datos es sintético y reproducible. Su propósito es demostrar
componentes, eventos, visualizaciones y exportación sin depender de servicios
externos durante la exposición.
"""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path
from typing import Iterable

import gradio as gr
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]
REGIONES = ["Centro", "Norte", "Sur", "Occidente"]
CATEGORIAS = ["Tecnología", "Hogar", "Oficina", "Accesorios"]
CANALES = ["Tienda", "Web", "Distribuidores"]


def construir_datos() -> pd.DataFrame:
    """Genera datos comerciales deterministas para todo 2026."""
    factor_region = {"Centro": 1.16, "Norte": 0.93, "Sur": 0.84, "Occidente": 1.03}
    mezcla_categoria = {"Tecnología": 0.39, "Hogar": 0.24, "Oficina": 0.21, "Accesorios": 0.16}
    mezcla_canal = {"Tienda": 0.44, "Web": 0.36, "Distribuidores": 0.20}
    margen_categoria = {"Tecnología": 0.28, "Hogar": 0.34, "Oficina": 0.31, "Accesorios": 0.42}
    precio_promedio = {"Tecnología": 1_850, "Hogar": 720, "Oficina": 410, "Accesorios": 185}
    estacionalidad = [0.86, 0.91, 0.96, 1.00, 1.06, 1.10, 1.02, 0.99, 1.08, 1.13, 1.22, 1.38]
    registros: list[dict[str, object]] = []

    for numero_mes, mes in enumerate(MESES, start=1):
        tendencia = 1 + (numero_mes - 1) * 0.018
        for indice_region, region in enumerate(REGIONES):
            for indice_categoria, categoria in enumerate(CATEGORIAS):
                for indice_canal, canal in enumerate(CANALES):
                    oscilacion = 1 + (((numero_mes * 7 + indice_region * 5 + indice_categoria * 3 + indice_canal) % 9) - 4) * 0.009
                    ventas = round(
                        92_000
                        * factor_region[region]
                        * mezcla_categoria[categoria]
                        * mezcla_canal[canal]
                        * estacionalidad[numero_mes - 1]
                        * tendencia
                        * oscilacion
                    )
                    unidades = max(1, round(ventas / precio_promedio[categoria]))
                    pedidos = max(1, round(unidades / ({"Tienda": 1.6, "Web": 1.35, "Distribuidores": 4.8}[canal])))
                    margen = margen_categoria[categoria] + (0.015 if canal == "Web" else -0.01 if canal == "Distribuidores" else 0)
                    costo = round(ventas * (1 - margen))
                    satisfaccion = round(4.15 + indice_region * 0.08 + indice_canal * 0.05 - indice_categoria * 0.03 + (numero_mes % 3) * 0.04, 2)
                    registros.append(
                        {
                            "Fecha": pd.Timestamp(2026, numero_mes, 1),
                            "Mes": mes,
                            "Mes_n": numero_mes,
                            "Región": region,
                            "Categoría": categoria,
                            "Canal": canal,
                            "Ventas": ventas,
                            "Costo": costo,
                            "Margen_bruto": ventas - costo,
                            "Unidades": unidades,
                            "Pedidos": pedidos,
                            "Satisfacción": min(satisfaccion, 4.95),
                        }
                    )

    return pd.DataFrame(registros)


DATOS = construir_datos()

PALETA = {
    "fondo": "#0A1020",
    "panel": "#111A2E",
    "panel_2": "#17233A",
    "texto": "#F8FAFC",
    "muted": "#9AA8C1",
    "violeta": "#7C6CFF",
    "naranja": "#FF7A45",
    "verde": "#4ED3A7",
    "azul": "#55B8FF",
    "grid": "#2A3852",
}


def _seleccion(valor: Iterable[str] | None, opciones: list[str]) -> list[str]:
    elegidos = list(valor or [])
    return elegidos if elegidos else opciones


def filtrar_datos(
    regiones: Iterable[str] | None,
    categorias: Iterable[str] | None,
    canales: Iterable[str] | None,
    rango_meses: Iterable[int] | None,
) -> pd.DataFrame:
    """Devuelve una copia filtrada; una selección vacía significa 'todas'."""
    regiones_ok = _seleccion(regiones, REGIONES)
    categorias_ok = _seleccion(categorias, CATEGORIAS)
    canales_ok = _seleccion(canales, CANALES)
    inicio, fin = [int(valor) for valor in (list(rango_meses or [1, 12]))]
    inicio, fin = min(inicio, fin), max(inicio, fin)

    mascara = (
        DATOS["Región"].isin(regiones_ok)
        & DATOS["Categoría"].isin(categorias_ok)
        & DATOS["Canal"].isin(canales_ok)
        & DATOS["Mes_n"].between(inicio, fin)
    )
    return DATOS.loc[mascara].copy()


def _estilo_figura(figura: go.Figure, altura: int = 390) -> go.Figure:
    figura.update_layout(
        height=altura,
        margin=dict(l=48, r=24, t=60, b=44),
        paper_bgcolor=PALETA["panel"],
        plot_bgcolor=PALETA["panel"],
        font=dict(family="Aptos, Segoe UI, sans-serif", color=PALETA["texto"], size=13),
        title=dict(font=dict(size=18, color=PALETA["texto"]), x=0.02, xanchor="left"),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1),
        hoverlabel=dict(bgcolor=PALETA["panel_2"], font_color=PALETA["texto"]),
    )
    figura.update_xaxes(gridcolor=PALETA["grid"], zeroline=False, linecolor=PALETA["grid"])
    figura.update_yaxes(gridcolor=PALETA["grid"], zeroline=False, linecolor=PALETA["grid"])
    return figura


def _formato_moneda(valor: float) -> str:
    return f"Q {valor:,.0f}"


def _kpis_html(
    ventas: float,
    crecimiento: float,
    margen: float,
    ticket: float,
    cumplimiento: float,
) -> str:
    crecimiento_clase = "positive" if crecimiento >= 0 else "negative"
    flecha = "↑" if crecimiento >= 0 else "↓"
    return f"""
    <section class="kpi-grid" aria-label="Indicadores principales">
      <article class="metric"><span>Ventas netas</span><strong>{_formato_moneda(ventas)}</strong><small>Periodo filtrado</small></article>
      <article class="metric"><span>Crecimiento</span><strong class="{crecimiento_clase}">{flecha} {abs(crecimiento):.1f}%</strong><small>Primer mes vs. último</small></article>
      <article class="metric"><span>Margen bruto</span><strong>{margen:.1f}%</strong><small>Ventas menos costo</small></article>
      <article class="metric"><span>Ticket promedio</span><strong>{_formato_moneda(ticket)}</strong><small>Por pedido</small></article>
      <article class="metric accent"><span>Cumplimiento</span><strong>{cumplimiento:.1f}%</strong><small>Respecto a la meta</small></article>
    </section>
    """


def _figura_tendencia(datos: pd.DataFrame, metrica: str, visualizacion: str, meta_mensual: int) -> go.Figure:
    agregacion = datos.groupby(["Mes_n", "Mes"], as_index=False).agg(
        Ventas=("Ventas", "sum"),
        Unidades=("Unidades", "sum"),
        Margen_bruto=("Margen_bruto", "sum"),
        Costo=("Costo", "sum"),
    ).sort_values("Mes_n")

    if metrica == "Margen (%)":
        agregacion[metrica] = agregacion["Margen_bruto"] / agregacion["Ventas"] * 100
        columna = metrica
        titulo = "Margen bruto mensual"
    elif metrica == "Margen bruto":
        columna = "Margen_bruto"
        titulo = "Margen bruto mensual"
    else:
        columna = metrica
        titulo = f"{metrica} por mes"

    argumentos = dict(data_frame=agregacion, x="Mes", y=columna)
    if visualizacion == "Barras":
        figura = px.bar(**argumentos, color_discrete_sequence=[PALETA["violeta"]])
    elif visualizacion == "Área":
        figura = px.area(**argumentos, color_discrete_sequence=[PALETA["violeta"]])
    else:
        figura = px.line(**argumentos, markers=True, color_discrete_sequence=[PALETA["violeta"]])

    if metrica == "Ventas":
        proporcion = (datos["Categoría"].nunique() / len(CATEGORIAS)) * (datos["Canal"].nunique() / len(CANALES))
        meta_periodo = meta_mensual * datos["Región"].nunique() * proporcion
        figura.add_trace(
            go.Scatter(
                x=agregacion["Mes"],
                y=[meta_periodo] * len(agregacion),
                mode="lines",
                name="Meta ajustada",
                line=dict(color=PALETA["naranja"], dash="dash", width=2),
                hovertemplate="Meta: Q %{y:,.0f}<extra></extra>",
            )
        )

    figura.update_traces(hovertemplate="%{x}<br>%{y:,.1f}<extra></extra>")
    figura.update_layout(title=titulo, yaxis_title=metrica, xaxis_title="")
    return _estilo_figura(figura, 420)


def _figura_categorias(datos: pd.DataFrame) -> go.Figure:
    resumen = datos.groupby("Categoría", as_index=False)["Ventas"].sum().sort_values("Ventas", ascending=False)
    figura = px.pie(
        resumen,
        names="Categoría",
        values="Ventas",
        hole=0.62,
        color_discrete_sequence=[PALETA["violeta"], PALETA["naranja"], PALETA["verde"], PALETA["azul"]],
    )
    figura.update_traces(textposition="inside", textinfo="percent", hovertemplate="%{label}<br>Q %{value:,.0f}<extra></extra>")
    figura.update_layout(title="Mezcla de ventas por categoría")
    return _estilo_figura(figura, 380)


def _figura_regiones(datos: pd.DataFrame) -> go.Figure:
    resumen = datos.groupby("Región", as_index=False).agg(Ventas=("Ventas", "sum"), Margen=("Margen_bruto", "sum"))
    resumen["Margen_pct"] = resumen["Margen"] / resumen["Ventas"] * 100
    resumen = resumen.sort_values("Ventas")
    figura = px.bar(
        resumen,
        x="Ventas",
        y="Región",
        orientation="h",
        color="Margen_pct",
        color_continuous_scale=[[0, PALETA["azul"]], [1, PALETA["verde"]]],
        text_auto=".3s",
    )
    figura.update_traces(hovertemplate="%{y}<br>Ventas: Q %{x:,.0f}<extra></extra>")
    figura.update_layout(title="Rendimiento regional", xaxis_title="Ventas (Q)", yaxis_title="", coloraxis_showscale=False)
    return _estilo_figura(figura, 380)


def _figura_calor(datos: pd.DataFrame) -> go.Figure:
    pivote = datos.pivot_table(index="Región", columns="Mes_n", values="Ventas", aggfunc="sum", fill_value=0)
    pivote = pivote.reindex(index=[r for r in REGIONES if r in pivote.index])
    meses_presentes = list(pivote.columns)
    figura = go.Figure(
        data=go.Heatmap(
            z=pivote.values,
            x=[MESES[numero - 1] for numero in meses_presentes],
            y=pivote.index,
            colorscale=[[0, "#18243B"], [0.45, PALETA["violeta"]], [1, PALETA["naranja"]]],
            colorbar=dict(title="Q", thickness=12),
            hovertemplate="%{y} · %{x}<br>Q %{z:,.0f}<extra></extra>",
        )
    )
    figura.update_layout(title="Intensidad de ventas por región y mes", xaxis_title="", yaxis_title="")
    return _estilo_figura(figura, 390)


def _hallazgos_html(datos: pd.DataFrame, crecimiento: float, cumplimiento: float) -> str:
    mejor_region = datos.groupby("Región")["Ventas"].sum().idxmax()
    mejor_categoria = datos.groupby("Categoría")["Ventas"].sum().idxmax()
    mejor_canal = datos.groupby("Canal")["Ventas"].sum().idxmax()
    mejor_mes_n = int(datos.groupby("Mes_n")["Ventas"].sum().idxmax())
    direccion = "creció" if crecimiento >= 0 else "disminuyó"
    estado_meta = "supera" if cumplimiento >= 100 else "aún no alcanza"
    return f"""
    <section class="insight-panel">
      <div><span>Lectura ejecutiva</span><h3>El periodo {estado_meta} la meta definida.</h3></div>
      <ol>
        <li><strong>{mejor_region}</strong> lidera el desempeño regional.</li>
        <li><strong>{mejor_categoria}</strong> aporta la mayor facturación y <strong>{mejor_canal}</strong> es el canal principal.</li>
        <li>El mejor mes es <strong>{MESES[mejor_mes_n - 1]}</strong>.</li>
        <li>Entre el primer y último mes visible, la venta {direccion} <strong>{abs(crecimiento):.1f}%</strong>.</li>
      </ol>
    </section>
    """


def actualizar_dashboard(
    regiones: Iterable[str] | None,
    categorias: Iterable[str] | None,
    canales: Iterable[str] | None,
    mes_inicio: int,
    mes_fin: int,
    meta_mensual: int,
    metrica: str,
    visualizacion: str,
):
    """Calcula todos los elementos coordinados de la aplicación."""
    datos = filtrar_datos(regiones, categorias, canales, [mes_inicio, mes_fin])
    if datos.empty:
        raise gr.Error("Los filtros no contienen registros. Amplía el periodo o la selección.")

    ventas = float(datos["Ventas"].sum())
    margen_bruto = float(datos["Margen_bruto"].sum())
    margen_pct = margen_bruto / ventas * 100 if ventas else 0
    pedidos = int(datos["Pedidos"].sum())
    ticket = ventas / pedidos if pedidos else 0

    mensual = datos.groupby("Mes_n")["Ventas"].sum().sort_index()
    crecimiento = ((mensual.iloc[-1] / mensual.iloc[0]) - 1) * 100 if len(mensual) > 1 and mensual.iloc[0] else 0
    meses_visibles = datos["Mes_n"].nunique()
    proporcion = (datos["Categoría"].nunique() / len(CATEGORIAS)) * (datos["Canal"].nunique() / len(CANALES))
    meta_total = meta_mensual * datos["Región"].nunique() * meses_visibles * proporcion
    cumplimiento = ventas / meta_total * 100 if meta_total else 0

    inicio, fin = int(datos["Mes_n"].min()), int(datos["Mes_n"].max())
    status = f"""
    <div class="coverage">
      <span class="live-dot"></span>
      <strong>{len(datos):,} observaciones</strong>
      <span>{MESES[inicio - 1]}–{MESES[fin - 1]} de 2026</span>
      <span>{datos['Región'].nunique()} regiones · {datos['Categoría'].nunique()} categorías · {datos['Canal'].nunique()} canales</span>
    </div>
    """

    tabla = datos.sort_values(["Fecha", "Región", "Categoría", "Canal"], ascending=[False, True, True, True]).copy()
    tabla["Fecha"] = tabla["Fecha"].dt.strftime("%Y-%m")
    tabla["Ventas"] = tabla["Ventas"].map(_formato_moneda)
    tabla["Margen_bruto"] = tabla["Margen_bruto"].map(_formato_moneda)
    tabla["Satisfacción"] = tabla["Satisfacción"].map(lambda valor: f"{valor:.2f} / 5")
    tabla = tabla[["Fecha", "Región", "Categoría", "Canal", "Ventas", "Margen_bruto", "Unidades", "Pedidos", "Satisfacción"]]

    return (
        status,
        _kpis_html(ventas, crecimiento, margen_pct, ticket, cumplimiento),
        _figura_tendencia(datos, metrica, visualizacion, meta_mensual),
        _figura_categorias(datos),
        _figura_regiones(datos),
        _figura_calor(datos),
        _hallazgos_html(datos, crecimiento, cumplimiento),
        tabla,
    )


def exportar_csv(
    regiones: Iterable[str] | None,
    categorias: Iterable[str] | None,
    canales: Iterable[str] | None,
    mes_inicio: int,
    mes_fin: int,
) -> str:
    datos = filtrar_datos(regiones, categorias, canales, [mes_inicio, mes_fin])
    archivo = tempfile.NamedTemporaryFile(prefix="gradio_ventas_", suffix=".csv", delete=False)
    archivo.close()
    ruta = Path(archivo.name)
    datos.to_csv(ruta, index=False, encoding="utf-8-sig")
    return str(ruta)


def valores_iniciales():
    return REGIONES, CATEGORIAS, CANALES, 1, 12, 95_000, "Ventas", "Línea"


CSS = """
:root, .dark {
  --body-background-fill: #0A1020 !important;
  --body-background-fill-dark: #0A1020 !important;
  --body-text-color: #F8FAFC !important;
  --body-text-color-dark: #F8FAFC !important;
  --background-fill-primary: #111A2E !important;
  --background-fill-primary-dark: #111A2E !important;
  --background-fill-secondary: #17233A !important;
  --background-fill-secondary-dark: #17233A !important;
  --block-background-fill: #111A2E !important;
  --block-background-fill-dark: #111A2E !important;
  --block-border-color: #2A3852 !important;
  --block-border-color-dark: #2A3852 !important;
  --input-background-fill: #0D1628 !important;
  --input-background-fill-dark: #0D1628 !important;
  --input-border-color: #31415E !important;
  --input-border-color-dark: #31415E !important;
}

html, body { overflow-x: hidden; background: #0A1020 !important; color-scheme: dark; }
body > gradio-app, gradio-app, .gradio-container, .main { width: 100% !important; }
.gradio-container, gradio-app .gradio-container, .main > .wrap {
  box-sizing: border-box !important;
  width: min(1360px, calc(100vw - 40px)) !important;
  max-width: 1360px !important;
  margin-inline: auto !important;
  padding-inline: 0 !important;
  overflow: hidden !important;
}
.gradio-container * { box-sizing: border-box; }
.gradio-container .gr-row { min-width: 0 !important; }
.gradio-container .gr-row > * { min-width: 0 !important; }

.hero {
  position: relative;
  overflow: hidden;
  margin: 18px 0 16px;
  padding: 34px 38px;
  border: 1px solid #2A3852;
  border-radius: 20px;
  background: linear-gradient(120deg, #111A2E 0%, #111A2E 62%, #201B49 100%);
}
.hero::after {
  content: "";
  position: absolute;
  width: 220px;
  height: 220px;
  right: -70px;
  top: -80px;
  border: 36px solid #7C6CFF;
  border-radius: 50%;
  opacity: .45;
}
.hero p { margin: 0; color: #AAB6CC; font-size: 15px; }
.hero h1 { max-width: 820px; margin: 8px 0 12px; color: #F8FAFC; font-size: clamp(32px, 4vw, 54px); line-height: 1.02; letter-spacing: -.035em; }
.hero .course { color: #FF9A6E; font-weight: 700; }

.filter-shell { overflow: hidden !important; padding: 14px !important; border: 1px solid #2A3852 !important; border-radius: 18px !important; background: #111A2E !important; }
.filter-shell .form, .filter-shell > div { background: #111A2E !important; border-color: #2A3852 !important; }
.filter-row, .settings-row, .plot-row { flex-wrap: wrap !important; gap: 12px !important; }
.filter-row > * { flex: 1 1 230px !important; }
.settings-row > * { flex: 1 1 190px !important; }
.actions > * { min-width: 150px !important; }
.actions button:not(.primary) { border-color: #3B4B69 !important; background: #17233A !important; color: #E7ECF6 !important; }
.plot-row > * { flex: 1 1 470px !important; }

.gradio-container .token {
  border: 1px solid #3A4A68 !important;
  background: #24324D !important;
  color: #F8FAFC !important;
}
.gradio-container .token span { color: #F8FAFC !important; }
.gradio-container .token-remove svg { fill: #C9D3E5 !important; }
.gradio-container label[data-testid$="-radio-label"] {
  border: 1px solid #34435F !important;
  background: #17233A !important;
  color: #D5DDEC !important;
}
.gradio-container label[data-testid$="-radio-label"] span { color: inherit !important; }
.gradio-container label[data-testid$="-radio-label"]:has(input:checked) {
  border-color: #7C6CFF !important;
  background: #6657EF !important;
  color: #FFFFFF !important;
}

.coverage { display: flex; flex-wrap: wrap; gap: 10px 20px; align-items: center; margin: 8px 2px 14px; color: #9AA8C1; font-size: 14px; }
.coverage strong { color: #F8FAFC; }
.live-dot { width: 9px; height: 9px; border-radius: 50%; background: #4ED3A7; box-shadow: 0 0 0 5px rgb(78 211 167 / 12%); }

.kpi-grid { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 12px; width: 100%; margin-bottom: 14px; }
.metric { min-width: 0; padding: 20px; border: 1px solid #2A3852; border-radius: 16px; background: #111A2E; }
.metric span, .metric small { display: block; color: #9AA8C1; }
.metric span { font-size: 14px; }
.metric strong { display: block; overflow: hidden; margin: 9px 0 5px; color: #F8FAFC; font-size: clamp(21px, 2.15vw, 30px); line-height: 1.05; letter-spacing: -.035em; text-overflow: ellipsis; white-space: nowrap; }
.metric small { font-size: 12px; }
.metric.accent { border-color: #7C6CFF; background: linear-gradient(145deg, #171F3D, #201B49); }
.metric .positive { color: #4ED3A7; }
.metric .negative { color: #FF7A7A; }

.insight-panel { display: grid; grid-template-columns: minmax(230px, .75fr) minmax(0, 1.25fr); gap: 34px; padding: 28px; border-left: 7px solid #FF7A45; border-radius: 14px; background: #111A2E; }
.insight-panel span { color: #FF9A6E; font-weight: 700; }
.insight-panel h3 { margin: 9px 0 0; color: #F8FAFC; font-size: 28px; line-height: 1.15; }
.insight-panel ol { margin: 0; padding-left: 1.3em; color: #C9D3E5; }
.insight-panel li { margin-bottom: 11px; }

.gradio-container .block, .gradio-container .form { border-radius: 14px !important; }
.gradio-container .tabs { overflow: hidden !important; }
.gradio-container button.primary { background: #7C6CFF !important; border-color: #7C6CFF !important; color: white !important; }
.gradio-container button.primary:hover { background: #6D5CF4 !important; }
.gradio-container footer { margin-top: 26px; }

@media (max-width: 1050px) {
  .kpi-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}
@media (max-width: 720px) {
  .gradio-container, gradio-app .gradio-container, .main > .wrap { width: min(100%, calc(100vw - 20px)) !important; }
  .hero { padding: 26px 22px; }
  .kpi-grid { grid-template-columns: 1fr 1fr; }
  .metric.accent { grid-column: 1 / -1; }
  .insight-panel { grid-template-columns: 1fr; }
  .filter-row > *, .settings-row > *, .plot-row > * { flex-basis: 100% !important; }
}
@media (max-width: 460px) {
  .kpi-grid { grid-template-columns: 1fr; }
  .metric.accent { grid-column: auto; }
}
"""


with gr.Blocks(title="Observatorio comercial | Gradio") as demo:
    gr.HTML(
        """
        <header class="hero">
          <p class="course">CC3084 · Data Science · Sección 10 · Grupo 6</p>
          <h1>Observatorio comercial interactivo</h1>
          <p>Explora ventas sintéticas de 2026, compara segmentos y convierte filtros en decisiones.</p>
        </header>
        """
    )

    with gr.Group(elem_classes="filter-shell"):
        with gr.Row(elem_classes="filter-row"):
            regiones = gr.Dropdown(REGIONES, value=REGIONES, multiselect=True, label="Regiones")
            categorias = gr.Dropdown(CATEGORIAS, value=CATEGORIAS, multiselect=True, label="Categorías")
            canales = gr.Dropdown(CANALES, value=CANALES, multiselect=True, label="Canales")
        with gr.Row(elem_classes="settings-row"):
            mes_inicio = gr.Slider(1, 12, value=1, step=1, label="Mes inicial")
            mes_fin = gr.Slider(1, 12, value=12, step=1, label="Mes final")
            meta = gr.Slider(60_000, 140_000, value=95_000, step=5_000, label="Meta mensual por región (Q)")
            metrica = gr.Radio(["Ventas", "Unidades", "Margen bruto", "Margen (%)"], value="Ventas", label="Métrica principal")
            visualizacion = gr.Radio(["Línea", "Barras", "Área"], value="Línea", label="Visualización")
        with gr.Row(elem_classes="actions"):
            aplicar = gr.Button("Aplicar filtros", variant="primary")
            restablecer = gr.Button("Restablecer")

    cobertura = gr.HTML()
    indicadores = gr.HTML()

    with gr.Tabs():
        with gr.Tab("Resumen ejecutivo"):
            tendencia = gr.Plot(show_label=False)
            with gr.Row(elem_classes="plot-row"):
                categorias_plot = gr.Plot(show_label=False)
                regiones_plot = gr.Plot(show_label=False)
        with gr.Tab("Patrones y hallazgos"):
            hallazgos = gr.HTML()
            calor = gr.Plot(show_label=False)
        with gr.Tab("Datos y exportación"):
            detalle = gr.Dataframe(label="Registros filtrados", interactive=False, max_height=520)
            with gr.Row():
                exportar = gr.Button("Preparar CSV", variant="primary")
                archivo_csv = gr.File(label="Descarga", interactive=False)

    entradas = [regiones, categorias, canales, mes_inicio, mes_fin, meta, metrica, visualizacion]
    salidas = [cobertura, indicadores, tendencia, categorias_plot, regiones_plot, calor, hallazgos, detalle]

    aplicar.click(actualizar_dashboard, entradas, salidas, concurrency_limit=4)
    demo.load(actualizar_dashboard, entradas, salidas)
    restablecer.click(
        valores_iniciales,
        outputs=[regiones, categorias, canales, mes_inicio, mes_fin, meta, metrica, visualizacion],
    ).then(actualizar_dashboard, entradas, salidas)
    exportar.click(exportar_csv, [regiones, categorias, canales, mes_inicio, mes_fin], archivo_csv)


def main() -> None:
    parser = argparse.ArgumentParser(description="Ejecuta el observatorio comercial en Gradio.")
    parser.add_argument("--share", action="store_true", help="Crea un enlace público temporal.")
    parser.add_argument("--port", type=int, default=7860, help="Puerto local (predeterminado: 7860).")
    args = parser.parse_args()
    demo.queue(default_concurrency_limit=4).launch(
        share=args.share,
        server_port=args.port,
        theme=gr.themes.Soft(primary_hue="indigo", secondary_hue="orange", neutral_hue="slate"),
        css=CSS,
        max_file_size="10mb",
    )


if __name__ == "__main__":
    main()
