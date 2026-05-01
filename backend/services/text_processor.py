import re

class TextProcessor:

    @staticmethod
    def clean_text(text):
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text

    @staticmethod
    def split_into_words(text):
        text = TextProcessor.clean_text(text)
        words = [word.strip() for word in text.split() if word.strip()]
        return words

    @staticmethod
    def get_word_count(text):
        words = TextProcessor.split_into_words(text)
        return len(words)

    @staticmethod
    def truncate_text(text, max_length=100):
        if len(text) <= max_length:
            return text
        return text[:max_length] + '...'