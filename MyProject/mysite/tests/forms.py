from django import forms
from .models import Question, AnswerOption

class TestSubmissionForm(forms.Form):
    def __init__(self, *args, questions=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.questions = questions or []

        for question in self.questions:
            choices = [
                (option.id, option.text)
                for option in question.options.all().order_by("order")
            ]
            self.fields[f"q_{question.id}"] = forms.ChoiceField(
                label=question.text,
                choices=choices,
                required=question.is_required,
                widget=forms.RadioSelect,
            )

    def clean(self):
        cleaned_data = super().clean()
        for question in self.questions:
            field_name = f"q_{question.id}"
            selected_option_id = cleaned_data.get(field_name)
            if not selected_option_id:
                continue
            exists = AnswerOption.objects.filter(
                id=selected_option_id,
                question=question
            ).exists()
            if not exists:
                raise forms.ValidationError(
                    f"Некорректный вариант ответа для вопроса: {question.text}"
                )
        return cleaned_data
