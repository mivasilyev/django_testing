from http import HTTPStatus

from django.contrib.auth import get_user_model

from notes.tests.test_common import TestCommon


User = get_user_model()


class TestRoutes(TestCommon):

    def test_pages_availability(self):
        """Страницы: домашняя, регистрации, входа и выхода доступны всем."""
        for url in self.urls_available_reverse:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_logged_user(self):
        """
        Список заметок, добавление и сообщение об успешном добавлении
        доступны залогиненному пользователю.
        """
        for url in self.urls_logged_available_reverse:
            with self.subTest(user=self.reader, url=url):
                response = self.reader_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_user_edit_and_delete(self):
        """
        Заметка, ее редактирование и удаление доступны только автору.
        Остальные пользователи получают NOT FOUND.
        """
        users_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.reader_client, HTTPStatus.NOT_FOUND)
        )
        for used_client, status in users_statuses:
            for url in self.urls_author_available_reverse:
                with self.subTest(used_client=used_client, url=url):
                    response = used_client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonimous_client(self):
        """
        Анониму редирект на страницу логина при попытке входа на:
        список заметок, заметку, добавление, редактир-е и удаление заметки.
        """
        for url in self.anonimous_login_redirect_reverse:
            with self.subTest(url=url):
                redirect_url = f'{self.url_login_reverse}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
