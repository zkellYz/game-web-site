# Generated by Django 4.0.4 on 2022-05-11 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0011_alter_customuser_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='avatar',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='users'),
        ),
    ]
