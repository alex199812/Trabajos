# scrapers/remax.py — RE/MAX Uruguay
from bs4 import BeautifulSoup
from .base import BaseScraper


class RemaxScraper(BaseScraper):
    SOURCE_NAME = "RE/MAX Uruguay"
    BASE_URL    = "https://www.remax.com.uy"

    PROP_MAP = {
        "": "", "apartamentos": "apartamentos",
        "casas": "casas", "ph": "ph", "locales": "locales",
    }

    def build_url(self, prop_type, page):
        ptype = self.PROP_MAP.get(prop_type, "")
        dept = getattr(self, "dept_slug", "montevideo") or "montevideo"
        url = f"{self.BASE_URL}/alquiler/{ptype}/uruguay/{dept}" if ptype else f"{self.BASE_URL}/alquiler/uruguay/{dept}"
        if page > 1:
            url += f"?pageNumber={page}"
        return url

    def parse_page(self, html):
        soup = BeautifulSoup(html, "html.parser")
        listings = []
        items = (
            soup.select("div.listing-item")
            or soup.select("[class*='listing-card']")
            or soup.select("[class*='property-card']")
            or soup.select("[class*='PropertyCard']")
            or soup.select("article.property")
            or soup.select("[class*='result-item']")
            or soup.select("article")
        )
        for item in items:
            try:
                title_el = self._select_first(item, [".listing-title",".property-title","h2","h3","[class*='title']","[class*='titulo']"])
                price_el = self._select_first(item, [".listing-price",".property-price","[class*='price']","[class*='precio']"])
                zone_el  = self._select_first(item, [".listing-address",".property-address","[class*='address']","[class*='ubicacion']","[class*='location']"])
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


def scrape_remax(prop_type="", max_pages=3, progress_callback=None, dept_slug="montevideo"):
    return RemaxScraper(max_pages, progress_callback).scrape(prop_type)
