# scrapers/computrabajo.py — Computrabajo Uruguay — v5 (scraping restaurado)
#
# DIAGNÓSTICO DEL PROBLEMA:
# - En v4 se deshabilitó el scraping y sólo se generaban links a páginas de búsqueda.
# - El usuario veía links a /trabajo-de-X (búsqueda), no a /ofertas/SLUG (oferta individual).
# - Al abrir un link de búsqueda buscando "postularse", obviamente no funciona como link de postulación.
#
# SOLUCIÓN:
# - Restaurar scraping con cloudscraper (instalado por requirements.txt).
# - cloudscraper pasa el challenge de Cloudflare JS en el servidor local del usuario.
# - Los links extraídos (/ofertas/SLUG) funcionan perfectamente en cualquier navegador.
# - Fallback a links de búsqueda si cloudscraper también falla.
import re
import time
import unicodedata
from bs4 import BeautifulSoup
from .base import BaseJobScraper


def _slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-z0-9\s-]", "", text.lower().strip())
    return re.sub(r"[\s_-]+", "-", text).strip("-")


_LOC_SLUGS = {
    "Montevideo": "montevideo", "Canelones": "canelones",
    "Maldonado": "maldonado", "Colonia": "colonia",
    "Salto": "salto", "Paysandú": "paysandu",
    "Rivera": "rivera", "San José": "san-jose",
    "Rocha": "rocha", "Flores": "flores",
    "Florida": "florida", "Durazno": "durazno",
    "Tacuarembó": "tacuarembo", "Cerro Largo": "cerro-largo",
    "Artigas": "artigas", "Lavalleja": "lavalleja",
    "Río Negro": "rio-negro", "Soriano": "soriano",
    "Treinta y Tres": "treinta-y-tres",
}


class ComputrabajoScraper(BaseJobScraper):
    SOURCE_NAME = "Computrabajo"
    BASE_URL    = "https://www.computrabajo.com.uy"

    ITEM_SELECTORS = [
        "article.box_offer",
        "div.box_offer",
        "[data-qa='offer-list-item']",
        "article[class*='offer']",
        "div[class*='offerList'] > article",
        "div[class*='offerList'] > div",
        "li[class*='offer']",
        "div[class*='job-item']",
    ]
    COMPANY_SELECTORS = [
        "[class*='company']", "[class*='empresa']",
        "p.fs16", "span.fs16", "[class*='companyName']",
    ]
    LOCATION_SELECTORS = [
        "[class*='location']", "[class*='ubicacion']",
        "[class*='city']", "[class*='ciudad']", "[class*='place']",
    ]

    _DATE_PAT = re.compile(
        r"^(hace\s+\d|ayer|hoy|\d{1,2}/\d{1,2}|\d{1,2}\s+de\s+|\d{4})",
        re.IGNORECASE,
    )

    def build_url(self, categoria_cfg: dict, location: str, page: int, keyword: str = "") -> str:
        # Prioridad: keyword usuario > keyword categoría > slug categoría
        kw = keyword.strip() or (categoria_cfg or {}).get("keyword", "") or (categoria_cfg or {}).get("computrabajo", "")
        if not kw:
            loc_slug = _LOC_SLUGS.get(location, "")
            return f"{self.BASE_URL}/empleos-en-{loc_slug}" if loc_slug else f"{self.BASE_URL}/empleos-hoy"

        kw_slug  = _slugify(kw)
        loc_slug = _LOC_SLUGS.get(location, "")
        path     = f"trabajo-de-{kw_slug}"
        if loc_slug:
            path += f"-en-{loc_slug}"
        url = f"{self.BASE_URL}/{path}"
        return f"{url}?p={page}" if page > 1 else url

    def _extract_offer_link(self, card) -> str:
        """
        Extrae el link de la oferta individual con prioridad estricta.
        Todos los links de oferta de Computrabajo contienen /ofertas/ o /empleo/
        y NUNCA /empresas/ ni /candidatos/.
        """
        # 1. Link js-o-link (el principal de Computrabajo)
        a = card.select_one("a.js-o-link, a[class*='js-o-link']")
        if a and a.get("href"):
            href = a["href"]
            if "/empresas/" not in href and "/candidatos/" not in href:
                return self._abs(href)

        # 2. Cualquier link con /ofertas/ (sin /empresas/)
        for a in card.find_all("a", href=True):
            href = a["href"]
            if ("/ofertas/" in href or "/empleo/" in href) and "/empresas/" not in href:
                return self._abs(href)

        # 3. Link del heading (h2/h3) que sea del dominio correcto
        for tag in ["h2", "h3", "h4"]:
            h = card.find(tag)
            if h:
                a = h.find("a", href=True)
                if a and a.get("href"):
                    full = self._abs(a["href"])
                    if "computrabajo.com" in full and "/empresas/" not in full:
                        return full

        return ""

    def _extract_location(self, card) -> str:
        from .base import _UY_LOCATIONS
        for sel in self.LOCATION_SELECTORS:
            try:
                el = card.select_one(sel)
                if el:
                    txt = el.get_text(strip=True)
                    if txt and not self._DATE_PAT.match(txt):
                        return txt[:80]
            except Exception:
                pass
        # Buscar en spans con clase fs13 descartando fechas
        for el in card.select("span, p"):
            cls = " ".join(el.get("class", []))
            if "fs13" not in cls and "fs14" not in cls:
                continue
            txt = el.get_text(strip=True)
            if txt and not self._DATE_PAT.match(txt) and _UY_LOCATIONS.search(txt):
                return txt[:80]
        m = _UY_LOCATIONS.search(card.get_text(" ", strip=True))
        return m.group(0).strip() if m else "Uruguay"

    def parse_page(self, html: str) -> list:
        soup    = BeautifulSoup(html, "html.parser")
        results = []
        cards   = []
        for sel in self.ITEM_SELECTORS:
            try:
                cards = soup.select(sel)
                if len(cards) >= 2:
                    break
            except Exception:
                pass

        for card in cards:
            # Título
            title_el = (
                card.select_one("h2 a, h3 a, a.js-o-link, [class*='title'] a")
                or card.select_one("h2, h3, h4")
            )
            title = self._text(title_el)
            if not title or len(title) < 4:
                continue

            # Link — método estricto
            link = self._extract_offer_link(card)
            if not link:
                continue

            company  = self._text(self._first(card, self.COMPANY_SELECTORS))
            location = self._extract_location(card)

            job = self._build_job(card, link, title, company, location)
            if job:
                results.append(job)
        return results

    def scrape(self, categoria_cfg=None, location="", keyword="") -> list:
        all_jobs = []
        loc = location if location not in ("Todo el país", "") else ""

        for page in range(1, self.max_pages + 1):
            url = self.build_url(categoria_cfg or {}, loc, page, keyword)
            self._status(f"{self.SOURCE_NAME} — pág.{page}: {url}")

            # Siempre intentar con cloudscraper primero (pasa Cloudflare JS challenge)
            resp = self._get(url, use_cloud=True)
            # Fallback: requests normal
            if not resp or len(resp.text) < 2000:
                resp = self._get(url, use_cloud=False)
            if not resp or len(resp.text) < 1000:
                self._status(f"{self.SOURCE_NAME} — sin respuesta (Cloudflare bloqueó el acceso)")
                break

            jobs = self._parse_with_fallback(resp.text)
            if not jobs:
                self._status(f"{self.SOURCE_NAME} — sin resultados en pág.{page}")
                break

            all_jobs.extend(jobs)
            if page < self.max_pages:
                time.sleep(1.2)

        return all_jobs


