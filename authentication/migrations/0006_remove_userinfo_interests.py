# Generated by Django 5.0.3 on 2024-03-07 09:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0005_user_groups_user_is_superuser_user_user_permissions'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userinfo',
            name='interests',
        ),
    ]