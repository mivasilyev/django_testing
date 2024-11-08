from http import HTTPStatus
import pytest

from pytest_django.asserts import assertRedirects
from django.urls import reverse

from news.forms import BAD_WORDS
from news.models import Comment


# Анонимный пользователь не может отправить комментарий.
@pytest.mark.django_db
def test_anonimous_cant_create_comment(client, news, form_data):
    url = reverse('news:detail', args=(news.pk,))
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    response = client.post(url, data=form_data)
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


# Авторизованный пользователь может отправить комментарий.
def test_author_can_create_comment(author_client, news, form_data):
    url = reverse('news:detail', args=(news.pk,))
    author_client.post(url, data=form_data)
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    # Сверяем атрибуты объекта с ожидаемыми.
    assert new_comment.text == form_data['text']


# Авторизованный пользователь может редактировать свои комментарии.
def test_author_can_edit_comment(author_client, comment, form_data):
    url = reverse('news:edit', args=(comment.pk,))
    author_client.post(url, data=form_data)
    assert comment.pk == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']


# Авторизованный пользователь может удалять свои комментарии.
def test_author_can_delete_comment(author_client, news, comment):
    url = reverse('news:delete', args=(comment.pk,))
    expected_url = reverse('news:detail', args=(news.pk,)) + '#comments'
    response = author_client.post(url)
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0

# Авториз/ пользователь не может редактировать и удалять чужие комментарии.
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_author_cant_edit_and_delete_others_comment(
        not_author_client, name, comment, form_data
    ):
    url = reverse(name, args=(comment.pk,))
    comment_text = comment.text
    not_author_client.post(url, data=form_data)
    assert Comment.objects.count() == 1
    assert Comment.objects.get().text == comment_text


# Если комментарий содержит запрещённые слова, он не будет опубликован, а
# форма вернёт ошибку.
def test_restricted_words_in_comment(author_client, news):
    url = reverse('news:detail', args=(news.pk,))
    response = author_client.post(url, data={'text': f'Слово {BAD_WORDS[0]}'})
    assert response.context['form'].errors
    assert Comment.objects.count() == 0
