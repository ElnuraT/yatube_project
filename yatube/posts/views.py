from django.shortcuts import render
from .models import Post, Group
from django.shortcuts import get_object_or_404
QUANTITY_POSTS = 10  # Количество элементов списка


def index(request):
    posts = Post.objects.select_related('group')[:QUANTITY_POSTS]
    context = {
        'posts': posts,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """
    Страница с информацией об публикациях;
    view-функция принимает параметр slug из path()
    """
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author')[:QUANTITY_POSTS]
    context = {
        'group': group,
        'posts': posts,
    }
    return render(request, 'posts/group_list.html', context)