# Generated by Django 4.2.4 on 2023-09-06 00:21

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("mangoAPP", "0015_rename_usuario_empleados_username"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="empleados",
            name="username",
        ),
        migrations.AddField(
            model_name="empleados",
            name="username_emple",
            field=models.CharField(default=1, max_length=255, unique=True),
            preserve_default=False,
        ),
    ]
