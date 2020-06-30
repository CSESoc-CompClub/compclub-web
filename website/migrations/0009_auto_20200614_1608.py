# Generated by Django 3.0.6 on 2020-06-14 06:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0008_school_region'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='email_consent',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]
