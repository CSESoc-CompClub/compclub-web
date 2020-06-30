# Generated by Django 3.0.6 on 2020-05-25 06:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LightBox',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('region', models.CharField(max_length=255)),
                ('ordering', models.IntegerField(default=0)),
                ('url', models.ImageField(max_length=150, upload_to='')),
                ('caption', models.CharField(help_text='Alternate text for the image.', max_length=150)),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='website_lightbox_set', to='website.Event')),
            ],
            options={
                'verbose_name': 'image',
                'verbose_name_plural': 'images',
            },
        ),
    ]
