"""Конфигурация приложения api."""

from django.apps import AppConfig


class ApiConfig(AppConfig):
    """Класс конфигурации приложения api."""
    name = 'api'
    default_auto_field = 'django.db.models.BigAutoField'
