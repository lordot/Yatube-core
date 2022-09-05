from django.urls import reverse
from django.test import TestCase, Client
from django.conf import settings

from ..models import User, Post, Group


class PaginatorPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='auth')
        cls.group = Group.objects.create(
            slug='test-slug',
            title='Тестовая группа',
            description='Описание тестовой группы',
        )
        # создаем тринадцать постов в цикле
        cls.posts = []
        for i in range(13):
            cls.posts.append(
                Post(
                    text=str(i),
                    author=cls.user,
                    group=cls.group,
                )
            )
        Post.objects.bulk_create(cls.posts)

    def setUp(self):
        # создаем гостя
        self.guest_client = Client()

    def test_second_page_paginator(self):
        """ тест проверяет правильность генерации страниц paginator"""
        paginator_addreses = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username})
        )
        for address in paginator_addreses:
            with self.subTest(address=address):
                response = self.guest_client.get(address + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_page_paginator(self):
        """ тест проверяет первую страницу paginator """
        paginator_addreses = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username}),
        ]
        for address in paginator_addreses:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(
                    len(response.context['page_obj']),
                    settings.POSTS_ON_PAGE)
