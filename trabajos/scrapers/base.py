# scrapers/base.py — Clase base para scrapers de empleo (v2 — parser agresivo)
import re
import time
import requests
from bs4 import BeautifulSoup
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import REQUEST_HEADERS

try:
    import cloudscraper as _cs
    _HAS_CLOUDSCRAPER = True
except ImportError:
    _HAS_CLOUDSCRAPER = False

_JOB_HREF_KEYWORDS = (
    "empleo", "trabajo", "oferta", "aviso", "cargo", "puesto", "vacante",
    "job", "vacancy", "position", "listing", "joboffer", "detalle", "ficha",
    "ver-empleo", "ver-oferta", "offer", "emprego",
)

_UY_LOCATIONS = re.compile(
    r"(Montevideo|Canelones|Maldonado|Colonia|Salto|Paysand[uú]|Rivera|"
    r"San\s+Jos[eé]|Tacuaremb[oó]|Cerro\s+Largo|Florida|Durazno|"
    r"Treinta\s+y\s+Tres|Rocha|Soriano|R[ií]o\s+Negro|Artigas|Lavalleja|"
    r"Flores|Remoto|teletrabajo|home\s+office)",
    re.IGNORECASE
)


class BaseJobScraper:
    SOURCE_NAME = "Genérico"
    BASE_URL    = ""

    ITEM_SELECTORS    = []
    TITLE_SELECTORS   = ["h2 a","h3 a","h4 a","a[class*='title']","a[class*='titulo']",
                         "[class*='title'] a","[class*='titulo'] a","h2","h3","h4"]
    COMPANY_SELECTORS = ["[class*='empresa']","[class*='company']","[class*='empleador']",
                         "[class*='razon']","span.empresa","p.empresa","[class*='client']"]
    LOCATION_SELECTORS= ["[class*='ubicacion']","[class*='location']","[class*='ciudad']",
                         "[class*='departamento']","[class*='lugar']","[class*='locali']"]
    SALARY_SELECTORS  = ["[class*='salario']","[class*='salary']","[class*='remuner']",
                         "[class*='sueldo']","[class*='importe']","[class*='remunera']"]
    DATE_SELECTORS    = ["time","[class*='fecha']","[class*='date']","[class*='publicad']",
                         "[class*='publicacion']","[class*='antiguedad']","[class*='ago']"]

    def __init__(self, max_pages=3, progress_callback=None):
        self.max_pages         = max_pages
        self.progress_callback = progress_callback
        self._sess_plain       = None
        self._sess_cloud       = None

    def _plain_session(self):
        if not self._sess_plain:
            s = requests.Session()
            s.headers.update(REQUEST_HEADERS)
            self._sess_plain = s
        return self._sess_plain

    def _cloud_session(self):
        if not self._sess_cloud:
            if _HAS_CLOUDSCRAPER:
                self._sess_cloud = _cs.create_scraper(
                    browser={"browser":"chrome","platform":"windows","desktop":True}
                )
                self._sess_cloud.headers.update(REQUEST_HEADERS)
            else:
                self._sess_cloud = self._plain_session()
        return self._sess_cloud

    def _status(self, msg):
        if self.progress_callback:
            self.progress_callback(msg)

    def _get(self, url, timeout=25, use_cloud=False):
        sess = self._cloud_session() if use_cloud else self._plain_session()
        try:
            resp = sess.get(url, timeout=timeout)
            resp.raise_for_status()
            return resp
        except requests.exceptions.HTTPError as e:
            code = e.response.status_code if e.response is not None else 0
            if code in (403, 429, 503) and not use_cloud and _HAS_CLOUDSCRAPER:
                self._status(f"{self.SOURCE_NAME} — cloudflare, reintentando…")
                return self._get(url, timeout=timeout, use_cloud=True)
            self._status(f"{self.SOURCE_NAME} — HTTP {code}")
            return None
        except Exception as e:
            self._status(f"{self.SOURCE_NAME} — {e}")
            return None

    def _abs(self, href):
        if not href:
            return ""
        href = href.strip()
        if href.startswith("http"):
            return href
        if href.startswith("//"):
            return "https:" + href
        if href.startswith("/"):
            return self.BASE_URL.rstrip("/") + href
        return self.BASE_URL + "/" + href

    def _text(self, el):
        return el.get_text(separator=" ", strip=True) if el else ""

    def _first(self, soup, selectors):
        for sel in selectors:
            try:
                el = soup.select_one(sel)
                if el:
                    return el
            except Exception:
                pass
        return None

    def _parse_salary(self, text):
        if not text:
            return None, ""
        cur = "USD" if re.search(r"U\$S|USD|US\$|dól|dolar", text, re.IGNORECASE) else ("UYU" if "$" in text else "")
        nums = re.sub(r"[^\d]", "", text)
        return (int(nums) if nums and len(nums) < 10 else None), cur

    def _extract_attrs(self, block):
        r = {"modalidad":"","area":"","salario":"","salario_num":None,"moneda":"","fecha":""}
        if block is None:
            return r
        tl = block.get_text(" ", strip=True).lower()
        if any(k in tl for k in ("remoto","teletrabajo","home office","work from home")):
            r["modalidad"] = "Remoto"
        elif any(k in tl for k in ("híbrido","hibrido","mixto")):
            r["modalidad"] = "Híbrido"
        elif "presencial" in tl:
            r["modalidad"] = "Presencial"
        sal_el = self._first(block, self.SALARY_SELECTORS)
        if sal_el:
            num, cur = self._parse_salary(sal_el.get_text(strip=True))
            r["salario"], r["salario_num"], r["moneda"] = sal_el.get_text(strip=True), num, cur
        else:
            m = re.search(r"(U\$S|USD|US\$|\$)\s*[\d.,]+(?:\s*[-–]\s*[\d.,]+)?",
                          block.get_text(" ", strip=True), re.IGNORECASE)
            if m:
                num, cur = self._parse_salary(m.group(0))
                r["salario"], r["salario_num"], r["moneda"] = m.group(0), num, cur
        date_el = self._first(block, self.DATE_SELECTORS)
        if date_el:
            r["fecha"] = (date_el.get("datetime","") or date_el.get_text(strip=True))[:30]
        return r

    def _build_job(self, block, link, title, company, location):
        if not link or not title or len(title) < 4:
            return None
        attrs = self._extract_attrs(block)
        return {
            "titulo":link[:0] or title[:120],  # dummy trick to keep order
            "titulo":      title[:120],
            "empresa":     (company or "")[:100],
            "zona":        (location or "Uruguay")[:100],
            "modalidad":   attrs["modalidad"],
            "area":        attrs["area"],
            "salario":     attrs["salario"],
            "salario_num": attrs["salario_num"],
            "moneda":      attrs["moneda"],
            "fecha":       attrs["fecha"],
            "link":        link,
            "fuente":      self.SOURCE_NAME,
        }

    # ── Parser genérico 3 capas ──────────────────────────────────────────────
    def _generic_parse(self, html: str) -> list:
        soup    = BeautifulSoup(html, "html.parser")
        results = []
        seen    = set()

        # Capa 1 — contenedores repetidos (tarjetas de resultados)
        freq = {}
        for el in soup.find_all(["article","li","div"]):
            cls = el.get("class")
            if not cls:
                continue
            key = f"{el.name}::{cls[0]}"
            freq.setdefault(key, []).append(el)

        for key, els in sorted(freq.items(), key=lambda x: -len(x[1])):
            if len(els) < 3:
                continue
            sample = " ".join(e.get_text(" ", strip=True) for e in els[:4]).lower()
            if not any(k in sample for k in (
                "empresa","cargo","puesto","empleo","trabajo","sueldo","postul",
                "requisito","experiencia","jornada","desarrollad","analista","comercial"
            )):
                continue
            for el in els:
                job = self._extract_block(el, seen)
                if job:
                    results.append(job)
            if len(results) >= 3:
                return results

        # Capa 2 — links con href de empleo
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if len(href) < 6 or href.startswith(("#","javascript","mailto","tel")):
                continue
            full = self._abs(href)
            if full in seen:
                continue
            if not any(k in href.lower() for k in _JOB_HREF_KEYWORDS) \
               and not (len(href) > 25 and href.count("/") >= 2):
                continue
            # Subir hasta encontrar un contenedor con texto
            container = a
            for _ in range(6):
                if container is None or len(container.get_text(strip=True)) > 20:
                    break
                container = container.parent
            job = self._extract_block(container, seen, forced_link=full)
            if job and len(job["titulo"]) > 4:
                results.append(job)

        if results:
            return results

        # Capa 3 — headings con link
        for h in soup.find_all(["h2","h3","h4"]):
            a = h.find("a",href=True) or (h.parent and h.parent.find("a",href=True))
            if not a:
                continue
            full = self._abs(a["href"])
            if not full or full in seen:
                continue
            title = h.get_text(strip=True)
            if not 4 < len(title) < 150:
                continue
            container = h.parent
            loc = "Uruguay"
            if container:
                m = _UY_LOCATIONS.search(container.get_text(" ",strip=True))
                if m:
                    loc = m.group(0).strip()
            attrs = self._extract_attrs(container)
            seen.add(full)
            results.append({
                "titulo":      title[:120],
                "empresa":     "",
                "zona":        loc,
                "modalidad":   attrs["modalidad"],
                "area":        "",
                "salario":     attrs["salario"],
                "salario_num": attrs["salario_num"],
                "moneda":      attrs["moneda"],
                "fecha":       attrs["fecha"],
                "link":        full,
                "fuente":      self.SOURCE_NAME,
            })
        return results

    def _extract_block(self, block, seen: set, forced_link: str = ""):
        if block is None:
            return None
        link = forced_link
        if not link:
            a = block.find("a", href=True)
            link = self._abs(a["href"]) if a else ""
        if not link or link in seen:
            return None

        # Validar que el link pertenece al mismo dominio (no links externos)
        if self.BASE_URL and not link.startswith(self.BASE_URL):
            # Permitir links absolutos del mismo dominio
            from urllib.parse import urlparse
            base_domain = urlparse(self.BASE_URL).netloc
            link_domain = urlparse(link).netloc
            if base_domain and link_domain and base_domain not in link_domain:
                return None

        seen.add(link)

        # Título
        title = ""
        for tag in ["h2","h3","h4","h5"]:
            h = block.find(tag)
            if h:
                title = h.get_text(strip=True)
                break
        if not title:
            a = block.find("a", href=True)
            if a:
                title = a.get_text(strip=True)
        if not title:
            title = block.get_text(" ", strip=True)[:80]
        if not title or len(title) < 4:
            return None

        # Empresa
        company = ""
        for sel in self.COMPANY_SELECTORS:
            try:
                el = block.select_one(sel)
                if el:
                    t = el.get_text(strip=True)
                    if t and t != title[:len(t)]:
                        company = t
                        break
            except Exception:
                pass

        # Zona
        location = "Uruguay"
        for sel in self.LOCATION_SELECTORS:
            try:
                el = block.select_one(sel)
                if el:
                    location = el.get_text(strip=True)[:80]
                    break
            except Exception:
                pass
        if location == "Uruguay":
            m = _UY_LOCATIONS.search(block.get_text(" ", strip=True))
            if m:
                location = m.group(0).strip()

        attrs = self._extract_attrs(block)
        return {
            "titulo":      title[:120],
            "empresa":     company[:100],
            "zona":        location[:100],
            "modalidad":   attrs["modalidad"],
            "area":        "",
            "salario":     attrs["salario"],
            "salario_num": attrs["salario_num"],
            "moneda":      attrs["moneda"],
            "fecha":       attrs["fecha"],
            "link":        link,
            "fuente":      self.SOURCE_NAME,
        }

    def parse_page(self, html: str) -> list:
        return []

    def _parse_with_fallback(self, html: str) -> list:
        results = self.parse_page(html)
        if not results:
            self._status(f"{self.SOURCE_NAME} — usando parser genérico…")
            results = self._generic_parse(html)
        return results

    def build_url(self, keyword: str, location: str, page: int) -> str:
        raise NotImplementedError

    def scrape(self, keyword: str = "", location: str = "") -> list:
        all_jobs = []
        for page in range(1, self.max_pages + 1):
            url = self.build_url(keyword, location, page)
            self._status(f"{self.SOURCE_NAME} — pág. {page}/{self.max_pages}…")
            resp = self._get(url)
            if resp is None:
                break
            jobs = self._parse_with_fallback(resp.text)
            if not jobs:
                self._status(f"{self.SOURCE_NAME} — sin resultados en pág. {page}.")
                break
            all_jobs.extend(jobs)
            if page < self.max_pages:
                time.sleep(0.8)
        return all_jobs
