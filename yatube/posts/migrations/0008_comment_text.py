# Generated by Django 2.2.16 on 2022-09-03 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='text',
            field=models.TextField(max_length=200, null=True),
        ),
    ]
