from django.db.models import Sum


def generate_shopping_list(user):
    """Создание списка покупок."""
    text = 'Список покупок:\n\n'
    ingredient_name = 'recipe__recipe__ingredient__name'
    ingredient_unit = 'recipe__recipe__ingredient__measurement_unit'
    recipe_amount = 'recipe__recipe__amount'
    amount_sum = 'recipe__recipe__amount__sum'
    cart = user.shopping_cart.select_related('recipe').values(
        ingredient_name, ingredient_unit).annotate(Sum(
            recipe_amount)).order_by(ingredient_name)
    text += '\n'.join(
        f'{item[ingredient_name]} ({item[ingredient_unit]})'
        f' — {item[amount_sum]}\n'
        for item in cart
    )
    return text
