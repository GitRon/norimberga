# Generated by Django 5.0 on 2023-12-29 12:11

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("event", "0006_rename_effect_event_effects"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="eventeffect",
            name="content_type",
        ),
        migrations.RemoveField(
            model_name="eventeffectfilter",
            name="effect",
        ),
        migrations.DeleteModel(
            name="Event",
        ),
        migrations.DeleteModel(
            name="EventEffect",
        ),
        migrations.DeleteModel(
            name="EventEffectFilter",
        ),
    ]
