from django.contrib.auth import get_user_model
from django.test import TestCase
from django.conf import settings
from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_groups_have_correct_object_name(self):
        group = PostModelTest.group
        expected_object_name = group.title
        with self.subTest(expected_object_name=expected_object_name):
            self.assertEqual(expected_object_name, str(group))

    def test_posts_have_correct_object_name(self):
        post = PostModelTest.post
        expected_object_name = post.text[:settings.TEXT_COUNT]
        self.assertEqual(expected_object_name, str(post))

    def test_help_text(self):
        field_helps = {
            'group': 'Группа, к которой будет относиться пост',
            'text': 'Текст нового поста',
        }
        for value, expected in field_helps.items():
            with self.subTest(value=value):
                self.assertEqual(
                    PostModelTest.post._meta.get_field(value).help_text,
                    expected
                )

    def test_verbose_name(self):
        field_verbose = {
            'group': 'Группа',
            'text': 'Текст Поста',
        }
        for value, expected in field_verbose.items():
            with self.subTest(value=value):
                self.assertEqual(
                    PostModelTest.post._meta.get_field(value).verbose_name,
                    expected
                )
