const API_BASE = "http://localhost:5000/api";

// ── Productos ──────────────────────────────────────────

export async function getProducts(filters = {}) {
  const params = new URLSearchParams(filters);
  const res = await fetch(`${API_BASE}/products/?${params}`);
  if (!res.ok) throw new Error("Error al obtener productos");
  return res.json();
}

export async function getProduct(id) {
  const res = await fetch(`${API_BASE}/products/${id}`);
  if (!res.ok) throw new Error("Producto no encontrado");
  return res.json();
}

export async function getDiscounts() {
  const res = await fetch(`${API_BASE}/products/discounts`);
  return res.json();
}

export async function getNewProducts() {
  const res = await fetch(`${API_BASE}/products/new`);
  return res.json();
}

// ── Categorías ─────────────────────────────────────────

export async function getCategories() {
  const res = await fetch(`${API_BASE}/categories/`);
  return res.json();
}

// ── Autenticación ──────────────────────────────────────

export async function login(email, password) {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Error al iniciar sesión");
  // Guardar sesión en localStorage
  localStorage.setItem("petnest_user", JSON.stringify(data.user));
  return data;
}

export async function register(name, email, password) {
  const res = await fetch(`${API_BASE}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, email, password }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Error al registrarse");
  return data;
}

export function logout() {
  localStorage.removeItem("petnest_user");
  window.location.href = "/index.html";
}

export function getCurrentUser() {
  const u = localStorage.getItem("petnest_user");
  return u ? JSON.parse(u) : null;
}
