from dataclasses import dataclass
from typing import Dict, List
from django.db import transaction
from ..models import AnswerOption, Submission, SubmissionAnswer
from ..services.scoring import ScoreCalculator


@dataclass
class SubmissionValidationResult:
    chosen: Dict[int, str]
    errors: set[int]


class SubmissionService:
    def __init__(self, score_calculator=None):
        self.score_calculator = score_calculator or ScoreCalculator()

    def parse_answers(self, questions, post_data) -> SubmissionValidationResult:
        chosen: Dict[int, str] = {}
        errors: set[int] = set()

        for question in questions:
            key = f"q_{question.id}"
            option_id = post_data.get(key)

            if question.is_required and not option_id:
                errors.add(question.id)
                continue

            if option_id:
                chosen[question.id] = option_id

        return SubmissionValidationResult(chosen=chosen, errors=errors)

    @transaction.atomic
    def create_submission(self, test, session_key: str, questions, chosen_answers: Dict[int, str], user=None,
                          duration=None):
        from django.utils import timezone
        import datetime

        finished_at = timezone.now()


        submission = Submission.objects.create(
            test=test,
            user=user if user and user.is_authenticated else None,
            session_key=session_key,
            total_score=0,
            finished_at=finished_at
        )


        if duration is not None:
            new_created_at = finished_at - datetime.timedelta(seconds=duration)
            Submission.objects.filter(pk=submission.pk).update(created_at=new_created_at)
            submission.created_at = new_created_at

        options_map = {
            option.id: option
            for option in AnswerOption.objects.filter(
                id__in=chosen_answers.values()
            ).select_related("question")
        }

        selected_options: List[AnswerOption] = []
        answers_to_create: List[SubmissionAnswer] = []

        for question in questions:
            option_id = chosen_answers.get(question.id)
            if not option_id:
                continue

            try:
                option = options_map.get(int(option_id))
            except (ValueError, TypeError):
                continue

            if not option:
                continue

            if option.question_id != question.id:
                continue

            selected_options.append(option)
            answers_to_create.append(
                SubmissionAnswer(
                    submission=submission,
                    question=question,
                    option=option,
                )
            )

        SubmissionAnswer.objects.bulk_create(answers_to_create)

        duration = (submission.finished_at - submission.created_at).total_seconds()
        total_score = self.score_calculator.calculate(selected_options, duration=duration)

        submission.total_score = total_score

        from django.utils import timezone
        summary = f"Score: {total_score} recorded at {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
        submission.magma_sealed_data = summary

        submission.save(update_fields=["total_score", "magma_sealed_data"])

        return submission
