from http import HTTPStatus
import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

COMMENT_TEXT = 'Текст комментария'
NEW_COMMENT_TEXT = 'Обновлённый комментарий'
COMMENT_FORM_DATA = {'text': 'Текст комментария'}

@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
    client, detail_url, clear_comments
):
    """Проверка - анонимный пользователь не может отправить комментарий."""
    client.post(detail_url, data=COMMENT_FORM_DATA)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_can_create_comment(
    author_client, detail_url, author, news, clear_comments
):
    """Проверка - авторизованный пользователь может отправить комментарий."""
    response = author_client.post(detail_url, data=COMMENT_FORM_DATA)
    assertRedirects(response, f'{detail_url}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == COMMENT_FORM_DATA['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, detail_url, clear_comments):
    """Проверка запрещенных слов."""
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(detail_url, data=bad_words_data)
    assert 'form' in response.context
    form = response.context['form']
    assertFormError(form, 'text', WARNING)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_can_delete_comment(
    author_client, comment, initial_comment_count, news_url, delete_url
):
    """
    Тестируем, что авторизованный пользователь может удалять
    свои комментарии.
    """
    response = author_client.post(delete_url)
    assertRedirects(response, f'{news_url}#comments')
    assert Comment.objects.count() == initial_comment_count - 1


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(
    not_author_client, comment, initial_comment_count
):
    """
    Проверяем, что авторизованный пользователь не может удалять
    комментарии другого пользователя.
    """
    delete_url = reverse('news:delete', args=(comment.id,))
    response = not_author_client.post(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == initial_comment_count


@pytest.mark.django_db
def test_author_can_edit_comment(
    author_client, comment, news_url, delete_url, edit_url
):
    """
    Тестируем, что авторизованный пользователь может редактировать
    свои комментарии.
    """
    initial_data = {
        'text': comment.text,
        'news': comment.news,
        'author': comment.author,
        'created': comment.created,
    }
    form_data = COMMENT_FORM_DATA.copy()
    form_data['text'] = NEW_COMMENT_TEXT
    response = author_client.post(edit_url, data=form_data)
    assertRedirects(response, f'{news_url}#comments')
    comment.refresh_from_db()
    assert comment.text == NEW_COMMENT_TEXT
    assert comment.news == initial_data['news']
    assert comment.author == initial_data['author']
    assert comment.created == initial_data['created']
    assert Comment.objects.count() == 1


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(not_author_client, comment, edit_url):
    """
    Проверяем, что авторизованный пользователь не может редактировать
    комментарии другого пользователя.
    """
    initial_data = {
        'text': comment.text,
        'news': comment.news,
        'author': comment.author,
        'created': comment.created,
    }
    form_data = COMMENT_FORM_DATA.copy()
    form_data['text'] = NEW_COMMENT_TEXT
    response = not_author_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == initial_data['text'] == COMMENT_TEXT
    assert comment.news == initial_data['news']
    assert comment.author == initial_data['author']
    assert comment.created == initial_data['created']
    assert Comment.objects.count() == 1
