/**
 * DigiSahay Apply Wizard - Requirements Fetching, Uploads & Pre-Submission Validation
 */
let currentStep = 1;
let currentServiceId = '';
let currentRequirementGroups = [];
let userVaultDocuments = [];
let attachedSlotDocuments = {};

document.addEventListener('DOMContentLoaded', () => {
  const select = document.getElementById('applyServiceSelect');
  if (select) {
    currentServiceId = select.value;
    onServiceSelectionChanged();
  }
  prefillApplicantFromSession();
  loadUserVaultForApply();
});

function onServiceSelectionChanged() {
  const select = document.getElementById('applyServiceSelect');
  if (!select) return;
  const opt = select.options[select.selectedIndex];
  if (!opt) return;

  currentServiceId = opt.value;
  document.getElementById('boxAuthority').textContent = opt.getAttribute('data-authority') || 'Government Department';
  document.getElementById('boxFee').textContent = opt.getAttribute('data-fee') || '₹0 (Free / Statutory)';
  document.getElementById('boxTimeline').textContent = opt.getAttribute('data-tat') || '15-30 Days';

  const portalUrl = opt.getAttribute('data-portal');
  const portalLink = document.getElementById('boxPortalLink');
  if (portalLink) portalLink.style.display = portalUrl ? 'inline' : 'none';
  if (portalUrl && portalLink) portalLink.href = portalUrl;

  const prereqLink = document.getElementById('boxPrereqLink');
  if (prereqLink) prereqLink.href = '/prerequisite-checker?service_id=' + encodeURIComponent(currentServiceId);
  const step3Link = document.getElementById('step3CheckerLink');
  if (step3Link) step3Link.href = '/prerequisite-checker?service_id=' + encodeURIComponent(currentServiceId);

  loadServiceRequirements(currentServiceId);
}

async function loadUserVaultForApply() {
  const token = localStorage.getItem('digisahay_jwt');
  if (!token) return;
  try {
    const res = await fetch('/api/documents/', { headers: { 'Authorization': 'Bearer ' + token } });
    const data = await res.json();
    if (res.ok && data.documents) {
      userVaultDocuments = data.documents;
      renderRequirementSlots();
    }
  } catch(e) {}
}

async function loadServiceRequirements(serviceId) {
  const container = document.getElementById('requirementSlotsContainer');
  const targetNameEl = document.getElementById('step3TargetServiceName');
  const sSelect = document.getElementById('applyServiceSelect');
  if (targetNameEl && sSelect) targetNameEl.textContent = sSelect.options[sSelect.selectedIndex].text;

  if (container) {
    container.innerHTML = `
      <div style="text-align: center; padding: 24px; color: var(--color-text-muted); font-size: var(--font-size-xs);">
        <span class="material-symbols-outlined" style="font-size: 26px; animation: spin 1.5s linear infinite;">sync</span>
        <div style="margin-top: 6px;">Fetching official requirements from Prerequisite Rules Engine...</div>
      </div>`;
  }

  try {
    const res = await fetch('/api/services/' + encodeURIComponent(serviceId) + '/requirements');
    const data = await res.json();
    if (res.ok && data.success && data.requirement_groups && data.requirement_groups.length > 0) {
      currentRequirementGroups = data.requirement_groups;
    } else {
      currentRequirementGroups = [{
        group_id: 'GRP-GEN-PROOF',
        group_name: 'Supporting Identity / Address Document',
        description: 'General supporting proof for administrative verification.',
        selection_mode: 'CHOOSE_ONE',
        min_selections: 1,
        documents: [{
          option_id: 'OPT-GEN-1',
          document_type_id: 'DOC-AADHAAR',
          document_name: 'Aadhaar Card / Any Government Issued Photo ID',
          official_acceptance_conditions: 'Clear, legible copy of valid government-issued identity or address proof.',
          format_or_size_constraints: 'PDF, JPG, PNG up to 5 MB'
        }]
      }];
    }
    renderRequirementChecklist();
    renderRequirementSlots();
    updateProgressIndicator();
  } catch(err) {
    if (container) container.innerHTML = '<div style="color: var(--color-error); padding: 12px; font-size: 12px;">Failed to load requirements. Please refresh.</div>';
  }
}

async function handleSlotFileUpload(groupId, input) {
  if (!input.files || !input.files[0]) return;
  const file = input.files[0];
  const msgEl = document.getElementById('slot_upload_msg_' + groupId);
  if (msgEl) {
    msgEl.style.color = 'var(--color-primary)';
    msgEl.innerHTML = '<span class="material-symbols-outlined" style="font-size: 12px; animation: spin 1s linear infinite;">sync</span> Uploading ' + file.name + '...';
  }

  const select = document.getElementById('doctype_select_' + groupId);
  const docTypeId = select ? select.value : 'DOC-AADHAAR';
  const optId = select ? (select.options[select.selectedIndex].getAttribute('data-opt') || '') : '';
  const docTypeName = select ? select.options[select.selectedIndex].text : file.name;

  const formData = new FormData();
  formData.append('file', file);
  formData.append('document_type_id', docTypeId);
  formData.append('document_name', docTypeName);
  formData.append('email', (document.getElementById('applicantEmail') || {}).value || '');

  const token = localStorage.getItem('digisahay_jwt');
  const headers = {};
  if (token) headers['Authorization'] = 'Bearer ' + token;

  try {
    const res = await fetch('/api/documents/upload', { method: 'POST', headers: headers, body: formData });
    const result = await res.json();
    if (res.ok && result.success && result.document) {
      attachedSlotDocuments[groupId] = {
        document_id: result.document.document_id,
        option_id: optId,
        document_type_id: docTypeId,
        name: docTypeName,
        filename: file.name,
        size: Math.round(file.size / 1024) + ' KB',
        source: 'UPLOADED',
        status: 'Uploaded'
      };
      clearSlotHighlight(groupId);
      renderRequirementChecklist();
      renderRequirementSlots();
      updateProgressIndicator();
    } else {
      if (msgEl) {
        msgEl.style.color = '#c62828';
        msgEl.textContent = 'Upload failed: ' + (result.message || 'Error');
      }
    }
  } catch(e) {
    if (msgEl) {
      msgEl.style.color = '#c62828';
      msgEl.textContent = 'Network error while uploading.';
    }
  }
}

