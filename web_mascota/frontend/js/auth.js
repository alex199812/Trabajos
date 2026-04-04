import { login, register } from './api.js';
import { showToast }       from './main.js';

let isRegMode = false;

export function initAuth() {
  const card      = document.getElementById('authCard');
  const switchBtn = document.getElementById('authSwitch');
  const submitBtn = document.getElementById('authSubmit');
  const extraFld  = document.getElementById('authExtra');
  const forgotLnk = document.getElementById('forgotLink');
  const formTitle = document.getElementById('authTitle');
  const panelTtl  = document.getElementById('panelTitle');
  const panelTxt  = document.getElementById('panelText');
  const errMsg    = document.getElementById('authError');

  if (!card) return;

  // Toggle login ↔ registro
  switchBtn.addEventListener('click', () => {
    isRegMode = !isRegMode;
    card.classList.toggle('reg-mode', isRegMode);
    formTitle.textContent   = isRegMode ? 'Crear cuenta'    : 'Iniciar sesión';
    extraFld.style.display  = isRegMode ? 'block'           : 'none';
    forgotLnk.style.display = isRegMode ? 'none'            : 'block';
    submitBtn.textContent   = isRegMode ? 'Crear cuenta'    : 'Ingresar';
    panelTtl.innerHTML      = isRegMode ? '¡Bienvenido<br>de vuelta!' : '¡Hola,<br>amigo!';
    panelTxt.textContent    = isRegMode
      ? 'Ya tenés cuenta. Iniciá sesión para ver tus pedidos y favoritos.'
      : '¿No tenés cuenta? ¡Registrate y empezá a disfrutar de los mejores productos!';
    switchBtn.textContent   = isRegMode ? 'INICIAR SESIÓN'  : 'REGISTRARSE';
    clearError();
  });

  // Submit
  submitBtn.addEventListener('click', handleSubmit);

  // Enter en campos
  document.querySelectorAll('.auth-field input').forEach(input => {
    input.addEventListener('keydown', e => { if (e.key === 'Enter') handleSubmit(); });
  });

  async function handleSubmit() {
    clearError();
    const email    = document.getElementById('authEmail').value.trim();
    const password = document.getElementById('authPassword').value;

    if (!email || !password) { showError('Completá todos los campos.'); return; }

    submitBtn.disabled   = true;
    submitBtn.textContent = '...';

    try {
      if (isRegMode) {
        const name = document.getElementById('authName').value.trim();
        if (!name) { showError('Ingresá tu nombre.'); return; }
        await register(name, email, password);
        showToast('✅ Cuenta creada. ¡Ahora iniciá sesión!');
        switchBtn.click(); // volver a login
      } else {
        await login(email, password);
        showToast('👋 ¡Bienvenido de vuelta!');
        setTimeout(() => window.location.href = '/index.html', 800);
      }
    } catch (err) {
      showError(err.message);
    } finally {
      submitBtn.disabled    = false;
      submitBtn.textContent = isRegMode ? 'Crear cuenta' : 'Ingresar';
    }
  }

  function showError(msg) {
    if (errMsg) { errMsg.textContent = msg; errMsg.style.display = 'block'; }
  }
  function clearError() {
    if (errMsg) { errMsg.textContent = ''; errMsg.style.display = 'none'; }
  }
}
