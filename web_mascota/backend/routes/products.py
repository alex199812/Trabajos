from flask import Blueprint, jsonify, request
import json, os

products_bp = Blueprint("products", __name__)

DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/products.json")

def load_products():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# GET /api/products — todos los productos (con filtros opcionales)
@products_bp.route("/", methods=["GET"])
def get_products():
    products = load_products()
    category = request.args.get("category")
    tag      = request.args.get("tag")
    search   = request.args.get("search", "").lower()

    if category:
        products = [p for p in products if p["category"] == category]
    if tag:
        products = [p for p in products if tag in p.get("tags", [])]
    if search:
        products = [p for p in products if search in p["name"].lower()]

    return jsonify({"total": len(products), "products": products})

# GET /api/products/<id> — producto individual
@products_bp.route("/<int:product_id>", methods=["GET"])
def get_product(product_id):
    products = load_products()
    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        return jsonify({"error": "Producto no encontrado"}), 404
    return jsonify(product)

# GET /api/products/discounts — productos con descuento
@products_bp.route("/discounts", methods=["GET"])
def get_discounts():
    products = load_products()
    discounts = [p for p in products if p.get("old_price")]
    return jsonify({"total": len(discounts), "products": discounts})

# GET /api/products/new — productos nuevos
@products_bp.route("/new", methods=["GET"])
def get_new():
    products = load_products()
    new_products = [p for p in products if "nuevo" in p.get("tags", [])]
    return jsonify({"total": len(new_products), "products": new_products})
