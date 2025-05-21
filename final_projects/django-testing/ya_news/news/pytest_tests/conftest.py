from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News

User = get_user_model()


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    return News.objects.create(title='Заголовок', text='Текст новости')


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
    )


@pytest.fixture
def news_with_comments(author, news):
    for index in range(3):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Текст {index}'
        )
        comment.created = timezone.now() + timedelta(days=index)
        comment.save()
    return news, reverse('news:detail', args=(news.id,))


@pytest.fixture
def multiple_news():
    today = datetime.today()
    all_news = News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Просто текст',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )
    return all_news


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def news_url(comment):
    return reverse('news:detail', args=(comment.news.id,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


# @pytest.fixture
# def login_url():
#     return reverse('users:login')


# @pytest.fixture
# def logout_url():
#     return reverse('users:logout')


# @pytest.fixture
# def signup_url():
#     return reverse('users:signup')


@pytest.fixture
def initial_comment_count():
    return Comment.objects.count()


@pytest.fixture
def clear_comments():
    Comment.objects.all().delete()
