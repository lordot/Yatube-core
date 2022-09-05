from django.test import TestCase, Client
from django.urls import reverse

from ..models import User, Post


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = User.objects.create(username='user1')
        cls.user2 = User.objects.create(username='user2')
        cls.user3 = User.objects.create(username='user3')
        # создаем тестовый пост
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user1,
        )

    def setUp(self):
        self.client1 = Client()
        self.client2 = Client()
        self.client3 = Client()
        self.client1.force_login(self.user1)
        self.client2.force_login(self.user2)
        self.client3.force_login(self.user3)

    def follow(self, author):
        # функция подписки на автора
        self.client2.get(
            reverse('posts:profile_follow',
                    kwargs={'username': author.username}
                    ),
        )

    def test_follow_self(self):
        """ Тест проверяет что нельзя подписаться на себя"""
        self.follow(self.user2)
        count_follows = self.user2.following.all().count()
        self.assertEqual(count_follows, 0)

    def test_follow_author(self):
        """ Тест подписки на автора """
        self.follow(self.user1)
        count_follows = self.user1.following.all().count()
        self.assertEqual(count_follows, 1)


    def test_follow_posts(self):
        """
        Тест проверяет наличие поста у подписавшихся
        и их отсутствие у других пользователей
        """
        self.follow(self.user1)
        response_user2 = self.client2.get(reverse('posts:index'))
        context_user2 = response_user2.context['page_obj'][0]
        response_user3 = self.client3.get(reverse('posts:follow_index'))
        context_user3 = response_user3.context['page_obj']
        self.assertEqual(context_user2.text, self.post.text)
        self.assertEqual(len(context_user3), 0)

    def test_unfollow_author(self):
        """ Тест отписки от автора """
        self.client2.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.user1.username}
                    ),
        )
        count_follows = self.user1.following.all().count()
        self.assertEqual(count_follows, 0)
