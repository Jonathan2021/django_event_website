# Generated by Django 2.2.2 on 2019-06-23 20:17

from django.db import migrations, models
import event.models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0025_auto_20190622_1315'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='title',
            field=models.CharField(max_length=64, validators=[event.models.UnicodeValidator()], verbose_name='Title of the event'),
        ),
    ]