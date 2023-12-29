from django.contrib import admin

from apps.event.models import Event, EventEffect, EventEffectFilter


class EventEffectFilterAdmin(admin.TabularInline):
    model = EventEffectFilter


@admin.register(EventEffect)
class EventEffectAdmin(admin.ModelAdmin):
    inlines = (EventEffectFilterAdmin,)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    pass
