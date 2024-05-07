import base64

from django.core.files.base import ContentFile

from rest_framework import serializers

from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (
    Ingredient, Tag, Recipe, RecipeIngredient,
    Favorite, ShoppingCart, Subscription  
)

from django.contrib.auth import get_user_model

from djoser.serializers import UserCreateSerializer, UserSerializer
from django.core.exceptions import BadRequest

User = get_user_model()


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class IngredientRecipeAllSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(
        source='ingredient.id'
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = (
            'id',
            'user',
            'recipe'
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Данный рецепт уже в избранном.'
            )
        ]


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = (
            'id',
            'recipe',
            'user'
        )
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Данный рецепт уже в списке покупок.'
            )
        ]


class SubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = (
            'id',
            'subscriber',
            'author'
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('author', 'subscriber'),
                message='Данный автор уже у Вас в подписке.'
            )
        ]

    def validate(self, data):
        if data['author'] == data['subscriber']:
            raise serializers.ValidationError(
                'Невозможно подписаться на самого себя!'
            )
        return data


class RecipeInSubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class UserDjoserSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )

    def validate(self, data):
        if User.objects.filter(username=data.get('username')):
            raise serializers.ValidationError(
                'Данный username занят, придумайте другой username!'
            )
        if User.objects.filter(email=data.get('email')):
            raise serializers.ValidationError(
                'Данный email уже используется, укажите другой email!'
            )
        return data


class MyUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

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

    def get_is_subscribed(self, object):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return object.author.filter(subscriber=request.user).exists()


class UserSubscriptionSerializer(MyUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, object):
        author_recipes = object.recipes.all()
        return RecipeInSubscriptionSerializer(
            author_recipes, many=True
        ).data

    def get_recipes_count(self, object):
        return object.recipes.count()


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = MyUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    @staticmethod
    def get_ingredients(object):
        ingredients = RecipeIngredient.objects.filter(recipe=object)
        return IngredientRecipeAllSerializer(ingredients, many=True).data

    def get_is_favorited(self, object):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return request.user.favorites.filter(recipe=object).exists()

    def get_is_in_shopping_cart(self, object):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return request.user.shopping_cart.filter(recipe=object).exists()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeFullSerializer(serializers.ModelSerializer):
    ingredients = IngredientRecipeSerializer(many=True, required=True)
    image = Base64ImageField(use_url=True, max_length=None)
    author = MyUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
            'author'
        )

    def validate(self, data):
        try:
            tags_data = data['tags']
        except Exception:
            raise BadRequest()
        if len(tags_data) != len(set(tags_data)):
            raise serializers.ValidationError(
                'Вы уже добавили этот тэг!'
            )
        return data

    def validate_ingredients(self, ingredients):
        ingredients_data = [
            ingredient.get('id') for ingredient in ingredients
        ]
        if len(ingredients_data) == 0:
            raise serializers.ValidationError(
                'В рецепте должен быть хотя бы один ингредиент!'
            )
        if len(ingredients_data) != len(set(ingredients_data)):
            raise serializers.ValidationError(
                'Ингредиент необходимо добавлять в рецепт только один раз!'
            )
        for ingredient in ingredients:
            if int(ingredient.get('amount')) < 1:
                raise serializers.ValidationError(
                    'Каждого ингредиента в рецепте должно быть >= 1!'
                )
        return ingredients

    @staticmethod
    def add_ingredients(ingredients_data, recipe):
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                ingredient=ingredient.get('id'),
                recipe=recipe,
                amount=ingredient.get('amount')
            )
            for ingredient in ingredients_data
        ])

    def create(self, validated_data):
        author = self.context.get('request').user
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags_data)
        self.add_ingredients(ingredients_data, recipe)
        return recipe

    def update(self, instance, validated_data):
        recipe = instance
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.name)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.tags.clear()
        instance.ingredients.clear()
        tags_data = validated_data.get('tags')
        instance.tags.set(tags_data)
        ingredients_data = validated_data.get('ingredients')
        if ingredients_data is None:
            raise BadRequest()
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        self.add_ingredients(ingredients_data, recipe)
        instance.save()
        return instance

    def to_representation(self, recipe):
        serializer = RecipeSerializer(recipe)
        return serializer.data


class RecipePartialSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
