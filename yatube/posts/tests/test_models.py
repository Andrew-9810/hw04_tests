from django.contrib.auth import get_user_model
from django.test import TestCase
from ..models import Group, Post
from .constants import (
    AUTHOR_USERNAME,
    GROUP_TITLE,
    GROUP_SLUG,
    GROUP_DESCRIPTION,
    POST_TEXT,
)
from ..models import SYMBOL_LIMIT


User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=AUTHOR_USERNAME)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=POST_TEXT,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        # Не совсем уверен что сделал то что нужно.
        post = self.post
        group = self.group
        expected_object_name = {
            str(post): post.text[:SYMBOL_LIMIT],
            str(group): group.title,
        }
        for field, expected_object in expected_object_name.items():
            with self.subTest(field=field):
                self.assertEqual(field, expected_object)
