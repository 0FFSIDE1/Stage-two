# Generated by Django 5.0.6 on 2024-07-06 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0007_alter_user_email_alter_user_firstname_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(default=None, max_length=30, unique=True),
        ),
    ]
