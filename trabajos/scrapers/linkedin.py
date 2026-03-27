# scrapers/linkedin.py — LinkedIn: genera links directos (no permite scraping)
import urllib.parse


def build_linkedin_links(keyword="", location="", modality="", experience="", job_type=""):
    """
    Genera links preconfigurados para buscar empleo en LinkedIn.
    LinkedIn no permite scraping — igual al comportamiento de Facebook en el buscador de alquileres.
    """
    links = []
    base = "https://www.linkedin.com/jobs/search/?"

    # Mapeo de modalidad a f_WT
    modality_map = {
        "Remoto":    "2",  # Remote
        "Híbrido":   "3",  # Hybrid
        "Presencial":"1",  # On-site
    }

    # Mapeo de experiencia a f_E
    experience_map = {
        "Sin experiencia":       "1",
        "Junior (1-3 años)":     "2",
        "Semi-senior (3-5 años)":"3",
        "Senior (5+ años)":      "4",
        "Gerencial":             "5,6",
    }

    # Mapeo de jornada a f_JT
    job_type_map = {
        "Full-time":       "F",
        "Part-time":       "P",
        "Freelance":       "C",
    }

    def make_url(kw, loc, extra_params=None):
        params = {"keywords": kw or "empleos Uruguay"}
        if loc and loc not in ("Todo el país", "Remoto / Teletrabajo", ""):
            params["location"] = f"{loc}, Uruguay"
        else:
            params["location"] = "Uruguay"

        if modality in modality_map:
            params["f_WT"] = modality_map[modality]
        if experience in experience_map:
            params["f_E"] = experience_map[experience]
        if job_type in job_type_map:
            params["f_JT"] = job_type_map[job_type]

        if extra_params:
            params.update(extra_params)

        return base + urllib.parse.urlencode(params)

    # Link principal
    links.append({
        "titulo":      f"LinkedIn — {keyword or 'Empleos'} en Uruguay",
        "link":        make_url(keyword, location),
        "descripcion": f"Búsqueda de '{keyword or 'empleos'}' con tus filtros en LinkedIn Jobs",
        "instruccion": "Abrí este link en tu navegador (necesitás estar logueado en LinkedIn)",
    })

    # Link adicional: búsqueda reciente (última semana)
    links.append({
        "titulo":      f"LinkedIn — {keyword or 'Empleos'} publicados esta semana",
        "link":        make_url(keyword, location, {"f_TPR": "r604800"}),
        "descripcion": "Filtra solo las ofertas publicadas en los últimos 7 días",
        "instruccion": "Abrí este link en tu navegador (necesitás estar logueado en LinkedIn)",
    })

    # Link adicional: empresas que están contratando en Uruguay
    if keyword:
        links.append({
            "titulo":      f"LinkedIn — Empresas que buscan '{keyword}'",
            "link":        make_url(keyword, "Uruguay", {"f_C": ""}),
            "descripcion": "Explora empresas uruguayas con posiciones abiertas para este perfil",
            "instruccion": "Abrí este link en tu navegador (necesitás estar logueado en LinkedIn)",
        })

    return links
