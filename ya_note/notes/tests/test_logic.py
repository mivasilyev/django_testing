from http import HTTPStatus

from django.contrib.auth import get_user_model
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from notes.tests.test_common import TestCommon


User = get_user_model()


class TestNoteCreation(TestCommon):

    def test_anonimous_user_cant_create_note(self):
        notes_count_start = Note.objects.count()
        self.client.post(self.url_add_reverse, data=self.form_data)
        notes_count_finish = Note.objects.count()
        self.assertEqual(notes_count_finish, notes_count_start)

    def test_user_can_create_note(self):
        Note.objects.all().delete()
        response = self.reader_client.post(
            self.url_add_reverse, data=self.form_data
        )
        self.assertRedirects(response, self.url_done_reverse)
        notes_count_finish = Note.objects.count()
        self.assertEqual(notes_count_finish, 1)
        note_new = Note.objects.get()
        # Проверяем, что все атрибуты заметки совпадают с ожидаемыми.
        self.assertEqual(note_new.title, self.form_data['title'])
        self.assertEqual(note_new.text, self.form_data['text'])
        self.assertEqual(note_new.author, self.reader)
        # Проверяем, что у заметки есть слаг, хотя его не задавали.
        # В других тестах это не проверяется.
        auto_slug = slugify(self.form_data['title'])
        self.assertIsNotNone(note_new.slug, auto_slug)

    def test_slug_duplication(self):

        notes_count_start = Note.objects.count()
        # Добавляем занятый слаг в форму запроса.
        form_data = self.form_data
        form_data['slug'] = self.note.slug
        # Пытаемся создать заметку с занятым слагом.
        response = self.author_client.post(
            self.url_add_reverse, data=form_data
        )
        # Проверяем, увеличилось ли количество заметок.
        notes_count_finish = Note.objects.count()
        self.assertEqual(notes_count_finish, notes_count_start)
        self.assertFormError(
            response, 'form', 'slug', errors=(self.note.slug + WARNING)
        )


class TestNoteEditDelete(TestCommon):

    def test_author_can_delete_note(self):
        notes_count_start = Note.objects.count()
        response = self.author_client.delete(self.url_del_reverse)
        self.assertRedirects(response, self.url_done_reverse)
        notes_count_finish = Note.objects.count()
        self.assertEqual(notes_count_start, notes_count_finish + 1)

    def test_reader_cant_delete_note(self):
        notes_count_start = Note.objects.count()
        response = self.reader_client.delete(self.url_del_reverse)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count_finish = Note.objects.count()
        self.assertEqual(notes_count_finish, notes_count_start)

    def test_author_can_edit_note(self):
        # Сохраняем pk заметки.
        note_pk = self.note.pk
        note_author = self.note.author
        # Выполняем запрос на редактирование от имени автора.
        response = self.author_client.post(
            self.url_edit_reverse,
            data=self.form_data
        )
        # Проверяем, что сработал редирект.
        self.assertRedirects(response, self.url_done_reverse)
        new_note = Note.objects.get(pk=note_pk)
        # Проверяем, что текст соответствует обновленному.
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        # Проверяем, что автор остался тот же, что и у исходной заметки.
        self.assertEqual(new_note.author, note_author)

    def test_user_cant_edit_note_of_another_user(self):
        # Выполняем запрос на редактирование от имени другого пользователя.
        note = self.note
        response = self.reader_client.post(
            self.url_edit_reverse,
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
