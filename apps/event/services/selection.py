import importlib
import random
from os.path import isdir
from pathlib import Path

from django.conf import settings

from apps.event.events.events.base_event import BaseEvent


class EventSelectionService:
    def _get_possible_events(self):
        dice = random.randint(1, 100)

        # Get base dir and locally installed apps
        root_dir = settings.ROOT_DIR
        local_apps = settings.LOCAL_APPS

        # Start collecting event classes...
        possible_event_classes = []

        # Iterate over all local apps...
        for app in local_apps:
            # Search for "events/events" package
            event_path = root_dir / app.replace(".", "/") / "events/events"

            # If the app doesn't have it, continue
            if not isdir(event_path):
                continue

            # Iterate all files within the package
            for file in event_path.iterdir():
                file_path = Path(file)

                # Ignore dunder and non-Python files
                if file_path.name.startswith("__") or file_path.suffix != ".py":
                    continue

                # Import file
                module = importlib.import_module(
                    file_path.as_posix().replace(root_dir.as_posix(), "").replace("/", ".").strip(".").strip(".py")
                )

                # Get event class
                try:
                    event_class = module.Event
                except AttributeError:
                    continue

                # Check if the loaded class is really an event
                if not isinstance(event_class(), BaseEvent):
                    continue

                # Check probability and add event to possible events
                probability = event_class.PROBABILITY
                if probability <= dice:
                    possible_event_classes.append(event_class)

        return possible_event_classes

    def process(self) -> BaseEvent | None:
        possible_event_classes = self._get_possible_events()
        if len(possible_event_classes):
            event_class = random.choice(possible_event_classes)

            if event_class:
                return event_class()
