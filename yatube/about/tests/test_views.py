from django.test import Client, TestCase
from django.urls import reverse


class AboutViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()

    def test_about_urls_use_correct_templates(self):
        """URL-адрес использует соответствующий шаблон."""
        urls_templates = (
            (reverse("about:author"), "about/author.html"),
            (reverse("about:tech"), "about/tech.html"),
        )
        for url, template in urls_templates:
            with self.subTest(url=url):
                response = AboutViewsTests.guest_client.get(url)
                self.assertTemplateUsed(response, template)
