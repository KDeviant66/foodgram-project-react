from django.db import transaction
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer as DjoserCreateSerialiser
from djoser.serializers import UserSerializer as DjoserUserSerialiser
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Favorite, Ingredient, ShoppingCart, Recipe,
                            RecipeIngredient, Tag)
from users.models import Follow, User


class UserSerializer(DjoserCreateSerialiser):

    class Meta(DjoserCreateSerialiser.Meta):
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'role'
        )


class UserShowSerializer(DjoserUserSerialiser):
    is_subscribed = serializers.SerializerMethodField()

    def is_subscribed(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and obj.subscribing.filter(user=user).exists()
        )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):

    tags = TagSerializer(many=True, read_only=True)
    author = UserShowSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients', many=True, read_only=True
    )
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)
    name = serializers.CharField(
        required=True, max_length=200
    )
    image = Base64ImageField()
    text = serializers.CharField(required=True)
    cooking_time = serializers.IntegerField(
        required=True
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def bulk_create_recipe(self, ingredients, recipe):
        recipe_ingredients = []
        for ingredient in ingredients:
            recipe_ingredient = RecipeIngredient(
                recipe=recipe,
                ingredient_id=ingredient['id'],
                amount=int(ingredient['amount'])
            )
            recipe_ingredients.append(recipe_ingredient)
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    @transaction.atomic
    def create(self, validated_data):

        image = validated_data.pop('image')
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(image=image, **validated_data)
        recipe.tags.set(tags)
        self.bulk_create_recipe(ingredients, recipe)
        recipe.save()
        return recipe

    @transaction.atomic
    def update(self, recipe, validated_data):

        recipe.ingredients.clear()
        self.bulk_create_recipe(validated_data.pop('ingredients'), recipe)
        tags = validated_data.pop('tags')
        recipe.tags.set(tags)
        return super().update(recipe, validated_data)

    def validate(self, data):

        ingredients = self.initial_data.get('ingredients')
        ingredients_list = [ingredient['id'] for ingredient in ingredients]
        if len(ingredients_list) != len(set(ingredients_list)):
            raise serializers.ValidationError(
                'Ингредиенты нее должны повторяться'
            )
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'Нужен хотя бы 1 ингредиент'}
            )
        for ingredient in ingredients:
            if int(ingredient.get('amount')) < 1:
                raise serializers.ValidationError(
                    'Количество ингредиента >= 1!')
        tags = self.initial_data.get('tags')
        if not tags:
            raise serializers.ValidationError(
                {'tags': 'Нужен хотя бы один 1 тэг'}
            )
        tags_list = []
        for tag_item in tags:
            tag = get_object_or_404(Tag, id=tag_item)
            if tag in tags_list:
                raise serializers.ValidationError(
                    {'tags': 'Теги не должны повторяться'}
                )
            tags_list.append(tag)
        cooking_time = self.initial_data.get('cooking_time')
        if int(cooking_time) < 1:
            raise serializers.ValidationError(
                'Время приготовления >= 1!')
        
        data['cooking_time'] = cooking_time
        data['author'] = self.context.get('request').user
        data['ingredients'] = ingredients
        data['tags'] = tags
        return data


class FavoriteSerializer(serializers.ModelSerializer):
    cooking_time = serializers.IntegerField()
    image = Base64ImageField(max_length=None, use_url=False,)

    class Meta:
        model = Favorite
        fields = ('image', 'cooking_time')
        validators = (
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe')
            )
        )


class ShoppingCartSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    cooking_time = serializers.IntegerField()
    image = Base64ImageField(max_length=None, use_url=False,)

    class Meta:
        model = ShoppingCart
        fields = ('name', 'image', 'cooking_time')
        validators = (
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe')
            )
        )


class SubscribeSerializer(serializers.Serializer):
    email = serializers.ReadOnlyField(source='following.email')
    id = serializers.ReadOnlyField(source='following.id')
    username = serializers.ReadOnlyField(source='following.username')
    first_name = serializers.ReadOnlyField(source='following.first_name')
    last_name = serializers.ReadOnlyField(source='following.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    def get_is_subscribed(self, username):
        return True

    def get_recipes(self, data):
        limit = self.context.get('request').query_params.get('recipes_limit')
        if not limit:
            limit = 3
        recipes = data.following.recipes.all()[:int(limit)]
        return RecipeSerializer(recipes, many=True).data


class SubscribeAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ('user', 'following')

    def validate(self, data):
        user = data['user']
        following = data['following']

        if user == following:
            raise serializers.ValidationError("Нельзя подписаться на себя")

        if Follow.objects.filter(user=user, following=following).exists():
            raise serializers.ValidationError("Ты уже подписан на этого юзера")

        return data