def build_computrabajo_links(categoria_cfg=None, location="", keyword=""):
    """Links de búsqueda como fallback cuando el scraping falla."""
    cat      = categoria_cfg or {}
    kw       = keyword.strip() if keyword.strip() else cat.get("keyword", "")
    kw_slug  = _slugify(kw) if kw else ""
    loc_slug = _LOC_SLUGS.get(location, "")
    cat_slug = cat.get("computrabajo", "")
    label    = cat.get("label", kw or "Empleos")
    BASE     = "https://www.computrabajo.com.uy"
    links    = []

    if kw_slug:
        url = f"{BASE}/trabajo-de-{kw_slug}"
        if loc_slug:
            url += f"-en-{loc_slug}"
        links.append({
            "titulo":      f"Computrabajo — {label}",
            "link":        url,
            "descripcion": f"Ver ofertas de {label}{(' en ' + location) if location and location not in ('Todo el país','') else ' en Uruguay'}",
            "instruccion": "Cloudflare bloqueó el acceso automático — abrí en el navegador para ver las ofertas individuales",
        })

    if cat_slug and _slugify(cat_slug) != kw_slug:
        url2 = f"{BASE}/trabajo-de-{_slugify(cat_slug)}"
        if loc_slug:
            url2 += f"-en-{loc_slug}"
        links.append({
            "titulo":      f"Computrabajo — categoría {label}",
            "link":        url2,
            "descripcion": f"Explorar toda la categoría {label}",
            "instruccion": "Cloudflare bloqueó el acceso automático — abrí en el navegador",
        })

    if not links:
        url3 = f"{BASE}/empleos-en-{loc_slug}" if loc_slug else f"{BASE}/empleos-hoy"
        links.append({
            "titulo": "Computrabajo — Empleos Uruguay",
            "link":   url3,
            "descripcion": "Ver todas las ofertas en Computrabajo Uruguay",
            "instruccion": "Abrí en el navegador",
        })
    return links


def scrape_computrabajo(categoria_cfg=None, location="", keyword="",
                        max_pages=3, progress_callback=None):
    return ComputrabajoScraper(max_pages, progress_callback).scrape(
        categoria_cfg, location, keyword)
