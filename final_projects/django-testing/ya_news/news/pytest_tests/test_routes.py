from http import HTTPStatus
import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects
from pytest_lazy_fixtures import lf

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'name',
    ('news:home', 'users:login', 'users:signup')
)
def test_home_availability_for_anonimous_user_get(client, name):
    """
    Проверяем, что главная страница доступна анонимному пользователю
    и страницы регистрации, входа в учетную запись и выхода из неё
    доступны анонимным пользователям.
    """
    url = reverse(name)
    # if name == 'users:logout':
    #     response = client.post(url)
    # else:
    #     response = client.get(url)
    # assert response.status_code == HTTPStatus.OK
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_logout_page_available_for_anonymous_user(client):
    url = reverse('users:logout')
    response = client.post(url)
    assert response.status_code == HTTPStatus.OK


def test_detail_page(client, news):
    """
    Проверяем, что страница отдельной новости доступна
    анонимному пользователю.
    """
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (lf('not_author_client'), HTTPStatus.NOT_FOUND),
        (lf('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_availability_for_comment_edit_and_delete(
    parametrized_client, name, comment, expected_status
):
    """
    Проверяем, что страницы удаления и редактирования комментария доступны
    автору комментария.
    """
    url = reverse(name, args=(comment.id,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, comment_object',
    (
        ('news:edit', lf('comment')),
        ('news:delete', lf('comment')),
    )
)
def test_redirects(client, name, comment_object):
    """
    Проверка перенаправления анонимного пользователя при попытке перейти
    на страницу редактирования и удаления комментария.
    """
    login_url = reverse('users:login')
    url = reverse(name, args=(comment_object.id,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
