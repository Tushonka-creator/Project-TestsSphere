from django.db import models
from .crypto import encrypt_text, decrypt_text

class EncryptedCharField(models.TextField):
    description = "Зашифрованная строка (Магма)"

    def get_prep_value(self, value):
        if value is None:
            return value
        return encrypt_text(str(value))

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return decrypt_text(value)

    def to_python(self, value):
        if value is None or not isinstance(value, str):
            return value
        if len(value) > 12 and "=" in value: # Эвристика для Base64
             return decrypt_text(value)
        return value
