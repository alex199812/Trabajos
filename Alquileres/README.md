# 🏠 Buscador de Alquileres — Montevideo v2

Búsqueda en tiempo real de alquileres en Montevideo desde **11 fuentes**:

| Grupo | Portales |
|-------|----------|
| **Portales grandes** | MercadoLibre · InfoCasas · Gallito · Casasweb · Casas y Más |
| **Inmobiliarias** | RE/MAX Uruguay · ACSA · Ciudad Inmobiliaria · Braglia · Lars |
| **Redes sociales** | Facebook Marketplace (links directos) |

---

## ✅ Requisitos

- **Python 3.9+** → https://www.python.org/downloads/

---

## 🚀 Instalación (una sola vez)

```bash
# 1. Entrar a la carpeta
cd buscador_alquileres

# 2. Crear entorno virtual (recomendado)
python -m venv .venv

# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt
```

## ▶️ Ejecutar

```bash
streamlit run app.py
```

Se abre en el navegador en **http://localhost:8501**

---

## 🎛️ Filtros disponibles

| Filtro | Descripción |
|--------|-------------|
| **Portales** | Seleccioná de cuáles fuentes buscar (checkboxes individuales) |
| **Tipo de propiedad** | Apartamentos, casas, PH, locales |
| **Barrio(s)** | Uno o varios barrios de Montevideo |
| **Dormitorios** | Rango con slider |
| **Superficie mínima** | En m² |
| **Precio de alquiler** | Rango en USD + filtro por moneda (USD/UYU) |
| **Gastos comunes máximos** | En $UYU — filtra anuncios que publiquen GC superiores |
| **Páginas por portal** | Más páginas = más resultados (tarda más) |
| **Ordenar por** | Precio, gastos, dormitorios, superficie, portal o barrio |

---

## 🔵 Facebook Marketplace

Facebook no permite scraping automático (requiere login). Al seleccionarlo, la app genera **links directos** preconfigurados con tus filtros para que los abras en tu navegador ya logueado en Facebook.

---

## 📥 Exportar

Al finalizar la búsqueda podés exportar los resultados en **CSV** o **Excel**.

---

## ⚠️ Notas

- Requiere conexión a internet.
- Los portales de inmobiliarias pequeñas (ACSA, Braglia, Lars, etc.) pueden devolver pocos o ningún resultado si cambiaron su HTML — es normal.
- Los grandes portales (MercadoLibre, InfoCasas, Gallito) son los más confiables.

---

## 📁 Estructura

```
buscador_alquileres/
├── app.py
├── config.py
├── requirements.txt
├── README.md
└── scrapers/
    ├── __init__.py
    ├── base.py              ← Clase base compartida
    ├── mercadolibre.py
    ├── infocasas.py
    ├── gallito.py
    ├── casasweb.py
    ├── casasymas.py
    ├── remax.py
    ├── agencias.py          ← ACSA, Ciudad Inmobiliaria, Braglia, Lars
    └── facebook.py          ← Generador de links de Facebook Marketplace
```
