# Generated by Django 5.0 on 2023-12-24 09:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("city", "0013_remove_building_is_city_remove_building_is_wall_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="savegame",
            name="silver",
            field=models.PositiveSmallIntegerField(default=0, verbose_name="Silver"),
        ),
    ]
