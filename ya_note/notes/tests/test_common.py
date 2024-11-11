from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestCommon(TestCase):

    MULTIPLE_NOTES = 3

    @classmethod
    def setUpTestData(cls):
        # Пользователи и клиенты.
        cls.author = User.objects.create(username='author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.author_second = User.objects.create(username='author_second')
        cls.author_second_client = Client()
        cls.author_second_client.force_login(cls.author_second)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        # Заметки
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
        cls.note = Note.objects.get(slug='slug0')
        # Реверсы
        cls.url_login_reverse = reverse('users:login')
        cls.url_del_reverse = reverse('notes:delete', args=(cls.note.slug,))
        cls.url_done_reverse = reverse('notes:success')
        cls.url_notes_reverse = reverse('notes:list')
        cls.url_detail_reverse = reverse(
            'notes:detail', args=(cls.note.slug,)
        )
        cls.url_edit_reverse = reverse('notes:edit', args=(cls.note.slug,))
        cls.url_add_reverse = reverse('notes:add')
        cls.urls = (cls.url_add_reverse, cls.url_edit_reverse)
        cls.urls_available_reverse = [
            reverse('notes:home'),
            reverse('users:signup'),
            reverse('users:logout'),
        ] + [cls.url_login_reverse]
        cls.urls_logged_available_reverse = [
            cls.url_notes_reverse,
            cls.url_add_reverse,
            cls.url_done_reverse
        ]
        cls.urls_author_available_reverse = [
            cls.url_detail_reverse,
            cls.url_edit_reverse,
            cls.url_del_reverse
        ]
        cls.anonimous_login_redirect_reverse = (
            cls.urls_logged_available_reverse
            + cls.urls_author_available_reverse
        )
        # Содержимое формы для запроса
        cls.form_data = {
            'title': 'Новая заметка',
            'text': 'Текст новой заметки'
        }
