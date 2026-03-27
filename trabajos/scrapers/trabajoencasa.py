# scrapers/trabajoencasa.py — Trabajo en Casa (Blogger) — CORREGIDO v2
#
# FIX 1: URL de búsqueda era /?buscar=keyword — Blogger NO usa ese parámetro.
#         La URL correcta es /search?q=keyword
# FIX 2: Intentar label de Blogger cuando la keyword mapea a uno conocido
import re
from bs4 import BeautifulSoup
from .base import BaseJobScraper, _UY_LOCATIONS

_BLOGGER_POST = re.compile(r'/20\d\d/\d\d/[^"\'#?]+')
_EXCLUDE = re.compile(
    r"^(inicio|empleos|llamados|siguenos|síguenos|compartir|leer más|ver más|"
    r"comentar|siguiente|anterior|buscar|etiquetas|\d+ comentarios|"
    r"trabaja con nosotros directorio|ad unit)$",
    re.IGNORECASE,
)
MONTHS = ["", "ene", "feb", "mar", "abr", "may", "jun",
          "jul", "ago", "sep", "oct", "nov", "dic"]

_SECTOR_PUBLICO_KW = ("ute", "ose", "ancap", "bps", "llamado", "concurso",
                      "brou", "anep", "caif", "msp", "inda", "mvotma")

# Labels reales del blog trabajoencasa.com.uy
_LABELS = {
    "teletrabajo":    "Teletrabajo",
    "remoto":         "Trabajo%20Remoto",
    "home office":    "Home%20Office",
    "informatica":    "Informatica",
    "diseño":         "Dise%C3%B1o",
    "marketing":      "Marketing",
    "redaccion":      "Redacci%C3%B3n",
    "traduccion":     "Traducci%C3%B3n",
    "contabilidad":   "Contabilidad",
    "ventas":         "Ventas",
    "atencion":       "Atenci%C3%B3n%20al%20Cliente",
}


class TrabajoCasaScraper(BaseJobScraper):
    SOURCE_NAME = "Trabajo en Casa"
    BASE_URL    = "https://www.trabajoencasa.com.uy"

    def build_url(self, categoria_cfg, location, page, keyword=""):
        kw = keyword.strip() if keyword.strip() else (categoria_cfg or {}).get("keyword", "")
        kw_lower = (kw or "").lower()

        # 1. Intentar label específico del portal si la keyword coincide
        for key, label in _LABELS.items():
            if key in kw_lower:
                return f"{self.BASE_URL}/search/label/{label}"

        # 2. Si hay keyword, incluir location en la query si está disponible
        if kw:
            q = kw
            # CORREGIDO: agregar ubicación a la búsqueda cuando esté disponible
            if location and location not in ("Todo el país", "Remoto / Teletrabajo", ""):
                q = f"{kw} {location}"
            return f"{self.BASE_URL}/search?q={q.replace(' ', '+')}"

        # 3. Solo ubicación: buscar por label de departamento
        if location and location not in ("Todo el país", "Remoto / Teletrabajo", ""):
            loc = location.split("/")[0].strip()
            return f"{self.BASE_URL}/search?q={loc.replace(' ', '+')}"

        return f"{self.BASE_URL}/"

    def parse_page(self, html):
        soup = BeautifulSoup(html, "html.parser")
        results, seen = [], set()

        titles = (
            soup.select(".post-title a")
            or soup.select("h3.post-title a")
            or soup.select(".entry-title a")
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
            tl    = title.lower()
            lm    = _UY_LOCATIONS.search(title)
            results.append({
                "titulo":      title[:120],
                "empresa":     "",
                "zona":        lm.group(0).strip() if lm else "Uruguay",
                "modalidad":   "Remoto" if any(k in tl for k in
                               ("remoto", "teletrabajo", "home office", "casa")) else "",
                "area":        "Sector público" if any(k in tl for k in _SECTOR_PUBLICO_KW) else "",
                "salario":     "", "salario_num": None, "moneda": "",
                "fecha":       fecha, "descripcion": "",
                "link":        link, "fuente":       self.SOURCE_NAME,
            })
        if results:
            return results

        # Fallback: links con patrón /YYYY/MM/
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
            tl    = title.lower()
            lm    = _UY_LOCATIONS.search(title)
            results.append({
                "titulo":      title[:120], "empresa":     "",
                "zona":        lm.group(0).strip() if lm else "Uruguay",
                "modalidad":   "Remoto" if "remoto" in tl or "teletrabajo" in tl else "",
                "area":        "Sector público" if any(k in tl for k in _SECTOR_PUBLICO_KW) else "",
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


def scrape_trabajoencasa(categoria_cfg=None, location="", keyword="",
                         max_pages=2, progress_callback=None):
    return TrabajoCasaScraper(min(max_pages, 2), progress_callback).scrape(
        categoria_cfg, location, keyword)
