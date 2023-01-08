from http import HTTPStatus
from django.urls import reverse
from django.test import Client, TestCase


class AboutURLTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_about_page(self):
        urls = [
            reverse('about:author'),
            reverse('about:tech'),
        ]

        for address in urls:
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_page_uses_correct_template(self):
        templates = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }

        for address, template in templates.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertTemplateUsed(response, template)
