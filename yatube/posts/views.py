from django.http import HttpResponse
from django.shortcuts import render

# Главная страница
def index(request):
    template = 'posts/index.html'
    title = 'Это главная страница проекта Yatube'
    context = {
        'title' : title
    }
    return render(request, template, context)


# Страница конкретной группы
def group_posts(request, slug):
    template = 'posts/group_list.html'
    title = 'Здесь будет информация о группах проекта Yatube'
    context = {
        'title' : title,
        'slug' : slug
    }
    return render(request, template, context)