from django.contrib.auth import get_user_model
from django.db import models

from .constants import FIRST_15

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name="Имя сообщества")
    slug = models.SlugField(
        unique=True, verbose_name="Слаг сообщества (group/<slug>/)"
    )
    description = models.TextField(verbose_name="Описание сообщества")

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"


class Post(models.Model):

    text = models.TextField(
        verbose_name="Текст поста",
        help_text="Введите текст поста",
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="Автор",
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="posts",
        verbose_name="Группа",
        help_text="Группа, к которой будет относиться пост",
    )
    image = models.ImageField(
        verbose_name="Картинка", upload_to="posts/", blank=True
    )

    def __str__(self) -> str:
        return self.text[:FIRST_15]

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "Пост"
        verbose_name_plural = "Посты"


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        related_name="comments",
        on_delete=models.CASCADE,
        verbose_name="Комментируемый пост",
    )
    text = models.TextField(verbose_name="Текст комментария")
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации комментария",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Автор комментария",
    )

    def __str__(self) -> str:
        return self.text[:FIRST_15]

    class Meta:
        ordering = ("-created",)
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Подписчик",
        related_name="follower",
    )
    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="following",
    )

    def __str__(self):
        return f"Подписки пользователя {self.user}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="unique_follow", fields=["user", "author"]
            ),
        ]
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
