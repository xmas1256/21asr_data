# Generated by Django 4.0.1 on 2022-02-28 03:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0014_alter_client_guvohnoma_file_alter_client_passport_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='passport',
            field=models.FileField(blank=True, null=True, upload_to='static/passport/'),
        ),
        migrations.AlterField(
            model_name='client',
            name='selfy',
            field=models.FileField(blank=True, null=True, upload_to='static/selfy/'),
        ),
        migrations.AlterField(
            model_name='client',
            name='ustav',
            field=models.FileField(blank=True, null=True, upload_to='static/ustav/'),
        ),
    ]
