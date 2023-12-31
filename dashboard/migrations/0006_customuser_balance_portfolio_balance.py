# Generated by Django 4.2.7 on 2023-12-16 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0005_rename_journal_list_transaction_portfolio_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='balance',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Общий баланс в рублях'),
        ),
        migrations.AddField(
            model_name='portfolio',
            name='balance',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Баланс в валюте'),
        ),
    ]
