from ambient_toolbox.system_checks.atomic_docs import check_atomic_docs
from django.apps import AppConfig
from django.core.checks import register


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"

    def ready(self):
        register(check_atomic_docs)
