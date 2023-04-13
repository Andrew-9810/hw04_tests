from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, Comment, Follow
from django.contrib.auth import get_user_model
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from core.utils import paginator
from django.views.decorators.cache import cache_page

User = get_user_model()


@cache_page(20, key_prefix='index_page')
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
    # Запрашиваю есть ли запись с автором и пользователем
    following_variable = Follow.objects.filter(
        # Фильтруем автора = автор профайла
        author=author
    ).filter(
        # Фильтруем пользователя = учетная запись с которой сидим
        user=request.user
    )
    # Ели что-то есть то отписаться, если нечего нет то подписаться
    if len(following_variable) == 0:
        following = False
    else:
        following = True
    context = {
        'author': author,
        'page_obj': paginator(request, posts),
        'count': count_post,
        'following': following
    }
    return render(request, template, context)


def post_detail(request, post_id):
    """Страница просмотра отдельного поста автора"""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm()
    comments = Comment.objects.filter(post=post)
    count_post = Post.objects.filter(author_id=post.author_id).count()
    template = 'posts/post_detail.html'
    context = {
        'post': post,
        'count': count_post,
        'form': form,
        'comments': comments
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


@login_required
def add_comment(request, post_id):
    """Странница сохраняет коментарии."""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    url = 'posts:post_detail'
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect(url, post_id=post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    user = get_object_or_404(User, username=request.user)
    posts = Post.objects.filter(author__following__user=user)
    context = {
        'page_obj': paginator(request, posts)
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    # Подписаться на автора
    url = 'posts:profile'
    Follow.objects.create(
        author=User.objects.get(username=username),
        user=request.user
    )
    return redirect(url, username)


@login_required
def profile_unfollow(request, username):
    # Дизлайк, отписка
    url = 'posts:profile'
    Follow.objects.filter(
        author=User.objects.get(username=username)
    ).filter(
        user=request.user
    ).delete()
    return redirect(url, username)

