# Generated by Django 4.0.1 on 2022-02-23 10:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0009_alter_upload_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='upload',
            options={'ordering': ['status']},
        ),
    ]