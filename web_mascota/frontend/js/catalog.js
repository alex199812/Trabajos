import { getCart, saveCart } from './cart.js';
import { showToast, updateCartBadge } from './main.js';
import { filterProducts } from './data.js';

// ── SVGs de animales (por categoría) ─────────────────
const CAT_SVG = {
  perros:     `<svg viewBox="0 0 80 80"><ellipse cx="40" cy="55" rx="20" ry="18" fill="#f5c040"/><circle cx="40" cy="30" r="17" fill="#f5c040"/><ellipse cx="28" cy="26" rx="7" ry="12" fill="#e8a820" transform="rotate(-15 28 26)"/><ellipse cx="52" cy="26" rx="7" ry="12" fill="#e8a820" transform="rotate(15 52 26)"/><circle cx="34" cy="29" r="2.5" fill="#1a2b3c"/><circle cx="46" cy="29" r="2.5" fill="#1a2b3c"/><ellipse cx="40" cy="35" rx="3.5" ry="2" fill="#c06840"/><path d="M58 60 Q68 65 64 54" stroke="#e8a820" stroke-width="4" fill="none" stroke-linecap="round"/></svg>`,
  gatos:      `<svg viewBox="0 0 80 80"><ellipse cx="40" cy="55" rx="18" ry="17" fill="#8ab0c4"/><circle cx="40" cy="30" r="16" fill="#8ab0c4"/><polygon points="26,20 22,6 34,18" fill="#8ab0c4"/><polygon points="54,20 58,6 46,18" fill="#8ab0c4"/><polygon points="27,19 24,10 33,18" fill="#c8dde8"/><polygon points="53,19 56,10 47,18" fill="#c8dde8"/><circle cx="35" cy="28" r="2" fill="#0a1830"/><circle cx="45" cy="28" r="2" fill="#0a1830"/><path d="M56 60 Q68 68 64 52" stroke="#8ab0c4" stroke-width="5" fill="none" stroke-linecap="round"/></svg>`,
  roedores:   `<svg viewBox="0 0 80 80"><ellipse cx="40" cy="55" rx="16" ry="20" fill="#4aa870"/><circle cx="40" cy="28" r="14" fill="#4aa870"/><ellipse cx="40" cy="28" rx="9" ry="14" fill="#5bc080"/><circle cx="36" cy="25" r="2.5" fill="#0a1810"/><circle cx="44" cy="25" r="2.5" fill="#0a1810"/><polygon points="40,31 37,35 43,35" fill="#e8a820"/><polygon points="14,40 28,36 22,50" fill="#4aa870"/><polygon points="66,40 52,36 58,50" fill="#4aa870"/></svg>`,
  acuario:    `<svg viewBox="0 0 80 80"><ellipse cx="38" cy="40" rx="22" ry="14" fill="#3a90d8"/><polygon points="60,40 72,28 72,52" fill="#2070b8"/><circle cx="22" cy="37" r="3.5" fill="#0a1830"/><circle cx="22.7" cy="36.5" r="1.1" fill="#fff"/><path d="M28 32 Q38 24 50 32" stroke="#5ab0f0" stroke-width="1.5" fill="none"/></svg>`,
  sanitaria:  `<svg viewBox="0 0 80 80"><ellipse cx="40" cy="55" rx="18" ry="17" fill="#b0a0d4"/><circle cx="40" cy="30" r="16" fill="#b0a0d4"/><polygon points="26,20 22,6 34,18" fill="#b0a0d4"/><polygon points="54,20 58,6 46,18" fill="#b0a0d4"/><circle cx="35" cy="28" r="2" fill="#1a0830"/><circle cx="45" cy="28" r="2" fill="#1a0830"/></svg>`,
  shampoo:    `<svg viewBox="0 0 80 80"><rect x="28" y="20" width="24" height="36" rx="8" fill="#5bc0c0"/><rect x="34" y="14" width="12" height="8" rx="4" fill="#3a9090"/><ellipse cx="40" cy="56" rx="12" ry="4" fill="#3a9090"/><circle cx="36" cy="36" r="3" fill="rgba(255,255,255,.4)"/><circle cx="44" cy="42" r="2" fill="rgba(255,255,255,.4)"/></svg>`,
  educadores: `<svg viewBox="0 0 80 80"><rect x="20" y="30" width="40" height="25" rx="8" fill="#f5c040"/><rect x="34" y="20" width="12" height="12" rx="4" fill="#e8a820"/><circle cx="30" cy="42" r="4" fill="#1a2b3c"/><circle cx="50" cy="42" r="4" fill="#1a2b3c"/><path d="M35 52 Q40 57 45 52" stroke="#1a2b3c" stroke-width="2" fill="none" stroke-linecap="round"/></svg>`,
};

