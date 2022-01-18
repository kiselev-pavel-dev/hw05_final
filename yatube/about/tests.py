from http import HTTPStatus

from django.test import Client, TestCase


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()

    def test_about(self):
        """Проверка доступности страниц приложения about."""
        pages_template = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/'
        }
        for template, adress in pages_template.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_404(self):
        """Проверка несуществующей страницы."""
        response = self.guest_client.get('/about/test404')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'core/404.html')
