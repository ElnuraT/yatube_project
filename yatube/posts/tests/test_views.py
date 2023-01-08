from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.conf import settings
from ..models import Comment, Follow, Group, Post
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()


class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username='Post_writer')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.posts = [
            Post(
                text=f'Тестовый текст {i}',
                group=cls.group,
                author=cls.user,
                image=uploaded,
            ) for i in range(settings.COUNT_POSTS)]
        Post.objects.bulk_create(cls.posts)

        cls.comment = Comment.objects.create(
            text='Тестовый комментарий',
            author=cls.user,
            post=cls.post,
        )
        cls.template_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', args=(PostPagesTest.group.slug,)):
                'posts/group_list.html',
            reverse('posts:profile', args=(PostPagesTest.user.username,)):
                'posts/profile.html',
            reverse('posts:post_detail', args=(1,)):
                'posts/post_detail.html',
            reverse('posts:post_edit', args=(1,)):
                'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorised_client = Client()
        self.authorised_client.force_login(PostPagesTest.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            (
                reverse('posts:group_list', kwargs={'slug': 'test-slug'})
            ): 'posts/group_list.html',
            (
                reverse('posts:profile', kwargs={'username': 'Post_writer'})
            ): 'posts/profile.html',
            (
                reverse('posts:post_detail', kwargs={
                    'post_id': 1})
            ): 'posts/post_detail.html',
            (
                reverse('posts:post_edit', kwargs={
                    'post_id': 1})
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorised_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_show_correct_context(self):
        page = Post.objects.select_related('author', 'group').all()[:10]
        response = self.authorised_client.get(reverse('posts:index'))
        self.assertEqual(
            list(response.context.get('page_obj').object_list), list(page)
        )

    def test_page_show_correct_context_group(self):
        page = Post.objects.filter(group=self.group).all()[:10]
        response = self.authorised_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}))
        self.assertEqual(list(response.context.get(
            'page_obj').object_list), list(page))

    def test_page_show_correct_context_author(self):
        page = Post.objects.filter(author=self.user).all()[:10]
        response = self.authorised_client.get(
            reverse('posts:profile', kwargs={'username': 'Post_writer'}))
        self.assertEqual(list(response.context.get(
            'page_obj').object_list), list(page))

    def test_post_page_show_correct_context_post_detail(self):
        self.user2 = User.objects.create_user(username='Post_writer2')
        self.post14 = Post.objects.create(
            author=self.user2,
            text='Тестовый пост от Post_writer2',
        )
        response = self.authorised_client.get(
            reverse('posts:post_detail', kwargs={'post_id': 14}))
        page_post = response.context['post'].text
        self.assertEqual(page_post, self.post14.text)

    def test_post_page_show_correct_context_post_edit(self):
        response = self.authorised_client.get(
            reverse('posts:post_edit', kwargs={'post_id': 10}))
        form = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_page_show_correct_context_creaete_post(self):
        response = self.authorised_client.get(
            reverse('posts:post_create')
        )
        form = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        group_test = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug2',
            description='Тестовое описание',
        )
        post_test = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
            group=group_test,
        )
        addresses = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug2'}),
            reverse('posts:profile', kwargs={'username': 'Post_writer'}),
        ]

        for address in addresses:
            response = self.authorised_client.get(address)
            last_object_id = response.context['page_obj'][0].id
            self.assertEqual(last_object_id, post_test.id)
        # проверяем, что пост не попал в другую группу
        response = self.authorised_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}))
        last_object_id = response.context['page_obj'][0].id
        self.assertNotEqual(last_object_id, post_test.id)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Post_writer')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.posts = [
            Post(
                text=f'Тестовый текст {i}',
                group=cls.group,
                author=cls.user,
                 ) for i in range(settings.COUNT_POSTS)]
        Post.objects.bulk_create(cls.posts)

        cls.authorised_client = Client()
        cls.authorised_client.force_login(cls.user)
        cls.guest_client = Client()

    def test_first_page_contains_ten_records(self):
        addresses = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': 'Post_writer'}),
        ]
        for address in addresses:
            response = self.authorised_client.get(address)
            self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        addresses = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': 'Post_writer'}),
        ]
        for address in addresses:
            response = self.authorised_client.get(address + '?page=2')
            self.assertEqual(len(response.context['page_obj']), 3)


class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_user = User.objects.create(
            username='post_user',
        )
        cls.post_follower = User.objects.create(
            username='post_follower',
        )
        cls.post = Post.objects.create(
            text='Подпишись на меня',
            author=cls.post_user,
        )

    def setUp(self):
        cache.clear()
        self.guest_user = Client()
        self.author_client = Client()
        self.author_client.force_login(self.post_follower)
        self.follower_client = Client()
        self.follower_client.force_login(self.post_user)

    def test_follow_on_user(self):
        """Проверка подписки на пользователя."""
        count_follow = Follow.objects.count()
        self.follower_client.post(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.post_follower}))
        follow = Follow.objects.all().latest('id')
        self.assertEqual(Follow.objects.count(), count_follow + 1)
        self.assertEqual(follow.author_id, self.post_follower.id)
        self.assertEqual(follow.user_id, self.post_user.id)

    def test_no_follow(self):
        """Проверка подписки неавторизованного пользователя"""
        count_follow = Follow.objects.count()
        self.guest_user.post(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.post_follower}))
        error = 'Подписка добавлена в базу данных по ошибке'
        self.assertNotEqual(Follow.objects.count(),
                            count_follow + 1,
                            error)

    def test_no_follow_on_author(self):
        """Проверка подписки пользователя самого на себя"""
        Follow.objects.create(
            user=self.post_user,
            author=self.post_follower)
        count_follow = Follow.objects.count()
        self.follower_client.post(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.post_follower}))
        follow = Follow.objects.all().latest('id')
        self.assertNotEqual(Follow.objects.count(),
                            count_follow + 1)
        self.assertNotEqual(follow.user_id, self.post_follower.id)

    def test_unfollow_on_user(self):
        """Проверка отписки от пользователя."""
        Follow.objects.create(
            user=self.post_user,
            author=self.post_follower)
        count_follow = Follow.objects.count()
        self.follower_client.post(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.post_follower}))
        self.assertEqual(Follow.objects.count(), count_follow - 1)
        follows = Follow.objects.filter(user=self.post_user,
                                        author=self.post_follower)
        self.assertFalse(follows)

    def test_follow_on_authors(self):
        """Проверка записей у тех кто подписан."""
        post = Post.objects.create(
            author=self.post_user,
            text="Подпишись на меня")
        Follow.objects.create(
            user=self.post_follower,
            author=self.post_user)
        response = self.author_client.get(
            reverse('posts:follow_index'))
        self.assertIn(post, response.context['page_obj'].object_list)

    def test_notfollow_on_authors(self):
        """Проверка записей у тех кто не подписан."""
        post = Post.objects.create(
            author=self.post_user,
            text="Подпишись на меня")
        response = self.author_client.get(
            reverse('posts:follow_index'))
        self.assertNotIn(post, response.context['page_obj'].object_list)
