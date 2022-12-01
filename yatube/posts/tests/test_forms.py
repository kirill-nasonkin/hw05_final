import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.guest_client = Client()

        cls.user = User.objects.create_user(username="anonymous")
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

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

    def setUp(self):
        cache.clear()
        self.post = Post.objects.create(
            text="Тестовый текст",
            author=PostFormTests.user,
            group=PostFormTests.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_form_creates_new_post(self):
        """Форма на странцие posts:post_create создаёт новый пост."""
        posts_count = Post.objects.count()
        form_data = {
            "text": "Тестовый текст для формы, создающей пост",
            "group": PostFormTests.group.id,
        }
        response = PostFormTests.authorized_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text="Тестовый текст для формы, создающей пост"
            ).exists()
        )

    def test_post_create_form_redirect_works_correctly(self):
        """Форма post_create осуществляет редирект."""
        form_data = {
            "text": "Тестовый текст для формы, создающей пост",
            "group": PostFormTests.group.id,
        }
        response = PostFormTests.authorized_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                "posts:profile",
                kwargs={"username": f"{PostFormTests.user.username}"},
            ),
        )

    def test_post_edit_form_makes_changes_in_db(self):
        """Форма на странцие post_edit изменяет пост."""
        form_data = {
            "text": "Отредактированный пост",
        }
        response = PostFormTests.authorized_client.post(
            reverse(
                "posts:post_edit",
                kwargs={"post_id": f"{self.post.id}"},
            ),
            data=form_data,
            follow=True,
        )
        edited_post = Post.objects.filter(
            text="Отредактированный пост",
        ).first()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIsNotNone(edited_post)
        self.assertEqual(edited_post.id, self.post.id)

    def test_post_edit_form_redirect_works_correctly(self):
        """Форма на странцие post_edit осуществляет редирект."""
        form_data = {
            "text": "Отредактированный пост",
        }
        response = PostFormTests.authorized_client.post(
            reverse(
                "posts:post_edit",
                kwargs={"post_id": f"{self.post.id}"},
            ),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(
                "posts:post_detail",
                kwargs={"post_id": f"{self.post.id}"},
            ),
        )

    def test_cant_create_post_without_text(self):
        """Новый пост не сохранится без текста."""
        posts_count = Post.objects.count()
        form_data = {
            "text": "",
            "group": PostFormTests.group.id,
        }
        response = PostFormTests.authorized_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertFalse(Post.objects.filter(text="").exists())
        self.assertFormError(
            response,
            "form",
            "text",
            "Обязательное поле.",
        )

    def test_cant_save_post_without_text_in_post_edit(self):
        """Редактируемый пост не сохранится без текста."""
        form_data = {
            "text": "",
            "group": PostFormTests.group.id,
        }
        response = PostFormTests.authorized_client.post(
            reverse(
                "posts:post_edit",
                kwargs={"post_id": f"{self.post.id}"},
            ),
            data=form_data,
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFormError(
            response,
            "form",
            "text",
            "Обязательное поле.",
        )

    def test_unauthorized_user_cant_create_post(self):
        """Неавторизованный пользователь не может создать пост."""
        posts_count = Post.objects.count()
        form_data = {
            "text": "Тестовый текст.",
            "group": PostFormTests.group.id,
        }
        response = PostFormTests.guest_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), posts_count)

    def test_unauthorized_user_cant_edit_post(self):
        """Неавторизованный пользователь не может изменить пост."""
        form_data = {
            "text": "Отредактированный пост",
        }
        response = PostFormTests.guest_client.post(
            reverse(
                "posts:post_edit",
                kwargs={"post_id": f"{self.post.id}"},
            ),
            data=form_data,
            follow=True,
        )
        edited_post = Post.objects.filter(
            text="Отредактированный пост",
        ).first()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIsNone(edited_post)
        self.assertEqual(self.post.text, "Тестовый текст")

    def test_can_create_new_post_with_image(self):
        """Форма создаёт пост при с переданной картинкой."""
        tasks_count = Post.objects.count()
        form_data = {
            "text": "Тестовый текст",
            "image": PostFormTests.uploaded,
        }
        response = PostFormTests.authorized_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                "posts:profile",
                kwargs={"username": f"{PostFormTests.user.username}"},
            ),
        )
        self.assertEqual(Post.objects.count(), tasks_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text="Тестовый текст",
                image="posts/small.gif",
            ).exists()
        )

    def test_unauthorized_user_cant_comment_post(self):
        """Неавторизованный пользователь не может добавить комментарий."""
        comments_count = Comment.objects.count()
        form_data = {
            "text": "Тестовый комментарий",
            "post": self.post,
        }
        request = PostFormTests.guest_client.post(
            reverse(
                "posts:add_comment", kwargs={"post_id": f"{self.post.id}"}
            ),
            data=form_data,
            follow=True,
        )
        self.assertEqual(request.status_code, HTTPStatus.OK)
        self.assertEqual(Comment.objects.count(), comments_count)
        self.assertIsNone(
            Comment.objects.filter(text="Тестовый комментарий").first()
        )

    def test_comment_appears_on_post_detail_page(self):
        """Комментарий появляется на странице post_detail."""
        first: int = 0
        comments_count = Comment.objects.count()
        form_data = {
            "text": "Тестовый комментарий",
            "post": self.post,
        }
        request = PostFormTests.authorized_client.post(
            reverse(
                "posts:add_comment", kwargs={"post_id": f"{self.post.id}"}
            ),
            data=form_data,
            follow=True,
        )
        post_detail_request = PostFormTests.authorized_client.get(
            reverse("posts:post_detail", kwargs={"post_id": f"{self.post.id}"})
        )
        test_comment_text = (
            post_detail_request.context["comments"][first].text,
        )
        test_data = (
            (request.status_code, HTTPStatus.OK),
            (Comment.objects.count(), comments_count + 1),
            (post_detail_request.status_code, HTTPStatus.OK),
            (*test_comment_text, "Тестовый комментарий"),
        )
        for verifiable, value in test_data:
            with self.subTest(verifiable=verifiable):
                self.assertEqual(verifiable, value)
