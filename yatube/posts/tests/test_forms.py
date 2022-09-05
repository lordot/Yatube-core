import shutil
import tempfile

from django.conf import settings
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from ..models import Post, User, Comment

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.MEDIA_ROOT)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class FormsTestClass(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='auth')

    @classmethod
    def tearDownClass(cls):
        """ удаляем временную папку с картинкой """
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # создаем новый пост
        self.post = Post.objects.create(
            text='Тестовый пост',
            author=self.user,
        )

    def test_create_post_from_form(self):
        """ Тест проверяет создание нового поста с картинкой """
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
        form_data = {
            'author': self.user,
            'title': 'Тестовый заголовок',
            'text': 'Тестовый текст',
            'image': uploaded,
        }
        posts_count = Post.objects.count()
        # отправляем пост через форму
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        # проверяем количество созданных постов
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_edit_post_from_form(self):
        """ Тест проверяет редактирование поста """
        # редактируем пост
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            {'text': 'Измененное сообщение'},
            follow=True
        )
        post_edit = Post.objects.get(pk=self.post.pk)
        # проверяем результат редактирования
        self.assertEqual(post_edit.text, 'Измененное сообщение')

    def test_post_edit_only_author(self):
        """ Тест проверяет, что только автор может редактировать свой пост """
        another_user = User.objects.create(username='someone')
        someone = Client()
        someone.force_login(user=another_user)
        someone.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            {'text': 'Текст изменил другой пользователь'}
        )
        post_edit = Post.objects.get(pk=self.post.pk)
        self.assertNotEqual(
            post_edit.text,
            'Текст изменил другой пользователь'
        )

    def test_add_comment(self):
        """ Тест проверяет форму добавления комментария """
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            {'text': 'Это тестовый комментарий'}
        )
        comment = self.post.comments.first()
        self.assertEqual(comment.text, 'Это тестовый комментарий')

    def test_add_comment_only_user(self):
        """
        Тест проверяет, что только авторизированный пользователь
        может оставить комментарий
        """
        self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            {'text': 'Это комментарий гостя'}
        )
        comment = self.post.comments.first()
        self.assertIsNone(comment)

    def test_form_create_post(self):
        """ тест проверяет форму создания поста """
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_form_edit_post(self):
        """ тест проверяет форму редактирования поста """
        address = reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
        response = self.authorized_client.get(address)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
