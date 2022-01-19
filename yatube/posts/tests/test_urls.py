from django.contrib.auth import get_user_model
from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create(username="NoName")
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group_test = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Описание тестовой группы'
        )
        cls.post_test = Post.objects.create(
            text='Тестовый пост контент',
            group=cls.group_test,
            author=cls.user,
        )

    def test_public_pages(self):
        """Проверка доступности публичных страниц приложения posts."""
        post_id = self.post_test.pk
        username = self.user.username
        slug = self.group_test.slug
        pages_for_all = {
            'posts/index.html': '/',
            'posts/group_list.html': f'/group/{slug}/',
            'posts/profile.html': f'/profile/{username}/',
            'posts/post_detail.html': f'/posts/{post_id}/',
        }
        for template, adress in pages_for_all.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_private_pages(self):
        """Проверка доступности страниц приложения posts
        для авторизованного пользователя."""
        post_id = self.post_test.pk
        pages_for_authorized = {
            '/create/': 'posts/create_post.html',
            f'/posts/{post_id}/edit/': 'posts/create_post.html',
            '/follow/': 'posts/follow.html',
        }
        for adress, template in pages_for_authorized.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_follow_unfollow_pages(self):
        """Проверка адресов follow и unfollow."""
        username = self.user.username
        pages_test = [
            f'/profile/{username}/follow/',
            f'/profile/{username}/unfollow/'
        ]
        for page in pages_test:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)
                self.assertRedirects(response, reverse('posts:follow_index'))

    def test_comment_url(self):
        """Проверка url комментария."""
        post_id = self.post_test.pk
        url = f'/posts/{post_id}/comment/'
        response = self.authorized_client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_404_page(self):
        """Проверка 404 страницы."""
        pages_404 = '/posts/test404/'
        response = self.authorized_client.get(pages_404)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
