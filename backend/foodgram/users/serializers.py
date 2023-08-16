from api.serializers import RecipeGetSerializer
from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework import serializers

from users.models import Follow, User

class UserSerializer(UserCreateSerializer):

    class Meta(UserCreateSerializer.Meta):
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


class UserShowSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    def get_is_subscribed(self, username):
        user = self.context['request'].user
        return (not user.is_anonymous
                and Follow.objects.filter(
                    user=user,
                    following=username
                ).exists())

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
        return RecipeGetSerializer(recipes, many=True).data
