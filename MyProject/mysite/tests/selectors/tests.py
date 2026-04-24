from django.shortcuts import get_object_or_404
from ..models import Test

def get_published_tests():
    """Возвращает список всех опубликованных тестов."""
    return Test.objects.filter(is_published=True).order_by("order", "id")

def get_published_test_by_slug(slug: str):
    """Ищет опубликованный тест по его slug."""
    return get_object_or_404(Test, slug=slug, is_published=True)

def get_test_questions_with_options(test):
    """Возвращает вопросы теста с предзагруженными вариантами ответов."""
    return test.questions.all().prefetch_related("options")
