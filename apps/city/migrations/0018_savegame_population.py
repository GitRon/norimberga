# Generated by Django 5.0 on 2023-12-25 10:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("city", "0017_remove_savegame_coin_savegame_coins"),
    ]

    operations = [
        migrations.AddField(
            model_name="savegame",
            name="population",
            field=models.PositiveSmallIntegerField(
                default=0, verbose_name="Population"
            ),
        ),
    ]
