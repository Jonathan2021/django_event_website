# Generated by Django 2.2.2 on 2019-06-15 10:14

from django.db import migrations, models
import event.models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0010_auto_20190615_1153'),
    ]

    operations = [
        migrations.AlterField(
            model_name='association',
            name='name',
            field=models.CharField(max_length=64, unique=True, validators=[event.models.UnicodeValidator], verbose_name='Name'),
        ),
    ]
