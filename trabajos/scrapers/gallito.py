# scrapers/gallito.py — Gallito Trabajo — CORREGIDO v2
#
# URL confirmada: /buscar/q/{keyword}/
# Con área:       /buscar/q/{keyword}/areas/{area}/
# Con depto:      /buscar/q/{keyword}/departamento/{dep}/
# Con ambos:      /buscar/q/{keyword}/areas/{area}/departamento/{dep}/
# Paginación:     ?pagina=N   al final
#
# FIX: La keyword de la categoría se usaba correctamente, pero:
#   1. Cuando se combina area + departamento el orden importa: primero areas/, luego departamento/
#   2. La keyword vacía o "trabajo" devuelve todo — mejorar fallback
#   3. Mejorar parser para más patrones de href
import re, time, unicodedata, warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from bs4 import BeautifulSoup
from .base import BaseJobScraper, _UY_LOCATIONS

_BASE = "https://trabajo.gallito.com.uy"

# Mapeo de departamento a slug de Gallito
_DEP_SLUGS = {
    "Montevideo":     "montevideo",
    "Canelones":      "canelones",
    "Maldonado":      "maldonado",
    "Colonia":        "colonia",
    "Salto":          "salto",
    "Paysandú":       "paysandu",
    "Rivera":         "rivera",
    "San José":       "san-jose",
    "Rocha":          "rocha",
    "Flores":         "flores",
    "Florida":        "florida",
    "Durazno":        "durazno",
    "Tacuarembó":     "tacuarembo",
    "Cerro Largo":    "cerro-largo",
    "Artigas":        "artigas",
    "Lavalleja":      "lavalleja",
    "Río Negro":      "rio-negro",
    "Soriano":        "soriano",
    "Treinta y Tres": "treinta-y-tres",
}


def _slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-z0-9\s-]", "", text.lower().strip())
    return re.sub(r"[\s_-]+", "-", text).strip("-")


