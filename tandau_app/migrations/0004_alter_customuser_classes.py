# Generated by Django 4.2.4 on 2024-03-22 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tandau_app', '0003_customuser_classes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='classes',
            field=models.IntegerField(null=True),
        ),
    ]
