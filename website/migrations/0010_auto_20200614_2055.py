# Generated by Django 3.0.6 on 2020-06-14 10:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0009_auto_20200614_1608'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
