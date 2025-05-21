from http import HTTPStatus
from django.urls import reverse

from .base import BaseTestCase


class TestRoutes(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.public_get_urls = [
            cls.home_url,
            cls.login_url,
            cls.signup_url,
        ]

    def test_public_pages_access(self):
        """
        Проверяет, что публичные страницы доступны анонимным пользователям
        с кодом статуса 200 OK при GET-запросах.
        """
        for url in self.public_get_urls:
            with self.subTest(url=url):
                response = self.anonymous_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_public_logout_post_access(self):
        """
        Проверяет, что маршрут logout доступен анонимным пользователям
        с кодом статуса 200 OK при POST-запросе.
        """
        response = self.anonymous_client.post(self.logout_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authenticated_user_pages_access(self):
        """
        Проверяет, что авторизованный пользователь имеет доступ к приватным
        страницам с кодом статуса 200 OK.
        """
        for url in self.private_urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_note_pages_access_for_author(self):
        """
        Проверяет, что автор заметки имеет доступ к страницам своей заметки
        (детали, редактирование, удаление) с кодом статуса 200 OK.
        """
        for url in self.note_urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_note_pages_access_for_non_author(self):
        """
        Проверяет, что неавтор заметки не имеет доступа к страницам чужой
        заметки и получает код статуса 404 NOT FOUND.
        """
        for url in self.note_urls:
            with self.subTest(url=url):
                response = self.other_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_anonymous_redirect_to_login(self):
        """
        Проверяет, что анонимный пользователь перенаправляется на страницу
        логина при попытке доступа к приватным страницам или страницам заметки.
        """
        all_protected_urls = self.private_urls + self.note_urls
        for url in all_protected_urls:
            with self.subTest(url=url):
                response = self.anonymous_client.get(url)
                self.assertRedirects(response, f'{self.login_url}?next={url}')
