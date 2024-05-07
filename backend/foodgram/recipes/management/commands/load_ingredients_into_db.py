import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        ingredient_file = open('../../data/ingredients.csv', encoding='utf-8')
        reader = csv.reader(ingredient_file)
        next(reader)
        ingredients = [
            Ingredient(
                name=row[0],
                measurement_unit=row[1],
            )
            for row in reader
        ]
        Ingredient.objects.bulk_create(ingredients)
        ingredient_file.close()
