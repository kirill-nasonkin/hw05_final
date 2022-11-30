from django.test import TestCase

from ..constants import FIRST_15
from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="Тестовый слаг",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=(
                "Тестовый пост длиной более 15 символов для проверки"
                "работы среза в __str__"
            ),
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group = PostModelTest.group
        post = PostModelTest.post
        expected_group_name = group.title
        expected_post_name = post.text[:FIRST_15]
        self.assertEqual(expected_group_name, str(group))
        self.assertEqual(expected_post_name, str(post))

    def test_post_help_text(self):
        """help_text в полях у модели Post соответствует ожиданиям."""
        post = PostModelTest.post
        field_help_texts = (
            ("text", "Введите текст поста"),
            ("group", "Группа, к которой будет относиться пост"),
        )
        for field, expected_value in field_help_texts:
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value
                )

    def test_post_verbose_name(self):
        """verbose_name в полях у модели Post соответствует ожиданиям."""
        post = PostModelTest.post
        field_verbose_names = (
            ("text", "Текст поста"),
            ("pub_date", "Дата публикации"),
            ("author", "Автор"),
            ("group", "Группа"),
        )
        for field, expected_value in field_verbose_names:
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value
                )
