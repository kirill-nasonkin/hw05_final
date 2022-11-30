from django.test import Client, TestCase
from django.urls import reverse

from ..constants import POSTS_PER_PAGE
from ..models import Group, Post, User


class PaginatorViewsTest(TestCase):
    TOTAL: int = 13
    REMAINDER: int = TOTAL - POSTS_PER_PAGE

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username="anonymous")
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-group",
            description="Тестовое описание",
        )

        for post_number in range(cls.TOTAL):
            cls.post = Post.objects.create(
                text=f"Это пост номер: {post_number}. Тестовый текст",
                author=cls.user,
                group=cls.group,
            )

    def test_first_page_contains_ten_records(self):
        """Проверка: на первой странице должно быть POSTS_PER_PAGE постов."""
        urls_quantity = (
            (reverse("posts:index"), POSTS_PER_PAGE),
            (
                reverse(
                    "posts:group_list",
                    kwargs={"slug": f"{PaginatorViewsTest.group.slug}"},
                ),
                POSTS_PER_PAGE,
            ),
            (
                reverse(
                    "posts:profile",
                    kwargs={"username": f"{PaginatorViewsTest.user.username}"},
                ),
                POSTS_PER_PAGE,
            ),
        )
        for reverse_name, quantity in urls_quantity:
            with self.subTest(reverse_name=reverse_name):
                response = PaginatorViewsTest.authorized_client.get(
                    reverse_name
                )
            self.assertEqual(len(response.context["page_obj"]), quantity)

    def test_second_page_contains_three_records(self):
        """Проверка: на второй странице должно быть REMAINDER постов."""
        urls_quantity = (
            (reverse("posts:index"), self.REMAINDER),
            (
                reverse(
                    "posts:group_list",
                    kwargs={"slug": f"{PaginatorViewsTest.group.slug}"},
                ),
                self.REMAINDER,
            ),
            (
                reverse(
                    "posts:profile",
                    kwargs={"username": f"{PaginatorViewsTest.user.username}"},
                ),
                self.REMAINDER,
            ),
        )
        for reverse_name, quantity in urls_quantity:
            with self.subTest(reverse_name=reverse_name):
                response = PaginatorViewsTest.authorized_client.get(
                    reverse_name + "?page=2"
                )
            self.assertEqual(len(response.context["page_obj"]), quantity)
