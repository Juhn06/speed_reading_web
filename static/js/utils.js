/**
 * Utility Functions
 * Helper functions dùng chung
 */

// Show loading overlay
function showLoading(message = 'Đang xử lý...') {
    const existing = document.getElementById('loadingOverlay');
    if (existing) {
        existing.remove();
    }

    const overlay = document.createElement('div');
    overlay.id = 'loadingOverlay';
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.7);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
    `;

    overlay.innerHTML = `
        <div style="
            background: white;
            padding: 2rem;
            border-radius: 1rem;
            text-align: center;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        ">
            <div class="loading-spinner" style="
                width: 50px;
                height: 50px;
                border: 4px solid #f3f4f6;
                border-top-color: #667eea;
                border-radius: 50%;
                animation: spin 0.8s linear infinite;
                margin: 0 auto 1rem;
            "></div>
            <p style="margin: 0; font-weight: 500; color: #374151;">${message}</p>
        </div>
    `;

    document.body.appendChild(overlay);

    // Add animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    `;
    document.head.appendChild(style);
}

// Hide loading overlay
function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.remove();
    }
}

// Show alert message
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.setAttribute('role', 'alert');

    const icons = {
        success: 'fa-check-circle',
        danger: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };

    alertDiv.innerHTML = `
        <div class="alert-content">
            <i class="fas ${icons[type] || icons.info}"></i>
            <span>${message}</span>
        </div>
        <button class="alert-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;

    // Insert into flash container or create one
    let container = document.querySelector('.flash-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'flash-container';
        document.body.appendChild(container);
    }

    container.appendChild(alertDiv);

    // Auto remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentElement) {
            alertDiv.remove();
        }
    }, 5000);
}

// Confirm dialog
function confirmDialog(message) {
    return confirm(message);
}

// Format number with commas
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Format time (seconds to mm:ss)
function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

// Format date
function formatDate(date) {
    const d = new Date(date);
    const day = d.getDate().toString().padStart(2, '0');
    const month = (d.getMonth() + 1).toString().padStart(2, '0');
    const year = d.getFullYear();
    return `${day}/${month}/${year}`;
}

// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Copy to clipboard
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showAlert('Đã copy vào clipboard!', 'success');
        }).catch(() => {
            showAlert('Không thể copy!', 'danger');
        });
    } else {
        // Fallback for older browsers
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        showAlert('Đã copy vào clipboard!', 'success');
    }
}

// Mobile menu toggle
document.addEventListener('DOMContentLoaded', () => {
    const navbarToggle = document.getElementById('navbarToggle');
    const navbarMenu = document.querySelector('.navbar-menu');

    if (navbarToggle && navbarMenu) {
        navbarToggle.addEventListener('click', () => {
            navbarMenu.classList.toggle('active');
        });

        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!navbarToggle.contains(e.target) && !navbarMenu.contains(e.target)) {
                navbarMenu.classList.remove('active');
            }
        });
    }
});