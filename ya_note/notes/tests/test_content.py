from notes.forms import NoteForm
from notes.tests.test_common import TestCommon


class TestNotes(TestCommon):

    def test_notes_list(self):
        authors = (
            (self.author, self.author_client),
            (self.author_second, self.author_second_client)
        )
        # В фикстурах в цикле созданы по несколько заметок для двух авторов.
        # Проверяем, что ни один из авторов не видит заметок другого.
        for author_, client_ in authors:
            with self.subTest(author_=author_, client_=client_):
                response = client_.get(self.url_notes_reverse)
                notes = response.context['object_list']
                # В цикле проверяем, что ни одна заметка на странице одного
                # пользователя не принадлежит другому.
                for note in notes:
                    self.assertEqual(note.author, author_)

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
