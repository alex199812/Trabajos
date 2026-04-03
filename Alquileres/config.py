# config.py — Configuración centralizada

# ── Departamentos y barrios de Uruguay ────────────────────────────────────────
# Estructura: { "Departamento": { "slug": "slug-para-urls", "barrios": [...] } }

DEPARTMENTS = {
    "Montevideo": {
        "slug_ml":       "montevideo",
        "slug_ic":       "montevideo",
        "slug_gallito":  "montevideo",
        "slug_cw":       "13",          # código z= de Casasweb
        "barrios": sorted([
            "Aguada","Arroyo Seco","Atahualpa","Barrio Sur","Belvedere",
            "Brazo Oriental","Buceo","Capurro","Carrasco","Casavalle","Centro",
            "Cerro","Ciudad Vieja","Colón","Cordón","Figurita","Flor de Maroñas",
            "Goes","Hipódromo","Jacinto Vera","Jardines del Hipódromo",
            "La Blanqueada","La Teja","Larrañaga","Las Acacias","Lezica",
            "Malvín","Malvín Norte","Manga","Maroñas","Mercado Modelo","Millán",
            "Nuevo París","Palermo","Parque Batlle","Parque Rodó",
            "Paso de la Arena","Peñarol","Pocitos","Prado","Punta Carretas",
            "Punta de Rieles","Reducto","Sayago","Tres Cruces","Unión",
            "Villa Española","Villa Muñoz","Belvedere","Casabó",
        ]),
    },
    "Maldonado": {
        "slug_ml":       "maldonado",
        "slug_ic":       "maldonado",
        "slug_gallito":  "maldonado",
        "slug_cw":       "7",
        "barrios": sorted([
            "Punta del Este","Maldonado","San Carlos","Piriápolis",
            "Pan de Azúcar","Aiguá","Solís","La Barra","José Ignacio",
            "Manantiales","El Chorro","Punta Ballena","Portezuelo",
            "Sauce de Portezuelo","Las Flores","Playa Grande",
        ]),
    },
    "Canelones": {
        "slug_ml":       "canelones",
        "slug_ic":       "canelones",
        "slug_gallito":  "canelones",
        "slug_cw":       "3",
        "barrios": sorted([
            "Ciudad de la Costa","Las Piedras","Pando","La Paz",
            "Progreso","Santa Lucía","Atlántida","Salinas","Lagomar",
            "El Pinar","Solymar","Parque del Plata","Canelones",
            "Sauce","San Jacinto","Toledo","Barros Blancos",
        ]),
    },
    "Colonia": {
        "slug_ml":       "colonia",
        "slug_ic":       "colonia",
        "slug_gallito":  "colonia",
        "slug_cw":       "4",
        "barrios": sorted([
            "Colonia del Sacramento","Nueva Helvecia","Carmelo",
            "Juan Lacaze","Rosario","Nueva Palmira","Tarariras",
        ]),
    },
    "San José": {
        "slug_ml":       "san-jose",
        "slug_ic":       "san-jose",
        "slug_gallito":  "san-jose",
        "slug_cw":       "14",
        "barrios": sorted([
            "San José de Mayo","Libertad","Ciudad del Plata",
            "Ecilda Paullier","Rodríguez","Puntas de Valdéz",
        ]),
    },
    "Paysandú": {
        "slug_ml":       "paysandu",
        "slug_ic":       "paysandu",
        "slug_gallito":  "paysandu",
        "slug_cw":       "11",
        "barrios": sorted([
            "Paysandú","Guichón","Quebracho","Tambores","Porvenir",
        ]),
    },
    "Salto": {
        "slug_ml":       "salto",
        "slug_ic":       "salto",
        "slug_gallito":  "salto",
        "slug_cw":       "13",
        "barrios": sorted([
            "Salto","Constitución","Bella Unión","Colonia Lavalleja",
        ]),
    },
    "Rivera": {
        "slug_ml":       "rivera",
        "slug_ic":       "rivera",
        "slug_gallito":  "rivera",
        "slug_cw":       "12",
        "barrios": sorted([
            "Rivera","Tranqueras","Vichadero","Minas de Corrales",
        ]),
    },
    "Rocha": {
        "slug_ml":       "rocha",
        "slug_ic":       "rocha",
        "slug_gallito":  "rocha",
        "slug_cw":       "13",
        "barrios": sorted([
            "Rocha","La Paloma","Punta del Diablo","Chuy",
            "Lascano","Castillos","La Pedrera",
        ]),
    },
    "Tacuarembó": {
        "slug_ml":       "tacuarembo",
        "slug_ic":       "tacuarembo",
        "slug_gallito":  "tacuarembo",
        "slug_cw":       "17",
        "barrios": sorted([
            "Tacuarembó","Paso de los Toros","Curtina",
        ]),
    },
    "Durazno": {
        "slug_ml":       "durazno",
        "slug_ic":       "durazno",
        "slug_gallito":  "durazno",
        "slug_cw":       "5",
        "barrios": sorted([
            "Durazno","Sarandí del Yí","Carlos Reyles",
        ]),
    },
    "Florida": {
        "slug_ml":       "florida",
        "slug_ic":       "florida",
        "slug_gallito":  "florida",
        "slug_cw":       "6",
        "barrios": sorted([
            "Florida","Sarandí Grande","Casupá",
        ]),
    },
    "Lavalleja": {
        "slug_ml":       "lavalleja",
        "slug_ic":       "lavalleja",
        "slug_gallito":  "lavalleja",
        "slug_cw":       "6",
        "barrios": sorted([
            "Minas","Solís de Mataojo","José Batlle y Ordóñez",
        ]),
    },
    "Treinta y Tres": {
        "slug_ml":       "treinta-y-tres",
        "slug_ic":       "treinta-y-tres",
        "slug_gallito":  "treinta-y-tres",
        "slug_cw":       "18",
        "barrios": sorted([
            "Treinta y Tres","Vergara","Río Branco",
        ]),
    },
    "Cerro Largo": {
        "slug_ml":       "cerro-largo",
        "slug_ic":       "cerro-largo",
        "slug_gallito":  "cerro-largo",
        "slug_cw":       "2",
        "barrios": sorted([
            "Melo","Río Branco","Aceguá",
        ]),
    },
    "Artigas": {
        "slug_ml":       "artigas",
        "slug_ic":       "artigas",
        "slug_gallito":  "artigas",
        "slug_cw":       "1",
        "barrios": sorted([
            "Artigas","Bella Unión","Tomás Gomensoro",
        ]),
    },
    "Flores": {
        "slug_ml":       "flores",
        "slug_ic":       "flores",
        "slug_gallito":  "flores",
        "slug_cw":       "6",
        "barrios": sorted([
            "Trinidad","Ismael Cortinas",
        ]),
    },
    "Río Negro": {
        "slug_ml":       "rio-negro",
        "slug_ic":       "rio-negro",
        "slug_gallito":  "rio-negro",
        "slug_cw":       "12",
        "barrios": sorted([
            "Fray Bentos","Young","Nuevo Berlín",
        ]),
    },
    "Soriano": {
        "slug_ml":       "soriano",
        "slug_ic":       "soriano",
        "slug_gallito":  "soriano",
        "slug_cw":       "16",
        "barrios": sorted([
            "Mercedes","Dolores","Palmitas","José Enrique Rodó",
        ]),
    },
}

