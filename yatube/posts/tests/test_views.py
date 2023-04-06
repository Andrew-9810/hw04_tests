import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms
from django.conf import settings
from ..models import Post, Group
from django.core.files.uploadedfile import SimpleUploadedFile
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
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostURLTests(TestCase):
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
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        cls.author = User.objects.create_user(username=AUTHOR_USERNAME)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION
        )
        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.author,
            group=cls.group,
            image=cls.uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username=USER_USERNAME)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.autor_client = Client()
        self.autor_client.force_login(self.author)
        self.POST_ID = self.post.pk

    def test_pages_post_edit_uses_correct_template(self):
        """URL-адрес post_edit использует соответствующий шаблон."""
        response = self.autor_client.get(
            reverse(
                f'{POST_EDIT_URL_NAME}',
                kwargs={'post_id': f'{self.POST_ID}'}
            )
        )
        self.assertTemplateUsed(response, f'{CREATE_TEMPLATE}')

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            f'{INDEX_TEMPLATE}': reverse(f'{INDEX_URL_NAME}'),
            f'{GROUP_LIST_TEMPLATE}': (
                reverse(
                    f'{GROUP_LIST_URL_NAME}',
                    kwargs={'slug': f'{GROUP_SLUG}'}
                )
            ),
            f'{PROFILE_TEMPLATE}': (
                reverse(
                    f'{PROFILE_URL_NAME}',
                    kwargs={'username': f'{AUTHOR_USERNAME}'}
                )
            ),
            f'{POST_DETAL_TEMPLATE}': (
                reverse(
                    f'{POST_DETAIL_URL_NAME}',
                    kwargs={'post_id': f'{self.POST_ID}'}
                )
            ),
            f'{CREATE_TEMPLATE}': reverse(f'{POST_CREAT_URL_NAME}')
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(INDEX_URL_NAME))
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author.username
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        post_image_0 = first_object.image
        self.assertEqual(post_author_0, AUTHOR_USERNAME)
        self.assertEqual(post_text_0, POST_TEXT)
        self.assertEqual(post_group_0, GROUP_TITLE)
        self.assertEqual(post_image_0, self.post.image)

    def test_group_list_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(f'{GROUP_LIST_URL_NAME}', kwargs={'slug': f'{GROUP_SLUG}'})
        )
        first_object = response.context['page_obj'][0]
        post_group_0 = first_object.group.title
        post_image_0 = first_object.image
        self.assertEqual(post_group_0, GROUP_TITLE)
        self.assertEqual(post_image_0, self.post.image)

    def test_profile_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                f'{PROFILE_URL_NAME}',
                kwargs={'username': f'{AUTHOR_USERNAME}'}
            )
        )
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author.username
        post_image_0 = first_object.image
        self.assertEqual(post_author_0, AUTHOR_USERNAME)
        self.assertEqual(post_image_0, self.post.image)

    def test_post_detal_correct_context(self):
        """Шаблон post_detal сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                f'{POST_DETAIL_URL_NAME}',
                kwargs={'post_id': self.POST_ID}
            )
        )
        first_object = response.context['post']
        post_author_0 = first_object.author.username
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        post_image_0 = first_object.image
        self.assertEqual(post_author_0, AUTHOR_USERNAME)
        self.assertEqual(post_text_0, POST_TEXT)
        self.assertEqual(post_group_0, GROUP_TITLE)
        self.assertEqual(post_image_0, self.post.image)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.autor_client.get(
            reverse(
                f'{POST_EDIT_URL_NAME}',
                kwargs={'post_id': f'{self.POST_ID}'}
            )
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_create_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(POST_CREAT_URL_NAME)
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username=AUTHOR_USERNAME)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION
        )
        cls.SHOW_QUANTITY_SECOND_PAGE: int = 3

        cls.post = Post.objects.bulk_create(
            [
                Post(
                    text=f'{POST_TEXT} {i}', author=cls.author, group=cls.group
                ) for i in range(
                    settings.SHOW_QUANTITY
                    + cls.SHOW_QUANTITY_SECOND_PAGE
                )
            ]
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username=USER_USERNAME)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.autor_client = Client()
        self.autor_client.force_login(self.author)

    def test_index_first_page_contains_ten_records(self):
        """Первая страница index, paginator вывод количества записей"""
        response = self.client.get(reverse(INDEX_URL_NAME))
        self.assertEqual(
            len(response.context['page_obj']), settings.SHOW_QUANTITY
        )

    def test_index_second_page_contains_three_records(self):
        """Вторая страница index, paginator вывод количества записей"""
        response = self.client.get(reverse(INDEX_URL_NAME) + '?page=2')
        self.assertEqual(
            len(response.context['page_obj']), self.SHOW_QUANTITY_SECOND_PAGE
        )

    def test_group_list_first_page_contains_ten_records(self):
        """Первая страница group_list, paginator вывод количества записей"""
        response = self.client.get(
            reverse(f'{GROUP_LIST_URL_NAME}', kwargs={'slug': f'{GROUP_SLUG}'})
        )
        self.assertEqual(
            len(response.context['page_obj']), settings.SHOW_QUANTITY
        )

    def test_group_list_second_page_contains_three_records(self):
        """Вторая страница group_list, paginator вывод количества записей"""
        response = self.client.get(
            reverse(
                f'{GROUP_LIST_URL_NAME}',
                kwargs={'slug': f'{GROUP_SLUG}'}
            ) + '?page=2',
        )
        self.assertEqual(
            len(response.context['page_obj']), self.SHOW_QUANTITY_SECOND_PAGE,
        )

    def test_profile_first_page_contains_ten_records(self):
        """Первая страница profile, paginator вывод количества записей"""
        response = self.client.get(
            reverse(
                f'{PROFILE_URL_NAME}',
                kwargs={'username': f'{AUTHOR_USERNAME}'}
            )
        )
        self.assertEqual(
            len(response.context['page_obj']), settings.SHOW_QUANTITY
        )

    def test_profile_second_page_contains_three_records(self):
        """Вторая страница profile, paginator вывод количества записей"""
        response = self.client.get(
            reverse(
                f'{PROFILE_URL_NAME}',
                kwargs={'username': f'{AUTHOR_USERNAME}'}
            ) + '?page=2'
        )
        self.assertEqual(
            len(response.context['page_obj']), self.SHOW_QUANTITY_SECOND_PAGE
        )
