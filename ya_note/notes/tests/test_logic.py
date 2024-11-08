# python3 manage.py test notes.tests.test_logic
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestNoteCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('notes:add', None)
        cls.user = User.objects.create(username='Аноним')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {'title': 'Название', 'text': 'Заметка'}

    def test_anonimous_user_cant_create_note(self):
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, '/done/')
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        # Проверяем, что все атрибуты заметки совпадают с ожидаемыми.
        self.assertEqual(note.title, 'Название')
        self.assertEqual(note.text, 'Заметка')
        # Проверяем, что у заметки есть слаг, хотя его не задавали.
        self.assertIsNotNone(note.slug)

    def test_slug_duplication(self):
        # Создаем заметку.
        self.auth_client.post(self.url, data=self.form_data)
        note = Note.objects.get()
        slug_occupied = note.slug
        # Сохраняем количество заметок.
        notes_count = Note.objects.count()
        # Добавляем занятый слаг к новой заметке.
        new_form_data = {
            'title': 'Новое название',
            'text': 'Еще одна заметка',
            'slug': slug_occupied
        }
        # Пытаемся создать заметку с занятым слагом.
        self.auth_client.post(self.url, data=new_form_data)
        # Проверяем, увеличилось ли количество заметок.
        notes_count_new = Note.objects.count()
        self.assertEqual(notes_count_new, notes_count)


class TestNoteEditDelete(TestCase):

    NEW_NOTE_DATA = {'title': 'Новое название', 'text': 'Новая заметка'}

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст заметки.',
            slug='slug',
            author=cls.author
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.url_to_login = reverse('users:login', None)

        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, '/done/')
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_reader_cant_delete_note(self):
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        # Выполняем запрос на редактирование от имени автора.
        response = self.author_client.post(
            self.edit_url,
            data=self.NEW_NOTE_DATA
        )
        # Проверяем, что сработал редирект.
        self.assertRedirects(response, '/done/')
        # Обновляем объект.
        self.note.refresh_from_db()
        # Проверяем, что текст соответствует обновленному.
        self.assertEqual(self.note.title, self.NEW_NOTE_DATA['title'])
        self.assertEqual(self.note.text, self.NEW_NOTE_DATA['text'])

    def test_user_cant_edit_note_of_another_user(self):
        # Выполняем запрос на редактирование от имени другого пользователя.
        response = self.reader_client.post(
            self.edit_url,
            data=self.NEW_NOTE_DATA
        )
        # Проверяем, что вернулась 404 ошибка.
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # Обновляем объект.
        self.note.refresh_from_db()
        # Проверяем, что текст остался тем же, что и был.
        self.assertEqual(self.note.title, self.note.title)
        self.assertEqual(self.note.text, self.note.text)
