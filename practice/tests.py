from types import SimpleNamespace
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase

from .csv_import import QuestionCSVImportError, parse_questions_csv
from .models import Subject
from .sitemaps import PracticeSitemap, SubjectSitemap


class HealthEndpointTests(SimpleTestCase):
    @patch(
        "django.db.backends.base.base.BaseDatabaseWrapper.ensure_connection",
        side_effect=AssertionError("Health endpoint must not connect to the database."),
    )
    def test_health_endpoint_is_public_and_does_not_connect_to_database(self, _):
        response = self.client.get("/health/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"ok")


class SeoEndpointTests(SimpleTestCase):
    def test_robots_txt_points_to_sitemap_and_excludes_private_paths(self):
        response = self.client.get("/robots.txt", secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/plain")
        self.assertContains(response, "Disallow: /admin/")
        self.assertContains(response, "Disallow: /health/")
        self.assertContains(
            response,
            "Sitemap: https://testserver/sitemap.xml",
        )

    @patch.object(
        SubjectSitemap,
        "items",
        return_value=[SimpleNamespace(slug="teaching-aptitude")],
    )
    @patch.object(
        PracticeSitemap,
        "items",
        return_value=[("teaching-aptitude", 1)],
    )
    def test_sitemap_lists_homepage_subjects_and_practice_sessions(self, _, __):
        response = self.client.get("/sitemap.xml", secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "https://testserver/")
        self.assertContains(
            response,
            "https://testserver/subject/teaching-aptitude/",
        )
        self.assertContains(
            response,
            "https://testserver/subject/teaching-aptitude/practice/1/",
        )

    @patch("practice.views.Subject.objects.all")
    def test_homepage_has_search_metadata_and_canonical_url(self, subjects):
        subjects.return_value = [
            SimpleNamespace(
                icon="book-open",
                name="Teaching Aptitude",
                slug="teaching-aptitude",
                total_questions=3,
            )
        ]

        response = self.client.get(
            "/?utm_source=test",
            secure=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "<title>UGC NET Paper 1 Online Practice Questions</title>",
            html=True,
        )
        self.assertContains(
            response,
            '<link rel="canonical" href="https://testserver/" />',
            html=True,
        )
        self.assertContains(
            response,
            "Practise UGC NET Paper 1 questions online by subject.",
        )

    @patch("practice.views.Subject.objects.filter")
    def test_empty_subject_page_is_noindex(self, subjects):
        subject = SimpleNamespace(
            slug="research-aptitude",
            name="Research Aptitude",
            get_practice_cards=lambda: [],
            total_questions=0,
        )
        subjects.return_value.first.return_value = subject

        response = self.client.get("/subject/research-aptitude/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<meta name="robots" content="noindex,follow" />', html=True)
        self.assertContains(response, "UGC NET Research Aptitude Practice Questions")


class QuestionCSVImportTests(SimpleTestCase):
    @patch("practice.csv_import.Question.full_clean")
    def test_import_parser_builds_question_with_defaults(self, full_clean):
        subject = Subject(id=7, name="Teaching Aptitude")
        content = (
            "subject,question_order,question_text,option_a,option_b,option_c,"
            "option_d,correct_answer\n"
            'Teaching Aptitude,2,"Which is correct, exactly?",A,B,C,D,b\n'
        ).encode()
        uploaded = SimpleUploadedFile("questions.csv", content, content_type="text/csv")

        questions = parse_questions_csv(uploaded, {subject.name: subject})

        self.assertEqual(len(questions), 1)
        question = questions[0]
        self.assertEqual(question.subject, subject)
        self.assertEqual(question.question_order, 2)
        self.assertEqual(question.question_text, "Which is correct, exactly?")
        self.assertEqual(question.correct_answer, "B")
        self.assertEqual(question.question_type, "Practice")
        self.assertEqual(question.difficulty, "Medium")
        full_clean.assert_called_once()

    def test_import_parser_rejects_unknown_subject_without_partial_import(self):
        content = (
            "subject,question_order,question_text,option_a,option_b,option_c,"
            "option_d,correct_answer\n"
            "Unknown Subject,1,Question,A,B,C,D,A\n"
        ).encode()
        uploaded = SimpleUploadedFile("questions.csv", content, content_type="text/csv")

        with self.assertRaisesRegex(QuestionCSVImportError, "unknown subject"):
            parse_questions_csv(uploaded, {})

    @patch("practice.csv_import.Question.full_clean")
    def test_import_parser_accepts_subject_id_column(self, full_clean):
        subject = Subject(id=7, name="Teaching Aptitude")
        content = (
            "question_order,question_text,option_a,option_b,option_c,option_d,"
            "correct_answer,subject_id\n"
            "2,Question,A,B,C,D,A,7\n"
        ).encode()
        uploaded = SimpleUploadedFile("questions.csv", content, content_type="text/csv")

        questions = parse_questions_csv(uploaded, {}, {subject.pk: subject})

        self.assertEqual(len(questions), 1)
        self.assertEqual(questions[0].subject, subject)
        full_clean.assert_called_once()

    @patch("practice.csv_import.Question.full_clean")
    def test_import_parser_assigns_order_for_selected_subject(self, full_clean):
        subject = Subject(id=7, name="Teaching Aptitude")
        content = (
            "question_text,option_a,option_b,option_c,option_d,correct_answer\n"
            "First question,A,B,C,D,A\n"
            "Second question,A,B,C,D,B\n"
        ).encode()
        uploaded = SimpleUploadedFile("questions.csv", content, content_type="text/csv")

        questions = parse_questions_csv(
            uploaded,
            {},
            selected_subject=subject,
            starting_order=12,
        )

        self.assertEqual([question.question_order for question in questions], [12, 13])
        self.assertEqual([question.subject for question in questions], [subject, subject])
        self.assertEqual(full_clean.call_count, 2)

    def test_import_parser_rejects_duplicate_question_orders(self):
        subject = Subject(id=7, name="Teaching Aptitude")
        content = (
            "subject,question_order,question_text,option_a,option_b,option_c,"
            "option_d,correct_answer\n"
            "Teaching Aptitude,2,First,A,B,C,D,A\n"
            "Teaching Aptitude,2,Second,A,B,C,D,B\n"
        ).encode()
        uploaded = SimpleUploadedFile("questions.csv", content, content_type="text/csv")

        with patch("practice.csv_import.Question.full_clean"):
            with self.assertRaisesRegex(QuestionCSVImportError, "also used in row 2"):
                parse_questions_csv(uploaded, {subject.name: subject})
