from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Comment, Group, Post

User = get_user_model()


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
        комментарий и он появился на странице поста."""
        comments_count = Comment.objects.count()
        post_id = self.post_test.pk
        form_data = {
            'text': 'Тестовый комментарий 2'
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': post_id}),
            data=form_data
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        new_comment = Comment.objects.latest('pub_date')
        response = self.authorized_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': post_id}
        ))
        first_object = response.context['comments'][0]
        self.assertEqual(first_object.text, new_comment.text)


class PostFormsTest(TestCase):
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
        cls.group_test_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test_2',
            description='Описание тестовой группы 2'
        )
        cls.post_test = Post.objects.create(
            text='Тестовый пост контент',
            group=cls.group_test,
            author=cls.user,
        )

    def test_form_post(self):
        """Проверяем что при POST запросе создается запись в БД."""
        post_count = Post.objects.count()
        username = self.user.username
        form_fields = {
            'text': 'Тестовый пост контент 2',
            'group': self.group_test.pk
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
