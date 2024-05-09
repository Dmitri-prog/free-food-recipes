from django.contrib import admin

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Subscription, Tag)

admin.site.empty_value_display = 'Не задано'


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    list_filter = ('name',)


class RecipeIngredientInline(admin.StackedInline):
    model = RecipeIngredient
    extra = 0


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'text',
        'cooking_time',
        'image',
        'pub_date',
        'count_favorite',
    )
    inlines = [
        RecipeIngredientInline,
    ]

    list_filter = ('author', 'name', 'tags',)
    filter_horizontal = ('tags', 'ingredients',)

    def count_favorite(self, object):
        return object.favorites.count()

    count_favorite.short_description = 'Добавлено в избранное'


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = (
        'ingredient',
        'amount',
        'recipe',
    )


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'color',
        'slug',
    )


class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'subscriber',
    )


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
