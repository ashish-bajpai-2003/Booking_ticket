# Generated by Django 5.1.6 on 2025-05-14 07:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_train_distance'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='source',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
    ]
