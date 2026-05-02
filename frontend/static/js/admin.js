

// document.addEventListener('DOMContentLoaded', () => {
//     const isSessionsPage = document.querySelector('.admin-sessions-page');
//     const isUsersPage = document.querySelector('.admin-users-page');
//     const isDocumentsPage = document.querySelector('.admin-documents-page');
//     const userDetailModal = document.getElementById('userDetailModal');
//     const userDetailBody = document.getElementById('userDetailBody');
//     const documentDetailModal = document.getElementById('documentDetailModal');
//     const documentDetailBody = document.getElementById('documentDetailBody');

//     const searchInput = document.getElementById('searchInput');
//     if (searchInput) {
//         if (isSessionsPage) {
//             searchInput.addEventListener('keydown', (e) => {
//                 if (e.key === 'Enter') {
//                     e.preventDefault();
//                     applySessionsFilters(true);
//                 }
//             });
//         } else if (isUsersPage) {
//             searchInput.addEventListener('keydown', (e) => {
//                 if (e.key === 'Enter') {
//                     e.preventDefault();
//                     applyUserFilters(true);
//                 }
//             });
//         } else if (isDocumentsPage) {
//             searchInput.addEventListener('keydown', (e) => {
//                 if (e.key === 'Enter') {
//                     e.preventDefault();
//                     applyDocumentFilters(true);
//                 }
//             });
//         } else {
//             searchInput.addEventListener('input', debounce(handleSearch, 300));
//         }
//     }

//     const searchButton = document.getElementById('searchButton');
//     if (searchButton && (isSessionsPage || isDocumentsPage || isUsersPage)) {
//         searchButton.addEventListener('click', () => {
//             if (isSessionsPage) {
//                 applySessionsFilters(true);
//             } else if (isUsersPage) {
//                 applyUserFilters(true);
//             } else if (isDocumentsPage) {
//                 applyDocumentFilters(true);
//             }
//         });
//     }

//     if (userDetailModal) {
//         userDetailModal.addEventListener('click', (e) => {
//             if (e.target.closest('[data-modal-close]') || e.target.classList.contains('modal-overlay')) {
//                 closeUserModal();
//             }
//         });
//     }

//     if (documentDetailModal) {
//         documentDetailModal.addEventListener('click', (e) => {
//             if (e.target.closest('[data-modal-close]') || e.target.classList.contains('modal-overlay')) {
//                 closeDocumentModal();
//             }
//         });
//     }

//     document.addEventListener('keydown', (e) => {
//         if (e.key === 'Escape') {
//             if (userDetailModal && userDetailModal.classList.contains('open')) {
//                 closeUserModal();
//             }
//             if (documentDetailModal && documentDetailModal.classList.contains('open')) {
//                 closeDocumentModal();
//             }
//         }
//     });

//     const filters = ['roleFilter', 'statusFilter', 'typeFilter', 'dateFilter', 'sortBy'];
//     filters.forEach(filterId => {
//         const filter = document.getElementById(filterId);
//         if (filter) {
//             if (isSessionsPage) {
//                 filter.addEventListener('change', () => applySessionsFilters(true));
//             } else if (isUsersPage) {
//                 filter.addEventListener('change', () => applyUserFilters(true));
//             } else if (isDocumentsPage) {
//                 filter.addEventListener('change', () => applyDocumentFilters(true));
//             } else {
//                 filter.addEventListener('change', handleFilter);
//             }
//         }
//     });
// });

// function handleSearch(e) {
//     const searchTerm = e.target.value.toLowerCase();
//     const table = document.querySelector('.admin-table tbody');

//     if (!table) return;

//     const rows = table.getElementsByTagName('tr');

//     for (let row of rows) {
//         const text = row.textContent.toLowerCase();
//         row.style.display = text.includes(searchTerm) ? '' : 'none';
//     }
// }

// function handleFilter() {
//     console.log('Filter changed');
// }

// function applyUserFilters(withLoading = true) {
//     const params = new URLSearchParams(window.location.search);

//     const searchInput = document.getElementById('searchInput');
//     const roleFilter = document.getElementById('roleFilter');
//     const sortBy = document.getElementById('sortBy');

//     const search = searchInput ? searchInput.value.trim() : '';
//     const role = roleFilter ? roleFilter.value : 'all';
//     const sort = sortBy ? sortBy.value : 'newest';

//     if (search) {
//         params.set('q', search);
//     } else {
//         params.delete('q');
//     }

//     if (role && role !== 'all') {
//         params.set('role', role);
//     } else {
//         params.delete('role');
//     }

//     if (sort && sort !== 'newest') {
//         params.set('sort', sort);
//     } else {
//         params.delete('sort');
//     }

//     params.delete('page');

