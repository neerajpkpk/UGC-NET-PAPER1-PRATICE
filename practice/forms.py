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
            "exam_date",
            "pyq_year",
            "shift",
            "difficulty",
            "question_order",
        ]


class QuestionCSVImportForm(forms.Form):
    subject = forms.ModelChoiceField(
        label="Subject",
        queryset=Subject.objects.order_by("name"),
        help_text=(
            "All questions in this CSV will be added to this subject. "
            "Question order is assigned automatically."
        ),
    )
    csv_file = forms.FileField(
        label="CSV file",
        help_text=(
            "UTF-8 CSV, one question per row, up to 500 questions and 5 MB. "
            "Do not include subject or question_order columns. Imported questions are marked as PYQ."
        ),
    )

    def clean_csv_file(self):
        csv_file = self.cleaned_data["csv_file"]
        if csv_file.size > 5 * 1024 * 1024:
            raise forms.ValidationError("CSV file must be 5 MB or smaller.")
        return csv_file
