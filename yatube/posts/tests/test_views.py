import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Follow, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):

    ONE: int = 1

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username="anonymous")
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.another_user = User.objects.create_user(username="another_guy")

        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-group",
            description="Тестовое описание",
        )

        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        cls.uploaded = SimpleUploadedFile(
            name="small.gif", content=small_gif, content_type="image/gif"
        )
        cls.post = Post.objects.create(
            text="Тестовый текст",
            author=cls.user,
            group=cls.group,
            image=cls.uploaded,
        )
        cls.comment = Comment.objects.create(
            text="Тестовый комментарий",
            post=cls.post,
            author=cls.user,
        )

    def setUp(self):
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    @staticmethod
    def first_el(response, field: str):
        first_el: int = 0
        return response.context[f"{field}"][first_el]

    def test_pages_use_correct_templates(self):
        """URL-адрес использует соответствующий шаблон."""

        reverse_names_templates = (
            (reverse("posts:index"), "posts/index.html"),
            (
                reverse(
                    "posts:group_list",
                    kwargs={"slug": f"{PostsPagesTests.group.slug}"},
                ),
                "posts/group_list.html",
            ),
            (
                reverse(
                    "posts:profile",
                    kwargs={"username": f"{PostsPagesTests.user.username}"},
                ),
                "posts/profile.html",
            ),
            (
                reverse(
                    "posts:post_detail",
                    kwargs={"post_id": f"{PostsPagesTests.post.id}"},
                ),
                "posts/post_detail.html",
            ),
            (reverse("posts:post_create"), "posts/create_post.html"),
            (
                reverse(
                    "posts:post_edit",
                    kwargs={"post_id": f"{PostsPagesTests.post.id}"},
                ),
                "posts/create_post.html",
            ),
        )

        for reverse_name, template in reverse_names_templates:
            with self.subTest(reverse_name=reverse_name):
                response = PostsPagesTests.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_shows_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = PostsPagesTests.authorized_client.get(
            reverse("posts:index")
        )

        first_object = PostsPagesTests.first_el(response, "page_obj")

        field_value = (
            (first_object.text, "Тестовый текст"),
            (first_object.author.username, "anonymous"),
            (first_object.group.title, "Тестовая группа"),
            (first_object.group.description, "Тестовое описание"),
            (first_object.group.slug, "test-group"),
            (first_object.image, "posts/small.gif"),
        )
        for field, value in field_value:
            with self.subTest(field=field):
                self.assertEqual(field, value)

    def test_group_list_page_shows_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        Post.objects.create(
            text="Тестовый текст для поста без группы",
            author=PostsPagesTests.user,
        )
        response = PostsPagesTests.authorized_client.get(
            reverse(
                "posts:group_list",
                kwargs={"slug": f"{PostsPagesTests.group.slug}"},
            )
        )
        self.assertEqual(len(response.context["page_obj"]), self.ONE)

        first_object = PostsPagesTests.first_el(response, "page_obj")
        self.assertNotEqual(
            first_object.text, "Тестовый текст для поста без группы"
        )
        self.assertEqual(first_object.image, "posts/small.gif")

    def test_profile_page_shows_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        Post.objects.create(
            text="Тестовый текст для поста другого автора",
            author=PostsPagesTests.another_user,
        )
        response = PostsPagesTests.authorized_client.get(
            reverse(
                "posts:profile",
                kwargs={"username": "another_guy"},
            )
        )
        self.assertEqual(len(response.context["page_obj"]), self.ONE)

        first_object = PostsPagesTests.first_el(response, "page_obj")
        self.assertEqual(
            first_object.text, "Тестовый текст для поста другого автора"
        )

    def test_profile_page_contains_image(self):
        """В словаре контекста профайла передается картинка."""
        response = PostsPagesTests.authorized_client.get(
            reverse(
                "posts:profile",
                kwargs={"username": "anonymous"},
            )
        )
        first_object = PostsPagesTests.first_el(response, "page_obj")
        self.assertEqual(first_object.image, "posts/small.gif")

    def test_post_detail_page_shows_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = PostsPagesTests.authorized_client.get(
            reverse(
                "posts:post_detail",
                kwargs={"post_id": f"{PostsPagesTests.post.id}"},
            )
        )
        post_object = response.context["post"]
        comment_obj = PostsPagesTests.first_el(response, "comments")
        self.assertEqual(post_object.id, PostsPagesTests.post.id)
        self.assertEqual(post_object.image, "posts/small.gif")
        self.assertEqual(comment_obj.text, "Тестовый комментарий")

    def test_create_post_page_shows_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = PostsPagesTests.authorized_client.get(
            reverse("posts:post_create")
        )
        form_fields = (
            ("text", forms.fields.CharField),
            ("group", forms.fields.ChoiceField),
            ("image", forms.fields.ImageField),
        )
        for value, expected in form_fields:
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_shows_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = PostsPagesTests.authorized_client.get(
            reverse(
                "posts:post_edit",
                kwargs={"post_id": f"{PostsPagesTests.post.id}"},
            )
        )
        form_fields_instance = (
            ("text", forms.fields.CharField),
            ("group", forms.fields.ChoiceField),
            ("image", forms.fields.ImageField),
        )
        for value, expected in form_fields_instance:
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)

        form_field_instance = response.context.get("form").instance
        self.assertEqual(form_field_instance.id, PostsPagesTests.post.id)

    def test_new_post_appears_on_pages(self):
        """Новый пост отображается на нужных страницах."""
        url = reverse("posts:post_create")
        group = PostsPagesTests.group
        text = "Новый пост из тестов"
        response = PostsPagesTests.authorized_client.post(
            url,
            data={
                "text": text,
                "group": group.id,
            },
        )
        post = Post.objects.filter(
            author=PostsPagesTests.user, text=text, group=group
        ).first()
        list_of_pages = (
            reverse("posts:index"),
            reverse(
                "posts:group_list",
                kwargs={"slug": f"{PostsPagesTests.group.slug}"},
            ),
            reverse(
                "posts:profile",
                kwargs={"username": f"{PostsPagesTests.user.username}"},
            ),
        )
        for url in list_of_pages:
            with self.subTest(url=url):
                response = PostsPagesTests.authorized_client.get(url)
                self.assertIn(post, response.context["page_obj"])


class PostsCacheTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(username="anonymous")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.post = Post.objects.create(
            text="Тестовый текст",
            author=self.user,
        )

    def test_index_page_cache_works_properly(self):
        """Кеширование index_page работает корректно."""
        index_url = reverse("posts:index")
        post_text_in_bytes = self.post.text.encode(encoding="utf-8")

        response_0 = self.authorized_client.get(index_url)
        self.assertIn(self.post, response_0.context["page_obj"])
        self.post.delete()
        response_1 = self.authorized_client.get(index_url)
        self.assertIn(post_text_in_bytes, response_1.content)

        cache.clear()
        response_2 = self.authorized_client.get(index_url)
        self.assertNotIn(post_text_in_bytes, response_2.content)


class PostsFollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.follower = User.objects.create_user(username="follower")
        cls.not_follower = User.objects.create_user(username="not_follower")
        cls.following = User.objects.create_user(username="following")
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.follower)
        cls.not_follower_client = Client()
        cls.not_follower_client.force_login(cls.not_follower)

        cls.follow_link = reverse(
            "posts:profile_follow", kwargs={"username": cls.following.username}
        )
        cls.unfollow_link = reverse(
            "posts:profile_unfollow",
            kwargs={"username": cls.following.username},
        )
        cls.follow_index = reverse("posts:follow_index")
        cls.post = Post.objects.create(
            author=PostsFollowTests.following, text="Test text"
        )

    def test_authorized_client_can_follow_and_unfollow(self):
        """Авторизованный пользователь может подписываться."""
        PostsFollowTests.authorized_client.get(PostsFollowTests.follow_link)
        self.assertTrue(
            Follow.objects.filter(
                user=PostsFollowTests.follower,
                author=PostsFollowTests.following,
            ).exists()
        )

    def test_authorized_client_can_unfollow(self):
        """Авторизованный пользователь может отписываться."""
        Follow.objects.create(
            user=PostsFollowTests.follower,
            author=PostsFollowTests.following,
        )
        PostsFollowTests.authorized_client.get(PostsFollowTests.unfollow_link)
        self.assertFalse(
            Follow.objects.filter(
                user=PostsFollowTests.follower,
                author=PostsFollowTests.following,
            ).exists()
        )

    def test_new_post_appears_on_followers_pages(self):
        """Новая запись появляется в ленте тех, кто на него подписан и не
        появляется в ленте тех, кто не подписан."""
        Follow.objects.create(
            user=PostsFollowTests.follower,
            author=PostsFollowTests.following,
        )
        response_follower = PostsFollowTests.authorized_client.get(
            PostsFollowTests.follow_index
        )
        response_not_follower = PostsFollowTests.not_follower_client.get(
            PostsFollowTests.follow_index
        )
        self.assertIn(
            PostsFollowTests.post, response_follower.context["page_obj"]
        )
        self.assertNotIn("page_obj", response_not_follower.context)
