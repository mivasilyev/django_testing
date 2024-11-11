from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture as lf

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url_reverse, parametrized_client, status',
    (
        (lf('url_home'), lf('client'), HTTPStatus.OK),
        (lf('url_login'), lf('client'), HTTPStatus.OK),
        (lf('url_logout'), lf('client'), HTTPStatus.OK),
        (lf('url_signup'), lf('client'), HTTPStatus.OK),
        (lf('url_news'), lf('client'), HTTPStatus.OK),
        (lf('url_edit'), lf('author_client'), HTTPStatus.OK),
        (lf('url_delete'), lf('author_client'), HTTPStatus.OK),
        (lf('url_edit'), lf('not_author_client'), HTTPStatus.NOT_FOUND),
        (lf('url_delete'), lf('not_author_client'), HTTPStatus.NOT_FOUND)
    )
)
def test_pages_availability(url_reverse, parametrized_client, status):
    response = parametrized_client.get(url_reverse)
    assert response.status_code == status


@pytest.mark.parametrize(
    'url_reverse',
    (lf('url_edit'), lf('url_delete'))
)
def test_redirect_for_anonimous(client, url_reverse, url_login):
    """
    При попытке перейти на страницу редактирования или удаления комментария
    анонимный пользователь перенаправляется на страницу авторизации.
    """
    url_expected = f'{url_login}?next={url_reverse}'
    response = client.get(url_reverse)
    assertRedirects(response, url_expected)
