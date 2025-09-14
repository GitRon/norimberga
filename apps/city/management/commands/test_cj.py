from random import randint

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        for _i in range(100):
            value = randint(1, 2)
            print(value)
            self.stdout.write(str(value))
