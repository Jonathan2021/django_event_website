# Generated by Django 2.2.2 on 2019-06-07 21:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0006_auto_20190607_2305'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='event_id',
            field=models.CharField(default=0, max_length=50),
            preserve_default=False,
        ),
    ]
