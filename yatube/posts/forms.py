from django.forms import ModelForm

from .models import Comment, Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text', 'image')
        labels = {
            'text': 'Текст поста',
            'group': 'Группа',
        }
        help_texts = {
            'text': 'Введите текст поста.',
            'group': 'Введите название группы.',
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
