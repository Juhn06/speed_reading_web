/**
 * Admin Functions
 * Các hàm cho trang admin
 */

// Search and filter functions
document.addEventListener('DOMContentLoaded', () => {
    // Search input
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(handleSearch, 300));
    }

    // Filter selects
    const filters = ['roleFilter', 'statusFilter', 'typeFilter', 'dateFilter', 'sortBy'];
    filters.forEach(filterId => {
        const filter = document.getElementById(filterId);
        if (filter) {
            filter.addEventListener('change', handleFilter);
        }
    });
});

// Handle search
function handleSearch(e) {
    const searchTerm = e.target.value.toLowerCase();
    const table = document.querySelector('.admin-table tbody');

    if (!table) return;

    const rows = table.getElementsByTagName('tr');

    for (let row of rows) {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(searchTerm) ? '' : 'none';
    }
}

// Handle filter
function handleFilter() {
    console.log('Filter changed');
    // TODO: Implement filter logic or reload page with filter params
}

// Delete user (admin)
async function deleteUser(userId, username) {
    if (!confirm(`Bạn chắc chắn muốn xóa user "${username}"?\n\nTất cả dữ liệu liên quan sẽ bị xóa vĩnh viễn!`)) {
        return;
    }

    try {
        showLoading('Đang xóa user...');

        const response = await fetch(`/admin/delete-user/${userId}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        hideLoading();

        if (data.success) {
            showAlert(data.message, 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            showAlert(data.error || 'Có lỗi xảy ra!', 'danger');
        }
    } catch (error) {
        hideLoading();
        showAlert('Lỗi xóa user: ' + error.message, 'danger');
    }
}

// View user details
function viewUserDetails(userId) {
    // TODO: Open modal with user details
    showAlert(`Xem chi tiết user ID: ${userId}`, 'info');
}

// Export data
function exportData(type) {
    showAlert(`Xuất dữ liệu ${type}...`, 'info');
    // TODO: Implement export functionality
}
```

---

## FILE `.gitignore` - CẬP NHẬT
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
ENV/

# Database
*.db
*.sqlite
*.sqlite3
instance/

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Uploads
uploads/*
!uploads/.gitkeep

# Logs
*.log

# Distribution
dist/
build/
*.egg-info/
```

---

## FILE `uploads/.gitkeep` - Tạo file trống
```
# File này để giữ folder uploads trong git
```

---

# 🎉 HOÀN THÀNH TẤT CẢ CODE!

---

## TỔNG KẾT CẤU TRÚC HOÀN CHỈNH:
```
speed_reading/
├── models/
│   ├── __init__.py
│   ├── user.py
│   ├── document.py
│   └── reading_session.py
│
├── routes/
│   ├── __init__.py
│   ├── auth.py
│   ├── main.py
│   ├── reading.py
│   ├── user.py
│   └── admin.py
│
├── services/
│   ├── __init__.py
│   ├── file_handler.py
│   ├── text_processor.py
│   └── stats_calculator.py
│
├── utils/
│   ├── __init__.py
│   ├── decorators.py
│   └── validators.py
│
├── config/
│   ├── __init__.py
│   ├── settings.py
│   └── database.py
│
├── templates/
│   ├── base.html
│   ├── components/ (navbar, footer, flash, pagination)
│   ├── home/ (index.html)
│   ├── auth/ (login, register, profile)
│   ├── reading/ (upload, reader, history, documents)
│   └── admin/ (dashboard, users, documents, sessions)
│
├── static/
│   ├── css/ (base, components, layout, pages, admin)
│   └── js/ (utils, api, reader, charts, admin)
│
├── instance/ (auto-generated)
├── uploads/
├── app.py
├── requirements.txt
├── .env
└── .gitignore