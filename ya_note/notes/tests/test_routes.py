from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestCommon(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Пользователи
        cls.user = User.objects.create(username='Аноним')
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        # Клиенты и логины
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        # Заметка
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug',
            author=cls.author
        )
        # Ссылки
        cls.url_login = 'users:login'
        cls.urls_available = [
            'notes:home',
            'users:signup',
            'users:logout',
        ] + [cls.url_login]
        cls.urls_logged_available = [
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None)
        ]
        cls.urls_author_available = [
            ('notes:detail', (cls.note.slug,)),
            ('notes:edit', (cls.note.slug,)),
            ('notes:delete', (cls.note.slug,))
        ]
        cls.anonimous_login_redirect = (
            cls.urls_logged_available + cls.urls_author_available
        )


class TestRoutes(TestCommon):

    def test_pages_availability(self):
        """Страницы: домашняя, регистрации, входа и выхода доступны всем."""
        for name in self.urls_available:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_logged_user(self):
        """
        Список заметок, добавление и сообщение об успешном добавлении
        доступны залогиненному пользователю.
        """
        for name, args in self.urls_logged_available:
            with self.subTest(user=self.reader, name=name):
                url = reverse(name, args)
                response = self.auth_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_user_edit_and_delete(self):
        """
        Заметка, ее редактирование и удаление доступны только автору.
        Остальные пользователи получают NOT FOUND.
        """
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND)
        )
        for user, status in users_statuses:
            self.client.force_login(user)  # Замечание понял, но пока не могу
            # это исправить. Не разобрался как в unittest передать в subTest
            # параметризованного клиента.
            for name, args in self.urls_author_available:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonimous_client(self):
        """
        Анониму редирект на страницу логина при попытке входа на:
        список заметок, заметку, добавление, редактир-е и удаление заметки.
        """
        for name, args in self.anonimous_login_redirect:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{reverse(self.url_login)}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
