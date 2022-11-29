from django.http import HttpResponse
from django.shortcuts import render

# Главная страница
def index(request):
    return render(request, 'posts/index.html')


# Страница конкретной группы
def group_posts(request, slug):
    return HttpResponse(f'Страница группы {slug}')