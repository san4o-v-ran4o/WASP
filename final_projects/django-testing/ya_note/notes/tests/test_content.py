from http import HTTPStatus
from django import forms
from django.urls import reverse

from .base import BaseTestCase


class TestContent(BaseTestCase):
    def test_note_in_user_list(self):
        response = self.author_client.get(self.list_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_notes_isolation_for_different_users(self):
        response = self.author_client.get(self.list_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        object_list = response.context['object_list']
        self.assertNotIn(self.other_note, object_list)

        response = self.other_client.get(self.list_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        object_list = response.context['object_list']
        self.assertIn(self.other_note, object_list)
        self.assertNotIn(self.note, object_list)

    def test_forms_in_context(self):
        urls = [self.add_url, self.edit_url]
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertIn('form', response.context)
                self.assertIsInstance(
                    response.context['form'], forms.ModelForm
                )
