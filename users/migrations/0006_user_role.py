# Generated by Django 5.2 on 2025-06-17 23:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_rename_is_verified_by_user_is_verified'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('admin', 'Администратор'), ('manager', 'Менеджер'), ('consultant', 'Консультант'), ('creator', 'Автор тура'), ('client', 'Клиент')], default='client', max_length=20, verbose_name='Роль'),
        ),
    ]
