# scrapers/agencias.py — ACSA, Ciudad Inmobiliaria, Braglia, Lars
from bs4 import BeautifulSoup
from .base import BaseScraper


class AcsaScraper(BaseScraper):
    SOURCE_NAME = "ACSA"
    BASE_URL    = "https://www.acsa.com.uy"
    def build_url(self, prop_type, page):
        url = f"{self.BASE_URL}/alquiler/montevideo"
        if page > 1: url += f"?pagina={page}"
        return url
    def parse_page(self, html):
        return self._generic_parse_items(html)


class CiudadInmobiliariaScraper(BaseScraper):
    SOURCE_NAME = "Ciudad Inmobiliaria"
    BASE_URL    = "https://www.ciudadinmobiliaria.com.uy"
    def build_url(self, prop_type, page):
        url = f"{self.BASE_URL}/alquiler/montevideo"
        if page > 1: url += f"/{page}"
        return url
    def parse_page(self, html):
        return self._generic_parse_items(html)


class BragliaScraper(BaseScraper):
    SOURCE_NAME = "Braglia"
    BASE_URL    = "https://www.braglia.com.uy"
    def build_url(self, prop_type, page):
        url = f"{self.BASE_URL}/alquileres/montevideo"
        if page > 1: url += f"?pagina={page}"
        return url
    def parse_page(self, html):
        return self._generic_parse_items(html)


class LarsScraper(BaseScraper):
    SOURCE_NAME = "Lars"
    BASE_URL    = "https://www.lars.com.uy"
    def build_url(self, prop_type, page):
        url = f"{self.BASE_URL}/alquiler/montevideo"
        if page > 1: url += f"?page={page}"
        return url
    def parse_page(self, html):
        return self._generic_parse_items(html)


# Agrega método helper a BaseScraper para las agencias
from .base import BaseScraper as _Base
def _generic_parse_items(self, html):
    """Parsea usando selectores conocidos + fallback genérico."""
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    items = (
        soup.select("div.propiedad") or soup.select("article.propiedad")
        or soup.select("[class*='propiedad']") or soup.select("[class*='listing']")
        or soup.select("[class*='property']") or soup.select("article")
        or soup.select("li.item") or soup.select("div.item")
    )
    for item in items:
        try:
            title_el = self._select_first(item, self.TITLE_SELECTORS)
            price_el = self._select_first(item, self.PRICE_SELECTORS)
            zone_el  = self._select_first(item, self.ZONE_SELECTORS)
            link_el  = item.find("a", href=True)
            title = self._clean_text(title_el)
            price = self._clean_text(price_el)
            zone  = self._clean_text(zone_el)
            link  = self._make_absolute(link_el["href"] if link_el else "")
            entry = self._build_listing(item, link, title, price, zone)
            if entry:
                listings.append(entry)
        except Exception:
            continue
    return listings

_Base._generic_parse_items = _generic_parse_items


def scrape_acsa(prop_type="", max_pages=3, progress_callback=None):
    return AcsaScraper(max_pages, progress_callback).scrape(prop_type)

def scrape_ciudad_inmobiliaria(prop_type="", max_pages=3, progress_callback=None):
    return CiudadInmobiliariaScraper(max_pages, progress_callback).scrape(prop_type)

def scrape_braglia(prop_type="", max_pages=3, progress_callback=None):
    return BragliaScraper(max_pages, progress_callback).scrape(prop_type)

def scrape_lars(prop_type="", max_pages=3, progress_callback=None):
    return LarsScraper(max_pages, progress_callback).scrape(prop_type)
