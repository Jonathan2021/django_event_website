# Generated by Django 2.2.2 on 2019-06-20 09:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0018_auto_20190619_1448'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='association',
            options={'permissions': (('create_event', 'User can create an event'), ('manage_member', 'User can add and remove a member'), ('choose_staff', 'User can choose staff'), ('manage_manager', 'User can add and remove managers'), ('modify_event', 'User can modify an event'), ('cancel_event', 'User can cancel an event')), 'verbose_name': 'Association', 'verbose_name_plural': 'Associations'},
        ),
    ]
