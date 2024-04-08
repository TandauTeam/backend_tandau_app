# Generated by Django 4.2.4 on 2024-04-06 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tandau_app', '0006_video'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='video',
            name='title',
        ),
        migrations.RemoveField(
            model_name='video',
            name='youtube_video_id',
        ),
        migrations.AddField(
            model_name='video',
            name='youtube_link',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
    ]
