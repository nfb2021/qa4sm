# Generated by Django 3.2.16 on 2024-09-05 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('validator', '0076_auto_20240716_1346'),
    ]

    operations = [
        migrations.AlterField(
            model_name='validationrun',
            name='intra_annual_type',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
