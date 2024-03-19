# Generated by Django 5.0.3 on 2024-03-19 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0008_rename_users_userinfo_interests'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='biography',
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.AlterField(
            model_name='userinfo',
            name='date_of_birth',
            field=models.DateField(blank=True),
        ),
        migrations.AlterField(
            model_name='userinfo',
            name='full_name',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='userinfo',
            name='occupation',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]