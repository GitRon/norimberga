# Generated by Django 5.0 on 2024-01-01 14:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("city", "0030_savegame_is_active"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="buildingtype",
            name="behaviour_type",
        ),
        migrations.AddField(
            model_name="buildingtype",
            name="is_city",
            field=models.BooleanField(default=False, verbose_name="Is city building"),
        ),
        migrations.AddField(
            model_name="buildingtype",
            name="is_country",
            field=models.BooleanField(
                default=False, verbose_name="Is country building"
            ),
        ),
    ]
