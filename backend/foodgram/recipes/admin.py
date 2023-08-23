from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe,
                     RecipeIngredient, ShoppingCart,
                     Tag)


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    search_fields = ('name', 'color', 'slug')
    list_filter = ('name', 'color', 'slug',)
    ordering = ('name',)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('name',)
    ordering = ('id',)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'count_favorites')
    search_fields = ('username', 'email', 'first_name', 'last_name',)
    list_filter = ('author', 'name', 'tags',)
    ordering = ('name',)

    def count_favorites(self, obj):
        return obj.favorites.count()


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount')
    search_fields = ('recipe', 'ingredient',)
    list_filter = ('recipe', 'ingredient',)


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user', 'recipe',)
    list_filter = ('user', 'recipe',)


class ShoppingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user', 'recipe',)
    list_filter = ('user', 'recipe',)


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingAdmin)
