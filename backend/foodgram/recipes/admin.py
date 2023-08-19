from django.contrib import admin

from . import models


class RecipeIngredientInline(admin.TabularInline):
    model = models.RecipeIngredient
    extra = 1


@admin.register(models.Recipe)
class TagAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline, )


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    list_filter = ('name', 'color')
    search_fields = ('name', 'color')
