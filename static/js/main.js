/**
 * DigiSahay Frontend - Vanilla JavaScript
 * Handles responsive navigation drawer, multi-lingual i18n translation, and accessible UI interactions.
 */

(function () {
  'use strict';

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
  } else {
    initApp();
  }

  function initApp() {
    initMobileNavigation();
    initLanguageSwitcher();
    initAuthStatus();
  }

  /**
   * Apply language translations across the document
   */
  function applyLanguage(lang) {
    const translations = window.DIGISAHAY_TRANSLATIONS || (typeof DIGISAHAY_TRANSLATIONS !== 'undefined' ? DIGISAHAY_TRANSLATIONS : null);
    if (!translations) {
      console.warn('DigiSahay: Translations dictionary not loaded yet.');
      return;
    }

    const dict = translations[lang] || translations['en'];
    if (!dict) return;

    document.documentElement.setAttribute('lang', lang);
    localStorage.setItem('digisahay_lang', lang);

    // Update buttons in all .lang-switcher containers
    document.querySelectorAll('.lang-switcher .lang-btn').forEach(function (btn) {
      if (btn.getAttribute('data-lang') === lang) {
        btn.classList.add('active');
        btn.setAttribute('aria-pressed', 'true');
      } else {
        btn.classList.remove('active');
        btn.setAttribute('aria-pressed', 'false');
      }
    });

    // Translate elements with data-i18n (plain text)
    document.querySelectorAll('[data-i18n]').forEach(function (el) {
      const key = el.getAttribute('data-i18n');
      if (dict[key] !== undefined) {
        el.textContent = dict[key];
      }
    });

    // Translate elements with data-i18n-html (preserves markup)
    document.querySelectorAll('[data-i18n-html]').forEach(function (el) {
      const key = el.getAttribute('data-i18n-html');
      if (dict[key] !== undefined) {
        el.innerHTML = dict[key];
      }
    });

    // Translate placeholder attributes
    document.querySelectorAll('[data-i18n-placeholder]').forEach(function (el) {
      const key = el.getAttribute('data-i18n-placeholder');
      if (dict[key] !== undefined) {
        el.setAttribute('placeholder', dict[key]);
      }
    });

    // Update guest header profile meta if not signed in
    const token = localStorage.getItem('digisahay_jwt');
    if (!token) {
      const pName = document.getElementById('headerProfileName');
      const pMeta = document.getElementById('headerProfileMeta');
      if (pName && dict.header_profile_guest) pName.textContent = dict.header_profile_guest;
      if (pMeta && dict.header_profile_meta_guest) pMeta.textContent = dict.header_profile_meta_guest;
    }

    // Dispatch global event for custom page handlers
    window.dispatchEvent(new CustomEvent('digisahay:langChange', { detail: { lang: lang, dict: dict } }));
  }

  window.changeDigiSahayLanguage = applyLanguage;

  /**
   * Multi-lingual Language Selector (English / हिन्दी / ગુજરાતી)
   */
  function initLanguageSwitcher() {
    const savedLang = localStorage.getItem('digisahay_lang') || 'en';
    applyLanguage(savedLang);

    // Attach click events to all lang buttons across desktop header & mobile drawer
    document.querySelectorAll('.lang-switcher .lang-btn').forEach(function (btn) {
      btn.addEventListener('click', function () {
        const lang = this.getAttribute('data-lang');
        if (lang) {
          applyLanguage(lang);
        }
      });
    });
  }

<<<<<<< HEAD
  function logoutCitizen() {
    localStorage.removeItem('digisahay_jwt');
    localStorage.removeItem('digisahay_user');
    window.location.href = '/logout';
  }
  window.logoutCitizen = logoutCitizen;

  /**
   * Sync Authenticated Citizen Profile in Header and Sidebar
=======
  /**
   * Sync Authenticated Citizen Profile in Header
>>>>>>> c981506dbd2f314e63b7e90f4ab444ee1eca2d2c
   */
  function initAuthStatus() {
    const token = localStorage.getItem('digisahay_jwt');
    const userJson = localStorage.getItem('digisahay_user');
    const nameEl = document.getElementById('headerProfileName');
    const metaEl = document.getElementById('headerProfileMeta');
<<<<<<< HEAD
    const linkEl = document.getElementById('headerProfileLink');
=======
>>>>>>> c981506dbd2f314e63b7e90f4ab444ee1eca2d2c

    if (token && userJson && nameEl && metaEl) {
      try {
        const user = JSON.parse(userJson);
        nameEl.textContent = user.email.split('@')[0];
        const currentLang = localStorage.getItem('digisahay_lang') || 'en';
        const dict = (window.DIGISAHAY_TRANSLATIONS && window.DIGISAHAY_TRANSLATIONS[currentLang]) || {};
        metaEl.textContent = dict.header_profile_meta_signed_in || 'Citizen Account • સક્રિય';
<<<<<<< HEAD
        if (linkEl) {
          linkEl.href = '/profile';
          linkEl.title = 'View Citizen Profile';
        }

        document.querySelectorAll('a[href="/auth"]').forEach(function(el) {
          if (el.classList.contains('sidebar-link')) {
            el.href = 'javascript:void(0)';
            el.onclick = logoutCitizen;
            el.innerHTML = '<span class="material-symbols-outlined">logout</span><span>Sign Out / બહાર નીકળો</span>';
          }
        });
=======
>>>>>>> c981506dbd2f314e63b7e90f4ab444ee1eca2d2c
      } catch (e) {}
    }
  }

  /**
   * Mobile Slide-out Drawer & Overlay Interactions
   */
  function initMobileNavigation() {
    const menuTrigger = document.getElementById('mobileMenuTrigger');
    const drawer = document.getElementById('mobileDrawer');
    const backdrop = document.getElementById('mobileBackdrop');
    const closeBtn = document.getElementById('mobileDrawerClose');

    if (!menuTrigger || !drawer || !backdrop) {
      return;
    }

    function openDrawer() {
      drawer.classList.add('open');
      backdrop.classList.add('open');
      document.body.style.overflow = 'hidden';
      drawer.setAttribute('aria-hidden', 'false');
      menuTrigger.setAttribute('aria-expanded', 'true');
    }

    function closeDrawer() {
      drawer.classList.remove('open');
      backdrop.classList.remove('open');
      document.body.style.overflow = '';
      drawer.setAttribute('aria-hidden', 'true');
      menuTrigger.setAttribute('aria-expanded', 'false');
    }

    menuTrigger.addEventListener('click', openDrawer);

    if (closeBtn) {
      closeBtn.addEventListener('click', closeDrawer);
    }

    backdrop.addEventListener('click', closeDrawer);

    // Close on Escape key
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && drawer.classList.contains('open')) {
        closeDrawer();
      }
    });

    // Close drawer when a link inside the drawer is clicked
    const drawerLinks = drawer.querySelectorAll('.sidebar-link');
    drawerLinks.forEach(function (link) {
      link.addEventListener('click', function () {
        closeDrawer();
      });
    });
  }

})();
