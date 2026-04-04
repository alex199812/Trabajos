from flask import Blueprint, jsonify, request
import json, os, hashlib, uuid
from datetime import datetime

auth_bp = Blueprint("auth", __name__)

USERS_PATH = os.path.join(os.path.dirname(__file__), "../data/users.json")

def load_users():
    if not os.path.exists(USERS_PATH):
        return []
    with open(USERS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_PATH, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# POST /api/auth/register
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    name     = data.get("name", "").strip()
    email    = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not name or not email or not password:
        return jsonify({"error": "Todos los campos son obligatorios"}), 400
    if len(password) < 6:
        return jsonify({"error": "La contraseña debe tener al menos 6 caracteres"}), 400

    users = load_users()
    if any(u["email"] == email for u in users):
        return jsonify({"error": "El email ya está registrado"}), 409

    new_user = {
        "id":         str(uuid.uuid4()),
        "name":       name,
        "email":      email,
        "password":   hash_password(password),
        "created_at": datetime.now().isoformat()
    }
    users.append(new_user)
    save_users(users)

    return jsonify({
        "message": "Usuario registrado correctamente",
        "user": {"id": new_user["id"], "name": name, "email": email}
    }), 201

# POST /api/auth/login
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email    = data.get("email", "").strip().lower()
    password = data.get("password", "")

    users = load_users()
    user = next((u for u in users if u["email"] == email), None)

    if not user or user["password"] != hash_password(password):
        return jsonify({"error": "Email o contraseña incorrectos"}), 401

    return jsonify({
        "message": "Login exitoso",
        "user": {"id": user["id"], "name": user["name"], "email": user["email"]}
    })
