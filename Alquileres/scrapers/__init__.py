# scrapers/__init__.py
from .mercadolibre import scrape_mercadolibre
from .infocasas    import scrape_infocasas
from .gallito      import scrape_gallito
from .casasweb     import scrape_casasweb
from .casasymas    import scrape_casasymas
from .remax        import scrape_remax
from .agencias     import (
    scrape_acsa,
    scrape_ciudad_inmobiliaria,
    scrape_braglia,
    scrape_lars,
)
from .facebook     import build_facebook_links

__all__ = [
    "scrape_mercadolibre",
    "scrape_infocasas",
    "scrape_gallito",
    "scrape_casasweb",
    "scrape_casasymas",
    "scrape_remax",
    "scrape_acsa",
    "scrape_ciudad_inmobiliaria",
    "scrape_braglia",
    "scrape_lars",
    "build_facebook_links",
]
