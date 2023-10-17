"""Кастомные вьюсеты для приложения api."""

from rest_framework import mixins, viewsets


class CreateDestroyViewSet(mixins.CreateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
    """Вьюсет для создания и удаления."""
    pass
