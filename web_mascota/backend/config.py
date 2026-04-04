import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Config:
    # Clave secreta para sesiones y JWT
    SECRET_KEY = os.environ.get("SECRET_KEY", "petnest-secret-key-cambiar-en-produccion")

    # Rutas a archivos de datos
    DATA_DIR      = os.path.join(BASE_DIR, "data")
    PRODUCTS_FILE = os.path.join(DATA_DIR, "products.json")
    CATEGORIES_FILE = os.path.join(DATA_DIR, "categories.json")
    USERS_FILE    = os.path.join(DATA_DIR, "users.json")

    # CORS — orígenes permitidos
    CORS_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Puerto del servidor
    PORT  = int(os.environ.get("PORT", 5000))
    DEBUG = os.environ.get("DEBUG", "true").lower() == "true"


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.environ.get("SECRET_KEY")  # obligatorio en producción


# Configuración activa según variable de entorno
config = {
    "development": DevelopmentConfig,
    "production":  ProductionConfig,
    "default":     DevelopmentConfig,
}

active_config = config[os.environ.get("FLASK_ENV", "default")]
