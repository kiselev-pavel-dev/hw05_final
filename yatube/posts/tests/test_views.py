import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms

from yatube.settings import POSTS_ON_PAGE

from ..models import Comment, Follow, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestImagePages(TestCase):
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
            image=uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_context_image(self):
        """Проверяем context страниц с постами приложения posts."""
        slug = self.group_test.slug
        username = self.user.username
        image = self.post_test.image
        post_id = self.post_test.pk
        page_list = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': slug}),
            reverse('posts:profile', kwargs={'username': username}),
        ]
        for page in page_list:
            response = self.authorized_client.get(page)
            first_object = response.context['page_obj'][0]
            self.assertEqual(first_object.image, image)
        page = reverse('posts:post_detail', kwargs={'post_id': post_id})
        response = self.authorized_client.get(page)
        self.assertEqual(response.context.get('post').image, image)


class PaginatorViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='NoName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group_test = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Описание тестовой группы'
        )
        post_list = []
        for i in range(0, 13):
            new_post = Post(
                text=f'Тестовый пост контент {i}',
                group=cls.group_test,
                author=cls.user
            )
            post_list.append(new_post)
        Post.objects.bulk_create(post_list)

    def test_first_page(self):
        """Тестируем первую страницу пагинатора."""
        slug = self.group_test.slug
        username = self.user.username
        page_list = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': slug}),
            reverse('posts:profile', kwargs={'username': username})
        ]
        for page in page_list:
            response = self.authorized_client.get(page)
            self.assertEqual(len(response.context['page_obj']), POSTS_ON_PAGE)

    def test_second_page(self):
        """Тестируем вторую страницу пагинатора."""
        slug = self.group_test.slug
        username = self.user.username
        page_list = {
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': slug}),
            reverse('posts:profile', kwargs={'username': username})
        }
        count_posts = Post.objects.count()
        count = count_posts - POSTS_ON_PAGE
        for page in page_list:
            response = self.authorized_client.get(page + '?page=2')
            self.assertEqual(len(response.context['page_obj']), count)


class PostViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='NoName',
            first_name='Иван',
            last_name='Иванов'
        )
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
            description='Описание второй тестовой группы'
        )
        cls.post_test = Post.objects.create(
            text='Тестовый пост контент',
            group=cls.group_test,
            author=cls.user,
        )

    def test_pages_correct_templates(self):
        """Проверяем URL с шаблоном."""
        slug = self.group_test.slug
        username = self.user.username
        post_id = self.post_test.pk
        template_pages = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': post_id}
            ): 'posts/create_post.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': post_id}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html'
        }
        for reverse_name, template in template_pages.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_context_index(self):
        """Проверяем context страниц с постами приложения posts."""
        slug = self.group_test.slug
        username = self.user.username
        full_name = self.user.get_full_name()
        page_list = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': slug}),
            reverse('posts:profile', kwargs={'username': username})
        ]
        for page in page_list:
            response = self.authorized_client.get(page)
            first_object = response.context['page_obj'][0]
            self.assertEqual(first_object.text, self.post_test.text)
            self.assertEqual(
                first_object.author.get_full_name(), full_name)
            self.assertEqual(first_object.group.slug, slug)

    def test_post_detail(self):
        """Тестируем страницу одного поста."""
        post_id = self.post_test.pk
        full_name = self.user.get_full_name()
        slug = self.group_test.slug
        post_text = self.post_test.text
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': post_id}))
        self.assertEqual(
            response.context.get('post').text, post_text)
        self.assertEqual(
            response.context.get('post').author.get_full_name(), full_name)
        self.assertEqual(response.context.get('post').group.slug, slug)

    def test_context_posts_create(self):
        """Тестируем страницу создания поста."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for tag, expected in form_fields.items():
            with self.subTest(tag=tag):
                form_field = response.context.get('form').fields.get(tag)
                self.assertIsInstance(form_field, expected)

    def test_context_post_edit(self):
        """Проверяем страницу редактирования поста."""
        post_id = self.post_test.pk
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': post_id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for tag, expected in form_fields.items():
            with self.subTest(tag=tag):
                form_field = response.context.get('form').fields.get(tag)
                self.assertIsInstance(form_field, expected)

    def test_post_in_group(self):
        """Проверяем что пост не появился в другой группе."""
        slug = self.group_test_2.slug
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': slug}))
        count_object = len(response.context['page_obj'])
        self.assertEqual(count_object, 0)

    def test_cache_index(self):
        """Проверяем что главная отдает кэшированные данные."""
        response_1 = self.authorized_client.get(reverse('posts:index'))
        count_1 = len(response_1.context['page_obj'])
        Post.objects.create(
            text='Тестовый пост контент 2',
            group=self.group_test,
            author=self.user,
        )
        response_2 = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response_1.content, response_2.content)
        cache.clear()
        response_3 = self.authorized_client.get(reverse('posts:index'))
        count_3 = len(response_3.context['page_obj'])
        self.assertEqual(count_3, count_1 + 1)


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_1 = User.objects.create(username='User')
        cls.user_2 = User.objects.create(username='User_2')
        cls.user_3 = User.objects.create(username='User_3')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user_1)
        cls.authorized_client_2 = Client()
        cls.authorized_client_2.force_login(cls.user_2)
        cls.group_test = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Описание тестовой группы'
        )
        cls.post_test = Post.objects.create(
            text='Тестовый пост контент',
            group=cls.group_test,
            author=cls.user_2,
        )
        cls.test_follow = Follow.objects.create(
            user=cls.user_1,
            author=cls.user_2
        )

    def test_profile_follow(self):
        """Проверяем что пользователь может подписаться."""
        follow_count = Follow.objects.count()
        username = self.user_3.username
        self.authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': username}
        ))
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        new_follow = Follow.objects.last()
        self.assertEqual(new_follow.user, self.user_1)
        self.assertEqual(new_follow.author, self.user_3)

    def test_profile_unfollow(self):
        """Проверяем что пользователь может отписаться."""
        follow_count = Follow.objects.count()
        username = self.user_2.username
        self.authorized_client.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': username}
        ))
        self.assertEqual(Follow.objects.count(), follow_count - 1)

    def test_add_post_in_follower(self):
        """Проверяем что пост появляется в ленте у тех, кто подписан."""
        Follow.objects.create(
            user=self.user_1,
            author=self.user_3,
        )
        new_post = Post.objects.create(
            text='Тестовый пост контент новый',
            group=self.group_test,
            author=self.user_3,
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        first = response.context['page_obj'][0]
        self.assertEqual(first.text, new_post.text)

    def test_no_add_post_in_follower(self):
        """Проверяем что пост не появляется в ленте у тех, кто
        не подписан."""
        posts = Post.objects.filter(author=self.user_2).count()
        Post.objects.create(
            text='Тестовый пост контент новый',
            group=self.group_test,
            author=self.user_3,
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        count_posts = len(response.context['page_obj'])
        self.assertEqual(count_posts, posts)


class ComentTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='NoName')
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

    def test_comment_add_on_page(self):
        """Проверка что комментарий добавился к посту."""
        post_id = self.post_test.pk
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': post_id}),
        )
        first_object = response.context['comments'][0]
        self.assertEqual(first_object.text, self.comment_test.text)
        self.assertEqual(first_object.author, self.comment_test.author)
