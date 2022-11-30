from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from ..models import User


class UserViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.guest_client = Client()

        cls.user = User.objects.create(username="user")
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_users_urls_use_correct_templates(self):
        """URL-адреса используют соответствующие шаблоны."""
        urls_templates = (
            (reverse("users:signup"), "users/signup.html"),
            (
                reverse("users:password_reset_form"),
                "users/password_reset_form.html",
            ),
            (
                reverse("users:password_reset_done"),
                "users/password_reset_done.html",
            ),
            (
                reverse(
                    "users:password_reset_confirm",
                    kwargs={"uidb64": "123", "token": "123123123"},
                ),
                "users/password_reset_confirm.html",
            ),
            (
                reverse("users:password_reset_complete"),
                "users/password_reset_complete.html",
            ),
            (
                reverse("users:password_change_form"),
                "users/password_change_form.html",
            ),
            (
                reverse("users:password_change_done"),
                "users/password_change_done.html",
            ),
            (reverse("users:login"), "users/login.html"),
            (reverse("users:logout"), "users/logged_out.html"),
        )
        for url, template in urls_templates:
            with self.subTest(url=url):
                response = UserViewsTests.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_users_signup_shows_correct_form(self):
        """Шаблон users_signup сформирован с правильным контекстом."""
        response = UserViewsTests.guest_client.get(reverse("users:signup"))
        form_fields = (
            ("first_name", forms.fields.CharField),
            ("last_name", forms.fields.CharField),
            ("username", forms.fields.CharField),
            ("email", forms.fields.EmailField),
        )
        for value, expected in form_fields:
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)
