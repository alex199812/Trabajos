from flask import Flask, send_from_directory
from flask_cors import CORS
from config import active_config
from routes.products import products_bp
from routes.auth import auth_bp
from routes.categories import categories_bp
import os

app = Flask(
    __name__,
    static_folder=os.path.join(os.path.dirname(__file__), "../frontend"),
    static_url_path=""
)
app.config.from_object(active_config)
CORS(app, origins=active_config.CORS_ORIGINS)

# API routes
app.register_blueprint(products_bp,  url_prefix="/api/products")
app.register_blueprint(auth_bp,       url_prefix="/api/auth")
app.register_blueprint(categories_bp, url_prefix="/api/categories")

# Sirve el frontend en la raíz
@app.route("/")
@app.route("/<path:path>")
def serve_frontend(path="index.html"):
    frontend_dir = os.path.join(os.path.dirname(__file__), "../frontend")
    # Si existe el archivo pedido, lo sirve; si no, devuelve index.html
    if path != "" and os.path.exists(os.path.join(frontend_dir, path)):
        return send_from_directory(frontend_dir, path)
    return send_from_directory(frontend_dir, "index.html")

@app.route("/status")
def status():
    return {"status": "ok", "app": "PetNest UY API", "version": "1.0"}

if __name__ == "__main__":
    app.run(debug=active_config.DEBUG, port=active_config.PORT)

