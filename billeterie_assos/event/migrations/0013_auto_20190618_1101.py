# Generated by Django 2.2.2 on 2019-06-18 09:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0012_auto_20190615_1300'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='image',
            field=models.ImageField(blank=True, default='event_pics/default.jpg', null=True, upload_to='event_pics/uploads', verbose_name="Event's cover image"),
        ),
        migrations.AlterField(
            model_name='event',
            name='event_state',
            field=models.CharField(choices=[('P', 'Pending'), ('A', 'Approved'), ('R', 'Refused'), ('C', 'Canceled'), ('V', 'Validated by the president')], default='P', max_length=1, verbose_name='State of the event'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='image',
            field=models.ImageField(default='profile_pics/default.jpg', upload_to='profile_pics/uploads'),
        ),
    ]
