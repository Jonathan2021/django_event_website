# Generated by Django 2.2.2 on 2019-06-26 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0009_auto_20190625_2308'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='ticket_id',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
