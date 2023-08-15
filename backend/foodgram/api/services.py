import io

from django.db.models import F, Sum
from recipes.models import RecipeIngredient
from users.models import User


def get_shopping_list(user: User) -> io.BytesIO:
    ingredients = RecipeIngredient.objects.filter(
        recipe__shopping_cart__user=user).values(
            name=F('ingredient__name'),
            measurement_unit=F('ingredient__measurement_unit')
            ).annotate(
            amount=Sum('amount')
    )
    data = []
    for ingredient in ingredients:
        data.append(
            f'{ingredient["name"]} - '
            f'{ingredient["amount"]} '
            f'{ingredient["measurement_unit"]}'
        )
    content = 'Список покупок:\n\n' + '\n'.join(data)
    return content
