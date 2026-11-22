// DigiSahay Prototype - Unified Apply & Track Flow (js/apply.js)
// Handles 4 document options, 3-step wizard, Leaflet map, booking, & tracker.

const APPLY = {
  docId: "aadhaar",
  currentOption: "new",
  currentStep: 1,
  selectedCenter: null,
  mapInstance: null,
  appRecord: null,

  init() {
    APP.requireAuth();
    APP.renderLayout("apply");
    const params = new URLSearchParams(window.location.search);
    const requestedDoc = params.get("doc");
    this.docId = (requestedDoc && DIGI_DATA.DOCUMENTS[requestedDoc]) ? requestedDoc : "aadhaar";

    const docConfig = DIGI_DATA.DOCUMENTS[this.docId];
    document.getElementById("apply-doc-title").textContent = docConfig.title;
    document.getElementById("apply-doc-desc").textContent = docConfig.desc + " (" + docConfig.authority + ")";
    document.getElementById("apply-doc-icon").textContent = docConfig.icon;
    document.getElementById("apply-biometric-note").innerHTML =
      APP.renderNote("warning", "Statutory Processing Rule", DIGI_DATA.BIOMETRIC_NOTE);
    this.switchOption("new");
  },

  switchOption(option) {
    this.currentOption = option;
    this.currentStep = 1;
    document.querySelectorAll(".option-tab-btn").forEach(btn => {
      const active = (btn.dataset.option === option);
      const isGreen = (option === "track" || option === "update");
      btn.classList.toggle("btn-saffron", active && !isGreen);
      btn.classList.toggle("btn-green", active && isGreen);
      btn.classList.toggle("btn-outline", !active);
    });
    const isTrack = (option === "track");
    document.getElementById("apply-wizard-wrapper").style.display = isTrack ? "none" : "block";
    document.getElementById("track-wrapper").style.display = isTrack ? "block" : "none";
    if (isTrack) this.initTrackView();
    else { this.renderStep1(); this.goToStep(1); }
  },

  goToStep(step) {
    this.currentStep = step;
    [1, 2, 3].forEach(s => {
      const el = document.getElementById(`step-content-${s}`);
      const indicator = document.getElementById(`stepper-item-${s}`);
      if (el) el.style.display = (s === step) ? "block" : "none";
      if (indicator) {
        indicator.classList.toggle("active", s === step);
        indicator.classList.toggle("completed", s < step);
      }
    });
    if (step === 2) setTimeout(() => this.initMapAndCenters(), 100);
    window.scrollTo({ top: 120, behavior: "smooth" });
  },

  // STEP 1: Details & Required Docs Checklist
  renderStep1() {
    const list = (DIGI_DATA.REQUIRED_DOCS[this.docId] && DIGI_DATA.REQUIRED_DOCS[this.docId][this.currentOption]) || [];
    const checklistHtml = list.map(item => `<li>${APP.escapeHtml(item)}</li>`).join("");

    document.getElementById("step1-requirements-note").innerHTML = APP.renderNote(
      "info",
      `Required Papers for ${DIGI_DATA.DOCUMENTS[this.docId].title} (${this.getOptionLabel(this.currentOption)})`,
      `<ul style="margin: 6px 0 0 18px; line-height: 1.5;">${checklistHtml}</ul>`
    );

    // Rule: Ask Aadhaar for all docs EXCEPT brand-new Aadhaar application
    const isNewAadhaar = (this.docId === "aadhaar" && this.currentOption === "new");
    const aadhaarFieldWrapper = document.getElementById("field-aadhaar-wrapper");
    if (aadhaarFieldWrapper) aadhaarFieldWrapper.style.display = isNewAadhaar ? "none" : "block";

    const updateSection = document.getElementById("field-update-options");
    const missingSection = document.getElementById("field-missing-options");
    if (updateSection) updateSection.style.display = (this.currentOption === "update") ? "block" : "none";
    if (missingSection) missingSection.style.display = (this.currentOption === "missing") ? "block" : "none";

    const profile = APP.get("digisahay_profile", {});
    ["name", "dob", "phone", "email"].forEach(k => {
      const el = document.getElementById("form-" + k);
      if (el && profile[k]) el.value = profile[k];
    });
  },

  getOptionLabel(opt) {
    const labels = { new: "New Apply", update: "Update", missing: "Lost Document Replacement", track: "Track Status" };
    return labels[opt] || opt;
  },

  validateStep1() {
    const name = document.getElementById("form-name").value.trim();
    const dob = document.getElementById("form-dob").value;
    const phone = document.getElementById("form-phone").value.trim();
    const isNewAadhaar = (this.docId === "aadhaar" && this.currentOption === "new");
    if (!name || !dob || !phone) return alert("Please fill all mandatory applicant details.");

    let aadhaarLast4 = "N/A";
    if (!isNewAadhaar) {
      const aVal = document.getElementById("form-aadhaar").value.replace(/\s+/g, "");
      if (!/^\d{12}$/.test(aVal)) return alert("Please enter a valid 12-digit mock Aadhaar number.");
      aadhaarLast4 = aVal.slice(-4);
    }

    this.appRecord = {
      docId: this.docId, docTitle: DIGI_DATA.DOCUMENTS[this.docId].title, option: this.currentOption,
      applicantName: name, dob, phone, aadhaarLast4,
      refNumber: "DS-" + this.docId.toUpperCase() + "-2026-" + Math.floor(1000 + Math.random() * 9000),
      tokenNumber: "TK-" + Math.floor(1000 + Math.random() * 9000), statusIndex: 0,
      createdAt: new Date().toLocaleString("en-IN")
    };
    this.goToStep(2);
  },

  // STEP 2: Leaflet Map & Ahmedabad Center Booking
  initMapAndCenters() {
    const mapContainer = document.getElementById("center-map");
    if (!mapContainer) return;
    if (!this.mapInstance) {
      this.mapInstance = L.map("center-map").setView([23.0300, 72.5650], 12);
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 18, attribution: "&copy; OpenStreetMap contributors"
      }).addTo(this.mapInstance);
    } else {
      this.mapInstance.invalidateSize();
    }

    const eligibleCenters = DIGI_DATA.CENTERS.filter(c => c.handles.includes(this.docId) || c.handles.includes("CSC"));
    if (this.markersGroup && this.mapInstance) this.mapInstance.removeLayer(this.markersGroup);
    this.markersGroup = L.layerGroup().addTo(this.mapInstance);

    const cardsContainer = document.getElementById("center-cards-container");
    cardsContainer.innerHTML = "";
    eligibleCenters.forEach((center) => {
      const marker = L.marker([center.lat, center.lng]).addTo(this.markersGroup);
      marker.bindPopup(`<b>${APP.escapeHtml(center.name)}</b><br><small>${APP.escapeHtml(center.type)}</small><br>${APP.escapeHtml(center.address)}<div style="margin-top:6px;"><a href="https://www.google.com/maps?q=${center.lat},${center.lng}+(${encodeURIComponent(center.name)})" target="_blank" rel="noopener noreferrer" style="font-size:11px; color:#000080; font-weight:600; text-decoration:none;">🗺️ Open in Google Maps ↗</a></div>`);
      const card = document.createElement("div");
      card.className = "center-card";
      card.id = `center-${center.id}`;
      card.innerHTML = `
        <div>
          <span class="badge ${center.handles.includes('aadhaar') ? 'badge-saffron' : 'badge-green'}">${APP.escapeHtml(center.type)}</span>
          <h4 style="font-size: 15px; color: var(--navy); margin-top: 3px;">${APP.escapeHtml(center.name)}</h4>
          <p style="font-size: 12px; color: var(--text-muted); margin-top: 2px;">${APP.escapeHtml(center.address)}</p>
          <div style="font-size: 12px; margin-top: 4px;">📍 ${center.distance} &bull; <strong style="color: var(--saffron-dark);">⏱ ${center.waitTime}</strong></div>
        </div>
        <div style="display: flex; gap: 6px; margin-top: 8px; flex-wrap: wrap;">
          <button type="button" class="btn btn-sm btn-outline-green select-center-btn" onclick="APPLY.selectCenter('${center.id}')" style="flex: 1;">Select Center</button>
          <a href="https://www.google.com/maps?q=${center.lat},${center.lng}+(${encodeURIComponent(center.name)})" target="_blank" rel="noopener noreferrer" class="btn btn-sm btn-outline" style="text-decoration: none; font-size: 11px; display: inline-flex; align-items: center; gap: 4px;" title="Open in Google Maps">📍 Map ↗</a>
        </div>`;
      cardsContainer.appendChild(card);
    });

    document.getElementById("booking-time-slot").innerHTML = DIGI_DATA.TIME_SLOTS.map(s => `<option value="${s}">${s}</option>`).join("");
    const dateInput = document.getElementById("booking-date");
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    dateInput.min = tomorrow.toISOString().split("T")[0];
    dateInput.value = dateInput.min;
  },

  selectCenter(centerId) {
    const center = DIGI_DATA.CENTERS.find(c => c.id === centerId);
    if (!center) return;
    this.selectedCenter = center;
    document.querySelectorAll(".center-card").forEach(c => c.classList.remove("selected"));
    const activeCard = document.getElementById(`center-${centerId}`);
    if (activeCard) activeCard.classList.add("selected");
    if (this.mapInstance) this.mapInstance.setView([center.lat, center.lng], 14);

    const slotSection = document.getElementById("slot-booking-section");
    if (slotSection) {
      slotSection.style.display = "block";
      document.getElementById("selected-center-name").textContent = center.name + " (" + center.type + ")";
      slotSection.scrollIntoView({ behavior: "smooth" });
    }
  },

  confirmBooking() {
    if (!this.selectedCenter) return alert("Please select a facilitation center first.");
    const date = document.getElementById("booking-date").value;
    const slot = document.getElementById("booking-time-slot").value;
    if (!date) return alert("Please select an appointment date.");

    Object.assign(this.appRecord, {
      centerName: this.selectedCenter.name, centerAddress: this.selectedCenter.address,
      centerType: this.selectedCenter.type, appointmentDate: date, appointmentSlot: slot
    });

    const existing = APP.get("digisahay_applications", []);
    existing.unshift(this.appRecord);
    APP.set("digisahay_applications", existing);

    document.getElementById("success-token").textContent = this.appRecord.tokenNumber;
    document.getElementById("success-ref").textContent = this.appRecord.refNumber;
    document.getElementById("success-center").textContent = `${this.appRecord.centerName} (${this.appRecord.centerAddress})`;
    document.getElementById("success-slot").textContent = `${date} at ${slot}`;
    document.getElementById("success-applicant").textContent = this.appRecord.applicantName;
    document.getElementById("success-aadhaar-masked").textContent = (this.appRecord.aadhaarLast4 !== "N/A")
      ? `XXXX-XXXX-${this.appRecord.aadhaarLast4}` : "New Enrollment (No prior Aadhaar)";
    this.goToStep(3);
  },

  // OPTION 4: Track Status View
  initTrackView() {
    const select = document.getElementById("track-ref-select");
    const apps = APP.get("digisahay_applications", []);
    if (apps.length > 0) {
      select.innerHTML = `<option value="">-- Choose from your past applications --</option>` +
        apps.map(a => `<option value="${a.refNumber}">${a.refNumber} (${a.docTitle} - ${a.option})</option>`).join("");
      select.style.display = "block";
    } else {
      select.style.display = "none";
    }

    if (!this.trackedApp) {
      this.trackedApp = apps[0] || {
        refNumber: "DS-AADHAAR-2026-1042",
        docTitle: DIGI_DATA.DOCUMENTS[this.docId].title,
        applicantName: "Aarav K. Patel",
        statusIndex: 1,
        appointmentDate: "Tomorrow",
        appointmentSlot: "11:00 AM - 11:30 AM",
        centerName: "Aadhaar Seva Kendra - Navrangpura",
        createdAt: "20 Nov 2026, 09:30 AM"
      };
    }
    this.renderTrackStatus();
  },

  onTrackSelectChange(select) {
    const ref = select.value;
    if (!ref) return;
    const apps = APP.get("digisahay_applications", []);
    const match = apps.find(a => a.refNumber === ref);
    if (match) {
      this.trackedApp = match;
      this.renderTrackStatus();
    }
  },

  lookupCustomRef() {
    const input = document.getElementById("track-custom-input").value.trim().toUpperCase();
    if (!input) return alert("Please enter a reference number.");
    const apps = APP.get("digisahay_applications", []);
    const match = apps.find(a => a.refNumber.toUpperCase() === input);
    this.trackedApp = match || {
      refNumber: input,
      docTitle: DIGI_DATA.DOCUMENTS[this.docId].title,
      applicantName: "Citizen Applicant",
      statusIndex: 0,
      appointmentDate: "Scheduled",
      appointmentSlot: "Morning",
      centerName: "Facilitation Counter",
      createdAt: new Date().toLocaleDateString("en-IN")
    };
    this.renderTrackStatus();
  },

  renderTrackStatus() {
    const app = this.trackedApp;
    document.getElementById("track-display-ref").textContent = app.refNumber;
    document.getElementById("track-display-doc").textContent = app.docTitle;
    document.getElementById("track-display-applicant").textContent = app.applicantName;
    document.getElementById("track-display-center").textContent = app.centerName;

    const stages = ["Submitted", "Documents Verified", "Under Review", "Approved"];
    [0, 1, 2, 3].forEach(idx => {
      const el = document.getElementById(`status-step-${idx}`);
      if (el) {
        el.className = "status-step" + (idx < app.statusIndex ? " done" : "") + (idx === app.statusIndex ? " current" : "");
      }
    });
    document.getElementById("track-status-badge").textContent = stages[app.statusIndex];
  },

  advanceStatusDemo() {
    if (!this.trackedApp) return;
    this.trackedApp.statusIndex = (this.trackedApp.statusIndex + 1) % 4;
    const apps = APP.get("digisahay_applications", []);
    const matchIndex = apps.findIndex(a => a.refNumber === this.trackedApp.refNumber);
    if (matchIndex >= 0) {
      apps[matchIndex].statusIndex = this.trackedApp.statusIndex;
      APP.set("digisahay_applications", apps);
    }
    this.renderTrackStatus();
  }
};
