
from django.urls import include, path
from rest_framework import routers

from api.views import (FavoriteViewSet, IngredientViewSet, RecipeViewSet,
                       ShoppingCartViewSet, TagViewSet)

router = routers.DefaultRouter()
router.register('tags', TagViewSet)
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register('ingredients', IngredientViewSet)

urlpatterns = [
    path('', include('users.urls')),
    path('recipes/download_shopping_cart/',
         ShoppingCartViewSet.as_view({'get': 'download'}), name='download'),
    path('', include(router.urls)),
    path('recipes/<recipes_id>/favorite/',
         FavoriteViewSet.as_view({'post': 'create',
                                  'delete': 'delete'}), name='favorite'),
    path('recipes/<recipes_id>/shopping_cart/',
         ShoppingCartViewSet.as_view({'post': 'create',
                                      'delete': 'delete'}), name='cart'),
]
