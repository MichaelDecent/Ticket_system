# Generated by Django 5.0.6 on 2024-06-29 23:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0004_payment'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='paid',
            field=models.BooleanField(default=False),
        ),
    ]
