from datetime import datetime, timedelta
import pytest

from django.urls import reverse

from news.forms import CommentForm
from news.models import Comment


# Количество новостей на главной странице — не более 10.
@pytest.mark.django_db
def test_homepage_news_limit(client):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    notes_count = object_list.count()
    assert notes_count <= 10


# Новости отсортированы. Свежие новости в начале списка.
@pytest.mark.django_db
def test_homepage_news_sorted(client):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


# Комментарии на странице отдельной новости отсортированы в хронологическом
# порядке: старые в начале списка, новые — в конце.
def test_comments_order(client, author, news):
    today = datetime.today()
    all_comments = [
        Comment(
            news=news,
            text=f'Комментарий {index}',
            author=author,
            created=today - timedelta(days=index)
        )
        for index in range(4)
    ]
    Comment.objects.bulk_create(all_comments)
    url = reverse('news:detail', args=(news.pk,))
    response = client.get(url)
    news = response.context['news']
    comments = news.comment_set.all()
    timestamps = [comment.created for comment in comments]
    timestamps_sorted = sorted(timestamps)
    assert timestamps == timestamps_sorted


# Анонимному пользователю недоступна форма для отправки комментария на
# странице отдельной новости, а авторизованному доступна.
def test_news_detail_contains_form_authorized(author_client, news):
    url = reverse('news:detail', args=(news.pk,))
    response = author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)


@pytest.mark.django_db
def test_news_detail_contains_no_form_anonimous(client, news):
    url = reverse('news:detail', args=(news.pk,))
    response = client.get(url)
    assert 'form' not in response.context
