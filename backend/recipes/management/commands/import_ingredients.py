import csv

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import IntegrityError

from recipes.models import Ingredient


class Command(BaseCommand):
    """Загрузка данных из csv файлов."""
    help = 'Загрузка данных из csv файлов'

    def handle(self, *args, **options):
        """Метод обработчик."""
        with open(
            f'{settings.BASE_DIR}/data/ingredients.csv',
            'r',
            encoding='utf-8'
        ) as csv_file:
            reader = csv.DictReader(csv_file)
            try:
                Ingredient.objects.bulk_create(
                    Ingredient(**items) for items in reader
                )
            except IntegrityError:
                return 'Такие ингредиенты уже есть...'
        return (
            f'Ингредиенты успешно загружены: {Ingredient.objects.count()}'
        )
