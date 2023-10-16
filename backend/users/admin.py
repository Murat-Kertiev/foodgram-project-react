from django.contrib import admin

from .models import CustomUser, Subscribe


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    """Отображение пользователей в админке."""
    list_display = (
        'id', 'email', 'username', 'first_name', 'last_name'
    )
    search_fields = ('username', 'first_name', 'last_name')
    list_filter = ('first_name', 'email')
    empty_value_display = '-пусто-'


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    """Отображение подписок в админке."""
    list_display = (
        'id', 'user', 'author',  'created'
    )
    search_fields = ('author', 'created')
    list_filter = ('user', 'author', 'created')
    empy_value_display = '-пусто-'
