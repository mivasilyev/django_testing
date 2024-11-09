from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url_reverse, parametrized_client, status',
    (
        (
            pytest.lazy_fixture('url_home'),
            pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('url_login'),
            pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('url_logout'),
            pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('url_signup'),
            pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('url_news'),
            pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('url_edit'),
            pytest.lazy_fixture('author_client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('url_delete'),
            pytest.lazy_fixture('author_client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('url_edit'),
            pytest.lazy_fixture('not_author_client'),
            HTTPStatus.NOT_FOUND
        ),
        (
            pytest.lazy_fixture('url_delete'),
            pytest.lazy_fixture('not_author_client'),
            HTTPStatus.NOT_FOUND
        )
    )
)
def test_pages_availability(url_reverse, parametrized_client, status):
    response = parametrized_client.get(url_reverse)
    assert response.status_code == status


@pytest.mark.parametrize(
    'url_reverse',
    (pytest.lazy_fixture('url_edit'), pytest.lazy_fixture('url_delete'))
)
def test_redirect_for_anonimous(client, url_reverse, url_login):
    """
    При попытке перейти на страницу редактирования или удаления комментария
    анонимный пользователь перенаправляется на страницу авторизации.
    """
    url_expected = f'{url_login}?next={url_reverse}'
    response = client.get(url_reverse)
    assertRedirects(response, url_expected)
