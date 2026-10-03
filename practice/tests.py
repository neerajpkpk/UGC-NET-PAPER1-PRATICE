from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase

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
