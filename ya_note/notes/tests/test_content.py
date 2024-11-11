from django.contrib.auth import get_user_model

from notes.forms import NoteForm
from notes.tests.test_common import TestCommon


User = get_user_model()


class TestNotes(TestCommon):

    def test_notes_list(self):
        response = self.author_client.get(self.url_notes_reverse)
        notes = response.context['object_list']
        # В цикле: ни одна заметка не принадлежит другому автору.
        # В список заметок одного пользователя не попадают заметки другого.
        for note in notes:
            self.assertEqual(note.author, self.author)

    def test_note_detail(self):
        response = self.author_client.get(self.url_detail_reverse)
        self.assertEqual(
            response.context['object'].title, self.all_notes[0].title
        )
        self.assertEqual(
            response.context['object'].text, self.all_notes[0].text
        )


class TestNoteCreationAndEdit(TestCommon):

    def test_anonymous_client_has_no_form(self):
        # Анониму на страницы создания и редактирования
        # заметок не передаются формы
        for name in self.urls:
            with self.subTest(name=name):
                response = self.client.get(name)
                self.assertIsNone(response.context)

    def test_authorized_client_has_form(self):
        # Авторизованному пользователю на страницы создания и редактирования
        # заметок передаются формы
        for name in self.urls:
            with self.subTest(name=name):
                response = self.author_client.get(name)
                self.assertIn('form', response.context)
                # Проверим, что объект формы соответствует нужному классу.
                self.assertIsInstance(response.context['form'], NoteForm)

# Проверка на попадание заметок одного пользователя в список заметок другого
# пользователя производится в test_notes_list.
