/**
 * API Helper Functions
 * Các hàm gọi API
 */

const API = {
    // Base URL
    baseURL: '',

    // Upload file
    async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/reading/upload', {
                method: 'POST',
                body: formData
            });

            return await response.json();
        } catch (error) {
            throw new Error('Lỗi upload file: ' + error.message);
        }
    },

    // Load document
    async loadDocument(docId) {
        try {
            const response = await fetch(`/reading/load-document/${docId}`);
            return await response.json();
        } catch (error) {
            throw new Error('Lỗi tải tài liệu: ' + error.message);
        }
    },

    // Save reading session
    async saveSession(data) {
        try {
            const response = await fetch('/reading/save-session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            return await response.json();
        } catch (error) {
            throw new Error('Lỗi lưu phiên đọc: ' + error.message);
        }
    },

    // Delete session
    async deleteSession(sessionId) {
        try {
            const response = await fetch(`/user/delete-session/${sessionId}`, {
                method: 'DELETE'
            });

            return await response.json();
        } catch (error) {
            throw new Error('Lỗi xóa phiên đọc: ' + error.message);
        }
    },

    // Delete document
    async deleteDocument(docId) {
        try {
            const response = await fetch(`/user/delete-document/${docId}`, {
                method: 'DELETE'
            });

            return await response.json();
        } catch (error) {
            throw new Error('Lỗi xóa tài liệu: ' + error.message);
        }
    },

    // Get stats
    async getStats() {
        try {
            const response = await fetch('/api/stats');
            return await response.json();
        } catch (error) {
            throw new Error('Lỗi lấy thống kê: ' + error.message);
        }
    }
};