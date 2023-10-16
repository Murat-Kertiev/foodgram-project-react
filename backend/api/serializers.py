from django.contrib.auth.hashers import check_password
from djoser.serializers import (PasswordSerializer, UserCreateSerializer,
                                UserSerializer)
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status

from recipes.models import (FavoriteRecipe, Ingredient, IngredientAmount,
                            Recipe, ShoppingCart, Tag)
from users.models import CustomUser, Subscribe


class UserListSerializer(UserSerializer):
    """Сериализатор для отображения информации о пользователе."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        """Получение подписок."""
        request = self.context.get('request')

        if request.user.is_authenticated:
            return Subscribe.objects.filter(
                user=request.user, author=obj
            ).exists()
        return False


class UserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания нового пользователя."""
    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )
        required_fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения тегов."""
    class Meta:
        model = Tag
        fields = '__all__'


class IngrediendAmountSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения количества ингредиентов."""
    id = serializers.ReadOnlyField(
        source='ingredient.id',
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name',
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиента."""
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientsCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания ингредиентов."""
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецептов."""
    ingredients = IngrediendAmountSerializer(
        many=True,
        source='recipe',
        required=True,
    )
    tags = TagSerializer(
        many=True,
        read_only=True
    )
    author = UserListSerializer(
        read_only=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        """Получение избранных рецептов."""
        request = self.context.get('request')

        if request.user.is_authenticated:
            return FavoriteRecipe.objects.filter(user=request.user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        """Получение рецептов в списке покупок."""
        request = self.context.get('request')

        if request.user.is_authenticated:
            return ShoppingCart.objects.filter(user=request.user).exists()
        return False


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""
    image = Base64ImageField(
        max_length=None,
        use_url=True)
    ingredients = IngredientsCreateSerializer(
        many=True)
    author = serializers.PrimaryKeyRelatedField(
        read_only=True)

    class Meta:
        model = Recipe
        fields = '__all__'
        extra_kwargs = {'tags': {"error_messages": {
            "does_not_exist": "Ошибка в Тэге, id = {pk_value} не существует"
            }}}

    def validate(self, data):
        ingredients = data.get('ingredients')
        tags = data.get('tags')
        cooking_time = data.get('cooking_time')
        image = data.get('image')

        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'Загрузите ингредиенты'}
            )

        ingredient_ids = [item['id'] for item in ingredients]
        if not Ingredient.objects.filter(id__in=ingredient_ids).exists():
            invalid_ingredients = (
                set(ingredient_ids) - set(Ingredient.objects.values_list(
                    'id', flat=True
                ))
            )
            raise serializers.ValidationError(
                {
                    'ingredients': [
                        f'Ингредиента с id - {ingredient_id} нет'
                        for ingredient_id in invalid_ingredients
                    ]
                }
            )

        if len(ingredients) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться!'
            )

        if len(tags) != len(set(tags)):
            raise serializers.ValidationError({
                'tags': 'Тэги не должны повторяться!'
            })

        if any(item['amount'] < 1 for item in ingredients):
            raise serializers.ValidationError(
                {'amount': 'Минимальное количество ингредиента 1'}
            )

        if cooking_time is None:
            raise serializers.ValidationError(
                {'cooking_time':
                 'Поле cooking_time обязательно для заполнения'}
            )
        if not 1 <= cooking_time:
            raise serializers.ValidationError(
                {'cooking_time':
                 'Время приготовления блюда должно быть не меньше 1 минуты'}
            )

        if image is None:
            raise serializers.ValidationError(
                {'image': 'Загрузите изображение'}
            )

        if not tags:
            raise serializers.ValidationError(
                {'tags': 'Поле tags обязательно для заполнения'}
            )
        return data

    def create_ingredients(self, ingredients, recipe):
        """Создание ингредиентов."""
        for ingredient in ingredients:
            IngredientAmount.objects.bulk_create([
                IngredientAmount(
                    recipe=recipe,
                    ingredient_id=ingredient.get('id'),
                    amount=ingredient.get('amount'),
                )
            ])

    def create(self, validated_data):
        """Создание рецепта."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        """Обновление рецепта."""
        if 'tags' not in validated_data:
            raise serializers.ValidationError(
                'Поле "tags" обязательно',
                code=status.HTTP_400_BAD_REQUEST
            )

        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            instance.ingredients.clear()
            self.create_ingredients(ingredients, instance)

        instance.tags.set(validated_data.pop('tags'))
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Отображение рецепта."""
        data = RecipeReadSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }).data
        if data.get('image') is None:
            data['image'] = ''
        return data


