from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group
from django.contrib.auth import get_user_model
from .forms import PostForm
from django.contrib.auth.decorators import login_required

from core.utils import paginator

User = get_user_model()


def index(request):
    """Главная страница."""
    template = 'posts/index.html'
    posts = Post.objects.all()
    context = {
        'page_obj': paginator(request, posts)
    }
    return render(request, template, context)


def group_posts(request, slug):
    """Страница постов отсортированных по группам."""
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = (group.posts_group.all())
    context = {
        'group': group,
        'page_obj': paginator(request, posts)
    }
    return render(request, template, context)


def profile(request, username):
    """Страница просмотра всех постов автора"""
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    count_post = posts.count()
    template = 'posts/profile.html'
    context = {
        'username': author,
        'page_obj': paginator(request, posts),
        'count': count_post,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    """Страница просмотра отдельного поста автора"""
    post = get_object_or_404(Post, id=post_id)
    count_post = Post.objects.filter(author_id=post.author_id).count()
    template = 'posts/post_detail.html'
    context = {
        'post': post,
        'count': count_post
    }
    return render(request, template, context)


@login_required
def post_create(request):
    """Страница создания постов"""
    template = 'posts/create_post.html'
    if request.method == 'POST':
        form = PostForm(
            request.POST or None,
            files=request.FILES or None
        )
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            form.save()
            return redirect('posts:profile', username=request.user.username)
        return render(request, template, {'form': form})
    form = PostForm()
    return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    """Страница редактирования постов"""
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        form = PostForm(
            request.POST or None,
            files=request.FILES or None,
            instance=post
        )
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            form.save()
            return redirect('posts:post_detail', post_id)
        return render(request, template, {'form': form})
    if request.user == post.author:
        form = PostForm(instance=post)
        return render(request, template, {'form': form, 'is_edit': True})
    return redirect('posts:profile', username=post.author)
