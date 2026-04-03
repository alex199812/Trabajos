# scrapers/casasweb.py — Casasweb Uruguay
# Clases CSS confirmadas por diagnóstico:
#   item-grid col-md-6 col-lg-4 col-xl-3  → contenedor de cada anuncio
#   item-title                              → título
#   item-precio                             → precio
#   tipo-propiedad-zona                     → zona/barrio
#   Links: ALQUILER__INMOBILIARIA_TIPO_ZONA_MONTEVIDEO_CW######

import re
import time
import requests
from bs4 import BeautifulSoup
from typing import List, Optional
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

BASE_URL = "https://casasweb.com"

HEADERS = {
    "User-Agent":      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-UY,es;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Connection":      "keep-alive",
    "Referer":         "https://casasweb.com/",
}

# Parámetros URL de Casasweb
# n=A → Alquiler, z=13 → Montevideo, x=PAGE
# t=a → Apartamento, t=c → Casa, t=lc → Local comercial
TYPE_PARAM = {
    "":             "",
    "apartamentos": "a",
    "casas":        "c",
    "ph":           "a",
    "locales":      "lc",
}


def _parse_price(text):
    if not text:
        return "Consultar", "", None
    text = text.strip()
    moneda = "USD" if any(k in text for k in ("U$S","USD","US$")) else ("UYU" if "$" in text else "")
    nums = re.findall(r"\d+", text.replace(".", "").replace(",", ""))
    num = int(nums[0]) if nums else None
    return text, moneda, num


def _parse_page(html):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    seen = set()

    # Cada anuncio está en un div con clase "item-grid"
    items = soup.select("div.item-grid") or soup.select("[class*='item-grid']")

    for item in items:
        try:
            # Link — patrón confirmado: ALQUILER__..._CW######
            link_el = item.find("a", href=re.compile(r"CW\d+", re.IGNORECASE))
            if not link_el:
                link_el = item.find("a", href=True)
            href = link_el["href"] if link_el else ""
            if not href or href in seen:
                continue
            # Construir URL absoluta
            link = href if href.startswith("http") else BASE_URL + "/" + href.lstrip("/")
            seen.add(link)

            # Título — en h3 dentro de item-title
            title_el = item.select_one(".item-title h3") or item.select_one(".item-title") or item.select_one("h3")
            title = title_el.get_text(strip=True) if title_el else "Propiedad en alquiler"

            # Precio — en item-precio, o extraerlo del título si está ahí
            price_el = item.select_one(".item-precio")
            if price_el:
                price_text = price_el.get_text(strip=True)
            else:
                # El precio a veces viene en el título (confirmado: "$28.000 gastos comunes...")
                pm = re.search(r'(?:U\$S|USD|\$)\s*[\d.,]+', title)
                price_text = pm.group(0) if pm else ""

            price_display, moneda, price_num = _parse_price(price_text)

            # Zona — en tipo-propiedad-zona
            zone_el = item.select_one(".tipo-propiedad-zona") or item.select_one(".card-footer")
            zona = zone_el.get_text(strip=True) if zone_el else "Montevideo"
            zona = zona[:80]

            # Atributos — en item-det
            det_el = item.select_one(".item-det")
            det_text = det_el.get_text(" ", strip=True).lower() if det_el else ""

            dormitorios = banos = superficie = None
            for part in re.split(r'[·\|,]', det_text):
                part = part.strip()
                nums = re.findall(r"\d+", part)
                if not nums: continue
                n = int(nums[0])
                if any(k in part for k in ("dorm","hab","ambi")) and dormitorios is None and n <= 10:
                    dormitorios = n
                elif any(k in part for k in ("baño","bano")) and banos is None and n <= 10:
                    banos = n
                elif ("m²" in part or "m2" in part) and superficie is None and 5 < n < 2000:
                    superficie = n

            listings.append({
                "titulo":        title[:120],
                "precio":        price_display,
                "precio_num":    float(price_num) if price_num else None,
                "moneda":        moneda,
                "zona":          zona,
                "dormitorios":   dormitorios,
                "banos":         banos,
                "superficie_m2": superficie,
                "gastos":        "",
                "gastos_num":    None,
                "link":          link,
                "fuente":        "Casasweb",
            })
        except Exception:
            continue

    return listings


def scrape_casasweb(prop_type="", max_pages=3, progress_callback=None, dept_slug="13"):
    def cb(msg):
        if progress_callback:
            progress_callback(msg)

    session = requests.Session()
    session.headers.update(HEADERS)
    t_param = TYPE_PARAM.get(prop_type, "")
    all_listings = []

    for page in range(1, max_pages + 1):
        zone_id = dept_slug if dept_slug and dept_slug.isdigit() else "13"
        params = f"n=A&z={zone_id}&x={page}"
        if t_param:
            params += f"&t={t_param}"
        url = f"{BASE_URL}/resultados.aspx?{params}"
        cb(f"Casasweb — página {page} de {max_pages}...")

        try:
            resp = session.get(url, timeout=20)
            if resp.status_code != 200:
                cb(f"Casasweb — status {resp.status_code}")
                break
            listings = _parse_page(resp.text)
            if not listings:
                cb(f"Casasweb — sin resultados en página {page}.")
                break
            all_listings.extend(listings)
            cb(f"Casasweb — {len(all_listings)} resultados acumulados.")
            if page < max_pages:
                time.sleep(1.0)
        except Exception as e:
            cb(f"Casasweb — error: {e}")
            break

    return all_listings
