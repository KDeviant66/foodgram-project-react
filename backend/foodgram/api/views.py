from django.http import FileResponse
from django.shortcuts import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from foodgram.pagination import PagePagination
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.base_class import CreateDeleteRecipeViewSet
from api.filters import RecipeFilter
from api.permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from api.serializers import (FavoriteSerializer, IngredientSerializer,
                             RecipeSerializer,
                             ShoppingCartSerializer, TagSerializer)
from api.services import get_shopping_list


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (IsAdminOrReadOnly,)

    def get_queryset(self):
        name = self.request.GET.get('name')
        if name:
            return self.queryset.filter(name__istartswith=name)
        return self.queryset


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = PagePagination
    permission_classes = (IsAuthorOrReadOnly,)
    filterset_class = RecipeFilter
    filter_backends = (DjangoFilterBackend,)
    serializer_class = RecipeSerializer


class FavoriteViewSet(CreateDeleteRecipeViewSet):
    model = Favorite
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = FavoriteSerializer


class ShoppingCartViewSet(CreateDeleteRecipeViewSet):
    model = ShoppingCart
    pagination_class = PagePagination
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ShoppingCartSerializer

    def download(self, request):
        response = HttpResponse(get_shopping_list(request.user),
                                content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="sh_cart.txt"'
        return FileResponse(response, as_attachment=True)
