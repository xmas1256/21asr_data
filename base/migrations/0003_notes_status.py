# Generated by Django 4.0.1 on 2022-02-06 04:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_alter_notes_options_notes_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='notes',
            name='status',
            field=models.CharField(choices=[('0', 'Bajarilmagan'), ('5', 'Jarayonda'), ('10', 'Tugatilgan')], default='0', max_length=255),
        ),
    ]
