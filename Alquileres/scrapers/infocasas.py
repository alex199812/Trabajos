# scrapers/infocasas.py — InfoCasas Uruguay
import re
from bs4 import BeautifulSoup
from .base import BaseScraper


class InfoCasasScraper(BaseScraper):
    SOURCE_NAME = "InfoCasas"
    BASE_URL    = "https://www.infocasas.com.uy"

    PROP_MAP = {
        "": "", "apartamentos": "apartamentos",
        "casas": "casas", "ph": "ph", "locales": "locales",
    }

    def build_url(self, prop_type, page):
        seg = self.PROP_MAP.get(prop_type, "")
        dept = dept_slug or "montevideo"
        path = f"/alquiler/{seg}/{dept}" if seg else f"/alquiler/{dept}"
        if page > 1:
            path += f"/pagina{page}"
        return self.BASE_URL + path

    def parse_page(self, html):
        soup = BeautifulSoup(html, "html.parser")
        listings = []

        # InfoCasas renderiza con Next.js — intentar varios selectores
        items = (
            soup.select("li[class*='listing']")
            or soup.select("div[class*='listing']")
            or soup.select("[class*='PropertyCard']")
            or soup.select("[class*='property-card']")
            or soup.select("[class*='listingCard']")
            or soup.select(".lc-data")
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


def scrape_infocasas(prop_type="", max_pages=3, progress_callback=None, dept_slug="montevideo"):
    scraper = InfoCasasScraper(max_pages, progress_callback)
    scraper.dept_slug = dept_slug
    return scraper.scrape(prop_type)
