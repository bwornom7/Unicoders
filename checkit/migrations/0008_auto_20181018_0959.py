# Generated by Django 2.1.2 on 2018-10-18 13:59

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkit', '0007_auto_20180919_2333'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Bank',
        ),
        migrations.AlterModelOptions(
            name='account',
            options={},
        ),
        migrations.AlterModelOptions(
            name='company',
            options={'verbose_name_plural': 'companies'},
        ),
        migrations.RemoveIndex(
            model_name='account',
            name='account_date_idx',
        ),
        migrations.RemoveIndex(
            model_name='check',
            name='check_date_idx',
        ),
        migrations.RenameField(
            model_name='account',
            old_name='date',
            new_name='date_created',
        ),
        migrations.RenameField(
            model_name='check',
            old_name='to',
            new_name='payee',
        ),
        migrations.RemoveField(
            model_name='account',
            name='address',
        ),
        migrations.AddField(
            model_name='account',
            name='city',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='account',
            name='state',
            field=models.CharField(max_length=2, null=True),
        ),
        migrations.AddField(
            model_name='account',
            name='street',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='account',
            name='zip_code',
            field=models.CharField(max_length=5, null=True, validators=[django.core.validators.RegexValidator('^[0-9]{5}$', code='invalid_zip_code', message='Zip code must be five digits.')]),
        ),
        migrations.AddField(
            model_name='check',
            name='amount_paid',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='check',
            name='date_created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='check',
            name='letter1_date',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='check',
            name='letter2_date',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='check',
            name='letter3_date',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='company',
            name='city',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='company',
            name='date_created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='company',
            name='state',
            field=models.CharField(max_length=2, null=True),
        ),
        migrations.AddField(
            model_name='company',
            name='street',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='company',
            name='zip_code',
            field=models.CharField(max_length=5, null=True, validators=[django.core.validators.RegexValidator('^[0-9]{5}$', code='invalid_zip_code', message='Zip code must be five digits.')]),
        ),
        migrations.AlterField(
            model_name='check',
            name='date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddIndex(
            model_name='account',
            index=models.Index(fields=['date_created'], name='account_date_created_idx'),
        ),
        migrations.AddIndex(
            model_name='check',
            index=models.Index(fields=['date_created'], name='check_date_created_idx'),
        ),
    ]
