import pytest
from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_news_count_on_home_page(client, multiple_news, home_url):
    """Проверяет, что на главной странице не более 10 новостей."""
    response = client.get(home_url)
    object_list = response.context['object_list']
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, multiple_news, home_url):
    """Делаем проверку, что новости отсортированы от свежих к старым."""
    response = client.get(home_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(client, news_with_comments):
    """Тестируем сортировку комментариев: старые в начале, новые - в конце."""
    news, detail_url = news_with_comments
    response = client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


def test_anonymous_client_has_no_form(client, news_with_comments):
    """
    Проверяем, что анонимному пользователю недоступна форма
    для отправки комментария на странице отдельной новости.
    """
    _, detail_url = news_with_comments
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, news_with_comments):
    """
    Проверяем, что авторизованному пользователю доступна форма
    для отправки комментария на странице отдельной новости.
    """
    _, detail_url = news_with_comments
    response = author_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
