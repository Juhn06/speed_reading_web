"""
Text Processor Service
Xử lý văn bản: tách từ, clean text
"""
import re


class TextProcessor:
    """Xử lý text"""

    @staticmethod
    def clean_text(text):
        """
        Làm sạch text
        - Xóa ký tự đặc biệt thừa
        - Chuẩn hóa khoảng trắng
        """
        # Xóa nhiều khoảng trắng thành 1
        text = re.sub(r'\s+', ' ', text)
        # Xóa khoảng trắng đầu cuối
        text = text.strip()
        return text

    @staticmethod
    def split_into_words(text):
        """
        Tách text thành từng từ
        Args:
            text: Văn bản
        Returns:
            list: Danh sách từ
        """
        # Clean text trước
        text = TextProcessor.clean_text(text)
        # Split thành từ, lọc bỏ từ rỗng
        words = [word.strip() for word in text.split() if word.strip()]
        return words

    @staticmethod
    def get_word_count(text):
        """Đếm số từ"""
        words = TextProcessor.split_into_words(text)
        return len(words)

    @staticmethod
    def truncate_text(text, max_length=100):
        """Cắt text về độ dài tối đa"""
        if len(text) <= max_length:
            return text
        return text[:max_length] + '...'