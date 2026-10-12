from math import ceil

from django.contrib.sitemaps import Sitemap
from django.db.models import Count
from django.urls import reverse

from .models import QUESTIONS_PER_PRACTICE, Subject


class StaticSitemap(Sitemap):
    protocol = "https"

    def items(self):
        return ["home", "questions_index"]

    def location(self, item):
        return reverse(item)


class SubjectSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    protocol = "https"

    def items(self):
        return (
            Subject.objects.filter(questions__isnull=False)
            .distinct()
            .order_by("slug")
        )

    def location(self, item):
        return reverse("subject_detail", kwargs={"slug": item.slug})


class SubjectQuestionsSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    protocol = "https"

    def items(self):
        subjects = (
            Subject.objects.filter(questions__isnull=False)
            .annotate(question_total=Count("questions", distinct=True))
            .distinct()
            .order_by("slug")
        )
        return [
            (subject.slug, page_number)
            for subject in subjects
            for page_number in range(1, ceil(subject.question_total / 100) + 1)
        ]

    def location(self, item):
        slug, page_number = item
        url = reverse("subject_questions", kwargs={"slug": slug})
        return f"{url}?page={page_number}" if page_number > 1 else url


class PracticeSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7
    protocol = "https"

    def items(self):
        subjects = (
            Subject.objects.filter(questions__isnull=False)
            .annotate(question_total=Count("questions", distinct=True))
            .order_by("slug")
        )
        return [
            (subject.slug, practice_number)
            for subject in subjects
            for practice_number in range(
                1,
                ceil(subject.question_total / QUESTIONS_PER_PRACTICE) + 1,
            )
        ]

    def location(self, item):
        slug, practice_number = item
        return reverse(
            "practice_detail",
            kwargs={"slug": slug, "practice_number": practice_number},
        )
