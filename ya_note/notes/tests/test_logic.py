from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
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
            title='Тестовая заметка',
            text='Текст заметки.',
            slug='slug',
            author=cls.author
        )
        # Содержимое формы для запроса
        cls.form_data = {
            'title': 'Новая заметка',
            'text': 'Текст новой заметки'
        }
        # Реверсы
        cls.url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.url_to_login = reverse('users:login')
        cls.url_done = reverse('notes:success')


class TestNoteCreation(TestCommon):

    def test_anonimous_user_cant_create_note(self):
        notes_count_start = Note.objects.count()
        self.client.post(self.url, data=self.form_data)
        notes_count_finish = Note.objects.count()
        self.assertEqual(notes_count_finish, notes_count_start)

    def test_user_can_create_note(self):
        Note.objects.all().delete()
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, self.url_done)
        notes_count_finish = Note.objects.count()
        self.assertEqual(notes_count_finish, 1)
        note_new = Note.objects.get()
        # Проверяем, что все атрибуты заметки совпадают с ожидаемыми.
        self.assertEqual(note_new.title, self.form_data['title'])
        self.assertEqual(note_new.text, self.form_data['text'])
        self.assertEqual(note_new.author, self.user)
        # Проверяем, что у заметки есть слаг, хотя его не задавали.
        # В других тестах это не проверяется.
        self.assertIsNotNone(note_new.slug)

    def test_slug_duplication(self):
        notes_count_start = Note.objects.count()
        # Добавляем занятый слаг в форму запроса.
        form_data = self.form_data
        form_data['slug'] = self.note.slug
        # Пытаемся создать заметку с занятым слагом.
        response = self.auth_client.post(self.url, data=form_data)
        # Проверяем, увеличилось ли количество заметок.
        notes_count_finish = Note.objects.count()
        self.assertEqual(notes_count_finish, notes_count_start)
        self.assertFormError(
            response, 'form', 'slug', errors=('slug' + WARNING)
        )


class TestNoteEditDelete(TestCommon):

    def test_author_can_delete_note(self):
        notes_count_start = Note.objects.count()
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.url_done)
        notes_count_finish = Note.objects.count()
        self.assertEqual(notes_count_start, notes_count_finish + 1)

    def test_reader_cant_delete_note(self):
        notes_count_start = Note.objects.count()
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count_finish = Note.objects.count()
        self.assertEqual(notes_count_finish, notes_count_start)

    def test_author_can_edit_note(self):
        # Сохраняем pk заметки.
        note_pk = self.note.pk
        # Выполняем запрос на редактирование от имени автора.
        response = self.author_client.post(
            self.edit_url,
            data=self.form_data
        )
        # Проверяем, что сработал редирект.
        self.assertRedirects(response, self.url_done)
        new_note = Note.objects.get(pk=note_pk)
        # Проверяем, что текст соответствует обновленному.
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.author, self.author)

    def test_user_cant_edit_note_of_another_user(self):
        # Выполняем запрос на редактирование от имени другого пользователя.
        note = self.note
        response = self.reader_client.post(
            self.edit_url,
            data=self.form_data
        )
        # Проверяем, что вернулась 404 ошибка.
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # Обновляем объект.
        new_note = Note.objects.get(pk=note.pk)
        # Проверяем, что текст остался тем же, что и был.
        self.assertEqual(note.title, new_note.title)
        self.assertEqual(note.text, new_note.text)
        self.assertEqual(note.author, new_note.author)
