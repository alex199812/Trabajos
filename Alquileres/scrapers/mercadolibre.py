# scrapers/mercadolibre.py — MercadoLibre Uruguay
# Flujo idéntico al diagnóstico confirmado:
#   1. GET home  → cookies iniciales
#   2. GET url   → recibe challenge + setea _bmstate en cookies
#   3. Leer _bmstate, resolver SHA256, setear _bmc
#   4. GET url   → HTML real con 200+ anuncios

import re
import hashlib
import time
import urllib.parse
import requests
from bs4 import BeautifulSoup
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

BASE   = "https://listado.mercadolibre.com.uy"
DOMAIN = "mercadolibre.com.uy"

def _build_prop_map(dept_slug):
    d = dept_slug.strip() if dept_slug else "montevideo"
    return {
        "":             f"{BASE}/inmuebles/apartamentos/alquiler/{d}/",
        "apartamentos": f"{BASE}/inmuebles/apartamentos/alquiler/{d}/",
        "casas":        f"{BASE}/inmuebles/casas/alquiler/{d}/",
        "ph":           f"{BASE}/inmuebles/ph/alquiler/{d}/",
        "locales":      f"{BASE}/inmuebles/locales-y-oficinas/alquiler/{d}/",
    }

ITEMS_PER_PAGE = 48

HEADERS = {
    "User-Agent":      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-UY,es;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Connection":      "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest":  "document",
    "Sec-Fetch-Mode":  "navigate",
    "Sec-Fetch-Site":  "none",
    "Cache-Control":   "no-cache",
}


def _is_challenge(html: str) -> bool:
    return "verifyChallenge" in html or ("_bmstate" in html and len(html) < 10_000)


def _solve_sha256(token: str, difficulty: int) -> int:
    """Encuentra N tal que SHA256(token+N) empiece con 'difficulty' ceros."""
    if difficulty == 0:
        return 0
    prefix = "0" * difficulty
    for n in range(10_000_000):
        if hashlib.sha256(f"{token}{n}".encode()).hexdigest().startswith(prefix):
            return n
    return 0


def _get_real_html(session: requests.Session, url: str, cb) -> str | None:
    """
    Obtiene el HTML real de una URL de ML resolviendo el challenge si aparece.
    Flujo exacto del diagnóstico: GET → challenge → solve → GET → HTML real.
    """
    session.headers.update({"Referer": "https://www.mercadolibre.com.uy/"})
    resp = session.get(url, timeout=25)
    html = resp.text

    # Sin challenge → devolver directo
    if not _is_challenge(html):
        return html

    # ── Paso 1: leer _bmstate de las cookies (ya fue seteada por ML) ──────────
    cb("MercadoLibre — resolviendo anti-bot SHA-256…")
    bmstate = None
    for c in session.cookies:
        if c.name == "_bmstate":
            bmstate = urllib.parse.unquote(c.value)
            break

    if not bmstate or ";" not in bmstate:
        cb("MercadoLibre — no se pudo leer _bmstate de cookies.")
        return None

    parts      = bmstate.split(";")
    token      = parts[0]
    difficulty = int(parts[1]) if len(parts) > 1 else 0

    # ── Paso 2: resolver el puzzle ────────────────────────────────────────────
    answer = _solve_sha256(token, difficulty)
    cb(f"MercadoLibre — challenge resuelto (dificultad={difficulty}, N={answer}).")

    # ── Paso 3: setear _bmc y hacer la segunda request ────────────────────────
    session.cookies.set(
        "_bmc",
        urllib.parse.quote(f"{token};{answer}"),
        domain=DOMAIN, path="/"
    )
    time.sleep(0.4)
    session.headers.update({"Referer": "https://www.mercadolibre.com.uy/"})

    resp2 = session.get(url, timeout=30)
    html2 = resp2.text

    if _is_challenge(html2):
        cb("MercadoLibre — reintentando tras challenge rechazado…")
        time.sleep(2)
        resp2 = session.get(url, timeout=30)
        html2 = resp2.text

    if _is_challenge(html2) or len(html2) < 10_000:
        cb("MercadoLibre — no se pudo superar el anti-bot.")
        return None

    cb(f"MercadoLibre — HTML real obtenido ({len(html2):,} chars).")
    return html2


def _page_url(base_url: str, page: int) -> str:
    if page <= 1:
        return base_url
    offset = (page - 1) * ITEMS_PER_PAGE + 1
    return base_url + f"_Desde_{offset}_NoIndex_True"


def _parse_price(text: str) -> tuple:
    if not text:
        return "Consultar", "", None
    t = text.strip()
    moneda = "USD" if any(k in t for k in ("U$S","USD","US$")) else ("UYU" if "$" in t else "")
    nums = re.findall(r"\d+", t.replace(".", "").replace(",", ""))
    return t, moneda, (int(nums[0]) if nums else None)


