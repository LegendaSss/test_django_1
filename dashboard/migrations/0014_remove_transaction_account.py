# Generated by Django 4.2.7 on 2023-12-18 20:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0013_transaction_account'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='account',
        ),
    ]