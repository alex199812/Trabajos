# scrapers/gallito.py — Gallito Uruguay
# Usa cloudscraper para pasar el challenge de Cloudflare (confirmado: status 200, 239KB)
# El link de ejemplo confirma el patrón: /slug-inmuebles-NNNNNNN

import re
import time
from bs4 import BeautifulSoup
from typing import List
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

BASE_URL = "https://www.gallito.com.uy"

# URLs confirmadas
PROP_MAP = {
    "":             "/inmuebles/alquiler/montevideo",
    "apartamentos": "/inmuebles/apartamentos/alquiler/montevideo",
    "casas":        "/inmuebles/casas/alquiler/montevideo",
    "ph":           "/inmuebles/ph/alquiler/montevideo",
    "locales":      "/inmuebles/locales/alquiler/montevideo",
}


def _get_scraper():
    """Crea un cloudscraper configurado para pasar Cloudflare."""
    import cloudscraper
    return cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "windows", "desktop": True}
    )


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

    # Gallito: anuncios en article o li con id numérico, o links con patrón -inmuebles-NNNNN
    # Buscar todos los links que terminan en -inmuebles-NNNNNN
    anuncio_links = soup.find_all("a", href=re.compile(r"-inmuebles-\d+", re.IGNORECASE))

    # Si no encontró por ese patrón, intentar contenedores artículo
    if not anuncio_links:
        items = (
            soup.select("article.item")
            or soup.select("li.item")
            or soup.select("[class*='item'][id]")
            or soup.select("article")
        )
        for item in items:
            a = item.find("a", href=True)
            if a:
                anuncio_links.append(a)

    for a_tag in anuncio_links:
        try:
            href = a_tag.get("href", "")
            link = href if href.startswith("http") else BASE_URL + href
            link = link.split("?")[0]
            if not link or link in seen or len(link) < 20:
                continue
            seen.add(link)

            # Título desde el texto del link o heading cercano
            title = a_tag.get_text(strip=True)
            if not title or len(title) < 5:
                container = a_tag.parent
                for _ in range(3):
                    if not container: break
                    h = container.find(["h2","h3","h4"])
                    if h:
                        title = h.get_text(strip=True)
                        break
                    container = container.parent

            # Precio — buscar en el contenedor padre
            price_text = zona_text = ""
            container = a_tag.parent
            for _ in range(6):
                if not container: break
                full = container.get_text(" ", strip=True)

                pm = re.search(r'(?:U\$S|USD|\$)\s*[\d.,]+', full)
                if pm and not price_text:
                    price_text = pm.group(0)

                zm = re.search(
                    r'\b(Pocitos|Carrasco|Cordón|Cordon|Centro|Palermo|Prado|Buceo|'
                    r'Malvín|Malvin|Punta\s*Carretas|Ciudad\s*Vieja|Tres\s*Cruces|'
                    r'Unión|Union|Aguada|Barrio\s*Sur|Reducto|Goes|'
                    r'La\s*Blanqueada|Parque\s*Rod[oó]|Sayago|La\s*Teja|'
                    r'Colón|Colon|Jacinto\s*Vera|Parque\s*Batlle|Lezica|'
                    r'Peñarol|Penarol|Malvin\s*Norte|Buceo|Belvedere)\b',
                    full, re.IGNORECASE
                )
                if zm and not zona_text:
                    zona_text = zm.group(0)

                if price_text and zona_text: break
                container = container.parent

            price_display, moneda, price_num = _parse_price(price_text)

            listings.append({
                "titulo":        (title or "Propiedad en alquiler")[:120],
                "precio":        price_display,
                "precio_num":    float(price_num) if price_num else None,
                "moneda":        moneda,
                "zona":          zona_text or "Montevideo",
                "dormitorios":   None,
                "banos":         None,
                "superficie_m2": None,
                "gastos":        "",
                "gastos_num":    None,
                "link":          link,
                "fuente":        "Gallito",
            })
            if len(listings) >= 80:
                break
        except Exception:
            continue

    return listings


def scrape_gallito(prop_type="", max_pages=3, progress_callback=None, dept_slug="montevideo"):
    def cb(msg):
        if progress_callback:
            progress_callback(msg)

    # Verificar que cloudscraper esté instalado
    try:
        import cloudscraper
    except ImportError:
        cb("Gallito — instalando cloudscraper...")
        import subprocess, sys as _sys
        subprocess.check_call([_sys.executable, "-m", "pip", "install", "cloudscraper"], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        import cloudscraper

    scraper = _get_scraper()
    dept = dept_slug or "montevideo"
    PROP_MAP_D = {k: v.replace("/montevideo", f"/{dept}") for k, v in PROP_MAP.items()}
    path = PROP_MAP_D.get(prop_type, PROP_MAP_D[""])
    all_listings = []

    for page in range(1, max_pages + 1):
        url = BASE_URL + path
        if page > 1:
            url += f"?pagina={page}"
        cb(f"Gallito — página {page} de {max_pages}...")

        try:
            resp = scraper.get(url, timeout=30)
            if resp.status_code != 200:
                cb(f"Gallito — status {resp.status_code}")
                break

            listings = _parse_page(resp.text)
            if not listings:
                cb(f"Gallito — sin resultados en página {page}.")
                break

            all_listings.extend(listings)
            cb(f"Gallito — {len(all_listings)} resultados acumulados.")
            if page < max_pages:
                time.sleep(1.5)

        except Exception as e:
            cb(f"Gallito — error: {e}")
            break

    return all_listings
