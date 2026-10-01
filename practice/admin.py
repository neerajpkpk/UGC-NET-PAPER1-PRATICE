from django.contrib import admin

from .forms import QuestionForm, SubjectForm
from .models import Question, Subject


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    form = SubjectForm
    list_display = ("name", "slug", "total_questions", "created_at")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    form = QuestionForm
    list_display = (
        "subject",
        "question_order",
        "question_type",
        "exam_date",
        "pyq_year",
        "shift",
        "difficulty",
        "correct_answer",
        "created_at",
    )
    list_filter = ("subject", "question_type", "exam_date", "pyq_year", "shift", "difficulty")
    search_fields = ("question_text", "subject__name")
    ordering = ("subject", "question_order")
    fieldsets = (
        (
            "Question Details",
            {
                "fields": (
                    "subject",
                    "question_order",
                    "question_text",
                    "difficulty",
                    "question_type",
                    "exam_date",
                    "pyq_year",
                    "shift",
                )
            },
        ),
        (
            "Options",
            {
                "fields": (
                    "option_a",
                    "option_b",
                    "option_c",
                    "option_d",
                    "correct_answer",
                )
            },
        ),
        (
            "Explanation",
            {"fields": ("explanation",)},
        ),
    )
