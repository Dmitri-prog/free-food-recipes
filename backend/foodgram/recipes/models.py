from django.contrib.auth import get_user_model
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models

from foodgram.settings import (MAX_LENGTH_BIG, MAX_LENGTH_SMALL, MAX_VALUE,
                               MIN_VALUE)

User = get_user_model()


class Ingredient(models.Model):
    """Ингредиенты."""

    name = models.CharField(
        max_length=MAX_LENGTH_BIG,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=MAX_LENGTH_BIG,
        verbose_name='Единицы измерения'
    )

    class Meta:
        ordering = ('name', )
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Tag(models.Model):
    """Тэги."""

    name = models.CharField(
        max_length=MAX_LENGTH_BIG,
        verbose_name='Название',
        unique=True,
    )
    color = models.CharField(
        max_length=MAX_LENGTH_SMALL,
        null=True,
        verbose_name='Цвет',
        unique=True
    )
    slug = models.SlugField(
        max_length=MAX_LENGTH_BIG,
        null=True,
        verbose_name='Слаг',
        unique=True,
        validators=[RegexValidator(
            regex=r'^[-a-zA-Z0-9_]+$',
            message=('Недопустимое название слага! '
                     'Название может содержать только целые числа, '
                     'буквы или подчеркивание.')
        )]
    )

    class Meta:
        ordering = ('name', )
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return f'{self.name} ({self.slug})'


class Recipe(models.Model):
    """Рецепты."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField(
        max_length=MAX_LENGTH_BIG,
        verbose_name='Название рецепта',
    )
    image = models.ImageField(
        verbose_name='Картинка блюда',
        upload_to='recipes_images/',
    )
    text = models.TextField(
        verbose_name='Текст'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        through_fields=('recipe', 'ingredient'),
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления, мин.',
        validators=[
            MinValueValidator(
                MIN_VALUE,
                message='Время приготовления должно быть минимум 1 мин.'
            ),
            MaxValueValidator(
                MAX_VALUE,
                message='Время приготовления должно быть максимум 32000 мин.'
            )
        ],
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )

    class Meta:
        ordering = ('-pub_date', )
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Промежуточная таблица ингредиентов для рецептов"""
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(
                MIN_VALUE,
                message='Количество должно быть минимум 1.'
            ),
            MaxValueValidator(
                MAX_VALUE,
                message='Количкство должно быть максимум 32000.'
            )
        ]
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        ordering = ('id', )
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.ingredient} в рецепте "{self.recipe}"'


class Favorite(models.Model):
    """Избранное."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт'
    )

    class Meta:
        ordering = ('id', )
        verbose_name = 'Объект избранного'
        verbose_name_plural = 'Объекты избранного'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite_user_recipe'
            )
        ]

    def __str__(self):
        return f'Избранный рецепт "{self.recipe}" у {self.user}'


class ShoppingCart(models.Model):
    """Список покупок."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь'
    )

    class Meta:
        ordering = ('user', )
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_cart_user_recipe'
            ),
        )

    def __str__(self):
        return f'У {self.user} рецепт "{self.recipe}" в списке покупок'


class Subscription(models.Model):
    """Подписки."""

    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Автор'
    )

    class Meta:
        ordering = ('id', )
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'subscriber'),
                name='unique_subscription_author_subscriber'
            ),
        )

    def __str__(self):
        return f'Подписчик {self.subscriber} у автора {self.author}'