const CAT_BG = {
  perros:    'linear-gradient(145deg,#fffae8,#ffeebb)',
  gatos:     'linear-gradient(145deg,#e8f2ff,#c0d8f5)',
  roedores:  'linear-gradient(145deg,#e8f8ef,#b8e8c8)',
  acuario:   'linear-gradient(145deg,#e6f5ff,#b8dcf8)',
  sanitaria: 'linear-gradient(145deg,#f5f0ff,#ddd0f8)',
  shampoo:   'linear-gradient(145deg,#e8fff0,#b8f0d0)',
  educadores:'linear-gradient(145deg,#fff0e8,#f5d0b0)',
};

function stars(n) {
  return Array.from({length:5},(_,i) => i < n ? '★' : '☆').join('');
}

// ── Tarjeta de producto ────────────────────────────────
export function productCard(p) {
  const bg  = CAT_BG[p.category]  || 'linear-gradient(145deg,#eef2f8,#dce6f0)';
  const svg = CAT_SVG[p.category] || CAT_SVG.perros;
  const disc = p.old_price ? Math.round((1 - p.price / p.old_price) * 100) : 0;
  const badgeCls = p.badge === 'descuento' ? 'bd' : p.badge === 'nuevo' ? 'bn' : 'bb';
  const badgeTxt = p.badge === 'descuento' ? `-${disc}%`  : p.badge === 'nuevo'  ? 'NUEVO' : 'HOY';

  return `
    <article class="pc" data-id="${p.id}" data-price="${p.price}">
      <div class="pci" style="background:${bg}">
        ${p.image
          ? `<img src="${p.image}" alt="${p.name}" loading="lazy">`
          : svg}
        <span class="badge ${badgeCls}">${badgeTxt}</span>
      </div>
      <div class="pcb">
        <div class="pcat">${p.category.toUpperCase()}</div>
        <div class="pnm">${p.name}</div>
        <div class="prow">
          <div class="prices">
            ${p.old_price ? `<span class="pold">$${p.old_price.toLocaleString('es-UY')}</span>` : ''}
            <span class="pnew">$${p.price.toLocaleString('es-UY')}</span>
            ${disc ? `<span class="pdisc">-${disc}%</span>` : ''}
          </div>
          <span class="prat">${stars(p.rating || 4)}</span>
        </div>
        <div class="card-qty">
          <div class="qty-ctrl">
            <button class="qty-down" type="button">−</button>
            <span class="qty-val">1</span>
            <button class="qty-up" type="button">+</button>
          </div>
          <span class="qty-total">$${p.price.toLocaleString('es-UY')}</span>
        </div>
        <button class="padd" data-id="${p.id}">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/>
            <line x1="3" y1="6" x2="21" y2="6"/>
            <path d="M16 10a4 4 0 0 1-8 0"/>
          </svg>
          Agregar al carrito
        </button>
      </div>
    </article>`;
}

// ── Cargar y renderizar productos (datos locales) ──────
export function loadProducts(filters = {}, containerId = 'prod-grid') {
  const container = document.getElementById(containerId);
  if (!container) return;

  const products = filterProducts(filters);

  if (!products.length) {
    container.innerHTML = '<p class="no-results">Sin productos en esta categoría.</p>';
    return;
  }

  container.innerHTML = products.map(productCard).join('');
  bindAddToCart(products, containerId);
}

// ── Etiqueta flotante sobre el botón ──────────────────
function showAddLabel(btn) {
  const rect  = btn.getBoundingClientRect();
  const label = document.createElement('div');
  label.className = 'add-label';
  label.innerHTML = `
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
      <polyline points="20 6 9 17 4 12"/>
    </svg>
    ¡Agregado al carrito!`;
  label.style.left = `${rect.left + rect.width / 2}px`;
  label.style.top  = `${rect.top}px`;
  label.style.transform = 'translateX(-50%)';
  document.body.appendChild(label);
  label.addEventListener('animationend', () => label.remove(), { once: true });
}

// ── Ripple sobre el botón ──────────────────────────────
function addRipple(btn, e) {
  const rect = btn.getBoundingClientRect();
  const size = Math.max(rect.width, rect.height) * 2;
  const rpl  = document.createElement('span');
  rpl.className = 'padd-ripple';
  rpl.style.cssText = `width:${size}px;height:${size}px;left:${e.clientX - rect.left - size / 2}px;top:${e.clientY - rect.top - size / 2}px`;
  btn.appendChild(rpl);
  rpl.addEventListener('animationend', () => rpl.remove(), { once: true });
}

