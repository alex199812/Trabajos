# app.py — BuscaEmpleo Uruguay — tabla limpia v6
import streamlit as st
import pandas as pd
import re

from scrapers import (
    scrape_buscojobs, scrape_gallito, build_gallito_links,
    scrape_computrabajo, build_computrabajo_links,
    scrape_empleosuruguay, scrape_trabajoencasa,
    scrape_vacantes, build_linkedin_links,
)
from config import (
    CATEGORIAS, LOCALIDADES, MODALIDADES, EXPERIENCIAS,
    JORNADAS, SECTORES, PORTALS, FECHAS, FECHA_PARAMS,
)

st.set_page_config(
    page_title="BuscaEmpleo Uruguay",
    page_icon="🇺🇾",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
:root{--bg:#0d0f1a;--s1:#141728;--s2:#1c2038;--s3:#232848;--acc:#6c63ff;--acc2:#a78bfa;--acc3:#4ade80;--tx:#e2e8f0;--mu:#8892a4;--bd:#2a2f52;--r:12px;--r2:8px;}
html,body,[class*="css"],.stApp{font-family:'Inter','Segoe UI',system-ui,sans-serif!important;background:var(--bg)!important;color:var(--tx)!important;}
.block-container{padding:1.2rem 1.5rem 3rem!important;max-width:1300px!important;}
.main{background:var(--bg)!important;}

/* Sidebar */
section[data-testid="stSidebar"]{background:var(--s1)!important;border-right:1px solid var(--bd)!important;}
section[data-testid="stSidebar"] label,section[data-testid="stSidebar"] p,section[data-testid="stSidebar"] .stMarkdown,section[data-testid="stSidebar"] div{color:#cbd5e1!important;}
section[data-testid="stSidebar"] .stSelectbox>div>div,section[data-testid="stSidebar"] .stTextInput>div>div{background:var(--s2)!important;border:1px solid var(--bd)!important;border-radius:var(--r2)!important;color:var(--tx)!important;}
.sb-sec{font-size:.67rem;font-weight:700;color:var(--mu)!important;text-transform:uppercase;letter-spacing:.1em;margin:.8rem 0 .25rem;border-top:1px solid var(--bd);padding-top:.7rem;}
section[data-testid="stSidebar"] hr{border-color:var(--bd)!important;margin:.5rem 0;}
.portal-group{font-size:.65rem;font-weight:700;color:var(--mu)!important;text-transform:uppercase;letter-spacing:.1em;margin:.5rem 0 .15rem;}
div.stButton>button[kind="primary"]{background:linear-gradient(135deg,var(--acc),#8b5cf6)!important;color:#fff!important;border:none!important;border-radius:var(--r2)!important;font-weight:700!important;font-size:.95rem!important;padding:.7rem!important;width:100%!important;transition:all .2s!important;}
div.stButton>button[kind="primary"]:hover{opacity:.88!important;transform:translateY(-1px)!important;}
section[data-testid="stSidebar"] .stCheckbox label{font-size:.83rem!important;color:#94a3b8!important;}

/* Hero */
.hero{background:linear-gradient(135deg,var(--s1) 0%,var(--s2) 50%,#0f2744 100%);border:1px solid var(--bd);border-radius:18px;padding:2rem 2.5rem;margin-bottom:1.5rem;position:relative;overflow:hidden;}
.hero::before{content:"";position:absolute;width:400px;height:400px;border-radius:50%;top:-150px;right:-100px;background:radial-gradient(circle,rgba(108,99,255,.18) 0%,transparent 65%);pointer-events:none;}
.hero-live{display:inline-flex;align-items:center;gap:7px;background:rgba(74,222,128,.12);border:1px solid rgba(74,222,128,.3);color:var(--acc3);border-radius:20px;padding:4px 13px;font-size:.7rem;font-weight:700;letter-spacing:.06em;margin-bottom:.8rem;}
.hero-dot{width:7px;height:7px;border-radius:50%;background:var(--acc3);animation:pulse 1.8s infinite;}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.4;transform:scale(1.4)}}
.hero h1{font-size:2.2rem;font-weight:800;color:#fff;letter-spacing:-.04em;margin:0 0 .4rem;}
.hero h1 span{color:var(--acc2);}
.hero-sub{font-size:.88rem;color:rgba(255,255,255,.42);}
.chips-row{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:1rem;}
.chip-f{display:inline-flex;align-items:center;gap:5px;background:rgba(108,99,255,.14);border:1px solid rgba(108,99,255,.35);color:var(--acc2);border-radius:20px;padding:4px 13px;font-size:.75rem;font-weight:500;}

/* Tabla */
.tbl-wrap{overflow-x:auto;border-radius:var(--r);border:1px solid var(--bd);margin-bottom:1rem;}
.rtable{width:100%;border-collapse:collapse;font-size:.83rem;}
.rtable thead th{background:var(--s2);color:var(--mu);padding:10px 14px;text-align:left;font-size:.7rem;font-weight:600;text-transform:uppercase;letter-spacing:.07em;white-space:nowrap;border-bottom:1px solid var(--bd);}
.rtable tbody tr{border-bottom:1px solid var(--bd);transition:background .12s;}
.rtable tbody tr:hover{background:var(--s2);}
.rtable tbody td{padding:10px 14px;vertical-align:middle;color:var(--tx);}
.rtable a.job-link{color:var(--acc2);text-decoration:none;font-weight:600;font-size:.85rem;}
.rtable a.job-link:hover{color:#c4b5fd;text-decoration:underline;}
.rtable a.btn-ver{display:inline-block;padding:5px 14px;background:linear-gradient(135deg,var(--acc),#8b5cf6);color:#fff;border-radius:6px;font-size:.73rem;font-weight:600;text-decoration:none;white-space:nowrap;}
.rtable a.btn-ver:hover{opacity:.85;}
.co-cell{font-size:.78rem;color:var(--mu);}
.zo-pill{display:inline-block;background:var(--s2);border:1px solid var(--bd);border-radius:5px;padding:2px 8px;font-size:.72rem;color:var(--mu);}
.mod-rem{color:#4ade80;font-size:.75rem;}
.mod-pre{color:#60a5fa;font-size:.75rem;}
.mod-hyb{color:#fb923c;font-size:.75rem;}
.portal-dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:5px;}
.date-cell{font-size:.73rem;color:var(--mu);white-space:nowrap;}
.nd{color:var(--bd);}

/* Métricas */
.metrics-row{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:1rem;}
.metric{background:var(--s1);border:1px solid var(--bd);border-radius:var(--r2);padding:.7rem 1.1rem;flex:1;min-width:100px;}
.metric .mv{font-size:1.4rem;font-weight:800;color:var(--tx);line-height:1.1;}
.metric .ml{font-size:.63rem;color:var(--mu);text-transform:uppercase;letter-spacing:.08em;margin-top:2px;}

/* Estado portales */
.pstats{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:1rem;}
.pstat{display:inline-flex;align-items:center;gap:5px;background:var(--s2);border:1px solid var(--bd);border-radius:var(--r2);padding:5px 11px;font-size:.75rem;}
.pstat.ok{border-color:rgba(74,222,128,.4);color:#4ade80;}
.pstat.warn{color:var(--mu);}
.pstat.lnk{border-color:rgba(108,99,255,.4);color:var(--acc2);}

/* Panel links externos */
.ext-panel{background:var(--s1);border:1px solid var(--bd);border-radius:var(--r);padding:16px;margin-bottom:14px;}
.ext-panel h4{font-size:.75rem;font-weight:700;color:var(--mu);text-transform:uppercase;letter-spacing:.08em;margin-bottom:10px;}
.ecard{display:flex;align-items:center;justify-content:space-between;gap:12px;background:var(--s2);border:1px solid var(--bd);border-radius:var(--r2);padding:11px 14px;margin-bottom:7px;transition:border-color .2s;}
.ecard:hover{border-color:var(--acc);}
.ecard-t{font-size:.84rem;font-weight:600;color:var(--tx);margin-bottom:2px;}
.ecard-d{font-size:.72rem;color:var(--mu);}
.ebtn{flex-shrink:0;padding:7px 16px;border:none;border-radius:6px;font-size:.77rem;font-weight:600;cursor:pointer;text-decoration:none;transition:opacity .2s;white-space:nowrap;}
.ebtn-li{background:linear-gradient(135deg,#0055a5,#0a66c2);color:#fff;}
.ebtn-gal{background:linear-gradient(135deg,#b03000,#e63e00);color:#fff;}
.ebtn-ct{background:linear-gradient(135deg,#cc4400,#ff6600);color:#fff;}
.ebtn:hover{opacity:.85;}

/* Aviso */
.aviso{background:rgba(245,158,11,.08);border:1px solid rgba(245,158,11,.25);border-radius:var(--r2);padding:.65rem 1rem;font-size:.79rem;color:#fbbf24;margin-bottom:1rem;}

/* Empty */
.empty-st{text-align:center;padding:3rem 1rem;color:var(--mu);}
.empty-st .eico{font-size:3rem;margin-bottom:.8rem;}

/* Download buttons */
div.stDownloadButton>button{background:var(--s2)!important;border:1px solid var(--bd)!important;color:var(--tx)!important;border-radius:var(--r2)!important;font-size:.8rem!important;}
div.stDownloadButton>button:hover{border-color:var(--acc)!important;}
</style>
""", unsafe_allow_html=True)

# ── Colores y metadatos de portales ───────────────────────────────────────────
PORTAL_COLORS = {
    "BuscoJobs":       "#6c63ff",
    "Computrabajo":    "#ff6600",
    "Gallito Trabajo": "#e63e00",
    "EmpleosUruguay":  "#4ade80",
    "Trabajo en Casa": "#a78bfa",
    "UruguayConcursa": "#ef4444",
    "LinkedIn":        "#0a66c2",
}
PORTAL_CSS = {
    "BuscoJobs":       "pstat ok",
    "Computrabajo":    "pstat ok",
    "Gallito Trabajo": "pstat ok",
    "EmpleosUruguay":  "pstat ok",
    "Trabajo en Casa": "pstat ok",
    "UruguayConcursa": "pstat ok",
    "LinkedIn":        "pstat lnk",
}

def render_table(df):
    """Tabla HTML limpia — sin etiquetas, sin emojis forzados."""
    mod_html = {
        "Remoto":     '<span class="mod-rem">Remoto</span>',
        "Híbrido":    '<span class="mod-hyb">Híbrido</span>',
        "Presencial": '<span class="mod-pre">Presencial</span>',
    }
    rows = ""
    for _, r in df.iterrows():
        titulo  = str(r.get("titulo",""))
        link    = str(r.get("link",""))
        empresa = str(r.get("empresa",""))
        zona    = str(r.get("zona",""))
        mod     = str(r.get("modalidad",""))
        area    = str(r.get("area",""))
        fecha   = str(r.get("fecha",""))
        fuente  = str(r.get("fuente",""))
        desc    = str(r.get("descripcion",""))

        titulo_s = titulo[:80]+"…" if len(titulo)>80 else titulo
        t_html   = f'<a href="{link}" target="_blank" rel="noopener" class="job-link">{titulo_s}</a>'
        if desc and desc.lower() not in ("","nan","none"):
            t_html += f'<div style="font-size:.72rem;color:var(--mu);margin-top:3px">{desc[:100]}</div>'

        co_html  = f'<div class="co-cell">{empresa[:45]}</div>' if empresa and empresa.lower() not in ("","nan","none") else '<span class="nd">—</span>'
        zo_html  = f'<span class="zo-pill">📍 {zona[:28]}</span>' if zona and zona.lower() not in ("","nan","none","uruguay") else "Uruguay"
        mo_html  = mod_html.get(mod, '<span class="nd">—</span>')
        ar_html  = area[:28] if area and area.lower() not in ("","nan","none") else ""

        color    = PORTAL_COLORS.get(fuente, "#6c63ff")
        fe_html  = f'<span class="date-cell">{fecha[:12]}</span>' if fecha and fecha.lower() not in ("","nan","none") else '<span class="nd">—</span>'
        src_html = f'<span class="portal-dot" style="background:{color}"></span>{fuente}'
        btn_html = f'<a href="{link}" target="_blank" rel="noopener" class="btn-ver">Ver →</a>' if link else ""

        rows += f"""<tr>
          <td>{t_html}</td>
          <td>{co_html}</td>
          <td>{zo_html}</td>
          <td>{mo_html}</td>
          <td style="font-size:.75rem;color:var(--mu)">{ar_html}</td>
          <td>{fe_html}</td>
          <td style="font-size:.77rem;white-space:nowrap">{src_html}</td>
          <td>{btn_html}</td>
        </tr>"""

    return f"""<div class="tbl-wrap"><table class="rtable">
      <thead><tr>
        <th>Puesto</th><th>Empresa</th><th>Ubicación</th>
        <th>Modalidad</th><th>Área</th><th>Publicado</th>
        <th>Portal</th><th></th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table></div>"""

def render_link_panel(links, btn_css, title):
    if not links: return
    cards = "".join(f"""<div class="ecard">
      <div><div class="ecard-t">{i['titulo']}</div><div class="ecard-d">{i.get('descripcion','')}</div></div>
      <a href="{i['link']}" target="_blank" rel="noopener" class="ebtn {btn_css}">Abrir →</a>
    </div>""" for i in links)
    st.markdown(f'<div class="ext-panel"><h4>{title}</h4>{cards}</div>', unsafe_allow_html=True)

SCRAPER_FN = {
    "buscojobs":     scrape_buscojobs,
    "computrabajo":  scrape_computrabajo,
    "gallito":       scrape_gallito,
    "empleosuruguay":scrape_empleosuruguay,
    "trabajoencasa": scrape_trabajoencasa,
    "vacantes":      scrape_vacantes,
}

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="padding:.5rem 0 .4rem"><span style="font-size:1.4rem">🇺🇾</span> <strong style="color:#a78bfa;font-size:1rem">BuscaEmpleo UY</strong></div>', unsafe_allow_html=True)

    st.markdown('<p class="sb-sec">📡 Portales</p>', unsafe_allow_html=True)
    selected_portals = {}
    groups = {}
    for name, cfg in PORTALS.items():
        groups.setdefault(cfg["group"], []).append(name)
    for grp, names in groups.items():
        st.markdown(f'<p class="portal-group">{grp}</p>', unsafe_allow_html=True)
        cols = st.columns(2)
        for i, pname in enumerate(names):
            default = pname in ("BuscoJobs","Computrabajo","Gallito Trabajo","LinkedIn")
            with cols[i % 2]:
                selected_portals[pname] = st.checkbox(pname, value=default, key=f"chk_{pname}")

    st.markdown('<p class="sb-sec">🗂 Categoría / Rubro</p>', unsafe_allow_html=True)
    cat_options = ["— Todas las categorías —"] + list(CATEGORIAS.keys())
    cat_sel = st.selectbox("Categoría", cat_options, index=0, label_visibility="collapsed")
    cat_cfg = CATEGORIAS.get(cat_sel) if cat_sel != "— Todas las categorías —" else None

    st.markdown('<p class="sb-sec">🔤 Palabra clave <em style="font-size:.65rem;font-weight:400">(opcional)</em></p>', unsafe_allow_html=True)
    keyword = st.text_input("Keyword", placeholder="Ej: React, senior, ANCAP…", label_visibility="collapsed")

    st.markdown('<p class="sb-sec">📍 Localidad</p>', unsafe_allow_html=True)
    localidad = st.selectbox("Localidad", ["Todo el país"] + LOCALIDADES, index=0, label_visibility="collapsed")

    st.markdown('<p class="sb-sec">🏢 Modalidad</p>', unsafe_allow_html=True)
    modalidad = st.selectbox("Modalidad", MODALIDADES, index=0, label_visibility="collapsed")

    st.markdown('<p class="sb-sec">📅 Antigüedad</p>', unsafe_allow_html=True)
    fecha_sel = st.selectbox("Fecha", FECHAS, index=0, label_visibility="collapsed")
    fecha_params = FECHA_PARAMS.get(fecha_sel, {}) if fecha_sel != "Cualquier fecha" else {}

    st.markdown('<p class="sb-sec">🎓 Experiencia</p>', unsafe_allow_html=True)
    experiencia = st.selectbox("Experiencia", EXPERIENCIAS, index=0, label_visibility="collapsed")

    st.markdown('<p class="sb-sec">🕐 Jornada</p>', unsafe_allow_html=True)
    jornada = st.selectbox("Jornada", JORNADAS, index=0, label_visibility="collapsed")

    st.markdown('<p class="sb-sec">⚖️ Sector</p>', unsafe_allow_html=True)
    sector = st.selectbox("Sector", SECTORES, index=0, label_visibility="collapsed")

    st.markdown('<p class="sb-sec">📄 Páginas por portal</p>', unsafe_allow_html=True)
    max_pages = st.slider("Páginas", 1, 8, 2, label_visibility="collapsed")

    st.markdown('<p class="sb-sec">↕️ Ordenar por</p>', unsafe_allow_html=True)
    sort_by  = st.selectbox("Ordenar", ["empresa","zona","modalidad","fuente","fecha"], label_visibility="collapsed")
    sort_asc = st.radio("Orden", ["↑ Asc","↓ Desc"], index=0, horizontal=True, label_visibility="collapsed") == "↑ Asc"

    st.markdown("<br>", unsafe_allow_html=True)
    search_btn = st.button("🚀  Buscar empleos", type="primary", use_container_width=True)

# ── HERO ─────────────────────────────────────────────────────────────────────
n_sel   = sum(1 for v in selected_portals.values() if v)
cat_lbl = cat_cfg["label"] if cat_cfg else "Todas las categorías"

st.markdown(f"""
<div class="hero">
  <div class="hero-live"><div class="hero-dot"></div> EN TIEMPO REAL</div>
  <h1>Busca<span>Empleo</span> Uruguay</h1>
  <div class="hero-sub">{n_sel} portales · {cat_lbl}</div>
</div>""", unsafe_allow_html=True)

# Chips de filtros activos
chips = []
if cat_cfg:                              chips.append(f"🗂 {cat_lbl}")
if keyword:                              chips.append(f"🔤 {keyword}")
if localidad != "Todo el país":          chips.append(f"📍 {localidad}")
if modalidad != "Todas":                 chips.append(f"🏢 {modalidad}")
if fecha_sel != "Cualquier fecha":       chips.append(f"📅 {fecha_sel}")
if experiencia != "Cualquier nivel":     chips.append(f"🎓 {experiencia}")
if jornada != "Cualquier jornada":       chips.append(f"🕐 {jornada}")
if sector != "Público y privado":        chips.append(f"⚖️ {sector}")
if chips:
    st.markdown(
        '<div class="chips-row">' +
        "".join(f'<span class="chip-f">{c}</span>' for c in chips) +
        "</div>", unsafe_allow_html=True
    )

# ── Estado sesión ─────────────────────────────────────────────────────────────
for key in ("results_df","li_links","gal_links","ct_links","portal_stats"):
    if key not in st.session_state:
        st.session_state[key] = None if key == "results_df" else []

# ── BÚSQUEDA ──────────────────────────────────────────────────────────────────
if search_btn:
    if not cat_cfg and not keyword.strip():
        st.warning("Seleccioná una categoría o escribí una palabra clave.")
        st.stop()
    active = [n for n, v in selected_portals.items() if v]
    if not active:
        st.warning("Seleccioná al menos un portal.")
        st.stop()

    if sector == "Solo privado":
        active = [p for p in active if p != "UruguayConcursa"]
    elif sector == "Solo público / Estado":
        active = [p for p in active if p in ("UruguayConcursa","Trabajo en Casa")]

    all_results, li_links, gal_links, ct_links, portal_stats = [], [], [], [], {}
    loc = localidad if localidad != "Todo el país" else ""
    prog = st.progress(0.0)
    stat = st.empty()
    done = 0; total = len(active)

    for pname in active:
        sk = PORTALS[pname]["scraper"]
        stat.markdown(f'<div style="color:var(--mu);font-size:.82rem">⏳ {pname}…</div>', unsafe_allow_html=True)

        if sk == "linkedin":
            li_links = build_linkedin_links(
                keyword=keyword or (cat_cfg["keyword"] if cat_cfg else ""),
                location=loc,
                modality=modalidad if modalidad != "Todas" else "",
                experience=experiencia if experiencia != "Cualquier nivel" else "",
                job_type=jornada if jornada != "Cualquier jornada" else "",
            )
            if fecha_params.get("linkedin_tpr"):
                for lk in li_links:
                    if "f_TPR" not in lk["link"]:
                        lk["link"] += f"&f_TPR={fecha_params['linkedin_tpr']}"
            portal_stats[pname] = ("lnk", len(li_links))

        elif sk in SCRAPER_FN:
            try:
                res = SCRAPER_FN[sk](
                    categoria_cfg=cat_cfg, location=loc, keyword=keyword,
                    max_pages=max_pages,
                    progress_callback=lambda m: stat.markdown(
                        f'<div style="color:var(--mu);font-size:.76rem">{m}</div>',
                        unsafe_allow_html=True),
                )

                # Gallito y Computrabajo: si 0 resultados → generar links de búsqueda
                if sk == "gallito" and not res:
                    gal_date = fecha_params.get("gallito", "")
                    gal_links = build_gallito_links(cat_cfg, loc, keyword)
                    if gal_date:
                        for gl in gal_links:
                            if "fecha-publicacion" not in gl["link"]:
                                gl["link"] += f"fecha-publicacion/{gal_date}/"
                    portal_stats[pname] = ("lnk", 0)

                elif sk == "computrabajo" and not res:
                    ct_links = build_computrabajo_links(cat_cfg, loc, keyword)
                    portal_stats[pname] = ("lnk", 0)

                else:
                    all_results.extend(res)
                    portal_stats[pname] = ("ok", len(res))

            except Exception as e:
                if sk == "gallito":
                    gal_links = build_gallito_links(cat_cfg, loc, keyword)
                    portal_stats[pname] = ("lnk", 0)
                elif sk == "computrabajo":
                    ct_links = build_computrabajo_links(cat_cfg, loc, keyword)
                    portal_stats[pname] = ("lnk", 0)
                else:
                    portal_stats[pname] = ("warn", 0)
                stat.markdown(f'<div style="color:#f87171;font-size:.76rem">⚠️ {pname}: {e}</div>', unsafe_allow_html=True)

        done += 1
        prog.progress(done / total)

    prog.empty(); stat.empty()
    st.session_state.update({
        "portal_stats": portal_stats,
        "li_links": li_links, "gal_links": gal_links, "ct_links": ct_links,
    })

    if all_results:
        df = pd.DataFrame(all_results).drop_duplicates(subset=["link"]).reset_index(drop=True)
        df["salario_num"] = pd.to_numeric(df.get("salario_num"), errors="coerce")
        for col in ("empresa","zona","modalidad","area","fecha","descripcion"):
            if col not in df.columns: df[col] = ""
        if modalidad != "Todas":
            df = df[df["modalidad"].str.contains(modalidad, case=False, na=False) | (df["modalidad"] == "")]
        st.session_state["results_df"] = df
    else:
        st.session_state["results_df"] = pd.DataFrame()

# ── RESULTADOS ────────────────────────────────────────────────────────────────
df_all        = st.session_state.get("results_df")
li_links      = st.session_state.get("li_links", [])
gal_links     = st.session_state.get("gal_links", [])
ct_links      = st.session_state.get("ct_links", [])
portal_stats  = st.session_state.get("portal_stats", {})

# Estado por portal
if portal_stats:
    stats_html = '<div class="pstats">'
    for pname, (stype, cnt) in portal_stats.items():
        color = PORTAL_COLORS.get(pname, "#6c63ff")
        dot   = f'<span style="display:inline-block;width:7px;height:7px;border-radius:50%;background:{color};margin-right:5px"></span>'
        if stype == "ok":
            stats_html += f'<span class="pstat ok">{dot}{pname} · {cnt}</span>'
        elif stype == "lnk":
            label = f"{cnt} links" if cnt else "links directos"
            stats_html += f'<span class="pstat lnk">{dot}{pname} · {label} ↗</span>'
        else:
            stats_html += f'<span class="pstat warn">{dot}{pname} · sin resultados</span>'
    stats_html += "</div>"
    st.markdown(stats_html, unsafe_allow_html=True)

# Paneles de links externos
if ct_links:
    render_link_panel(ct_links, "ebtn-ct", "Computrabajo — abrir búsqueda en el navegador")
if gal_links:
    render_link_panel(gal_links, "ebtn-gal", "Gallito Trabajo — abrir búsqueda en el navegador")
if li_links:
    render_link_panel(li_links, "ebtn-li", "LinkedIn Jobs — abrir en el navegador")

# Tabla de resultados scrapeados
if df_all is not None and not df_all.empty:
    portal_counts = df_all.groupby("fuente").size().to_dict()
    n_rem = (df_all["modalidad"] == "Remoto").sum()
    n_emp = df_all["empresa"].replace("", pd.NA).dropna().nunique()

    metrics_html = f"""<div class="metrics-row">
      <div class="metric"><div class="mv">{len(df_all)}</div><div class="ml">Resultados</div></div>
      <div class="metric"><div class="mv">{n_emp}</div><div class="ml">Empresas</div></div>
      <div class="metric"><div class="mv">{n_rem}</div><div class="ml">Remotos</div></div>"""
    for pn, cnt in sorted(portal_counts.items(), key=lambda x: -x[1]):
        metrics_html += f'<div class="metric"><div class="mv">{cnt}</div><div class="ml">{pn}</div></div>'
    metrics_html += "</div>"
    st.markdown(metrics_html, unsafe_allow_html=True)

    df_sorted = df_all.sort_values(sort_by, ascending=sort_asc, na_position="last")
    st.markdown(render_table(df_sorted), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, _ = st.columns([1,1,5])
    with c1:
        st.download_button("📥 CSV", df_sorted.to_csv(index=False).encode("utf-8-sig"),
                           "empleos_uy.csv", "text/csv")
    with c2:
        try:
            import io; buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as w:
                df_sorted.to_excel(w, index=False, sheet_name="Empleos")
            buf.seek(0)
            st.download_button("📊 Excel", buf, "empleos_uy.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        except ImportError: pass

elif df_all is not None and df_all.empty and not li_links and not gal_links and not ct_links:
    st.markdown("""<div class="empty-st">
      <div class="eico">🔍</div>
      <p>Sin resultados para los filtros seleccionados.<br>
      Probá con otra categoría, menos filtros o más páginas.</p>
    </div>""", unsafe_allow_html=True)

elif df_all is None:
    st.markdown("""<div class="empty-st">
      <div class="eico">🇺🇾</div>
      <p style="font-size:.95rem;font-weight:600;color:#e2e8f0;margin-bottom:.4rem">
        Seleccioná una categoría y tus filtros</p>
      <p>Resultados en tiempo real desde 7 portales de empleo en Uruguay</p>
    </div>""", unsafe_allow_html=True)
