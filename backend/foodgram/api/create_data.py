from recipes.models import RecipeIngredient


def bulk_create_recipe_ingredient(ingredients, instance):
    RecipeIngredient.objects.bulk_create([RecipeIngredient(
            ingredient=ingredient['id'],
            recipe=instance,
            amount=ingredient['amount']
        )for ingredient in ingredients])
