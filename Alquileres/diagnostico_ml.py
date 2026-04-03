"""
diagnostico_ml.py v4 — prueba el solver del challenge SHA-256
"""
import re, hashlib, time, urllib.parse, requests

HEADERS = {
    "User-Agent":      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-UY,es;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Connection":      "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest":  "document",
    "Sec-Fetch-Mode":  "navigate",
    "Sec-Fetch-Site":  "none",
    "Cache-Control":   "no-cache",
}
URL     = "https://listado.mercadolibre.com.uy/inmuebles/apartamentos/alquiler/montevideo/"
DOMAIN  = "mercadolibre.com.uy"

session = requests.Session()
session.headers.update(HEADERS)

print("[1] Visitando home...")
session.get("https://www.mercadolibre.com.uy/", timeout=15)
time.sleep(1)

print("[2] Primera request (esperar challenge)...")
r = session.get(URL, timeout=25)
html = r.text
print(f"    Tamaño: {len(html)} | Challenge: {'SÍ' if '_bmstate' in html or 'verifyChallenge' in html else 'NO'}")

if '_bmstate' not in html and 'verifyChallenge' not in html:
    print("    ✅ No hay challenge — HTML directo!")
    mlu = re.findall(r'MLU-\d+', html)
    print(f"    Links MLU-: {len(mlu)}")
else:
    print("[3] Leyendo _bmstate de cookies...")
    bmstate = None
    for c in session.cookies:
        if c.name == "_bmstate":
            bmstate = urllib.parse.unquote(c.value)
            break
    print(f"    _bmstate = {bmstate}")

    if bmstate and ";" in bmstate:
        parts     = bmstate.split(";")
        token     = parts[0]
        difficulty= int(parts[1]) if len(parts) > 1 else 0
        print(f"    Token: {token[:30]}... | Dificultad: {difficulty}")

        print(f"[4] Resolviendo SHA-256 proof-of-work (dificultad={difficulty})...")
        t0      = time.time()
        prefix  = "0" * difficulty
        answer  = 0
        if difficulty > 0:
            for n in range(10_000_000):
                d = hashlib.sha256(f"{token}{n}".encode()).hexdigest()
                if d.startswith(prefix):
                    answer = n
                    break
        elapsed = time.time() - t0
        print(f"    ✅ Respuesta: {answer} (en {elapsed:.2f}s)")
        print(f"    SHA256({token[:15]}...{answer}) = {hashlib.sha256(f'{token}{answer}'.encode()).hexdigest()[:20]}...")

        print("[5] Seteando cookie _bmc y haciendo segunda request...")
        bmc = urllib.parse.quote(f"{token};{answer}")
        session.cookies.set("_bmc", bmc, domain=DOMAIN, path="/")
        time.sleep(0.5)
        session.headers.update({"Referer": "https://www.mercadolibre.com.uy/"})

        r2   = session.get(URL, timeout=25)
        html2= r2.text
        print(f"    Status: {r2.status_code} | Tamaño: {len(html2)}")
        print(f"    ¿Challenge otra vez? {'SÍ ❌' if '_bmstate' in html2 or 'verifyChallenge' in html2 else 'NO ✅'}")
        mlu2 = re.findall(r'MLU-\d+', html2)
        print(f"    Links MLU- encontrados: {len(mlu2)}")
        if mlu2:
            print(f"    Ejemplo: {mlu2[0]}")
        prices = re.findall(r'[\$]\s*[\d.]{3,}', html2)
        print(f"    Precios $: {len(prices)}")
        if prices:
            print(f"    Ejemplos: {prices[:5]}")
        # Guardar HTML
        with open("ml_debug_post_challenge.html","w",encoding="utf-8",errors="replace") as f:
            f.write(html2)
        print("    HTML guardado en ml_debug_post_challenge.html")
    else:
        print("    ❌ No se pudo leer _bmstate")
