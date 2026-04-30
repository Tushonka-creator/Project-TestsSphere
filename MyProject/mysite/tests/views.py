from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.db.models import Q

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
    from .models import Submission
    test = get_published_test_by_slug(slug)
    questions = list(get_test_questions_with_options(test))

    if not request.session.session_key:
        request.session.save()

    if 'original_session_key' not in request.session:
        request.session['original_session_key'] = request.session.session_key

    request.session.modified = True
    request.session.save()

    submission_service = SubmissionService()

    if request.method == 'POST':
        validation = submission_service.parse_answers(questions, request.POST)

        if validation.errors:
            for q in questions:
                q.selected_option_id = validation.chosen.get(q.id)

            return render(request, 'tests/test_detail.html', {
                'test': test,
                'questions': questions,
                'errors': validation.errors,
                'start_time': request.POST.get('start_time')
            })

        duration = None
        start_time_ms = request.POST.get('start_time')
        if start_time_ms:
            try:
                import time
                duration = (int(time.time() * 1000) - int(start_time_ms)) / 1000.0
            except (ValueError, TypeError):
                pass

        submission = submission_service.create_submission(
            test=test,
            session_key=request.session.session_key or "",
            questions=questions,
            chosen_answers=validation.chosen,
            user=request.user,
            duration=duration
        )

        if 'submission_ids' not in request.session:
            request.session['submission_ids'] = []
        request.session['submission_ids'].append(submission.id)
        request.session.modified = True

        return redirect('tests:test_result', pk=submission.pk)

    return redirect('tests:test_detail', slug=slug)


def debug_submissions(request):
    from .models import Submission
    from django.contrib.auth.models import User
    from django.http import HttpResponse

    users = User.objects.all()
    subs = Submission.objects.all().order_by('-id')[:100]

    output = "<h1>Debug info</h1>"
    output += f"<p>Current user in request: {request.user} (Auth: {request.user.is_authenticated}, ID: {request.user.id if request.user.is_authenticated else 'N/A'})</p>"
    output += f"<p>Current session key: {request.session.session_key}</p>"
    output += f"<p>Original session key: {request.session.get('original_session_key')}</p>"
    output += f"<p>Submission IDs in session: {request.session.get('submission_ids')}</p>"

    output += "<h2>Users</h2><ul>"
    for u in users:
        output += f"<li>{u.username} (ID: {u.id}), Submissions: {u.submissions.count()}</li>"
    output += "</ul>"

    output += "<h2>Recent Submissions</h2><table border='1'><tr><th>ID</th><th>Test</th><th>User</th><th>Score</th><th>Magma Decrypted</th><th>Raw (Encrypted)</th></tr>"
    for s in subs:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT magma_sealed_data FROM tests_submission WHERE id=%s", [s.id])
            row = cursor.fetchone()
            raw_magma = row[0] if row else "N/A"

        output += f"<tr><td>{s.id}</td><td>{s.test.title}</td><td>{s.user}</td><td>{s.total_score}</td><td>{s.magma_sealed_data}</td><td style='font-family:monospace; font-size:10px;'>{raw_magma}</td></tr>"
    output += "</table>"
    return HttpResponse(output)


@login_required
def profile_view(request):
    from .models import Submission
    """
    Личный кабинет: история прохождения тестов пользователем.
    """
    user = request.user

    submission_ids = request.session.get('submission_ids', [])
    if submission_ids:
        Submission.objects.filter(id__in=submission_ids, user__isnull=True).update(user=user)

    original_session_key = request.session.get('original_session_key')
    current_session_key = request.session.session_key
    keys_to_check = [k for k in [original_session_key, current_session_key] if k]
    if keys_to_check:
        Submission.objects.filter(user__isnull=True, session_key__in=keys_to_check).update(user=user)

    submissions = user.submissions.all().order_by('-created_at').select_related('test')

    return render(request, 'tests/profile.html', {
        'submissions': list(submissions),
        'debug_count': submissions.count()
    })


def register_view(request):
    from django.contrib.auth.forms import UserCreationForm
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


def test_result(request, pk):
    from .models import Submission
    submission = get_object_or_404(Submission, pk=pk)


    if request.user.is_authenticated and submission.user is None:
        original_session_key = request.session.get('original_session_key')
        current_session_key = request.session.session_key
        if submission.session_key in [original_session_key, current_session_key]:
            submission.user = request.user
            submission.save(update_fields=['user'])

    result_service = ResultRangeService()

    result = result_service.get_result_for_score(submission.test, submission.total_score)

    return render(request, 'tests/test_result.html', {
        'submission': submission,
        'result': result,
        'test': submission.test
    })


def test_list(request, *args, **kwargs):
    return TestListView.as_view()(request, *args, **kwargs)


def test_detail(request, *args, **kwargs):
    return TestDetailView.as_view()(request, *args, **kwargs)
