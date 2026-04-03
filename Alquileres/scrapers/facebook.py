# scrapers/facebook.py — Facebook Marketplace (generador de links)
#
# Facebook Marketplace requiere sesión iniciada y bloquea scrapers automáticos.
# Esta función genera los links directos de búsqueda para que el usuario los
# abra en su propio navegador (ya logueado en Facebook).

import urllib.parse


FACEBOOK_MARKETPLACE_BASE = "https://www.facebook.com/marketplace/montevideo/propertyrentals"

# Parámetros de búsqueda conocidos de Facebook Marketplace
PROP_TYPE_MAP = {
    "":             "",
    "apartamentos": "apartment",
    "casas":        "house",
    "ph":           "apartment",   # FB no tiene PH exacto
    "locales":      "commercial",
}

BEDROOMS_MAP = {
    0: "",   1: "1+",  2: "2+",
    3: "3+", 4: "4+",  5: "5+",
}


def build_facebook_links(
    prop_type:    str = "",
    min_bedrooms: int = 0,
    min_price:    int = 0,
    max_price:    int = 0,
) -> list[dict]:
    """
    Genera una lista de links de Facebook Marketplace para búsqueda manual.
    Retorna hasta 3 variantes (USD y UYU, distintas configuraciones).

    Cada dict tiene:
        { "titulo": str, "descripcion": str, "link": str }
    """
    links = []

    # ── Link principal (precio en USD)
    params_usd = {}
    if PROP_TYPE_MAP.get(prop_type):
        params_usd["propertyType"] = PROP_TYPE_MAP[prop_type]
    if min_bedrooms > 0:
        params_usd["minBedrooms"] = str(min_bedrooms)
    if max_price > 0:
        params_usd["maxPrice"]    = str(max_price)
        params_usd["priceType"]   = "monthly"

    url_usd = FACEBOOK_MARKETPLACE_BASE
    if params_usd:
        url_usd += "?" + urllib.parse.urlencode(params_usd)

    links.append({
        "titulo":      "🔵 Facebook Marketplace — Alquileres en Montevideo",
        "descripcion": f"Búsqueda filtrada: {prop_type or 'todos'} · {min_bedrooms}+ dorms · hasta {max_price or '∞'} USD",
        "link":        url_usd,
        "fuente":      "Facebook Marketplace",
        "instruccion": (
            "Abre este link en tu navegador (logueado en Facebook). "
            "Facebook Marketplace no permite búsqueda automática."
        ),
    })

    # ── Link sin filtros (por si los filtros no funcionan en tu región)
    links.append({
        "titulo":      "🔵 Facebook Marketplace — Todos los alquileres",
        "descripcion": "Sin filtros aplicados — explorá vos mismo",
        "link":        FACEBOOK_MARKETPLACE_BASE,
        "fuente":      "Facebook Marketplace",
        "instruccion": "Abre este link en tu navegador (logueado en Facebook).",
    })

    # ── Link de grupo de Facebook Uruguay (búsqueda complementaria)
    grupo_url = "https://www.facebook.com/groups/search/results/?q=alquiler+montevideo"
    links.append({
        "titulo":      "👥 Grupos de Facebook — Alquiler Montevideo",
        "descripcion": "Busca posts en grupos públicos de alquiler en Montevideo",
        "link":        grupo_url,
        "fuente":      "Facebook Marketplace",
        "instruccion": "Abre este link logueado en Facebook para ver publicaciones en grupos.",
    })

    return links
