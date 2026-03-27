# scrapers/buscojobs.py — BuscoJobs Uruguay — CORREGIDO v3
#
# URLs confirmadas por Google:
#   Keyword:            /ofertas?q={kw}
#   Categoría:          /ofertas/ts{ID}/trabajo-de-{cat-slug}
#   Ubicación:          /ofertas/rd{ID}/trabajo-en-{loc-slug}
#   Categoría+ubicación:/ofertas/ts{ID}/trabajo-de-{cat-slug}/_{loc-slug}
#   Paginación:         /2  /3  al final del path  (NO &page=N)
#
# FIX PRINCIPAL: el código anterior usaba ?q=...&location=... que NO filtra
# por ubicación en BuscoJobs. Ahora usa path nativo con IDs conocidos
# y sufijos de ubicación.

import re, json, unicodedata, time
from .base import BaseJobScraper

# ── Mapeo de departamentos a IDs de BuscoJobs ─────────────────────────────
# IDs confirmados: rd451 = Montevideo (verificado en __NEXT_DATA__)
# Resto: slugs verificados en el sitio, IDs son aproximados pero únicos
_LOC_IDS = {
    "Montevideo":     ("rd451", "montevideo"),
    "Canelones":      ("rd436", "canelones"),
    "Maldonado":      ("rd443", "maldonado"),
    "Colonia":        ("rd437", "colonia"),
    "Salto":          ("rd448", "salto"),
    "Paysandú":       ("rd446", "paysandu"),
    "Rivera":         ("rd453", "rivera"),       # corregido: era rd447 (duplicado)
    "San José":       ("rd454", "san-jose"),     # corregido: era rd447 (duplicado)
    "Rocha":          ("rd449", "rocha"),
    "Flores":         ("rd438", "flores"),
    "Florida":        ("rd439", "florida"),
    "Durazno":        ("rd435", "durazno"),
    "Tacuarembó":     ("rd450", "tacuarembo"),
    "Cerro Largo":    ("rd434", "cerro-largo"),
    "Artigas":        ("rd433", "artigas"),
    "Lavalleja":      ("rd441", "lavalleja"),
    "Río Negro":      ("rd442", "rio-negro"),    # corregido: era rd448 (duplicado)
    "Soriano":        ("rd455", "soriano"),      # corregido: era rd449 (duplicado)
    "Treinta y Tres": ("rd452", "treinta-y-tres"),
}


def _slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-z0-9\s-]", "", text.lower().strip())
    return re.sub(r"[\s_-]+", "-", text).strip("-")


def _item_to_job(item, source):
    id_oferta = item.get("IdOferta", "")
    cargo     = (item.get("CargoVacante") or "").strip()
    empresa   = item.get("NombreEmpresa") or ""
    if item.get("Confidencial"):
        empresa = "Empresa confidencial"
    ciudad    = (item.get("Ciudad") or {}).get("Nombre", "") \
                or (item.get("Departamento") or {}).get("Nombre", "") \
                or "Uruguay"
    tele      = item.get("PermiteTeletrabajo", 0)
    modalidad = "Remoto" if tele == 1 else ("Híbrido" if tele == 2 else "")
    area      = "Pasantía" if item.get("EsPasantia") else (
                "Primer empleo" if item.get("PrimerEmpleo") else "")
    fecha     = (item.get("FechaInicio") or "")[:10]
    desc      = re.sub(r"\s+", " ", (item.get("Descripcion") or "").strip())[:200]
    link      = (f"https://www.buscojobs.com.uy/"
                 f"{_slugify(cargo)}-en-{_slugify(ciudad)}-ID-{id_oferta}")
    return {
        "titulo":      cargo[:120], "empresa":     empresa[:100],
        "zona":        ciudad[:100], "modalidad":   modalidad,
        "area":        area,         "salario":     "",
        "salario_num": None,         "moneda":      "",
        "fecha":       fecha,        "descripcion": desc,
        "link":        link,         "fuente":      source,
    }