class SetPasswordSerializer(PasswordSerializer):
    current_password = serializers.CharField(
        required=True,
        label='Текущий пароль'
    )

    def validate(self, data):
        user = self.context.get('request').user
        if data['new_password'] == data['current_password']:
            raise serializers.ValidationError({
                "new_password": "Пароли не должны совпадать"})
        check_current = check_password(
            data['current_password'], user.password
        )
        if check_current is False:
            raise serializers.ValidationError({
                "current_password": "Введен неверный пароль"})
        return data


class SubscribeRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов пользователя."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор подписки."""
    email = serializers.CharField(
        source='author.email',
        read_only=True)
    id = serializers.IntegerField(
        source='author.id',
        read_only=True)
    username = serializers.CharField(
        source='author.username',
        read_only=True)
    first_name = serializers.CharField(
        source='author.first_name',
        read_only=True)
    last_name = serializers.CharField(
        source='author.last_name',
        read_only=True)
    recipes = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(
        source='author.recipe.count')

    class Meta:
        model = Subscribe
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count',)

    def validate(self, data):
        """Проверка валидности."""
        user = self.context.get('request').user
        author = self.context.get('author_id')
        if user.id == int(author):
            raise serializers.ValidationError({
                'errors': 'Нельзя подписаться на самого себя'})
        if Subscribe.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError({
                'errors': 'Вы уже подписаны на данного пользователя'})
        return data

    def get_recipes(self, obj):
        """Получение рецептов пользователя."""
        recipes = obj.author.recipe.all()
        recipes_limit = self.context.get('recipes_limit')
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return SubscribeRecipeSerializer(recipes, many=True).data

    def get_is_subscribed(self, obj):
        """Проверка подписки."""
        return Subscribe.objects.filter(
            user=self.context.get('request').user, author=obj.author
        ).exists()


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для избранных рецептов."""
    id = serializers.ReadOnlyField(
        source='favorite_recipe.id',
    )
    name = serializers.ReadOnlyField(
        source='favorite_recipe.name',
    )
    image = serializers.CharField(
        source='favorite_recipe.image',
        read_only=True,
    )
    cooking_time = serializers.ReadOnlyField(
        source='favorite_recipe.cooking_time',
    )

    class Meta:
        model = FavoriteRecipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        """Проверка валидности."""
        user = self.context.get('request').user
        recipe = self.context.get('recipe_id')
        if FavoriteRecipe.objects.filter(user=user,
                                         favorite_recipe=recipe).exists():
            raise serializers.ValidationError({
                'errors': 'Рецепт уже в избранном'})
        return data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов в списке покупок."""
    id = serializers.ReadOnlyField(
        source='recipe.id',
    )
    name = serializers.ReadOnlyField(
        source='recipe.name',
    )
    image = serializers.CharField(
        source='recipe.image',
        read_only=True,
    )
    cooking_time = serializers.ReadOnlyField(
        source='recipe.cooking_time',
    )

    class Meta:
        model = ShoppingCart
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        """Проверка валидности."""
        user = self.context.get('request').user
        recipe = self.context.get('recipe_id')
        if ShoppingCart.objects.filter(user=user,
                                       recipe=recipe).exists():
            raise serializers.ValidationError({
                'errors': 'Рецепт уже добавлен в список покупок'})
        return data
