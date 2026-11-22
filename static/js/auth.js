/**
 * DigiSahay Dedicated Authentication Portal Controller
 */

document.addEventListener('DOMContentLoaded', initAuthPortal);

function initAuthPortal() {
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get('expired') === '1') {
    localStorage.removeItem('digisahay_jwt');
    localStorage.removeItem('digisahay_user');
    showNotice('Your session has expired due to inactivity. Please sign in again to continue.', 'warn');
  } else if (urlParams.get('logged_out') === '1') {
    localStorage.removeItem('digisahay_jwt');
    localStorage.removeItem('digisahay_user');
    showNotice('You have been signed out successfully.', 'info');
  } else if (urlParams.get('next')) {
    showNotice('Please sign in to access that protected citizen page.', 'info');
  }

  if (urlParams.get('tab') === 'register') {
    switchAuthTab('register');
  }
}

function showNotice(msg, type) {
  const el = document.getElementById('systemNotice');
  if (!el) return;
  el.style.display = 'block';
  if (type === 'warn') {
    el.style.background = '#fffbeb';
    el.style.border = '1px solid #fde68a';
    el.style.color = '#92400e';
  } else {
    el.style.background = '#eff6ff';
    el.style.border = '1px solid #bfdbfe';
    el.style.color = '#1e40af';
  }
  el.textContent = msg;
}

function switchAuthTab(tab) {
  const loginForm = document.getElementById('loginForm');
  const regForm = document.getElementById('registerForm');
  const loginBtn = document.getElementById('tabLoginBtn');
  const regBtn = document.getElementById('tabRegisterBtn');
  clearAlert();

  if (tab === 'login') {
    if (loginForm) loginForm.style.display = 'flex';
    if (regForm) regForm.style.display = 'none';
    if (loginBtn) loginBtn.classList.add('active');
    if (regBtn) regBtn.classList.remove('active');
  } else {
    if (loginForm) loginForm.style.display = 'none';
    if (regForm) regForm.style.display = 'flex';
    if (regBtn) regBtn.classList.add('active');
    if (loginBtn) loginBtn.classList.remove('active');
  }
}

function showAlert(msg, isError) {
  const al = document.getElementById('authAlert');
  if (!al) return;
  al.style.display = 'block';
  al.style.backgroundColor = isError ? 'var(--color-error-bg, #fef2f2)' : 'var(--color-green-bg, #f0fdf4)';
  al.style.border = isError ? '1px solid var(--color-error-border, #fecaca)' : '1px solid var(--color-green-border, #bbf7d0)';
  al.style.color = isError ? 'var(--color-error-text, #b91c1c)' : 'var(--color-green-text, #138808)';
  al.textContent = msg;
}

function clearAlert() {
  const al = document.getElementById('authAlert');
  if (al) al.style.display = 'none';
}

async function handleLogin(e) {
  e.preventDefault();
  clearAlert();
  const btn = document.getElementById('loginSubmitBtn');
  btn.disabled = true;
  btn.innerHTML = '<span class="material-symbols-outlined" style="font-size: 20px; animation: spin 1s linear infinite;">sync</span> Signing in...';

  const email = document.getElementById('loginEmail').value.trim();
  const password = document.getElementById('loginPassword').value;

  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await res.json();

    if (res.ok && data.success) {
      localStorage.setItem('digisahay_jwt', data.access_token);
      localStorage.setItem('digisahay_user', JSON.stringify(data.user));
      showAlert('Login successful! Redirecting to DigiSahay...', false);

      const urlParams = new URLSearchParams(window.location.search);
      const nextTarget = urlParams.get('next');
      const dest = (nextTarget && nextTarget.startsWith('/') && !nextTarget.startsWith('//')) ? nextTarget : '/dashboard';

      setTimeout(() => {
        window.location.href = dest;
      }, 400);
    } else {
      showAlert(data.message || 'Invalid email or password', true);
    }
  } catch (err) {
    showAlert('Unable to reach authentication server. Please try again.', true);
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<span class="material-symbols-outlined" style="font-size: 20px;">login</span> <span>Sign In to DigiSahay</span>';
  }
}

async function handleRegister(e) {
  e.preventDefault();
  clearAlert();
  const btn = document.getElementById('registerSubmitBtn');
  btn.disabled = true;
  btn.innerHTML = '<span class="material-symbols-outlined" style="font-size: 20px; animation: spin 1s linear infinite;">sync</span> Creating account...';

  const email = document.getElementById('regEmail').value.trim();
  const password = document.getElementById('regPassword').value;
  const preferred_language = document.getElementById('regLang').value;

  try {
    const res = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, preferred_language })
    });
    const data = await res.json();

    if (res.ok && data.success) {
      showAlert('Account registered successfully! Please sign in with your credentials.', false);
      switchAuthTab('login');
      document.getElementById('loginEmail').value = email;
      document.getElementById('loginPassword').value = '';
    } else {
      showAlert(data.message || 'Registration failed', true);
    }
  } catch (err) {
    showAlert('Unable to reach server. Please try again.', true);
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<span class="material-symbols-outlined" style="font-size: 20px;">person_add</span> <span>Create DigiSahay Account</span>';
  }
}
