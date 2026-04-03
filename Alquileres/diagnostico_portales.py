"""
diagnostico_portales.py v2 — analiza el HTML real de Casasweb
y verifica cloudscraper para Gallito
"""
import re, requests, time

HEADERS = {
    "User-Agent":      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-UY,es;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Connection":      "keep-alive",
}

# ── CASASWEB: analizar HTML real ──────────────────────────
print("="*55)
print("CASASWEB — analizando HTML real (326KB)")
print("="*55)

s = requests.Session()
s.headers.update(HEADERS)
r = s.get("https://casasweb.com/resultados.aspx?n=A&z=13&x=1", timeout=20)
html = r.text
print(f"Status: {r.status_code} | Tamaño: {len(html):,}")

# Buscar TODOS los patrones de links posibles
all_hrefs = re.findall(r'href=["\']([^"\']+)["\']', html)
print(f"\nTotal hrefs en la página: {len(all_hrefs)}")

# Filtrar los que parecen anuncios
anuncio_links = [h for h in all_hrefs if
    re.search(r'CW\d+', h, re.IGNORECASE) or
    re.search(r'ALQUILER', h, re.IGNORECASE) or
    re.search(r'/[A-Z][A-Z_]{5,}', h) or
    re.search(r'ficha|aviso|propiedad|inmueble', h, re.IGNORECASE)
]
print(f"Links que parecen anuncios: {len(anuncio_links)}")
for l in anuncio_links[:10]:
    print(f"  -> {l}")

# Buscar precios con patrones correctos
precios = re.findall(r'(?:U\$S|USD|\$)\s*[\d.,]+', html)
print(f"\nPrecios encontrados: {len(precios)}")
for p in precios[:10]:
    print(f"  -> {p}")

# Buscar clases CSS que podrían contener items
clases_interesantes = set(re.findall(r'class=["\']([^"\']*(?:result|item|prop|aviso|ficha|card|listing)[^"\']*)["\']', html, re.IGNORECASE))
print(f"\nClases CSS relevantes: {list(clases_interesantes)[:15]}")

# Imprimir sección del HTML donde aparece el primer precio
idx = html.find("$28.000")
if idx > 0:
    print(f"\n--- Contexto alrededor del precio $28.000 ---")
    print(html[max(0,idx-300):idx+300])

# ── GALLITO: probar cloudscraper ──────────────────────────
print("\n" + "="*55)
print("GALLITO — probando cloudscraper")
print("="*55)
try:
    import cloudscraper
    scraper = cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "windows", "desktop": True}
    )
    r2 = scraper.get(
        "https://www.gallito.com.uy/inmuebles/apartamentos/alquiler/montevideo",
        timeout=30
    )
    print(f"Status: {r2.status_code} | Tamaño: {len(r2.text):,}")
    if r2.status_code == 200 and len(r2.text) > 10000:
        gal_links = re.findall(r'href="([^"]*inmuebles-\d+[^"]*)"', r2.text)
        print(f"Links de anuncios Gallito: {len(gal_links)}")
        for l in gal_links[:5]:
            print(f"  -> {l}")
        precios_gal = re.findall(r'(?:U\$S|USD|\$)\s*[\d.,]+', r2.text)
        print(f"Precios: {len(precios_gal)}")
        # Guardar para inspección
        with open("gallito_cloudscraper.html","w",encoding="utf-8",errors="replace") as f:
            f.write(r2.text)
        print("HTML guardado: gallito_cloudscraper.html")
    else:
        print("Cloudflare sigue bloqueando o respuesta muy corta")
        print(r2.text[:400])
except ImportError:
    print("cloudscraper NO instalado — instalando...")
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "cloudscraper"])
    print("Instalado! Volvé a correr el diagnóstico.")
except Exception as e:
    print(f"Error con cloudscraper: {e}")
