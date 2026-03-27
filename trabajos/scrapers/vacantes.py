# scrapers/vacantes.py — UruguayConcursa — CORREGIDO v3
# FIX: GET de init primero para establecer sesión + POST más robusto
import re
import warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from bs4 import BeautifulSoup
from .base import BaseJobScraper

_BASE      = "https://www.uruguayconcursa.gub.uy"
_INIT_URL  = f"{_BASE}/Portal/servlet/com.si.recsel.inicio"
_SEARCH_URL = f"{_BASE}/Portal/servlet/com.si.recsel.dspllamados62"

_DEP_MAP = {
    "Montevideo":      "MO", "Canelones":   "CA", "Maldonado":  "MA",
    "Colonia":         "CO", "Salto":        "SA", "Paysandú":   "PA",
    "Rivera":          "RI", "San José":     "SJ", "Flores":     "FS",
    "Rocha":           "RO", "Tacuarembó":  "TA", "Cerro Largo": "CL",
    "Artigas":         "AR", "Durazno":      "DU", "Florida":    "FL",
    "Lavalleja":       "LA", "Río Negro":   "RN", "Soriano":    "SO",
    "Treinta y Tres":  "TT",
}

# Valores posibles de estado que acepta el formulario
_ESTADOS = ["", "Abierto", "En Curso"]


class UruguayConcursaScraper(BaseJobScraper):
    SOURCE_NAME = "UruguayConcursa"
    BASE_URL    = _BASE

    def build_url(self, *args, **kwargs):
        return _SEARCH_URL

    def _init_session(self):
        """
        FIX CLAVE: Hacer GET a la página de inicio primero para
        establecer cookies de sesión antes del POST.
        """
        sess = self._plain_session()
        try:
            sess.get(_INIT_URL, timeout=20, verify=False)
        except Exception:
            pass  # Continuar aunque falle, la sesión puede funcionar igual

    def _resolve_dep(self, location: str) -> str:
        if not location or location in ("Todo el país", "Remoto / Teletrabajo", ""):
            return ""
        for dep, code in _DEP_MAP.items():
            if location.lower() in dep.lower() or dep.lower() in location.lower():
                return code
        return ""

    def _do_post(self, keyword: str, dep_id: str, estado: str) -> str | None:
        """Realiza el POST y retorna el HTML si tiene contenido."""
        sess = self._plain_session()
        payload = {
            "vFTEXTO":     keyword,
            "vFLLANUM":    "",
            "vFDEPID":     dep_id,
            "vFLOCID":     "",
            "vFORGID":     "",
            "vFLLAESTWEB": estado,
            "vFTIPTARID":  "",
            "vAFRO":       "",
            "vFPAGINA":    "1",
        }
        try:
            r = sess.post(_SEARCH_URL, data=payload, timeout=30, verify=False)
            if r.status_code == 200 and len(r.text) > 1000:
                return r.text
        except Exception as e:
            self._status(f"{self.SOURCE_NAME} — POST error: {e}")
        return None

    def _parse_table(self, html: str) -> list:
        soup = BeautifulSoup(html, "html.parser")
        jobs = []
        seen = set()

        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            # Acepta tanto "verllamado" como "verLlamado" (case-insensitive)
            if "verllamado" not in href.lower():
                continue

            # Construir link absoluto
            if href.startswith("http"):
                link = href
            elif href.startswith("/"):
                link = _BASE + href
            else:
                # Puede ser relativo al servlet: "com.si.recsel.verllamado?ID"
                link = f"{_BASE}/Portal/servlet/{href}"

            if link in seen:
                continue
            seen.add(link)

            # Título desde el texto del link o celda de la fila
            title = a.get_text(strip=True)
            empresa, zona, fecha = "", "Uruguay", ""

            row = a.find_parent("tr")
            if row:
                cells = [td.get_text(" ", strip=True) for td in row.find_all("td")]
                # Estructura típica: [Nº, Título, Organismo, Departamento, Fecha, Estado]
                if len(cells) >= 2 and (not title or len(title) < 4):
                    title = cells[1]
                if len(cells) >= 3:
                    empresa = cells[2][:80]
                if len(cells) >= 4:
                    zona = cells[3][:60] or "Uruguay"
                # Buscar fecha en cualquier celda (formato dd/mm/yyyy)
                dm = re.search(r'\d{1,2}/\d{1,2}/\d{4}', row.get_text())
                if dm:
                    fecha = dm.group(0)

            if not title or len(title) < 4:
                continue

            jobs.append({
                "titulo":      title[:120],
                "empresa":     empresa or "Organismo estatal",
                "zona":        zona,
                "modalidad":   "",
                "area":        "Sector público",
                "salario":     "",
                "salario_num": None,
                "moneda":      "",
                "fecha":       fecha,
                "descripcion": "",
                "link":        link,
                "fuente":      self.SOURCE_NAME,
            })

        # Fallback: si no hay filas de tabla, buscar cualquier link verllamado
        if not jobs:
            for a in soup.find_all("a", href=True):
                href = a["href"].strip()
                if "verllamado" not in href.lower():
                    continue
                link = (href if href.startswith("http")
                        else (_BASE + href if href.startswith("/")
                              else f"{_BASE}/Portal/servlet/{href}"))
                if link in seen:
                    continue
                seen.add(link)
                title = a.get_text(strip=True)
                if not title or len(title) < 4:
                    continue
                jobs.append({
                    "titulo": title[:120], "empresa": "Organismo estatal",
                    "zona": "Uruguay", "modalidad": "", "area": "Sector público",
                    "salario": "", "salario_num": None, "moneda": "",
                    "fecha": "", "descripcion": "", "link": link,
                    "fuente": self.SOURCE_NAME,
                })

        return jobs

    def scrape(self, categoria_cfg=None, location="", keyword="") -> list:
        # CORREGIDO: Prioridad de keyword:
        # 1. Keyword explícito del usuario (el más específico)
        # 2. Sin keyword → POST vacío (devuelve todos los llamados abiertos)
        # El keyword de la categoría privada (ej: "desarrollador", "enfermero")
        # puede no matchear términos del sector público, así que si el usuario
        # no escribió nada, preferimos traer todos y filtrar post-búsqueda.
        kw     = keyword.strip()   # solo usar keyword del usuario
        dep_id = self._resolve_dep(location)

        self._status(f"{self.SOURCE_NAME} — iniciando sesión…")
        self._init_session()

        for estado in _ESTADOS:
            label = f"estado='{estado}'" if estado else "todos los estados"
            self._status(f"{self.SOURCE_NAME} — buscando '{kw or '(todos)'}' ({label})…")

            html = self._do_post(kw, dep_id, estado)
            if not html:
                continue

            jobs = self._parse_table(html)
            if jobs:
                self._status(f"{self.SOURCE_NAME} — {len(jobs)} resultados.")
                return jobs

            if "verllamado" not in html.lower() and "sin resultado" not in html.lower():
                self._status(f"{self.SOURCE_NAME} — respuesta sin llamados (estado={estado!r})")

        self._status(f"{self.SOURCE_NAME} — sin resultados.")
        return []


def scrape_vacantes(categoria_cfg=None, location="", keyword="", max_pages=2, progress_callback=None):
    return UruguayConcursaScraper(max_pages, progress_callback).scrape(categoria_cfg, location, keyword)
