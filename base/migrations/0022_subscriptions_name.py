# Generated by Django 4.0.1 on 2022-03-23 18:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0021_telegrampost'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriptions',
            name='name',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]
