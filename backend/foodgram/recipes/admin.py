from django.contrib import admin

from . import models


class RecipeIngredientInline(admin.TabularInline):
    model = models.RecipeIngredient
    extra = 1


@admin.register(models.Recipe)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'ingredient', 'amount')
    list_filter = ('recipe', 'ingredient')
    search_fields = ('recipe', 'ingredient')


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    pass
