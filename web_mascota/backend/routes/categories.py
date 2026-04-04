# ─── backend/routes/categories.py ──────────────────────
from flask import Blueprint, jsonify
import json, os

categories_bp = Blueprint("categories", __name__)
DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/categories.json")

@categories_bp.route("/", methods=["GET"])
def get_categories():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return jsonify(data)


# ─── backend/data/categories.json ──────────────────────
# (guardar como archivo JSON separado)
CATEGORIES_JSON = """
[
  {
    "id": "perros",
    "name": "Perros",
    "subtitle": "Alimentos y accesorios",
    "emoji": "🐶",
    "bg": "#fffae8"
  },
  {
    "id": "gatos",
    "name": "Gatos",
    "subtitle": "Todo para tu gato",
    "emoji": "🐱",
    "bg": "#e8f2ff"
  },
  {
    "id": "roedores",
    "name": "Aves y Roedores",
    "subtitle": "Conejos, hámsters, aves",
    "emoji": "🐹",
    "bg": "#e8f8ef"
  },
  {
    "id": "acuario",
    "name": "Acuario",
    "subtitle": "Peces, filtros, plantas",
    "emoji": "🐠",
    "bg": "#e6f5ff"
  },
  {
    "id": "sanitaria",
    "name": "Sanitaria",
    "subtitle": "Arena y bandeja",
    "emoji": "🐾",
    "bg": "#f5f0ff"
  },
  {
    "id": "shampoo",
    "name": "Higiene",
    "subtitle": "Shampoo y cuidado",
    "emoji": "🛁",
    "bg": "#e8fff0"
  },
  {
    "id": "educadores",
    "name": "Educadores",
    "subtitle": "Collares y clickers",
    "emoji": "🎓",
    "bg": "#fff0e8"
  }
]
"""
