# Generated by Django 2.1.2 on 2018-10-18 14:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('checkit', '0009_auto_20181018_1038'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='check',
            name='paid',
        ),
        migrations.RemoveField(
            model_name='check',
            name='payee',
        ),
    ]
