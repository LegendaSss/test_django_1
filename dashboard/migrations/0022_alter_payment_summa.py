# Generated by Django 4.2.7 on 2023-12-20 18:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0021_alter_income_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='summa',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Сумма'),
        ),
    ]