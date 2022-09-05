from http import HTTPStatus

from django.test import TestCase, Client
from ..models import User, Post, Group


class PostsURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_homepage(self):
        """ Тест проверяет работу главной страницы """
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_urls_status(self):
        """ Тест проверяет работу страниц группы, профиля и поста """
        statues_urls = (
            f'/group/{self.group.slug}/',
            f'/profile/{self.user.username}/',
            f'/posts/{self.post.pk}/',
        )
        for address in statues_urls:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_urls_uses_correct_templates(self):
        """ Тест проверяет корректность передаваемых шаблонов """
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
            '/none/': 'core/404.html',
        }

        for address, template in templates_url_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_redirect(self):
        """ Тест проверяет редиректы от гостя """
        redirect_urls = {
            '/create/':
                '/auth/login/?next=/create/',
            f'/posts/{self.post.pk}/edit/':
                f'/posts/{self.post.pk}/',
            f'/posts/{self.post.pk}/comment/':
                f'/auth/login/?next=/posts/{self.post.pk}/comment/',
        }
        for address, redirect in redirect_urls.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertRedirects(response, redirect)
