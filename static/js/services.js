/**
 * DigiSahay - Services Page: 2-Level In-Tab Page Navigation
 * Level 1: Choose Document (Aadhaar | PAN Card | Voter ID)
 * Level 2: Dedicated Document Services Page View (Inside same tab)
 */

let selectedCategory = null;

const CATEGORY_MAP = {
  'aadhaar': 'Aadhaar Card',
  'pan': 'PAN Card',
  'voter': 'Voter ID',
  'aadhaar card': 'Aadhaar Card',
  'pan card': 'PAN Card',
  'voter id': 'Voter ID'
};

const CATEGORY_META = {
  'Aadhaar Card': {
    docId: 'aadhaar',
    title: 'Aadhaar Card Services',
    authority: 'Unique Identification Authority of India (UIDAI)',
    badge: '6 Services In-Scope',
    icon: 'fingerprint',
    iconColor: '#000080',
    iconBg: '#fff7ed',
    accentBorder: 'var(--color-saffron)'
  },
  'PAN Card': {
    docId: 'pan',
    title: 'PAN Card Services',
    authority: 'Income Tax Department • Protean / UTIITSL',
    badge: '4 Services In-Scope',
    icon: 'badge',
    iconColor: 'var(--color-primary)',
    iconBg: '#eef2ff',
    accentBorder: 'var(--color-primary)'
  },
  'Voter ID': {
    docId: 'voter',
    title: 'Voter ID (EPIC) Services',
    authority: 'Election Commission of India (ECI)',
    badge: '6 Services In-Scope',
    icon: 'how_to_vote',
    iconColor: 'var(--color-green)',
    iconBg: '#f0fdf4',
    accentBorder: 'var(--color-green)'
  }
};

function openDocumentServices(categoryName, pushState = true) {
  const normKey = (categoryName || '').toLowerCase();
  const fullCategory = CATEGORY_MAP[normKey] || categoryName;
  const meta = CATEGORY_META[fullCategory];
  if (!meta) return;

  selectedCategory = fullCategory;

  const selectionView = document.getElementById('documentSelectionView');
  const detailView = document.getElementById('categoryDetailView');
  if (selectionView) selectionView.style.display = 'none';
  if (detailView) {
    detailView.style.display = 'flex';
    detailView.classList.remove('services-fade-in');
    void detailView.offsetWidth;
    detailView.classList.add('services-fade-in');
  }

  const bName = document.getElementById('breadcrumbDocName');
  const hTitle = document.getElementById('detailHeaderTitle');
  const hAuth = document.getElementById('detailHeaderAuthority');
  const hBadge = document.getElementById('detailHeaderBadge');
  const hCard = document.getElementById('detailHeaderCard');
  const iconEl = document.getElementById('detailHeaderIcon');

  if (bName) bName.textContent = meta.title;
  if (hTitle) hTitle.textContent = meta.title;
  if (hAuth) hAuth.textContent = meta.authority;
  if (hBadge) hBadge.textContent = meta.badge;
  if (hCard) hCard.style.borderTop = `4px solid ${meta.accentBorder}`;
  if (iconEl) {
    iconEl.textContent = meta.icon;
    iconEl.style.color = meta.iconColor;
    iconEl.parentElement.style.background = meta.iconBg;
  }

  const searchInput = document.getElementById('serviceSearchInput');
  if (searchInput) {
    searchInput.value = '';
    searchInput.placeholder = `Search in ${meta.title} (e.g. update, new, correction)...`;
  }

  filterServices();
  window.scrollTo({ top: 0, behavior: 'smooth' });

  if (pushState && window.history.pushState) {
    const url = new URL(window.location);
    url.searchParams.set('doc', meta.docId);
    window.history.pushState({ doc: meta.docId }, '', url);
  }
}

function goBackToDocuments(pushState = true) {
  selectedCategory = null;

  const selectionView = document.getElementById('documentSelectionView');
  const detailView = document.getElementById('categoryDetailView');
  if (detailView) detailView.style.display = 'none';
  if (selectionView) {
    selectionView.style.display = 'flex';
    selectionView.classList.remove('services-fade-in');
    void selectionView.offsetWidth;
    selectionView.classList.add('services-fade-in');
  }

  window.scrollTo({ top: 0, behavior: 'smooth' });

  if (pushState && window.history.pushState) {
    const url = new URL(window.location);
    url.searchParams.delete('doc');
    window.history.pushState({}, '', url);
  }
}

function filterServices() {
  const query = (document.getElementById('serviceSearchInput')?.value || '').toLowerCase().trim();
  const cards = document.querySelectorAll('.service-card');
  let count = 0;

  cards.forEach(card => {
    const cat = card.getAttribute('data-category');
    const name = card.getAttribute('data-name') || '';
    const form = card.getAttribute('data-form') || '';
    const authority = card.getAttribute('data-authority') || '';
    const desc = card.getAttribute('data-desc') || '';
    const matchesQuery = (!query || name.includes(query) || form.includes(query) || authority.includes(query) || desc.includes(query));

    if (cat === selectedCategory && matchesQuery) {
      card.style.display = 'flex';
      count++;
    } else {
      card.style.display = 'none';
    }
  });

  const noFound = document.getElementById('noServicesFound');
  if (noFound) noFound.style.display = (count === 0) ? 'block' : 'none';
  const countEl = document.getElementById('detailCategoryCount');
  if (countEl) countEl.textContent = count;
}

function clearServiceSearch() {
  const input = document.getElementById('serviceSearchInput');
  if (input) input.value = '';
  filterServices();
}

function showServiceModal(id, name, category, authority, form, desc, url) {
  document.getElementById('modalTitle').textContent = name + (form ? ' (' + form + ')' : '');
  document.getElementById('modalCategory').textContent = category;
  document.getElementById('modalAuthority').textContent = authority;
  document.getElementById('modalDesc').textContent = desc;
  document.getElementById('modalEligibilityLink').href = '/prerequisite-checker?service_id=' + encodeURIComponent(id);
  document.getElementById('modalApplyLink').href = '/apply?service_id=' + encodeURIComponent(id);
  const offLink = document.getElementById('modalOfficialLink');
  if (url) { offLink.href = url; offLink.style.display = 'inline-flex'; } else { offLink.style.display = 'none'; }
  document.getElementById('serviceDetailsModal').style.display = 'flex';
}

function hideServiceModal() {
  const modal = document.getElementById('serviceDetailsModal');
  if (modal) modal.style.display = 'none';
}

function closeServiceModal(e) {
  if (e.target.id === 'serviceDetailsModal') hideServiceModal();
}

window.addEventListener('popstate', function() {
  const urlParams = new URLSearchParams(window.location.search);
  const doc = urlParams.get('doc');
  if (doc && CATEGORY_MAP[doc.toLowerCase()]) {
    openDocumentServices(CATEGORY_MAP[doc.toLowerCase()], false);
  } else {
    goBackToDocuments(false);
  }
});

document.addEventListener('DOMContentLoaded', function() {
  const urlParams = new URLSearchParams(window.location.search);
  const doc = urlParams.get('doc');
  if (doc && CATEGORY_MAP[doc.toLowerCase()]) {
    openDocumentServices(CATEGORY_MAP[doc.toLowerCase()], false);
  } else {
    goBackToDocuments(false);
  }
});
