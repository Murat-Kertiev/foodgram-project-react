from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from recipes.models import (FavoriteRecipe, Ingredient, Recipe, ShoppingCart,
                            Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import (SAFE_METHODS, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from users.models import CustomUser, Subscribe

from .filters import IngredientFilter, RecipesFilter
from .mixins import CreateDestroyViewSet
from .permissions import IsAuthorOrReadOnly
from .serializers import (FavoriteRecipeSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeReadSerializer,
                          SetPasswordSerializer, ShoppingCartSerializer,
                          SubscribeSerializer, TagSerializer,
                          UserCreateSerializer, UserListSerializer)
from .utils import generate_shopping_list


class CustomUserViewSet(UserViewSet):
    """Вьюсет для пользователей."""
    queryset = CustomUser.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        """Сериализатор для отображения информации о пользователе."""
        action_serializer_map = {
            'set_password': SetPasswordSerializer,
            'create': UserCreateSerializer,
        }
        return action_serializer_map.get(self.action, UserListSerializer)

    def get_permissions(self):
        """Права доступа."""
        if self.action == 'me':
            self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        """Подписки."""
        queryset = Subscribe.objects.filter(user=request.user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            pages,
            many=True,
            context={'request': request},
        )
        return self.get_paginated_response(serializer.data)


class SubscribeViewSet(CreateDestroyViewSet):
    """Вьюсет для подписок."""
    serializer_class = SubscribeSerializer

    def get_queryset(self):
        """Получение подписок."""
        return self.request.user.follower.all()

    def get_serializer_context(self):
        """Получение контекста."""
        context = super().get_serializer_context()
        context['author_id'] = self.kwargs.get('user_id')
        context['resipes_limit'] = self.request.query_params.get(
            'recipes_limit',
        )
        return context

    def perform_create(self, serializer):
        """Создание подписки."""
        serializer.save(
            user=self.request.user,
            author=get_object_or_404(
                CustomUser,
                id=self.kwargs.get('user_id')
            )
        )

    @action(methods=('delete',), detail=True)
    def delete(self, request, user_id):
        """Удаление подписки."""
        get_object_or_404(CustomUser, id=user_id)
        if not Subscribe.objects.filter(
                user=request.user, author_id=user_id).exists():
            return Response({'errors': 'Вы не были подписаны на автора'},
                            status=status.HTTP_400_BAD_REQUEST)
        get_object_or_404(
            Subscribe,
            user=request.user,
            author_id=user_id
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
    filterset_class = RecipesFilter

    def get_serializer_class(self):
        """Сериализатор для отображения информации о рецепте."""
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        """Создание рецепта."""
        serializer.save(author=self.request.user)

    def update(self, request, *args, **kwargs):
        """Обновление рецепта."""
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True
        )
        if 'tags' not in request.data:
            return Response(
                {'tags': ['This field is required.']},
                status=status.HTTP_400_BAD_REQUEST
            )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=False,
        methods=('get',),
        url_path='download_shopping_cart',
        pagination_class=None
    )
    def download_file(self, request):
        """Скачивание списка покупок."""
        user = request.user
        if not user.shopping_cart.exists():
            return Response(
                'В корзине нет товаров', status=status.HTTP_400_BAD_REQUEST
            )
        response = HttpResponse(
            generate_shopping_list(user),
            content_type='text/plain'
        )
        filename = 'shopping_list.txt'
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response


class FavoriteRecipeViewSet(CreateDestroyViewSet):
    """Вьюсет для избранных рецептов."""
    serializer_class = FavoriteRecipeSerializer

    def get_queryset(self):
        """Получение избранных рецептов."""
        user = self.request.user.id
        return FavoriteRecipe.objects.filter(user=user)

    def get_serializer_context(self):
        """Получение контекста."""
        context = super().get_serializer_context()
        context['recipe_id'] = self.kwargs.get('recipe_id')
        return context

    def perform_create(self, serializer):
        """Создание избранных рецептов."""
        serializer.save(
            user=self.request.user,
            favorite_recipe=get_object_or_404(
                Recipe,
                id=self.kwargs.get('recipe_id')
            )
        )

    @action(methods=('delete',), detail=True)
    def delete(self, request, recipe_id):
        """Удаление избранных рецептов."""
        user = request.user
        if not user.favorite.select_related(
                'favorite_recipe').filter(
                    favorite_recipe_id=recipe_id).exists():
            return Response({'errors': 'Рецепт не в избранном'},
                            status=status.HTTP_400_BAD_REQUEST)

        get_object_or_404(
            FavoriteRecipe,
            user=user,
            favorite_recipe_id=recipe_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(CreateDestroyViewSet):
    """Вьюсет для корзины покупок."""
    serializer_class = ShoppingCartSerializer

    def get_queryset(self):
        """Получение корзины покупок."""
        user = self.request.user.id
        return ShoppingCart.objects.filter(user=user)

    def get_serializer_context(self):
        """Получение контекста."""
        context = super().get_serializer_context()
        context['recipe_id'] = self.kwargs.get('recipe_id')
        return context

    def perform_create(self, serializer):
        """Создание корзины покупок."""
        recipe_id = self.kwargs.get('recipe_id')
        user = self.request.user

        try:
            recipe = Recipe.objects.get(id=recipe_id)
        except Recipe.DoesNotExist:
            raise ValidationError({'errors': 'Рецепт не существует'}, code=400)

        serializer.save(user=user, recipe=recipe)

    @action(methods=('delete',), detail=True)
    def delete(self, request, recipe_id):
        """Удаление из корзины покупок."""
        cart_item = ShoppingCart.objects.filter(
            user=request.user, recipe_id=recipe_id
        ).first()

        if not cart_item:
            return Response(
                {'errors': 'Рецепта нет в корзине'},
                status=status.HTTP_404_NOT_FOUND
            )
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
