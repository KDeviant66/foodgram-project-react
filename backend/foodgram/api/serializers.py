from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag, TagRecipe)
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from users.models import User


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientGetSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientPostSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class UserDetailSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(
        method_name='is_subscribed'
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def is_subscribed(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and obj.subscribing.filter(user=user).exists()
        )


class RecipeGetSerializer(serializers.ModelSerializer):
    author = UserDetailSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    ingredients = RecipeIngredientGetSerializer(
        read_only=True,
        many=True,
        source='recipe_ingredients'
    )
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user, recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj
        ).exists()


class RecipePostSerializer(serializers.ModelSerializer):
    author = UserDetailSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True)
    ingredients = RecipeIngredientPostSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'author', 'name', 'text',
                  'cooking_time')
        lookup_field = 'author'

    @transaction.atomic
    def create(self, validated_data):
        tags_set = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        TagRecipe.objects.bulk_create([TagRecipe(
            recipe=recipe,
            tag=tag
        ) for tag in tags_set])


        RecipeIngredient.objects.bulk_create([RecipeIngredient(
             ingredient=ingredient['id'],
             recipe=recipe,
             amount=ingredient['amount']
         ) for ingredient in ingredients ])
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.tags.clear()
        tags_data = self.initial_data.get('tags')
        instance.tags.set(tags_data)
        RecipeIngredient.objects.filter(recipe=instance).all().delete()
        instance.ingredients.all().delete()

        ingredients = validated_data.get('ingredients')
        RecipeIngredient.objects.bulk_create([RecipeIngredient(
             ingredient=ingredient['id'],
             recipe=instance,
             amount=ingredient['amount']
         ) for ingredient in ingredients ])
        instance.save()
        return instance

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        ingredient_list = []
        for ingredient_item in ingredients:
            ingredient = get_object_or_404(Ingredient,
                                           id=ingredient_item['id'])
            if ingredient in ingredient_list:
                raise serializers.ValidationError('Ингредиент должен '
                                                  'быть уникальным')
            ingredient_list.append(ingredient)
            if int(ingredient_item['amount']) < 1:
                raise serializers.ValidationError({
                    'ingredients': ('Число ингредиентов должно быть больше 1')
                })
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