# Lista de departamentos ordenada con Montevideo primero
DEPARTMENT_NAMES = ["Montevideo"] + sorted([d for d in DEPARTMENTS if d != "Montevideo"])

# Compatibilidad con código anterior
NEIGHBORHOODS = DEPARTMENTS["Montevideo"]["barrios"]

PROPERTY_TYPES = {
    "Todos":        {"key": ""},
    "Apartamentos": {"key": "apartamentos"},
    "Casas":        {"key": "casas"},
    "PH":           {"key": "ph"},
    "Locales":      {"key": "locales"},
}

PORTALS = {
    "MercadoLibre":        {"group": "Portales grandes",  "scraper": "mercadolibre",        "color": "#FFE600", "text": "#333"},
    "InfoCasas":           {"group": "Portales grandes",  "scraper": "infocasas",           "color": "#00A651", "text": "#fff"},
    "Gallito":             {"group": "Portales grandes",  "scraper": "gallito",             "color": "#003087", "text": "#fff"},
    "Casasweb":            {"group": "Portales grandes",  "scraper": "casasweb",            "color": "#E84040", "text": "#fff"},
    "Casas y Más":         {"group": "Portales grandes",  "scraper": "casasymas",           "color": "#FF6B00", "text": "#fff"},
    "RE/MAX Uruguay":      {"group": "Inmobiliarias",     "scraper": "remax",               "color": "#CC0000", "text": "#fff"},
    "ACSA":                {"group": "Inmobiliarias",     "scraper": "acsa",                "color": "#1A3C6E", "text": "#fff"},
    "Ciudad Inmobiliaria": {"group": "Inmobiliarias",     "scraper": "ciudad_inmobiliaria", "color": "#5C2D91", "text": "#fff"},
    "Braglia":             {"group": "Inmobiliarias",     "scraper": "braglia",             "color": "#2E7D32", "text": "#fff"},
    "Lars":                {"group": "Inmobiliarias",     "scraper": "lars",                "color": "#0277BD", "text": "#fff"},
    "Facebook Marketplace":{"group": "Redes sociales",   "scraper": "facebook",            "color": "#1877F2", "text": "#fff"},
}

REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-UY,es;q=0.9,en;q=0.8",
    "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Connection":      "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}
