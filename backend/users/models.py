from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Модель пользователя."""
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Email',
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Логин',
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия',
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.username} - {self.email}'


class Subscribe(models.Model):
    """Модель подписки."""
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор')
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата подписки'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_subscription')
        ]

    def __str__(self):
        return (f'{self.user} - {self.author}')
