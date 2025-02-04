# Generated by Django 2.2.2 on 2019-06-20 12:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0023_auto_20190620_1414'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='association',
            options={'permissions': (('create_event', 'User can create an event'), ('manage_member', 'User can add and remove a member'), ('choose_staff', 'User can choose staff'), ('manage_manager', 'User can add and remove managers'), ('modify_event', 'User can modify an event'), ('make_event_cancelable', 'User can cancel an event'), ('validate_event', 'User can validate event and make it available for approval')), 'verbose_name': 'Association', 'verbose_name_plural': 'Associations'},
        ),
        migrations.AlterModelOptions(
            name='boss',
            options={'verbose_name': 'Boss', 'verbose_name_plural': 'Boss'},
        ),
    ]
