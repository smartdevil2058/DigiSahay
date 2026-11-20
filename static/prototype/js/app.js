// ==========================================================================
// DigiSahay Prototype - Core App Logic (js/app.js)
// Handles Auth, Header/Footer Injection, Profile, Home, and Upload Docs.
// ==========================================================================

const APP = {
  // Utility: Escape HTML text to prevent XSS
  escapeHtml(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  },

  // Storage Helpers
  get(key, fallback = null) {
    try {
      const data = localStorage.getItem(key);
      return data ? JSON.parse(data) : fallback;
    } catch (e) {
      return fallback;
    }
  },
  set(key, val) {
    try {
      localStorage.setItem(key, JSON.stringify(val));
    } catch (e) {
      console.error("Storage error:", e);
    }
  },

  // Auth Guards
  isLoggedIn() {
    return localStorage.getItem("digisahay_logged_in") === "true";
  },
  requireAuth() {
    if (!this.isLoggedIn()) window.location.replace("index.html");
  },
  redirectIfLoggedIn() {
    if (this.isLoggedIn()) window.location.replace("home.html");
  },
  logout() {
    localStorage.removeItem("digisahay_logged_in");
    localStorage.removeItem("digisahay_user_email");
    window.location.replace("index.html");
  },

  // Render Persistent Header & Footer with Indian Flag Brand Identity
  renderLayout(activePage = "") {
    const headerContainer = document.getElementById("header-placeholder");
    const footerContainer = document.getElementById("footer-placeholder");
    const userEmail = APP.get("digisahay_user_email", "Citizen");

    if (headerContainer) {
      const loggedIn = this.isLoggedIn();
      headerContainer.innerHTML = `
        <div class="tricolour-stripe"></div>
        <header class="site-header">
          <div class="container header-inner">
            <a href="${loggedIn ? 'home.html' : 'index.html'}" class="brand-link" aria-label="DigiSahay Home">
              <div class="brand-chakra" aria-hidden="true">☸</div>
              <div>
                <div class="brand-title"><span class="brand-orange">Digi</span><span class="brand-green">Sahay</span></div>
                <div class="brand-sub">Citizen Assistance &amp; Document Locker &bull; भारत सरकार</div>
              </div>
            </a>
            ${loggedIn ? `
              <nav class="main-nav" aria-label="Main Navigation">
                <a href="home.html" class="nav-link ${activePage === 'home' ? 'active' : ''}">Home</a>
                <a href="home.html#upload-section" class="nav-link">Upload Docs</a>
                <a href="profile.html" class="nav-link ${activePage === 'profile' ? 'active' : ''}">Profile</a>
                <span class="badge badge-saffron" style="margin-left: 6px;">🇮🇳 ${APP.escapeHtml(userEmail)}</span>
                <button type="button" class="nav-btn-logout" onclick="APP.logout()">Logout</button>
              </nav>
            ` : `<span class="badge badge-saffron">Prototype Mode</span>`}
          </div>
        </header>`;
    }

    if (footerContainer) {
      footerContainer.innerHTML = `
        <footer class="site-footer">
          <div class="footer-line"></div>
          <div class="container">
            <p><strong>DigiSahay Prototype</strong> &bull; For First-Time Citizen Applicants (Aged 18–19)</p>
            <p style="margin-top: 6px; font-size: 12px;">Designed with Indian Flag Palette (Saffron &bull; White &bull; Green) &bull; Sample Demo Data Only</p>
          </div>
        </footer>`;
    }
  },

  // Helper: Create High-Visibility Note Box
  renderNote(type, title, text) {
    const icons = { warning: "⚠️", info: "ℹ️", success: "✅" };
    return `
      <div class="note-box note-${type}" role="region" aria-label="${APP.escapeHtml(title)}">
        <div class="note-icon" aria-hidden="true">${icons[type] || 'ℹ️'}</div>
        <div class="note-content">
          <strong>${APP.escapeHtml(title)}</strong>
          <div>${APP.escapeHtml(text)}</div>
        </div>
      </div>`;
  },

  // 1. Login Page (index.html)
  initLogin() {
    this.redirectIfLoggedIn();
    this.renderLayout("login");

    const noteBox = document.getElementById("login-biometric-note");
    if (noteBox) noteBox.innerHTML = this.renderNote("warning", "Important Statutory Notice", DIGI_DATA.BIOMETRIC_NOTE);

    const form = document.getElementById("login-form");
    if (form) {
      form.addEventListener("submit", (e) => {
        e.preventDefault();
        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value;
        if (!email || !password) {
          alert("Please enter both email and password.");
          return;
        }
        localStorage.setItem("digisahay_logged_in", "true");
        APP.set("digisahay_user_email", email);
        window.location.replace("home.html");
      });
    }
  },

  // 2. Profile Page (profile.html)
  initProfile() {
    this.requireAuth();
    this.renderLayout("profile");

    const noteBox = document.getElementById("profile-biometric-note");
    if (noteBox) noteBox.innerHTML = this.renderNote("warning", "Notice on Biometrics", DIGI_DATA.BIOMETRIC_NOTE);

    this.fillProfileForm(APP.get("digisahay_profile", {}));

    const photoInput = document.getElementById("profile-photo-input");
    const photoPreview = document.getElementById("profile-photo-preview");
    if (photoInput && photoPreview) {
      photoInput.addEventListener("change", (e) => {
        const file = e.target.files[0];
        if (file) {
          const reader = new FileReader();
          reader.onload = (event) => {
            photoPreview.src = event.target.result;
            photoPreview.alt = "Citizen photo of " + (document.getElementById("name").value || "user");
          };
          reader.readAsDataURL(file);
        }
      });
    }

    const fillBtn = document.getElementById("btn-fill-sample");
    if (fillBtn) {
      fillBtn.addEventListener("click", () => this.fillProfileForm(DIGI_DATA.SAMPLE_PROFILE));
    }

    const form = document.getElementById("profile-form");
    if (form) {
      form.addEventListener("submit", (e) => {
        e.preventDefault();
        const phone = document.getElementById("phone").value.trim();
        if (!/^[6-9]\d{9}$/.test(phone)) {
          alert("Please enter a valid 10-digit Indian mobile number starting with 6-9.");
          return;
        }

        const data = {
          name: document.getElementById("name").value.trim(),
          dob: document.getElementById("dob").value,
          gender: document.getElementById("gender").value,
          phone: phone,
          email: document.getElementById("email").value.trim(),
          photoUrl: photoPreview.src
        };

        APP.set("digisahay_profile", data);
        const msg = document.getElementById("profile-save-msg");
        if (msg) {
          msg.style.display = "block";
          setTimeout(() => { msg.style.display = "none"; }, 3500);
        }
      });
    }
  },

  fillProfileForm(data) {
    if (!data) return;
    ["name", "dob", "gender", "phone", "email"].forEach(field => {
      const el = document.getElementById(field);
      if (el && data[field]) el.value = data[field];
    });
    if (data.photoUrl) {
      const preview = document.getElementById("profile-photo-preview");
      if (preview) {
        preview.src = data.photoUrl;
        preview.alt = "Profile photo of " + (data.name || "applicant");
      }
    }
  },

  // 3. Home Page (home.html)
  initHome() {
    this.requireAuth();
    this.renderLayout("home");

    const noteBox = document.getElementById("home-biometric-note");
    if (noteBox) noteBox.innerHTML = this.renderNote("warning", "Biometric Scope Reminder", DIGI_DATA.BIOMETRIC_NOTE);

    this.renderUploadedDocs();
    this.renderDocCards();

    const uploadForm = document.getElementById("doc-upload-form");
    if (uploadForm) {
      uploadForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const typeSelect = document.getElementById("upload-doc-type");
        const fileInput = document.getElementById("upload-file-picker");
        const file = fileInput.files[0];
        if (!typeSelect.value || !file) {
          alert("Please choose a document type and select a file.");
          return;
        }

        const existing = APP.get("digisahay_uploaded_docs", []);
        existing.push({
          id: "doc_" + Date.now(),
          type: typeSelect.value,
          fileName: file.name,
          uploadedAt: new Date().toLocaleDateString("en-IN")
        });

        APP.set("digisahay_uploaded_docs", existing);
        fileInput.value = "";
        this.renderUploadedDocs();
      });
    }
  },

  renderUploadedDocs() {
    const list = document.getElementById("uploaded-docs-list");
    if (!list) return;
    const docs = APP.get("digisahay_uploaded_docs", []);
    if (docs.length === 0) {
      list.innerHTML = `<p style="color: var(--text-muted); font-size: 13px;">No documents uploaded yet. Add your 10th marksheet or identity proofs below.</p>`;
      return;
    }
    list.innerHTML = docs.map(d => `
      <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; background: var(--bg-page); border: 1px solid var(--border); border-left: 5px solid var(--green); border-radius: 8px; margin-bottom: 8px;">
        <div>
          <strong style="color: var(--navy);">${APP.escapeHtml(d.type)}</strong>
          <div style="font-size: 12px; color: var(--text-muted);">📄 ${APP.escapeHtml(d.fileName)} &bull; Uploaded: ${APP.escapeHtml(d.uploadedAt)}</div>
        </div>
        <button type="button" class="btn btn-sm btn-danger" onclick="APP.removeUploadedDoc('${d.id}')">Remove</button>
      </div>`).join("");
  },

  removeUploadedDoc(id) {
    const docs = APP.get("digisahay_uploaded_docs", []).filter(d => d.id !== id);
    APP.set("digisahay_uploaded_docs", docs);
    this.renderUploadedDocs();
  },

  // Alternating Saffron (Orange) and Green Cards for Indian Flag Theme
  renderDocCards() {
    const grid = document.getElementById("apply-cards-grid");
    if (!grid) return;
    grid.innerHTML = Object.keys(DIGI_DATA.DOCUMENTS).map((key, idx) => {
      const doc = DIGI_DATA.DOCUMENTS[key];
      const isOrange = (idx % 2 === 0);
      const topBorder = isOrange ? "var(--saffron-bright)" : "var(--green)";
      const badgeClass = isOrange ? "badge-saffron" : "badge-green";
      const btnClass = isOrange ? "btn-saffron" : "btn-green";
      const linkColor = isOrange ? "var(--saffron-dark)" : "var(--green)";
      return `
        <a href="apply.html?doc=${doc.id}" class="card card-hover doc-card" style="border-top: 4px solid ${topBorder};" aria-label="Apply or Manage ${APP.escapeHtml(doc.title)}">
          <div>
            <div class="doc-card-icon" aria-hidden="true">${doc.icon}</div>
            <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 6px;">
              <h3 style="font-size: 18px; color: var(--navy); font-weight: 700;">${APP.escapeHtml(doc.title)}</h3>
              <span class="badge ${badgeClass}">${APP.escapeHtml(doc.badge)}</span>
            </div>
            <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 12px;">${APP.escapeHtml(doc.desc)}</p>
          </div>
          <div style="border-top: 1px solid var(--border); padding-top: 12px; display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 12px; font-weight: 700; color: ${linkColor};">4 Services Available &rarr;</span>
            <span class="btn btn-sm ${btnClass}">Open Services</span>
          </div>
        </a>`;
    }).join("");
  }
};
