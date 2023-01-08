from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from django.conf import settings
from .utils import get_page_context
from .models import Follow, Group, Post, User
from .forms import CommentForm, PostForm


def index(request):
    post_list = Post.objects.select_related('author', 'group')
    context = {
        'page_obj': get_page_context(post_list, request),
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('author')
    context = {
        'group': group,
        'page_obj': get_page_context(post_list, request),
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.prefetch_related('group')
    following = request.user.is_authenticated
    if following:
        following = author.following.filter(user=request.user).exists()
    post_count = author.posts.count()
    context = {
        'author': author,
        'page_obj': get_page_context(post_list, request),
        'post_count': post_count,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    posts_count = post.author.posts.count()
    title = post.text[:settings.TEXT_TITLE]
    context = {
        'post': post,
        posts_count: posts_count,
        'title': title,
        'form': CommentForm(),
        'comments': post.comments.all(),
        'author': post.author,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect('posts:profile', request.user)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if not form.is_valid():
        return render(request, 'posts/create_post.html',
                      {'form': form, 'is_edit': True})
    post.text = form.cleaned_data['text']
    post.group = form.cleaned_data['group']
    post.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Старница с постами авторов, на которых подписан текущий пользователь."""
    post_list = Post.objects.filter(author__following__user=request.user).all()
    page_obj = get_page_context(post_list, request)
    context = {
        'following': True,
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        follow = Follow.objects.filter(user=request.user, author=author)
        if not follow.exists():
            follow = Follow.objects.create(user=request.user, author=author)
            follow.save()
            return redirect('posts:follow_index')
    return redirect('posts:index')


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follow = get_object_or_404(Follow, user=request.user, author=author)
    follow.delete()
    return redirect('posts:index')
