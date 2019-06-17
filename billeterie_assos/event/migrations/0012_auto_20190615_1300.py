# Generated by Django 2.2.2 on 2019-06-15 11:00

from django.db import migrations, models
import event.models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0011_auto_20190615_1214'),
    ]

    operations = [
        migrations.AddField(
            model_name='association',
            name='url',
            field=models.URLField(blank=True, null=True, verbose_name="Association's website"),
        ),
        migrations.AlterField(
            model_name='association',
            name='name',
            field=models.CharField(max_length=64, unique=True, validators=[event.models.UnicodeValidator()], verbose_name='Name'),
        ),
    ]