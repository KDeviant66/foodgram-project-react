from django.db.models.expressions import Exists, OuterRef, Value
from django.http import FileResponse
from django.shortcuts import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
#from rest_framework import filters
from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet


from .base_class import CreateDeleteRecipeViewSet
from .filters import RecipeFilter, IngredientFilter
from .paginations import PagePagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeSerializer, ShoppingCartSerializer,
                          TagSerializer)
from .services import get_shopping_list
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (IsAdminOrReadOnly,)
    #filter_backends = [filters.SearchFilter]
    #search_fields = ['name']
    filterset_class = IngredientFilter


class RecipeViewSet(ModelViewSet):
    pagination_class = PagePagination
    permission_classes = (IsAuthorOrReadOnly,)
    filterset_class = RecipeFilter
    filter_backends = (DjangoFilterBackend,)
    serializer_class = RecipeSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Recipe.objects.annotate(
                is_in_shopping_cart=Value(False),
                is_favorited=Value(False),
            ).select_related(
                'author'
            ).prefetch_related(
                'tags',
            )

        return Recipe.objects.annotate(
            is_favorited=Exists(Favorite.objects.filter(
                user=self.request.user, recipe=OuterRef('id'))
            ),
            is_in_shopping_cart=Exists(ShoppingCart.objects.filter(
                user=self.request.user, recipe=OuterRef('id'))
            )
        ).select_related(
            'author'
        ).prefetch_related(
            'tags',
        )


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