class GallitoTrabajoScraper(BaseJobScraper):
    SOURCE_NAME = "Gallito Trabajo"
    BASE_URL    = _BASE

    def _get(self, url, timeout=25, use_cloud=False):
        sess = self._cloud_session() if use_cloud else self._plain_session()
        try:
            r = sess.get(url, timeout=timeout, verify=False)
            return r if r.status_code == 200 else None
        except Exception as e:
            self._status(f"{self.SOURCE_NAME} — {e}")
            return None

    def _build_url(self, cat_cfg: dict, location: str, page: int,
                   keyword: str) -> str:
        """
        URL correcta: /buscar/q/{kw}/[areas/{area}/][departamento/{dep}/][?pagina=N]

        CORREGIDO: El filtro de área de la categoría SOLO se aplica cuando el usuario
        no escribió un keyword propio. Si el usuario escribe "React", se busca "react"
        sin filtro de área (para no restringir en exceso).
        Si el usuario no escribió nada, se usa keyword+área de la categoría.
        """
        user_kw = keyword.strip()  # keyword que escribió el usuario

        # Keyword de búsqueda: prioridad al usuario
        if user_kw:
            kw_slug = _slugify(user_kw)
            area_slug = ""  # sin filtro de área cuando hay keyword del usuario
        else:
            # Sin keyword del usuario: usar keyword+área de la categoría
            cat_kw = (cat_cfg or {}).get("keyword", "") or (cat_cfg or {}).get("buscojobs_q", "") or "trabajo"
            kw_slug   = _slugify(cat_kw)
            area_slug = (cat_cfg or {}).get("gallito_area", "")

        url = f"{_BASE}/buscar/q/{kw_slug}/"
        if area_slug:
            url += f"areas/{area_slug}/"

        dep_slug = _DEP_SLUGS.get(location, "")
        if dep_slug:
            url += f"departamento/{dep_slug}/"

        if page > 1:
            url += f"?pagina={page}"

        return url

    def parse_page(self, html: str) -> list:
        soup  = BeautifulSoup(html, "html.parser")
        jobs  = []
        seen  = set()

        # FIX: identificar el contenedor principal de resultados
        # para no levantar avisos del sidebar o sección de recomendados.
        # Gallito usa un div principal con clase que contiene "results" o "list"
        main = (
            soup.select_one("[class*='results']")
            or soup.select_one("[class*='listado']")
            or soup.select_one("[class*='avisos']")
            or soup.select_one("main")
            or soup.select_one("#content")
            or soup  # fallback: todo el HTML
        )

        for a in main.find_all("a", href=True):
            href = a["href"]
            if not any(k in href for k in ("/anuncio/", "/empleo/", "/aviso/")):
                continue

            # FIX: descartar links que estén dentro de secciones de sidebar,
            # recomendados, destacados o publicidad
            parent_classes = " ".join(
                " ".join(p.get("class", []))
                for p in a.parents
                if hasattr(p, "get")
            ).lower()
            if any(k in parent_classes for k in
                   ("sidebar", "recomend", "destac", "sponsor",
                    "publicidad", "widget", "aside", "related")):
                continue

            link = href if href.startswith("http") else _BASE + href
            if link in seen:
                continue
            seen.add(link)

            # Subir hasta contenedor con suficiente texto
            container = a
            for _ in range(7):
                if container is None:
                    break
                if len(container.get_text(strip=True)) > 30:
                    break
                container = container.parent

            # Título
            title = ""
            for tag in ["h2", "h3", "h4", "h5"]:
                h = container.find(tag) if container else None
                if h:
                    title = h.get_text(strip=True)
                    break
            if not title:
                title = a.get_text(strip=True)
            if not title or len(title) < 4:
                continue

            co  = self._text(self._first(container, self.COMPANY_SELECTORS)) if container else ""
            loc = self._text(self._first(container, self.LOCATION_SELECTORS)) if container else ""

            if not loc or re.match(r"^(hace\s+\d|ayer|hoy|\d{1,2}/)", loc, re.I):
                loc = ""
            if not loc and container:
                m = _UY_LOCATIONS.search(container.get_text(" ", strip=True))
                loc = m.group(0).strip() if m else "Uruguay"

            attrs = self._extract_attrs(container)
            jobs.append({
                "titulo":      title[:120], "empresa":     co[:100],
                "zona":        loc[:100],   "modalidad":   attrs["modalidad"],
                "area":        "",          "salario":     attrs["salario"],
                "salario_num": attrs["salario_num"],
                "moneda":      attrs["moneda"],
                "fecha":       attrs["fecha"],
                "descripcion": "",
                "link":        link,
                "fuente":      self.SOURCE_NAME,
            })
        return jobs

    def scrape(self, categoria_cfg=None, location="", keyword="") -> list:
        all_jobs = []
        loc = location if location not in ("Todo el país", "Remoto / Teletrabajo", "") else ""

        for page in range(1, self.max_pages + 1):
            url = self._build_url(categoria_cfg or {}, loc, page, keyword)
            self._status(f"{self.SOURCE_NAME} — pág.{page}: {url}")
            resp = self._get(url)
            if not resp or len(resp.text) < 3000:
                self._status(f"{self.SOURCE_NAME} — sin respuesta o muy corto")
                break
            jobs = self.parse_page(resp.text)
            if not jobs:
                self._status(f"{self.SOURCE_NAME} — sin avisos (carga dinámica probable)")
                break
            all_jobs.extend(jobs)
            if page < self.max_pages:
                time.sleep(0.8)
        return all_jobs


def scrape_gallito(categoria_cfg=None, location="", keyword="",
                   max_pages=3, progress_callback=None):
    return GallitoTrabajoScraper(max_pages, progress_callback).scrape(
        categoria_cfg, location, keyword)


def build_gallito_links(categoria_cfg=None, location="", keyword=""):
    kw   = keyword.strip() if keyword.strip() else (categoria_cfg or {}).get("keyword", "trabajo")
    slug = _slugify(kw)
    area = (categoria_cfg or {}).get("gallito_area", "")
    url  = f"{_BASE}/buscar/q/{slug}/"
    if area:
        url += f"areas/{area}/"
    dep  = _DEP_SLUGS.get(location, "")
    if dep:
        url += f"departamento/{dep}/"
    label = (categoria_cfg or {}).get("label", kw)
    return [{
        "titulo":      f"Gallito — {label}",
        "link":        url,
        "descripcion": f"Ver empleos de {label} en Gallito Trabajo",
        "instruccion": "Abrí en el navegador para ver los resultados actualizados",
    }]
