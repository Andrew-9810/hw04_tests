from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from ..models import Post, Group
from .constants import (
    INDEX_TEMPLATE,
    GROUP_LIST_TEMPLATE,
    PROFILE_TEMPLATE,
    POST_DETAL_TEMPLATE,
    CREATE_TEMPLATE,
    AUTHOR_USERNAME,
    GROUP_TITLE,
    GROUP_SLUG,
    GROUP_DESCRIPTION,
    POST_TEXT,
    USER_USERNAME
)

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username=AUTHOR_USERNAME)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION
        )
        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.author
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username=USER_USERNAME)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.autor_client = Client()
        self.autor_client.force_login(self.author)
        self.POST_ID = self.post.pk

    def test_group_slug_url_exists_at_desired_location(self):
        """Страница group_slug доступна любому пользователю."""
        response = self.guest_client.get(f'/group/{GROUP_SLUG}/')
        self.assertEqual(response.status_code, 200)

    def test_profile_url_exists_at_desired_location(self):
        """Страница profile доступна любому пользователю."""
        response = self.guest_client.get(f'/profile/{AUTHOR_USERNAME}/')
        self.assertEqual(response.status_code, 200)

    def test_post_id_url_exists_at_desired_location(self):
        """Страница post_id доступна любому пользователю."""
        response = self.guest_client.get(f'/posts/{self.POST_ID}/')
        self.assertEqual(response.status_code, 200)

    def test_post_id_edit_author_url_exists_at_desired_location(self):
        """Страница post_id_edit доступна автору."""
        response = self.autor_client.get(f'/posts/{self.POST_ID}/edit/')
        self.assertEqual(response.status_code, 200)

    def test_post_id_edit_guest_url_exists_at_desired_location(self):
        """Страница post_id_edit перенаправила не автора поста."""
        response = self.authorized_client.get(f'/posts/{self.POST_ID}/edit/')
        self.assertRedirects(response, f'/profile/{AUTHOR_USERNAME}/')

    def test_post_id_edit_user_url_exists_at_desired_location(self):
        """Страница post_id_edit перенаправила неавторизованного пользователя."""
        response = self.guest_client.get(f'/posts/{self.POST_ID}/edit/')
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.POST_ID}/edit/'
        )

    def test_create_guest_url_exists_at_desired_location(self):
        """Страница create перенаправила неавторизованного пользователя."""
        response = self.guest_client.get('/create/')
        self.assertRedirects(
            response, '/auth/login/?next=/create/'
        )

    def test_create_user_url_exists_at_desired_location(self):
        """Страница create доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_unexisting_url_exists_at_desired_location(self):
        """Несуществующая страница не найдена статус 404."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)

    def test_urls_uses_correct_template(self):
        """Проверка взаимосвязи url с шаблоном"""
        templates_url_name = {
            '/': INDEX_TEMPLATE,
            f'/group/{GROUP_SLUG}/': GROUP_LIST_TEMPLATE,
            f'/profile/{USER_USERNAME}/': PROFILE_TEMPLATE,
            f'/posts/{self.POST_ID}/': POST_DETAL_TEMPLATE,
            f'/posts/{self.POST_ID}/edit/': CREATE_TEMPLATE,
            f'/create/': CREATE_TEMPLATE,
        }
        for address, template in templates_url_name.items():
            with self.subTest(address=address):
                response = self.autor_client.get(address)
                self.assertTemplateUsed(response, template)