//     if (withLoading && typeof showLoading === 'function') {
//         showLoading('�ang l?c d? li?u...');
//     }
//     window.location.search = params.toString();
// }

// function applyDocumentFilters(withLoading = true) {
//     const params = new URLSearchParams(window.location.search);

//     const searchInput = document.getElementById('searchInput');
//     const typeFilter = document.getElementById('typeFilter');
//     const sortBy = document.getElementById('sortBy');

//     const search = searchInput ? searchInput.value.trim() : '';
//     const type = typeFilter ? typeFilter.value : 'all';
//     const sort = sortBy ? sortBy.value : 'newest';

//     if (search) {
//         params.set('q', search);
//     } else {
//         params.delete('q');
//     }

//     if (type && type !== 'all') {
//         params.set('type', type);
//     } else {
//         params.delete('type');
//     }

//     if (sort && sort !== 'newest') {
//         params.set('sort', sort);
//     } else {
//         params.delete('sort');
//     }

//     params.delete('page');

//     if (withLoading && typeof showLoading === 'function') {
//         showLoading('�ang l?c d? li?u...');
//     }
//     window.location.search = params.toString();
// }

// function escapeHtml(value) {
//     return String(value)
//         .replace(/&/g, '&amp;')
//         .replace(/</g, '&lt;')
//         .replace(/>/g, '&gt;')
//         .replace(/"/g, '&quot;')
//         .replace(/'/g, '&#39;');
// }

// function openUserModal() {
//     const modal = document.getElementById('userDetailModal');
//     if (!modal) return;
//     modal.classList.add('open');
//     document.body.classList.add('modal-open');
// }

// function closeUserModal() {
//     const modal = document.getElementById('userDetailModal');
//     if (!modal) return;
//     modal.classList.remove('open');
//     document.body.classList.remove('modal-open');
// }

// function openDocumentModal() {
//     const modal = document.getElementById('documentDetailModal');
//     if (!modal) return;
//     modal.classList.add('open');
//     document.body.classList.add('modal-open');
// }

// function closeDocumentModal() {
//     const modal = document.getElementById('documentDetailModal');
//     if (!modal) return;
//     modal.classList.remove('open');
//     document.body.classList.remove('modal-open');
// }

// function renderUserDetails(data) {
//     const stats = data.stats || {};
//     const totalWords = Number(stats.total_words || 0).toLocaleString('vi-VN');
//     const totalTime = typeof formatTime === 'function' ? formatTime(stats.total_time || 0) : `${stats.total_time || 0}s`;
//     const roleBadge = data.is_admin
//         ? '<span class="badge badge-admin"><i class="fas fa-shield-alt"></i> Admin</span>'
//         : '<span class="badge badge-user"><i class="fas fa-user"></i> User</span>';

//     const recentRows = (data.recent_sessions || []).map((session) => `
//         <tr>
//             <td>#${session.id}</td>
//             <td>${escapeHtml(session.filename)}</td>
//             <td>${escapeHtml(session.created_at)}</td>
//             <td>${session.speed} t?/ph�t</td>
//             <td>${session.completed ? 'Ho�n th�nh' : 'Chua xong'}</td>
//             <td>${session.progress}%</td>
//         </tr>
//     `).join('');

//     const recentSection = recentRows
//         ? `
//         <div class="detail-section-title">Phi�n d?c g?n d�y</div>
//         <table class="detail-table">
//             <thead>
//                 <tr>
//                     <th>ID</th>
//                     <th>File</th>
//                     <th>Ng�y</th>
//                     <th>T?c d?</th>
//                     <th>Tr?ng th�i</th>
//                     <th>Ti?n d?</th>
//                 </tr>
//             </thead>
//             <tbody>
//                 ${recentRows}
//             </tbody>
//         </table>
//         `
//         : `<div class="detail-empty">Chua c� phi�n d?c n�o.</div>`;

//     return `
//         <div class="detail-grid">
//             <div class="detail-item">
//                 <div class="detail-label">Username</div>
//                 <div class="detail-value">${escapeHtml(data.username)}</div>
//             </div>
//             <div class="detail-item">
//                 <div class="detail-label">Email</div>
//                 <div class="detail-value">${escapeHtml(data.email)}</div>
//             </div>
//             <div class="detail-item">
//                 <div class="detail-label">Vai tr�</div>
//                 <div class="detail-value">${roleBadge}</div>
//             </div>
//             <div class="detail-item">
//                 <div class="detail-label">Ng�y tham gia</div>
//                 <div class="detail-value">${escapeHtml(data.created_at)}</div>
//             </div>
//         </div>
//         <div class="detail-stats">
//             <div class="detail-stat">
//                 <div class="stat-value">${stats.total_sessions || 0}</div>
//                 <div class="stat-label">Phi�n d?c</div>
//             </div>
//             <div class="detail-stat">
//                 <div class="stat-value">${stats.completed_sessions || 0}</div>
//                 <div class="stat-label">Ho�n th�nh</div>
//             </div>
//             <div class="detail-stat">
//                 <div class="stat-value">${totalWords}</div>
//                 <div class="stat-label">T?ng t?</div>
//             </div>
//             <div class="detail-stat">
//                 <div class="stat-value">${totalTime}</div>
//                 <div class="stat-label">T?ng th?i gian</div>
//             </div>
//             <div class="detail-stat">
//                 <div class="stat-value">${stats.avg_speed || 0}</div>
//                 <div class="stat-label">T?c d? TB</div>
//             </div>
//             <div class="detail-stat">
//                 <div class="stat-value">${stats.total_documents || 0}</div>
//                 <div class="stat-label">T�i li?u</div>
//             </div>
//         </div>
//         ${recentSection}
//     `;
// }