function handleSlotVaultSelect(groupId, selectEl) {
  const docId = selectEl.value;
  if (!docId) return;
  const match = userVaultDocuments.find(d => d.document_id === docId);
  if (!match) return;

  const typeSelect = document.getElementById('doctype_select_' + groupId);
  const optId = typeSelect ? (typeSelect.options[typeSelect.selectedIndex].getAttribute('data-opt') || '') : '';

  attachedSlotDocuments[groupId] = {
    document_id: match.document_id,
    option_id: optId,
    document_type_id: match.document_type_id,
    name: match.document_name,
    filename: match.original_filename || match.document_name,
    size: match.file_size ? Math.round(match.file_size / 1024) + ' KB' : 'Vault File',
    source: 'VAULT',
    status: 'Verified'
  };

  clearSlotHighlight(groupId);
  renderRequirementChecklist();
  renderRequirementSlots();
  updateProgressIndicator();
}

function removeSlotDocument(groupId) {
  delete attachedSlotDocuments[groupId];
  renderRequirementChecklist();
  renderRequirementSlots();
  updateProgressIndicator();
}

function replaceSlotDocument(groupId) {
  delete attachedSlotDocuments[groupId];
  renderRequirementChecklist();
  renderRequirementSlots();
  updateProgressIndicator();
  const fileInput = document.getElementById('slot_file_' + groupId);
  if (fileInput) fileInput.click();
}

function updateProgressIndicator() {
  let mandatoryTotal = 0;
  let mandatoryAttached = 0;
  let optionalTotal = 0;

  currentRequirementGroups.forEach(grp => {
    const isMandatory = (grp.selection_mode !== 'OPTIONAL' && grp.selection_mode !== 'CONDITIONAL') && (grp.min_selections === undefined || grp.min_selections > 0);
    if (isMandatory) {
      mandatoryTotal++;
      if (attachedSlotDocuments[grp.group_id]) mandatoryAttached++;
    } else {
      optionalTotal++;
    }
  });

  const totalAttached = Object.keys(attachedSlotDocuments).length;
  document.getElementById('totalReqBadge').textContent = mandatoryTotal + ' Mandatory';
  document.getElementById('totalOptBadge').textContent = optionalTotal + ' Optional';
  document.getElementById('totalAttachedBadge').textContent = totalAttached + ' Attached';

  const percent = mandatoryTotal > 0 ? Math.round((mandatoryAttached / mandatoryTotal) * 100) : 100;
  const bar = document.getElementById('docsProgressBar');
  const txt = document.getElementById('docsProgressText');

  if (bar) {
    bar.style.width = percent + '%';
    bar.style.background = percent === 100 ? 'var(--color-green, #138808)' : 'var(--color-saffron, #FF9933)';
  }
  if (txt) {
    txt.textContent = `${mandatoryAttached} of ${mandatoryTotal} required uploaded (${percent}%)`;
    if (percent === 100) txt.innerHTML = `<span style="color: var(--color-green-text);">✓ All ${mandatoryTotal} required documents attached (100%)</span>`;
  }
}

function prepareReviewAndGoToStep(nextStep) {
  const missingSlots = [];
  currentRequirementGroups.forEach(grp => {
    const isMandatory = (grp.selection_mode !== 'OPTIONAL' && grp.selection_mode !== 'CONDITIONAL') && (grp.min_selections === undefined || grp.min_selections > 0);
    if (isMandatory && !attachedSlotDocuments[grp.group_id]) {
      missingSlots.push(grp);
    }
  });

  const alertEl = document.getElementById('missingDocsAlert');
  if (missingSlots.length > 0) {
    if (alertEl) {
      alertEl.style.display = 'block';
      document.getElementById('missingCountText').textContent = missingSlots.length;
    }
    currentRequirementGroups.forEach(grp => {
      const card = document.getElementById('slot_card_' + grp.group_id);
      if (card) {
        if (missingSlots.find(m => m.group_id === grp.group_id)) {
          card.style.border = '2px solid var(--color-error, #d32f2f)';
          card.style.boxShadow = '0 0 0 3px rgba(211, 47, 47, 0.15)';
        } else {
          card.style.border = '1px solid var(--color-border)';
          card.style.boxShadow = 'none';
        }
      }
    });

    const firstMissing = document.getElementById('slot_card_' + missingSlots[0].group_id);
    if (firstMissing) firstMissing.scrollIntoView({ behavior: 'smooth', block: 'center' });
    return;
  }

  if (alertEl) alertEl.style.display = 'none';
  populateReviewDossier();
  goToStep(nextStep);
}
