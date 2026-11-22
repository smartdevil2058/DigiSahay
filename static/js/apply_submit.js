/**
 * DigiSahay Apply Review & Submission Handler
 */

function goToStep(step) {
  currentStep = step;
  for (let i = 1; i <= 4; i++) {
    const container = document.getElementById('stepContainer' + i);
    const indicator = document.getElementById('stepIndicator' + i);
    if (container) container.style.display = (i === step) ? 'block' : 'none';
    if (indicator) {
      indicator.className = (i < step) ? 'ds-step ds-step-completed' : (i === step ? 'ds-step ds-step-active' : 'ds-step');
    }
  }
  window.scrollTo({ top: document.getElementById('applyStepper').offsetTop - 20, behavior: 'smooth' });
}

function validateAndGoToStep(nextStep) {
  const name = document.getElementById('applicantName').value.trim();
  const guardian = document.getElementById('applicantGuardian').value.trim();
  const dob = document.getElementById('applicantDob').value;
  const mobile = document.getElementById('applicantMobile').value.trim();
  const email = document.getElementById('applicantEmail').value.trim();
  const address = document.getElementById('applicantAddress').value.trim();
  const pincode = document.getElementById('applicantPincode').value.trim();

  if (!name || !guardian || !dob || !mobile || !email || !address || !pincode) {
    alert('Please fill in all required applicant fields before proceeding.');
    return;
  }
  if (mobile.length !== 10) {
    alert('Mobile number must be exactly 10 digits.');
    return;
  }
  goToStep(nextStep);
}

function prefillApplicantFromSession() {
  const userJson = localStorage.getItem('digisahay_user');
  if (userJson) {
    try {
      const u = JSON.parse(userJson);
      if (u.email && !document.getElementById('applicantEmail').value) {
        document.getElementById('applicantEmail').value = u.email;
      }
      if (u.name && !document.getElementById('applicantName').value) {
        document.getElementById('applicantName').value = u.name;
      }
    } catch(e) {}
  }
}

function populateReviewDossier() {
  const sSelect = document.getElementById('applyServiceSelect');
  document.getElementById('reviewServiceName').textContent = sSelect ? sSelect.options[sSelect.selectedIndex].text : '-';
  const modeVal = document.querySelector('input[name="applyMode"]:checked').value;
  document.getElementById('reviewMode').textContent = (modeVal === 'ONLINE_ASSISTED') ? 'Online Assisted Digital Preparation' : 'Jan Seva Kendra In-Person Submission';

  document.getElementById('reviewApplicantName').textContent = document.getElementById('applicantName').value.trim();
  document.getElementById('reviewDob').textContent = document.getElementById('applicantDob').value;
  document.getElementById('reviewGender').textContent = document.getElementById('applicantGender').value;
  document.getElementById('reviewMobile').textContent = document.getElementById('applicantMobile').value.trim();
  document.getElementById('reviewEmail').textContent = document.getElementById('applicantEmail').value.trim();
  document.getElementById('reviewAddress').textContent = document.getElementById('applicantAddress').value.trim();
  document.getElementById('reviewDistrict').textContent = document.getElementById('applicantDistrict').value;
  document.getElementById('reviewPincode').textContent = document.getElementById('applicantPincode').value.trim();

  const listEl = document.getElementById('reviewAttachedDocsList');
  listEl.innerHTML = '';
  const entries = Object.entries(attachedSlotDocuments);
  document.getElementById('reviewDocsTallyBadge').textContent = entries.length + ' Documents Verified';

  if (entries.length === 0) {
    listEl.innerHTML = '<span style="font-size: var(--font-size-xs); color: var(--color-text-muted);">No documents attached.</span>';
  } else {
    entries.forEach(([grpId, doc]) => {
      const grp = currentRequirementGroups.find(g => g.group_id === grpId);
      const row = document.createElement('div');
      row.style.display = 'flex';
      row.style.alignItems = 'center';
      row.style.justifyContent = 'space-between';
      row.style.padding = '8px 12px';
      row.style.background = 'var(--color-surface-container-low)';
      row.style.borderRadius = 'var(--radius-md)';
      row.style.fontSize = 'var(--font-size-xs)';
      row.innerHTML = `
        <div>
          <strong style="color: var(--color-primary);">${grp ? escapeHtml(grp.group_name) : grpId}:</strong>
          <span style="color: var(--color-text-primary); margin-left: 6px;">${escapeHtml(doc.name)}</span>
          <span style="color: var(--color-text-muted); font-size: 11px; margin-left: 4px;">(${escapeHtml(doc.filename)})</span>
        </div>
        <span class="ds-badge ds-badge-verified" style="font-size: 11px;">
          <span class="material-symbols-outlined" style="font-size: 12px;">check_circle</span>
          ${doc.source === 'VAULT' ? 'From Vault' : 'Uploaded'}
        </span>
      `;
      listEl.appendChild(row);
    });
  }
}

