from django.urls import reverse
import pytest
from pytest_django.asserts import assertRedirects

from news.forms import BAD_WORDS
from news.models import Comment


pytestmark = pytest.mark.django_db
FORM_DATA = {'text': 'Текст комментария'}


def test_anonimous_cant_create_comment(client, url_news):
    """Анонимный пользователь не может отправить комментарий."""
    initial_count = Comment.objects.count()
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url_news}'
    response = client.post(url_news, data=FORM_DATA)
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == initial_count


def test_author_can_create_comment(news, author, author_client, url_news):
    """Авторизованный пользователь может отправить комментарий."""
    Comment.objects.all().delete()
    author_client.post(url_news, data=FORM_DATA)
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == FORM_DATA['text']
    assert new_comment.author == author
    assert new_comment.news == news


def test_author_can_edit_comment(news, author, author_client, comment):
    """Авторизованный пользователь может редактировать свои комментарии."""
    url = reverse('news:edit', args=(comment.pk,))
    author_client.post(url, data=FORM_DATA)
    new_comment = Comment.objects.get(pk=comment.pk)
    assert new_comment.text == FORM_DATA['text']
    assert new_comment.author == author
    assert new_comment.news == news


def test_author_can_delete_comment(author_client, url_news, comment):
    """Авторизованный пользователь может удалять свои комментарии."""
    initial_count = Comment.objects.count()
    url = reverse('news:delete', args=(comment.pk,))
    expected_url = url_news + '#comments'
    response = author_client.post(url)
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == initial_count - 1


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_author_cant_edit_and_delete_others_comment(
    author, news, not_author_client, name, comment
):
    """
    Авторизованный пользователь не может редактировать и удалять чужие
    комментарии.
    """
    url = reverse(name, args=(comment.pk,))
    comment_text = comment.text
    initial_count = Comment.objects.count()
    not_author_client.post(url, data=FORM_DATA)
    assert Comment.objects.count() == initial_count
    comment = Comment.objects.get(pk=comment.pk)
    assert comment.text == comment_text
    assert comment.author == author
    assert comment.news == news


def test_restricted_words_in_comment(author_client, url_news):
    """
    Если комментарий содержит запрещённые слова, он не будет опубликован,
    а форма вернёт ошибку.
    """
    initial_count = Comment.objects.count()
    response = author_client.post(
        url_news,
        data={'text': f'Слово {BAD_WORDS[0]}'}
    )
    assert Comment.objects.count() == initial_count
    assert response.context['form'].errors
