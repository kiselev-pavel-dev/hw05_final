import shutil
import tempfile

from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp()


class CommentFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='NoName')
        cls.guest_client = Client()
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
        cls.comment_test = Comment.objects.create(
            text='Тестовый комментарий',
            post=cls.post_test,
            author=cls.user
        )

    def test_authorized_comment_add(self):
        """Проверка что авторизованный пользователь может добавить
        комментарий."""
        comments_count = Comment.objects.count()
        post_id = self.post_test.pk
        form_data = {
            'text': 'Тестовый комментарий 2'
        }
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': post_id}),
            data=form_data
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)

    def test_guest_comment_add(self):
        """Проверка что гостевой пользователь не может добавить
        комментарий."""
        comments_count = Comment.objects.count()
        post_id = self.post_test.pk
        form_data = {
            'text': 'Тестовый комментарий 2'
        }
        self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': post_id}),
            data=form_data
        )
        self.assertEqual(Comment.objects.count(), comments_count)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create(username='NoName')
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group_test = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Описание тестовой группы'
        )
        cls.group_test_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test_2',
            description='Описание тестовой группы 2'
        )
        cls.post_test = Post.objects.create(
            text='Тестовый пост контент',
            group=cls.group_test,
            author=cls.user,
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_form_post(self):
        """Проверяем что при POST запросе создается запись в БД."""
        post_count = Post.objects.count()
        username = self.user.username
        form_fields = {
            'text': 'Тестовый пост контент 2',
            'group': self.group_test.pk,
            'image': self.post_test.image
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_fields,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': username}
        ))
        self.assertEqual(Post.objects.count(), post_count + 1)
        new_post = Post.objects.latest('pub_date')
        self.assertEqual(new_post.text, form_fields['text'])
        self.assertEqual(new_post.author.username, username)
        self.assertEqual(new_post.group, self.group_test)

    def test_form_edit(self):
        """Проверяем редактирование поста."""
        post_id = self.post_test.pk
        username = self.user.username
        form_fields = {
            'text': 'Тестовый пост контент редакт',
            'group': self.group_test_2.pk
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post_id}),
            data=form_fields,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': post_id}
        ))
        post = Post.objects.get(pk=post_id)
        self.assertEqual(post.text, form_fields['text'])
        self.assertEqual(post.author.username, username)
        self.assertEqual(post.group, self.group_test_2)

    def test_guest_create_post(self):
        """Проверка что неавторизованный юзер
        не сможет создать пост."""
        post_count = Post.objects.count()
        form_fields = {
            'text': 'Тестовый пост контент 2',
            'group': self.group_test.pk
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_fields,
        )
        redirect = "%s?next=%s" % (
            reverse('users:login'), reverse('posts:post_create')
        )
        self.assertRedirects(response, redirect)
        self.assertEqual(Post.objects.count(), post_count)
