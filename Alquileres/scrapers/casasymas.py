# scrapers/casasymas.py — Casas y Más Uruguay
from bs4 import BeautifulSoup
from .base import BaseScraper


class CasasymasScraper(BaseScraper):
    SOURCE_NAME = "Casas y Más"
    BASE_URL    = "https://www.casasymas.com.uy"

    PROP_MAP = {
        "": "", "apartamentos": "apartamento",
        "casas": "casa", "ph": "ph", "locales": "local",
    }

    def build_url(self, prop_type, page):
        ptype = self.PROP_MAP.get(prop_type, "")
        url = f"{self.BASE_URL}/alquiler/{ptype}/montevideo" if ptype else f"{self.BASE_URL}/alquiler/montevideo"
        if page > 1:
            url += f"/{page}"
        return url

    def parse_page(self, html):
        soup = BeautifulSoup(html, "html.parser")
        listings = []
        items = (
            soup.select("div.aviso")
            or soup.select("article.aviso")
            or soup.select("[class*='aviso']")
            or soup.select("[class*='item-propiedad']")
            or soup.select("[class*='PropertyCard']")
            or soup.select("li.item")
            or soup.select("article")
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


def scrape_casasymas(prop_type="", max_pages=3, progress_callback=None):
    return CasasymasScraper(max_pages, progress_callback).scrape(prop_type)
