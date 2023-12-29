from django.core.management.base import BaseCommand

from apps.event.services.selection import EventSelectionService


class Command(BaseCommand):
    def handle(self, *args, **options):
        EventSelectionService().process()
