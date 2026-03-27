# scrapers/empleosuruguay.py — EmpleosEnUruguay (Blogger) — CORREGIDO v2
#
# FIX 1: build_url tenía una comilla `'` colgante al final de la URL con ?q=
#         que generaba URLs inválidas tipo /?q=keyword'
# FIX 2: Prioridad de búsqueda: keyword > label de categoría > página principal
# FIX 3: Búsqueda por label de Blogger usa /search/label/{label} —
#         mapeamos categoría a labels reales del blog
import re
from bs4 import BeautifulSoup
from .base import BaseJobScraper, _UY_LOCATIONS

_BLOGGER_POST = re.compile(r'/20\d\d/\d\d/[^"\'#?]+')
_EXCLUDE = re.compile(
    r"^(inicio|empleos|llamados|primer empleo|montevideo|maldonado|canelones|"
    r"urgente|más|siguiente|anterior|etiquetas|buscar|ver más|leer más|"
    r"empleos hoy|síguenos|comentar|compartir|\d+ comentarios)$",
    re.IGNORECASE,
)
MONTHS = ["", "ene", "feb", "mar", "abr", "may", "jun",
          "jul", "ago", "sep", "oct", "nov", "dic"]

# Labels reales del blog EmpleosEnUruguay
_LABELS = {
    "administracion":   "Administracion",
    "atencion cliente": "Atencion al Cliente",
    "ventas":           "Ventas",
    "contabilidad":     "Contabilidad",
    "tecnologia":       "Informatica",
    "logistica":        "Logistica",
    "marketing":        "Marketing",
    "salud":            "Salud",
    "educacion":        "Educacion",
    "gastronomia":      "Gastronomia",
    "seguridad":        "Seguridad",
    "ingenieria":       "Ingenieria",
    "recursos humanos": "Recursos Humanos",
    "diseño":           "Diseno",
    "construccion":     "Construccion",
}


class EmpleosUruguayScraper(BaseJobScraper):
    SOURCE_NAME = "EmpleosUruguay"
    BASE_URL    = "https://www.empleosenuruguay.com"

    def _get_label(self, kw: str) -> str:
        kw_lower = kw.lower()
        for key, label in _LABELS.items():
            if key in kw_lower or kw_lower in key:
                return label
        return ""

    def build_url(self, categoria_cfg, location, page, keyword=""):
        kw = keyword.strip() if keyword.strip() else (categoria_cfg or {}).get("keyword", "")

        # 1. Si hay keyword, intentar label primero (filtra mucho mejor que ?q=)
        if kw:
            label = self._get_label(kw)
            if label:
                return f"{self.BASE_URL}/search/label/{label.replace(' ', '%20')}"
            # Keyword sin label → usar búsqueda por texto
            # CORREGIDO: NO redirigir a label de ubicación, usar ?q= con el keyword
            return f"{self.BASE_URL}/search?q={kw.replace(' ', '+')}"

        # 2. Sin keyword: filtrar por ubicación si se especificó
        if location and location not in ("Todo el país", "Remoto / Teletrabajo", ""):
            loc = location.split("/")[0].strip()
            return f"{self.BASE_URL}/search/label/{loc}"

        # 3. Sin nada: página principal
        return f"{self.BASE_URL}/"

    def parse_page(self, html):
        soup = BeautifulSoup(html, "html.parser")
        results, seen = [], set()

        titles = (
            soup.select(".item-title a")
            or soup.select(".post-title a")
            or soup.select(".entry-title a")
            or soup.select("h3.post-title a")
            or soup.select("h2.entry-title a")
        )
        for a in titles:
            href  = a.get("href", "")
            title = a.get_text(strip=True)
            if not href or not title or len(title) < 5 or _EXCLUDE.match(title):
                continue
            link = href if href.startswith("http") else self._abs(href)
            if link in seen:
                continue
            seen.add(link)
            fm    = re.search(r'/(20\d\d)/(\d\d)/', href)
            fecha = f"{MONTHS[int(fm.group(2))]} {fm.group(1)}" if fm else ""
            lm    = _UY_LOCATIONS.search(title)
            tl    = title.lower()
            results.append({
                "titulo":      title[:120],
                "empresa":     "",
                "zona":        lm.group(0).strip() if lm else "Uruguay",
                "modalidad":   "Remoto" if any(k in tl for k in
                               ("remoto", "teletrabajo", "home office")) else "",
                "area":        "",
                "salario":     "", "salario_num": None, "moneda": "",
                "fecha":       fecha, "descripcion": "",
                "link":        link, "fuente":       self.SOURCE_NAME,
            })
        if results:
            return results

        # Fallback: links con patrón de post Blogger /YYYY/MM/
        for a in soup.find_all("a", href=True):
            href  = a["href"]
            title = a.get_text(strip=True)
            if (not _BLOGGER_POST.search(href) or not title
                    or len(title) < 8 or _EXCLUDE.match(title)):
                continue
            link = href if href.startswith("http") else self._abs(href)
            if link in seen:
                continue
            seen.add(link)
            fm    = re.search(r'/(20\d\d)/(\d\d)/', href)
            fecha = f"{MONTHS[int(fm.group(2))]} {fm.group(1)}" if fm else ""
            lm    = _UY_LOCATIONS.search(title)
            results.append({
                "titulo":      title[:120], "empresa":     "",
                "zona":        lm.group(0).strip() if lm else "Uruguay",
                "modalidad":   "", "area":        "",
                "salario":     "", "salario_num": None, "moneda": "",
                "fecha":       fecha, "descripcion": "",
                "link":        link, "fuente":       self.SOURCE_NAME,
            })
        return results

    def scrape(self, categoria_cfg=None, location="", keyword=""):
        import time
        all_jobs = []
        for page in range(1, min(self.max_pages, 2) + 1):
            url  = self.build_url(categoria_cfg, location, page, keyword)
            self._status(f"{self.SOURCE_NAME} — {url}")
            resp = self._get(url)
            if not resp:
                break
            jobs = self.parse_page(resp.text)
            if not jobs:
                break
            all_jobs.extend(jobs)
            time.sleep(0.5)
        return all_jobs


def scrape_empleosuruguay(categoria_cfg=None, location="", keyword="",
                          max_pages=2, progress_callback=None):
    return EmpleosUruguayScraper(min(max_pages, 2), progress_callback).scrape(
        categoria_cfg, location, keyword)
