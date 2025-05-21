from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.utils.text import slugify
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='testAuthor')
        cls.other_user = User.objects.create(username='testOtherUser')

        cls.note = Note.objects.create(
            title='Заметка 1',
            text='Текст 1',
            slug=slugify('zametka-1'),
            author=cls.author
        )

        cls.other_note = Note.objects.create(
            title='Заметка 2',
            text='Текст 2',
            slug=slugify('zametka-2'),
            author=cls.other_user
        )

        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.other_client = Client()
        cls.other_client.force_login(cls.other_user)
        cls.anonymous_client = Client()

        # cls.list_url = reverse('notes:list')
        # cls.add_url = reverse('notes:add')
        # cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))

        cls.home_url = reverse('notes:home')
        cls.login_url = reverse('users:login')
        cls.signup_url = reverse('users:signup')
        cls.logout_url = reverse('users:logout')
        cls.list_url = reverse('notes:list')
        cls.success_url = reverse('notes:success')
        cls.add_url = reverse('notes:add')
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))

        cls.public_urls = [
            cls.home_url,
            cls.login_url,
            cls.signup_url,
            cls.logout_url,
        ]

        cls.private_urls = [
            cls.list_url,
            cls.success_url,
            cls.add_url,
        ]

        cls.note_urls = [
            cls.detail_url,
            cls.edit_url,
            cls.delete_url,
        ]