def _extract_listings(html: str) -> list:
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    seen = set()

    # ── Intento 1: selectores CSS del diseño Poly/Andes de ML ─────────────────
    items = (
        soup.select("li.ui-search-layout__item")
        or soup.select("div.poly-card")
        or soup.select("[class*='ui-search-result']")
    )

    for item in items:
        try:
            title_el = (
                item.select_one(".poly-component__title")
                or item.select_one(".ui-search-item__title")
                or item.select_one("h2") or item.select_one("h3")
            )
            title = title_el.get_text(strip=True) if title_el else ""

            link_el = item.select_one("a[href*='MLU']") or item.find("a", href=True)
            link = link_el.get("href","").split("?")[0].split("#")[0] if link_el else ""
            if not link or link in seen:
                continue
            seen.add(link)

            sym_el   = item.select_one(".andes-money-amount__currency-symbol,.price-tag-symbol")
            price_el = item.select_one(".andes-money-amount__fraction,.price-tag-amount")
            pt = (f"{sym_el.get_text(strip=True)} {price_el.get_text(strip=True)}"
                  if sym_el and price_el else (price_el.get_text(strip=True) if price_el else ""))
            price_display, moneda, price_num = _parse_price(pt)

            zone_el = item.select_one(".poly-component__location,.ui-search-item__location-label")
            zona = zone_el.get_text(strip=True) if zone_el else "Montevideo"

            dorm = banos = surf = None
            for el in item.find_all(True):
                t = el.get_text(strip=True).lower()
                if not (2 < len(t) < 50): continue
                nums = re.findall(r"\d+", t)
                if not nums: continue
                n = int(nums[0])
                if any(k in t for k in ("dorm","hab","ambi")) and dorm is None and n<=10: dorm=n
                elif any(k in t for k in ("baño","bano")) and banos is None and n<=10: banos=n
                elif ("m²" in t or "m2" in t) and surf is None and 5<n<2000: surf=n

            listings.append({
                "titulo": (title or "Propiedad en alquiler")[:120],
                "precio": price_display, "precio_num": float(price_num) if price_num else None,
                "moneda": moneda, "zona": zona[:100],
                "dormitorios": dorm, "banos": banos, "superficie_m2": surf,
                "gastos": "", "gastos_num": None, "link": link, "fuente": "MercadoLibre",
            })
        except Exception:
            continue

    if listings:
        return listings

    # ── Intento 2: buscar todos los links MLU- en el HTML ─────────────────────
    # Diagnóstico confirmó 200 links MLU en el HTML real de ML
    for a in soup.find_all("a", href=re.compile(r"MLU-\d+")):
        href = a.get("href","").split("?")[0].split("#")[0]
        if not href or href in seen or len(href) < 20:
            continue
        seen.add(href)

        title     = a.get_text(strip=True) or "Propiedad en alquiler"
        price_text = zona_text = ""
        container = a.parent

        for _ in range(8):
            if not container: break
            full = container.get_text(" ", strip=True)
            pm = re.search(r'(U\$S|USD|\$)\s*([\d.]{3,})', full)
            if pm and not price_text:
                price_text = pm.group(0)
            zm = re.search(
                r'\b(Pocitos|Carrasco|Cordón|Cordon|Centro|Palermo|Prado|Buceo|'
                r'Malvín|Malvin|Punta\s*Carretas|Ciudad\s*Vieja|Tres\s*Cruces|'
                r'Unión|Union|Aguada|Barrio\s*Sur|Reducto|Goes|Parque\s*Rod[oó]|'
                r'La\s*Blanqueada|Sayago|La\s*Teja|Colón|Colon|Jacinto\s*Vera|'
                r'Parque\s*Batlle|Lezica|Peñarol|Penarol|Malvin\s*Norte)\b',
                full, re.IGNORECASE)
            if zm and not zona_text:
                zona_text = zm.group(0)
            if price_text and zona_text: break
            container = container.parent

        price_display, moneda, price_num = _parse_price(price_text)
        listings.append({
            "titulo": title[:120], "precio": price_display,
            "precio_num": float(price_num) if price_num else None,
            "moneda": moneda, "zona": zona_text or "Montevideo",
            "dormitorios": None, "banos": None, "superficie_m2": None,
            "gastos": "", "gastos_num": None, "link": href, "fuente": "MercadoLibre",
        })
        if len(listings) >= 60:
            break

    return listings


def scrape_mercadolibre(prop_type="", max_pages=3, progress_callback=None, dept_slug="montevideo"):
    def cb(msg):
        if progress_callback:
            progress_callback(msg)

    session = requests.Session()
    session.headers.update(HEADERS)

    # Paso 1: visitar home para obtener cookies iniciales (igual que el diagnóstico)
    cb("MercadoLibre — iniciando sesión…")
    try:
        session.get("https://www.mercadolibre.com.uy/", timeout=15)
        time.sleep(0.8)
    except Exception:
        pass

    PROP_MAP     = _build_prop_map(dept_slug)
    base_url     = PROP_MAP.get(prop_type, PROP_MAP[""])
    all_listings = []

    for page in range(1, max_pages + 1):
        url = _page_url(base_url, page)
        cb(f"MercadoLibre — página {page} de {max_pages}…")

        # Paso 2+3+4: obtener HTML real (resolviendo challenge si aparece)
        html = _get_real_html(session, url, cb)

        if not html:
            cb("MercadoLibre — no se pudo obtener la página.")
            break

        # Paso 5: extraer los anuncios del HTML
        listings = _extract_listings(html)
        if not listings:
            cb(f"MercadoLibre — sin anuncios en página {page}. HTML size={len(html):,}")
            break

        all_listings.extend(listings)
        cb(f"MercadoLibre — {len(all_listings)} resultados acumulados.")

        if page < max_pages:
            time.sleep(2.5)

    return all_listings
