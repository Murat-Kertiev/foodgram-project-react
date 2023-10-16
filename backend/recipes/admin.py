from django.contrib import admin
from django.db.models import Count

from .models import (FavoriteRecipe, Ingredient, IngredientAmount, Recipe,
                     ShoppingCart, Tag)


class IngredientAmountAdmin(admin.TabularInline):
    """Отображение количества ингредиентов в админке."""
    model = IngredientAmount
    autocomplete_fields = ('ingredient',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Отображение тегов в админке."""
    list_display = (
        'id', 'name', 'color', 'slug'
    )
    search_fields = ('name', 'slug')
    list_filter = ('name', 'slug')
    empy_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Отображение ингредиентов в админке."""
    list_display = (
        'id', 'name', 'measurement_unit'
    )
    search_fields = ('name',)
    list_filter = ('name',)
    empy_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Отображение рецептов в админке."""
    inlines = (IngredientAmountAdmin,)
    list_display = (
        'id', 'name', 'author', 'text', 'favorite_count', 'pub_date'
    )
    search_fields = ('name', 'author', 'tags')
    list_filter = ('name', 'author', 'tags', 'pub_date')
    filter_vertical = ('tags',)
    empy_value_display = '-пусто-'

    def favorite_count(self, obj):
        """Количество избранных рецептов."""
        return obj.obj_count

    def get_queryset(self, request):
        """Метод получения queryset."""
        queryset = super().get_queryset(request)
        return queryset.annotate(
            obj_count=Count("favorite_recipe", distinct=True),
        )


@admin.register(FavoriteRecipe)
class FavoriteAdmin(admin.ModelAdmin):
    """Отображение избранных рецептов в админке."""
    list_display = (
        'id', 'user', 'favorite_recipe'
    )
    search_fields = ('favorite_recipe',)
    list_filter = ('id', 'user', 'favorite_recipe')
    empy_value_display = '-пусто-'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Отображение корзины покупок в админке."""
    list_display = (
        'id', 'user', 'recipe'
    )
    search_fields = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    empy_value_display = '-пусто-'
