from django.urls import include, path
from rest_framework import routers

from .views import (CustomUserViewSet, FavoriteRecipeViewSet,
                    IngredientViewSet, RecipeViewSet, ShoppingCartViewSet,
                    SubscribeViewSet, TagViewSet)

app_name = 'api'

router_v1 = routers.DefaultRouter()
router_v1.register('users', CustomUserViewSet, basename='users')
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register(
    r'users/(?P<user_id>\d+)/subscribe',
    SubscribeViewSet,
    basename='subscribe'
)
router_v1.register(
    r'recipes/(?P<recipe_id>\d+)/favorite',
    FavoriteRecipeViewSet,
    basename='favorite'
)
router_v1.register(
    r'recipes/(?P<recipe_id>\d+)/shopping_cart',
    ShoppingCartViewSet,
    basename='shoppingcart'
)

urlpatterns = [
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
