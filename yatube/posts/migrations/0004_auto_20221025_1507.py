# Generated by Django 2.2.19 on 2022-10-25 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_auto_20221025_1448'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='slug',
            field=models.SlugField(unique=True, verbose_name='Слаг сообщества (group/<slug>/)'),
        ),
    ]
