/**
 * DigiSahay Apply Slots Renderer
 * Renders requirement checklists, dedicated upload slots, and attached cards.
 */

function escapeHtml(text) {
  if (!text) return '';
  const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
  return String(text).replace(/[&<>"']/g, m => map[m]);
}

function clearSlotHighlight(groupId) {
  const card = document.getElementById('slot_card_' + groupId);
  if (card) {
    card.style.border = '1px solid var(--color-border)';
    card.style.boxShadow = 'none';
  }
  const alertEl = document.getElementById('missingDocsAlert');
  if (alertEl) alertEl.style.display = 'none';
}

function renderRequirementChecklist() {
  const container = document.getElementById('requirementsChecklist');
  if (!container) return;
  container.innerHTML = '';

  currentRequirementGroups.forEach(grp => {
    const isMandatory = (grp.selection_mode !== 'OPTIONAL' && grp.selection_mode !== 'CONDITIONAL') && (grp.min_selections === undefined || grp.min_selections > 0);
    const isAttached = !!attachedSlotDocuments[grp.group_id];
    const pill = document.createElement('span');
    pill.className = 'ds-badge ' + (isAttached ? 'ds-badge-verified' : 'ds-badge-neutral');
    pill.style.fontSize = '11px';
    pill.style.cursor = 'pointer';
    pill.onclick = () => {
      const card = document.getElementById('slot_card_' + grp.group_id);
      if (card) card.scrollIntoView({ behavior: 'smooth', block: 'center' });
    };
    pill.innerHTML = `
      <span class="material-symbols-outlined" style="font-size: 13px; color: ${isAttached ? 'var(--color-green)' : (isMandatory ? '#c62828' : 'var(--color-text-muted)')};">
        ${isAttached ? 'check_circle' : (isMandatory ? 'radio_button_unchecked' : 'help_outline')}
      </span>
      <span>${escapeHtml(grp.group_name)}</span>
      <span style="opacity: 0.7; font-size: 10px;">${isAttached ? '✓' : (isMandatory ? '*' : 'Opt')}</span>
    `;
    container.appendChild(pill);
  });
}

function renderUploadDropzoneHtml(groupId, vaultOptionsHtml) {
  const hasVault = userVaultDocuments && userVaultDocuments.length > 0;
  return `
    <div style="border: 2px dashed var(--color-border); border-radius: var(--radius-md); padding: 12px; text-align: center; background: var(--color-surface-container-lowest);">
      <div style="display: flex; gap: 8px; justify-content: center; align-items: center; flex-wrap: wrap;">
        <input type="file" id="slot_file_${groupId}" accept=".pdf,.jpg,.jpeg,.png" style="display: none;" onchange="handleSlotFileUpload('${groupId}', this)">
        <button type="button" class="ds-btn ds-btn-saffron ds-btn-sm" onclick="document.getElementById('slot_file_${groupId}').click()">
          <span class="material-symbols-outlined" style="font-size: 16px;">upload_file</span>
          <span>Upload Document</span>
        </button>
        ${hasVault ? `
          <select class="ds-select ds-select-sm" style="max-width: 260px; font-size: 11px;" onchange="handleSlotVaultSelect('${groupId}', this)">
            ${vaultOptionsHtml}
          </select>` : `
          <a href="/auth" class="ds-btn ds-btn-outline ds-btn-xs" style="font-size: 10px;">Sign In to Link from Vault</a>
        `}
      </div>
      <div id="slot_upload_msg_${groupId}" style="font-size: 11px; margin-top: 6px; color: var(--color-text-muted);">
        PDF, JPG, PNG up to 5 MB
      </div>
    </div>`;
}

function renderAttachedBoxHtml(groupId, doc) {
  return `
    <div style="border: 1px solid var(--color-green-border, #a5d6a7); background: #f1f8e9; border-radius: var(--radius-md); padding: 10px 14px; display: flex; align-items: center; justify-content: space-between; gap: 8px; flex-wrap: wrap;">
      <div style="display: flex; align-items: center; gap: 10px;">
        <span class="material-symbols-outlined" style="font-size: 26px; color: var(--color-green);">verified_user</span>
        <div>
          <div style="font-weight: var(--font-weight-bold); font-size: 12px; color: var(--color-text-primary);">${escapeHtml(doc.name)}</div>
          <div style="font-size: 11px; color: var(--color-text-secondary);">${escapeHtml(doc.filename)} • ${doc.size || 'Verified'} • <strong style="color: var(--color-green-text);">Ready</strong></div>
        </div>
      </div>
      <div style="display: flex; gap: 6px;">
        <button type="button" class="ds-btn ds-btn-secondary ds-btn-xs" onclick="replaceSlotDocument('${groupId}')">
          <span class="material-symbols-outlined" style="font-size: 14px;">sync</span>
          <span>Replace</span>
        </button>
        <button type="button" class="ds-btn ds-btn-outline ds-btn-xs" style="color: var(--color-error); border-color: #ef9a9a;" onclick="removeSlotDocument('${groupId}')">
          <span class="material-symbols-outlined" style="font-size: 14px;">delete</span>
          <span>Remove</span>
        </button>
      </div>
    </div>`;
}

function renderRequirementSlots() {
  const container = document.getElementById('requirementSlotsContainer');
  if (!container) return;
  container.innerHTML = '';

  currentRequirementGroups.forEach((grp, idx) => {
    const isMandatory = (grp.selection_mode !== 'OPTIONAL' && grp.selection_mode !== 'CONDITIONAL') && (grp.min_selections === undefined || grp.min_selections > 0);
    const isConditional = grp.selection_mode === 'CONDITIONAL';
    const attached = attachedSlotDocuments[grp.group_id];

    const card = document.createElement('div');
    card.id = 'slot_card_' + grp.group_id;
    card.className = 'ds-card';
    card.style.padding = 'var(--space-md)';
    card.style.borderLeft = isMandatory ? '4px solid var(--color-primary)' : (isConditional ? '4px solid var(--color-saffron)' : '4px solid var(--color-border)');
    card.style.background = attached ? 'var(--color-surface-container-low)' : 'var(--color-surface-container-lowest)';
    card.style.transition = 'all 0.25s ease';

    let statusBadgeHtml = '';
    if (attached) {
      statusBadgeHtml = `<span class="ds-badge ds-badge-verified" style="font-size: 11px;"><span class="material-symbols-outlined" style="font-size: 12px;">${attached.source === 'VAULT' ? 'verified' : 'check_circle'}</span> ${attached.source === 'VAULT' ? 'Verified from Vault' : 'Uploaded'}</span>`;
    } else if (isMandatory) {
      statusBadgeHtml = '<span class="ds-badge" style="font-size: 11px; background: #ffebee; color: #c62828; border: 1px solid #ef9a9a;"><span class="material-symbols-outlined" style="font-size: 12px;">radio_button_unchecked</span> Required — Not Uploaded</span>';
    } else if (isConditional) {
      statusBadgeHtml = '<span class="ds-badge ds-badge-saffron" style="font-size: 11px;">Conditional — Not Uploaded</span>';
    } else {
      statusBadgeHtml = '<span class="ds-badge ds-badge-neutral" style="font-size: 11px;">Optional — Not Uploaded</span>';
    }

    let vaultOptionsHtml = '<option value="">-- Or Link Document from My Vault --</option>';
    if (userVaultDocuments && userVaultDocuments.length > 0) {
      userVaultDocuments.forEach(vd => {
        vaultOptionsHtml += `<option value="${vd.document_id}">${escapeHtml(vd.document_name)} (${vd.file_type || 'PDF'})</option>`;
      });
    }

    const firstDoc = (grp.documents && grp.documents[0]) || {};

    card.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; flex-wrap: wrap;">
        <div>
          <div style="display: flex; align-items: center; gap: 6px; flex-wrap: wrap; margin-bottom: 2px;">
            <span class="ds-badge ${isMandatory ? 'ds-badge-action' : (isConditional ? 'ds-badge-saffron' : 'ds-badge-neutral')}" style="font-size: 10px;">
              ${isMandatory ? '★ Required' : (isConditional ? 'Conditional' : 'Optional')}
            </span>
            <span style="font-size: 11px; color: var(--color-text-muted); font-weight: var(--font-weight-semibold);">${grp.selection_mode || 'Choose One'}</span>
          </div>
          <h3 style="font-size: var(--font-size-base); font-weight: var(--font-weight-bold); color: var(--color-text-primary); margin: 2px 0 0 0;">
            ${idx + 1}. ${escapeHtml(grp.group_name)}
          </h3>
          <p style="font-size: var(--font-size-xs); color: var(--color-text-secondary); margin: 2px 0 0 0;">
            ${escapeHtml(grp.description || 'Statutory proof document required for verification.')}
          </p>
        </div>
        <div id="status_badge_${grp.group_id}">${statusBadgeHtml}</div>
      </div>

      <div style="margin-top: 10px;">
        <label class="ds-label" style="font-size: 11px; text-transform: uppercase;">Accepted Document Alternative:</label>
        <select id="doctype_select_${grp.group_id}" class="ds-select" style="font-size: 12px; margin-top: 3px;" ${attached ? 'disabled' : ''}>
          ${(grp.documents || []).map(d => `<option value="${d.document_type_id}" data-opt="${d.option_id}">${escapeHtml(d.document_name)} (${d.format_or_size_constraints || 'PDF/JPEG'})</option>`).join('')}
        </select>
      </div>

      <div style="margin-top: 10px;" id="slot_action_area_${grp.group_id}">
        ${attached ? renderAttachedBoxHtml(grp.group_id, attached) : renderUploadDropzoneHtml(grp.group_id, vaultOptionsHtml)}
      </div>

      <details class="ds-prereq-accordion" style="margin-top: 10px; background: var(--color-surface-container-low); border-radius: var(--radius-md); padding: 8px 12px; font-size: 11px;">
        <summary style="cursor: pointer; font-weight: var(--font-weight-bold); color: var(--color-primary); display: flex; align-items: center; gap: 6px;">
          <span class="material-symbols-outlined" style="font-size: 15px; color: var(--color-saffron-dark);">help_outline</span>
          <span>Why do I need this document? / આ દસ્તાવેજ શા માટે જરૂરી છે?</span>
        </summary>
        <div style="margin-top: 6px; padding-top: 6px; border-top: 1px solid var(--color-border); display: flex; flex-direction: column; gap: 4px; color: var(--color-text-secondary); line-height: 1.5;">
          <div><strong style="color: var(--color-text-primary);">Statutory Purpose:</strong> ${escapeHtml(grp.description || 'Required under statutory norms to establish citizen eligibility.')}</div>
          <div><strong style="color: var(--color-text-primary);">Acceptance Conditions:</strong> ${escapeHtml(firstDoc.official_acceptance_conditions || 'Must be a clear, legible copy matching applicant identity details.')}</div>
          <div><strong style="color: var(--color-text-primary);">Accepted Alternatives:</strong> ${(grp.documents || []).map(d => `<span class="ds-badge ds-badge-neutral" style="font-size: 10px; margin-right: 4px;">${escapeHtml(d.document_name)}</span>`).join('')}</div>
        </div>
      </details>
    `;
    container.appendChild(card);
  });
}
