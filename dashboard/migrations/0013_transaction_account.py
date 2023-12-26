# Generated by Django 4.2.7 on 2023-12-18 20:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0012_remove_transaction_account'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='account',
            field=models.ForeignKey(default='1', on_delete=django.db.models.deletion.CASCADE, to='dashboard.accounttype'),
            preserve_default=False,
        ),
    ]