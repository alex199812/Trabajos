import { getCurrentUser, logout } from './api.js';
import { getCart }                from './cart.js';

// ── Navegación entre páginas ───────────────────────────
export function navigate(path) {
  window.location.href = path;
}

// ── Marcar ncat activo ─────────────────────────────────
export function setActiveNav(id) {
  document.querySelectorAll('.ncat').forEach(b => b.classList.remove('active'));
  const btn = document.querySelector(`.ncat[data-page="${id}"]`);
  if (btn) btn.classList.add('active');
}

// ── SVG del logo (mismo que index.html) ───────────────
const LOGO_SVG = `<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><circle cx="50" cy="50" r="48" fill="#d8eaf4" stroke="#1a4080" stroke-width="3"/><ellipse cx="33" cy="68" rx="15" ry="20" fill="#f5c040"/><circle cx="28" cy="38" r="13" fill="#f5c040"/><ellipse cx="20" cy="34" rx="5" ry="9" fill="#e8a820" transform="rotate(-20 20 34)"/><circle cx="24" cy="35" r="1.8" fill="#1a2b3c"/><ellipse cx="20" cy="45" rx="2" ry="1.2" fill="#1a2b3c"/><rect x="40" y="55" width="8" height="13" rx="4" fill="#f5c040"/><ellipse cx="68" cy="66" rx="13" ry="17" fill="#8fb0c0"/><circle cx="70" cy="44" r="11" fill="#8fb0c0"/><polygon points="63,37 60,27 67,34" fill="#8fb0c0"/><polygon points="77,37 80,27 73,34" fill="#8fb0c0"/><polygon points="63,36 61,28 67,33" fill="#c8dde8"/><polygon points="77,36 79,28 73,33" fill="#c8dde8"/><circle cx="74" cy="43" r="1.5" fill="#1a2b3c"/><circle cx="66" cy="43" r="1.5" fill="#1a2b3c"/><polygon points="70,47 68.5,49 71.5,49" fill="#d07080"/><line x1="71" y1="49" x2="82" y2="47" stroke="#1a2b3c" stroke-width=".8"/><line x1="71" y1="51" x2="82" y2="52" stroke="#1a2b3c" stroke-width=".8"/><line x1="69" y1="49" x2="58" y2="47" stroke="#1a2b3c" stroke-width=".8"/><line x1="69" y1="51" x2="58" y2="52" stroke="#1a2b3c" stroke-width=".8"/><path d="M79 79 Q93 68 87 54" stroke="#8fb0c0" stroke-width="4.5" fill="none" stroke-linecap="round"/></svg>`;

// ── Renderizar HEADER ──────────────────────────────────
export function renderHeader(activePage = 'home') {
  const user = getCurrentUser();
  const cartCount = getCart().reduce((s, i) => s + i.qty, 0);

  const nav = [
    { id: 'home',         label: '🏠 Inicio',          href: '/index.html' },
    { id: 'nuevo',        label: '✨ Novedades',        href: '/catalog.html?tag=nuevo' },
    { id: 'descuentos',   label: '🔥 Descuentos',       href: '/catalog.html?tag=descuentos' },
    { id: 'catalog',      label: '🛍️ Catálogo',         href: '/catalog.html' },
    { id: 'perros',       label: '🐶 Perros',           href: '/catalog.html?category=perros' },
    { id: 'gatos',        label: '🐱 Gatos',            href: '/catalog.html?category=gatos' },
    { id: 'roedores',     label: '🐹 Aves y Roedores',  href: '/catalog.html?category=roedores' },
    { id: 'acuario',      label: '🐠 Acuario',          href: '/catalog.html?category=acuario' },
    { id: 'shampoo',      label: '🛁 Higiene',          href: '/catalog.html?category=shampoo' },
    { id: 'educadores',   label: '🎓 Educadores',       href: '/catalog.html?category=educadores' },
  ];

  const headerEl = document.getElementById('main-header');
  if (!headerEl) return;

  headerEl.innerHTML = `
    <header>
      <div class="htop">
        <a class="logo" href="/index.html">
          <div class="logo-icon">${LOGO_SVG}</div>
          <span class="logo-name">PetNest UY</span>
        </a>
        <div class="hsearch">
          <svg class="hsearch-ico" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#888" stroke-width="2.2">
            <circle cx="11" cy="11" r="7"/><path d="m21 21-4.35-4.35"/>
          </svg>
          <input type="search" id="globalSearch" placeholder="Buscar productos…">
        </div>
        <div class="hacts">
          <button class="hbtn" id="loginBtn">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
            </svg>
            <span>${user ? user.name.split(' ')[0] : 'Mi cuenta'}</span>
          </button>
          <button class="hbtn hcart" id="cartBtn" onclick="window.location.href='/cart.html'">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
              <path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/>
              <line x1="3" y1="6" x2="21" y2="6"/>
              <path d="M16 10a4 4 0 0 1-8 0"/>
            </svg>
            <span class="cart-count" id="cartCount">${cartCount}</span>
          </button>
        </div>
      </div>
      <nav class="hnav">
        ${nav.map(n => `
          <a class="ncat ${n.id === activePage ? 'active' : ''}" href="${n.href}" data-page="${n.id}">
            ${n.label}
          </a>`).join('')}
      </nav>
    </header>
  `;

  // Búsqueda global
  document.getElementById('globalSearch').addEventListener('keydown', e => {
    if (e.key === 'Enter') {
      const q = e.target.value.trim();
      if (q) navigate(`/catalog.html?search=${encodeURIComponent(q)}`);
    }
  });

  // Login / logout
  document.getElementById('loginBtn').addEventListener('click', () => {
    if (user) {
      logout();
    } else {
      navigate('/login.html');
    }
  });
}

