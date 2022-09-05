import tempfile
import shutil

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.core.cache import cache
from django.test import TestCase, Client, override_settings

from ..models import User, Post, Group

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.MEDIA_ROOT)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTest(TestCase):
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
        cls.user = User.objects.create(username='auth')
        cls.group = Group.objects.create(
            slug='test-slug',
            title='Тестовая группа',
            description='Описание тестовой группы',
        )
        # создаем тестовый пост
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=cls.group,
            image=uploaded
        )

    @classmethod
    def tearDownClass(cls):
        """ удаляем временную папку с картинкой """
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # создаем гостя и авторизированного пользователя
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def context_check(self, post):
        """ Функция проверки контекста """
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.image, self.post.image)

    def test_views_uses_correct_templates(self):
        """тест проверяет правильность переданных views шаблонов"""
        templates_url_names = {
            reverse('posts:index'):
            'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
            'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user.username}):
            'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}):
            'posts/post_detail.html',
            reverse('posts:post_create'):
            'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}):
            'posts/create_post.html',
        }

        for reverse_name, template in templates_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_context(self):
        """ тест проверяет context на главной странице """
        response = self.guest_client.get(reverse('posts:index'))
        post = response.context['page_obj'][0]
        self.context_check(post)

    def test_group_list(self):
        """ тест проверяет context на странице группы """
        address = reverse('posts:group_list', kwargs={'slug': self.group.slug})
        response = self.guest_client.get(address)
        group = response.context['group']
        post = response.context['page_obj'][0]
        self.assertEqual(group.title, self.group.title)
        self.context_check(post)

    def test_profile(self):
        """ тест проверяет context на странице автора """
        address = reverse('posts:profile', kwargs={'username': 'auth'})
        response = self.guest_client.get(address)
        author = response.context['author']
        post = response.context['page_obj'][0]
        self.assertEqual(author.username, self.user.username)
        self.context_check(post)

    def test_post_detail(self):
        """ тест проверяет подробную страницу поста """
        address = reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.pk}
        )
        response = self.guest_client.get(address)
        post = response.context['post']
        self.assertEqual(post.id, self.post.pk)
        self.context_check(post)

    def test_index_cache(self):
        """
        Тест сравнивает два запроса главной страницы до и после очистки кеша
        """
        self.authorized_client.post(
            reverse('posts:post_create'),
            {'text': 'Новый пост'},
            follow=True
        )
        bef_clear = self.authorized_client.get(reverse('posts:index')).content
        cache.clear()
        aft_clear = self.authorized_client.get(reverse('posts:index')).content
        self.assertNotEqual(bef_clear, aft_clear)


