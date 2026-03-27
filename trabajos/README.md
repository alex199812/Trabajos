# 💼 Buscador de Empleos — Uruguay

Búsqueda en tiempo real de empleos en Uruguay desde **7 fuentes**:

| Grupo | Portales |
|-------|----------|
| **Portales grandes** | BuscoJobs · Gallito Trabajo · Computrabajo · EmpleosUruguay · Trabajo en Casa |
| **Sector público** | Vacantes (llamados estatales) |
| **Redes profesionales** | LinkedIn (links directos) |

---

## ✅ Requisitos

- **Python 3.9+** → https://www.python.org/downloads/

---

## 🚀 Instalación (una sola vez)

```bash
# 1. Entrar a la carpeta
cd buscador_empleos

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
| **Cargo / palabras clave** | Búsqueda por puesto, tecnología, habilidad |
| **Portales** | Seleccioná de cuáles fuentes buscar |
| **Localidad** | Departamento o remoto |
| **Área / Rubro** | 18 categorías laborales |
| **Modalidad** | Presencial, Remoto, Híbrido |
| **Nivel de experiencia** | Sin experiencia hasta Gerencial |
| **Jornada** | Full-time, Part-time, Freelance |
| **Páginas por portal** | Más páginas = más resultados |
| **Ordenar por** | Salario, empresa, zona, fecha, portal |

---

## 🔵 LinkedIn

LinkedIn no permite scraping automático (requiere login). Al seleccionarlo, la app genera **links directos** preconfigurados con tus filtros para que los abras en tu navegador ya logueado en LinkedIn.

---

## 📥 Exportar

Al finalizar la búsqueda podés exportar los resultados en **CSV** o **Excel**.

---

## 📁 Estructura

```
buscador_empleos/
├── app.py
├── config.py
├── requirements.txt
├── README.md
└── scrapers/
    ├── __init__.py
    ├── base.py              ← Clase base compartida
    ├── buscojobs.py
    ├── gallito.py
    ├── computrabajo.py
    ├── empleosuruguay.py
    ├── trabajoencasa.py
    ├── vacantes.py
    └── linkedin.py          ← Generador de links de LinkedIn
```
