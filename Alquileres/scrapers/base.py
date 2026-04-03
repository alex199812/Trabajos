# scrapers/base.py — Clase base con scraping genérico robusto
import re
import time
import requests
from bs4 import BeautifulSoup
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import REQUEST_HEADERS


class BaseScraper:
    SOURCE_NAME = "Genérico"
    BASE_URL    = ""

    TITLE_SELECTORS  = ["h2","h3","h4",".titulo","[class*='title']","[class*='titulo']","[class*='Title']"]
    PRICE_SELECTORS  = [".precio",".price","[class*='precio']","[class*='price']","[class*='valor']","[class*='importe']","[class*='Price']","[class*='Precio']"]
    ZONE_SELECTORS   = [".ubicacion",".location","[class*='ubicacion']","[class*='location']",".barrio",".zona","address","[class*='address']","[class*='Address']"]
    GASTOS_SELECTORS = ["[class*='gasto']","[class*='expensa']","[class*='cargo']","[class*='Gasto']","[class*='Expensa']"]
    ITEM_SELECTORS   = []

    def __init__(self, max_pages=3, progress_callback=None):
        self.max_pages         = max_pages
        self.progress_callback = progress_callback
        self.session           = requests.Session()
        self.session.headers.update(REQUEST_HEADERS)

    def _status(self, msg):
        if self.progress_callback:
            self.progress_callback(msg)

    def _get(self, url, timeout=25):
        try:
            resp = self.session.get(url, timeout=timeout)
            resp.raise_for_status()
            return resp
        except Exception as e:
            self._status(f"{self.SOURCE_NAME} — error: {e}")
            return None

    def _select_first(self, soup, selectors):
        for sel in selectors:
            try:
                el = soup.select_one(sel)
                if el:
                    return el
            except Exception:
                continue
        return None

    def _clean_text(self, el):
        return el.get_text(separator=" ", strip=True) if el else ""

    def _make_absolute(self, href):
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

    def _parse_price_text(self, text):
        if not text or not text.strip():
            return "Consultar", "", None
        text = text.strip()
        if re.search(r"U\$S|USD|US\$|dól|dol", text, re.IGNORECASE):
            currency = "USD"
        elif "$" in text:
            currency = "UYU"
        else:
            currency = ""
        clean = re.sub(r"[^\d]", "", text)
        num = int(clean) if clean and len(clean) < 10 else None
        return text, currency, num

    def _extract_attrs(self, item):
        result = {"dormitorios": None, "banos": None, "superficie_m2": None,
                  "gastos_num": None, "gastos": ""}
        for sel in self.GASTOS_SELECTORS:
            try:
                el = item.select_one(sel)
                if el:
                    t = el.get_text(strip=True)
                    nums = re.findall(r"\d+", t)
                    if nums:
                        result["gastos"]     = t
                        result["gastos_num"] = int(nums[0])
                    break
            except Exception:
                pass
        for el in item.find_all(True):
            try:
                t = el.get_text(strip=True).lower()
                if len(t) > 80 or len(t) < 2:
                    continue
                nums = re.findall(r"\d+", t)
                if not nums:
                    continue
                n = int(nums[0])
                if any(k in t for k in ("dorm","habitac","cuarto","recám","ambi")) and result["dormitorios"] is None and n <= 20:
                    result["dormitorios"] = n
                elif any(k in t for k in ("baño","bano","wc","toilet")) and result["banos"] is None and n <= 10:
                    result["banos"] = n
                elif ("m²" in t or "m2" in t) and result["superficie_m2"] is None and 5 < n < 5000:
                    result["superficie_m2"] = n
                elif any(k in t for k in ("gasto","expensa","gc")) and result["gastos_num"] is None and n > 100:
                    result["gastos"]     = el.get_text(strip=True)
                    result["gastos_num"] = n
            except Exception:
                continue
        return result

    def _build_listing(self, item, link, title, price_text, zone):
        if not link or link.rstrip("/") == self.BASE_URL.rstrip("/"):
            return None
        price_display, currency, price_num = self._parse_price_text(price_text)
        attrs = self._extract_attrs(item)
        return {
            "titulo":        (title or "Propiedad en alquiler")[:120],
            "precio":        price_display,
            "precio_num":    price_num,
            "moneda":        currency,
            "zona":          (zone or "Montevideo")[:100],
            "dormitorios":   attrs["dormitorios"],
            "banos":         attrs["banos"],
            "superficie_m2": attrs["superficie_m2"],
            "gastos":        attrs["gastos"],
            "gastos_num":    attrs["gastos_num"],
            "link":          link,
            "fuente":        self.SOURCE_NAME,
        }

    # ── Scraping genérico de último recurso ──────────────────────────────────
    def _generic_parse(self, html: str) -> list:
        """
        Extrae anuncios de CUALQUIER página de portal inmobiliario.
        Busca todos los links que parecen anuncios + precio cercano.
        """
        soup = BeautifulSoup(html, "html.parser")
        listings = []
        seen = set()

        # Buscar todos los <a> que parecen links a propiedades
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            full_link = self._make_absolute(href)

            # Filtrar links que parecen anuncios (no menús, no logos)
            if not full_link or full_link in seen:
                continue
            if len(href) < 8 or href in ("#", "/", ""):
                continue
            # El link debe tener palabras clave de propiedad o ser un path largo
            href_lower = href.lower()
            is_property = any(k in href_lower for k in (
                "apartamento","apto","casa","inmueble","propiedad",
                "alquiler","rental","property","listing","aviso",
                "ficha","detalle","inmobil"
            )) or (len(href) > 25 and href.count("/") >= 2)
            if not is_property:
                continue

            seen.add(full_link)

            # Buscar precio en el contenedor más cercano (hasta 4 niveles arriba)
            price_text = ""
            zone_text  = ""
            title_text = ""
            container  = a_tag.parent
            for _ in range(5):
                if container is None:
                    break
                text = container.get_text(" ", strip=True)
                # Buscar precio (patrón: $, U$S, USD seguido de números)
                price_match = re.search(
                    r"(U\$S|USD|US\$|\$)\s*[\d.,]+", text, re.IGNORECASE
                )
                if price_match and not price_text:
                    # Extraer alrededor del match para más contexto
                    start = max(0, price_match.start() - 5)
                    end   = min(len(text), price_match.end() + 10)
                    price_text = text[start:end].strip()

                # Buscar zona/barrio
                zone_match = re.search(
                    r"(Pocitos|Carrasco|Cordón|Cordon|Centro|Palermo|Prado|Buceo|"
                    r"Malvín|Malvin|Punta\s+Carretas|Ciudad\s+Vieja|Parque\s+Batlle|"
                    r"Tres\s+Cruces|Unión|Union|Aguada|Barrio\s+Sur|Reducto|"
                    r"Jacinto\s+Vera|La\s+Blanqueada|Parque\s+Rod[oó]|Goes|"
                    r"Lezica|Sayago|Colón|Colon|La\s+Teja|Peñarol|Penarol|"
                    r"Montevideo)",
                    text, re.IGNORECASE
                )
                if zone_match and not zone_text:
                    zone_text = zone_match.group(0).strip()

                if price_text:
                    break
                container = container.parent

            # Título: texto del propio link o heading cercano
            title_text = a_tag.get_text(strip=True)
            if not title_text or len(title_text) < 5:
                # Buscar heading dentro del contenedor
                for tag in ["h2","h3","h4","h5"]:
                    h = a_tag.find(tag) or (a_tag.parent and a_tag.parent.find(tag))
                    if h:
                        title_text = h.get_text(strip=True)
                        break
            if not title_text:
                title_text = "Propiedad en alquiler"

            # Solo incluir si tiene precio o el link parece un anuncio específico
            if not price_text and len(href) < 35:
                continue

            price_display, currency, price_num = self._parse_price_text(price_text)

            listings.append({
                "titulo":        title_text[:120],
                "precio":        price_display,
                "precio_num":    price_num,
                "moneda":        currency,
                "zona":          zone_text or "Montevideo",
                "dormitorios":   None,
                "banos":         None,
                "superficie_m2": None,
                "gastos":        "",
                "gastos_num":    None,
                "link":          full_link,
                "fuente":        self.SOURCE_NAME,
            })

            if len(listings) >= 100:
                break

        return listings

    # ── Parse principal con fallback ─────────────────────────────────────────
    def parse_page(self, html: str) -> list:
        """Subclases sobreescriben esto. Si no hay resultados, usa genérico."""
        return []

    def _parse_with_fallback(self, html: str) -> list:
        results = self.parse_page(html)
        if not results:
            self._status(f"{self.SOURCE_NAME} — usando modo genérico…")
            results = self._generic_parse(html)
        return results

    def build_url(self, prop_type: str, page: int) -> str:
        raise NotImplementedError

    def scrape(self, prop_type: str = "") -> list:
        all_listings = []
        for page in range(1, self.max_pages + 1):
            url = self.build_url(prop_type, page)
            self._status(f"{self.SOURCE_NAME} — página {page} de {self.max_pages}…")
            resp = self._get(url)
            if resp is None:
                break
            listings = self._parse_with_fallback(resp.text)
            if not listings:
                self._status(f"{self.SOURCE_NAME} — sin resultados en pág. {page}.")
                break
            all_listings.extend(listings)
            if page < self.max_pages:
                time.sleep(1.0)
        return all_listings
