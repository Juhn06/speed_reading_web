

const API = {
    baseURL: '',
    getTimezoneHeaders() {
        try {
            const tz = Intl.DateTimeFormat().resolvedOptions().timeZone || '';
            const offsetMinutes = -new Date().getTimezoneOffset();
            return {
                'X-Timezone': tz,
                'X-Timezone-Offset': String(offsetMinutes)
            };
        } catch (e) {
            return {};
        }
    },

    async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/reading/upload', {
                method: 'POST',
                headers: this.getTimezoneHeaders(),
                body: formData
            });

            return await response.json();
        } catch (error) {
            throw new Error('Lỗi upload file: ' + error.message);
        }
    },

    async loadDocument(docId) {
        try {
            const response = await fetch(`/reading/load-document/${docId}`);
            return await response.json();
        } catch (error) {
            throw new Error('Lỗi tải tài liệu: ' + error.message);
        }
    },

    async getDocumentContent(docId) {
        try {
            const response = await fetch(`/reading/document-content/${docId}`);
            return await response.json();
        } catch (error) {
            throw new Error('Lỗi tải nội dung tài liệu: ' + error.message);
        }
    },

    async saveSession(data) {
        try {
            const response = await fetch('/reading/save-session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...this.getTimezoneHeaders()
                },
                body: JSON.stringify(data)
            });

            return await response.json();
        } catch (error) {
            throw new Error('Lỗi lưu phiên đọc: ' + error.message);
        }
    },

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

    async getStats() {
        try {
            const response = await fetch('/api/stats');
            return await response.json();
        } catch (error) {
            throw new Error('Lỗi lấy thống kê: ' + error.message);
        }
    }
};
