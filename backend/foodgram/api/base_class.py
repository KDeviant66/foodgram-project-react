from http import HTTPStatus

from django.shortcuts import get_object_or_404
from recipes.models import Recipe
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet


class BaseViewSet(ModelViewSet):
    model = None
    serializer_class = None

    def create(self, request, *args, **kvargs):
        recipe_id = int(self.kwargs['recipes_id'])
        recipe = get_object_or_404(Recipe, id=recipe_id)
        instance = self.model.objects.create(user=request.user)
        instance.recipe.set([recipe])
        serializer = self.serializer_class()
        return Response(serializer.to_representation(instance=recipe),
                        status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        recipe_id = self.kwargs['recipes_id']
        user_id = request.user.id
        object = get_object_or_404(
            self.model, user__id=user_id, recipe__id=recipe_id)
        object.delete()
        return Response(HTTPStatus.NO_CONTENT)