async function submitCitizenApplication() {
  const decl = document.getElementById('statutoryDeclarationCheck');
  if (!decl.checked) {
    alert('Please accept the statutory citizen declaration before submitting.');
    return;
  }

  const submitBtn = document.getElementById('submitApplicationBtn');
  const alertEl = document.getElementById('applySubmitAlert');
  submitBtn.disabled = true;
  submitBtn.innerHTML = '<span class="material-symbols-outlined" style="font-size: 18px; animation: spin 1s linear infinite;">sync</span> Submitting Application...';

  const docEntries = Object.values(attachedSlotDocuments).map(d => ({
    document_id: d.document_id,
    requirement_option_id: d.option_id
  }));

  const payload = {
    service_id: document.getElementById('applyServiceSelect').value,
    application_mode: document.querySelector('input[name="applyMode"]:checked').value,
    applicant_name: document.getElementById('applicantName').value.trim(),
    father_name: document.getElementById('applicantGuardian').value.trim(),
    dob: document.getElementById('applicantDob').value,
    gender: document.getElementById('applicantGender').value,
    mobile: document.getElementById('applicantMobile').value.trim(),
    email: document.getElementById('applicantEmail').value.trim(),
    address: document.getElementById('applicantAddress').value.trim(),
    district: document.getElementById('applicantDistrict').value,
    pincode: document.getElementById('applicantPincode').value.trim(),
    document_ids: docEntries
  };

  const token = localStorage.getItem('digisahay_jwt');
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = 'Bearer ' + token;

  try {
    const res = await fetch('/api/applications', { method: 'POST', headers: headers, body: JSON.stringify(payload) });
    const result = await res.json();
    if (res.ok && result.success) {
      document.getElementById('applyWizardForm').style.display = 'none';
      const successScreen = document.getElementById('applySuccessScreen');
      successScreen.style.display = 'flex';
      document.getElementById('successAppRef').textContent = result.application_reference || result.application_id;
      document.getElementById('successAppId').textContent = result.application_id;
      document.getElementById('successServiceName').textContent = document.getElementById('reviewServiceName').textContent;
      document.getElementById('successAppStatus').textContent = (result.application && result.application.application_status) || 'READY_TO_APPLY';
      document.getElementById('successTrackLink').href = '/applications?track_id=' + encodeURIComponent(result.application_id);
      window.scrollTo({ top: successScreen.offsetTop - 30, behavior: 'smooth' });
    } else {
      alertEl.style.display = 'block';
      alertEl.style.background = '#ffebee';
      alertEl.style.color = '#c62828';
      alertEl.textContent = 'Submission failed: ' + (result.message || 'Please check your inputs.');
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<span class="material-symbols-outlined" style="font-size: 20px;">send</span> Submit Application';
    }
  } catch(e) {
    alertEl.style.display = 'block';
    alertEl.style.background = '#ffebee';
    alertEl.style.color = '#c62828';
    alertEl.textContent = 'Network error while submitting application.';
    submitBtn.disabled = false;
    submitBtn.innerHTML = '<span class="material-symbols-outlined" style="font-size: 20px;">send</span> Submit Application';
  }
}
