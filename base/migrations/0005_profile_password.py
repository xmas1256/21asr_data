# Generated by Django 4.0.1 on 2022-02-11 03:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_smstext'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='password',
            field=models.CharField(default='', max_length=300),
            preserve_default=False,
        ),
    ]
