from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = (
            "text",
            "group",
            "image",
        )
        help_texts = {
            "text": _("Введите текст нового поста"),
            "group": _("Группа, к которой будет относиться пост"),
            "image": _("Добавьте изображение для вашего поста"),
        }
        labels = {
            "text": "Текст",
            "group": "Группа",
            "image": "Изображение",
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)
        help_texts = {
            "text": _("Здесь введите текст вашего комментария"),
        }
        labels = {
            "text": _("Текст комментария"),
        }
