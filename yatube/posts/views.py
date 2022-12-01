from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .constants import PAGE_CACHE_INTERVAL, POSTS_PER_PAGE
from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def create_paginator(request, post_list, posts_per_page):
    paginator = Paginator(post_list, posts_per_page)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return page_obj


@cache_page(timeout=PAGE_CACHE_INTERVAL, key_prefix="index_page")
def index(request):
    post_list = Post.objects.all()
    page_obj = create_paginator(request, post_list, POSTS_PER_PAGE)

    context = {
        "page_obj": page_obj,
        "to_show_groups": True,
    }
    return render(request, "posts/index.html", context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page_obj = create_paginator(request, post_list, POSTS_PER_PAGE)

    context = {
        "page_obj": page_obj,
        "group": group,
    }
    return render(request, "posts/group_list.html", context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    page_obj = create_paginator(request, post_list, POSTS_PER_PAGE)

    following = (
        request.user.is_authenticated
        and Follow.objects.filter(user=request.user, author=author).exists()
    )

    context = {
        "page_obj": page_obj,
        "author": author,
        "to_show_groups": True,
        "is_author_hidden": True,
        "following": following,
    }
    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm()
    comments = post.comments.all()
    context = {
        "comments": comments,
        "form": form,
        "post": post,
    }
    return render(request, "posts/post_detail.html", context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(False)
        post.author = request.user
        post.save()
        return redirect("posts:profile", username=request.user.username)
    return render(request, "posts/create_post.html", {"form": form})


@login_required
def post_edit(request, post_id):
    post_editable = get_object_or_404(Post, pk=post_id)
    if request.user != post_editable.author:
        return redirect("posts:post_detail", post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post_editable,
    )
    if form.is_valid():
        form.save()
        return redirect("posts:post_detail", post_id)
    context = {
        "post": post_editable,
        "form": form,
        "is_edit": True,
    }
    return render(request, "posts/create_post.html", context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect("posts:post_detail", post_id=post_id)


@login_required
def follow_index(request):
    user = request.user
    post_list = Post.objects.filter(author__following__user=user)
    page_obj = create_paginator(request, post_list, POSTS_PER_PAGE)
    context = {"page_obj": page_obj, "to_show_groups": True}
    return render(request, "posts/follow.html", context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    if user != author:
        Follow.objects.get_or_create(user=user, author=author)
    return redirect("posts:profile", username=username)


@login_required
def profile_unfollow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(user=user, author=author).first()
    if follow:
        follow.delete()
    return redirect("posts:profile", username=username)