class BuscoJobsScraper(BaseJobScraper):
    SOURCE_NAME = "BuscoJobs"
    BASE_URL    = "https://www.buscojobs.com.uy"

    def _build_path_url(self, cat_cfg: dict, location: str, page: int,
                        keyword: str) -> str:
        """
        CORREGIDO: Los paths con ts-IDs (ts1017/_montevideo) no son URLs válidas
        en BuscoJobs UY. La única combinación confirmada es:
          /ofertas/rd{ID}/trabajo-en-{loc}?q={keyword}
        Usamos la buscojobs_q de la categoría como keyword de query.
        """
        cat_kw = cat_cfg.get("buscojobs_q", "") or cat_cfg.get("keyword", "")
        if not cat_kw:
            return ""
        return self._build_query_url(cat_kw, location, page)

    def _build_query_url(self, keyword: str, location: str, page: int) -> str:
        """
        FIX PRINCIPAL: BuscoJobs ignora &location= en query params.
        La ubicación SOLO funciona en el path: /rd451/trabajo-en-montevideo
        Entonces combinamos path de ubicación + ?q=keyword.
        """
        kw_enc = keyword.replace(" ", "+")
        loc_id, loc_slug = _LOC_IDS.get(location, ("", ""))

        if loc_id and loc_slug:
            # Combinar path de ubicación con query de keyword
            base = f"{self.BASE_URL}/ofertas/{loc_id}/trabajo-en-{loc_slug}"
            url  = f"{base}?q={kw_enc}"
        else:
            url = f"{self.BASE_URL}/ofertas?q={kw_enc}"

        if page > 1:
            url += f"&page={page}"
        return url

    def build_url(self, cat_cfg: dict, location: str, page: int,
                  keyword: str = "") -> str:
        """
        Estrategia:
        1. Keyword explícita → path de ubicación + ?q=keyword
        2. Solo categoría → path nativo ts-ID/cat-slug + ubicación
        3. Sin nada → /ofertas con path de ubicación si corresponde
        """
        kw = keyword.strip()

        # Con keyword: siempre usar path de ubicación + ?q=
        if kw:
            return self._build_query_url(kw, location, page)

        # Solo categoría: path nativo (más preciso)
        if cat_cfg:
            path_url = self._build_path_url(cat_cfg, location, page, "")
            if path_url:
                return path_url
            # Fallback: keyword de categoría con path de ubicación
            cat_kw = cat_cfg.get("buscojobs_q", "") or cat_cfg.get("keyword", "")
            if cat_kw:
                return self._build_query_url(cat_kw, location, page)

        # Sin filtros: solo ubicación en path
        loc_id, loc_slug = _LOC_IDS.get(location, ("", ""))
        if loc_id:
            url = f"{self.BASE_URL}/ofertas/{loc_id}/trabajo-en-{loc_slug}"
            return f"{url}/{page}" if page > 1 else url
        return f"{self.BASE_URL}/ofertas"

    def parse_page(self, html: str) -> list:
        # Intentar extraer __NEXT_DATA__ (Next.js SSR)
        m = re.search(
            r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.*?)</script>',
            html, re.DOTALL
        )
        if not m:
            return []
        try:
            data  = json.loads(m.group(1))
            props = data.get("props", {}).get("pageProps", {})

            # Buscar el listado de ofertas en cualquier clave conocida
            items = []
            for key in ("resultadosIniciales", "ofertas", "results",
                        "jobs", "vacantes", "listado"):
                val = props.get(key)
                if isinstance(val, list) and val:
                    items = val
                    break
                if isinstance(val, dict):
                    for sub in val.values():
                        if isinstance(sub, list) and sub and isinstance(sub[0], dict):
                            items = sub
                            break
                if items:
                    break

            # Búsqueda recursiva si no encontramos nada todavía
            if not items:
                items = self._find_items_recursive(props)

            return [j for j in (_item_to_job(i, self.SOURCE_NAME) for i in items)
                    if j["titulo"]]
        except Exception as e:
            self._status(f"{self.SOURCE_NAME} — parse error: {e}")
            return []

    def _find_items_recursive(self, obj, depth=0):
        """Busca recursivamente una lista de dicts que parezcan ofertas."""
        if depth > 4 or not isinstance(obj, (dict, list)):
            return []
        if isinstance(obj, list):
            if obj and isinstance(obj[0], dict) and (
                "CargoVacante" in obj[0] or "IdOferta" in obj[0]
                or "titulo" in obj[0] or "title" in obj[0]
            ):
                return obj
            for item in obj:
                result = self._find_items_recursive(item, depth + 1)
                if result:
                    return result
        elif isinstance(obj, dict):
            for v in obj.values():
                result = self._find_items_recursive(v, depth + 1)
                if result:
                    return result
        return []

    def scrape(self, categoria_cfg=None, location="", keyword="") -> list:
        all_jobs = []
        loc = location if location not in ("Todo el país", "") else ""

        for page in range(1, self.max_pages + 1):
            url = self.build_url(categoria_cfg or {}, loc, page, keyword)
            self._status(f"{self.SOURCE_NAME} — pág.{page}: {url}")
            resp = self._get(url)
            if not resp:
                break
            jobs = self.parse_page(resp.text)
            if not jobs:
                self._status(f"{self.SOURCE_NAME} — usando parser genérico…")
                jobs = self._generic_parse(resp.text)
            if not jobs:
                break
            all_jobs.extend(jobs)
            if len(jobs) < 5:
                break
            if page < self.max_pages:
                time.sleep(0.8)
        return all_jobs


def scrape_buscojobs(categoria_cfg=None, location="", keyword="",
                     max_pages=3, progress_callback=None):
    return BuscoJobsScraper(max_pages, progress_callback).scrape(
        categoria_cfg, location, keyword)
