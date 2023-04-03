
from django.contrib.auth import get_user_model
from ..models import Post, Group
from django.test import Client, TestCase
from django.urls import reverse
from .constants import (
    INDEX_URL_NAME,
    GROUP_LIST_URL_NAME,
    PROFILE_URL_NAME,
    POST_DETAIL_URL_NAME,
    POST_EDIT_URL_NAME,
    POST_CREAT_URL_NAME,
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
        # Создаем форму, если нужна проверка атрибутов
        #cls.form = TaskCreateForm()

    def setUp(self):
        # Создаем неавторизованный клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.GROUP_ID = self.group.pk


    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        # Подсчитаем количество записей в Post
        post_count = Post.objects.count()
        print(post_count)

        form_data = {
            'text': POST_TEXT,
            'group': self.GROUP_ID,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, f'/profile/{AUTHOR_USERNAME}/')
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), post_count + 1)
        # Проверяем, что создалась запись с заданным слагом
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
        print(id)
        self.authorized_client.post(reverse('posts:post_edit', args=[id]),
            data=form_data,
            follow=True
        )
        self.assertNotEqual(self.post.text, 'Новый текст')
