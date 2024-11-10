from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note


User = get_user_model()


class TestCommon(TestCase):

    MULTIPLE_NOTES = 3

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.author_second = User.objects.create(username='author_second')
        cls.author_second_client = Client()
        cls.author_second_client.force_login(cls.author_second)
        cls.all_notes = []
        for index in range(cls.MULTIPLE_NOTES * 2):
            # В цикле создаем заметки для двух авторов.
            if index % 2 == 0:
                author = cls.author
            else:
                author = cls.author_second
            note = Note(
                title=f'Заметка {index}',
                text=f'Текст {index} заметки.',
                slug=f'slug{index}',
                author=author
            )
            cls.all_notes.append(note)
        Note.objects.bulk_create(cls.all_notes)
        cls.note = cls.all_notes[0]
        # Реверсы
        cls.url_notes_reverse = reverse('notes:list')
        cls.url_detail_reverse = reverse(
            'notes:detail', args=(cls.note.slug,)
        )
        cls.url_edit_reverse = reverse('notes:edit', args=(cls.note.slug,))
        cls.url_add_reverse = reverse('notes:add', None)
        cls.urls = (cls.url_add_reverse, cls.url_edit_reverse)


class TestNotes(TestCommon):

    def test_notes_list(self):
        response = self.author_client.get(self.url_notes_reverse)
        notes = response.context['object_list']
        # Число заметок совпадает с числом заметок автора.
        self.assertEqual(notes.count(), self.MULTIPLE_NOTES)
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
