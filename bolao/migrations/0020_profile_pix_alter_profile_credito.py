# Generated by Django 4.0.6 on 2022-08-24 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bolao', '0019_auto_20220823_1705'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='pix',
            field=models.TextField(default='', null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='credito',
            field=models.FloatField(default=0.0),
        ),
    ]
