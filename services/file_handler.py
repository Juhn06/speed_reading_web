"""
File Handler Service
Xử lý đọc file txt, docx, pdf
"""
import os
from docx import Document as DocxDocument
import PyPDF2


class FileHandler:
    """Xử lý file upload"""

    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}

    @staticmethod
    def allowed_file(filename):
        """Kiểm tra file hợp lệ"""
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in FileHandler.ALLOWED_EXTENSIONS

    @staticmethod
    def read_file(filepath):
        """
        Đọc nội dung file
        Args:
            filepath: Đường dẫn file
        Returns:
            str: Nội dung văn bản
        """
        ext = filepath.rsplit('.', 1)[1].lower()

        try:
            if ext == 'txt':
                return FileHandler._read_txt(filepath)
            elif ext == 'docx':
                return FileHandler._read_docx(filepath)
            elif ext == 'pdf':
                return FileHandler._read_pdf(filepath)
            else:
                raise ValueError(f"Unsupported file type: {ext}")
        except Exception as e:
            raise Exception(f"Error reading {ext} file: {str(e)}")

    @staticmethod
    def _read_txt(filepath):
        """Đọc file .txt"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

    @staticmethod
    def _read_docx(filepath):
        """Đọc file .docx"""
        doc = DocxDocument(filepath)
        paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
        return '\n'.join(paragraphs)

    @staticmethod
    def _read_pdf(filepath):
        """Đọc file .pdf"""
        text = ''
        with open(filepath, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + '\n'
        return text.strip()

    @staticmethod
    def delete_file(filepath):
        """Xóa file"""
        if os.path.exists(filepath):
            os.remove(filepath)