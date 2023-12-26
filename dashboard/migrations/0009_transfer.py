# Generated by Django 4.2.7 on 2023-12-18 04:57

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0008_alter_transaction_amount'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transfer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('date', models.DateField(default=datetime.datetime.today)),
                ('receiver_portfolio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receiver_transfers', to='dashboard.portfolio')),
                ('sender_portfolio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sender_transfers', to='dashboard.portfolio')),
            ],
        ),
    ]