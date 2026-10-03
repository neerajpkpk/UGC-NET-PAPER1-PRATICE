from unittest.mock import patch

from django.test import SimpleTestCase


class HealthEndpointTests(SimpleTestCase):
    @patch(
        "django.db.backends.base.base.BaseDatabaseWrapper.ensure_connection",
        side_effect=AssertionError("Health endpoint must not connect to the database."),
    )
    def test_health_endpoint_is_public_and_does_not_connect_to_database(self, _):
        response = self.client.get("/health/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"ok")
