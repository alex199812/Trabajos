const CART_KEY = 'petnest_cart';

export function getCart() {
  return JSON.parse(localStorage.getItem(CART_KEY) || '[]');
}

export function saveCart(cart) {
  localStorage.setItem(CART_KEY, JSON.stringify(cart));
}

// Limpia el SVG para que no tenga width/height absolutos inline
function sanitizeSvg(svgStr) {
  if (!svgStr) return null;
  return svgStr
    .replace(/\s+width="[^"]*"/g, ' width="100%"')
    .replace(/\s+height="[^"]*"/g, ' height="100%"');
}

export function addToCart(product) {
  const cart = getCart();
  const existing = cart.find(i => i.id === product.id);
  if (existing) {
    existing.qty += 1;
  } else {
    cart.push({
      id:        product.id,
      name:      product.name      || product.nm,
      nm:        product.name      || product.nm,
      category:  product.category  || product.cat,
      cat:       product.category  || product.cat,
      price:     product.price     || product.pr,
      pr:        product.price     || product.pr,
      old_price: product.old_price || product.old || null,
      badge:     product.badge     || product.b   || null,
      svg:       sanitizeSvg(product.svg) || null,
      bg:        product.bg  || null,
      qty: 1,
    });
  }
  saveCart(cart);
}

export function removeFromCart(productId) {
  saveCart(getCart().filter(i => i.id !== productId));
}

export function updateQty(productId, delta) {
  const cart = getCart();
  const item = cart.find(i => i.id === productId);
  if (!item) return;
  item.qty += delta;
  if (item.qty <= 0) saveCart(cart.filter(i => i.id !== productId));
  else saveCart(cart);
}

export function clearCart() {
  localStorage.removeItem(CART_KEY);
}

export function getCartTotal() {
  return getCart().reduce((sum, i) => sum + (i.price || i.pr) * i.qty, 0);
}

export function getCartCount() {
  return getCart().reduce((sum, i) => sum + i.qty, 0);
}