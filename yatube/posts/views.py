from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from django.conf import settings


from .forms import PostForm, CommentForm
from .models import Group, Post, User, Follow


def paginator(request, post_list):
    pages = Paginator(post_list, settings.POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    return pages.get_page(page_number)


def index(request):
    post_list = Post.objects.select_related('author', 'group')
    page_obj = paginator(request, post_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('author')
    page_obj = paginator(request, post_list)
    context = {
        'group': group,
        'page_obj': page_obj,

    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    post_list = author.posts.select_related('group')
    page_obj = paginator(request, post_list)
    following = author.following.filter(user=user.pk).exists()
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all()
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'comments': comments,
        'form': form
    }
    return render(request, 'posts/post_detail.html', context)


@login_required()
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user)
    return render(request, 'posts/create_post.html', {'form': form})


def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    context = {
        'form': form,
        'is_edit': True,
        'post_id': post.id,
    }
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    return render(request, 'posts/create_post.html', context)


@login_required()
def add_comment(request, post_id):
    post = Post.objects.get(pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required()
def follow_index(request):
    user = request.user
    authors = user.follower.all()
    post_list = []
    for a in authors:
        post_list += Post.objects.filter(author=a.author)
    page_obj = paginator(request, post_list)
    context = {'page_obj': page_obj}
    return render(request, 'posts/follow.html', context)


@login_required()
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    Follow.objects.create(user=user, author=author)
    return redirect('posts:profile', username=username)


@login_required()
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    author.following.filter(user=user.pk).delete()
    return redirect('posts:profile', username=username)
