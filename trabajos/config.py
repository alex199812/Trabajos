# config.py — Configuración centralizada v3
#
# NUEVO en cada categoría:
#   buscojobs_ts  → ID de tipo de trabajo en BuscoJobs (ej: "ts1008")
#   buscojobs_cat → slug de categoría en BuscoJobs (ej: "atencion-al-cliente")
# Si buscojobs_ts está vacío, el scraper usa ?q= como fallback.

CATEGORIAS = {
    "Administración / Oficina": {
        "label":         "Administración / Oficina",
        "buscojobs_q":   "administracion",
        "buscojobs_ts":  "ts1001",
        "buscojobs_cat": "administracion-secretariado",
        "computrabajo":  "administracion-y-secretariado",
        "gallito_area":  "administracion-secretariado",
        "keyword":       "administracion",
    },
    "Atención al cliente": {
        "label":         "Atención al cliente",
        "buscojobs_q":   "atencion al cliente",
        "buscojobs_ts":  "ts1008",
        "buscojobs_cat": "atencion-al-cliente",
        "computrabajo":  "atencion-al-cliente",
        "gallito_area":  "atencion-al-cliente",
        "keyword":       "atencion cliente",
    },
    "Comercial / Ventas": {
        "label":         "Comercial / Ventas",
        "buscojobs_q":   "ventas",
        "buscojobs_ts":  "ts1004",
        "buscojobs_cat": "comercial-ventas",
        "computrabajo":  "comercial-ventas-y-negocios",
        "gallito_area":  "ventas-comercial",
        "keyword":       "ventas",
    },
    "Construcción / Obras": {
        "label":         "Construcción / Obras",
        "buscojobs_q":   "construccion",
        "buscojobs_ts":  "",
        "buscojobs_cat": "construccion-obras",
        "computrabajo":  "construccion-y-obra-civil",
        "gallito_area":  "construccion-inmobiliaria",
        "keyword":       "construccion",
    },
    "Contabilidad / Finanzas": {
        "label":         "Contabilidad / Finanzas",
        "buscojobs_q":   "contabilidad",
        "buscojobs_ts":  "ts1003",
        "buscojobs_cat": "contabilidad-finanzas",
        "computrabajo":  "contabilidad-y-finanzas",
        "gallito_area":  "contabilidad-finanzas",
        "keyword":       "contabilidad",
    },
    "Diseño / Artes gráficas": {
        "label":         "Diseño / Artes gráficas",
        "buscojobs_q":   "diseño",
        "buscojobs_ts":  "",
        "buscojobs_cat": "diseno-artes-graficas",
        "computrabajo":  "diseno-y-artes-graficas",
        "gallito_area":  "diseno-publicidad",
        "keyword":       "diseño",
    },
    "Educación / Docencia": {
        "label":         "Educación / Docencia",
        "buscojobs_q":   "educacion",
        "buscojobs_ts":  "",
        "buscojobs_cat": "educacion-docencia",
        "computrabajo":  "educacion-y-formacion",
        "gallito_area":  "educacion-formacion",
        "keyword":       "docente",
    },
    "Gastronomía / Hotelería": {
        "label":         "Gastronomía / Hotelería",
        "buscojobs_q":   "gastronomia",
        "buscojobs_ts":  "",
        "buscojobs_cat": "gastronomia-hoteleria",
        "computrabajo":  "hoteleria-y-turismo",
        "gallito_area":  "hoteleria-gastronomia-turismo",
        "keyword":       "gastronomia",
    },
    "Ingeniería": {
        "label":         "Ingeniería",
        "buscojobs_q":   "ingenieria",
        "buscojobs_ts":  "",
        "buscojobs_cat": "ingenieria",
        "computrabajo":  "ingenieria-y-tecnologia",
        "gallito_area":  "ingenieria",
        "keyword":       "ingeniero",
    },
    "Legal / Jurídico": {
        "label":         "Legal / Jurídico",
        "buscojobs_q":   "legal",
        "buscojobs_ts":  "",
        "buscojobs_cat": "legal-juridico",
        "computrabajo":  "derecho-y-asesoría-jurídica",
        "gallito_area":  "legal-juridico",
        "keyword":       "abogado",
    },
    "Logística / Depósito": {
        "label":         "Logística / Depósito",
        "buscojobs_q":   "logistica",
        "buscojobs_ts":  "ts1007",
        "buscojobs_cat": "logistica-deposito",
        "computrabajo":  "logistica-y-transporte",
        "gallito_area":  "logistica-deposito",
        "keyword":       "logistica",
    },
    "Marketing / Comunicación": {
        "label":         "Marketing / Comunicación",
        "buscojobs_q":   "marketing",
        "buscojobs_ts":  "ts1021",
        "buscojobs_cat": "marketing",
        "computrabajo":  "marketing-y-comunicacion",
        "gallito_area":  "marketing-comunicacion-publicidad",
        "keyword":       "marketing",
    },
    "Recursos Humanos": {
        "label":         "Recursos Humanos",
        "buscojobs_q":   "recursos humanos",
        "buscojobs_ts":  "",
        "buscojobs_cat": "recursos-humanos",
        "computrabajo":  "recursos-humanos",
        "gallito_area":  "recursos-humanos",
        "keyword":       "recursos humanos",
    },
    "Salud / Medicina": {
        "label":         "Salud / Medicina",
        "buscojobs_q":   "salud",
        "buscojobs_ts":  "",
        "buscojobs_cat": "salud-medicina",
        "computrabajo":  "salud-y-medicina",
        "gallito_area":  "salud-medicina",
        "keyword":       "enfermero",
    },
    "Seguridad": {
        "label":         "Seguridad",
        "buscojobs_q":   "seguridad",
        "buscojobs_ts":  "",
        "buscojobs_cat": "seguridad",
        "computrabajo":  "seguridad-y-vigilancia",
        "gallito_area":  "seguridad",
        "keyword":       "seguridad",
    },
    "Tecnología / IT": {
        "label":         "Tecnología / IT",
        "buscojobs_q":   "tecnologia",
        "buscojobs_ts":  "ts1017",
        "buscojobs_cat": "tecnologia-de-la-informacion",
        "computrabajo":  "informatica-y-telecomunicaciones",
        "gallito_area":  "sistemas-tecnologia-internet",
        "keyword":       "desarrollador",
    },
    "Transporte / Chofer": {
        "label":         "Transporte / Chofer",
        "buscojobs_q":   "transporte",
        "buscojobs_ts":  "",
        "buscojobs_cat": "transporte-chofer",
        "computrabajo":  "transporte-y-logistica",
        "gallito_area":  "transporte",
        "keyword":       "chofer",
    },
    "Producción / Industria": {
        "label":         "Producción / Industria",
        "buscojobs_q":   "produccion",
        "buscojobs_ts":  "ts1006",
        "buscojobs_cat": "produccion-industria",
        "computrabajo":  "produccion-y-manufactura",
        "gallito_area":  "produccion",
        "keyword":       "operario",
    },
}

