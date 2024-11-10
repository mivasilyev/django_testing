import pytest

from news.forms import CommentForm
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE


pytestmark = pytest.mark.django_db


def test_homepage_news_limit(client, url_home, many_news):
    """Количество новостей на гравной странице не более заданного."""
    response = client.get(url_home)
    object_list = response.context['object_list']
    notes_count = object_list.count()
    assert notes_count <= NEWS_COUNT_ON_HOME_PAGE


def test_homepage_news_sorted(client, url_home, many_news):
    """Новости отсортированы. Свежие новости в начале списка."""
    response = client.get(url_home)
    all_dates = [news.date for news in response.context['object_list']]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(client, url_news, many_comments):
    """Комментарии на странице новости отсортированы. Старые в начале."""
    response = client.get(url_news)
    news = response.context['news']
    comments = news.comment_set.all()
    timestamps = [comment.created for comment in comments]
    timestamps_sorted = sorted(timestamps)
    assert timestamps == timestamps_sorted


def test_news_detail_contains_form_authorized(author_client, url_news):
    """
    Авторизованному пользователю доступна форма комментирования на странице
    отдельной новости.
    """
    response = author_client.get(url_news)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)


def test_news_detail_contains_no_form_anonimous(client, url_news):
    """Анониму недоступна форма комментирования на странице новости."""
    response = client.get(url_news)
    assert 'form' not in response.context
