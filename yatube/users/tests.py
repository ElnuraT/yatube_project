from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client, TestCase

User = get_user_model()


class UserURLTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_about_page(self):
        urls = [
            reverse('users:logout'),
            reverse('users:signup'),
            reverse('users:login'),
            reverse('users:password_reset_done'),
            reverse('users:password_reset_complete'),
            reverse('users:password_reset_form'),
        ]

        for address in urls:
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_user_signup(self):
        '''
        Проверка, что при заполнении формы reverse('users:signup')
        создается новый пользователь
        '''
        user_count = User.objects.count()
        form_data = {
            'username': 'TestUser',
            'email': 'test@test.ru',
            'password1': 'testpassword',
            'password2': 'testpassword',
        }
        response = self.client.post(reverse('users:signup'), data=form_data)
        self.assertEqual(User.objects.count(), user_count + 1)
        self.assertRedirects(response, reverse('posts:index'))