// function renderDocumentDetails(data) {
//     const totalWords = Number(data.word_count || 0).toLocaleString('vi-VN');
//     const totalReads = Number(data.total_reads || 0).toLocaleString('vi-VN');
//     const roleBadge = data.file_type
//         ? `<span class="badge badge-${data.file_type === 'pdf' ? 'danger' : data.file_type === 'docx' ? 'primary' : 'secondary'}">${data.file_type.toUpperCase()}</span>`
//         : '';

//     const recentRows = (data.recent_sessions || []).map((session) => `
//         <tr>
//             <td>#${session.id}</td>
//             <td>${escapeHtml(session.user)}</td>
//             <td>${escapeHtml(session.created_at)}</td>
//             <td>${session.speed} t?/ph�t</td>
//             <td>${typeof formatTime === 'function' ? formatTime(session.duration || 0) : `${session.duration || 0}s`}</td>
//             <td>${session.completed ? 'Ho�n th�nh' : 'Chua xong'}</td>
//             <td>${session.progress}%</td>
//         </tr>
//     `).join('');

//     const recentSection = recentRows
//         ? `
//         <div class="detail-section-title">Phi�n d?c g?n d�y</div>
//         <table class="detail-table">
//             <thead>
//                 <tr>
//                     <th>ID</th>
//                     <th>User</th>
//                     <th>Ng�y</th>
//                     <th>T?c d?</th>
//                     <th>Th?i gian</th>
//                     <th>Tr?ng th�i</th>
//                     <th>Ti?n d?</th>
//                 </tr>
//             </thead>
//             <tbody>
//                 ${recentRows}
//             </tbody>
//         </table>
//         `
//         : `<div class="detail-empty">Chua c� phi�n d?c n�o.</div>`;

//     return `
//         <div class="detail-grid">
//             <div class="detail-item">
//                 <div class="detail-label">T�i li?u</div>
//                 <div class="detail-value">${escapeHtml(data.filename)}</div>
//             </div>
//             <div class="detail-item">
//                 <div class="detail-label">Lo?i file</div>
//                 <div class="detail-value">${roleBadge}</div>
//             </div>
//             <div class="detail-item">
//                 <div class="detail-label">Ngu?i upload</div>
//                 <div class="detail-value">${escapeHtml(data.uploader.username)} (${escapeHtml(data.uploader.email)})</div>
//             </div>
//             <div class="detail-item">
//                 <div class="detail-label">Ng�y upload</div>
//                 <div class="detail-value">${escapeHtml(data.created_at)}</div>
//             </div>
//         </div>
//         <div class="detail-stats">
//             <div class="detail-stat">
//                 <div class="stat-value">${totalWords}</div>
//                 <div class="stat-label">S? t?</div>
//             </div>
//             <div class="detail-stat">
//                 <div class="stat-value">${totalReads}</div>
//                 <div class="stat-label">Lu?t d?c</div>
//             </div>
//         </div>
//         ${recentSection}
//     `;
// }

// function applySessionsFilters(withLoading = true) {
//     const params = new URLSearchParams(window.location.search);

//     const searchInput = document.getElementById('searchInput');
//     const statusFilter = document.getElementById('statusFilter');
//     const dateFilter = document.getElementById('dateFilter');
//     const sortBy = document.getElementById('sortBy');

//     const search = searchInput ? searchInput.value.trim() : '';
//     const status = statusFilter ? statusFilter.value : 'all';
//     const date = dateFilter ? dateFilter.value : 'all';
//     const sort = sortBy ? sortBy.value : 'newest';

//     if (search) {
//         params.set('q', search);
//     } else {
//         params.delete('q');
//     }

//     if (status && status !== 'all') {
//         params.set('status', status);
//     } else {
//         params.delete('status');
//     }

//     if (date && date !== 'all') {
//         params.set('date', date);
//     } else {
//         params.delete('date');
//     }