LOCALIDADES = sorted([
    "Montevideo", "Canelones", "Maldonado", "Colonia", "Salto",
    "Paysandú", "Rivera", "San José", "Flores", "Rocha",
    "Tacuarembó", "Cerro Largo", "Artigas", "Durazno", "Florida",
    "Lavalleja", "Río Negro", "Soriano", "Treinta y Tres",
    "Remoto / Teletrabajo",
])

MODALIDADES  = ["Todas", "Presencial", "Remoto", "Híbrido"]
EXPERIENCIAS = [
    "Cualquier nivel", "Sin experiencia / Primer empleo",
    "Junior (1-3 años)", "Semi-senior (3-5 años)",
    "Senior (5+ años)", "Gerencial / Dirección",
]
JORNADAS = ["Cualquier jornada", "Full-time", "Part-time", "Freelance / Por horas"]
SECTORES = ["Público y privado", "Solo privado", "Solo público / Estado"]

PORTALS = {
    "BuscoJobs":       {"group": "Portales grandes",    "scraper": "buscojobs",      "color": "#0066cc"},
    "Computrabajo":    {"group": "Portales grandes",    "scraper": "computrabajo",   "color": "#e8820c"},
    "Gallito Trabajo": {"group": "Portales grandes",    "scraper": "gallito",        "color": "#003087"},
    "EmpleosUruguay":  {"group": "Portales grandes",    "scraper": "empleosuruguay", "color": "#2ecc71"},
    "Trabajo en Casa": {"group": "Portales grandes",    "scraper": "trabajoencasa",  "color": "#8e44ad"},
    "UruguayConcursa": {"group": "Sector público",      "scraper": "vacantes",       "color": "#c0392b"},
    "LinkedIn":        {"group": "Redes profesionales", "scraper": "linkedin",       "color": "#0a66c2"},
}

REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-UY,es;q=0.9,en;q=0.8",
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Encoding": "gzip, deflate, br",
    "Connection":      "keep-alive",
}

# Filtro de fecha — opciones de antigüedad máxima de los resultados
FECHAS = [
    "Cualquier fecha",
    "Hoy",
    "Últimos 2 días",
    "Última semana",
    "Últimos 15 días",
    "Último mes",
    "Últimos 3 meses",
]

# Mapeo de fecha a parámetros por portal
FECHA_PARAMS = {
    "Hoy":            {"gallito": "hoy",          "buscojobs_days": 1,  "linkedin_tpr": "r86400"},
    "Últimos 2 días": {"gallito": "hace-2-dias",   "buscojobs_days": 2,  "linkedin_tpr": "r172800"},
    "Última semana":  {"gallito": "ultima-semana", "buscojobs_days": 7,  "linkedin_tpr": "r604800"},
    "Últimos 15 días":{"gallito": "ultima-quincena","buscojobs_days": 15, "linkedin_tpr": "r1296000"},
    "Último mes":     {"gallito": "ultimo-mes",    "buscojobs_days": 30, "linkedin_tpr": "r2592000"},
    "Últimos 3 meses":{"gallito": "",              "buscojobs_days": 90, "linkedin_tpr": ""},
}
