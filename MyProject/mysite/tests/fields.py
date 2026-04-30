from django.db import models
from .crypto import encrypt_text, decrypt_text

class EncryptedCharField(models.TextField):
    """
    Поле, которое автоматически шифрует данные алгоритмом Магма перед сохранением.
    """
    description = "Зашифрованная строка (Магма)"

    def get_prep_value(self, value):
        if value is None:
            return value
        # Шифруем только строки
        return encrypt_text(str(value))

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return decrypt_text(value)

    def to_python(self, value):
        if value is None or not isinstance(value, str):
            return value
        # Если значение похоже на Base64 (т.е. зашифровано), пробуем расшифровать
        # В идеале здесь должна быть логика проверки префикса или структуры
        if len(value) > 12 and "=" in value: # Эвристика для Base64
             return decrypt_text(value)
        return value
