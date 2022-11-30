from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from ..models import User


class AboutURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.guest_client = Client()

    def test_about_urls_for_unauthorized(self):
        """Доступность URLs для неавторизованного пользователя."""
        urls_http_status = (
            (reverse("about:author"), HTTPStatus.OK),
            (reverse("about:tech"), HTTPStatus.OK),
        )
        for url, status in urls_http_status:
            with self.subTest(url=url):
                response = AboutURLTests.guest_client.get(url)
                self.assertEqual(response.status_code, status)
