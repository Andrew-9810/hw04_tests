from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()
SYMBOL_LIMIT: int = 15


class Group(models.Model):
    """Модель Group для сообществ."""
    title = models.CharField('Имя', max_length=200)
    slug = models.SlugField('Адрес', max_length=255, unique=True)
    description = models.TextField('Описание', null=True, blank=True)

    def __str__(self):
        return self.title


class Post(models.Model):
    """Модель Post для хранения постов."""
    text = models.TextField(
        'Текст поста',
        help_text='Введите текст поста'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts_group',
        help_text='Выберите группу'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self):
        return self.text[:SYMBOL_LIMIT]

    class Meta:
        ordering = ['-pub_date', 'id']