// ── Partícula que vuela al carrito ─────────────────────
function flyToCart(originBtn) {
  const cartBtn = document.getElementById('cartBtn');
  if (!cartBtn) return;

  const o = originBtn.getBoundingClientRect();
  const c = cartBtn.getBoundingClientRect();

  const particle = document.createElement('div');
  particle.className = 'cart-fly-particle';
  particle.textContent = '🛍️';
  particle.style.left = `${o.left + o.width / 2}px`;
  particle.style.top  = `${o.top  + o.height / 2}px`;
  particle.style.setProperty('--dx', `${(c.left + c.width / 2) - (o.left + o.width / 2)}px`);
  particle.style.setProperty('--dy', `${(c.top  + c.height / 2) - (o.top  + o.height / 2)}px`);
  document.body.appendChild(particle);

  particle.addEventListener('animationend', () => {
    particle.remove();
    cartBtn.classList.add('cart-bounce');
    cartBtn.addEventListener('animationend', () => cartBtn.classList.remove('cart-bounce'), { once: true });
  }, { once: true });
}

// ── Bind botones agregar ───────────────────────────────
function bindAddToCart(products, containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;

  // ── Controles de cantidad ──────────────────────────
  container.querySelectorAll('.qty-down').forEach(btn => {
    btn.addEventListener('click', e => {
      e.stopPropagation();
      const card    = btn.closest('.pc');
      const valEl   = card.querySelector('.qty-val');
      const totalEl = card.querySelector('.qty-total');
      const price   = parseInt(card.dataset.price);
      let v = parseInt(valEl.textContent);
      if (v > 1) {
        v--;
        valEl.textContent   = v;
        totalEl.textContent = `$${(price * v).toLocaleString('es-UY')}`;
      }
    });
  });

  container.querySelectorAll('.qty-up').forEach(btn => {
    btn.addEventListener('click', e => {
      e.stopPropagation();
      const card    = btn.closest('.pc');
      const valEl   = card.querySelector('.qty-val');
      const totalEl = card.querySelector('.qty-total');
      const price   = parseInt(card.dataset.price);
      let v = parseInt(valEl.textContent) + 1;
      valEl.textContent   = v;
      totalEl.textContent = `$${(price * v).toLocaleString('es-UY')}`;
    });
  });

  // ── Agregar al carrito (respeta qty) ──────────────
  container.querySelectorAll('.padd').forEach(btn => {
    btn.addEventListener('click', e => {
      e.stopPropagation();
      if (btn.classList.contains('added')) return;

      const id   = Number(btn.dataset.id);
      const prod = products.find(p => p.id === id);
      if (!prod) return;

      const card    = btn.closest('.pc');
      const qtySpan = card.querySelector('.qty-val');
      const qty     = qtySpan ? parseInt(qtySpan.textContent) : 1;

      // Agregar al carrito con la qty seleccionada
      const cart     = getCart();
      const existing = cart.find(i => i.id === prod.id);
      if (existing) {
        existing.qty += qty;
      } else {
        cart.push({
          id:        prod.id,
          name:      prod.name,      nm:  prod.name,
          category:  prod.category,  cat: prod.category,
          price:     prod.price,     pr:  prod.price,
          old_price: prod.old_price || null,
          badge:     prod.badge     || null,
          svg:       CAT_SVG[prod.category] || CAT_SVG.perros,
          bg:        CAT_BG[prod.category]  || '#edf2f8',
          qty,
        });
      }
      saveCart(cart);
      updateCartBadge();
      showToast(`✅ ${prod.name} agregado al carrito`);

      // Animaciones
      addRipple(btn, e);
      showAddLabel(btn);
      flyToCart(btn);

      // Botón → éxito → reset
      const originalHTML = btn.innerHTML;
      btn.classList.add('added');
      btn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg> ¡Agregado!`;
      setTimeout(() => {
        btn.classList.remove('added');
        btn.innerHTML = originalHTML;
        // Reset qty a 1
        if (qtySpan) {
          qtySpan.textContent = '1';
          card.querySelector('.qty-total').textContent = `$${prod.price.toLocaleString('es-UY')}`;
        }
      }, 1800);
    });
  });
}

// ── Leer parámetros de URL ─────────────────────────────
export function getUrlParams() {
  const p = new URLSearchParams(window.location.search);
  return {
    category: p.get('category') || '',
    tag:      p.get('tag')      || '',
    search:   p.get('search')   || '',
  };
}