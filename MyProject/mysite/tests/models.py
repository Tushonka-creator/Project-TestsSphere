from django.db import models
from .fields import EncryptedCharField


class Test(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField(blank=True)
    is_published = models.BooleanField(default=False)

    # порядок вывода на главной/в списках
    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


class Question(models.Model):
    test = models.ForeignKey("Test", on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    order = models.PositiveIntegerField()
    is_required = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]
        # unique_together = ("test", "order")

    def __str__(self):
        return f"{self.test.title} — Q{self.order + 1}"


class AnswerOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="options")
    text = models.CharField(max_length=255)
    score = models.IntegerField(default=0)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ["order"]
    def __str__(self):
        return f"Option({self.question.id}): {self.text[:40]}"


class Submission(models.Model):
    user = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="submissions"
    )
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="submissions")
    session_key = models.CharField(max_length=40, blank=True, db_index=True)
    total_score = models.IntegerField(default=0)
    magma_sealed_data = EncryptedCharField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Submission #{self.id} — {self.test.title}"

    @property
    def duration(self):
        if self.finished_at and self.created_at:
            return (self.finished_at - self.created_at).total_seconds()
        return None


class SubmissionAnswer(models.Model):

    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    option = models.ForeignKey(AnswerOption, on_delete=models.PROTECT)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["submission", "question"], name="uniq_submission_question")
        ]

    def __str__(self):
        return f"SubmissionAnswer(sub={self.submission_id}, q={self.question_id})"


class ResultRange(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="result_ranges")
    min_score = models.IntegerField()
    max_score = models.IntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "min_score", "id"]

    def __str__(self):
        return f"{self.test.title}: {self.min_score}-{self.max_score} - {self.title}"