//     if (sort && sort !== 'newest') {
//         params.set('sort', sort);
//     } else {
//         params.delete('sort');
//     }

//     params.delete('page');

//     if (withLoading && typeof showLoading === 'function') {
//         showLoading('�ang l?c d? li?u...');
//     }
//     window.location.search = params.toString();
// }

// async function deleteUser(userId, username) {
//     if (!confirm(`B?n ch?c ch?n mu?n x�a user "${username}"?\n\nT?t c? d? li?u li�n quan s? b? x�a vinh vi?n!`)) {
//         return;
//     }

//     try {
//         showLoading('�ang x�a user...');

//         const response = await fetch(`/admin/delete-user/${userId}`, {
//             method: 'DELETE'
//         });

//         const data = await response.json();

//         hideLoading();

//         if (data.success) {
//             showAlert(data.message, 'success');
//             setTimeout(() => location.reload(), 1000);
//         } else {
//             showAlert(data.error || 'C� l?i x?y ra!', 'danger');
//         }
//     } catch (error) {
//         hideLoading();
//         showAlert('L?i x�a user: ' + error.message, 'danger');
//     }
// }

// function viewUserDetails(userId) {
//     const modalBody = document.getElementById('userDetailBody');
//     if (!modalBody) {
//         showAlert('Kh�ng th? m? chi ti?t ngu?i d�ng', 'danger');
//         return;
//     }

//     openUserModal();
//     modalBody.innerHTML = '<div class="modal-loading">�ang t?i d? li?u...</div>';

//     fetch(`/admin/user/${userId}/details`)
//         .then((response) => {
//             if (!response.ok) {
//                 throw new Error('Kh�ng th? t?i d? li?u');
//             }
//             return response.json();
//         })
//         .then((data) => {
//             if (data.error) {
//                 throw new Error(data.error);
//             }
//             modalBody.innerHTML = renderUserDetails(data);
//         })
//         .catch((error) => {
//             modalBody.innerHTML = `<div class="detail-empty">${escapeHtml(error.message || 'C� l?i x?y ra')}</div>`;
//         });
// }

// window.viewUserDetails = viewUserDetails;

// function viewDocument(docId) {
//     const modalBody = document.getElementById('documentDetailBody');
//     if (!modalBody) {
//         showAlert('Kh�ng th? m? chi ti?t t�i li?u', 'danger');
//         return;
//     }

//     openDocumentModal();
//     modalBody.innerHTML = '<div class="modal-loading">�ang t?i d? li?u...</div>';

//     fetch(`/admin/document/${docId}/details`)
//         .then((response) => {
//             if (!response.ok) {
//                 throw new Error('Kh�ng th? t?i d? li?u');
//             }
//             return response.json();
//         })
//         .then((data) => {
//             if (data.error) {
//                 throw new Error(data.error);
//             }
//             modalBody.innerHTML = renderDocumentDetails(data);
//         })
//         .catch((error) => {
//             modalBody.innerHTML = `<div class="detail-empty">${escapeHtml(error.message || 'C� l?i x?y ra')}</div>`;
//         });
// }

// window.viewDocument = viewDocument;

// function exportData(type) {
//     showAlert(`Xu?t d? li?u ${type}...`, 'info');
// }
// async function deleteDocument(docId, filename) {
//     if (!confirm(`B?n ch?c ch?n mu?n x�a t�i li?u "${filename}"?`)) {
//         return;
//     }

//     try {
//         const response = await fetch(`/user/delete-document/${docId}`, {
//             method: 'DELETE'
//         });

//         const data = await response.json();

//         if (data.success) {
//             showAlert(data.message, 'success');
//             setTimeout(() => location.reload(), 1000);
//         } else {
//             showAlert(data.error, 'error');
//         }
//     } catch (error) {
//         showAlert('L?i x�a t�i li?u: ' + error.message, 'error');
//     }
// }

// window.deleteDocument = deleteDocument;

// LINE CHART
const ctx1 = document.getElementById('lineChart');

if (ctx1) {
    new Chart(ctx1, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
            datasets: [
                {
                    label: 'Users',
                    data: [10, 30, 20, 40, 35],
                    borderColor: '#3b82f6'
                },
                {
                    label: 'Docs',
                    data: [20, 10, 30, 25, 45],
                    borderColor: '#10b981'
                }
            ]
        }
    });
}

// DONUT
const ctx2 = document.getElementById('donutChart');

if (ctx2) {
    new Chart(ctx2, {
        type: 'doughnut',
        data: {
            labels: ['Users', 'Docs', 'Sessions'],
            datasets: [{
                data: [14, 11, 9],
                backgroundColor: ['#3b82f6', '#10b981', '#ef4444']
            }]
        }
    });
}