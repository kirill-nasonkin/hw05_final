from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.guest_client = Client()

        cls.user = User.objects.create(username="anonymous")
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.not_author = User.objects.create(username="not_author")
        cls.authorized_but_not_author = Client()
        cls.authorized_but_not_author.force_login(cls.not_author)

        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-group",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            text="Тестовый текст",
            author=cls.user,
            group=cls.group,
        )

    def test_posts_urls_for_unauthorized(self):
        """Доступность URLs для неавторизованного пользователя."""

        urls_http_status = (
            (reverse("posts:index"), HTTPStatus.OK),
            (
                reverse(
                    "posts:group_list",
                    kwargs={"slug": f"{PostURLTests.group.slug}"},
                ),
                HTTPStatus.OK,
            ),
            (
                reverse(
                    "posts:profile",
                    kwargs={"username": f"{PostURLTests.user.username}"},
                ),
                HTTPStatus.OK,
            ),
            (
                reverse(
                    "posts:post_detail",
                    kwargs={"post_id": f"{PostURLTests.post.id}"},
                ),
                HTTPStatus.OK,
            ),
            ("/unexisting-page/", HTTPStatus.NOT_FOUND),
        )

        for url, status in urls_http_status:
            with self.subTest(url=url):
                response = PostURLTests.guest_client.get(url)
                self.assertEqual(response.status_code, status)

    def test_posts_urls_for_authorized_author(self):
        """Доступность URLs для авторизованного автора поста."""
        urls_http_status = (
            (reverse("posts:index"), HTTPStatus.OK),
            (
                reverse(
                    "posts:group_list",
                    kwargs={"slug": f"{PostURLTests.group.slug}"},
                ),
                HTTPStatus.OK,
            ),
            (
                reverse(
                    "posts:profile",
                    kwargs={"username": f"{PostURLTests.user.username}"},
                ),
                HTTPStatus.OK,
            ),
            (
                reverse(
                    "posts:post_detail",
                    kwargs={"post_id": f"{PostURLTests.post.id}"},
                ),
                HTTPStatus.OK,
            ),
            ("/unexisting-page/", HTTPStatus.NOT_FOUND),
            (
                reverse(
                    "posts:post_edit",
                    kwargs={"post_id": f"{PostURLTests.post.id}"},
                ),
                HTTPStatus.OK,
            ),
            (reverse("posts:post_create"), HTTPStatus.OK),
        )

        for url, status in urls_http_status:
            with self.subTest(url=url):
                response = PostURLTests.authorized_client.get(url)
                self.assertEqual(response.status_code, status)

    def test_posts_urls_redirect_for_unauthorized(self):
        """Редиректы для неавторизованного пользователя"""
        login = reverse("users:login")
        post_create = reverse("posts:post_create")
        post_edit = reverse(
            "posts:post_edit", kwargs={"post_id": f"{PostURLTests.post.id}"}
        )
        urls_redirects = (
            (post_create, f"{login}?next={post_create}"),
            (post_edit, f"{login}?next={post_edit}"),
        )
        for url, redirect in urls_redirects:
            with self.subTest(url=url):
                response = PostURLTests.guest_client.get(url, follow=True)
                self.assertRedirects(response, redirect)

    def test_post_edit_url_for_not_author(self):
        """Редирект для авторизованного юзера, но не автора поста."""
        post_edit = reverse(
            "posts:post_edit", kwargs={"post_id": f"{PostURLTests.post.id}"}
        )
        post_detail = reverse(
            "posts:post_detail", kwargs={"post_id": f"{PostURLTests.post.id}"}
        )
        response = PostURLTests.authorized_but_not_author.get(
            post_edit, follow=True
        )
        self.assertRedirects(response, post_detail)
