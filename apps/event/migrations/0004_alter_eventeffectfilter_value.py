# Generated by Django 5.0 on 2023-12-27 12:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("event", "0003_eventeffectfilter_value"),
    ]

    operations = [
        migrations.AlterField(
            model_name="eventeffectfilter",
            name="value",
            field=models.CharField(max_length=75, verbose_name="Value"),
        ),
    ]
