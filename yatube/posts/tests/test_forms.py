from django.contrib.auth import get_user_model
from ..models import Post, Group
from django.test import Client, TestCase
from django.urls import reverse
from .constants import (
    AUTHOR_USERNAME,
    GROUP_TITLE,
    GROUP_SLUG,
    GROUP_DESCRIPTION,
    POST_TEXT,
)

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=AUTHOR_USERNAME)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION
        )
        cls.post = Post.objects.create(
            text="Andrew",
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.GROUP_ID = self.group.pk

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        post_count = Post.objects.count()
        form_data = {
            'text': POST_TEXT,
            'group': self.GROUP_ID,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, f'/profile/{AUTHOR_USERNAME}/')
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=POST_TEXT,
                group=self.GROUP_ID,
            ).exists()
        )

    def test_edit_post(self):
        """Валидная форма изменяет запись в базе данных"""
        form_data = {
            'text': 'Новый текст'
        }
        self.author = self.post.author
        id = self.post.id
        self.authorized_client.post(reverse('posts:post_edit', args=[id]),
                                            data=form_data,
                                            follow=True)
        self.assertNotEqual(self.post.text, 'Новый текст')
