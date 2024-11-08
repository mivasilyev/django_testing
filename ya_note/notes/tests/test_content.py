from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note


User = get_user_model()


class TestNotesList(TestCase):

    MULTIPLE_NOTES = 3
    NOTES_URL = 'notes:list'

    @classmethod
    def setUpTestData(cls):
        cls.author_first = User.objects.create(username='author_first')
        cls.author_second = User.objects.create(username='author_second')
        all_notes = []
        for index in range(cls.MULTIPLE_NOTES * 2):
            # В цикле создаем заметки для двух авторов.
            if index % 2 == 0:
                author = cls.author_first
            else:
                author = cls.author_second
            note = Note(
                title=f'Заметка {index}',
                text=f'Текст {index} заметки.',
                slug=f'slug{index}',
                author=author
            )
            all_notes.append(note)
        Note.objects.bulk_create(all_notes)

    def test_notes_list(self):
        # Логиним автора.
        self.client.force_login(self.author_first)
        # Загружаем список заметок.
        response = self.client.get(reverse('notes:list', None))
        # Получаем список объектов из словаря контекста.
        object_list = response.context['object_list']
        # Определяем количество записей в списке.
        notes_count = object_list.count()
        # Проверяем, что на странице все созданные первым автором заметки.
        self.assertEqual(notes_count, self.MULTIPLE_NOTES)
        # Проверяем, что на странице выведен заголовок первой заметки.
        self.assertEqual(object_list[0].title, 'Заметка 0')


class TestDetailPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст заметки.',
            slug='slug',
            author=cls.author
        )
        # Сохраняем в переменную адрес страницы с новостью:
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))

    def test_note_detail(self):
        self.client.force_login(self.author)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.context['object'].title, self.note.title)
        self.assertEqual(response.context['object'].text, self.note.text)


class TestNoteCreationAndEdit(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст заметки.',
            slug='slug',
            author=cls.author
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.new_note_url = reverse('notes:add', None)
        cls.urls = (cls.new_note_url, cls.edit_url)

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
        self.client.force_login(self.author)
        for name in self.urls:
            with self.subTest(name=name):
                response = self.client.get(name)
                self.assertIn('form', response.context)
                # Проверим, что объект формы соответствует нужному классу.
                self.assertIsInstance(response.context['form'], NoteForm)
