# Generated by Django 2.1.2 on 2018-10-24 18:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkit', '0011_check_paid'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='check',
            options={},
        ),
        migrations.AddIndex(
            model_name='account',
            index=models.Index(fields=['name'], name='account_name_idx'),
        ),
        migrations.AddIndex(
            model_name='account',
            index=models.Index(fields=['number'], name='account_number_idx'),
        ),
        migrations.AddIndex(
            model_name='company',
            index=models.Index(fields=['date_created'], name='company_date_created_idx'),
        ),
    ]
