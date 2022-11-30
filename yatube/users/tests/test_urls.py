from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from ..models import User


class UsersURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.guest_client = Client()

        cls.user = User.objects.create(username="anonymous")
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_users_urls_unauthorized(self):
        """Доступность URLs для неавторизованного пользователя."""
        signup = reverse("users:signup")
        response = UsersURLTests.guest_client.get(signup)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_users_urls_work_correctly(self):
        """Адреса работают корректно."""
        urls = (
            reverse("users:signup"),
            reverse("users:password_reset_form"),
            reverse("users:password_reset_done"),
            reverse(
                "users:password_reset_confirm",
                kwargs={"uidb64": "123", "token": "123123123"},
            ),
            reverse("users:password_reset_complete"),
            reverse("users:password_change_form"),
            reverse("users:password_change_done"),
            reverse("users:login"),
            reverse("users:logout"),
        )
        for url in urls:
            with self.subTest(url=url):
                response = UsersURLTests.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