// ── Renderizar FOOTER ──────────────────────────────────
export function renderFooter() {
  const footerEl = document.getElementById('main-footer');
  if (!footerEl) return;

  footerEl.innerHTML = `
    <footer>
      <div class="ft-brand">
        <div class="ft-logo">🐾 PetNest UY</div>
        <p class="ft-desc">Tu tienda de mascotas de confianza en Uruguay.</p>
        <div class="ft-contact">
          <div class="ft-ci">
            <div class="ft-ico" style="background:rgba(37,99,196,.4)">
              <svg viewBox="0 0 24 24" stroke="#7ab4f5" fill="none" stroke-width="2.2">
                <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.72 9.79 19.79 19.79 0 0 1 1.7 1.22 2 2 0 0 1 3.68 0h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L7.91 7.91a16 16 0 0 0 6.08 6.08l1.01-1.02a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/>
              </svg>
            </div>
            <span>+598 099 000 000</span>
          </div>
          <div class="ft-ci">
            <div class="ft-ico" style="background:rgba(245,168,28,.3)">
              <svg viewBox="0 0 24 24" stroke="#ffd166" fill="none" stroke-width="2.2">
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                <polyline points="22,6 12,13 2,6"/>
              </svg>
            </div>
            <span>hola@petnestuy.com</span>
          </div>
          <div class="ft-ci">
            <div class="ft-ico" style="background:rgba(100,200,150,.25)">
              <svg viewBox="0 0 24 24" stroke="#7acfa0" fill="none" stroke-width="2.2">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                <circle cx="12" cy="10" r="3"/>
              </svg>
            </div>
            <span>Montevideo, Uruguay</span>
          </div>
        </div>
        <div class="ft-social">
          <div class="ft-sb"><svg viewBox="0 0 24 24"><path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/></svg></div>
          <div class="ft-sb"><svg viewBox="0 0 24 24"><rect x="2" y="2" width="20" height="20" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1.2" fill="#fff" stroke="none"/></svg></div>
          <div class="ft-sb"><svg viewBox="0 0 24 24"><path d="M9 12a4 4 0 1 0 4 4V4a5 5 0 0 0 5 5"/></svg></div>
          <div class="ft-sb"><svg viewBox="0 0 24 24"><path d="M22.54 6.42a2.78 2.78 0 0 0-1.95-1.96C18.88 4 12 4 12 4s-6.88 0-8.59.46A2.78 2.78 0 0 0 1.46 6.42 29 29 0 0 0 1 12a29 29 0 0 0 .46 5.58A2.78 2.78 0 0 0 3.41 19.6C5.12 20 12 20 12 20s6.88 0 8.59-.46a2.78 2.78 0 0 0 1.96-1.96A29 29 0 0 0 23 12a29 29 0 0 0-.46-5.58z"/><polygon points="9.75,15.02 15.5,12 9.75,8.98" fill="#fff" stroke="none"/></svg></div>
          <div class="ft-sb"><svg viewBox="0 0 24 24"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg></div>
        </div>
      </div>
      <div class="ft-cols">
        <div class="ft-col"><h4>Tienda</h4><ul>
          <li><a href="/catalog.html">Catálogo</a></li>
          <li><a href="/catalog.html?tag=descuentos">Descuentos</a></li>
          <li><a href="/catalog.html?tag=nuevo">Novedades</a></li>
          <li>Mercado Libre</li><li>Marcas</li>
        </ul></div>
        <div class="ft-col"><h4>Mascotas</h4><ul>
          <li><a href="/catalog.html?category=perros">Perros</a></li>
          <li><a href="/catalog.html?category=gatos">Gatos</a></li>
          <li><a href="/catalog.html?category=roedores">Aves y Roedores</a></li>
          <li><a href="/catalog.html?category=acuario">Acuario</a></li>
          <li><a href="/catalog.html?category=sanitaria">Sanitaria</a></li>
        </ul></div>
        <div class="ft-col"><h4>Ayuda</h4><ul>
          <li>Cómo comprar</li><li>Envíos</li>
          <li>Devoluciones</li><li>Preguntas</li><li>Contacto</li>
        </ul></div>
      </div>
      <div class="ft-bot">
        <span class="ft-copy">© 2025 PetNest UY</span>
        <div class="ft-pays">
          <span class="ft-pay">VISA</span>
          <span class="ft-pay">MasterCard</span>
          <span class="ft-pay">MercadoPago</span>
          <span class="ft-pay">Abitab</span>
        </div>
      </div>
    </footer>
  `;
}

// ── Toast global ───────────────────────────────────────
export function showToast(msg, type = 'success') {
  let t = document.getElementById('global-toast');
  if (!t) {
    t = document.createElement('div');
    t.id = 'global-toast';
    t.className = 'toast';
    document.body.appendChild(t);
  }
  t.textContent = msg;
  t.className = `toast ${type}`;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 3200);
}

// ── Actualizar contador carrito ────────────────────────
export function updateCartBadge() {
  const el = document.getElementById('cartCount');
  if (!el) return;
  el.textContent = getCart().reduce((s, i) => s + i.qty, 0);
  el.classList.remove('bump');
  void el.offsetWidth; // forzar reflow para reiniciar la animación
  el.classList.add('bump');
  el.addEventListener('animationend', () => el.classList.remove('bump'), { once: true });
}