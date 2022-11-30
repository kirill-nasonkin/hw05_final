from django.test import Client, TestCase


class ViewTestClass(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_error_page_status(self):
        """Неверный адрес возвращает статус 404."""
        response = self.guest_client.get("/nonexist-page/")
        self.assertEqual(response.status_code, 404)

    def test_404_template_used(self):
        """Используется шаблон core/404.html."""
        response = self.guest_client.get("/nonexist-page/")
        self.assertTemplateUsed(response, "core/404.html")
