# Generated by Django 3.1 on 2020-09-12 15:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scrud_django', '0002_auto_20200826_0345'),
    ]

    operations = [
        migrations.AddField(
            model_name='resourcetype',
            name='revision',
            field=models.CharField(default='1', max_length=40),
            preserve_default=False,
        ),
    ]
