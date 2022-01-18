from http import HTTPStatus

from django.test import Client, TestCase


class CorePageTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    def test_page_template_404(self):
        """Проверяем что применился кастомный шаблон 404 страницы."""
        response = self.client.get('/test404/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
