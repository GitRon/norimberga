# Generated by Django 5.0 on 2023-12-31 11:44

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("city", "0026_buildingtype_is_house_buildingtype_is_wall_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="building",
            name="level",
            field=models.PositiveSmallIntegerField(default=1, verbose_name="Level"),
            preserve_default=False,
        ),
    ]
