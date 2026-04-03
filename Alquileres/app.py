# app.py — Buscador de Alquileres en Montevideo v2
# Ejecutar: streamlit run app.py

import streamlit as st
import pandas as pd
import re
import time

from scrapers import (
    scrape_mercadolibre, scrape_infocasas, scrape_gallito,
    scrape_casasweb, scrape_casasymas, scrape_remax,
    scrape_acsa, scrape_ciudad_inmobiliaria, scrape_braglia, scrape_lars,
    build_facebook_links,
)
from config import NEIGHBORHOODS, PROPERTY_TYPES, PORTALS, DEPARTMENTS, DEPARTMENT_NAMES

# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Alquileres Montevideo",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# CSS
# ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,wght@0,400;0,500;0,700;1,400&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

/* ── Header ── */
.app-header {
    background: linear-gradient(135deg, #0a1628 0%, #1a3a5c 50%, #0f2d4a 100%);
    border-radius: 18px; padding: 2rem 2.5rem; margin-bottom: 1.5rem;
    color: white; position: relative; overflow: hidden;
}
.app-header::before {
    content: ""; position: absolute; top: -40px; right: -40px;
    width: 200px; height: 200px; border-radius: 50%;
    background: rgba(255,255,255,0.04);
}
.app-header h1 { font-size: 2.1rem; font-weight: 700; margin: 0; color: white; letter-spacing: -0.02em; }
.app-header p  { font-size: 0.95rem; opacity: 0.65; margin: 0.4rem 0 0; }

/* ── Portal tags ── */
.portal-tag {
    display: inline-block; padding: 2px 9px; border-radius: 20px;
    font-size: 0.72rem; font-weight: 700; letter-spacing: 0.02em; white-space: nowrap;
}
.tag-ml   { background: #fff8c0; color: #6b5800; }
.tag-ic   { background: #d0f0e0; color: #0a4020; }
.tag-gal  { background: #ccd8f5; color: #0a1f6e; }
.tag-cw   { background: #fde0e0; color: #7a0000; }
.tag-cm   { background: #ffe5cc; color: #6b2700; }
.tag-rmx  { background: #ffd0d0; color: #7a0000; }
.tag-acsa { background: #dce8f5; color: #0a2040; }
.tag-ci   { background: #ecdcf5; color: #3a0070; }
.tag-brg  { background: #d5ecd6; color: #0a3010; }
.tag-lars { background: #d0e8f5; color: #0a2a40; }
.tag-fb   { background: #d0e4fc; color: #0a2870; }

/* ── Métricas ── */
.metric-row { display: flex; gap: 0.75rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
.metric-card {
    background: #f5f7fa; border-radius: 12px;
    padding: 0.85rem 1.2rem; flex: 1; min-width: 120px;
    border-left: 4px solid #1a3a5c;
}
.metric-card .lbl { font-size: 0.7rem; color: #888; text-transform: uppercase; letter-spacing: 0.06em; }
.metric-card .val { font-size: 1.55rem; font-weight: 700; color: #0a1628; line-height: 1.2; }
.metric-card .val.sm { font-size: 1.1rem; }

/* ── Tabla ── */
.table-wrapper {
    max-height: 68vh; overflow-y: auto; overflow-x: auto;
    border-radius: 12px; border: 1px solid #e0e4ea;
    box-shadow: 0 2px 14px rgba(0,0,0,0.07);
}
.result-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; min-width: 820px; }
.result-table thead th {
    background: #0a1628; color: white; padding: 10px 13px;
    text-align: left; font-size: 0.75rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.05em;
    position: sticky; top: 0; z-index: 2; white-space: nowrap;
}
.result-table tbody tr { border-bottom: 1px solid #edf0f4; transition: background 0.12s; }
.result-table tbody tr:hover { background: #f0f4f9; }
.result-table tbody td { padding: 9px 13px; vertical-align: middle; }
.result-table a { color: #1a3a5c; text-decoration: none; font-weight: 600; border-bottom: 1px dashed #1a3a5c; }
.result-table a:hover { color: #0a1628; border-bottom-style: solid; }

.price-usd { color: #1a6e3a; font-weight: 700; font-family: 'DM Mono', monospace; }
.price-uyu { color: #1a4e9e; font-weight: 700; font-family: 'DM Mono', monospace; }
.price-ask { color: #bbb; font-style: italic; }
.pill      { display:inline-block; background:#eef1f5; border-radius:20px; padding:2px 9px; font-size:0.78rem; color:#445; }
.pill-gc   { display:inline-block; background:#fff3e0; border-radius:20px; padding:2px 9px; font-size:0.78rem; color:#7a4000; font-family:'DM Mono',monospace; }
.no-data   { color: #ccc; }

/* ── Aviso ── */
.aviso-box {
    background: #fff8e1; border-left: 4px solid #f9a825;
    border-radius: 10px; padding: 0.75rem 1rem;
    font-size: 0.83rem; color: #5a4000; margin-bottom: 1rem;
}

/* ── Facebook panel ── */
.fb-panel {
    background: linear-gradient(135deg, #e8f0fe, #f0f4ff);
    border: 1px solid #c5d3f8; border-radius: 14px;
    padding: 1.5rem; margin: 1rem 0;
}
.fb-panel h3 { margin: 0 0 0.8rem; color: #1a1a6e; font-size: 1.1rem; }
.fb-card {
    background: white; border-radius: 10px; padding: 1rem;
    margin-bottom: 0.75rem; border: 1px solid #d8e2f8;
    transition: box-shadow 0.15s;
}
.fb-card:hover { box-shadow: 0 3px 12px rgba(24,119,242,0.15); }
.fb-card a { color: #1877F2; font-weight: 700; font-size: 0.95rem; }
.fb-card .desc { font-size: 0.8rem; color: #666; margin: 0.3rem 0; }
.fb-card .note { font-size: 0.75rem; color: #999; font-style: italic; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] { background: #f5f7fa; }
section[data-testid="stSidebar"] .stCheckbox label { font-size: 0.88rem; }
section[data-testid="stSidebar"] hr { margin: 0.6rem 0; opacity: 0.3; }

/* ── Botón ── */
div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #0a1628, #1a3a5c);
    color: white; border: none; border-radius: 10px;
    font-weight: 700; font-size: 1rem; padding: 0.75rem;
    width: 100%; letter-spacing: 0.02em; transition: opacity 0.2s;
}
div.stButton > button[kind="primary"]:hover { opacity: 0.85; }

/* ── Portal group headers ── */
.portal-group-header {
    font-size: 0.7rem; font-weight: 700; color: #999;
    text-transform: uppercase; letter-spacing: 0.07em;
    margin: 0.8rem 0 0.3rem; padding: 0;
}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Helpers de formato
# ──────────────────────────────────────────────
PORTAL_TAG_CLASS = {
    "MercadoLibre":        "tag-ml",
    "InfoCasas":           "tag-ic",
    "Gallito":             "tag-gal",
    "Casasweb":            "tag-cw",
    "Casas y Más":         "tag-cm",
    "RE/MAX Uruguay":      "tag-rmx",
    "ACSA":                "tag-acsa",
    "Ciudad Inmobiliaria": "tag-ci",
    "Braglia":             "tag-brg",
    "Lars":                "tag-lars",
    "Facebook Marketplace":"tag-fb",
}

def fmt_price(precio: str, moneda: str) -> str:
    if not precio or str(precio).lower() in ("consultar", "", "nan", "none"):
        return '<span class="price-ask">Consultar</span>'
    if moneda == "USD":
        return f'<span class="price-usd">{precio}</span>'
    if moneda == "UYU":
        return f'<span class="price-uyu">{precio}</span>'
    return precio

def fmt_num(val, icon: str = "") -> str:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return '<span class="no-data">—</span>'
    return f'<span class="pill">{icon} {int(val)}</span>'

def fmt_m2(val) -> str:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return '<span class="no-data">—</span>'
    return f'<span class="pill">📐 {int(val)} m²</span>'

def fmt_gc(gastos: str, gastos_num) -> str:
    if not gastos or str(gastos).lower() in ("", "nan", "none"):
        return '<span class="no-data">—</span>'
    return f'<span class="pill-gc">💰 {gastos}</span>'

def tag_portal(fuente: str) -> str:
    cls = PORTAL_TAG_CLASS.get(fuente, "tag-ml")
    return f'<span class="portal-tag {cls}">{fuente}</span>'

def build_table(df: pd.DataFrame) -> str:
    rows = ""
    for _, r in df.iterrows():
        titulo = str(r.get("titulo", ""))
        short  = titulo[:85] + "…" if len(titulo) > 85 else titulo
        link   = str(r.get("link", ""))
        titulo_html = f'<a href="{link}" target="_blank" rel="noopener">{short}</a>' if link else short
        rows += f"""<tr>
            <td>{titulo_html}</td>
            <td>{fmt_price(str(r.get('precio','')), str(r.get('moneda','')))}</td>
            <td style="white-space:nowrap">{fmt_gc(str(r.get('gastos','')), r.get('gastos_num'))}</td>
            <td>{str(r.get('zona',''))[:55]}</td>
            <td style="text-align:center">{fmt_num(r.get('dormitorios'), '🛏')}</td>
            <td style="text-align:center">{fmt_num(r.get('banos'), '🚿')}</td>
            <td style="text-align:center">{fmt_m2(r.get('superficie_m2'))}</td>
            <td>{tag_portal(str(r.get('fuente','')))}</td>
            <td style="text-align:center"><a href="{link}" target="_blank" rel="noopener">Ver →</a></td>
        </tr>"""
    return f"""
    <div class="table-wrapper">
      <table class="result-table">
        <thead><tr>
          <th>Propiedad</th><th>Precio</th><th>Gastos Comunes</th>
          <th>Zona / Barrio</th><th style="text-align:center">Dorm.</th>
          <th style="text-align:center">Baños</th><th style="text-align:center">Superficie</th>
          <th>Portal</th><th style="text-align:center">Link</th>
        </tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>"""


# ──────────────────────────────────────────────
# Mapeo de scraper functions
# ──────────────────────────────────────────────
SCRAPER_FN = {
    "mercadolibre":        scrape_mercadolibre,
    "infocasas":           scrape_infocasas,
    "gallito":             scrape_gallito,
    "casasweb":            scrape_casasweb,
    "casasymas":           scrape_casasymas,
    "remax":               scrape_remax,
    "acsa":                scrape_acsa,
    "ciudad_inmobiliaria": scrape_ciudad_inmobiliaria,
    "braglia":             scrape_braglia,
    "lars":                scrape_lars,
}


# ──────────────────────────────────────────────
# Filtrado
# ──────────────────────────────────────────────
def apply_filters(df: pd.DataFrame, f: dict) -> pd.DataFrame:
    # Filtro por barrio(s) — si hay barrios seleccionados, filtrar por ellos
    if f["neighborhoods"]:
        pat  = "|".join(re.escape(n) for n in f["neighborhoods"])
        mask = df["zona"].str.contains(pat, case=False, na=False, regex=True)
        df   = df[mask]
    # Filtro por departamento — si no es Montevideo, filtrar por nombre del depto en zona
    elif f.get("department") and f["department"] != "Montevideo":
        dept_name = f["department"]
        mask = df["zona"].str.contains(dept_name, case=False, na=False)
        df   = df[mask]

    min_d, max_d = f["bedrooms"]
    if min_d > 0:
        # Solo filtrar por mínimo si el usuario lo especificó — los sin dato pasan
        df = df[df["dormitorios"].isna() | (df["dormitorios"] >= min_d)]
    if max_d < 6:
        # Solo filtrar por máximo si el usuario lo especificó — los sin dato pasan
        df = df[df["dormitorios"].isna() | (df["dormitorios"] <= max_d)]

    # Precio
    min_p, max_p = f["price"]
    currency     = f["currency"]
    if min_p > 0 or max_p < f["price_max"]:
        has_num   = df["precio_num"].notna()
        in_range  = df["precio_num"].between(min_p, max_p)
        # Moneda vacía ("") = desconocida → siempre pasa
        moneda_ok = (currency == "Todas") | (df["moneda"] == currency) | (df["moneda"] == "")
        df = df[~has_num | (in_range & moneda_ok)]
    elif currency != "Todas":
        # Moneda vacía ("") = desconocida → siempre pasa
        df = df[(df["moneda"] == currency) | (df["moneda"] == "")]

    # Gastos comunes
    max_gc = f["max_gastos"]
    if max_gc > 0:
        has_gc  = df["gastos_num"].notna()
        gc_ok   = df["gastos_num"] <= max_gc
        df = df[~has_gc | gc_ok]

    # Superficie
    if f["surface"] > 0:
        df = df[df["superficie_m2"].notna() & (df["superficie_m2"] >= f["surface"])]

    if f["sources"]:
        df = df[df["fuente"].isin(f["sources"])]

    return df


# ──────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔍 Filtros de búsqueda")

    # ── Portales ──────────────────────────────
    st.markdown("### 📡 Portales y fuentes")

    selected_portals = {}
    groups = {}
    for name, cfg in PORTALS.items():
        groups.setdefault(cfg["group"], []).append(name)

    for group_name, portal_names in groups.items():
        st.markdown(f'<p class="portal-group-header">{group_name}</p>', unsafe_allow_html=True)
        cols = st.columns(2)
        for i, pname in enumerate(portal_names):
            default = pname in ("MercadoLibre", "InfoCasas", "Gallito", "Casasweb", "RE/MAX Uruguay")
            with cols[i % 2]:
                selected_portals[pname] = st.checkbox(pname, value=default, key=f"chk_{pname}")

    st.divider()

    # ── Tipo de propiedad ─────────────────────
    st.markdown("### 🏢 Tipo de propiedad")
    prop_key = st.selectbox(
        "Tipo", options=list(PROPERTY_TYPES.keys()), index=1,
        label_visibility="collapsed"
    )
    prop_type_str = PROPERTY_TYPES[prop_key]["key"]

    # ── Departamento ──────────────────────────
    st.markdown("### 🗺️ Departamento")
    selected_dept = st.selectbox(
        "Departamento", options=DEPARTMENT_NAMES, index=0,
        label_visibility="collapsed"
    )

    # ── Barrios (según departamento seleccionado) ──────────────
    dept_barrios = DEPARTMENTS[selected_dept]["barrios"]
    st.markdown("### 📍 Barrio(s)")
    selected_hoods = st.multiselect(
        "Barrios", options=dept_barrios, default=[],
        placeholder="Todos los barrios", label_visibility="collapsed"
    )

    st.divider()

    # ── Dormitorios ───────────────────────────
    st.markdown("### 🛏 Dormitorios")
    bed_range = st.slider("Dormitorios", 0, 6, (0, 6), label_visibility="collapsed")

    # ── Superficie ────────────────────────────
    st.markdown("### 📐 Superficie mínima (m²)")
    min_surface = st.number_input(
        "m²", min_value=0, max_value=500, value=0, step=10, label_visibility="collapsed"
    )

    st.divider()

    # ── Precio ────────────────────────────────
    st.markdown("### 💵 Precio de alquiler ($ UYU)")
    PRICE_MAX = 150_000
    price_range = st.slider(
        "Precio", 0, PRICE_MAX, (0, PRICE_MAX), step=1000, label_visibility="collapsed"
    )
    currency_filter = st.selectbox("Moneda", ["Todas", "UYU", "USD"], index=1)

    st.divider()

    # ── Gastos comunes ────────────────────────
    st.markdown("### 💰 Gastos comunes máx. (UYU)")
    max_gastos = st.number_input(
        "Gastos comunes máximos en $UYU (0 = sin filtro)",
        min_value=0, max_value=50_000, value=0, step=500,
        label_visibility="collapsed",
        help="Filtra anuncios que publiquen gastos comunes superiores a este valor.",
    )

    st.divider()

    # ── Páginas ───────────────────────────────
    st.markdown("### 📄 Páginas por portal")
    max_pages = st.slider(
        "Páginas", min_value=1, max_value=10, value=3,
        help="Más páginas = más resultados pero más tiempo de espera.",
        label_visibility="collapsed"
    )

    st.divider()

    # ── Ordenamiento ─────────────────────────
    st.markdown("### ↕️ Ordenar resultados por")
    sort_by  = st.selectbox(
        "Campo", ["precio_num", "gastos_num", "dormitorios", "superficie_m2", "fuente", "zona"],
        label_visibility="collapsed"
    )
    sort_asc = st.radio(
        "Orden", ["↑ Ascendente", "↓ Descendente"], index=0, label_visibility="collapsed"
    ) == "↑ Ascendente"

    st.divider()
    search_btn = st.button("🔍  Buscar alquileres", type="primary", use_container_width=True)


# ──────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────
n_portals_sel = sum(1 for v in selected_portals.values() if v)
st.markdown(f"""
<div class="app-header">
  <h1>🏠 Alquileres en Uruguay</h1>
  <p>🗺️ <strong>{selected_dept}</strong> · {n_portals_sel} portales seleccionados · 
     MercadoLibre · InfoCasas · Gallito · Casasweb · RE/MAX · y más</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="aviso-box">
  ⚠️ Esta herramienta consulta los portales directamente (requiere internet). 
  Algunos portales pueden devolver pocos resultados si cambiaron su estructura HTML — 
  en ese caso los datos llegan igual desde otros portales. 
  Facebook Marketplace genera links para abrir en tu navegador (requiere cuenta de Facebook).
</div>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# BÚSQUEDA
# ──────────────────────────────────────────────
if "results_df" not in st.session_state:
    st.session_state["results_df"]    = None
if "fb_links" not in st.session_state:
    st.session_state["fb_links"]      = []

if search_btn:
    active_portals = [name for name, checked in selected_portals.items() if checked]

    if not active_portals:
        st.warning("Seleccioná al menos un portal.")
        st.stop()

    all_results  = []
    fb_links     = []
    portal_stats = {}
    total        = len(active_portals)
    progress     = st.progress(0.0)
    status       = st.empty()
    done         = 0

    for portal_name in active_portals:
        portal_cfg  = PORTALS[portal_name]
        scraper_key = portal_cfg["scraper"]

        if scraper_key == "facebook":
            status.text("Facebook Marketplace — generando links…")
            max_usd  = price_range[1] if price_range[1] < 150_000 else 0
            fb_links = build_facebook_links(
                prop_type    = prop_type_str,
                min_bedrooms = bed_range[0],
                min_price    = price_range[0],
                max_price    = max_usd,
            )
            portal_stats[portal_name] = len(fb_links)

        elif scraper_key in SCRAPER_FN:
            fn = SCRAPER_FN[scraper_key]
            try:
                dept_cfg  = DEPARTMENTS.get(selected_dept, {})
                dept_slug = dept_cfg.get("slug_ml", "montevideo")
                # Casasweb uses numeric zone code
                if scraper_key == "casasweb":
                    dept_slug = dept_cfg.get("slug_cw", "13")
                try:
                    results = fn(
                        prop_type        = prop_type_str,
                        max_pages        = max_pages,
                        progress_callback= lambda m: status.text(m),
                        dept_slug        = dept_slug,
                    )
                except TypeError:
                    # fallback for scrapers without dept_slug param
                    results = fn(
                        prop_type        = prop_type_str,
                        max_pages        = max_pages,
                        progress_callback= lambda m: status.text(m),
                    )
                all_results.extend(results)
                portal_stats[portal_name] = len(results)
            except Exception as e:
                portal_stats[portal_name] = 0
                status.text(f"{portal_name} — error: {e}")

        done += 1
        progress.progress(done / total)

    progress.empty()
    status.empty()

    st.session_state["portal_stats"] = portal_stats

    if all_results:
        df = pd.DataFrame(all_results)
        df = df.drop_duplicates(subset=["link"]).reset_index(drop=True)
        for col in ["precio_num", "dormitorios", "banos", "superficie_m2", "gastos_num"]:
            df[col] = pd.to_numeric(df.get(col), errors="coerce")
        st.session_state["results_df"] = df
    else:
        st.session_state["results_df"] = pd.DataFrame()

    st.session_state["fb_links"] = fb_links


# ──────────────────────────────────────────────
# RESULTADOS
# ──────────────────────────────────────────────
df_all  = st.session_state.get("results_df")
fb_links= st.session_state.get("fb_links", [])

# ── Panel de Facebook ──────────────────────────
if fb_links:
    cards_html = ""
    for item in fb_links:
        cards_html += f"""
        <div class="fb-card">
          <div><a href="{item['link']}" target="_blank" rel="noopener">{item['titulo']}</a></div>
          <div class="desc">{item.get('descripcion', '')}</div>
          <div class="note">📌 {item.get('instruccion', '')}</div>
        </div>"""
    st.markdown(f"""
    <div class="fb-panel">
      <h3>🔵 Facebook Marketplace</h3>
      <p style="font-size:0.83rem;color:#555;margin:0 0 1rem">
        Facebook no permite búsqueda automática. Hacé clic en los links para abrir la búsqueda en tu navegador (necesitás estar logueado).
      </p>
      {cards_html}
    </div>
    """, unsafe_allow_html=True)

# ── Tabla de resultados ────────────────────────
if df_all is not None and not df_all.empty:
    active_sources = [n for n, v in selected_portals.items() if v and PORTALS[n]["scraper"] != "facebook"]

    filters = {
        "neighborhoods": selected_hoods,
        "department":    selected_dept,
        "bedrooms":      bed_range,
        "price":         price_range,
        "price_max":     PRICE_MAX,
        "currency":      currency_filter,
        "surface":       min_surface,
        "max_gastos":    max_gastos,
        "sources":       active_sources,
    }

    df_filtered = apply_filters(df_all.copy(), filters)
    df_sorted   = df_filtered.sort_values(sort_by, ascending=sort_asc, na_position="last")

    # Métricas
    prices_usd = df_filtered[df_filtered["moneda"] == "USD"]["precio_num"].dropna()
    prices_uyu = df_filtered[df_filtered["moneda"] == "UYU"]["precio_num"].dropna()
    gastos_val = df_filtered["gastos_num"].dropna()
    avg_usd  = f"USD {prices_usd.mean():,.0f}"  if not prices_usd.empty else "—"
    min_usd  = f"USD {prices_usd.min():,.0f}"   if not prices_usd.empty else "—"
    avg_gc   = f"$ {gastos_val.mean():,.0f}"    if not gastos_val.empty else "—"

    # Contar por portal
    portal_counts = df_filtered.groupby("fuente").size().to_dict()

    metric_cards = f"""
    <div class="metric-row">
      <div class="metric-card">
        <div class="lbl">Total resultados</div>
        <div class="val">{len(df_filtered)}</div>
      </div>
      <div class="metric-card">
        <div class="lbl">Precio prom. USD</div>
        <div class="val sm">{avg_usd}</div>
      </div>
      <div class="metric-card">
        <div class="lbl">Precio mín. USD</div>
        <div class="val sm">{min_usd}</div>
      </div>
      <div class="metric-card">
        <div class="lbl">GC prom. (UYU)</div>
        <div class="val sm">{avg_gc}</div>
      </div>"""
    for portal_name, cnt in sorted(portal_counts.items(), key=lambda x: -x[1]):
        metric_cards += f"""
      <div class="metric-card">
        <div class="lbl">{portal_name}</div>
        <div class="val">{cnt}</div>
      </div>"""
    metric_cards += "</div>"

    st.markdown(metric_cards, unsafe_allow_html=True)

    # Panel estado por portal
    portal_stats = st.session_state.get("portal_stats", {})
    if portal_stats:
        stat_cols = st.columns(min(len(portal_stats), 6))
        for i, (pname, cnt) in enumerate(portal_stats.items()):
            with stat_cols[i % len(stat_cols)]:
                color = "#28a745" if cnt > 0 else "#aaa"
                icon  = "✅" if cnt > 0 else "⚠️"
                st.markdown(
                    f'<div style="background:#f8f9fa;border-radius:8px;padding:0.5rem 0.7rem;'
                    f'border-left:3px solid {color};font-size:0.78rem;margin-bottom:0.5rem">'
                    f'<strong>{pname}</strong><br>'
                    f'<span style="color:{color}">{icon} {cnt} encontrados</span></div>',
                    unsafe_allow_html=True
                )
        st.markdown("<br>", unsafe_allow_html=True)

    # Tabla
    st.markdown(build_table(df_sorted), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Exportar
    col1, col2, _ = st.columns([1, 1, 3])
    with col1:
        csv = df_sorted.to_csv(index=False).encode("utf-8-sig")
        st.download_button("📥 CSV", data=csv, file_name="alquileres_mvd.csv", mime="text/csv")
    with col2:
        try:
            import io
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as w:
                df_sorted.to_excel(w, index=False, sheet_name="Alquileres")
            buf.seek(0)
            st.download_button(
                "📊 Excel", data=buf, file_name="alquileres_mvd.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except ImportError:
            pass

elif df_all is not None and df_all.empty and not fb_links:
    portal_stats = st.session_state.get("portal_stats", {})
    st.markdown("""
    <div style="background:#fff3cd;border-left:4px solid #f9a825;border-radius:10px;padding:1rem 1.2rem;margin-bottom:1rem">
      <strong>⚠️ No se encontraron resultados</strong><br>
      <span style="font-size:0.87rem">
        Algunos portales usan JavaScript y pueden no devolver resultados con scraping simple.
        <strong>MercadoLibre siempre funciona</strong> (usa API oficial).
        Para los demás portales, intentá con menos filtros o más páginas.
      </span>
    </div>
    """, unsafe_allow_html=True)
    if portal_stats:
        cols = st.columns(min(len(portal_stats), 5))
        for i, (pname, cnt) in enumerate(portal_stats.items()):
            with cols[i % len(cols)]:
                color = "#28a745" if cnt > 0 else "#dc3545"
                icon  = "✅" if cnt > 0 else "❌"
                st.markdown(
                    f'<div style="background:#f8f9fa;border-radius:8px;padding:0.6rem 0.8rem;'
                    f'border-left:3px solid {color};font-size:0.82rem">'
                    f'<strong>{icon} {pname}</strong><br>'
                    f'<span style="color:{color}">{cnt} resultados</span></div>',
                    unsafe_allow_html=True
                )

elif df_all is None:
    st.markdown("""
    <div style="text-align:center;padding:4rem 2rem;color:#aaa;">
      <div style="font-size:4rem;margin-bottom:1rem">🏠</div>
      <div style="font-size:1.15rem;font-weight:600;color:#666;margin-bottom:0.5rem">
        Configurá los filtros y hacé clic en <strong>Buscar</strong>
      </div>
      <div style="font-size:0.9rem;color:#999">
        Resultados en tiempo real desde 11 portales y fuentes de Montevideo
      </div>
    </div>
    """, unsafe_allow_html=True)
