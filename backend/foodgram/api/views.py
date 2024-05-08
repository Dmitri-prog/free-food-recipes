from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from recipes.filters import IngredientFilter, RecipeFilter
from django.core.exceptions import BadRequest

from api.serializers import (
    IngredientSerializer, TagSerializer, MyUserSerializer,
    SubscriptionSerializer, UserSubscriptionSerializer,
    RecipeFullSerializer, FavoriteSerializer, RecipePartialSerializer,
    ShoppingCartSerializer, RecipeSerializer
)
from recipes.models import (
    Ingredient, Tag, Recipe, RecipeIngredient,
    Favorite, ShoppingCart, Subscription
)

from django.contrib.auth import get_user_model

from api.permissions import AdminOrReadOnly, AuthorOrReadOnly

User = get_user_model()


class CustomPagination(PageNumberPagination):
    page_size_query_param = 'limit'


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeFullSerializer
    permission_classes = (AuthorOrReadOnly, )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPagination

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            try:
                recipe = Recipe.objects.get(pk=pk)
            except Recipe.DoesNotExist:
                raise BadRequest()
            serializer = FavoriteSerializer(
                data={
                    'user': request.user.id,
                    'recipe': recipe.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            favorite_serializer = RecipePartialSerializer(recipe)
            return Response(
                favorite_serializer.data, status=status.HTTP_201_CREATED
            )
        recipe = get_object_or_404(Recipe, pk=pk)
        try:
            favorite = Favorite.objects.get(
                user=request.user,
                recipe=recipe
            )
        except Favorite.DoesNotExist:
            raise BadRequest()
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            try:
                recipe = Recipe.objects.get(pk=pk)
            except Recipe.DoesNotExist:
                raise BadRequest()
            serializer = ShoppingCartSerializer(
                data={'user': request.user.id, 'recipe': recipe.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            shopping_cart_serializer = RecipePartialSerializer(recipe)
            return Response(
                shopping_cart_serializer.data, status=status.HTTP_201_CREATED
            )
        recipe = get_object_or_404(Recipe, pk=pk)
        try:
            shopping_cart = ShoppingCart.objects.get(
                user=request.user,
                recipe=recipe
            )
        except ShoppingCart.DoesNotExist:
            raise BadRequest()
        shopping_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def ingredients_to_txt(ingredients):
        shopping_list = ''
        for ingredient in ingredients:
            shopping_list += (
                f"{ingredient['ingredient__name']}  - "
                f"{ingredient['sum']}"
                f"({ingredient['ingredient__measurement_unit']})\n"
            )
        return shopping_list

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(sum=Sum('amount'))
        shopping_list = self.ingredients_to_txt(ingredients)
        return HttpResponse(shopping_list, content_type='text/plain')

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return RecipeFullSerializer


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = MyUserSerializer
    permission_classes = (AdminOrReadOnly,)
    pagination_class = CustomPagination

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        if request.method == 'PATCH':
            serializer = MyUserSerializer(
                request.user,
                data=request.data,
                partial=True,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = MyUserSerializer(
            request.user,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            serializer = SubscriptionSerializer(
                data={'subscriber': request.user.id,
                      'author': author.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            author_serializer = UserSubscriptionSerializer(
                author,
                context={'request': request}
            )
            return Response(
                author_serializer.data, status=status.HTTP_201_CREATED
            )
        try:
            subscription = Subscription.objects.get(
                subscriber=request.user,
                author=author
                )
        except Subscription.DoesNotExist:
            raise BadRequest()
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        authors = User.objects.filter(author__subscriber=request.user)
        result_pages = self.paginate_queryset(
            queryset=authors
        )
        serializer = UserSubscriptionSerializer(
            result_pages,
            context={'request': request},
            many=True
        )
        return self.get_paginated_response(serializer.data)
