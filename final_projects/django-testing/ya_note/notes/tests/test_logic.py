from http import HTTPStatus
from django.urls import reverse
from pytils.translit import slugify as pytils_slugify

from notes.models import Note
from .base import BaseTestCase


class TestLogic(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.note_data = {
            'title': 'Новая заметка',
            'text': 'Текст новой заметки',
            'slug': 'novaya-zametka'
        }
        cls.edit_data = {
            'title': 'Отредактированная заметка',
            'text': 'Новый текст',
            'slug': 'otredaktirovannaya-zametka'
        }

    def test_authenticated_user_can_create_note(self):
        """
        Проверяет, что авторизованный пользователь может создать заметку,
        а анонимный пользователь перенаправляется на страницу логина.
        """
        url = reverse('notes:add')
        response = self.author_client.post(url, data=self.note_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.filter(slug='novaya-zametka').count(), 1)

        response = self.anonymous_client.post(url, data=self.note_data)
        login_url = reverse('users:login')
        self.assertRedirects(response, f'{login_url}?next={url}')
        self.assertEqual(Note.objects.filter(slug='novaya-zametka').count(), 1)

    def test_cannot_create_notes_with_same_slug(self):
        """
        Проверяет, что нельзя создать две заметки с одинаковым slug.
        Ожидается ошибка формы и отсутствие новой заметки в базе данных.
        """
        note_data = {
            'title': 'Ещё одна заметка',
            'text': 'Текст',
            'slug': self.note.slug
        }
        url = reverse('notes:add')
        response = self.author_client.post(url, data=note_data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        form = response.context.get('form')
        self.assertIn('form', response.context)
        expected_error = (
            f"{self.note.slug} - такой slug уже существует, "
            "придумайте уникальное значение!"
        )
        self.assertFormError(form, 'slug', expected_error)
        self.assertEqual(Note.objects.filter(slug=self.note.slug).count(), 1)

    def test_auto_slug_generation(self):
        """
        Проверяет, что при создании заметки без указания slug он генерируется
        автоматически на основе заголовка с помощью pytils.translit.slugify.
        """
        Note.objects.all().delete()
        note_data = {
            'title': 'Заметка без slug',
            'text': 'Текст',
        }
        url = reverse('notes:add')
        response = self.author_client.post(url, data=note_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.first()
        expected_slug = pytils_slugify(note_data['title'])[:100]
        self.assertEqual(new_note.slug, expected_slug)

    def test_user_can_edit_own_note(self):
        """Проверка, что автор может редактировать свою заметку."""
        edit_data = {
            'title': 'Отредактированная заметка',
            'text': 'Новый текст',
            'slug': 'otredaktirovannaya-zametka'
        }
        edit_url = reverse('notes:edit', args=(self.note.slug,))
        response = self.author_client.post(edit_url, data=edit_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, edit_data['title'])
        self.assertEqual(self.note.text, edit_data['text'])
        self.assertEqual(self.note.slug, edit_data['slug'])

    def test_user_cannot_edit_others_note(self):
        """
        Проверка, что другой пользователь не может редактировать чужую заметку.
        """
        edit_url = reverse('notes:edit', args=(self.note.slug,))
        response = self.other_client.post(edit_url, data=self.edit_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertNotEqual(self.note.title, self.edit_data['title'])

    def test_user_can_delete_own_note(self):
        """Проверка, что автор может удалить свою заметку."""
        delete_url = reverse('notes:delete', args=(self.note.slug,))
        response = self.author_client.post(delete_url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)

    def test_user_cannot_delete_others_note(self):
        """Проверка, что другой пользователь не может удалить чужую заметку."""
        delete_url = reverse('notes:delete', args=(self.note.slug,))
        response = self.other_client.post(delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 2)
