from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from ..models import User


class UsersFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.guest_client = Client()

    def test_signup_form_creates_user(self):
        """Форма регистрации создаёт пользователя."""
        data_form = {
            "first_name": "Иван",
            "last_name": "Иванович",
            "username": "ivan",
            "email": "ivan@gmail.com",
        }
        response = UsersFormsTests.guest_client.post(
            reverse("users:signup"), data=data_form, follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIsNotNone(User.objects.filter(username="ivan"))
