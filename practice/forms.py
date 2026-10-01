from django import forms

from .models import Question, Subject


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ["name", "slug", "description", "icon"]


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = [
            "subject",
            "question_text",
            "option_a",
            "option_b",
            "option_c",
            "option_d",
            "correct_answer",
            "explanation",
            "question_type",
            "exam_date",
            "pyq_year",
            "shift",
            "difficulty",
            "question_order",
        ]
