import csv
from io import StringIO

from django.contrib import admin
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Max
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils.translation import gettext_lazy as _

from .csv_import import QuestionCSVImportError, parse_questions_csv
from .forms import QuestionCSVImportForm, QuestionForm, SubjectForm
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
    change_list_template = "admin/practice/question/change_list.html"
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

    def get_urls(self):
        custom_urls = [
            path(
                "import-csv/",
                self.admin_site.admin_view(self.import_csv_view),
                name="practice_question_import_csv",
            ),
            path(
                "import-csv/template/",
                self.admin_site.admin_view(self.csv_template_view),
                name="practice_question_csv_template",
            ),
        ]
        return custom_urls + super().get_urls()

    def import_csv_view(self, request):
        if not self.has_add_permission(request):
            raise PermissionDenied

        form = QuestionCSVImportForm(request.POST or None, request.FILES or None)
        import_errors = []
        if request.method == "POST" and form.is_valid():
            try:
                with transaction.atomic():
                    subject = Subject.objects.select_for_update().get(
                        pk=form.cleaned_data["subject"].pk
                    )
                    last_order = Question.objects.filter(subject=subject).aggregate(
                        maximum=Max("question_order")
                    )["maximum"] or 0
                    questions = parse_questions_csv(
                        form.cleaned_data["csv_file"],
                        {},
                        selected_subject=subject,
                        starting_order=last_order + 1,
                    )
                    Question.objects.bulk_create(questions)
            except QuestionCSVImportError as error:
                import_errors = str(error).splitlines()
            else:
                self.message_user(
                    request,
                    _("%(count)s questions imported successfully.")
                    % {"count": len(questions)},
                    messages.SUCCESS,
                )
                return redirect(
                    reverse(
                        f"{self.admin_site.name}:practice_question_changelist",
                    )
                )

        context = {
            **self.admin_site.each_context(request),
            "opts": self.model._meta,
            "title": _("Import questions from CSV"),
            "form": form,
            "import_errors": import_errors,
        }
        return render(request, "admin/practice/question/import_csv.html", context)

    def csv_template_view(self, request):
        if not self.has_add_permission(request):
            raise PermissionDenied

        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(
            [
                "question_text",
                "option_a",
                "option_b",
                "option_c",
                "option_d",
                "correct_answer",
                "explanation",
                "question_type",
                "difficulty",
                "exam_date",
                "pyq_year",
                "shift",
            ]
        )
        response = HttpResponse(output.getvalue(), content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="questions-template.csv"'
        return response
