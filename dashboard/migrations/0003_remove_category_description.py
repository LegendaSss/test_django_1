# Generated by Django 4.2.7 on 2023-12-05 21:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_category_description_payment_payment_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='description',
        ),
    ]
