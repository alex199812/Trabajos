from .buscojobs        import scrape_buscojobs
from .gallito          import scrape_gallito, build_gallito_links
from .computrabajo     import scrape_computrabajo, build_computrabajo_links
from .empleosuruguay   import scrape_empleosuruguay
from .trabajoencasa    import scrape_trabajoencasa
from .vacantes         import scrape_vacantes
from .linkedin         import build_linkedin_links

__all__ = [
    "scrape_buscojobs", "scrape_gallito", "build_gallito_links",
    "scrape_computrabajo", "build_computrabajo_links",
    "scrape_empleosuruguay", "scrape_trabajoencasa",
    "scrape_vacantes", "build_linkedin_links",
]
