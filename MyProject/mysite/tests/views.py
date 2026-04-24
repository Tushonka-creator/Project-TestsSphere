from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required

from .models import Submission
from .selectors.tests import (
    get_published_tests,
    get_published_test_by_slug,
    get_test_questions_with_options
)
from .services.submission import SubmissionService
from .services.result_range import ResultRangeService


class TestListView(ListView):
    template_name = 'tests/test_list.html'
    context_object_name = 'tests'

    def get_queryset(self):
        return get_published_tests()


class TestDetailView(DetailView):
    template_name = 'tests/test_detail.html'
    context_object_name = 'test'

    def get_object(self):
        return get_published_test_by_slug(self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['questions'] = get_test_questions_with_options(self.object)
        return context


def submit_test(request, slug):
    test = get_published_test_by_slug(slug)
    # Преобразуем в список, чтобы привязывать временные атрибуты
    questions = list(get_test_questions_with_options(test))

    submission_service = SubmissionService()

    if request.method == 'POST':
        validation = submission_service.parse_answers(questions, request.POST)

        if validation.errors:
            # Если есть ошибки, привязываем выбранные ответы к вопросам для отображения в шаблоне
            for q in questions:
                q.selected_option_id = validation.chosen.get(q.id)

            return render(request, 'tests/test_detail.html', {
                'test': test,
                'questions': questions,
                'errors': validation.errors,
            })

        submission = submission_service.create_submission(
            test=test,
            session_key=request.session.session_key or "",
            questions=questions,
            chosen_answers=validation.chosen,
            user=request.user
        )

        return redirect('test_result', pk=submission.pk)

    return redirect('test_detail', slug=slug)


@login_required
def profile_view(request):
    """
    Личный кабинет: история прохождения тестов пользователем.
    """
    submissions = Submission.objects.filter(user=request.user).order_by('-created_at').select_related('test')
    return render(request, 'tests/profile.html', {
        'submissions': submissions
    })


def test_result(request, pk):
    submission = get_object_or_404(Submission, pk=pk)
    result_service = ResultRangeService()

    result = result_service.get_result_for_score(submission.test, submission.total_score)

    return render(request, 'tests/test_result.html', {
        'submission': submission,
        'result': result,
        'test': submission.test
    })
