from random import randint

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        for _i in range(100):
            print(randint(1, 2))
